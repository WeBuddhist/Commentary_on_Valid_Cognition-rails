#!/usr/bin/env python3
"""Run the toc-generate LLM phases (A, B, C, D-repair) through the Gemini API.

Each call is isolated: system instruction = exactly one prompt file from
4-SYSTEM/Skills/toc-generate/prompts/, user content = only that phase's input.
This is the Gemini stand-in for the skill's per-phase isolated subagents.

  gemini_toc.py chunks --phase A|B --source S --index TSV --outdir D --id ID [--workers 8]
  gemini_toc.py tree   --cand C --enum E --id ID --out O
  gemini_toc.py repair --tree T --qc Q1 Q2 --cand C --enum E --source S --id ID

The API key is read from $GEMINI_API_KEY or an `export GEMINI_API_KEY=` line in
~/.zshrc. It is never printed.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# IPv6 to Google is unreachable from this host (connects time out); Python tries
# addresses sequentially, so force IPv4.
import socket as _socket
_orig_gai = _socket.getaddrinfo
def _gai_v4(host, port, family=0, *a, **k):
    return _orig_gai(host, port, _socket.AF_INET, *a, **k)
_socket.getaddrinfo = _gai_v4

VAULT = Path("/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails")
PROMPTS = VAULT / "4-SYSTEM/Skills/toc-generate/prompts"
MODELS = [m for m in os.environ.get("GEMINI_TOC_MODELS", "gemini-3.1-pro-preview,gemini-pro-latest,gemini-2.5-pro").split(",") if m]
LOG = Path(os.environ.get("GEMINI_TOC_LOG", "/dev/null"))


def api_key() -> str:
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if k:
        return k
    for line in (Path.home() / ".zshrc").read_text(errors="ignore").splitlines():
        m = re.match(r"\s*export\s+GEMINI_API_KEY=['\"]?([^'\"\s]+)", line)
        if m:
            return m.group(1)
    sys.exit("GEMINI_API_KEY not found")


KEY = None
_model_ok: str | None = None


def call(system: str, user: str, max_tokens: int = 65536, timeout: int = 900) -> tuple[str, str]:
    global KEY, _model_ok
    KEY = KEY or api_key()
    body = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    models = [_model_ok] if _model_ok else MODELS
    last = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        for attempt in range(6):
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    data = json.loads(r.read())
                cand = (data.get("candidates") or [{}])[0]
                fin = cand.get("finishReason")
                text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])
                               if not p.get("thought"))
                if fin not in ("STOP", None) or not text.strip():
                    last = f"{model}: finishReason={fin} empty={not text.strip()}"
                    time.sleep(5 * (attempt + 1))
                    continue
                _model_ok = model
                return text, model
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    last = f"{model}: 404"
                    break
                last = f"{model}: HTTP {e.code}"
                log(f"retry {model} HTTP {e.code} attempt {attempt + 1}")
                time.sleep(min(120, 10 * 2 ** attempt))
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError, json.JSONDecodeError) as e:
                last = f"{model}: {e}"
                log(f"retry {model} {type(e).__name__}: {e} attempt {attempt + 1}")
                time.sleep(min(120, 10 * 2 ** attempt))
    raise RuntimeError(f"Gemini call failed: {last}")


def unfence(t: str) -> str:
    t = t.strip()
    m = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", t, re.S)
    return m.group(1).strip() if m else t


def log(msg: str) -> None:
    with LOG.open("a") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")


# ---------------------------------------------------------------- Phase A / B
def do_chunks(a) -> int:
    src = Path(a.source).read_text(encoding="utf-8").splitlines()
    rows = [l.split("\t") for l in Path(a.index).read_text().splitlines() if l and not l.startswith("#")]
    rows = [(r[0], int(r[1]), int(r[2])) for r in rows if r[0].isdigit()]
    sub = "candidates" if a.phase == "A" else "enumerations"
    prompt = (PROMPTS / ("pass1-candidates.md" if a.phase == "A" else "pass2-enumerations.md")).read_text()
    outdir = Path(a.outdir) / sub
    outdir.mkdir(parents=True, exist_ok=True)

    def work(row):
        cid, s, e = row
        out = outdir / f"chunk_{cid}.md"
        if out.exists() and out.stat().st_size > 0:
            return cid, "skip"
        text = "\n".join(src[s - 1:e])
        if a.phase == "A":
            user = f"Source commentary: {a.id}. Input text chunk (lines {s}–{e}):\n\n{text}"
        else:
            user = (f"Source commentary: {a.id}. Input text chunk (lines {s}–{e}).\n"
                    "Isolate ONLY the division-announcement clauses (start at the topic being divided, "
                    "stop at the closing count/list marker); do NOT copy the commentary body that explains "
                    "each part. Copy verbatim; add no interpretation.\n\n" + text)
        resp, model = call(prompt, user, timeout=480)
        resp = unfence(resp)
        if a.phase == "A":
            body = "<!-- no candidates -->" if resp.strip() == "NO CANDIDATES" else resp
            out.write_text(f"<!-- chunk {cid} | lines {s}–{e} | source: {a.id} -->\n\n{body}\n", encoding="utf-8")
        else:
            out.write_text(resp + "\n", encoding="utf-8")
        log(f"{a.id} {a.phase} chunk {cid} ok ({model})")
        return cid, model

    fails = 0
    with cf.ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(work, r): r for r in rows}
        for f in cf.as_completed(futs):
            try:
                f.result()
            except Exception as e:  # noqa: BLE001
                fails += 1
                log(f"{a.id} {a.phase} chunk {futs[f][0]} FAILED: {e}")
    print(f"{a.id} phase {a.phase}: {len(rows) - fails}/{len(rows)} chunks present, {fails} failed")
    return fails


# ---------------------------------------------------------------- Phase C
def do_tree(a) -> int:
    prompt = (PROMPTS / "pass3-tree.md").read_text()
    user = (f'Build the full nested decimal TOC for commentary "{a.id}" from the candidates below, '
            "reconciled against the enumerations below. Output only the tree block, starting with "
            "`## དཀར་ཆག / Table of Contents`.\n\n=== CANDIDATES ===\n"
            + Path(a.cand).read_text() + "\n\n=== ENUMERATIONS ===\n" + Path(a.enum).read_text())
    resp, model = call(prompt, user)
    Path(a.out).write_text(f"---\nsource: {a.id}\nskill: toc-generate\nstage: toc-tree\nmodel: {model}\n---\n\n"
                           + unfence(resp) + "\n", encoding="utf-8")
    log(f"{a.id} C tree ok ({model})")
    print(a.out, model)
    return 0


# ---------------------------------------------------------------- Phase D repair
def do_repair(a) -> int:
    prompt = (PROMPTS / "pass4-qc-repair.md").read_text()
    tree_path = Path(a.tree)
    tree_txt = tree_path.read_text()
    fm = re.match(r"^---\n.*?\n---\n\n?", tree_txt, re.S)
    head = fm.group(0) if fm else ""
    parts = [f'Correct the tree for commentary "{a.id}", fixing every issue in both QC reports, against the '
             "enumerations, the candidates and the source commentary itself — the source is the final "
             "authority when it and the candidates disagree. Output ONLY the corrected tree block.",
             "=== TREE ===\n" + tree_txt[len(head):]]
    for q in a.qc:
        parts.append(f"=== QC REPORT {Path(q).name} ===\n" + Path(q).read_text())
    parts.append("=== ENUMERATIONS ===\n" + Path(a.enum).read_text())
    parts.append("=== CANDIDATES ===\n" + Path(a.cand).read_text())
    src = Path(a.source).read_text(encoding="utf-8").splitlines()
    qc_text = "\n".join(Path(q).read_text() for q in a.qc) + tree_txt
    hits = {int(x) for x in re.findall(r"(?:\[\[|line |L)(\d+)", qc_text) if 0 < int(x) <= len(src)}
    keep = sorted({i for h in hits for i in range(max(1, h - 15), min(len(src), h + 15) + 1)})
    chunks, prev = [], None
    for i in keep:
        if prev is not None and i != prev + 1:
            chunks.append("[…]")
        if src[i - 1].strip():
            chunks.append(f"{i}\t{src[i - 1]}")
        prev = i
    parts.append("=== SOURCE COMMENTARY EXCERPTS (±15 lines around every line the tree and QC reports "
                 "point to; each line prefixed with its 1-based line number and a tab; […] = gap) ===\n"
                 + "\n".join(chunks))
    resp, model = call(prompt, "\n\n".join(parts))
    tree_path.write_text(head + unfence(resp) + "\n", encoding="utf-8")
    log(f"{a.id} D repair ok ({model})")
    print(a.tree, model)
    return 0


# ---------------------------------------------------------------- segmented Phase C / D
# A full tree for these commentaries exceeds Gemini's 65,536-token output ceiling
# (measured: 1,315-node tree = 68,551 tokens), so C and D run over segments.
NODE_LINE = re.compile(r"^(?P<ind>[ \t]*)\*[ \t]+(?P<dec>\d+(?:\.\d+)*)\.?[ \t]+(?P<title>.*?)[ \t]*(?:\[\[(?:\d+|\?)\]\])?[ \t]*$")


def chunk_blocks(cand_dir: Path) -> list[tuple[str, list[str]]]:
    """Per-chunk SECTION_TITLE/ITEMS blocks, CONTEXT dropped, overlap duplicates removed."""
    out, prev = [], set()
    for f in sorted(cand_dir.glob("chunk_*.md")):
        blocks = [b.strip() for b in re.findall(r"(?ms)^SECTION_TITLE:.*?(?=^CONTEXT:|^SECTION_TITLE:|^<!--|\Z)", f.read_text())]
        cur = set(blocks)
        out.append((f.stem.split("_")[1], [b for b in blocks if b not in prev]))
        prev = cur
    return out


def chunk_enums(enum_dir: Path) -> dict[str, str]:
    d = {}
    for f in sorted(enum_dir.glob("chunk_*.md")):
        s = f.read_text().strip()
        if s and s != "NO ENUMERATIONS":
            d[f.stem.split("_")[1]] = s
    return d


def parse_nodes(lines: list[str]):
    res = []
    for l in lines:
        m = NODE_LINE.match(l)
        if m and l.lstrip().startswith("*"):
            res.append((tuple(int(x) for x in m.group("dec").split(".")), m.group("title").strip(), l.rstrip()))
    return res


def fmt(dec, title):
    return "   " * (len(dec) - 1) + "* " + ".".join(map(str, dec)) + " " + title


def open_branch_view(nodes, max_sibs=15) -> str:
    if not nodes:
        return "(the tree is empty — this is the first segment)"
    last = nodes[-1][0]
    out = []
    for d in range(1, len(last) + 1):
        parent = last[:d - 1]
        sibs = [(dec, ti) for dec, ti, _ in nodes if len(dec) == d and dec[:d - 1] == parent]
        if len(sibs) > max_sibs:
            out.append("   " * (d - 1) + f"… ({len(sibs) - max_sibs} earlier siblings omitted)")
            sibs = sibs[-max_sibs:]
        out += [fmt(dec, ti) for dec, ti in sibs]
    return "\n".join(out)


def do_tree_seg(a) -> int:
    prompt = (PROMPTS / "pass3-tree.md").read_text()
    blocks = chunk_blocks(Path(a.cand_dir))
    enums = chunk_enums(Path(a.enum_dir))
    segs, cur, n = [], [], 0
    for cid, bl in blocks:
        cur.append((cid, bl)); n += len(bl)
        if n >= a.seg_blocks:
            segs.append(cur); cur, n = [], 0
    if cur:
        segs.append(cur)
    segdir = Path(a.out + ".segments"); segdir.mkdir(exist_ok=True)
    tree: list[str] = []
    model = None
    for i, seg in enumerate(segs, 1):
        sf = segdir / f"seg_{i:03d}.md"
        if not sf.exists():
            nodes = parse_nodes(tree)
            cids = [c for c, _ in seg]
            prev_cids = [c for c, _ in segs[i - 2]][-1:] if i > 1 else []
            cand = "\n\n".join(b for _, bl in seg for b in bl) or "(no candidates in this segment)"
            en = "\n\n".join(f"<!-- chunk {c} -->\n{enums[c]}" for c in prev_cids + cids if c in enums) or "(none)"
            user = (
                f'Commentary "{a.id}". Its full tree is too large to emit in one response, so you are building '
                f"it in consecutive SEGMENTS, in document order. This is segment {i} of {len(segs)}.\n\n"
                "=== TREE SO FAR — the open branches (every ancestor of the most recent entry, each shown with "
                "its children so far) ===\n" + open_branch_view(nodes) + "\n\n"
                "=== TREE SO FAR — the last 25 entries in document order ===\n"
                + ("\n".join(l for _, _, l in nodes[-25:]) or "(empty)") + "\n\n"
                "TASK: continue the SAME tree. Output ONLY the new entries for the sections that the candidates "
                "below open, continuing the decimal numbering and nesting from the tree so far — a new entry may be "
                "a child or later sibling of any open branch shown above. Do NOT repeat entries already in the tree. "
                "Add a gap-filling node (rule B) only for a part that is OPENED within this segment; parts announced "
                "here but opened later belong to a later segment. All FORMAT RULES apply. Output no heading, no "
                "commentary — bullet entries only.\n\n"
                f"=== CANDIDATES (this segment: chunks {cids[0]}–{cids[-1]}) ===\n{cand}\n\n"
                f"=== ENUMERATIONS (this segment, plus the previous chunk for context) ===\n{en}\n")
            resp, model = call(prompt, user, timeout=900)
            new = [l.rstrip() for l in unfence(resp).splitlines() if NODE_LINE.match(l) and l.lstrip().startswith("*")]
            sf.write_text("\n".join(new) + "\n", encoding="utf-8")
            log(f"{a.id} C segment {i}/{len(segs)} ok: {len(new)} entries ({model})")
        tree += [l for l in sf.read_text(encoding="utf-8").splitlines() if l.strip()]
    Path(a.out).write_text(f"---\nsource: {a.id}\nskill: toc-generate\nstage: toc-tree\nmodel: {model or 'gemini'}\n"
                           f"phase_c: segmented ({len(segs)} segments)\n---\n\n## དཀར་ཆག / Table of Contents\n\n"
                           + "\n".join(tree) + "\n", encoding="utf-8")
    log(f"{a.id} C tree ok (segmented, {len(segs)} segments, {len(tree)} entries)")
    print(a.out, len(segs), len(tree))
    return 0


def do_repair_seg(a) -> int:
    prompt = (PROMPTS / "pass4-qc-repair.md").read_text()
    tp = Path(a.tree); txt = tp.read_text(encoding="utf-8")
    lines = txt.splitlines()
    node_idx = [i for i, l in enumerate(lines) if l.lstrip().startswith("*") and NODE_LINE.match(l)]
    decs = {NODE_LINE.match(lines[i]).group("dec"): k for k, i in enumerate(node_idx)}
    issues = []
    for q in a.qc:
        issues += [l for l in Path(q).read_text().splitlines() if l.startswith("- ")]
    win = a.window
    nwin = (len(node_idx) + win - 1) // win
    per_win: dict[int, list[str]] = {}
    for iss in issues:
        hit = set()
        for d in re.findall(r"(?<![\d.])(\d+(?:\.\d+)+|\d+)(?=[ ,)])", iss):
            if d in decs:
                hit.add(decs[d] // win)
        for w in hit:
            per_win.setdefault(w, []).append(iss)
    src = Path(a.source).read_text(encoding="utf-8").splitlines()
    idx_rows = [r.split("\t") for r in Path(a.index).read_text().splitlines() if r[:1].isdigit()]
    blocks = dict(chunk_blocks(Path(a.cand_dir))); enums = chunk_enums(Path(a.enum_dir))

    def work(w):
        lo, hi = w * win, min(len(node_idx), (w + 1) * win)
        wl = [lines[node_idx[k]] for k in range(lo, hi)]
        ptrs = [int(p) for l in wl for p in re.findall(r"\[\[(\d+)\]\]", l)]
        plo, phi = (min(ptrs), max(ptrs)) if ptrs else (1, len(src))
        cids = [c for c, s, e in idx_rows if int(e) >= plo and int(s) <= phi]
        hits = {int(x) for iss in per_win[w] for x in re.findall(r"(?:\[\[|line |L)(\d+)", iss)
                if 0 < int(x) <= len(src)}
        keep = sorted({i for h in hits for i in range(max(1, h - 15), min(len(src), h + 15) + 1)})
        ex, prev = [], None
        for i in keep:
            if prev is not None and i != prev + 1:
                ex.append("[…]")
            if src[i - 1].strip():
                ex.append(f"{i}\t{src[i - 1]}")
            prev = i
        before = [lines[node_idx[k]] for k in range(max(0, lo - 5), lo)]
        after = [lines[node_idx[k]] for k in range(hi, min(len(node_idx), hi + 5))]
        user = (f'Correct the tree for commentary "{a.id}". The tree is too large for one response, so you are '
                f"repairing ONE WINDOW of it (entries {lo + 1}–{hi} of {len(node_idx)}). Fix every issue listed for "
                "this window against the enumerations, the candidates and the source excerpts — the source is the "
                "final authority. Output ONLY the corrected entries of this window, in the same shape as the input "
                "(you may add, drop, renumber or re-nest entries inside the window). Do NOT output the read-only "
                "context entries and do not renumber anything outside the window.\n\n"
                "=== READ-ONLY CONTEXT: the 5 entries before the window ===\n" + ("\n".join(before) or "(start of tree)")
                + "\n\n=== WINDOW TO CORRECT ===\n" + "\n".join(wl)
                + "\n\n=== READ-ONLY CONTEXT: the 5 entries after the window ===\n" + ("\n".join(after) or "(end of tree)")
                + "\n\n=== QC ISSUES FOR THIS WINDOW ===\n" + "\n".join(per_win[w])
                + "\n\n=== ENUMERATIONS (source lines of this window) ===\n"
                + ("\n\n".join(enums[c] for c in cids if c in enums) or "(none)")
                + "\n\n=== CANDIDATES (source lines of this window) ===\n"
                + ("\n\n".join(b for c in cids for b in blocks.get(c, [])) or "(none)")
                + "\n\n=== SOURCE EXCERPTS (±15 lines around each line the issues cite; line number, tab, text; […] = gap) ===\n"
                + "\n".join(ex))
        resp, model = call(prompt, user, timeout=900)
        new = [l.rstrip() for l in unfence(resp).splitlines() if l.lstrip().startswith("*") and NODE_LINE.match(l)]
        if not new:
            raise RuntimeError("empty repair output")
        log(f"{a.id} D repair window {w + 1}/{nwin}: {len(per_win[w])} issues, {len(wl)} -> {len(new)} entries ({model})")
        return w, new

    results = {}
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for fut in cf.as_completed([ex.submit(work, w) for w in sorted(per_win)]):
            try:
                w, new = fut.result(); results[w] = new
            except Exception as e:  # noqa: BLE001
                log(f"{a.id} D repair window FAILED: {e}")
    out, k = [], 0
    first, last = node_idx[0], node_idx[-1]
    out += lines[:first]
    for w in range(nwin):
        lo, hi = w * win, min(len(node_idx), (w + 1) * win)
        out += results.get(w, [lines[node_idx[j]] for j in range(lo, hi)])
    out += lines[last + 1:]
    tp.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"repaired {len(results)}/{len(per_win)} windows with issues")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    c = sp.add_parser("chunks")
    c.add_argument("--phase", choices=["A", "B"], required=True)
    for k in ("source", "index", "outdir", "id"):
        c.add_argument(f"--{k}", required=True)
    c.add_argument("--workers", type=int, default=8)
    t = sp.add_parser("tree")
    for k in ("cand", "enum", "id", "out"):
        t.add_argument(f"--{k}", required=True)
    r = sp.add_parser("repair")
    for k in ("tree", "cand", "enum", "source", "id"):
        r.add_argument(f"--{k}", required=True)
    r.add_argument("--qc", nargs="+", required=True)
    ts = sp.add_parser("tree-seg")
    for k in ("cand-dir", "enum-dir", "id", "out"):
        ts.add_argument(f"--{k}", required=True)
    ts.add_argument("--seg-blocks", type=int, default=120)
    rs = sp.add_parser("repair-seg")
    for k in ("tree", "cand-dir", "enum-dir", "index", "source", "id"):
        rs.add_argument(f"--{k}", required=True)
    rs.add_argument("--qc", nargs="+", required=True)
    rs.add_argument("--window", type=int, default=200)
    rs.add_argument("--workers", type=int, default=4)
    a = p.parse_args()
    return {"chunks": do_chunks, "tree": do_tree, "repair": do_repair,
            "tree-seg": do_tree_seg, "repair-seg": do_repair_seg}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
