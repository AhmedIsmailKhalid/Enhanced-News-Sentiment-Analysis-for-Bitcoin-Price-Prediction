"""
Unified data collection with automatic sentiment processing
Collects price + news data, then processes sentiment
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
    print("Unified Data Collection & Sentiment Processing")
    print("="*60)
    
    results = {
        'price_collection': False,
        'news_collection': False,
        'sentiment_processing': False
    }
    
    # Step 1: Collect price data
    print("\n→ Step 1: Collecting Price Data...")
    price_collector = PriceCollector()
    results['price_collection'] = price_collector.run_collection()
    
    if results['price_collection']:
        print("✓ Price collection successful")
    else:
        print("✗ Price collection failed")
    
    # Step 2: Collect news data
    print("\n→ Step 2: Collecting News Data...")
    news_collector = NewsCollector()
    results['news_collection'] = news_collector.run_collection()
    
    if results['news_collection']:
        print("✓ News collection successful")
    else:
        print("✗ News collection failed")
    
    # Step 3: Process sentiment for new articles
    print("\n→ Step 3: Processing Sentiment Analysis...")
    try:
        # Use VADER only for speed (FinBERT is too slow for automated runs)
        processor = SentimentProcessor()
        processed_count = processor.process_unprocessed_articles(target_db="local")
        
        if processed_count > 0:
            print(f"✓ Processed sentiment for {processed_count} articles")
            results['sentiment_processing'] = True
        else:
            print("✓ No new articles to process (all up-to-date)")
            results['sentiment_processing'] = True
            
    except Exception as e:
        print(f"✗ Sentiment processing failed: {e}")
        results['sentiment_processing'] = False
        
    # Step 4: Feature Engineering
    print("\n→ Step 4: Engineering Features...")
    try:
        from src.data_processing.feature_engineering.feature_combiner import FeatureCombiner
        from src.data_processing.feature_engineering.feature_storage import FeatureStorageManager

        # Create features
        combiner = FeatureCombiner()
        vader_df, finbert_df = combiner.create_feature_sets(target_db="local")
        
        if not vader_df.empty and not finbert_df.empty:
            # Store features
            storage_manager = FeatureStorageManager()
            storage_results = storage_manager.store_feature_sets(
                vader_df, finbert_df, target_db="local"
            )
            
            print(f"✓ Stored {storage_results['vader_stored']} VADER features")
            print(f"✓ Stored {storage_results['finbert_stored']} FinBERT features")
            results['feature_engineering'] = True
        else:
            print("✗ No features generated (insufficient data)")
            results['feature_engineering'] = False
            
    except Exception as e:
        print(f"✗ Feature engineering failed: {e}")
        results['feature_engineering'] = False

    
    # Summary
    print("\n" + "="*60)
    print("Pipeline Summary")
    print("="*60)
    
    total = len(results)
    successful = sum(1 for v in results.values() if v)
    
    print(f"Total Steps: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    for step, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {step.replace('_', ' ').title()}")
    
    print("="*60)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())