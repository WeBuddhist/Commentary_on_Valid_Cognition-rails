#!/usr/bin/env python3
"""toc_replace.py — replace an uploaded commentary's live table of contents with the freshly
parsed one (dry run by default). Run from the vault root, after linter + parser.

    python 4-SYSTEM/scripts/toc_replace.py "<file.md>"                       # dry run
    python 4-SYSTEM/scripts/toc_replace.py "<file.md>" --execute --confirm <stem>

Payload: 4-SYSTEM/scripts/parser-commentary/output/<stem>/<stem>.toc.json.
Dry run: GETs the live toc (frontmatter toc_id), checks it belongs to the file's edition, and
lists every node whose title or span differs. Execute:
    1. DELETE /v2/table-of-contents/{old toc_id}
    2. POST   /v2/editions/{edition_id}/table-of-contents  <- toc.json  -> new toc_id
    3. new toc_id into the frontmatter and the ledger (old id kept under "replaced_tocs")
    4. GET the new toc back and check it equals the payload node by node.
Text, edition, durchens and alignment are not touched. Use it only when the edition payload is
unchanged (headings are not edition content; a changed edition needs a full re-upload).
Adapted from Vinaya_sutra-rails 0-INBOX/temp/api-lint/toc_replace.py, using upload_text.py's API
helpers and ledger.
"""
import argparse, datetime as dt, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import upload_text as ut  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def flatten(sections, depth=0, out=None):
    out = [] if out is None else out
    for s in sections:
        out.append((depth, s["title"].get("bo", ""), s["span"]["start"], s["span"]["end"]))
        flatten(s.get("subsections", []), depth + 1, out)
    return out


ap = argparse.ArgumentParser()
ap.add_argument("file"); ap.add_argument("--execute", action="store_true"); ap.add_argument("--confirm", default="")
a = ap.parse_args()
src = Path(a.file)
stem = src.stem
if a.execute and a.confirm != stem:
    ap.error(f"--execute needs --confirm {stem}")

fm = ut.read_fm(src)
eid, old = fm.get("edition_id"), fm.get("toc_id")
assert eid and old, "frontmatter needs edition_id and toc_id"
out = ut.VAULT / "4-SYSTEM/scripts/parser-commentary/output" / stem
payload = json.loads((out / f"{stem}.toc.json").read_text(encoding="utf-8"))
new_flat = flatten(payload["sections"])

live = ut.call("GET", f"/v2/table-of-contents/{old}")
assert live["edition_id"] == eid, f"live toc {old} belongs to edition {live['edition_id']}, not {eid}"
old_flat = flatten(live["sections"])
same_shape = [(d, s, e) for d, _, s, e in old_flat] == [(d, s, e) for d, _, s, e in new_flat]
print(f"== {'EXECUTE' if a.execute else 'DRY RUN'}: {stem}")
print(f"  edition {eid} | live toc {old}: {len(old_flat)} nodes | payload: {len(new_flat)} nodes | "
      f"same shape & spans: {same_shape}")
if len(old_flat) == len(new_flat):
    for i, (o, n) in enumerate(zip(old_flat, new_flat)):
        what = [w for w, x, y in (("depth", o[0], n[0]), ("title", o[1], n[1]), ("span", o[2:], n[2:])) if x != y]
        if what:
            print(f"  node {i:4} depth {n[0]:2} {'+'.join(what):12} {o[1][:40]!r} {o[2:]} -> {n[1][:40]!r} {n[2:]}")
if not a.execute:
    print(f"  plan: DELETE /v2/table-of-contents/{old} ; POST /v2/editions/{eid}/table-of-contents <- toc.json ; nothing sent.")
    sys.exit(0)

ut.call("DELETE", f"/v2/table-of-contents/{old}")
new_id = ut.call("POST", f"/v2/editions/{eid}/table-of-contents", payload)["id"]
ut.patch_fm(src, "toc_id", new_id)
ledger = ut.load_ledger()
entry = ledger.setdefault(stem, {"file": str(src).replace("\\", "/"), "receipts": []})
now = dt.datetime.now().isoformat(timespec="seconds")
entry.setdefault("replaced_tocs", []).append({"toc_id": old, "replaced_at": now})
entry["toc_id"] = new_id
entry.setdefault("receipts", []).append({"step": "toc-replace", "toc_id": new_id, "old": old, "at": now})
ut.save_ledger(ledger)
back = flatten(ut.call("GET", f"/v2/table-of-contents/{new_id}")["sections"])
print(f"  deleted toc {old}; new toc {new_id}; read back {len(back)} nodes, identical to payload: {back == new_flat}")
