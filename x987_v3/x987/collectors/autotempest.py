from __future__ import annotations
from typing import List, Dict, Iterable
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

SUPPORTED_HOSTS = {"cars.com", "truecar.com", "carvana.com"}

def _base_host(netloc: str) -> str:
    # Reduce 'www.cars.com' -> 'cars.com'
    parts = [p for p in netloc.split(".") if p]
    return ".".join(parts[-2:]) if len(parts) >= 2 else netloc

def _extract_vdp_links(hrefs: Iterable[str]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    seen = set()
    for href in hrefs:
        try:
            u = urlparse(href)
            if not (u.scheme and u.netloc):
                continue
            host = _base_host(u.netloc)
            if host not in SUPPORTED_HOSTS:
                continue
            # De-dupe by full URL
            key = (host, href)
            if key in seen:
                continue
            seen.add(key)
            out.append({"source": host, "listing_url": href})
        except Exception:
            continue
    return out

def collect_autotempest(url: str, settings: dict) -> List[Dict[str, str]]:
    """
    Headful navigation to an AutoTempest search URL, then collect VDP links
    for cars.com, truecar.com, and carvana.com.
    """
    browser_cfg = (settings or {}).get("browser", {})
    headless = not browser_cfg.get("headful", True)
    slow = int(browser_cfg.get("slow_ms", 0))

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless, slow_mo=slow)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # Give the page a moment to settle; AutoTempest hydrates content.
        page.wait_for_timeout(1200)

        # First pass: obvious anchors in the DOM
        anchors = page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
        rows = _extract_vdp_links(anchors)
        if rows:
            ctx.close(); browser.close()
            return rows

        # Fallback: grab all anchors again after small scroll (some lazy-load)
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(800)
        anchors2 = page.locator("a[href]").evaluate_all("els => els.map(e => e.href)")
        rows = _extract_vdp_links(anchors + anchors2)

        ctx.close(); browser.close()
        return rows
