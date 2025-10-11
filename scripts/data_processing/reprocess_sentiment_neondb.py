"""
Reprocess sentiment for all articles in NeonDB
Run after deleting sentiment_data to regenerate with proper alignment
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_processing.text_processing.sentiment_processor import SentimentProcessor
from src.data_processing.feature_engineering.feature_combiner import FeatureCombiner
from src.data_processing.feature_engineering.feature_storage import FeatureStorageManager
from src.shared.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

def main():
    """Reprocess sentiment and features for NeonDB"""
    
    target_db = "neondb_production"
    
    print("=" * 60)
    print("Reprocessing Sentiment & Features for NeonDB")
    print("=" * 60)
    print()
    
    # Step 1: Process sentiment for all unprocessed articles
    print("→ Processing sentiment analysis...")
    processor = SentimentProcessor()
    article_count = processor.process_unprocessed_articles(target_db=target_db)
    print(f"✓ Processed {article_count} articles")
    print()
    
    # Step 2: Generate features
    print("→ Generating features...")
    combiner = FeatureCombiner()
    vader_df, finbert_df = combiner.create_feature_sets(target_db=target_db)
    print(f"✓ Generated {len(vader_df)} VADER features")
    print(f"✓ Generated {len(finbert_df)} FinBERT features")
    print()
    
    # Step 3: Store features
    print("→ Storing features to NeonDB...")
    storage = FeatureStorageManager()
    result = storage.store_feature_sets(vader_df, finbert_df, target_db=target_db)
    print(f"✓ Stored {result['vader_stored']} VADER features")
    print(f"✓ Stored {result['finbert_stored']} FinBERT features")
    print()
    
    print("=" * 60)
    print("Reprocessing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()