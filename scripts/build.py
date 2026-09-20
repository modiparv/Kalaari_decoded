#!/usr/bin/env python3
"""Inline data/kalaari.json into src/index.template.html and write index.html.

The dashboard is a single self-contained HTML file so it can be opened from disk,
published as an artifact, or dropped on any static host with no fetch calls.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "kalaari.json"
TEMPLATE = ROOT / "src" / "index.template.html"
OUT = ROOT / "index.html"

MARK = re.compile(r"/\*__DATA__\*/.*?/\*__END__\*/", re.S)


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ids = [c["id"] for c in data["companies"]]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        print(f"duplicate company ids: {dupes}", file=sys.stderr)
        return 1
    for c in data["companies"]:
        if c["sector"] not in data["sectors"]:
            print(f"{c['id']}: unknown sector {c['sector']!r}", file=sys.stderr)
            return 1
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/")  # keep </script> out of the inline block
    html = TEMPLATE.read_text(encoding="utf-8")
    if not MARK.search(html):
        print("template is missing the /*__DATA__*/ … /*__END__*/ marker", file=sys.stderr)
        return 1
    html = MARK.sub(lambda _: blob, html, count=1)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(html)//1024} KB, {len(ids)} companies)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
