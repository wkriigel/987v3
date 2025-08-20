"""Mileage based price normalisation.

This module implements the *fair value* stage of the pipeline.  Each input row
is expected to contain at least ``price_usd`` and optionally ``mileage``.  The
stage adds an ``adj_price_usd`` field representing the price adjusted to a
baseline mileage.  The calculation is intentionally simple but provides stable
figures for subsequent stages (baseline and ranking) to operate on.

The adjustment formula mirrors the v2 "dollar" model used by previous versions
of the project::

    adj_price = price_usd + (mileage - baseline_miles) * usd_per_mile

``baseline_miles`` defaults to ``50_000`` and ``usd_per_mile`` to ``0.20`` but
both can be overridden via ``settings['fairvalue']``.
"""

from __future__ import annotations

from typing import Dict, List

from ..utils.text import parse_miles, parse_price


def _to_int(val: object, parser) -> int | None:
    """Coerce ``val`` to ``int`` using ``parser`` for strings.

    ``parser`` should accept a string and return an ``int`` or ``None``.  Any
    error results in ``None``.
    """

    if isinstance(val, (int, float)):
        return int(val)
    if val is None:
        return None
    try:
        parsed = parser(str(val))
        return int(parsed) if parsed is not None else None
    except Exception:
        return None


def run_fairvalue(rows: List[Dict], settings: dict) -> List[Dict]:
    """Compute ``adj_price_usd`` for each row and return the updated list."""

    fv_cfg = settings.get("fairvalue", {}) if isinstance(settings, dict) else {}
    base_miles = fv_cfg.get("baseline_miles", 50_000)
    usd_per_mile = fv_cfg.get("usd_per_mile", 0.20)

    for r in rows:
        price = _to_int(r.get("price_usd"), parse_price)
        miles = _to_int(r.get("mileage"), parse_miles)

        if price is None:
            r["adj_price_usd"] = None
            continue

        adj_price = float(price)
        if miles is not None:
            adj_price += (miles - base_miles) * float(usd_per_mile)

        r["adj_price_usd"] = int(round(adj_price))

    return rows

