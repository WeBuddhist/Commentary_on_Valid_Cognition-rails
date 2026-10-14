# 4-SYSTEM/scripts

Standalone scripts that are not bundled inside a single skill — either because several skills use them, or because they are vault-maintenance tools rather than steps in a workflow.

A script that belongs to exactly one skill lives in that skill's own `scripts/` folder instead, so the skill stays self-contained and can be installed anywhere.

| Script | What it does |
| ------ | ------------ |
| `install-skills.py` | Installs skills from the shared skill library into `4-SYSTEM/Skills/`, resolving the library's logical location names to this vault's paths and writing the `.claude/commands/` stubs. See [`../How-to guides/Sync with rails-template.md`](../How-to%20guides/Sync%20with%20rails-template.md). |
| `linter-root-text/` | Lints a root text, edition or translation against the OpenPecha API schemas and writes the `text_input` payload to its own `output/`. **Patches `language` / `lang_tag` in the source file's frontmatter.** Vendored from Nalanda-texts-rails via Introduction_to_the_Middle_Way-rails (see its `UPSTREAM.md`). |
| `linter-commentary/` | Same for `file_type: commentary`; also fills `commentary_of` / `category_id` from the linked `root_text`. Vendored from Nalanda-texts-rails. |
| `parser-root-text/` | Turns a source file and its `.lint.json` into API payloads: text, edition segments, yigchungs, durchens (footnotes → variant-reading notes), TOC and alignment. Run the linter first. Vendored from Nalanda-texts-rails. |
| `upload_text.py` | Uploads one linted + parsed root text or commentary to the WeBuddhist library: text → edition → TOC → durchens → yigchungs, and for a commentary (`commentary_of` = the root's `text_id`) the alignment to the root edition. Dry run by default; writes each id back into the frontmatter and a ledger in `0-INBOX/temp/api-upload/`; resumes without duplicating. API code adapted from Nalanda-texts-rails `run_upload_batch.py`. |
| `delete_upload.py` | Deletes one uploaded text's live records (durchens, yigchungs, TOC, edition, text — reverse upload order) and removes the ids from the frontmatter, keeping them in the ledger's `deleted` history. Dry run by default; deletion is permanent. |
| `parser-commentary/` | Same for commentaries: segments default to `paragraph`, and alignment comes from the transclusions. Vendored from Nalanda-texts-rails. |

## Conventions

**Vendored code records its upstream.** If you copy a tool in from another repository rather than writing it here, put an `UPSTREAM.md` beside it recording the source repository, the path, the commit it was pinned at, and the date. Make the first commit byte-identical to upstream so that every later commit reads as your delta — then a re-sync is a diff rather than an archaeology exercise. Say in the same file *why* it was forked, and whether the changes should be offered back upstream.

**Nothing here writes to `1-SOURCES/` in place.** Scripts may create whole files from reviewed inbox material; they may not rewrite a source file's content.

**Credentials never live in the repository.** A script that needs one reads it from the environment or from a `.env` file that is git-ignored, and ships a `.env.example` containing **placeholders only** — never a real address, password or token, even an expired one.

**Generated output goes to `0-INBOX/`**, not into this folder.
