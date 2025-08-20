import options_v2
from x987.pipeline.transform import run_transform


def test_run_transform_normalizes_and_maps_options(monkeypatch):
    monkeypatch.setattr(options_v2, "OPTIONS", {
        "Sport Chrono": ["Sport Chrono Package"],
        "Heated Seats": ["Seat Heating"],
    })
    rows = [{
        "transmission_raw": "7-speed PDK dual clutch",
        "exterior_color": "Agate Gray Metallic",
        "interior_color": "Tan Leather",
        "trim": "Sport Chrono Package",
        "raw_options": ["Seat Heating"],
    }]
    transformed = run_transform(rows, {})
    r = transformed[0]
    assert r["transmission"] == "PDK"
    assert r["exterior_color_bucket"] == "Gray"
    assert r["interior_color_bucket"] == "Brown"
    assert set(r["raw_options"]) == {"Sport Chrono Package", "Seat Heating"}
    assert set(r["options"]) == {"Sport Chrono", "Heated Seats"}

