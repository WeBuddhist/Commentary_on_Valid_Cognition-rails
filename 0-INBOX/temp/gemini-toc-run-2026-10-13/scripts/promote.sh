#!/bin/bash
# usage: promote.sh <id> <round> "<note>"
# Promotes the scored copy eval/<id>-r<round>.md (run eval_rounds.sh first) to
# 2-RAILS/Sections/Raw/ as status: draft, with candidates, enumerations, both QC
# reports and the pointer table. Refuses if the source changed since chunking.
V=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails
R=$V/0-INBOX/temp/gemini-toc-run-2026-10-13
cd "$V" || exit 1
RAW=2-RAILS/Sections/Raw; mkdir -p $RAW/toc-tree $RAW/toc-candidates $RAW/toc-enumerations $RAW/toc-qc
id=$1; r=$2; note=$3
src=$(awk -F'\t' -v id=$id '$1==id{print $2}' $R/state/ids.tsv); sha=$(grep "^$id " $R/state/hashes.txt | cut -d' ' -f2)
[ "$(shasum -a 256 "$src" | cut -c1-16)" = "$sha" ] || { echo "$id: SOURCE CHANGED — not promoting"; exit 1; }
e=$R/eval/$id-r$r.md
[ -f "$e" ] || { echo "$id: $e missing — run eval_rounds.sh $id first"; exit 1; }
python3 -I $R/scripts/toc_pointers.py resolve --tree $e --source "$src" --report $RAW/toc-qc/toc-pointers-$id.md >/dev/null
q1=$(grep -c '^- ' $e.qc1); q2=$(grep -c '^- ' $e.qc2); q10=$(grep -c '^- ' $R/eval/$id-r0.md.qc1); q20=$(grep -c '^- ' $R/eval/$id-r0.md.qc2)
n=$(grep -c '^\s*\* ' $e); un=$(grep -c '\[\[?\]\]' $e); mid=$(grep -c '| yes |' $RAW/toc-qc/toc-pointers-$id.md)
{ printf -- "---\nregistered_id: %s  # provisional — not yet in the vault-annex commentary roster\nsource_file: %s\nsource_sha256_16: %s  # the tree's [[N]] line pointers are valid ONLY for this exact file version\nqc_reports: [%s/toc-qc/toc-tree-qc-%s.md, %s/toc-qc/toc-tree-qc-source-%s.md]\npointer_table: %s/toc-qc/toc-pointers-%s.md\nstatus: draft\nreview_needed: \"%s QC issues remain (%s corpus, %s source); %s nodes unanchored [[?]]; %s anchors are mid-paragraph — see pointer_table\"\ngenerated_by: \"toc-generate phases A–D via Gemini (gemini-3.1-pro-preview); Phase C segmented; repair round %s selected; pointers = first line of the paragraph holding each announcement\"\nnote: \"%s\"\ndate: %s\n---\n\n" \
    "$id" "$src" "$sha" "$RAW" "$id" "$RAW" "$id" "$RAW" "$id" "$((q1+q2))" "$q1" "$q2" "$un" "$mid" "$r" "$note" "$(date +%F)"
  sed -n '/^## དཀར་ཆག/,$p' $e; } > $RAW/toc-tree/$id.md
cp $V/0-INBOX/temp/toc-candidates-$id.md $RAW/toc-candidates/$id.md
cp $V/0-INBOX/temp/toc-enumerations-$id.md $RAW/toc-enumerations/$id.md
{ cat $e.qc1; printf "\n---\nissues_before: %s\nissues_after: %s\nselected_round: %s\nrepair_model: gemini-3.1-pro-preview\n" $q10 $q1 $r; } > $RAW/toc-qc/toc-tree-qc-$id.md
{ cat $e.qc2; printf "\n---\nissues_before: %s\nissues_after: %s\nselected_round: %s\nrepair_model: gemini-3.1-pro-preview\n" $q20 $q2 $r; } > $RAW/toc-qc/toc-tree-qc-source-$id.md
echo "$id: promoted round $r — $n nodes, $un unanchored, $mid mid-paragraph, issues $((q10+q20)) -> $((q1+q2))"
