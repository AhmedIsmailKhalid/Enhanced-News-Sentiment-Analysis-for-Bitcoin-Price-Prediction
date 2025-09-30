"""
Unified data collection script
Runs all collectors in sequence with comprehensive error handling
"""
# ruff: noqa : E402

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
    print("Unified Data Collection")
    print("="*60)
    
    results = {
        'price': False,
        'news': False
    }
    
    # Collect price data
    print("\n→ Running Price Collector...")
    price_collector = PriceCollector()
    results['price'] = price_collector.run_collection()
    
    if results['price']:
        print("✓ Price collection successful")
    else:
        print("✗ Price collection failed")
    
    # Collect news data
    print("\n→ Running News Collector...")
    news_collector = NewsCollector()
    results['news'] = news_collector.run_collection()
    
    if results['news']:
        print("✓ News collection successful")
    else:
        print("✗ News collection failed")
    
    # Summary
    print("\n" + "="*60)
    print("Collection Summary")
    print("="*60)
    
    total = len(results)
    successful = sum(1 for v in results.values() if v)
    failed = total - successful
    
    print(f"Total Collectors: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    for collector_type, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {collector_type.capitalize()}")
    
    print("="*60)
    
    # Exit with appropriate code
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())