#!/bin/bash
SP=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/scripts
cd /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails
export GEMINI_TOC_LOG=/Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/logs/gemini.log
while IFS=$'\t' read id f; do
  pids=()
  for ph in A B; do python3 -I $SP/gemini_toc.py chunks --phase $ph --source "$f" --index 0-INBOX/temp/TOC-$id/chunk-index.tsv --outdir 0-INBOX/temp/TOC-$id --id $id --workers 8 >> /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/logs/chunks.out 2>&1 & pids+=($!); done
  wait "${pids[@]}"
  $SP/post.sh "$id" "$f" > /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/logs/post-$id.out 2>&1 &
done < /Users/tashitsering/Desktop/work/Obsidian/Commentary_on_Valid_Cognition-rails/0-INBOX/temp/gemini-toc-run-2026-10-13/state/ids.tsv
wait; echo ALL-DONE
