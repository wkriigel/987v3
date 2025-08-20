from __future__ import annotations
import re
from typing import List, Dict

from ..utils.text import normalize_transmission


def run_transform(rows: List[Dict], settings: dict) -> List[Dict]:
    out: List[Dict] = []
    for r in rows:
        tx = normalize_transmission(r.get("transmission_raw"))
        if tx:
            r["transmission"] = tx

        opts = r.get("raw_options")
        if isinstance(opts, list):
            parts = [p.strip() for p in opts if p and p.strip()]
            r["raw_options"] = "; ".join(parts) if parts else None
        elif isinstance(opts, str):
            parts = [p.strip() for p in re.split(r"[\n;]+", opts) if p.strip()]
            r["raw_options"] = "; ".join(parts) if parts else None

        out.append(r)
    return out

