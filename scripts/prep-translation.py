#!/usr/bin/env python3
"""
Prepare input files for LLM card translation.

Produces:
- /tmp/translate/batch_NN.json     — cards to translate, ≤90 each
- /tmp/translate/glossary.json     — already-translated card pairs as terminology reference

Untranslated = (no CJK char in `name`) AND (no CJK char in `text`).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "frontend" / "public" / "cards_zh.json"
OUT = Path("/tmp/translate")
OUT.mkdir(exist_ok=True)

CJK = re.compile(r'[一-鿿]')


def has_cjk(s) -> bool:
    return bool(s and CJK.search(s))


def is_untranslated(c: dict) -> bool:
    return not has_cjk(c.get("name", "")) and not has_cjk(c.get("text", ""))


# Fields we want the translator to produce. We only emit a field in the input
# if the card has an English source for it.
TRANSLATABLE_FIELDS = [
    ("name",       "real_name"),
    ("subname",    "real_subname"),
    ("text",       "real_text"),
    ("traits",     "real_traits"),
    ("back_name",  "real_back_name"),
    ("back_text",  "real_back_text"),
    ("back_flavor","real_back_flavor"),
    ("flavor",     "real_flavor"),
    ("slot",       "real_slot"),
    ("customization_text", "real_customization_text"),
    ("customization_change", "real_customization_change"),
]


def english_source(c, zh_field, en_field):
    """Pick the best English source for a translatable field."""
    # Prefer real_X if non-empty, otherwise X (since X may be the English placeholder)
    v = c.get(en_field) or c.get(zh_field)
    if not v:
        return None
    v = str(v).strip()
    if not v:
        return None
    # If it already has Chinese, skip — already translated
    if CJK.search(v):
        return None
    return v


def make_input_record(c: dict) -> dict:
    rec = {"code": c["code"], "type_code": c.get("type_code", "")}
    for zh_field, en_field in TRANSLATABLE_FIELDS:
        v = english_source(c, zh_field, en_field)
        if v is not None:
            rec[zh_field] = v
    return rec


def make_glossary(all_cards, n=60):
    """Sample translated cards with meaningful name+text translation."""
    pairs = []
    for c in all_cards:
        nm_zh = c.get("name", "")
        nm_en = c.get("real_name", "")
        tx_zh = c.get("text", "") or ""
        tx_en = c.get("real_text", "") or ""
        tr_zh = c.get("traits", "") or ""
        tr_en = c.get("real_traits", "") or ""
        if not (has_cjk(nm_zh) and nm_zh != nm_en):
            continue
        if not tx_en or not tx_zh or tx_en == tx_zh:
            continue
        if len(tx_en) < 40 or len(tx_en) > 400:
            continue
        pairs.append({
            "code": c["code"],
            "name_en": nm_en, "name_zh": nm_zh,
            "traits_en": tr_en, "traits_zh": tr_zh,
            "text_en": tx_en, "text_zh": tx_zh,
        })
        if len(pairs) >= n:
            break
    return pairs


def main():
    cards = json.load(open(CARDS))
    untranslated = [c for c in cards if is_untranslated(c)]
    print(f"Untranslated cards: {len(untranslated)}")

    glossary = make_glossary(cards)
    print(f"Glossary samples: {len(glossary)}")
    json.dump(glossary, open(OUT / "glossary.json", "w"), ensure_ascii=False, indent=2)

    # Batch into 3
    BATCH_SIZE = 90
    batches = [untranslated[i:i+BATCH_SIZE] for i in range(0, len(untranslated), BATCH_SIZE)]
    for i, batch in enumerate(batches, 1):
        records = [make_input_record(c) for c in batch]
        path = OUT / f"batch_{i:02d}.json"
        json.dump(records, open(path, "w"), ensure_ascii=False, indent=2)
        print(f"  batch {i}: {len(records)} cards → {path}")

    print(f"\nDone. Inputs at {OUT}")


if __name__ == "__main__":
    main()
