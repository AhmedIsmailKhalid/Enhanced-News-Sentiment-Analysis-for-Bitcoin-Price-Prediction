"""
Database Cleanup - Remove old data based on retention policy
Run daily via cron or GitHub Actions
"""
# ruff: noqa: E402

import argparse
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project root to path FIRST
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# NOW import project modules
from src.shared.database import SessionLocal
from src.shared.models import FeatureData, NewsData, PredictionLog, PriceData, SentimentData

# Configure logging to console
logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Retention policy (days)
RETENTION = {
    "price_data": 90,
    "news_data": 30,
    "sentiment_data": 60,
    "feature_data": 90,
    "prediction_logs": 90,
}


def cleanup_old_records(db, model, retention_days, date_column="collected_at", dry_run=False):
    """Delete records older than retention period"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

    try:
        # Build query dynamically based on date column
        if date_column == "collected_at":
            query = db.query(model).filter(model.collected_at < cutoff_date)
        elif date_column == "predicted_at":
            query = db.query(model).filter(model.predicted_at < cutoff_date)
        elif date_column == "processed_at":
            query = db.query(model).filter(model.processed_at < cutoff_date)
        elif date_column == "timestamp":
            query = db.query(model).filter(model.timestamp < cutoff_date)
        else:
            query = db.query(model).filter(model.collected_at < cutoff_date)

        # Count how many would be deleted
        count = query.count()

        if dry_run:
            logger.info(f"  [DRY RUN] Would delete {count} records from {model.__tablename__}")
            return count
        else:
            # Actually delete
            deleted = query.delete()
            db.commit()
            logger.info(f"  Deleted {deleted} records from {model.__tablename__}")
            return deleted

    except Exception as e:
        logger.error(f"Failed to cleanup {model.__tablename__}: {e}")
        db.rollback()
        return 0


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Clean up old database records")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--force", action="store_true", help="Actually delete records (use with caution)"
    )
    args = parser.parse_args()

    # Default to dry run unless --force is specified
    dry_run = not args.force

    if dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No data will be deleted")
        logger.info("=" * 60)
    else:
        logger.warning("=" * 60)
        logger.warning("⚠️  LIVE MODE - Data WILL be deleted!")
        logger.warning("=" * 60)

    logger.info("Starting Database Cleanup")
    logger.info("=" * 60)

    db = SessionLocal()

    try:
        results = {}

        # Cleanup price data
        logger.info(f"Checking price data older than {RETENTION['price_data']} days...")
        results["price_data"] = cleanup_old_records(
            db, PriceData, RETENTION["price_data"], "collected_at", dry_run
        )

        # Cleanup news data
        logger.info(f"Checking news data older than {RETENTION['news_data']} days...")
        results["news_data"] = cleanup_old_records(
            db, NewsData, RETENTION["news_data"], "collected_at", dry_run
        )

        # Cleanup sentiment data
        logger.info(f"Checking sentiment data older than {RETENTION['sentiment_data']} days...")
        results["sentiment_data"] = cleanup_old_records(
            db, SentimentData, RETENTION["sentiment_data"], "processed_at", dry_run
        )

        # Cleanup feature data
        logger.info(f"Checking feature data older than {RETENTION['feature_data']} days...")
        results["feature_data"] = cleanup_old_records(
            db, FeatureData, RETENTION["feature_data"], "timestamp", dry_run
        )

        # Cleanup prediction logs
        logger.info(f"Checking predictions older than {RETENTION['prediction_logs']} days...")
        results["prediction_logs"] = cleanup_old_records(
            db, PredictionLog, RETENTION["prediction_logs"], "predicted_at", dry_run
        )

        # Summary
        logger.info("\n" + "=" * 60)
        if dry_run:
            logger.info("Cleanup Summary (DRY RUN):")
        else:
            logger.info("Cleanup Summary (ACTUAL DELETION):")
        logger.info("=" * 60)

        total = 0
        for table, count in results.items():
            logger.info(f"  {table}: {count} records")
            total += count

        if dry_run:
            logger.info(f"\nTotal: {total} records WOULD BE deleted")
            logger.info("\nTo actually delete, run with --force flag:")
            logger.info("  poetry run python scripts/maintenance/cleanup_old_data.py --force")
        else:
            logger.info(f"\nTotal: {total} records DELETED")

        logger.info("=" * 60)

        return total > 0

    finally:
        db.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0)
