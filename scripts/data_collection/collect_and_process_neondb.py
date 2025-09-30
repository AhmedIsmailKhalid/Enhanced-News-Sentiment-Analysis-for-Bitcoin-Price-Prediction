"""
NeonDB collection with automatic sentiment processing
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_collection.collectors.news_collector import NewsCollector
from src.data_collection.collectors.price_collector import PriceCollector
from src.data_processing.text_processing.sentiment_processor import SentimentProcessor
from src.shared.logging import setup_logging


def main():
    setup_logging(log_level="INFO")
    
    print("="*60)
    print("NeonDB Collection & Sentiment Processing")
    print("="*60)
    
    results = {}
    
    # Step 1: Collect Price Data
    print("\n→ Collecting Price Data to NeonDB...")
    price_collector = PriceCollector(target_db="neondb_production")
    results['price'] = price_collector.run_collection()
    
    # Step 2: Collect News Data
    print("\n→ Collecting News Data to NeonDB...")
    news_collector = NewsCollector(target_db="neondb_production")
    results['news'] = news_collector.run_collection()
    
    # Step 3: Process Sentiment
    print("\n→ Processing Sentiment Analysis on NeonDB...")
    try:
        # VADER only for automated runs (faster)
        processor = SentimentProcessor(use_finbert=False)
        processed = processor.process_unprocessed_articles(target_db="neondb_production")
        
        if processed > 0:
            print(f"✓ Processed {processed} articles")
            results['sentiment'] = True
        else:
            print("✓ All articles already processed")
            results['sentiment'] = True
            
    except Exception as e:
        print(f"✗ Sentiment processing failed: {e}")
        results['sentiment'] = False
    
    # Summary
    print("\n" + "="*60)
    successful = sum(1 for v in results.values() if v)
    print(f"NeonDB Pipeline: {successful}/{len(results)} successful")
    
    for step, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {step.capitalize()}")
    
    print("="*60)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())