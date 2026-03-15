"""
Ingestion job: upload local raw data to MinIO.

Usage:
    python -m ingestion.jobs.run_ingestion
    python -m ingestion.jobs.run_ingestion --load-date 2025-03-13
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# Ensure project root is on path
_project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_project_root / "shared" / "src"))

from ingestion.src.loaders.file_loader import load_all_entities
from retail_lakehouse.utils.logging_utils import get_logger

logger = get_logger(__name__)


def main() -> int:
    """Run ingestion job. Returns 0 on success, 1 on failure."""
    parser = argparse.ArgumentParser(description="Upload raw data to MinIO")
    parser.add_argument(
        "--load-date",
        type=str,
        default=None,
        help="Load date (YYYY-MM-DD). Default: today.",
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default=None,
        help="Local data/raw directory. Default: from config.",
    )
    parser.add_argument(
        "--entities",
        type=str,
        nargs="*",
        default=None,
        help="Entities to ingest. Default: all.",
    )
    args = parser.parse_args()

    load_date = None
    if args.load_date:
        try:
            load_date = date.fromisoformat(args.load_date)
        except ValueError:
            logger.error("Invalid load-date: %s (use YYYY-MM-DD)", args.load_date)
            return 1

    raw_dir = Path(args.raw_dir) if args.raw_dir else None

    logger.info("Starting ingestion (load_date=%s)", load_date or "today")
    try:
        results = load_all_entities(raw_dir=raw_dir, load_date=load_date, entities=args.entities)
    except ValueError as e:
        logger.error("%s", e)
        return 1

    failed = [e for e, ok in results.items() if not ok]
    if failed:
        logger.error("Ingestion failed for: %s", failed)
        return 1

    logger.info("Ingestion complete. All %d entities uploaded.", len(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
