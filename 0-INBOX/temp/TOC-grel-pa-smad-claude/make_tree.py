"""Build the anchored top-mode tree for སྨད་ཆ། (chapters numbered as in the root text, fascicles
under them, back-matter frame). Every [[context]] is sliced verbatim from the source."""
import re, sys
SRC, OUT = sys.argv[1:3]
L = open(SRC, encoding="utf-8").read().split("\n")
ORD = ["བཅུ་གཉིས་པ","བཅུ་གསུམ་པ","བཅུ་བཞི་པ","བཅོ་ལྔ་པ","བཅུ་དྲུག་པ","བཅུ་བདུན་པ","བཅོ་བརྒྱད་པ","བཅུ་དགུ་པ","ཉི་ཤུ་པ",
       "ཉི་ཤུ་གཅིག་པ","ཉི་ཤུ་གཉིས་པ","ཉི་ཤུ་གསུམ་པ","ཉི་ཤུ་བཞི་པ","ཉི་ཤུ་ལྔ་པ","ཉི་ཤུ་དྲུག་པ","ཉི་ཤུ་བདུན་པ","ཉི་ཤུ་བརྒྱད་པ",
       "ཉི་ཤུ་དགུ་པ","སུམ་ཅུ་པ","སུམ་ཅུ་རྩ་གཅིག་པ","སུམ་ཅུ་རྩ་གཉིས་པ","སུམ་ཅུ་རྩ་གསུམ་པ","སུམ་ཅུ་རྩ་བཞི་པ","སུམ་ཅུ་རྩ་ལྔ་པ",
       "སུམ་ཅུ་རྩ་དྲུག་པ","སུམ་ཅུ་རྩ་བདུན་པ","སུམ་ཅུ་རྩ་བརྒྱད་པ","སུམ་ཅུ་རྩ་དགུ་པ","བཞི་བཅུ་པ"]
fasc = []   # (line_idx, title, context)
for i, l in enumerate(L):
    for m in re.finditer(r"བམ་པོ་([^ །]+)།", l):
        hdr = re.search(r"(?:༄༅༅། །)?ཚད་མ་རྣམས?་འགྲེལ་གྱི་འགྲེལ་པ། ?$", l[:m.start()])
        start = hdr.start() if hdr else m.start()
        fasc.append((i, "བམ་པོ་" + m.group(1), l[start:m.end()]))
assert [f[1] for f in fasc] == ["བམ་པོ་" + o for o in ORD], [f[1] for f in fasc]
chap_end = {2: 1370 - 1, 3: 3390 - 1}          # 0-based lines of the ch.2 / ch.3 colophons
assert "ཚད་མ་གྲུབ་པ་སྟེ་ལེའུ་གཉིས་པའོ" in L[chap_end[2]] and "མངོན་སུམ་གྱི་ལེའུ་སྟེ་གསུམ་པའོ" in L[chap_end[3]]
CH = {2: "ལེའུ་གཉིས་པ། ཚད་མ་གྲུབ་པ", 3: "ལེའུ་གསུམ་པ། མངོན་སུམ", 4: "ལེའུ་བཞི་པ། གཞན་གྱི་དོན་གྱི་རྗེས་སུ་དཔག་པ"}
def chap(i):
    return 2 if i <= chap_end[2] else 3 if i < chap_end[3] or (i == chap_end[3] and False) else 4
out = ["## དཀར་ཆག / Table of Contents", ""]
cur, n = None, 0
for i, title, ctx in fasc:
    c = 2 if i <= chap_end[2] else (3 if i < chap_end[3] else 4)
    if c != cur:
        cur, n = c, 0
        out.append(f"* {c}. {CH[c]} [[{ctx}]]")
    n += 1
    out.append(f"   * {c}.{n} {title} [[{ctx}]]")
# back matter: closing verse + author colophon, translators' colophon
v = 4208 - 1; col = 4213 - 1
assert L[v].startswith("ཕལ་ཆེར་སྐལ་བ་མེད་ཉིད་དང་། །")
k = L[col].index("བོད་ཀྱི་དཔལ་ལྷ་བཙན་པོ")
out += [f"* a. མཇུག་བྱང། [[{L[v]}]]", f"   * a.1 མཛད་བྱང། [[{L[v]}]]", f"   * a.2 འགྱུར་བྱང། [[{L[col][k:k+60]}]]"]
open(OUT, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(o[:110] for o in out))
