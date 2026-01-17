"""
Test Pandera validation with collected data
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_collection.collectors.news_collector import NewsCollector
from src.data_collection.collectors.price_collector import PriceCollector
from src.shared.logging import setup_logging


def test_price_validation():
    """Test price data validation"""
    print("\n" + "=" * 60)
    print("Testing Price Data Pandera Validation")
    print("=" * 60)

    collector = PriceCollector()

    # Collect data
    print("\n→ Collecting price data...")
    data = collector.collect_data()
    print(f"✓ Collected {len(data)} records")

    # Validate with Pandera
    print("\n→ Validating with Pandera...")
    try:
        is_valid = collector.validate_data(data)
        if is_valid:
            print("✓ Pandera validation passed")
            return True
        else:
            print("✗ Pandera validation failed")
            return False
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return False


def test_news_validation():
    """Test news data validation"""
    print("\n" + "=" * 60)
    print("Testing News Data Pandera Validation")
    print("=" * 60)

    collector = NewsCollector()

    # Collect data
    print("\n→ Collecting news data...")
    data = collector.collect_data()
    print(f"✓ Collected {len(data)} records")

    # Validate with Pandera
    print("\n→ Validating with Pandera...")
    try:
        is_valid = collector.validate_data(data)
        if is_valid:
            print("✓ Pandera validation passed")
            return True
        else:
            print("✗ Pandera validation failed")
            return False
    except Exception as e:
        print(f"✗ Validation error: {e}")
        return False


def main():
    setup_logging(log_level="INFO")

    print("=" * 60)
    print("Pandera Validation Test Suite")
    print("=" * 60)

    results = {
        "price": test_price_validation(),
        "news": test_news_validation(),
    }

    # Summary
    print("\n" + "=" * 60)
    print("Validation Test Summary")
    print("=" * 60)

    for data_type, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {data_type.capitalize()} validation")

    all_passed = all(results.values())

    if all_passed:
        print("\n✓ All Pandera validations passed")
        return 0
    else:
        print("\n✗ Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
