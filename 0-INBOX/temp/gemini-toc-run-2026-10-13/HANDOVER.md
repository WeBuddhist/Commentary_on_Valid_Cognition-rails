---
title: Gemini TOC extraction run — handover
date: 2026-10-13
skill: toc-generate (phases 0–D; Phase E deliberately NOT run)
status: in progress — trees promoted as drafts, awaiting human review
---

# Gemini sa-bcad TOC run — handover (2026-10-13)

## Where things stand

`toc-generate` phases A–D were run with **Gemini (`gemini-3.1-pro-preview`)** in place of the skill's subagents, over all five commentaries. **Nothing in `1-SOURCES/` was modified** — every source file is byte-identical to the version the trees were built from (hashes in `state/hashes.txt`).

| Commentary (id) | Nodes | Unanchored `[[?]]` | QC issues (round 0 → selected) | Selected round | Rail |
|---|---|---|---|---|---|
| དཀའ་འགྲེལ་དགོངས་པ་རབ་གསལ། (`dgongs-pa-rab-gsal`) | 780 | 41 | 345 → 190 | 3 (final) | promoted, draft |
| ལེགས་བཤད་སྣང་བའི་གཏེར། (`legs-bshad-snang-ba-gter`) | 1,691 | 162 | 1,271 → 666 | 1 (round 2 scored 676 — not better; round 3 restarted 22:11) | promoted, draft |
| རྣམ་འགྲེལ་ཐར་ལམ་གསལ་བྱེད། (`thar-lam-gsal-byed`) | 1,079 | 328 | 875 → 781 | 1 (rounds 2–3 restarted 22:11) | promoted, draft |
| ཚད་མ་རྣམ་འགྲེལ་གྱི་འགྲེལ་པ། སྟོད་ཆ། (`grel-pa-stod`) | 4 | — | 0 | 0 | **not promoted** |
| ཚད་མ་རྣམ་འགྲེལ་གྱི་འགྲེལ་པ། སྨད་ཆ། (`grel-pa-smad`) | 14 | 1 | 3 (all 3 repair rounds made it worse; round 0 restored) | 0 | **not promoted** |

