"""
Test sentiment processor with real news articles from database
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from src.data_processing.text_processing.sentiment_processor import SentimentProcessor
from src.shared.database import SessionLocal
from src.shared.logging import setup_logging
from src.shared.models import NewsData, SentimentData


def main():
    setup_logging(log_level="INFO")
    
    print("="*60)
    print("Sentiment Processor Test")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Check if we have news articles
        article_count = db.query(NewsData).count()
        print(f"\n→ Found {article_count} news articles in database")
        
        if article_count == 0:
            print("✗ No articles to process. Run data collection first.")
            return 1
        
        # Check existing sentiment data
        sentiment_count = db.query(SentimentData).count()
        print(f"→ Existing sentiment records: {sentiment_count}")
        
        # Initialize processor (VADER only for now)
        print("\n→ Initializing sentiment processor (VADER only)...")
        processor = SentimentProcessor(use_finbert=False)
        
        # Process unprocessed articles
        print("\n→ Processing unprocessed articles...")
        processed = processor.process_unprocessed_articles(target_db="local")
        
        print(f"\n✓ Processed {processed} articles")
        
        # Show statistics
        print("\n→ Sentiment Statistics:")
        stats = processor.get_sentiment_statistics(db)
        
        print(f"  Total processed: {stats['total_processed']}")
        print("  By category:")
        for category, count in stats['by_category'].items():
            print(f"    {category}: {count}")
        print(f"  Average VADER compound: {stats['average_vader_compound']:.3f}")
        
        # Show sample results
        print("\n→ Sample Results:")
        results = db.execute(text("""
            SELECT 
                n.title,
                s.vader_compound,
                s.sentiment_category
            FROM news_data n
            JOIN sentiment_data s ON n.id = s.news_data_id
            ORDER BY s.processed_at DESC
            LIMIT 5
        """)).fetchall()
        
        for title, compound, category in results:
            print(f"\n  Title: {title[:70]}...")
            print(f"  Compound: {compound:.3f}")
            print(f"  Category: {category}")
        
        print("\n" + "="*60)
        print("✓ Sentiment processing test complete")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())