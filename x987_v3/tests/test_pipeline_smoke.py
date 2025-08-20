import os
import sys
import csv
import re
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from x987.scrapers import universal_vdp
from x987.pipeline.scrape import run_scrape
from x987.pipeline.transform import run_transform
from x987.pipeline.dedupe import run_dedupe
from x987.pipeline.fairvalue import run_fairvalue
from x987.pipeline.baseline import run_baseline
from x987.pipeline.rank import run_rank

def make_sync_playwright(body_text: str, title: str):
    class DummyMouse:
        def wheel(self, x, y):
            pass

    class DummyPage:
        def __init__(self):
            self.mouse = DummyMouse()
        def goto(self, url, wait_until="domcontentloaded"):
            pass
        def wait_for_selector(self, sel, timeout=0):
            pass
        def wait_for_timeout(self, ms):
            pass
        def inner_text(self, selector: str):
            return body_text if selector == "body" else ""
        def title(self):
            return title

    class DummyContext:
        def new_page(self):
            return DummyPage()
        def close(self):
            pass

    class DummyBrowser:
        def new_context(self):
            return DummyContext()
        def close(self):
            pass

    class DummyChromium:
        def launch(self, headless=False, slow_mo=0):
            return DummyBrowser()

    class DummyPlaywright:
        def __init__(self):
            self.chromium = DummyChromium()
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            pass

    return DummyPlaywright()

def test_pipeline_smoke(monkeypatch):
    canned = Path(__file__).parent / "canned"
    html = canned / "sample_vdp.html"
    urls_csv = canned / "urls.csv"
    with urls_csv.open() as f:
        url_entries = list(csv.DictReader(f))
    raw_html = html.read_text(encoding="utf-8")
    body_text = re.search(r"<body>(.*)</body>", raw_html, re.S).group(1)
    monkeypatch.setattr(universal_vdp, "sync_playwright", lambda: make_sync_playwright(body_text, "2010 Porsche Cayman S"))
    rows = run_scrape(url_entries, {})
    rows = run_transform(rows, {})
    rows = run_dedupe(rows, {})
    rows = run_fairvalue(rows, {})
    rows = run_baseline(rows, {})
    rows = run_rank(rows, {})
    assert rows and isinstance(rows, list)
    assert rows[0]["price_usd"] == 45000
    assert rows[0]["mileage"] == 52123
    assert rows[0]["vin"] == "WP0AB2A80AL780123"
