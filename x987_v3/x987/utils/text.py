from __future__ import annotations
import re

RE_PRICE = re.compile(r"\$?\s*([0-9][0-9,]{0,})(?:\.\d{2})?")
RE_MILES = re.compile(r"([0-9][0-9,]{0,})\s*(?:miles?|mi\.?)\b", re.I)
RE_YEAR  = re.compile(r"\b(19|20)\d{2}\b")
RE_VIN   = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b")

def parse_price(s: str):
    m = RE_PRICE.search(s or "")
    return int(m.group(1).replace(",", "")) if m else None

def parse_miles(s: str):
    m = RE_MILES.search(s or "")
    return int(m.group(1).replace(",", "")) if m else None
