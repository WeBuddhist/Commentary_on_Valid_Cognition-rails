#!/usr/bin/env python3
"""delete_upload.py — delete one uploaded text's live records from the WeBuddhist library, so it
can be re-uploaded with upload_text.py.

Deletes in the reverse of the upload order (as Nalanda-texts-rails run_upload_batch.py --delete):

    1. DELETE /v2/durchens/{id}            every durchen on the edition (listed live)
       DELETE /v2/yigchungs/{id}           every yigchung on the edition (listed live)
    2. DELETE /v2/table-of-contents/{toc_id}
    3. DELETE /v2/editions/{edition_id}
    4. DELETE /v2/texts/{text_id}

The ids come from the file's frontmatter. Afterwards the id keys (text_id, edition_id, toc_id,
durchen_count, yigchung_count, aligned_to_edition_id) are removed from the frontmatter and the
old ids are kept in the ledger's "deleted" history (0-INBOX/temp/api-upload/upload-ledger.json).

Deleting is permanent and cannot be undone. A root text that commentaries are aligned to should
be deleted only when those commentaries will be re-uploaded against the new root ids.

Dry run is the default; it lists what would be deleted.

    python 4-SYSTEM/scripts/delete_upload.py "<file.md>"             # dry run
    python 4-SYSTEM/scripts/delete_upload.py "<file.md>" --execute   # delete

Run from the vault root. Credentials as in upload_text.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from upload_text import ApiError, call, load_ledger, read_fm, save_ledger, BASE  # noqa: E402

ID_KEYS = ("text_id", "edition_id", "toc_id", "durchen_count", "yigchung_count", "aligned_to_edition_id")


def live_ids(path):
    d = call("GET", path) or []
    items = d.get("items", []) if isinstance(d, dict) else d
    return [i["id"] for i in items if isinstance(i, dict) and i.get("id")]


def unpatch_fm(path, keys):
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    nl = "\r\n" if "\r\n" in text[:2000] else "\n"
    lines = text.split(nl)
    close = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    keep = [l for i, l in enumerate(lines)
            if not (0 < i < close and any(re.match(rf"^{re.escape(k)}\s*:", l) for k in keys))]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(nl.join(keep))


def delete(path):
    try:
        call("DELETE", path)
        return True
    except ApiError as exc:
        if " 404 " in str(exc):
            return False
        raise


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("file")
    ap.add_argument("--execute", action="store_true", help="delete (default: dry run)")
    args = ap.parse_args(argv)

    path = Path(args.file)
    fm = read_fm(path)
    tid, eid, toc = fm.get("text_id"), fm.get("edition_id"), fm.get("toc_id")
    if not tid:
        sys.exit(f"{path.name}: no text_id in the frontmatter — nothing to delete")
    durch = live_ids(f"/v2/editions/{eid}/durchens") if eid else []
    yig = live_ids(f"/v2/editions/{eid}/yigchungs") if eid else []
    print(f"{path.name}\n  host {BASE}")
    print(f"  durchens {len(durch)}, yigchungs {len(yig)}, toc {toc}, edition {eid}, text {tid}")
    if not args.execute:
        print("\nDry run — nothing deleted. Re-run with --execute to delete (permanent).")
        return 0

    n = sum(delete(f"/v2/durchens/{i}") for i in durch)
    print(f"  deleted {n}/{len(durch)} durchens")
    n = sum(delete(f"/v2/yigchungs/{i}") for i in yig)
    print(f"  deleted {n}/{len(yig)} yigchungs")
    for label, p, i in (("toc", "/v2/table-of-contents/", toc), ("edition", "/v2/editions/", eid), ("text", "/v2/texts/", tid)):
        if i:
            print(f"  {'deleted' if delete(p + i) else 'already gone:'} {label} {i}")

    ledger = load_ledger()
    entry = ledger.setdefault(path.stem, {"file": str(path).replace("\\", "/"), "receipts": []})
    old = {k: fm[k] for k in ID_KEYS if fm.get(k)}
    old["deleted_at"] = dt.datetime.now().isoformat(timespec="seconds")
    entry.setdefault("deleted", []).append(old)
    for k in ID_KEYS + ("durchen_ids", "yigchung_ids"):
        entry.pop(k, None)
    save_ledger(ledger)
    unpatch_fm(path, ID_KEYS)
    print("  ids removed from the frontmatter; kept in the ledger's 'deleted' history")
    return 0


if __name__ == "__main__":
    sys.exit(main())
