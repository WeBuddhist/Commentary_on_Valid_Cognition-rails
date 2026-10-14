# Upstream

| | |
|---|---|
| Source repository | https://github.com/WeBuddhist/21-taras-rails |
| Path | `4-SYSTEM/scripts/linter-root-text/` |
| Pinned commit | `2d14cddf9bdd207e34da4eff58b1d0fa98141a5f` (2026-10-01, "Add support for yigchungs in linter and parser") |
| Copied | 2026-10-12 |

Copied byte-identical, without upstream's `output/` folder. Every later commit here is a local delta.

**Why vendored:** this vault needs the same API lint → parse step for its root texts and commentaries.

## Local changes

- 2026-10-12: **durchens** (variant readings written as footnotes `[^n]`). Added `durchen.py`, shared by all four tools. The linter takes footnote definitions out before the block-ID check, which used to fail on them, and checks each marker against its definition and lemma. Not Nalanda-specific: offer it back to 21-taras-rails.

## Copied into this vault

- 2026-10-14: copied from `https://github.com/WeBuddhist/Nalanda-texts-rails`, `4-SYSTEM/scripts/linter-root-text/`, at commit `e6c182cf6e8b86f2068ff53095ffa5c9ea0effed` (2026-10-13), without its `output/` folder. This includes every local change listed above. The only difference from that commit is an auto-generated timestamp in `languages.py` (not yet committed there). Every later change here is a local delta.

- 2026-10-14: the frontmatter patch now writes with `newline=""`. On Windows `Path.write_text` turned every `
` into `
`, so a one-line patch (e.g. `commentary_of`) rewrote the whole source file with CRLF. Not vault-specific: offer it back upstream.

## Copied into Treasury_of_Abhidharma-rails

- 2026-10-14: copied from `Introduction_to_the_Middle_Way-rails`, `4-SYSTEM/scripts/linter-root-text/`, at commit `94fe26c` (branch `api-upload-2026-10-14`), without its `output/` folder. Includes every local change listed above. Every later change here is a local delta.
