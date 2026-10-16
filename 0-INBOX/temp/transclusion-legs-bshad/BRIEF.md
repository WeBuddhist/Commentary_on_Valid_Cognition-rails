# Brief — root-text transclusion map for ལེགས་བཤད་སྣང་བའི་གཏེར། (one part)

You map where a Tibetan commentary quotes, glosses or cites its root text, for ONE part of the file
(your part id and line range are given in your task). The method is the same one used for the Vinaya and
Middle-Way commentaries. Your output is a table of evidence; nothing is inserted into any file by you.

**The texts.** Root: Dharmakīrti's *Pramāṇavārttika* (ཚད་མ་རྣམ་འགྲེལ།), Tibetan verse, 4 chapters in THIS vault's order:
ch.1 རང་དོན་རྗེས་དཔག (root ids `^1-N`), ch.2 ཚད་མ་གྲུབ་པ (`^2-N`), ch.3 མངོན་སུམ (`^3-N`), ch.4 གཞན་དོན་རྗེས་དཔག (`^4-N`);
front matter `^I-1`…`^I-3` (title lines, translator's homage), colophons `^a-1` (author) and `^a-2`…`^a-9` (translators).
Each root block is normally one verse (4 lines), sometimes a half verse or two.
Commentary: ཚད་མ་རྣམ་འགྲེལ་གྱི་གཞུང་གསལ་པོར་བཤད་པ་ལེགས་བཤད་སྣང་བའི་གཏེར། (signed དྷཱི་མིང་པ།) — a sa-bcad commentary
that goes through the root in order. Its sections follow the root chapters in the same order:
lines 91–1474 ↔ root ch.1, 1475–2686 ↔ ch.2, 2687–5451 ↔ ch.3, 5452–6929 ↔ ch.4.
Front: lines 24–52 are the commentary's OWN title and homage (not root); `## དང་པོ་མཚན་དོན། ^1-0` (53–65) explains the
root's title lines (root `^I-1`, `^I-2`); `## གཉིས་པ་འགྱུར་ཕྱག། ^2-0` (66–69) explains the root's translator's homage
(`^I-3`); `### དང་པོ་རྩོམ་པའི་ཡན་ལག། ^3-1-0` (72–86) explains the root's opening verses (`^1-1`, `^1-2`).
Closing: `### གསུམ་པ་མཇུག་དོན། ^3-3-0` (6930–6939) the root's last verses; `## བཞི་པ་མཇུག་དོན། ^4-0` (6940–7081) explains the
root's colophons — `### དང་པོ་མཛད་བྱང།` ↔ root `^a-1`, `### གཉིས་པ་འགྱུར་བྱང།` ↔ root `^a-2`…`^a-9` (place each where it is
explained); 7082–7224 dedication and the commentary's own colophon (not root).

**Its own verse outlines are NOT root verses.** This commentary announces its divisions in short verse lines of its
own (e.g. `ཚད་མས་གཞལ་བྱ་གཉིས་སུ་ངེས། །མཐར་ཐུག་འཇུག་ཡུལ་གཅིག་ཏུ་བསྒྲུབ། །`, `དང་པོ་ལ། … །`), often as separate verse
blocks between headings. Never map those to root blocks — a row needs the root's own words or a clear gloss of them.

**How it uses the root.** It explains verse after verse. Typical devices:
- the root's words woven into its own prose sentence (glossing word by word, the root words often only 2–5 syllables
  at a time, interleaved with explanation) — this is the commonest form and the matcher misses most of it;
- `<root words> ཞེས་པ / ཞེས་སོ / ཞེས་པ་ནི / ཞེས་པའི་དོན / ཅེས་པ …`;
- ranges: `<first words> ཞེས་པ་ནས། <last words> ཞེས་པའི་བར་` (= every root block from the first to the last — give a
  row for EACH root block in that range);
- a whole verse or half-verse quoted as its own verse block (lines ending `། །`).
It also quotes OTHER works, which are NOT root citations: Dignāga's *Pramāṇasamuccaya* (ཀུན་བཏུས, མདོ / ཚད་མ་མདོ —
e.g. `རྗེས་དཔག་བྱ་དང་དེ་མཚུངས་ལ། །ཡོད་དང་མེད་ལ་མེད་པར་ནི།`), the *Pramāṇaviniścaya* (རྣམ་ངེས), the *Nyāyabindu*
(རིགས་ཐིགས), Dharmakīrti's own autocommentary (རང་འགྲེལ), Devendrabuddhi (ལྷ་དབང་བློ / ལྷ), Śākyabuddhi (ཤཱཀྱ་བློ),
Prajñākaragupta (རྒྱན), sūtras (མདོ་ལས), the Kośa (མཛོད) and others.

Run every command from the vault root `D:\Work\OpenPecha\Commentary_on_Valid_Cognition-rails`. Use `python -I` for scripts.

## Files (read-only)
- Commentary: `0-INBOX/temp/transclusion-legs-bshad/source.md` — exact copy of
  `1-SOURCES/Commentaries/ཚད་མ་རྣམ་འགྲེལ་གྱི་འགྲེལ་པ་ལེགས་བཤད་སྣང་བའི་གཏེར།.md`. Blocks are separated by blank lines; each content block ends with its
  own `^id`; headings start with `#` (bold `**…**` on deep ones). Blocks can be long — read with line ranges.
- Root text: `1-SOURCES/Text/ཚད་མ་རྣམ་འགྲེལ།.md`. Look a block up with e.g. `grep -n "\^3-112\s*$" <root>`, or search
  the root for quoted syllables with grep (the root text has no frontmatter quirks; a verse spans 4 lines and the id is
  on the last line).
- Seeds: `0-INBOX/temp/transclusion-legs-bshad/seeds/seeds-<PART>.tsv` — every place where a commentary block shares
  ≥ 6 consecutive syllables with a root block (`line` = first line of the commentary block, `matched_syllables` = length
  of the shared run, `preview` = the shared words with a little context). Seeds are evidence, not answers.

Never edit any file except your output file. Keep ALL your own working files (notes, row lists, helper scripts) in
`0-INBOX/temp/transclusion-legs-bshad/work/<PART>/` — other agents run in parallel; never use a shared scratch folder.
Do not read the whole commentary at once: read your range in pieces (e.g. 60–100 lines at a time; lines are long).

## What to produce
`0-INBOX/temp/transclusion-legs-bshad/place-<PART>.tsv`, UTF-8, tab-separated, this header exactly:

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
   root blocks inside that range that you did NOT place, so a reviewer can check them.
6. **Validate before you finish** and fix every problem it reports:
   `python -I 0-INBOX/temp/transclusion-legs-bshad/validate_place.py 0-INBOX/temp/transclusion-legs-bshad/place-<PART>.tsv <PART>`

## Reply (≤ 15 lines)
The output path; rows by kind; seeds kept / dropped (and the main reasons for drops); rows added beyond the seeds;
the root range your part explains and the root blocks in it you did not place; anything you were unsure of
(line + root block), and the validator's last line.
