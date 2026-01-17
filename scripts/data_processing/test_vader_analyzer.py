"""
Test VADER sentiment analyzer
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.text_processing.vader_analyzer import VADERAnalyzer
from src.shared.logging import setup_logging


def main():
    setup_logging(log_level="INFO")

    print("=" * 60)
    print("VADER Sentiment Analyzer Test")
    print("=" * 60)

    # Initialize analyzer
    analyzer = VADERAnalyzer()

    # Test cases
    test_texts = [
        {
            "text": "Bitcoin surges to new all-time high as institutional adoption accelerates!",
            "expected": "positive",
        },
        {
            "text": "Cryptocurrency market crashes amid regulatory concerns and security breaches.",
            "expected": "negative",
        },
        {
            "text": "Bitcoin price remains stable around $60,000 with moderate trading volume.",
            "expected": "neutral",
        },
        {
            "text": "The Federal Reserve announced new monetary policy guidelines today.",
            "expected": "neutral",
        },
        {
            "text": "Major exchange suffers devastating hack, millions of dollars stolen from users.",
            "expected": "negative",
        },
    ]

    print("\n→ Running sentiment analysis tests...\n")

    passed = 0
    failed = 0

    for i, test in enumerate(test_texts, 1):
        print(f"Test {i}:")
        print(f"Text: {test['text']}")

        # Analyze
        scores = analyzer.analyze(test["text"])
        compound = scores["compound"]
        category = analyzer.categorize_sentiment(compound)

        print(
            f"Scores: compound={compound:.3f}, pos={scores['positive']:.3f}, "
            f"neu={scores['neutral']:.3f}, neg={scores['negative']:.3f}"
        )
        print(f"Category: {category}")
        print(f"Expected: {test['expected']}")

        # Check if matches expected
        if category == test["expected"]:
            print("✓ PASS\n")
            passed += 1
        else:
            print("✗ FAIL\n")
            failed += 1

    # Summary
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
