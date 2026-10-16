# Brief — root-text transclusion map for དཀའ་འགྲེལ་དགོངས་པ་རབ་གསལ། (one part)

You map where a Tibetan commentary quotes, glosses or cites its root text, for ONE part of the file
(your part id and line range are given in your task). The method is the same one used for the Vinaya and
Middle-Way commentaries. Your output is a table of evidence; nothing is inserted into any file by you.

**The texts.** Root: Dharmakīrti's *Pramāṇavārttika* (ཚད་མ་རྣམ་འགྲེལ།), Tibetan verse, 4 chapters in THIS vault's order:
ch.1 རང་དོན་རྗེས་དཔག (root ids `^1-N`), ch.2 ཚད་མ་གྲུབ་པ (`^2-N`), ch.3 མངོན་སུམ (`^3-N`), ch.4 གཞན་དོན་རྗེས་དཔག (`^4-N`);
front matter `^I-1`…`^I-3` (title lines, translator's homage), colophons `^a-1` (author) and `^a-2`…`^a-9` (translators).
Each root block is normally one verse (4 lines), sometimes a half verse or two.
Commentary: རྒྱས་པའི་བསྟན་བཅོས་ཚད་མ་རྣམ་འགྲེལ་གྱི་དཀའ་འགྲེལ་དགོངས་པ་རབ་གསལ། (བསོད་ནམས་གྲགས་པ།) — a *dka' 'grel*, an
explanation of the DIFFICULT POINTS, written largely as debate (`འོ་ན། … ཞེ་ན། … ཡོད་དེ། / … ཕྱིར།`, `ཁོ་ན་རེ། …`). It follows
the root chapters in this vault's order: lines 144–1932 ↔ root ch.1, 1933–2791 ↔ ch.2, 2792–5313 ↔ ch.3,
5314–6954 ↔ ch.4.
Front: lines 24–59 the commentary's OWN homage, 60–74 its own preamble (not root unless a root verse is quoted);
`## དང་པོ་མཚན་གྱི་དོན། ^1-0` (75–82) explains the root's title lines (root `^I-1`, `^I-2`); `## གཉིས་པ་འགྱུར་གྱི་ཕྱག། ^2-0`
(83–86) the root's translator's homage (`^I-3`); `### དང་པོ་བཤད་པ་ལ་འཇུག་པ། ^3-1-0` (89–141) the root's opening verses
(`^1-1`, `^1-2`). Closing: `### གསུམ་པ་བཤད་པ་མཐར་ཕྱིན་པའི་ཚུལ། ^3-3-0` (6955–6965) the root's closing verses if quoted;
`## བཞི་པ་མཇུག་གི་དོན། ^4-0` (6966–6969) the root's colophons (author `^a-1`, translators `^a-2`…`^a-9`) — place those
only if the block really quotes or explains them; 6970–7033 dedication and the commentary's own colophon (not root).

**Coverage is NOT expected to be complete.** A dka' 'grel picks out difficult points; it may pass over many verses
without explaining them. Place a root block only where the commentary actually quotes, glosses or cites it — never
just because it "should" be somewhere. Report the gaps; do not fill them.

**Range statements.** It often describes the layout of the root: `<A> ཞེས་པ་ནས། <B> ཞེས་པའི་བར་གྱིས་ <topic> འཆད`
("from A to B explains …"). Treat such a statement as a lemma for every root block from A to B ONLY when it opens
the commentary's explanation of exactly that stretch AND the stretch is at most ~12 root blocks; then give a row for
each root block in it, on that block. A longer range, or a statement that just describes the structure (e.g. listing
which passages explain which line of a verse), gets NO rows — place those verses where they are individually quoted
or explained. Its section headings sometimes quote root words (`X ཞེས་པ་རྒྱས་པར་འཆད་པ`): the row goes on the first
content block under that heading that explains them.

**How it uses the root.** Typical devices:
- `<root words> ཞེས་པ / ཞེས་སོ / ཞེས་པ་ནི / ཞེས་པའི་དོན / ཅེས་པ / ཞེས་གསུངས་པ …`, often a full line or pāda;
- a whole verse or half-verse quoted as its own verse block (lines ending `། །`);
- root words woven into a debate sentence (`… ཞེས་པའི་དོན་ཇི་ལྟར་ཡིན་ཞེ་ན།`).
It also quotes OTHER works, which are NOT root citations: Dignāga's *Pramāṇasamuccaya* (ཀུན་བཏུས, མདོ / ཚད་མ་མདོ —
e.g. `རྗེས་དཔག་བྱ་དང་དེ་མཚུངས་ལ། །ཡོད་དང་མེད་ལ་མེད་པར་ནི།`), the *Pramāṇaviniścaya* (རྣམ་ངེས), the *Nyāyabindu*
(རིགས་ཐིགས), Dharmakīrti's autocommentary (རང་འགྲེལ), Devendrabuddhi (ལྷ་དབང་བློ / ལྷར།), Śākyabuddhi (ཤཱཀྱ་བློ),
Prajñākaragupta (རྒྱན), Dharmottara (ཆོས་མཆོག), rGyal tshab's commentary (རྣམ་བཤད / རྣམ་བཤད་ཐར་ལམ), ཁ་ཅིག, sūtras
(མདོ་ལས), the Kośa (མཛོད) and others. When a quoted Indian or Tibetan commentary itself quotes the root, the row is
for the root words only if the commentary is explaining that root passage there.

