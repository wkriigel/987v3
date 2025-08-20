import os
import sys
from pathlib import Path
import re

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from x987.scrapers import universal_vdp

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

def test_scrape_one_extracts_fields(monkeypatch):
    html = Path(__file__).parent / "canned" / "sample_vdp.html"
    raw_html = html.read_text(encoding="utf-8")
    body_text = re.search(r"<body>(.*)</body>", raw_html, re.S).group(1)
    monkeypatch.setattr(universal_vdp, "sync_playwright", lambda: make_sync_playwright(body_text, "2010 Porsche Cayman S"))
    row = universal_vdp.scrape_one("http://example.com/car1", "test", {"ready_selectors": [], "primary_selectors": {}, "rate_limit_ms": 0}, {})
    assert row["price_usd"] == 45000
    assert row["mileage"] == 52123
    assert row["vin"] == "WP0AB2A80AL780123"
