"""
Gold build: fct_store_sales_daily.
Grain: one row per store per sale date. Purpose: store daily sales summary mart.
"""

import argparse
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_project_root / "shared" / "src"))

from spark_jobs.lib.gold_transform import run_gold_build


def run(load_date: str, **kwargs) -> None:
    run_gold_build("fct_store_sales_daily", load_date, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--load-date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args()
    run(args.load_date)
