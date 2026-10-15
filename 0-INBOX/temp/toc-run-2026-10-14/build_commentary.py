#!/usr/bin/env python3
"""Build the headed + block-ID'd commentary from an anchored TOC tree (pass 5 output).

Same steps as 0-INBOX/temp/TOC-thar-lam-gsal-byed-claude/build_headed.sh, parameterised, plus the
ADAPTIVE cut used for ཐར་ལམ་གསལ་བྱེད་ (2026-10-14): a section is opened into its subsections only
while it is longer than --min-syl syllables, down to --max-depth; frame nodes are always kept.

  titled source -> (optional extra front frame) -> full-depth trial ingest to measure sections ->
  adaptive tree -> ingest (split at openers, frame nodes) -> stamp body IDs with the strict text gate
  -> re-stack first-child heading runs -> gate again -> heading '#' count = ID segments (bold > 6)

Run from the vault root:
  python build_commentary.py --id X --source S --tree T --out O --title line
  python build_commentary.py ... --title "editorial:<title>" --front-frame "ཀླད་ཀྱི་དོན།"
"""
import argparse
import collections
import json
import re
import subprocess
import sys
from pathlib import Path

LIB = "4-SYSTEM/Skills/seg-toc-lib"
PY = [sys.executable, "-X", "utf8"]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--source", required=True)
ap.add_argument("--tree", required=True, help="anchored full tree")
ap.add_argument("--out", required=True)
ap.add_argument("--title", default="line", help="'line' (first paragraph becomes '# …') or 'editorial:<text>'")
ap.add_argument("--front-frame", default="", help="label of an extra frame I. over the opening title paragraph")
ap.add_argument("--min-syl", type=int, default=2500)
ap.add_argument("--max-depth", type=int, default=16)
a = ap.parse_args()

W = Path(f"0-INBOX/temp/TOC-{a.id}/build")
W.mkdir(parents=True, exist_ok=True)


