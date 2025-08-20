# ===========================
# x987 v3 bootstrap (lean, headful-only)
# ===========================
$ErrorActionPreference = "Stop"

# Where to create the project (current folder)
$root = Join-Path (Get-Location) "x987_v3"
if (Test-Path $root) { Remove-Item -Recurse -Force $root }
New-Item -ItemType Directory -Force -Path $root | Out-Null

# Helper to write files with UTF-8 (no BOM)
function Write-Utf8 ($Path, $Content) {
  $dir = Split-Path -Parent $Path
  if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  [System.IO.File]::WriteAllText($Path, $Content, (New-Object System.Text.UTF8Encoding($false)))
}

# ---------- Top-level ----------
Write-Utf8 (Join-Path $root "README.md") @"
# x987 v3 (starter)
Lean, headful-only skeleton:
- Collector: AutoTempest-first; collects VDP links (cars.com, truecar.com, carvana.com)
- Scraper: Universal headful Playwright parser with site profiles
- Transform: uses options_v2 as canonical
- View: keep current styled table approach
"@

Write-Utf8 (Join-Path $root "requirements.txt") @"
playwright
rich
tomli; python_version < '3.11'
"@

Write-Utf8 (Join-Path $root "options_v2.py") @"
# Authoritative expanded options mapping lives here (placeholder).
OPTIONS = {
  # Example:
  # "Sport Chrono": ["Sport Chrono Package", "Sport Chrono Plus"],
}
"@

Write-Utf8 (Join-Path $root "scripts\setup.ps1") @"
# Setup environment
python -m pip install -r requirements.txt
python -m playwright install chromium
"@

Write-Utf8 (Join-Path $root "docs\PR_TEMPLATE.md") @"
# v3: Universal headful scraper + options_v2 + lean repo

## Goals
- Keep pricing/scoring + table view unchanged.
- Headful-only navigation/scraping.
- AutoTempest-first collector producing mixed VDPs (cars.com, truecar.com, carvana.com).
- Universal VDP scraper with small site profiles.
- Adopt options_v2; remove legacy options logic.
- Trim deps and nonessential tests/lints.

## Acceptance
- [ ] python -m x987 completes; CSVs non-empty when URLs present; table renders.
- [ ] Raw CSV shows cars.com, truecar.com, carvana.com sources.
- [ ] Pricing/scoring/view unchanged vs v2 Cars.com-only baseline.
- [ ] Minimal dependencies only; doctor OK.
- [ ] Repo free of vestigial files.
"@

# ---------- Package skeleton ----------
$pkg = Join-Path $root "x987"
New-Item -ItemType Directory -Force -Path $pkg | Out-Null

Write-Utf8 (Join-Path $pkg "__init__.py") "__all__ = []`n"

Write-Utf8 (Join-Path $pkg "__main__.py") @"
from .cli import main

if __name__ == '__main__':
    raise SystemExit(main())
"@

Write-Utf8 (Join-Path $pkg "cli.py") @"
from __future__ import annotations
from .doctor import doctor_check
from .settings import get_settings
from .pipeline.collect import run_collect
from .pipeline.scrape import run_scrape
from .pipeline.transform import run_transform
from .pipeline.dedupe import run_dedupe
from .pipeline.fairvalue import run_fairvalue
from .pipeline.baseline import run_baseline
from .pipeline.rank import run_rank
from .view.report import render_table

def main() -> int:
    print('✅ x987 v3 starter (headful-only, universal scraper)')
    settings = get_settings()
    doctor_check()

    print('=== COLLECT ===')
    urls = run_collect(settings)
    print(f'OK {{\"count\": {len(urls)} }}')

    print('=== SCRAPE ===')
    rows = run_scrape(urls, settings)
    print(f'OK {{\"count\": {len(rows)} }}')

    print('=== TRANSFORM ===')
    rows_t = run_transform(rows, settings)
    print(f'OK {{\"count\": {len(rows_t)} }}')

    print('=== DEDUPE ===')
    rows_d = run_dedupe(rows_t, settings)
    print(f'OK {{\"count\": {len(rows_d)} }}')

    print('=== FAIRVALUE ===')
    rows_f = run_fairvalue(rows_d, settings)
    print(f'OK {{\"count\": {len(rows_f)} }}')

    print('=== BASELINE ===')
    rows_b = run_baseline(rows_f, settings)
    print(f'OK {{\"count\": {len(rows_b)} }}')

    print('=== RANK ===')
    rows_r = run_rank(rows_b, settings)
    print(f'OK {{\"count\": {len(rows_r)} }}')

    print('=== VIEW ===')
    render_table(rows_r)
    return 0
"@

Write-Utf8 (Join-Path $pkg "settings.py") @"
from __future__ import annotations
from pathlib import Path

def get_settings() -> dict:
    base = Path.cwd() / 'x987-data'
    (base / 'raw').mkdir(parents=True, exist_ok=True)
    (base / 'normalized').mkdir(parents=True, exist_ok=True)
    return {
        'data_dir': str(base),
        'browser': {'headful': True, 'slow_ms': 400},
        'collector': {'autotempest_url': 'TODO: paste AutoTempest search URL here'},
        'profiles': ['cars_com', 'truecar_com', 'carvana_com'],
    }
"@

Write-Utf8 (Join-Path $pkg "doctor.py") @"
from __future__ import annotations

def doctor_check() -> None:
    try:
        import rich  # noqa
        import playwright  # noqa
    except Exception:
        print('''
[!] Missing deps. Run:
    pip install -r requirements.txt
    python -m playwright install chromium
'''.strip())
        raise
    print('✅ Doctor OK')
"@

