from __future__ import annotations
import re
from typing import Optional

RE_PRICE = re.compile(r"\$?\s*([0-9][0-9,]{0,})(?:\.\d{2})?")
RE_MILES = re.compile(r"([0-9][0-9,]*(?:\.\d+)?)\s*(k)?\s*(?:miles?|mi\.?)\b", re.I)
RE_YEAR  = re.compile(r"\b(19|20)\d{2}\b")
RE_VIN   = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b")


def parse_price(s: str):
    m = RE_PRICE.search(s or "")
    return int(m.group(1).replace(",", "")) if m else None


def parse_miles(s: str):
    """Extract mileage in miles from a string.

    Supports numbers with optional comma separators and values with a
    ``k`` suffix (e.g. ``"52k miles"`` or ``"1.5k mi"``).  Returns ``None``
    when no mileage figure can be detected.
    """
    m = RE_MILES.search(s or "")
    if not m:
        return None
    num = float(m.group(1).replace(",", ""))
    if m.group(2):
        num *= 1000
    return int(num)


# transmission helpers -----------------------------------------------------

TX_MAP = [
    (r"(?i)7[- ]speed(?:\s*pdk)?|\bPDK\b|dual[- ]clutch|dct|doppelkupplung", "PDK"),
    (r"(?i)Tiptronic|automatic|auto\b|a/t", "Automatic"),
    (r"(?i)6[- ]speed|6mt|manual", "Manual"),
]


def detect_transmission(text: str) -> Optional[str]:
    """Return the raw transmission string detected in ``text``."""
    if not text:
        return None
    for pat, _ in TX_MAP:
        m = re.search(pat, text)
        if m:
            return m.group(0)
    return None


def normalize_transmission(text: str) -> Optional[str]:
    """Normalize ``text`` to a canonical transmission label."""
    if not text:
        return None
    for pat, label in TX_MAP:
        if re.search(pat, text):
            return label
    return None

