from __future__ import annotations
from typing import List, Dict, Any
import importlib
from urllib.parse import urlparse

from ..scrapers.universal_vdp import scrape_one

def _norm_host(url: str) -> str:
    u = urlparse(url)
    parts = [p for p in (u.netloc or '').split('.') if p]
    return '.'.join(parts[-2:]) if len(parts) >= 2 else (u.netloc or '')

def _load_profile(host: str) -> Dict[str, Any]:
    modname = host.replace('.', '_')
    try:
        mod = importlib.import_module(f'x987.scrapers.profiles.{modname}')
        return getattr(mod, 'PROFILE')
    except Exception:
        return {'site_id': host, 'ready_selectors': ['h1','title'], 'primary_selectors': {}, 'rate_limit_ms': 800}

def run_scrape(url_entries: List[Dict[str, str]], settings: dict) -> List[Dict]:
    rows: List[Dict] = []
    for item in url_entries:
        url = item.get('listing_url') or ''
        host = item.get('source') or _norm_host(url)
        profile = _load_profile(host)
        try:
            row = scrape_one(url, host, profile)
        except Exception as ex:
            row = {'source': host, 'listing_url': url, 'error': str(ex)}
        rows.append(row)
    return rows