Write-Utf8 (Join-Path $pkg "schema.py") @"
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

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
    raw_options: Optional[str] = None
    location: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
"@

# ---------- utils ----------
Write-Utf8 (Join-Path $pkg "utils\io.py") @"
from __future__ import annotations
from pathlib import Path
import csv
from typing import Iterable, Dict, Any

def write_csv(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    cols = sorted({k for r in rows for k in r.keys()})
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
"@

Write-Utf8 (Join-Path $pkg "utils\log.py") "def info(msg: str): print(msg)`n"

Write-Utf8 (Join-Path $pkg "utils\text.py") @"
import re
RE_PRICE = re.compile(r'\$?\s*([0-9][0-9,]{0,})(?:\.\d{2})?')
RE_MILES = re.compile(r'([0-9][0-9,]{0,})\s*(?:miles?|mi\.?)\b', re.I)
RE_YEAR  = re.compile(r'\b(19|20)\d{2}\b')
RE_VIN   = re.compile(r'\b([A-HJ-NPR-Z0-9]{17})\b')

def parse_price(s: str):
    m = RE_PRICE.search(s or '')
    return int(m.group(1).replace(',', '')) if m else None

def parse_miles(s: str):
    m = RE_MILES.search(s or '')
    return int(m.group(1).replace(',', '')) if m else None
"@

# ---------- collectors ----------
Write-Utf8 (Join-Path $pkg "collectors\autotempest.py") @"
from __future__ import annotations
from typing import List, Dict

# TODO: implement headful navigation + extraction of VDP links for multiple hosts
def collect_autotempest(url: str) -> List[Dict[str, str]]:
    # expected shape: { 'source': 'cars.com'|'truecar.com'|'carvana.com', 'listing_url': 'https://...' }
    return []
"@

# ---------- scrapers ----------
Write-Utf8 (Join-Path $pkg "scrapers\universal_vdp.py") @"
from __future__ import annotations
from typing import Dict, Any
from ..schema import Row

# TODO: implement headful Playwright page open, wait via site profile, parse via shared regex.
def scrape_one(url: str, host: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal placeholder: echoes fields so pipeline runs
    return Row(source=host, listing_url=url).to_dict()
"@

Write-Utf8 (Join-Path $pkg "scrapers\profiles\cars_com.py") @"
PROFILE = {
  'site_id': 'cars.com',
  'ready_selectors': ['title'],
  'primary_selectors': {},
  'rate_limit_ms': 600
}
"@

Write-Utf8 (Join-Path $pkg "scrapers\profiles\truecar_com.py") @"
PROFILE = {
  'site_id': 'truecar.com',
  'ready_selectors': ['title'],
  'primary_selectors': {},
  'rate_limit_ms': 800
}
"@

Write-Utf8 (Join-Path $pkg "scrapers\profiles\carvana_com.py") @"
PROFILE = {
  'site_id': 'carvana.com',
  'ready_selectors': ['title'],
  'primary_selectors': {},
  'rate_limit_ms': 800
}
"@

# ---------- pipeline ----------
Write-Utf8 (Join-Path $pkg "pipeline\collect.py") @"
from __future__ import annotations
from typing import List, Dict
from ..collectors.autotempest import collect_autotempest

def run_collect(settings: dict) -> List[Dict[str, str]]:
    url = settings['collector']['autotempest_url']
    if str(url).startswith('TODO'):
        return []  # starter mode
    return collect_autotempest(url)
"@

Write-Utf8 (Join-Path $pkg "pipeline\scrape.py") @"
from __future__ import annotations
from typing import List, Dict
from ..scrapers.universal_vdp import scrape_one

def run_scrape(url_entries: List[Dict[str, str]], settings: dict) -> List[Dict]:
    rows: List[Dict] = []
    for item in url_entries:
        host = item.get('source') or ''
        url = item.get('listing_url') or ''
        rows.append(scrape_one(url, host, profile={}))
    return rows
"@

Write-Utf8 (Join-Path $pkg "pipeline\transform.py") @"
from __future__ import annotations
from typing import List, Dict
# TODO: import options_v2 and apply detection; placeholder passthrough
def run_transform(rows: List[Dict], settings: dict) -> List[Dict]:
    return rows
"@

Write-Utf8 (Join-Path $pkg "pipeline\dedupe.py") @"
from __future__ import annotations
from typing import List, Dict
def run_dedupe(rows: List[Dict], settings: dict) -> List[Dict]:
    # TODO: VIN-based dedupe; placeholder passthrough
    return rows
"@

Write-Utf8 (Join-Path $pkg "pipeline\fairvalue.py") @"
from __future__ import annotations
from typing import List, Dict
def run_fairvalue(rows: List[Dict], settings: dict) -> List[Dict]:
    # TODO: keep existing model unchanged; placeholder passthrough
    return rows
"@

Write-Utf8 (Join-Path $pkg "pipeline\baseline.py") @"
from __future__ import annotations
from typing import List, Dict
def run_baseline(rows: List[Dict], settings: dict) -> List[Dict]:
    # TODO: compute medians/deltas; placeholder passthrough
    return rows
"@

Write-Utf8 (Join-Path $pkg "pipeline\rank.py") @"
from __future__ import annotations
from typing import List, Dict
def run_rank(rows: List[Dict], settings: dict) -> List[Dict]:
    # TODO: keep ranking logic; placeholder passthrough
    return rows
"@

# ---------- view ----------
Write-Utf8 (Join-Path $pkg "view\report.py") @"
from __future__ import annotations
from typing import List, Dict

def render_table(rows: List[Dict]) -> None:
    print('(table placeholder) rows:', len(rows))
"@

Write-Host "✅ Wrote project to $root"
