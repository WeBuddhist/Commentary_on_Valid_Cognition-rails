#!/bin/bash
# Per-commentary: merge → Phase C (Gemini) → resolve pointers → both checkers →
# up to MAX_ROUNDS isolated repair rounds (Gemini), each followed by resolve + both checkers.
# usage: post.sh <id> <source-file>
set -u
ID="$1"; SRC="$2"; MAX_ROUNDS="${MAX_ROUNDS:-3}"
SP=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/scripts
VAULT=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails
S=$VAULT/4-SYSTEM/Skills/toc-generate/scripts
T=$VAULT/0-INBOX/temp
export GEMINI_TOC_LOG=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/logs/gemini.log
cd "$VAULT" || exit 1
D=$T/TOC-$ID
TODAY=$(date +%F)
nchunks=$(grep -c '^[0-9]' $D/chunk-index.tsv)
for sub in candidates enumerations; do
  have=$(ls $D/$sub | wc -l | tr -d ' ')
  [ "$have" -eq "$nchunks" ] || { echo "$ID: $sub $have/$nchunks — not ready"; exit 1; }
done

# Merge (on disk)
CAND=$T/toc-candidates-$ID.md; ENUM=$T/toc-enumerations-$ID.md
body=$(mktemp); cat $D/candidates/chunk_*.md > $body
printf -- "---\nsource: %s\nskill: toc-generate\nstage: candidates\nmodel: gemini\ndate: %s\ntotal_candidates: %s\n---\n\n" \
  "$ID" "$TODAY" "$(grep -c '^SECTION_TITLE:' $body)" > $CAND; cat $body >> $CAND
: > $body
for f in $D/enumerations/chunk_*.md; do grep -qx 'NO ENUMERATIONS' "$f" || { printf '<!-- %s -->\n' "$(basename $f .md)"; cat "$f"; echo; } >> $body; done
printf -- "---\nsource: %s\nskill: toc-generate\nstage: enumerations\nmodel: gemini\ndate: %s\n---\n\n" "$ID" "$TODAY" > $ENUM; cat $body >> $ENUM
rm -f $body

SLIM=$T/toc-candidates-slim-$ID.md
python3 -I $SP/slim.py $CAND $SLIM
TREE=$T/toc-tree-$ID.md; QC1=$T/toc-tree-qc-$ID.md; QC2=$T/toc-tree-qc-source-$ID.md
[ -s "$TREE" ] || python3 -I $SP/gemini_toc.py tree-seg --cand-dir $D/candidates --enum-dir $D/enumerations --id $ID --out $TREE || exit 1

qc() {
  python3 -I $SP/toc_pointers.py resolve --tree $TREE --source "$SRC" --report $T/toc-pointers-$ID.md
  python3 $S/qc_check_tree.py $TREE --corpus $CAND $ENUM --out $QC1 >/dev/null; a=$?
  python3 $S/qc_tree_vs_source.py $TREE --source "$SRC" --out $QC2 >/dev/null; b=$?
  echo "$a $b"
}
read a0 b0 < <(qc | tail -1)
echo "$ID round 0: qc_check_tree=$a0 qc_tree_vs_source=$b0" | tee -a /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/logs/post-$ID.log
cp $QC1 /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/rounds/qc1-$ID-round0.md; cp $QC2 /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/rounds/qc2-$ID-round0.md; cp $TREE /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/rounds/tree-$ID-round0.md
a=$a0; b=$b0; r=0
while [ $((a + b)) -gt 0 ] && [ $r -lt $MAX_ROUNDS ]; do
  r=$((r + 1))
  python3 -I $SP/gemini_toc.py repair-seg --tree $TREE --qc $QC1 $QC2 --cand-dir $D/candidates --enum-dir $D/enumerations --index $D/chunk-index.tsv --source "$SRC" --id $ID || break
  read a b < <(qc | tail -1)
  echo "$ID round $r: qc_check_tree=$a qc_tree_vs_source=$b" | tee -a /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/logs/post-$ID.log
  cp $TREE /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/rounds/tree-$ID-round$r.md
done
for q in $QC1 $QC2; do
  first=$([ $q = $QC1 ] && echo $a0 || echo $b0); last=$([ $q = $QC1 ] && echo $a || echo $b)
  printf "\n---\nissues_before: %s\nissues_after: %s\nrepair_rounds: %s\nrepair_model: gemini\n" "$first" "$last" "$r" >> $q
done
echo "$ID DONE before=($a0,$b0) after=($a,$b) rounds=$r" | tee -a /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/logs/post-$ID.log
