"""Find verbatim root-text quotations in a commentary (syllable n-gram match).

usage: root_quotes.py ROOT.md COMMENTARY.md OUT.tsv [--n 6]
Writes one row per (commentary block, root block) match:
  line  cblock  root_block  longest_run  root_len  preview
"line" is the 1-based line of the commentary block's first line in the file.
"""
import re, sys, argparse, collections

ap = argparse.ArgumentParser()
ap.add_argument("root"); ap.add_argument("comm"); ap.add_argument("out")
ap.add_argument("--n", type=int, default=6)
a = ap.parse_args()

TOK = re.compile(r"[^\s་༌།༎༏༐༑༔༄༅༈\*\[\]\^:()!,#]+")
BID = re.compile(r"\^([\w-]+)\s*$")


def blocks(path):
    L = open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    i = 0
    if L and L[0].strip() == "---":
        i = next(k for k in range(1, len(L)) if L[k].strip() == "---") + 1
    out, cur, start = [], [], None
    for k in range(i, len(L) + 1):
        l = L[k] if k < len(L) else ""
        if l.strip():
            if not cur: start = k + 1
            cur.append(l)
        elif cur:
            out.append((start, cur)); cur = []
    res = []
    for start, ls in out:
        if ls[0].startswith("#") or ls[0].startswith("![["):
            continue
        m = BID.search(ls[-1])
        res.append((start, m.group(1) if m else "", TOK.findall(" ".join(ls))))
    return res


root = blocks(a.root)
idx = collections.defaultdict(set)
for _, rid, toks in root:
    for k in range(len(toks) - a.n + 1):
        idx[tuple(toks[k:k + a.n])].add(rid)
rlen = {rid: len(t) for _, rid, t in root}

rows = []
for line, cid, toks in blocks(a.comm):
    hits = collections.defaultdict(list)       # rid -> positions matched
    for k in range(len(toks) - a.n + 1):
        for rid in idx.get(tuple(toks[k:k + a.n]), ()):
            hits[rid].append(k)
    for rid, ps in hits.items():
        # longest run of consecutive n-gram starts = matched span length
        best = run = 1
        for x, y in zip(ps, ps[1:]):
            run = run + 1 if y == x + 1 else 1
            best = max(best, run)
        span = best + a.n - 1
        if len(idx_rids := {r for k in range(ps[0], ps[0] + 1) for r in idx[tuple(toks[k:k + a.n])]}) > 6 and span < 10:
            continue                            # common formula shared by many root blocks
        k0 = ps[0]
        rows.append((line, cid, rid, span, rlen[rid], "་".join(toks[max(0, k0 - 3):k0 + span + 2])))
with open(a.out, "w", encoding="utf-8") as f:
    f.write("line\tcblock\troot_block\tmatched_syllables\troot_block_syllables\tpreview\n")
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
cb = {r[1] for r in rows}
print(f"commentary blocks: {len(blocks(a.comm))}, with a root quote: {len(cb)}, match rows: {len(rows)}, root blocks quoted: {len({r[2] for r in rows})} of {len(root)}")
