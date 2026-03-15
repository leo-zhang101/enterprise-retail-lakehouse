"""
Warehouse load job: load Gold parquet into PostgreSQL staging.
"""

import argparse
import logging
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_project_root))

from warehouse.src.loaders.postgres_loader import run_warehouse_load
from warehouse.src.connectors.postgres_client import test_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(description="Load Gold parquet into PostgreSQL staging")
    parser.add_argument("--load-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--gold-path", default=None, help="Base path to Gold parquet (default: GOLD_PATH env or ./gold)")
    parser.add_argument("--tables", nargs="*", default=None, help="Tables to load (default: all)")
    args = parser.parse_args()

    if not test_connection():
        logger.error("PostgreSQL connection failed. Check POSTGRES_* env vars.")
        return 1

    try:
        results = run_warehouse_load(
            load_date=args.load_date,
            gold_base=args.gold_path,
            tables=args.tables,
        )
        total = sum(results.values())
        logger.info("Warehouse load complete: %d total rows across %d tables", total, len(results))
        for table, count in results.items():
            logger.info("  %s: %d rows", table, count)
        return 0
    except Exception as e:
        logger.exception("Warehouse load failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
