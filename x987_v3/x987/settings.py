from __future__ import annotations
from pathlib import Path

def get_settings() -> dict:
    base = Path.cwd() / 'x987-data'
    (base / 'raw').mkdir(parents=True, exist_ok=True)
    (base / 'normalized').mkdir(parents=True, exist_ok=True)
    return {
        'data_dir': str(base),
        'browser': {'headful': True, 'slow_ms': 400},
        'collector': {'autotempest_url': 'https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214'},
        'profiles': ['cars_com', 'truecar_com', 'carvana_com'],
    }
