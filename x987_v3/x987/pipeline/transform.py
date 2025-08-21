from __future__ import annotations
import re
from typing import List, Dict

from ..utils.text import normalize_transmission
import options_v2 as option_aliases
from .options_v2 import recompute_options_v2


def run_transform(rows: List[Dict], settings: dict) -> List[Dict]:
    out: List[Dict] = []

    # Flatten option aliases for quick lookup
    alias_map: Dict[str, str] = {}
    for canon, aliases in option_aliases.OPTIONS.items():
        for a in aliases:
            alias_map[a.lower()] = canon

    for r in rows:
        vin = str(r.get("vin") or "").upper()
        if not r.get("model") and vin.startswith("WP0"):
            r["model"] = "Cayman"
        if not r.get("trim") and vin.startswith("WP0A") and len(vin) > 4:
            code = vin[4]
            if code == "A":
                r["trim"] = "Base"
            elif code == "B":
                r["trim"] = "S"

        tx = normalize_transmission(r.get("transmission_raw"))
        if tx:
            r["transmission"] = tx

        parts = [
            str(r.get("year")).strip() if r.get("year") else None,
            str(r.get("model")).strip() if r.get("model") else None,
            str(r.get("trim")).strip() if r.get("trim") else None,
        ]
        title = " ".join(p for p in parts if p)
        if title:
            r["title"] = title

        # normalise raw options into a single string
        opts = r.get("raw_options")
        raw_opts = None
        if isinstance(opts, list):
            parts = [p.strip() for p in opts if p and p.strip()]
            raw_opts = "; ".join(parts) if parts else None
        elif isinstance(opts, str):
            parts = [p.strip() for p in re.split(r"[\n;]+", opts) if p.strip()]
            raw_opts = "; ".join(parts) if parts else None
        r["raw_options"] = raw_opts

        # detect canonical options
        found: List[str] = []
        hay = raw_opts.lower() if raw_opts else ""
        for alias, canon in alias_map.items():
            if alias in hay and canon not in found:
                found.append(canon)
        r["options"] = ", ".join(found) if found else None

        out.append(r)

    out = recompute_options_v2(out, settings)
    return out
