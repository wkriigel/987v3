"""Ranking stage for the v2 dollar model.

This final stage computes a ``deal_delta`` for each row – the difference
between the ``baseline_adj_price_usd`` and the row's ``adj_price_usd`` – and
returns the rows sorted by that delta (largest positive deltas first).
"""

from __future__ import annotations

from typing import Dict, List


def run_rank(rows: List[Dict], settings: dict) -> List[Dict]:
    """Calculate deal deltas and sort results.

    ``deal_delta`` is the baseline adjusted price minus the row's adjusted
    price.  Listings with the highest positive deltas are considered better
    deals and therefore appear first in the returned list.
    """

    for r in rows:
        adj = r.get("adj_price_usd")
        baseline = r.get("baseline_adj_price_usd")
        if isinstance(adj, (int, float)) and isinstance(baseline, (int, float)):
            r["deal_delta"] = int(baseline - adj)
        else:
            r["deal_delta"] = None

    return sorted(
        rows,
        key=lambda r: r.get("deal_delta", float("-inf")),
        reverse=True,
    )

