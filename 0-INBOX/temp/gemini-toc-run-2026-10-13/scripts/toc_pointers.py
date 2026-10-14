#!/usr/bin/env python3
"""Deterministic pointer resolution + segmentation-preserving ingest for toc-generate trees.

  toc_pointers.py resolve --tree T --source S [--report R]
      Rewrites T in place, giving every node a [[N]] pointer = 1-based line of the
      FIRST line of the paragraph (blank-line-delimited block) holding its
      announcement, or [[?]]. Pointers always land on a block start, so a heading
      inserted there can never split a human-made paragraph.

  toc_pointers.py ingest --tree T --source S --sha16 HASH [--report R]
      Inserts `<hashes> <label> ^N-N-0` + blank line before each node's pointer
      block (above any root-verse transclusion lines immediately preceding it when
      the announcement opens that block). Aborts if the source's sha256 prefix is
      not HASH. Verifies that removing exactly the inserted lines restores the
      original bytes before writing.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import sys
from pathlib import Path

SCRIPTS = Path("/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/"
               "4-SYSTEM/Skills/toc-generate/scripts")
sys.path.insert(0, str(SCRIPTS))
import qc_check_tree as Q  # noqa: E402
import toc_tree_ingest as TI  # noqa: E402

NODE_RE = re.compile(r"^(?P<indent>[ \t]*)\*[ \t]+(?P<dec>\d+(?:\.\d+)*)\.?[ \t]+"
                     r"(?P<title>.*?)(?:[ \t]*\[\[(?:\d+|\?)\]\])?[ \t]*$")
TRANSCLUSION_RE = re.compile(r"^\s*!\[\[[^\]]+\]\]\s*$")
PARA = "¶"
SYL_START = {Q._TSHEG, Q._BOUND, PARA}


def blocks_of(lines: list[str]) -> list[tuple[int, int]]:
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].strip():
            j = i
            while j + 1 < n and lines[j + 1].strip():
                j += 1
            out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


class Doc:
    def __init__(self, lines: list[str]):
        self.lines = lines
        self.blocks = blocks_of(lines)
        parts, self.starts = [], []
        off = 0
        for s, e in self.blocks:
            c = Q._canon("\n".join(lines[s:e + 1])) + PARA
            self.starts.append(off)
            parts.append(c)
            off += len(c)
        self.text = "".join(parts)

    def block_at(self, pos: int) -> int:
        return bisect.bisect_right(self.starts, pos) - 1

    def occurrences(self, needle: str, lo: int = 0, hi: int | None = None) -> list[int]:
        hi = len(self.text) if hi is None else hi
        out, i = [], self.text.find(needle, lo)
        while i != -1 and i < hi:
            if i == 0 or self.text[i - 1] in SYL_START:
                out.append(i)
            i = self.text.find(needle, i + 1)
        return out


def parse_tree(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    nodes = []
    for i, l in enumerate(lines):
        if re.match(r"^\s*\*\s", l):
            m = NODE_RE.match(l)
            if m:
                nodes.append({"i": i, "indent": m.group("indent"), "dec": m.group("dec"),
                              "title": m.group("title").strip()})
    return lines, nodes


def monotone_best(cands: list[list[int]]) -> list[int | None]:
    """Choose ≤1 candidate per node so chosen positions are non-decreasing in node
    order and the number of chosen nodes is maximal (LIS with candidate sets)."""
    tails: list[int] = []   # tails[k] = smallest end pos of a chain of length k+1
    tail_ref: list[tuple[int, int]] = []  # (node, pos) at that tail
    back: dict[tuple[int, int], tuple[int, int] | None] = {}
    for ni, cs in enumerate(cands):
        updates = []
        for p in sorted(set(cs)):
            k = bisect.bisect_right(tails, p)  # non-decreasing allowed
            prev = tail_ref[k - 1] if k > 0 else None
            updates.append((k, p, prev))
        # apply after computing so one node never chains onto itself
        for k, p, prev in updates:
            back[(ni, p)] = prev
            if k == len(tails):
                tails.append(p); tail_ref.append((ni, p))
            elif p < tails[k]:
                tails[k] = p; tail_ref[k] = (ni, p)
    chosen: list[int | None] = [None] * len(cands)
    cur = tail_ref[-1] if tail_ref else None
    while cur:
        chosen[cur[0]] = cur[1]
        cur = back[cur]
    return chosen


def ordinal_pattern(title: str):
    word, _ = Q._leading_tibetan_ordinal_word(title)
    if not word:
        return None
    return re.compile(re.escape(Q._canon(word)) + "(?:་(?:ནི|ལ)(?=[་§¶])|(?=§))")


def resolve(args) -> int:
    src = Path(args.source).read_text(encoding="utf-8").splitlines()
    doc = Doc(src)
    tree_lines, nodes = parse_tree(Path(args.tree))
    full = [Q._canon(n["title"]) for n in nodes]
    bare = [Q._canon(Q._strip_leading_ordinal(n["title"])) for n in nodes]

    # Pass 1: full title (ordinal included) — specific, monotone best fit.
    def variants(c):
        out = [c]
        syl = c.split("་")
        if len(syl) > 2 and syl[-1] in Q._TRAILING_PARTICLES:
            out.append("་".join(syl[:-1]))
        return out
    cands = []
    for f, b in zip(full, bare):
        if len(f) >= 6 and f != b or len(b) >= 12:
            cands.append(sorted({o for v in variants(f) for o in doc.occurrences(v)}))
        else:
            cands.append([])
    pos = monotone_best(cands)
    method = ["title" if p is not None else None for p in pos]

    # Pass 2: fill gaps between resolved neighbours.
    n = len(nodes)
    for k in range(n):
        if pos[k] is not None:
            continue
        lo = next((pos[j] for j in range(k - 1, -1, -1) if pos[j] is not None), 0)
        hi = next((pos[j] for j in range(k + 1, n) if pos[j] is not None), len(doc.text))
        best = None
        pat = ordinal_pattern(nodes[k]["title"])
        if pat:
            for m in pat.finditer(doc.text, lo + 1 if k else 0, hi + 1):
                if m.start() == 0 or doc.text[m.start() - 1] in SYL_START:
                    best = (m.start(), "ordinal"); break
        if bare[k] and len(bare[k]) >= 6:
            occ = sorted({o for v in variants(bare[k]) for o in doc.occurrences(v, lo + 1 if k else 0, hi + 1)})
            if occ and (best is None or occ[0] < best[0]):
                best = (occ[0], "bare-title")
        if best:
            pos[k], method[k] = best

    # Pass 3: an unresolved node whose next node is its own first child stacks with
    # that child — at the start of the child's block.
    for k in range(n - 1, -1, -1):
        if pos[k] is None and k + 1 < n and pos[k + 1] is not None \
                and nodes[k + 1]["dec"].startswith(nodes[k]["dec"] + "."):
            b = doc.block_at(pos[k + 1])
            prev = next((pos[j] for j in range(k - 1, -1, -1) if pos[j] is not None), -1)
            if doc.starts[b] >= prev:
                pos[k], method[k] = doc.starts[b], "child-stack"

    # Write pointers + report.
    report = ["| node | title | line | method | mid-paragraph |", "|---|---|---|---|---|"]
    first_in_block: dict[int, int] = {}
    for k, p in enumerate(pos):
        if p is not None:
            first_in_block.setdefault(doc.block_at(p), k)
    unresolved = 0
    meta: dict = {}
    for k, nd in enumerate(nodes):
        p = pos[k]
        if p is None:
            ptr, unresolved = "?", unresolved + 1
            mid = ""
        else:
            b = doc.block_at(p)
            ptr = str(doc.blocks[b][0] + 1)
            lead = doc.text[doc.starts[b]:p]
            mid = "yes" if first_in_block[b] == k and lead.strip("༄༅" + Q._BOUND + Q._TSHEG) else ""
            meta[nd["dec"]] = {"mid": bool(mid) or bool(meta.get("_block_mid", {}).get(b))}
            if mid:
                meta.setdefault("_block_mid", {})[b] = True
        # indent is a pure function of the decimal (pass3 FORMAT RULES: 3 spaces × (depth − 1))
        tree_lines[nd["i"]] = "   " * nd["dec"].count(".") + f"* {nd['dec']} {nd['title']} [[{ptr}]]"
        report.append(f"| {nd['dec']} | {nd['title']} | {ptr} | {method[k] or '-'} | {mid} |")
    Path(args.tree).write_text("\n".join(tree_lines) + "\n", encoding="utf-8")
    if args.report:
        Path(args.report).write_text("\n".join(report) + "\n", encoding="utf-8")
    meta.pop("_block_mid", None)
    Path(str(args.tree) + ".meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    by = {m: method.count(m) for m in ("title", "ordinal", "bare-title", "child-stack")}
    print(f"nodes={n} resolved={n - unresolved} unresolved={unresolved} {by}")
    return 0


def ingest(args) -> int:
    path = Path(args.source)
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest()[:16] != args.sha16:
        sys.exit("ABORT: source changed since chunking — tree pointers are stale; rebuild.")
    text = raw.decode("utf-8")
    lines = text.splitlines(keepends=True)
    if any(re.search(r"\^[\d-]+-0\s*$", l) for l in lines if l.startswith("#")):
        sys.exit("ABORT: file already carries heading block IDs.")
    blank = [not l.strip() for l in lines]

    meta = json.loads(Path(str(args.tree) + ".meta.json").read_text(encoding="utf-8"))
    nodes = [TI.parse_toc_line(l) for l in Path(args.tree).read_text(encoding="utf-8").splitlines()]
    nodes = [x for x in nodes if x]
    report = []
    groups: dict[int, list[str]] = {}
    missing = []
    for nd in nodes:
        if nd["pointer"] is None:
            missing.append(nd); continue
        idx = nd["pointer"] - 1
        assert idx == 0 or blank[idx - 1], f"pointer {nd['pointer']} is not a block start"
        # lift above root-verse transclusion blocks directly preceding the block
        j = idx
        while not meta.get(nd["decimal_id"], {}).get("mid"):
            k = j - 1
            while k >= 0 and blank[k]:
                k -= 1
            if k >= 0 and TRANSCLUSION_RE.match(lines[k]) and (k == 0 or blank[k - 1]):
                j = k
            else:
                break
        if j != idx:
            report.append(f"{nd['decimal_id']}: lifted above {sum(1 for x in range(j, idx) if lines[x].strip())} transclusion line(s) (line {idx + 1} → {j + 1})")
        label = nd["label"]
        if nd["depth"] > 6:
            label = f"**{label}**"
        if meta.get(nd["decimal_id"], {}).get("mid"):
            report.append(f"{nd['decimal_id']}: announcement is mid-paragraph — heading placed before the containing paragraph (line {idx + 1})")
        groups.setdefault(j, []).append(f"{TI.depth_to_heading(nd['depth'])} {label} {nd['block_id']}\n")

    out, inserted_idx = [], set()
    for i, l in enumerate(lines):
        for h in groups.get(i, []):
            inserted_idx.add(len(out)); out.append(h)
            inserted_idx.add(len(out)); out.append("\n")
        out.append(l)
    if len(lines) in groups:  # never expected; pointers are in range
        sys.exit("ABORT: pointer past EOF")
    restored = "".join(l for i, l in enumerate(out) if i not in inserted_idx)
    assert restored == text, "verification failed: original bytes not preserved"
    path.write_text("".join(out), encoding="utf-8")
    n_ins = sum(len(v) for v in groups.values())
    print(f"inserted={n_ins} unresolved_not_inserted={len(missing)} lines {len(lines)} -> {len(out)} "
          f"(expected {len(lines) + 2 * n_ins}) verification=PASS")
    if args.report:
        Path(args.report).write_text("\n".join(report + [f"UNRESOLVED {m['decimal_id']} {m['label']}" for m in missing]) + "\n",
                                     encoding="utf-8")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("resolve"); r.add_argument("--tree", required=True); r.add_argument("--source", required=True)
    r.add_argument("--report")
    g = sp.add_parser("ingest"); g.add_argument("--tree", required=True); g.add_argument("--source", required=True)
    g.add_argument("--sha16", required=True); g.add_argument("--report")
    a = p.parse_args()
    return resolve(a) if a.cmd == "resolve" else ingest(a)


if __name__ == "__main__":
    sys.exit(main())
