#!/bin/bash
# usage: eval_rounds.sh <id>   — scores every saved round tree for <id> (true counts from reports)
SP=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/scripts
VAULT=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails
S=$VAULT/4-SYSTEM/Skills/toc-generate/scripts; T=$VAULT/0-INBOX/temp
ID=$1; SRC=$VAULT/$(awk -F'\t' -v id=$ID '$1==id{print $2}' /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/state/ids.tsv)
mkdir -p /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/eval
printf "%-8s %6s %8s %6s %6s %10s %8s\n" round nodes attested qc1 qc2 unresolved total
for t in $(ls /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/rounds/tree-$ID-round*.md | sort -V); do
  r=$(basename $t .md | sed 's/.*-round//'); c=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/eval/$ID-r$r.md; cp $t $c
  python3 -I $SP/toc_pointers.py resolve --tree $c --source "$SRC" >/dev/null
  python3 $S/qc_check_tree.py $c --corpus $T/toc-candidates-$ID.md $T/toc-enumerations-$ID.md --out $c.qc1 >/dev/null
  python3 $S/qc_tree_vs_source.py $c --source "$SRC" --out $c.qc2 >/dev/null
  read n att < <(python3 -I - "$c" "$SRC" <<'EOF'
import sys, re
sys.path.insert(0, "/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/4-SYSTEM/Skills/toc-generate/scripts")
import qc_check_tree as Q
src = Q._canon(open(sys.argv[2], encoding="utf-8").read())
ts = [re.sub(r"\s*\[\[.*", "", re.sub(r"^\s*\*\s+[\d.]+\s+", "", l)).strip() for l in open(sys.argv[1], encoding="utf-8") if re.match(r"^\s*\*\s+\d", l)]
att = sum(1 for t in ts if (b := Q._canon(Q._strip_leading_ordinal(t))) and b in src)
print(len(ts), att)
EOF
)
  q1=$(grep -c '^- ' $c.qc1); q2=$(grep -c '^- ' $c.qc2); u=$(grep -c '\[\[?\]\]' $c)
  printf "%-8s %6s %8s %6s %6s %10s %8s\n" $r $n $att $q1 $q2 $u $((q1 + q2))
done
