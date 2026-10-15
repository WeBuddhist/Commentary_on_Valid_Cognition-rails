#!/usr/bin/env bash
# Gemini TOC extraction (passes 1-4), two commentaries at a time. Run from the vault root.
cd "$(dirname "$0")/../../.."
L=0-INBOX/temp/toc-run-2026-10-14/logs
X=4-SYSTEM/Skills/seg-toc-lib/toc_tree_extractor/extract_toc_tree.py
C=1-SOURCES/Commentaries
run() { echo "START $2 $(date +%T)" >> $L/progress.log
        PYTHONIOENCODING=utf-8 python -X utf8 -u $X "$C/$1" --commentary-id "$2" > "$L/$2.log" 2>&1
        echo "END   $2 exit=$? $(date +%T)" >> $L/progress.log; }
run "ཚད་མ་རྣམ་འགྲེལ་གྱི་འགྲེལ་པ་ལེགས་བཤད་སྣང་བའི་གཏེར།.md" legs-bshad-snang-ba-gter-v2 &
run "དཀའ་འགྲེལ་དགོངས་པ་རབ་གསལ།.md" dgongs-pa-rab-gsal-v2 &
wait -n
run "རྣམ་འགྲེལ་ཐར་ལམ་གསལ་བྱེད།.md" thar-lam-gsal-byed-v2 &
wait -n
run "ཚད་མ་རྣམ་འགྲེལ་གྱི་འགྲེལ་པ། སྨད་ཆ།.md" grel-pa-smad-v2 &
wait
echo "ALL DONE $(date +%T)" >> $L/progress.log
