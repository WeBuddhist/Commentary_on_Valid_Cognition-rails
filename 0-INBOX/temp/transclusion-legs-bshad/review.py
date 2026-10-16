"""Review the place-*.tsv files of the ཐར་ལམ་ transclusion run (priority_repo.md B.6 step 3).

usage: python -I review.py            (run from the vault root)
Reports: rows per part/kind; root coverage per chapter (which root blocks were never placed);
dropped seeds with >= 12 matched syllables and a single candidate root block for that commentary
block; gloss rows whose block has a verbatim seed for the same root block (-> should be lemma);
order check (root order vs commentary order inversions per chapter); writes merged.tsv.
"""
import csv, re, pathlib, collections

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2] / "1-SOURCES" / "Text" / "ཚད་མ་རྣམ་འགྲེལ།.md"
root_ids = re.findall(r"\^([\w-]+)\s*$", ROOT.read_text(encoding="utf-8"), re.M)
root_ids = [r for r in root_ids if not r.endswith("-0") and r != "0"]
order = {r: k for k, r in enumerate(root_ids)}

rows = []
for p in sorted(HERE.glob("place-P*.tsv")):
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"):
        r["part"] = p.stem.split("-")[1]
        r["root_block"] = r["root_block"].lstrip("^")
        rows.append(r)
print(f"rows: {len(rows)} from {len({r['part'] for r in rows})} parts")
for part in sorted({r["part"] for r in rows}):
    c = collections.Counter(r["kind"] for r in rows if r["part"] == part)
    print(f"  {part}: {sum(c.values())} rows {dict(c)}")

placed = {r["root_block"] for r in rows}
print("\n== root coverage ==")
for ch in ["I", "1", "2", "3", "4", "a"]:
    ids = [r for r in root_ids if r.split("-")[0] == ch]
    miss = [r for r in ids if r not in placed]
    print(f"  ch {ch}: {len(ids) - len(miss)}/{len(ids)} placed; missing {len(miss)}: {' '.join(miss[:60])}{' …' if len(miss) > 60 else ''}")

seeds = list(csv.DictReader(open(HERE / "seeds" / "all.tsv", encoding="utf-8"), delimiter="\t"))
by_line = collections.defaultdict(set)
for s in seeds:
    by_line[s["line"]].add(s["root_block"])
have = {(r["line"], r["root_block"]) for r in rows}
print("\n== dropped strong seeds (>= 12 syllables, single candidate in that block) ==")
n = 0
for s in seeds:
    if (s["line"], s["root_block"]) in have or int(s["matched_syllables"]) < 12 or len(by_line[s["line"]]) > 1:
        continue
    placed_elsewhere = sorted({r["line"] for r in rows if r["root_block"] == s["root_block"]}, key=int)
    n += 1
    print(f"  L{s['line']} ^{s['root_block']} ({s['matched_syllables']} syl) placed at {placed_elsewhere[:4]} | {s['preview'][:70]}")
print(f"  total {n}")

print("\n== gloss rows that have a verbatim seed (-> lemma) ==")
seed_pairs = {(s["line"], s["root_block"]) for s in seeds}
relabel = [r for r in rows if r["kind"] == "gloss" and (r["line"], r["root_block"]) in seed_pairs]
for r in relabel:
    print(f"  {r['part']} L{r['line']} ^{r['root_block']}")
print(f"  total {len(relabel)}")

print("\n== order: root blocks placed out of root order (per chapter, by first placement) ==")
first = {}
for r in sorted(rows, key=lambda r: int(r["line"])):
    first.setdefault(r["root_block"], int(r["line"]))
for ch in ["1", "2", "3", "4"]:
    seq = sorted([(ln, order[rb], rb) for rb, ln in first.items() if rb.split("-")[0] == ch and rb in order])
    inv = [(a[2], b[2], a[0], b[0]) for a, b in zip(seq, seq[1:]) if b[1] < a[1] - 3]
    print(f"  ch {ch}: {len(seq)} blocks, {len(inv)} backward jumps > 3 blocks: {inv[:8]}")

with open(HERE / "merged.tsv", "w", encoding="utf-8") as f:
    f.write("part\theading\troot_block\tline\tkind\twords\n")
    for r in sorted(rows, key=lambda r: (int(r["line"]), order.get(r["root_block"], 0))):
        f.write("\t".join([r["part"], r["heading"], r["root_block"], r["line"], r["kind"], r["words"]]) + "\n")
print("\nwrote merged.tsv")
