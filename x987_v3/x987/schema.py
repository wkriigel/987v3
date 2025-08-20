from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

@dataclass
class Row:
    source: str
    listing_url: str
    vin: Optional[str] = None
    year: Optional[int] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    transmission_raw: Optional[str] = None
    mileage: Optional[int] = None
    price_usd: Optional[int] = None
    exterior_color: Optional[str] = None
    interior_color: Optional[str] = None
    raw_options: Optional[List[str]] = None
    location: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)