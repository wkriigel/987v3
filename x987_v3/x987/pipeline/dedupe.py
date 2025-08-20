from __future__ import annotations
from typing import List, Dict

def run_dedupe(rows: List[Dict], settings: dict) -> List[Dict]:
    seen = set()
    out: List[Dict] = []
    for r in rows:
        vin = (r.get("vin") or "").strip().upper()
        key = vin if vin else None
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        out.append(r)
    return out
