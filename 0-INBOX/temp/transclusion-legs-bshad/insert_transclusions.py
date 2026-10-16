"""Insert root-text transclusions before commentary blocks, from place-*.tsv files.

usage: python -I insert_transclusions.py SOURCE.md OUT.md place-P1.tsv [place-P2.tsv …]

For every distinct `line` (first line of a commentary block) the rows' root blocks are written as one
group directly before that block, in root-text order, one `![[1-SOURCES/Text/ཚད་མ་རྣམ་འགྲེལ།.md#^ID]]`
per line, no blank line inside the group, one blank line before and after the group. Nothing else in
the file changes; the script checks that the output minus the inserted lines (and the blank lines
added around them) equals the input, and that every root id exists.
"""
import csv, re, sys, pathlib

HERE = pathlib.Path(__file__).resolve().parent
VAULT = HERE.parents[2]
ROOT_REL = "1-SOURCES/Text/ཚད་མ་རྣམ་འགྲེལ།.md"
ROOT = VAULT / ROOT_REL

src, out = sys.argv[1], sys.argv[2]
raw = open(src, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in raw[:3000] else "\n"
L = raw.split(nl)

root_order = {m.group(1): k for k, m in enumerate(re.finditer(r"\^([\w-]+)\s*$", ROOT.read_text(encoding="utf-8"), re.M))}

groups = {}
for p in sys.argv[3:]:
    for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"):
        rid = r["root_block"].lstrip("^")
        assert rid in root_order, f"{p}: unknown root block {rid}"
        groups.setdefault(int(r["line"]), set()).add(rid)

new, inserted, active, skipped = [], 0, None, 0
for i, l in enumerate(L, 1):
    if l.startswith("#"):
        active = None                            # a heading ends the parser's scope
    if i in groups:
        assert l.strip() and not l.startswith("#") and (i == 1 or not L[i - 2].strip() or L[i - 2].startswith("#")), \
            f"line {i} is not the first line of a content block"
        if frozenset(groups[i]) == active:       # same root blocks already in scope: a repeat adds nothing
            skipped += 1
        else:
            if new and new[-1].strip():
                new.append("")                   # blank line before the group (after a heading)
            for rid in sorted(groups[i], key=root_order.get):
                new.append(f"![[{ROOT_REL}#^{rid}]]"); inserted += 1
            new.append("")                       # blank line between the group and the block
            active = frozenset(groups[i])
    new.append(l)

# integrity: drop the inserted links and collapse blank runs → must equal the input with blank runs collapsed
def norm(lines):
    out_, prev_blank = [], False
    for x in lines:
        if x.startswith(f"![[{ROOT_REL}#^"):
            continue
        b = not x.strip()
        if b and prev_blank:
            continue
        out_.append(x); prev_blank = b
    return out_
assert norm(new) == norm(L), "non-transclusion content changed"
open(out, "w", encoding="utf-8", newline="").write(nl.join(new))
print(f"blocks with a group: {len(groups) - skipped} (repeats of the group in scope skipped: {skipped}), transclusion lines: {inserted}, output: {out}")
