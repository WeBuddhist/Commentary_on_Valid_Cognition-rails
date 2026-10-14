#!/usr/bin/env bash
# Build the headed + block-ID'd commentary from an anchored tree. Run from the vault root.
# usage: build_headed.sh <anchored-tree.md> <output.md>
# Steps: titled source copy -> ingest (split at openers, frame nodes) -> stamp body IDs with the
# strict text gate -> stack first-child headings that fell into a mid-list paragraph break under
# their parent -> gate again -> set heading '#' count = ID segments (bold > 6) -> diff check.
set -euo pipefail
TREE="$1"; OUT="$2"
D=0-INBOX/temp/TOC-thar-lam-gsal-byed-claude
LIB=4-SYSTEM/Skills/seg-toc-lib
SRC="1-SOURCES/Commentaries/རྣམ་འགྲེལ་ཐར་ལམ་གསལ་བྱེད།.md"
W=$D/build; mkdir -p $W
PY="python -X utf8"

# source with only "# " added to the title line (reference for the text gate)
$PY - "$SRC" "$W/titled.md" <<'EOF'
import re, sys
src = open(sys.argv[1], encoding="utf-8").read()
m = re.match(r"(---\n.*?\n---\n\s*)(.*)", src, re.S)
assert m.group(2).startswith("༄༅། །ཚད་མ་རྣམ་འགྲེལ་གྱི་ཚིག་ལེའུར")
open(sys.argv[2], "w", encoding="utf-8").write(m.group(1) + "# " + m.group(2))
EOF
cp "$W/titled.md" "$OUT"
$PY $LIB/toc_tree_ingest.py parse --input "$TREE" --out "$W/tree.json" > /dev/null
$PY $LIB/toc_tree_ingest.py ingest --tree "$W/tree.json" --commentary "$OUT" --split-frame-nodes > "$W/ingest.log" 2>&1
grep -E "reordered|REORDER|Inserted|Not found|Integrity" "$W/ingest.log" || true
grep -o "split at a node: [0-9]*" "$W/ingest.log" || true
$PY $LIB/toc_tree_ingest.py ingest --tree "$W/tree.json" --commentary "$OUT" --split-frame-nodes \
    --stamp-body-ids --verify-against "$W/titled.md" > "$W/stamp.log" 2>&1
tail -1 "$W/stamp.log" | cut -c1-120

$PY - "$OUT" <<'EOF'
import re, sys
p = sys.argv[1]
paras = open(p, encoding="utf-8").read().split("\n\n")
ish = lambda x: re.match(r"^#{2,}\s", x.strip()) is not None
moved = 0; i = 0
while i < len(paras):
    if ish(paras[i]):
        j = i
        while j < len(paras) and ish(paras[j]): j += 1
        prev = paras[i-1].strip() if i else ""
        body = re.sub(r"\s+\^[\w-]+$", "", prev)
        if prev and not ish(paras[i-1]) and re.search(r"དང[༌་]།$", body) and i >= 2 and ish(paras[i-2]):
            run = paras[i:j]; paras[i:j] = []; paras[i-1:i-1] = run; moved += 1
        i = j
    else:
        i += 1
open(p, "w", encoding="utf-8").write("\n\n".join(paras))
print("first-child heading runs re-stacked under parent:", moved)
EOF
$PY $LIB/verify_text.py "$W/titled.md" "$OUT" | cut -c1-120
cp "$OUT" "$W/pre-levels.md"

$PY - "$OUT" <<'EOF'
import re, sys
p = sys.argv[1]; L = open(p, encoding="utf-8").read().split("\n")
H = re.compile(r"^(#{2,})\s+(.*?)\s+\^([\w-]+)\s*$"); c = 0
for k, l in enumerate(L):
    m = H.match(l)
    if m:
        n = len(m.group(3).split("-")); t = m.group(2)
        t = t[2:-2] if t.startswith("**") and t.endswith("**") else t
        new = f"{'#'*n} {('**'+t+'**') if n > 6 else t} ^{m.group(3)}"
        c += new != l; L[k] = new
open(p, "w", encoding="utf-8").write("\n".join(L))
print("heading levels rewritten:", c)
EOF
diff <(sed -E '/^#+ /d' "$W/pre-levels.md") <(sed -E '/^#+ /d' "$OUT") > /dev/null && echo "non-heading lines identical ✓"
diff <(grep -E '^#+ ' "$W/pre-levels.md" | sed -E 's/^#+ //; s/\*\*//g') <(grep -E '^#+ ' "$OUT" | sed -E 's/^#+ //; s/\*\*//g') > /dev/null && echo "heading titles+IDs identical ✓"
$PY - "$OUT" <<'EOF'
import re, sys, collections
L = open(sys.argv[1], encoding="utf-8").read().split("\n")
H = [l for l in L if re.match(r"^#{2,}\s", l)]
bad = [l for l in H if len(re.search(r"\^([\w-]+)\s*$", l).group(1).split('-')) != len(re.match(r"^#+", l).group(0))]
ids = re.findall(r"\^([\w-]+)\s*$", "\n".join(L), re.M)
print("headings", len(H), "| level mismatches", len(bad), "| max #", max(len(re.match(r'^#+', l).group(0)) for l in H),
      "| block IDs", len(ids), "| duplicates", sum(1 for v in collections.Counter(ids).values() if v > 1))
EOF
