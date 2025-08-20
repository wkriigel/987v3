from __future__ import annotations
from pathlib import Path
from .doctor import doctor_check
from .settings import get_settings
from .utils.io import write_csv
from .pipeline.collect import run_collect
from .pipeline.scrape import run_scrape
from .pipeline.transform import run_transform
from .pipeline.dedupe import run_dedupe
from .pipeline.fairvalue import run_fairvalue
from .pipeline.baseline import run_baseline
from .pipeline.rank import run_rank
from .view.report import print_table

def main() -> int:
    print("✅ x987 v3 starter (headful-only, universal scraper)")
    settings = get_settings()
    doctor_check()

    data_dir = Path(settings["data_dir"])
    raw_dir = data_dir / "raw"
    norm_dir = data_dir / "normalized"
    out_dir = data_dir / "out"
    for d in (raw_dir, norm_dir, out_dir):
        d.mkdir(parents=True, exist_ok=True)

    print("=== COLLECT ===")
    urls = run_collect(settings)
    print(f"OK {{\"count\": {len(urls)} }}")
    write_csv(raw_dir / "urls.latest.csv", urls)

    print("=== SCRAPE ===")
    rows = run_scrape(urls, settings)
    print(f"OK {{\"count\": {len(rows)} }}")
    write_csv(raw_dir / "scrape.latest.csv", rows)

    print("=== TRANSFORM ===")
    rows_t = run_transform(rows, settings)
    print(f"OK {{\"count\": {len(rows_t)} }}")
    write_csv(norm_dir / "transform.latest.csv", rows_t)

    print("=== DEDUPE ===")
    rows_d = run_dedupe(rows_t, settings)
    print(f"OK {{\"count\": {len(rows_d)} }}")
    write_csv(norm_dir / "dedupe.latest.csv", rows_d)

    print("=== FAIRVALUE ===")
    rows_f = run_fairvalue(rows_d, settings)
    print(f"OK {{\"count\": {len(rows_f)} }}")
    write_csv(norm_dir / "fairvalue.latest.csv", rows_f)

    print("=== BASELINE ===")
    rows_b = run_baseline(rows_f, settings)
    print(f"OK {{\"count\": {len(rows_b)} }}")
    write_csv(norm_dir / "baseline.latest.csv", rows_b)

    print("=== RANK ===")
    rows_r = run_rank(rows_b, settings)
    print(f"OK {{\"count\": {len(rows_r)} }}")
    write_csv(out_dir / "rank.latest.csv", rows_r)

    print("=== VIEW ===")
    print_table(rows_r)
    return 0
