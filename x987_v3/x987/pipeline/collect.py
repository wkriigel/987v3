from __future__ import annotations
from typing import List, Dict
from ..collectors.autotempest import collect_autotempest

def run_collect(settings: dict) -> List[Dict[str, str]]:
    url = settings['collector']['autotempest_url']
    if str(url).startswith('TODO'):
        return []  # starter mode
    return collect_autotempest(url)