"""
Test news collector in isolation
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_collection.collectors.news_collector import NewsCollector
from src.shared.logging import setup_logging


def main():
    setup_logging(log_level="INFO")

    print("=" * 60)
    print("News Collector Test")
    print("=" * 60)

    collector = NewsCollector()

    # Test 1: Connection
    print("\n→ Test 1: Testing RSS feed connections...")
    if collector.test_connection():
        print("✓ Connection test passed")
    else:
        print("✗ Connection test failed")
        return 1

    # Test 2: Full collection workflow
    print("\n→ Test 2: Running full collection workflow...")
    success = collector.run_collection()

    if success:
        print("✓ Collection workflow completed successfully")
    else:
        print("✗ Collection workflow failed")
        return 1

    print("\n" + "=" * 60)
    print("✓ All news collector tests passed")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
