"""Slim a merged candidates file for Phase C: drop CONTEXT lines and drop a block that
exactly repeats one from the previous chunk (25-line chunk overlap)."""
import re, sys
from pathlib import Path
src, out = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8")
fm = re.match(r"^---\n.*?\n---\n", text, re.S)
body = text[fm.end():] if fm else text
chunks = re.split(r"(?m)^(?=<!-- chunk )", body)
res, prev, n = [], set(), 0
for ch in chunks:
    if not ch.strip():
        continue
    blocks = re.findall(r"(?ms)^SECTION_TITLE:.*?(?=^CONTEXT:|^SECTION_TITLE:|^<!--|\Z)", ch)
    cur = set()
    for b in blocks:
        key = b.strip()
        cur.add(key)
        if key in prev:
            continue
        res.append(key); n += 1
    prev = cur
out.write_text("# Section candidates (document order; CONTEXT lines and chunk-overlap duplicates removed)\n\n"
               + "\n\n".join(res) + "\n", encoding="utf-8")
print(f"slim: {n} blocks, {out.stat().st_size} bytes")
