import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from x987.utils.text import detect_transmission
from x987.scrapers.universal_vdp import _extract_options
from x987.pipeline.transform import run_transform


def test_detect_and_normalize_transmission():
    txt = "This car has a 7-speed PDK gearbox"
    raw = detect_transmission(txt)
    assert raw == "7-speed PDK"
    rows = run_transform([{ "transmission_raw": raw }], {})
    assert rows[0]["transmission_raw"] == raw
    assert rows[0]["transmission"] == "PDK"


def test_extract_options():
    body = "Features:\n• Sport Chrono Package\n• Bose Audio\n- Heated Seats"
    opts = _extract_options(body)
    assert opts == "Sport Chrono Package; Bose Audio; Heated Seats"


def test_run_transform_parses_options_string():
    rows = run_transform([{ "raw_options": "First Option\nSecond Option" }], {})
    assert rows[0]["raw_options"] == "First Option; Second Option"


