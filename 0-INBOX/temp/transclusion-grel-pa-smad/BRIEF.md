# Brief — root-text transclusion map for ཚད་མ་རྣམ་འགྲེལ་གྱི་འགྲེལ་པ། སྨད་ཆ། (one part)

You map where a Tibetan commentary quotes, glosses or cites its root text, for ONE part of the file
(your part id and line range are given in your task). The method is the same one used for the other commentaries
in this vault. Your output is a table of evidence; nothing is inserted into any file by you.

**The texts.** Root: Dharmakīrti's *Pramāṇavārttika* (ཚད་མ་རྣམ་འགྲེལ།), Tibetan verse, 4 chapters in THIS vault's order:
ch.1 རང་དོན་རྗེས་དཔག (root ids `^1-N`), ch.2 ཚད་མ་གྲུབ་པ (`^2-N`), ch.3 མངོན་སུམ (`^3-N`), ch.4 གཞན་དོན་རྗེས་དཔག (`^4-N`);
front matter `^I-1`…`^I-3`, chapter colophons (`^2-327`, `^3-671`, `^4-348`), root colophons `^a-1`…`^a-9`.
Each root block is normally one verse (4 lines), sometimes a half verse or two.
Commentary: Devendrabuddhi's (ལྷ་དབང་བློ།) *Pramāṇavārttikapañjikā*, ཚད་མ་རྣམ་འགྲེལ་གྱི་དཀའ་འགྲེལ། — its lower half (སྨད་ཆ།),
bam po 12–40, covering root ch.2–4 only. It is an Indian word-by-word commentary that goes through the root IN ORDER and
explains practically every verse, pāda by pāda. Its only headings are chapters (`##`) and bam po (`###`):
lines 25–1408 ↔ root ch.2, 1409–3480 ↔ ch.3, 3481–4316 ↔ ch.4. `## མཇུག་བྱང། ^a-0` (4317–end) is the COMMENTARY's own
colophon (Devendrabuddhi's closing verse and the translators' colophon) — not root; do not map it to root `^a-*`.
Line 29 (start of bam po 12) introduces ch.2 and its homage verse (root `^2-1`…).

**WARNING — the commentary's own block ids look like root ids.** The commentary numbers its blocks `^2-1`, `^2-2`, … `^3-…`
in its own sequence; a commentary block ending in `^2-3` is NOT root `^2-3`. Always identify the root block by its WORDS,
looking it up in the root text file.

**How it uses the root.** Typical devices:
- a pāda or half-verse of the root quoted as its own verse block (lines ending `། །`), then explained;
- `<root words> ཞེས་བྱ་བ་སྨོས་ཏེ / ཞེས་བྱ་བ་ནི / ཞེས་བྱ་བ་ལ་སོགས་པ་སྨོས་སོ / ཞེས་བྱ་བ་ལ་སོགས་པས / ཞེས་བྱ་བ་རྗེས་སུ་འཇུག་གོ`;
- the root's words woven into its own prose (glossing word by word, 2–5 syllables at a time) — the matcher misses most of this;
- objections (`… ཞེ་ན།`) answered by the next root verse — the answer verse's row goes on the block that quotes/glosses it,
  not on the objection.
It also quotes OTHER works, which are NOT root citations: Dignāga's *Pramāṇasamuccaya* (མདོ / ཀུན་ལས་བཏུས), Dharmakīrti's
other works and autocommentary on ch.1 (རང་གི་འགྲེལ་པ), sūtras (མདོ་ལས / བཅོམ་ལྡན་འདས་ཀྱིས), Sāṃkhya, Vaiśeṣika, Mīmāṃsā and
Nyāya positions, and others. A ch.1 verse quoted as authority is a `proof` row.

Run every command from the vault root `D:\Work\OpenPecha\Commentary_on_Valid_Cognition-rails`. Use `python -I` for scripts.

## Files (read-only)
- Commentary: `0-INBOX/temp/transclusion-grel-pa-smad/source.md` — exact copy of
  `1-SOURCES/Commentaries/ཚད་མ་རྣམ་འགྲེལ་གྱི་འགྲེལ་པ། སྨད་ཆ།.md`. Blocks are separated by blank lines; each content block ends with its
  own `^id`; headings start with `#` (only chapter `##` and bam po `###` headings). Blocks can be long — read with line ranges.
