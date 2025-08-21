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
    rows = run_transform([{ "raw_options": "Sport Chrono Package\nBose Audio" }], {})
    assert rows[0]["raw_options"] == "Sport Chrono Package; Bose Audio"
    assert rows[0]["options"] == "Sport Chrono, Bose Audio"


def test_vin_infers_model_and_trim():
    vin_s = "WP0AB29889U780241"  # Cayman S
    vin_base = "WP0AA2A85AU760548"  # Cayman Base
    rows = run_transform([
        {"vin": vin_s},
        {"vin": vin_base},
    ], {})
    assert rows[0]["model"] == "Cayman"
    assert rows[0]["trim"] == "S"
    assert rows[1]["model"] == "Cayman"
    assert rows[1]["trim"] == "Base"