Run every command from the vault root `D:\Work\OpenPecha\Commentary_on_Valid_Cognition-rails`. Use `python -I` for scripts.

## Files (read-only)
- Commentary: `0-INBOX/temp/transclusion-dgongs-pa/source.md` — exact copy of
  `1-SOURCES/Commentaries/དཀའ་འགྲེལ་དགོངས་པ་རབ་གསལ།.md`. Blocks are separated by blank lines; each content block ends with its
  own `^id`; headings start with `#` (bold `**…**` on deep ones). Blocks can be long — read with line ranges.
- Root text: `1-SOURCES/Text/ཚད་མ་རྣམ་འགྲེལ།.md`. Look a block up with e.g. `grep -n "\^3-112\s*$" <root>`, or search
  the root for quoted syllables with grep (the root text has no frontmatter quirks; a verse spans 4 lines and the id is
  on the last line).
- Seeds: `0-INBOX/temp/transclusion-dgongs-pa/seeds/seeds-<PART>.tsv` — every place where a commentary block shares
  ≥ 6 consecutive syllables with a root block (`line` = first line of the commentary block, `matched_syllables` = length
  of the shared run, `preview` = the shared words with a little context). Seeds are evidence, not answers.

Never edit any file except your output file. Keep ALL your own working files (notes, row lists, helper scripts) in
`0-INBOX/temp/transclusion-dgongs-pa/work/<PART>/` — other agents run in parallel; never use a shared scratch folder.
Do not read the whole commentary at once: read your range in pieces (e.g. 60–100 lines at a time; lines are long).

## What to produce
`0-INBOX/temp/transclusion-dgongs-pa/place-<PART>.tsv`, UTF-8, tab-separated, this header exactly:

```
heading	root_block	line	kind	words
```

One row per (commentary block, root block) that the block quotes, glosses or cites:
- `heading` — the block id of the nearest heading above the block (e.g. `3-2-1-1-1-2-0`), for reference.
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
3. **Look for what the matcher missed.** Read every content block in your range. Quotations shorter than 6 syllables
   (a pāda, a few words with ཞེས་པ) are not in the seeds. Short woven
   lemmas and paraphrases do not appear in the seeds: find their root block by searching the root text for the
   quoted syllables; add a row only when you are confident which root block it is.
4. **Placement = the first block that explains that verse's words.** If a verse is explained across several
   consecutive blocks, one row on the FIRST of them is enough (the parser's scope runs on until the next transclusion
   or heading) — but add another row if a later block is separated from it by another verse's row or a heading.
   A pure outline announcement (`X ལ་གཉིས། A དང་། B`) is not an explanation; put the row on the block that actually
   explains. A block can carry several root blocks (several rows, same `line`); a root block can appear at many lines.
5. **Your part's root range.** Work out which root blocks your part explains (first and last). In your reply list the
   root blocks inside that range that you did NOT place (compressed as ranges, e.g. `1-40…1-52`), so a reviewer can
   check them; also write the full list to `work/<PART>/unplaced.txt`.
6. **Validate before you finish** and fix every problem it reports:
   `python -I 0-INBOX/temp/transclusion-dgongs-pa/validate_place.py 0-INBOX/temp/transclusion-dgongs-pa/place-<PART>.tsv <PART>`

## Reply (≤ 15 lines)
The output path; rows by kind; seeds kept / dropped (and the main reasons for drops); rows added beyond the seeds;
the root range your part explains and the root blocks in it you did not place; anything you were unsure of
(line + root block), and the validator's last line.