- Root text: `1-SOURCES/Text/ཚད་མ་རྣམ་འགྲེལ།.md`. Look a block up with e.g. `grep -n "\^3-112\s*$" <root>`, or search
  the root for quoted syllables with grep (the root text has no frontmatter quirks; a verse spans 4 lines and the id is
  on the last line).
- Seeds: `0-INBOX/temp/transclusion-grel-pa-smad/seeds/seeds-<PART>.tsv` — every place where a commentary block shares
  ≥ 6 consecutive syllables with a root block (`line` = first line of the commentary block, `matched_syllables` = length
  of the shared run, `preview` = the shared words with a little context). Seeds are evidence, not answers.

Never edit any file except your output file. Keep ALL your own working files (notes, row lists, helper scripts) in
`0-INBOX/temp/transclusion-grel-pa-smad/work/<PART>/` — other agents run in parallel; never use a shared scratch folder.
Do not read the whole commentary at once: read your range in pieces (e.g. 60–100 lines at a time; lines are long).

## What to produce
`0-INBOX/temp/transclusion-grel-pa-smad/place-<PART>.tsv`, UTF-8, tab-separated, this header exactly:

```
heading	root_block	line	kind	words
```

One row per (commentary block, root block) that the block quotes, glosses or cites:
- `heading` — the block id of the nearest heading above the block (e.g. `3-4-0`), for reference.
- `root_block` — the root block id without `^` (e.g. `1-23`).
- `line` — the FIRST line number (1-based, in source.md) of the commentary block. Never a heading line, never a blank
  line, never the 2nd+ line of a multi-line block. The transclusion will be inserted directly before this block.
- `kind` — one of:
  - `lemma`: the block quotes the root's words in order to explain them (including words woven into the gloss, and
    `ཞེས་པ་ནས … ཞེས་པའི་བར་` ranges).
  - `gloss`: the block explains a specific root block in its own words, quoting no more than a few syllables of it.
  - `proof`: the block cites the root as authority for a point about some other topic (e.g. `ཞེས་གསུངས་པའི་ཕྱིར`
    after a root sentence from elsewhere in the PV).
- `words` — the root words as the commentary gives them (short; ≤ 25 syllables; `…` to elide), so a reviewer can see why.

## Rules
1. **Only the root text (Pramāṇavārttika) counts.** A quotation from another work is not a root citation — unless the
   shared words are the root's own sentence that the commentary is explaining there.
2. **Seeds: decide each one.** Keep a seed when the block really quotes/explains/cites THAT root block. If the same
   words occur in several root blocks, choose the one being explained here (normally the verse currently being glossed
   or its neighbour, in the root chapter your part corresponds to). Keep a block from another chapter only when the
   commentary explicitly cites it as authority or cross-reference (`proof`). Drop seeds that are only a stock phrase
   with no specific root sentence behind them, and matches inside a quotation of another work (rule 1).
3. **Look for what the matcher missed.** Read every content block in your range. The commentary glosses verse after
   verse in root order, so expect almost every root block of your stretch to be explained somewhere. Short woven
   lemmas and paraphrases do not appear in the seeds: find their root block by searching the root text for the
   quoted syllables; add a row only when you are confident which root block it is.
4. **Placement = the first block that explains that verse's words.** If a verse is explained across several
   consecutive blocks, one row on the FIRST of them is enough (the parser's scope runs on until the next transclusion
   or heading) — but add another row if a later block is separated from it by another verse's row or a heading.
   A pure outline announcement (`X ལ་གཉིས། A དང་། B`) is not an explanation; put the row on the block that actually
   explains. A block can carry several root blocks (several rows, same `line`); a root block can appear at many lines.
5. **Your part's root range.** Work out which root blocks your part explains (first and last). In your reply list the
   root blocks inside that range that you did NOT place (compressed as ranges, e.g. `3-40…3-52`), so a reviewer can
   check them; also write the full list to `work/<PART>/unplaced.txt`. A bam po heading ends the parser's scope: when a
   verse's explanation runs on past a `###` heading, add a row for it on the first block after that heading.
6. **Validate before you finish** and fix every problem it reports:
   `python -I 0-INBOX/temp/transclusion-grel-pa-smad/validate_place.py 0-INBOX/temp/transclusion-grel-pa-smad/place-<PART>.tsv <PART>`

## Reply (≤ 15 lines)
The output path; rows by kind; seeds kept / dropped (and the main reasons for drops); rows added beyond the seeds;
the root range your part explains and the root blocks in it you did not place; anything you were unsure of
(line + root block), and the validator's last line.