def run(cmd, log=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if log:
        Path(log).write_text(r.stdout + r.stderr, encoding="utf-8")
    return r


# 1. titled source (the reference for the text gate)
src = Path(a.source).read_text(encoding="utf-8")
m = re.match(r"(---\n.*?\n---\n\s*)(.*)", src, re.S)
head, body = m.group(1), m.group(2)
if a.title == "line":
    first = body.split("\n\n", 1)[0]
    assert "\n" not in first.strip(), "first paragraph is not a single line"
    titled = head + "# " + body
else:
    titled = head + "# " + a.title.split(":", 1)[1] + "\n\n" + body
(W / "titled.md").write_text(titled, encoding="utf-8")

# 2. tree: optional extra front frame I. over the title paragraph (existing romans shift by one)
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
tree = Path(a.tree).read_text(encoding="utf-8").splitlines()
if a.front_frame:
    p0 = body.split("\n\n", 1)[0].strip().split("\n")[0]
    ctx = p0[:40]
    out, inserted = [], False
    for l in tree:
        mm = re.match(r"^(\s*\*\s+)([IVX]+)(\.?)(\s.*)$", l)
        if mm and mm.group(2) in ROMAN:
            if not inserted:
                out.append(f"* I. {a.front_frame} [[{ctx}]]")
                inserted = True
            l = mm.group(1) + ROMAN[ROMAN.index(mm.group(2)) + 1] + mm.group(3) + mm.group(4)
        out.append(l)
    assert inserted, "no front frame node found to insert before"
    tree = out
(W / "tree-full.md").write_text("\n".join(tree) + "\n", encoding="utf-8")

# 3. full-depth trial ingest, measure each node's section in syllables
full = W / "trial-full.md"
full.write_text(titled, encoding="utf-8")
run(PY + [f"{LIB}/toc_tree_ingest.py", "parse", "--input", str(W / "tree-full.md"), "--out", str(W / "tree-full.json")])
r = run(PY + [f"{LIB}/toc_tree_ingest.py", "ingest", "--tree", str(W / "tree-full.json"), "--commentary", str(full),
              "--split-frame-nodes"], log=W / "ingest-trial.log")
print("trial ingest:", " | ".join(l.strip() for l in (r.stdout + r.stderr).splitlines()
                                   if re.search(r"Not found|Integrity|REORDER|Inserted", l))[:400])
H = re.compile(r"^#{2,}\s+.*?\^([\w-]+)-0\s*$")
L = full.read_text(encoding="utf-8").split("\n")
heads = [(i, H.match(l).group(1)) for i, l in enumerate(L) if H.match(l)]
syl = {}
for k, (i, hid) in enumerate(heads):
    end = len(L)
    for j, hid2 in heads[k + 1:]:
        if not (hid2 + "-").startswith(hid + "-"):
            end = j
            break
    text = "\n".join(x for x in L[i:end] if not x.startswith("#"))
    syl[hid] = len(re.findall(r"[^\s་།༌]+", re.sub(r"\^[\w-]+", "", text)))

# 4. adaptive subset
NODE = re.compile(r"^\s*\*\s+([\dIVXa-z]+(?:\.\d+)*)\.?\s")
keep_dec = set()
kept = []
for l in tree:
    mm = NODE.match(l)
    if not mm:
        continue
    dec = mm.group(1)
    parts = dec.split(".")
    if not parts[0].isdigit():                       # frame node
        keep = True
    elif len(parts) == 1:
        keep = True
    else:
        par = ".".join(parts[:-1])
        keep = par in keep_dec and syl.get(par.replace(".", "-"), 0) > a.min_syl and len(parts) <= a.max_depth
    if keep:
        keep_dec.add(dec)
        kept.append(l)
sub = W / f"tree-adaptive{a.min_syl}-max{a.max_depth}.md"
sub.write_text("## དཀར་ཆག / Table of Contents\n\n" + "\n".join(kept) + "\n", encoding="utf-8")
print(f"adaptive tree: {len(kept)} of {sum(1 for l in tree if NODE.match(l))} nodes")

# 5. build: ingest + stamp with the strict gate
out = Path(a.out)
out.write_text(titled, encoding="utf-8")
run(PY + [f"{LIB}/toc_tree_ingest.py", "parse", "--input", str(sub), "--out", str(W / "tree.json")])
r = run(PY + [f"{LIB}/toc_tree_ingest.py", "ingest", "--tree", str(W / "tree.json"), "--commentary", str(out),
              "--split-frame-nodes"], log=W / "ingest.log")
print("ingest:", " | ".join(l.strip() for l in (r.stdout + r.stderr).splitlines()
                             if re.search(r"Not found|not found|Integrity|REORDER|split at a node", l))[:600])
r = run(PY + [f"{LIB}/toc_tree_ingest.py", "ingest", "--tree", str(W / "tree.json"), "--commentary", str(out),
              "--split-frame-nodes", "--stamp-body-ids", "--verify-against", str(W / "titled.md")], log=W / "stamp.log")
print("stamp: exit", r.returncode, "|", ((r.stdout + r.stderr).strip().splitlines() or [""])[-1][:160])
if r.returncode not in (0,):
    sys.exit("stamping failed — see " + str(W / "stamp.log"))

# 6. re-stack first-child heading runs that fell after a mid-list paragraph break (as build_headed.sh)
paras = out.read_text(encoding="utf-8").split("\n\n")
ish = lambda x: re.match(r"^#{2,}\s", x.strip()) is not None
moved = i = 0
while i < len(paras):
    if ish(paras[i]):
        j = i
        while j < len(paras) and ish(paras[j]):
            j += 1
        prev = paras[i - 1].strip() if i else ""
        bodyp = re.sub(r"\s+\^[\w-]+$", "", prev)
        if prev and not ish(paras[i - 1]) and re.search(r"དང[༌་]།$", bodyp) and i >= 2 and ish(paras[i - 2]):
            run_ = paras[i:j]
            paras[i:j] = []
            paras[i - 1:i - 1] = run_
            moved += 1
        i = j
    else:
        i += 1
out.write_text("\n\n".join(paras), encoding="utf-8")
print("first-child heading runs re-stacked:", moved)
r = run(PY + [f"{LIB}/verify_text.py", str(W / "titled.md"), str(out)])
print("verify_text:", (r.stdout + r.stderr).strip().splitlines()[-1][:160] if (r.stdout + r.stderr).strip() else r.returncode)
(W / "pre-levels.md").write_text(out.read_text(encoding="utf-8"), encoding="utf-8")

# 7. heading level = ID segments, bold beyond six
L = out.read_text(encoding="utf-8").split("\n")
HH = re.compile(r"^(#{2,})\s+(.*?)\s+\^([\w-]+)\s*$")
c = 0
for k, l in enumerate(L):
    mm = HH.match(l)
    if mm:
        n = len(mm.group(3).split("-"))
        t = mm.group(2)
        t = t[2:-2] if t.startswith("**") and t.endswith("**") else t
        new = f"{'#' * n} {('**' + t + '**') if n > 6 else t} ^{mm.group(3)}"
        c += new != l
        L[k] = new
out.write_text("\n".join(L), encoding="utf-8")
pre = (W / "pre-levels.md").read_text(encoding="utf-8").split("\n")
strip_h = lambda xs: [x for x in xs if not re.match(r"^#+ ", x)]
norm_h = lambda xs: [re.sub(r"\*\*", "", re.sub(r"^#+ ", "", x)) for x in xs if re.match(r"^#+ ", x)]
print("heading levels rewritten:", c, "| non-heading lines identical:", strip_h(pre) == strip_h(L),
      "| heading titles+IDs identical:", norm_h(pre) == norm_h(L))
Hs = [l for l in L if re.match(r"^#{2,}\s", l)]
ids = re.findall(r"\^([\w-]+)\s*$", "\n".join(L), re.M)
bad = [l for l in Hs if len(re.search(r"\^([\w-]+)\s*$", l).group(1).split("-")) != len(re.match(r"^#+", l).group(0))]
print("headings", len(Hs), "| level mismatches", len(bad), "| max #", max(len(re.match(r"^#+", l).group(0)) for l in Hs),
      "| block IDs", len(ids), "| duplicates", sum(1 for v in collections.Counter(ids).values() if v > 1))
json.dump({"syl": syl}, open(W / "section-syllables.json", "w", encoding="utf-8"), ensure_ascii=False)
