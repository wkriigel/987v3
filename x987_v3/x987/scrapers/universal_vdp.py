from __future__ import annotations
from typing import Dict, Any, Optional
import importlib, re
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from ..schema import Row
from ..utils.text import parse_price, parse_miles, RE_YEAR, RE_VIN

TX_MAP = [
    (r"(?i)\bPDK\b|dual[- ]clutch|dct|doppelkupplung|7[- ]speed(?:\s*pdk)?", "PDK"),
    (r"(?i)\bTiptronic\b|automatic|auto\b|a/t", "Automatic"),
    (r"(?i)\bmanual\b|6[- ]speed|6mt", "Manual"),
]

def _norm_host(url: str) -> str:
    u = urlparse(url)
    parts = [p for p in (u.netloc or "").split(".") if p]
    return ".".join(parts[-2:]) if len(parts) >= 2 else (u.netloc or "")

def _load_profile(host: str) -> Dict[str, Any]:
    modname = host.replace(".", "_")
    try:
        mod = importlib.import_module(f"x987.scrapers.profiles.{modname}")
        return getattr(mod, "PROFILE")
    except Exception:
        return {
            "site_id": host,
            "ready_selectors": ["h1", "title"],
            "primary_selectors": {"title": "h1"},
            "rate_limit_ms": 800,
        }

def _detect_transmission(text: str) -> Optional[str]:
    if not text:
        return None
    for pat, label in TX_MAP:
        if re.search(pat, text):
            return label
    return None

def _derive_model_trim_from_title(title: str) -> (Optional[int], Optional[str], Optional[str]):
    if not title:
        return None, None, None
    yr = None
    m = RE_YEAR.search(title)
    if m:
        yr = int(m.group(0))
    parts = title.replace("PORSCHE","Porsche").split()
    model, trim = None, None
    if "Porsche" in parts:
        try:
            pidx = parts.index("Porsche")
            after = parts[pidx+1:]
            if after:
                model = after[0].title()
                if len(after) > 1:
                    trim = " ".join(after[1:]).strip()
        except Exception:
            pass
    return yr, model, trim

def _extract_text(page, selector: str) -> str:
    try:
        el = page.locator(selector)
        if el.count() > 0:
            return el.first.inner_text().strip()
    except Exception:
        pass
    return ""

def scrape_one(url: str, host: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    host = host or _norm_host(url)
    prof = profile or _load_profile(host)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=200)
        ctx = browser.new_context()
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded")
        except Exception as ex:
            ctx.close(); browser.close()
            return Row(source=host, listing_url=url, error=f"goto:{ex}").to_dict()

        # wait for any ready selector (best-effort)
        ready = prof.get("ready_selectors") or []
        for sel in ready:
            try:
                page.wait_for_selector(sel, timeout=4000)
                break
            except PWTimeoutError:
                continue

        # small settle + light scroll
        page.wait_for_timeout(600)
        try:
            page.mouse.wheel(0, 800)
            page.wait_for_timeout(400)
        except Exception:
            pass

        # page text for regex parsing
        try:
            body_txt = page.inner_text("body")
        except Exception:
            body_txt = ""

        # title via profile then document.title
        title_sel = (prof.get("primary_selectors") or {}).get("title") or ""
        title_txt = _extract_text(page, title_sel) if title_sel else ""
        if not title_txt:
            try:
                title_txt = page.title() or ""
            except Exception:
                title_txt = ""

        # Parse core fields
        price = parse_price(body_txt)
        miles = parse_miles(body_txt)

        vin = None
        vm = RE_VIN.search(body_txt or "")
        if vm: vin = vm.group(1)

        year, model, trim = _derive_model_trim_from_title(title_txt)
        if not year:
            m = RE_YEAR.search(body_txt or "")
            if m: year = int(m.group(0))

        tx = _detect_transmission(body_txt)

        # heuristic colors/location
        exterior_color = None
        interior_color = None
        location = None
        for line in (body_txt or "").splitlines():
            s = line.strip()
            if not s: continue
            if (not exterior_color) and re.search(r"(?i)exterior", s):
                exterior_color = s.split(":")[-1].strip()
            if (not interior_color) and re.search(r"(?i)interior", s):
                interior_color = s.split(":")[-1].strip()
            if (not location) and re.search(r"(?i)\bLocation\b", s):
                location = s.split(":")[-1].strip()

        row = Row(
            source=host,
            listing_url=url,
            vin=vin,
            year=year,
            model=model,
            trim=trim,
            transmission_raw=tx,
            mileage=miles,
            price_usd=price,
            exterior_color=exterior_color,
            interior_color=interior_color,
            raw_options=None,
            location=location,
            error=None
        ).to_dict()

        # polite delay
        delay_ms = int(prof.get("rate_limit_ms") or 800)
        page.wait_for_timeout(delay_ms)

        ctx.close(); browser.close()
        return row
