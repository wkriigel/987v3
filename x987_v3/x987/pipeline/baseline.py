"""Baseline median computation for adjusted prices.

The *baseline* stage groups cars by year and trim and calculates the median of
the ``adj_price_usd`` field for each group.  The resulting median is stored in
``baseline_adj_price_usd`` on each row so that later stages can quantify how
far a particular listing deviates from the typical price for its peers.
"""

from __future__ import annotations

from statistics import median
from typing import Dict, List, Tuple


def _group_key(row: Dict) -> Tuple[str, str]:
    """Return the grouping key used for baseline medians."""

    year = str(row.get("year") or "").strip()
    trim = str(row.get("trim") or "").strip()
    return year, trim


def run_baseline(rows: List[Dict], settings: dict) -> List[Dict]:
    """Attach ``baseline_adj_price_usd`` medians for each (year, trim) group."""

    groups: Dict[Tuple[str, str], List[int]] = {}
    for r in rows:
        adj = r.get("adj_price_usd")
        if isinstance(adj, (int, float)):
            groups.setdefault(_group_key(r), []).append(int(adj))

    medians = {k: int(median(v)) for k, v in groups.items() if v}

    for r in rows:
        r["baseline_adj_price_usd"] = medians.get(_group_key(r))

    return rows

