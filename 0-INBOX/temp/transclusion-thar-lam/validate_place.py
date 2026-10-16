"""Validate a place-*.tsv for the Rin chen phreng ba stod transclusion run.

usage: python -I validate_place.py place-P1.tsv P1
Checks: header; every `line` is the FIRST line of a content block of source.md (not a heading,
not blank, not inside a block) and inside the part's range; root_block exists in the root text;
kind is lemma|gloss|proof; no duplicate (line, root_block). Exit code = number of problems.
"""
import csv, re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
VAULT = HERE.parents[2]
SRC = HERE / "source.md"
ROOT = VAULT / "1-SOURCES" / "Text" / "ཚད་མ་རྣམ་འགྲེལ།.md"

place, part = sys.argv[1], sys.argv[2]
rng = {r["part"]: (int(r["start_line"]), int(r["end_line"]))
       for r in csv.DictReader(open(HERE / "parts.tsv", encoding="utf-8"), delimiter="\t")}[part]
L = SRC.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
starts = set()
for i, l in enumerate(L):
    if l.strip() and not l.startswith("#") and not l.startswith("![[") and (i == 0 or not L[i - 1].strip() or L[i - 1].startswith("#")):
        starts.add(i + 1)
root_ids = set(re.findall(r"\^([\w-]+)\s*$", ROOT.read_text(encoding="utf-8"), re.M))

problems, seen = [], set()
rows = list(csv.DictReader(open(place, encoding="utf-8"), delimiter="\t"))
need = {"heading", "root_block", "line", "kind", "words"}
if not rows or not need <= set(rows[0]):
    print(f"header must contain: {sorted(need)}"); sys.exit(1)
for n, r in enumerate(rows, 2):
    try:
        ln = int(r["line"])
    except ValueError:
        problems.append(f"row {n}: line not an integer"); continue
    if not rng[0] <= ln <= rng[1]: problems.append(f"row {n}: line {ln} outside {part} {rng}")
    if ln not in starts: problems.append(f"row {n}: line {ln} is not the first line of a content block")
    if r["root_block"] not in root_ids: problems.append(f"row {n}: root block ^{r['root_block']} not in the root text")
    if r["kind"] not in ("lemma", "gloss", "proof"): problems.append(f"row {n}: kind {r['kind']!r}")
    k = (ln, r["root_block"])
    if k in seen: problems.append(f"row {n}: duplicate {k}")
    seen.add(k)
for p in problems[:50]: print(p)
print(f"{len(rows)} rows, {len(problems)} problems")
sys.exit(len(problems))
