#!/usr/bin/env python3
"""
Apply translations from /tmp/translate/all_zh.json into cards_zh.json.

For each translated record, update the matching card's translatable fields
(name, subname, text, traits, back_*, flavor, slot, customization_*).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "frontend" / "public" / "cards_zh.json"
TRANS = Path("/tmp/translate/all_zh.json")

# Fields the translator may produce (excluding `code` which is the key)
APPLY = {
    "name", "subname", "text", "traits",
    "back_name", "back_text", "back_flavor",
    "flavor", "slot",
    "customization_text", "customization_change",
}


def main():
    cards = json.load(CARDS.open())
    translations = json.load(TRANS.open())
    print(f"cards_zh.json: {len(cards)} cards")
    print(f"translations:  {len(translations)} records")

    by_code = {c["code"]: c for c in cards}
    updated = 0
    fields_touched = 0
    missing = []

    for t in translations:
        code = t.get("code")
        if not code:
            continue
        card = by_code.get(code)
        if not card:
            missing.append(code)
            continue
        for f, v in t.items():
            if f == "code":
                continue
            if f not in APPLY:
                continue
            if v is None or v == "":
                continue
            card[f] = v
            fields_touched += 1
        updated += 1

    if missing:
        print(f"WARNING: {len(missing)} codes from translation not found in cards_zh.json: {missing[:5]}")

    # Sort by code for stable diff
    cards.sort(key=lambda c: c["code"])

    tmp = CARDS.with_suffix(".json.tmp")
    with tmp.open("w") as f:
        json.dump(cards, f, ensure_ascii=False, separators=(",", ":"))
    tmp.replace(CARDS)
    print(f"\nUpdated {updated} cards, {fields_touched} fields written.")
    print(f"Saved {CARDS.relative_to(ROOT)} ({CARDS.stat().st_size} bytes)")


if __name__ == "__main__":
    sys.exit(main())
