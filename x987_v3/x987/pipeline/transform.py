from __future__ import annotations
from typing import List, Dict
import re
import options_v2

TX_MAP = [
    (r"(?i)\bPDK\b|dual[- ]clutch|dct|doppelkupplung|7[- ]speed(?:\s*pdk)?", "PDK"),
    (r"(?i)\bTiptronic\b|automatic|auto\b|a/t", "Automatic"),
    (r"(?i)\bmanual\b|6[- ]speed|6mt", "Manual"),
]

COLOR_BUCKETS = [
    (r"(?i)black", "Black"),
    (r"(?i)white|ivory", "White"),
    (r"(?i)silver|gray|grey", "Gray"),
    (r"(?i)red", "Red"),
    (r"(?i)blue", "Blue"),
    (r"(?i)green", "Green"),
    (r"(?i)yellow|gold", "Yellow"),
    (r"(?i)orange", "Orange"),
    (r"(?i)brown|tan|beige", "Brown"),
    (r"(?i)purple", "Purple"),
]


def _norm_transmission(tx_raw: str | None) -> str | None:
    if not tx_raw:
        return None
    for pat, label in TX_MAP:
        if re.search(pat, tx_raw):
            return label
    return tx_raw.strip()


def _color_bucket(color: str | None) -> str | None:
    if not color:
        return None
    for pat, bucket in COLOR_BUCKETS:
        if re.search(pat, color):
            return bucket
    return "Other"


def run_transform(rows: List[Dict], settings: dict) -> List[Dict]:
    option_aliases = getattr(options_v2, "OPTIONS", {})
    for row in rows:
        row["transmission"] = _norm_transmission(row.get("transmission_raw"))
        row["exterior_color_bucket"] = _color_bucket(row.get("exterior_color"))
        row["interior_color_bucket"] = _color_bucket(row.get("interior_color"))

        text_parts = []
        for key in ("trim", "model"):
            val = row.get(key)
            if val:
                text_parts.append(str(val))
        raw = row.get("raw_options")
        if isinstance(raw, list):
            text_parts.extend(str(v) for v in raw if v)
        elif raw:
            text_parts.append(str(raw))
        blob = " ".join(text_parts).lower()

        raw_opts = set()
        opts = set()
        for canon, aliases in option_aliases.items():
            for alias in aliases:
                if alias.lower() in blob:
                    raw_opts.add(alias)
                    opts.add(canon)
        row["raw_options"] = sorted(raw_opts) if raw_opts else None
        row["options"] = sorted(opts) if opts else None
    return rows