QC issue counts are the **true** counts from the report files (see *Lessons* — the checkers' exit codes wrap at 256).

Promoted rails (all `status: draft`, frontmatter records the source hash, QC summary and selected round):
- `2-RAILS/Sections/Raw/toc-tree/<id>.md` — the tree, `[[N]]` = first line of the paragraph holding the announcement
- `2-RAILS/Sections/Raw/toc-candidates/<id>.md`, `toc-enumerations/<id>.md` — evidence (never citable)
- `2-RAILS/Sections/Raw/toc-qc/toc-tree-qc-<id>.md`, `toc-tree-qc-source-<id>.md` — both QC reports + `issues_before/after`
- `2-RAILS/Sections/Raw/toc-qc/toc-pointers-<id>.md` — node → line → match method → mid-paragraph flag

## Decisions made by the human contributor

1. **Human segmentation must not be affected.** No paragraph is ever split or reflowed.
2. **No headings are written into `1-SOURCES/` yet ("tree only").** The segmentation follows root-verse units, so sa-bcad announcements fall mid-paragraph in 51–87% of anchors (counting every node stacked in such a paragraph: thar-lam 69%, legs-bshad 51%, dgongs 87%; the pointer tables flag only the *first* anchored node per paragraph, hence the smaller "yes" counts). Options still open for later:
   - heading before the containing paragraph (segmentation untouched, placement imprecise), or
   - a paragraph break + heading at the announcement (precise, adds breaks to the segmentation).
3. **The two འགྲེལ་པ། files (Devendrabuddhi) should not get sa-bcad headings** — they barely announce divisions inline (20/23 stod chunks had no candidates); their "trees" are mostly doctrinal lists (e.g. གཏན་ཚིགས་གསུམ་), which the skill's scope note says this pipeline is not for.

## What the next session should do

1. **Re-score and re-promote ལེགས་བཤད་ and ཐར་ལམ་.** At 22:11 their repair runs were restarted as detached processes (`nohup scripts/resume_repair.sh <id> <start> <end>`) after a network outage (DNS failures 20:56–22:06) left them stuck in retries: ཐར་ལམ་ rounds 2–3 from round 1, ལེགས་བཤད་ round 3 from round 2. Progress: `logs/resume-<id>.out` and `logs/post-<id>.log` (`RESUME DONE` marks the end); each round lands in `rounds/tree-<id>-roundN.md`. Then run
   `scripts/eval_rounds.sh <id>`, pick the round with the lowest total that does **not** lose source-attested nodes, and `scripts/promote.sh <id> <round> "<note>"`. If a run died, re-launch `scripts/resume_repair.sh <id> <next-round> 3`.
2. **Human review** of each draft tree against its QC reports — especially the sibling-count mismatches (the checker itself says "verify by hand") and the unanchored nodes.
3. **Register commentary IDs** in `4-SYSTEM/Guidelines/vault-annex.md` §3 (a human-only file). The ids used here are provisional.
4. Decide heading placement (decision 2) before any Phase E ingest. `scripts/toc_pointers.py ingest` is ready: it refuses to run if the source hash changed, inserts headings only at paragraph boundaries, and proves byte-for-byte that removing the headings restores the original. A dry run on དགོངས་པ་རབ་གསལ་ (`dryrun/`) passed: 739 headings, 0 bytes of original text changed.
5. The old spreadsheet import (commit `b4dd963`) carried pre-existing numbered sa-bcad headings (ཐར་ལམ་ 1,315; ལེགས་བཤད་ ~1,800; དགོངས་པ་ 606) — `state/thar-lam-old-spreadsheet-headings.txt`. A useful independent cross-check for review.

## How the run works (folder map)

- `scripts/gemini_toc.py` — the only thing that calls Gemini. `chunks` (Phase A/B per chunk), `tree-seg` (segmented Phase C), `repair-seg` (windowed Phase D repair). Each call = one `prompts/*.md` file as system instruction + only that phase's input (the skill's isolation). Key from `$GEMINI_API_KEY` or the `export` line in `~/.zshrc`; never logged.
- `scripts/toc_pointers.py` — deterministic: `resolve` gives each node a paragraph-start `[[N]]` (monotone best fit on full titles, then ordinal openings `དང་པོ་ནི / ལ / །`, then bare title, then child-stack) and re-indents from the decimal; `ingest` (Phase E, unused).
- `scripts/resume_repair.sh <id> <start> <end>` — restart repair from a saved round; `scripts/promote.sh <id> <round> "<note>"` — promote a scored round to `2-RAILS/` as draft.
- `scripts/post.sh <id> <source>` — merge → Phase C → resolve → both checkers → up to 3 repair rounds. `scripts/run_all.sh` drives all five. `scripts/slim.py` drops `CONTEXT:` lines. `scripts/eval_rounds.sh <id>` re-scores every saved round with true counts.
- `rounds/` per-round trees + round-0 QC; `eval/` scored copies; `logs/` (`gemini.log` = every call and retry); `singlecall/` the truncated first Phase C attempt; `dryrun/` the ingest proof; `state/` ids and source hashes.
- `../_archive-claude-run-2026-10-13/` — the earlier, partial Claude-subagent run (stale for ཐར་ལམ་: built before today's transclusions).

## Deviations from the skill, and why

- **Gemini instead of Claude subagents** (human request). Isolation preserved: one prompt file + one input per call.
- **Phase C segmented; repair windowed.** A full tree exceeds Gemini's 65,536-token output ceiling (measured: a 1,315-node tree = 68,551 tokens). The single-call attempt returned 168 nodes and collapsed the rest (`singlecall/`).
- **Phase C / repair read slim candidates** (`CONTEXT:` dropped — 1.9 MB → 0.2 MB; the tree prompt never uses it). The full candidates remain the QC corpus.
- **Pointers are resolved deterministically** (the Phase C prompt emits titles only; without pointers `qc_tree_vs_source.py` skips its main checks and E1 cannot run). Pointers are paragraph starts by design, so stacked headings trip the checker's "shared pointer" flag — expected here, not cursor loss.
- **Best round, not last round, is kept.** Repair sometimes made trees worse (སྨད་ཆ།: 3 → 8 issues).
- **Promoted as `status: draft`**, not `complete`: issues remain, and the vault rule is that an LLM never marks its own output complete.

## Lessons (environment)

- This host's IPv6 route to Google broke at ~15:04; Python tried IPv6 addresses sequentially and hung. `gemini_toc.py` forces IPv4.
- `qc_check_tree.py` / `qc_tree_vs_source.py` return the issue count as the exit code, which wraps at 256 — always count `^- ` lines in the report.
- A full network outage (DNS failures, 20:56–22:06) stalled two repair runs for hours; they were stopped and resumed from the last saved round.
- Network to the API is flaky (resets, SSL bad-record-MAC); all are retried and logged.
- 95 "possible hallucination" flags on དགོངས་པ་ were all titles verbatim in the source — the corpus checker only sees extracted candidates.
