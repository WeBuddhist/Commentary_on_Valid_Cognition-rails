#!/bin/bash
# usage: resume_repair.sh <id> <start_round> <end_round>
# Restarts Phase D repair from the saved tree rounds/tree-<id>-round<start-1>.md,
# writing each new round to rounds/tree-<id>-round<N>.md. Score afterwards with
# eval_rounds.sh <id>, then promote the best round with promote.sh.
set -u
V=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails
R=$V/0-INBOX/temp/gemini-toc-run-2026-10-13
S=$V/4-SYSTEM/Skills/toc-generate/scripts; T=$V/0-INBOX/temp
ID=$1; START=$2; END=$3
export GEMINI_TOC_LOG=$R/logs/gemini.log
cd "$V" || exit 1
SRC=$(awk -F'\t' -v id=$ID '$1==id{print $2}' $R/state/ids.tsv)
D=$T/TOC-$ID; TREE=$T/toc-tree-$ID.md; QC1=$T/toc-tree-qc-$ID.md; QC2=$T/toc-tree-qc-source-$ID.md
BASE=$R/rounds/tree-$ID-round$((START - 1)).md
[ -f "$BASE" ] || { echo "missing $BASE"; exit 1; }
cp "$BASE" "$TREE"
qc() {
  python3 -I $R/scripts/toc_pointers.py resolve --tree $TREE --source "$SRC" --report $T/toc-pointers-$ID.md >/dev/null
  python3 $S/qc_check_tree.py $TREE --corpus $T/toc-candidates-$ID.md $T/toc-enumerations-$ID.md --out $QC1 >/dev/null
  python3 $S/qc_tree_vs_source.py $TREE --source "$SRC" --out $QC2 >/dev/null
  echo "$(grep -c '^- ' $QC1) $(grep -c '^- ' $QC2)"   # true counts (exit codes wrap at 256)
}
read a b < <(qc)
echo "$(date +%H:%M) $ID resume from round $((START - 1)): qc1=$a qc2=$b" | tee -a $R/logs/post-$ID.log
for r in $(seq $START $END); do
  python3 -I $R/scripts/gemini_toc.py repair-seg --tree $TREE --qc $QC1 $QC2 --cand-dir $D/candidates \
    --enum-dir $D/enumerations --index $D/chunk-index.tsv --source "$SRC" --id $ID || break
  read a b < <(qc)
  cp $TREE $R/rounds/tree-$ID-round$r.md
  echo "$(date +%H:%M) $ID round $r: qc1=$a qc2=$b" | tee -a $R/logs/post-$ID.log
done
echo "$(date +%H:%M) $ID RESUME DONE" | tee -a $R/logs/post-$ID.log
