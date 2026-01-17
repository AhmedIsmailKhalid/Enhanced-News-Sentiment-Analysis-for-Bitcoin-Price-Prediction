"""Quick test to see what would be deleted"""
# ruff : noqa: E402

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.shared.database import SessionLocal
from src.shared.models import FeatureData, NewsData, PredictionLog, PriceData, SentimentData

RETENTION = {
    "price_data": 90,
    "news_data": 30,
    "sentiment_data": 60,
    "feature_data": 90,
    "prediction_logs": 90,
}


def main():
    db = SessionLocal()

    print("\n" + "=" * 60)
    print("Database Cleanup Test (DRY RUN)")
    print("=" * 60)

    try:
        # Check each table
        cutoff_price = datetime.now(timezone.utc) - timedelta(days=RETENTION["price_data"])
        old_price = db.query(PriceData).filter(PriceData.collected_at < cutoff_price).count()
        total_price = db.query(PriceData).count()
        print("\nPrice Data:")
        print(f"  Total records: {total_price}")
        print(f"  Older than {RETENTION['price_data']} days: {old_price}")
        print(f"  Would delete: {old_price}")

        cutoff_news = datetime.now(timezone.utc) - timedelta(days=RETENTION["news_data"])
        old_news = db.query(NewsData).filter(NewsData.collected_at < cutoff_news).count()
        total_news = db.query(NewsData).count()
        print("\nNews Data:")
        print(f"  Total records: {total_news}")
        print(f"  Older than {RETENTION['news_data']} days: {old_news}")
        print(f"  Would delete: {old_news}")

        cutoff_sentiment = datetime.now(timezone.utc) - timedelta(days=RETENTION["sentiment_data"])
        old_sentiment = (
            db.query(SentimentData).filter(SentimentData.processed_at < cutoff_sentiment).count()
        )
        total_sentiment = db.query(SentimentData).count()
        print("\nSentiment Data:")
        print(f"  Total records: {total_sentiment}")
        print(f"  Older than {RETENTION['sentiment_data']} days: {old_sentiment}")
        print(f"  Would delete: {old_sentiment}")

        cutoff_features = datetime.now(timezone.utc) - timedelta(days=RETENTION["feature_data"])
        old_features = db.query(FeatureData).filter(FeatureData.timestamp < cutoff_features).count()
        total_features = db.query(FeatureData).count()
        print("\nFeature Data:")
        print(f"  Total records: {total_features}")
        print(f"  Older than {RETENTION['feature_data']} days: {old_features}")
        print(f"  Would delete: {old_features}")

        cutoff_predictions = datetime.now(timezone.utc) - timedelta(
            days=RETENTION["prediction_logs"]
        )
        old_predictions = (
            db.query(PredictionLog).filter(PredictionLog.predicted_at < cutoff_predictions).count()
        )
        total_predictions = db.query(PredictionLog).count()
        print("\nPrediction Logs:")
        print(f"  Total records: {total_predictions}")
        print(f"  Older than {RETENTION['prediction_logs']} days: {old_predictions}")
        print(f"  Would delete: {old_predictions}")

        total_old = old_price + old_news + old_sentiment + old_features + old_predictions

        print("\n" + "=" * 60)
        print(f"TOTAL RECORDS THAT WOULD BE DELETED: {total_old}")
        print("=" * 60)
        print("\nThis is a DRY RUN - no data was deleted")
        print("=" * 60 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    main()
