# thar-lam-gsal-byed — Claude TOC run, 2026-10-14

Commentary: `1-SOURCES/Commentaries/རྣམ་འགྲེལ་ཐར་ལམ་གསལ་བྱེད།.md` (unchanged; sha256 7deec2ab…).
Model: isolated Opus subagents (Gemini 3.8 Flash was unavailable: 503 high demand).

| Step | Result |
|---|---|
| Pass 1 candidates | 29 chunks → 1,814 candidate blocks → `0-INBOX/toc-candidates-thar-lam-gsal-byed-claude.md` |
| Pass 2 enumerations | 29 chunks → 506 blocks → `0-INBOX/toc-enumerations-thar-lam-gsal-byed-claude.md`. Note: this commentary announces most divisions without a count word (`ཞེས་ལ། A། B་འོ།`); agents were told to keep those (chunk 012 redone; strict version in `_strict/`). |
| Pass 3 tree | 1,539 nodes, depth 1–28 → `0-INBOX/toc-tree-thar-lam-gsal-byed-claude.md` |
| Pass 4 QC | 22 flags, all "ordinal not attested" false positives (ordinal = position in parent's enumeration); tree unchanged |
| Pass 5 anchors | 28 segments (`pass5-plan.tsv`, `segments/`, `anchors/`) → `toc-tree-thar-lam-gsal-byed-claude.md` here: 1,544 nodes incl. frame I, II, a, b, b.1; 0 `[[?]]` |
| Pass 6 QC | 0 unresolved / out-of-order; 586 title-proximity + 177 shared-pointer flags expected; 6 count flags checked — false positives. Tree unchanged |
| Ingest | 1,544 headings, 0 not found, no reorder, 728 paragraphs split at openers (user choice), text unchanged |
| Block IDs | stamped; `verify_text.py` ✓ letters + spacing; then heading `#` count set to ID segment count (no cap, bold > 6) — only heading markers changed (diff-verified) |

Output: `0-INBOX/རྣམ་འགྲེལ་ཐར་ལམ་གསལ་བྱེད།.toc.md` — ADAPTIVE headings (user choice 2026-10-14): a section is opened into its subsections only while it is longer than 2,500 syllables, max depth 16 → 416 headings (incl. frame), 197 paragraph splits, 5 first-child heading runs re-stacked, 2,033 block IDs. Built with `build_headed.sh` from `toc-tree-thar-lam-gsal-byed-claude.adaptive2500-max16.md`. Full 28-level tree stays in `toc-tree-thar-lam-gsal-byed-claude.md`; full-depth and depth-5 builds kept in `rounds/`.
Not done: publishing the tree to `2-RAILS/Sections/Raw/toc-tree/` (a Gemini draft already exists there).

## Applied to 1-SOURCES (2026-10-14, user instruction)

The 280 root-verse transclusions (`![[ཚད་མ་རྣམ་འགྲེལ།#^…]]`) were removed and the result replaced
`1-SOURCES/Commentaries/རྣམ་འགྲེལ་ཐར་ལམ་གསལ་བྱེད།.md` (sha256 00c1fe1c…). Text gate ✓ against the
previous source minus its transclusion lines (title line `# ` the only other change); 416 headings,
2,033 block IDs unchanged by the removal. Previous source: `source-backup/…before-toc-2026-10-14.md`
(sha256 7deec2ab…). Version with transclusions: `rounds/adaptive2500-max16-with-transclusions.toc.md`.
