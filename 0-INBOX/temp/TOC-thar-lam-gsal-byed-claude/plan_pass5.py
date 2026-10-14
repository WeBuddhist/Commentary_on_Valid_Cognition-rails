"""Plan pass-5 anchoring windows. Each tree node is located (monotone) on the pass-1
candidate whose SECTION_TITLE matches it; the candidate's chunk gives a source line range.
The tree is then cut into contiguous segments, each with a source line window.
Planning aid only — the anchors themselves are written by the pass-5 subagents.

usage: python plan_pass5.py <tree.md> <candidates.md> <chunk-index.tsv> <out.tsv> [max_nodes] [max_lines]
"""
import re, sys

SHAD = "།༎༏༐༑༒༔"
ORD = (r"^(དང་པོ|གཉིས་པ|གསུམ་པ|བཞི་པ|ལྔ་པ|དྲུག་པ|བདུན་པ|བརྒྱད་པ|དགུ་པ|བཅུ་པ|"
       r"བཅུ་གཅིག་པ|བཅུ་གཉིས་པ|བཅུ་གསུམ་པ|བཅུ་བཞི་པ|བཅོ་ལྔ་པ)་")

def canon(s):
    s = re.sub(r"\[\[[^\]]*\]\]", "", s)
    s = re.sub("[" + SHAD + r"\s]+", "་", s)
    s = re.sub("་+", "་", s)
    return s.strip("་")

tree_path, cand_path, idx_path, out_path = sys.argv[1:5]
max_nodes = int(sys.argv[5]) if len(sys.argv) > 5 else 130
max_lines = int(sys.argv[6]) if len(sys.argv) > 6 else 320

chunks = {}
for line in open(idx_path, encoding="utf-8"):
    f = line.rstrip("\n").split("\t")
    if len(f) == 3 and f[0].isdigit():
        chunks[int(f[0])] = (int(f[1]), int(f[2]))
total_lines = max(e for _, e in chunks.values())

cands = []                     # (chunk, full canon, core canon)
chunk = 0
for line in open(cand_path, encoding="utf-8"):
    m = re.match(r"<!-- chunk (\d+)", line)
    if m:
        chunk = int(m.group(1))
    elif line.startswith("SECTION_TITLE:"):
        t = canon(line.split(":", 1)[1])
        cands.append((chunk, t, re.sub(ORD, "", t)))

NODE = re.compile(r"^(\s*)\*\s+(\d+(?:\.\d+)*)\.?\s+(.+?)\s*$")
nodes = []
for i, raw in enumerate(open(tree_path, encoding="utf-8").read().splitlines(), 1):
    m = NODE.match(raw)
    if m:
        t = canon(m.group(3))
        nodes.append({"tline": i, "dec": m.group(2), "full": t, "core": re.sub(ORD, "", t)})

cur = 0
for n in nodes:
    hit = None
    for key in ("full", "core"):
        for j in range(cur, min(len(cands), cur + 80)):
            c = cands[j]
            if (c[1] if key == "full" else c[2]) == n[key] and len(n[key]) > 3:
                hit = j
                break
        if hit is not None:
            break
    n["cand"] = hit
    if hit is not None:
        cur = hit

last = 0
for n in nodes:
    if n["cand"] is not None:
        last = cands[n["cand"]][0]
    n["chunk"] = last

def lines_of(ch):
    return chunks[ch]

segs, start = [], 0
for i in range(1, len(nodes) + 1):
    if i == len(nodes):
        segs.append((start, i - 1)); break
    span = lines_of(nodes[i]["chunk"])[1] - lines_of(nodes[start]["chunk"])[0]
    if i - start >= max_nodes or (span > max_lines and i - start >= 10):
        segs.append((start, i - 1)); start = i

with open(out_path, "w", encoding="utf-8") as f:
    f.write("seg\tfirst_dec\tlast_dec\ttree_from\ttree_to\tnodes\tsrc_from\tsrc_to\tlocated\n")
    for k, (a, b) in enumerate(segs):
        lo = lines_of(nodes[a]["chunk"])[0]
        hi = lines_of(nodes[b + 1]["chunk"])[1] if b + 1 < len(nodes) else total_lines
        if b + 1 == len(nodes):
            hi = total_lines
        loc = sum(1 for n in nodes[a:b + 1] if n["cand"] is not None)
        f.write(f"{k:02d}\t{nodes[a]['dec']}\t{nodes[b]['dec']}\t{nodes[a]['tline']}\t"
                f"{nodes[b]['tline']}\t{b - a + 1}\t{lo}\t{hi}\t{loc}\n")
print(f"{len(nodes)} nodes, {sum(1 for n in nodes if n['cand'] is not None)} located, "
      f"{len(segs)} segments -> {out_path}")
