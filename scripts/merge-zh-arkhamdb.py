#!/usr/bin/env python3
"""
Merge new cards from zh.arkhamdb.com into frontend/public/cards_zh.json.

Strategy: ADD ONLY. Cards already present in the local file are left untouched
(to preserve any fork-specific translations). Cards present in the ArkhamDB API
but missing locally are appended.

Usage:
    python3 scripts/merge-zh-arkhamdb.py            # write the merge
    python3 scripts/merge-zh-arkhamdb.py --dry-run  # report counts only
"""
import json
import sys
import urllib.request
from pathlib import Path

API_URL = "https://zh.arkhamdb.com/api/public/cards/"
ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / "frontend" / "public" / "cards_zh.json"


def fetch_api() -> list[dict]:
    with urllib.request.urlopen(API_URL, timeout=60) as r:
        return json.load(r)


def main(dry_run: bool) -> int:
    print(f"Fetching {API_URL} ...")
    api_cards = fetch_api()
    print(f"  → {len(api_cards)} cards from ArkhamDB zh API")

    print(f"Reading {LOCAL.relative_to(ROOT)} ...")
    with LOCAL.open() as f:
        local = json.load(f)
    print(f"  → {len(local)} cards locally")

    local_codes = {c["code"] for c in local}
    new = [c for c in api_cards if c["code"] not in local_codes]
    print(f"\nNew cards to add: {len(new)}")

    from collections import Counter
    by_pack = Counter(c.get("pack_name", "?") for c in new)
    by_type = Counter(c.get("type_code", "?") for c in new)
    print("  by pack:")
    for p, n in by_pack.most_common():
        print(f"    {n:>4}  {p}")
    print("  by type:")
    for t, n in by_type.most_common():
        print(f"    {n:>4}  {t}")

    if dry_run:
        print("\n[dry-run] no file written.")
        return 0

    merged = local + new
    # Sort by code for deterministic output and easier diff
    merged.sort(key=lambda c: c["code"])

    tmp = LOCAL.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(merged, f, ensure_ascii=False, separators=(",", ":"))
    tmp.replace(LOCAL)
    print(f"\nWrote {LOCAL.relative_to(ROOT)} ({len(merged)} cards)")
    return 0


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv))
