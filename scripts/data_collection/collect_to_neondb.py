"""
Collect data to NeonDB production
"""
# ruff: noqa: E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_collection.collectors.news_collector import NewsCollector
from src.data_collection.collectors.price_collector import PriceCollector
from src.shared.logging import setup_logging


def main():
    setup_logging(log_level="INFO")
    
    print("="*60)
    print("NeonDB Production Data Collection")
    print("="*60)
    
    results = {}
    
    # Collect to NeonDB Production
    print("\n→ Collecting Price Data to NeonDB...")
    price_collector = PriceCollector(target_db="neondb_production")
    results['price'] = price_collector.run_collection()
    
    print("\n→ Collecting News Data to NeonDB...")
    news_collector = NewsCollector(target_db="neondb_production")
    results['news'] = news_collector.run_collection()
    
    # Summary
    print("\n" + "="*60)
    successful = sum(1 for v in results.values() if v)
    print(f"NeonDB Collection: {successful}/{len(results)} successful")
    print("="*60)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())