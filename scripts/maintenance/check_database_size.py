"""
Check NeonDB storage usage
"""

import sys
from pathlib import Path

from sqlalchemy import text

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import FeatureData, NewsData, PredictionLog, PriceData, SentimentData

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logger = get_logger(__name__)


def main():
    db = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print("Database Storage Analysis")
        print("=" * 60)

        # Get table sizes
        try:
            result = db.execute(
                text(
                    """
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
            """
                )
            )

            print("\nTable Sizes:")
            print("-" * 60)

            total_bytes = 0
            for row in result:
                print(f"{row.tablename:30s} {row.size:>15s}")
                total_bytes += row.size_bytes

            print("=" * 60)
            total_mb = total_bytes / (1024 * 1024)
            available_mb = 512  # NeonDB free tier
            remaining_mb = available_mb - total_mb
            usage_pct = (total_mb / available_mb) * 100

            print(f"{'TOTAL':30s} {total_mb:>12.2f} MB")
            print(f"{'Available (NeonDB Free)':30s} {available_mb:>12.0f} MB")
            print(f"{'Remaining':30s} {remaining_mb:>12.2f} MB")
            print(f"{'Usage':30s} {usage_pct:>12.1f}%")
            print("=" * 60)

            # Warning if usage is high
            if usage_pct > 80:
                logger.warning(f"⚠️  Database usage is {usage_pct:.1f}% - cleanup recommended!")
            elif usage_pct > 90:
                logger.error(f"🚨 Database usage is {usage_pct:.1f}% - cleanup URGENTLY needed!")
            else:
                logger.info(f"✓ Database usage is healthy ({usage_pct:.1f}%)")

        except Exception as e:
            logger.warning(f"Could not get table sizes (requires PostgreSQL): {e}")

        # Record counts
        print("\nRecord Counts:")
        print("-" * 60)

        counts = {
            "Price Data": db.query(PriceData).count(),
            "News Data": db.query(NewsData).count(),
            "Sentiment Data": db.query(SentimentData).count(),
            "Feature Data": db.query(FeatureData).count(),
            "Prediction Logs": db.query(PredictionLog).count(),
        }

        for table, count in counts.items():
            print(f"{table:30s} {count:>15,} records")

        total_records = sum(counts.values())
        print("=" * 60)
        print(f"{'TOTAL':30s} {total_records:>15,} records")
        print("=" * 60)

        # Estimate storage from counts
        estimated_mb = (
            counts["Price Data"] * 0.0002
            + counts["News Data"] * 0.005  # ~200 bytes per record
            + counts["Sentiment Data"] * 0.001  # ~5 KB per article
            + counts["Feature Data"] * 0.006  # ~1 KB per record
            + counts["Prediction Logs"] * 0.0012  # ~6 KB per record  # ~1.2 KB per record
        )

        print(f"\nEstimated Storage: {estimated_mb:.2f} MB")
        print(f"Estimated Usage: {(estimated_mb/512*100):.1f}%")
        print("=" * 60 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
