"""Remove link groups that repeat the group already in scope.

usage: python -I dedupe_transclusions.py FILE.md [--write]

The parser's scope of a transclusion group runs to the next group or heading. A group whose set of
root blocks equals the group already in scope (no heading in between) changes nothing in the
alignment, so it is dropped together with one of the blank lines around it. Groups that differ —
including a smaller subset, which narrows the scope — are kept. Without --write it only reports.
"""
import re, sys

sys.stdout.reconfigure(encoding="utf-8")
LINK = re.compile(r"^!\[\[1-SOURCES/Text/ཚད་མ་རྣམ་འགྲེལ།\.md#\^([\w-]+)\]\]\s*$")
path = sys.argv[1]
raw = open(path, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in raw[:3000] else "\n"
L = raw.split(nl)

out, active, dropped_groups, dropped_lines, i = [], None, 0, 0, 0
while i < len(L):
    l = L[i]
    if l.startswith("#"):
        active = None
    if LINK.match(l):
        j = i
        while j < len(L) and LINK.match(L[j]): j += 1
        g = frozenset(LINK.match(x).group(1) for x in L[i:j])
        if g == active:
            dropped_groups += 1; dropped_lines += j - i
            # drop the group and the blank line that follows it (the one before stays as the separator)
            if j < len(L) and not L[j].strip():
                j += 1
            i = j
            continue
        active = g
        out += L[i:j]; i = j
        continue
    out.append(l); i += 1

# integrity: identical apart from link lines and blank runs
def norm(lines):
    o, prev_blank = [], False
    for x in lines:
        if LINK.match(x): continue
        b = not x.strip()
        if b and prev_blank: continue
        o.append(x); prev_blank = b
    return o
assert norm(out) == norm(L), "non-link content changed"
# spacing: every link line has a link or a blank on each side
bad = [k for k, x in enumerate(out) if LINK.match(x) and not ((LINK.match(out[k-1]) or not out[k-1].strip()) and (k + 1 == len(out) or LINK.match(out[k+1]) or not out[k+1].strip()))]
assert not bad, f"spacing problem at output lines {bad[:5]}"
print(f"{path}: dropped {dropped_groups} groups / {dropped_lines} link lines; {sum(1 for x in out if LINK.match(x))} link lines remain")
if "--write" in sys.argv:
    open(path, "w", encoding="utf-8", newline="").write(nl.join(out))
