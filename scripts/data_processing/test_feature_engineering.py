"""
Test complete feature engineering pipeline
Creates two separate feature sets: VADER and FinBERT
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.feature_engineering.feature_combiner import FeatureCombiner
from src.shared.logging import setup_logging


def main():
    setup_logging(log_level="INFO")

    print("=" * 60)
    print("Feature Engineering Pipeline Test")
    print("=" * 60)

    # Initialize feature combiner
    print("\n→ Initializing feature combiner...")
    combiner = FeatureCombiner()

    # Create both feature sets
    print("\n→ Creating feature sets...")
    print("This will create two separate datasets:")
    print("  1. VADER + Price + Temporal features")
    print("  2. FinBERT + Price + Temporal features\n")

    try:
        vader_dataset, finbert_dataset = combiner.create_feature_sets(target_db="local")

        if vader_dataset.empty or finbert_dataset.empty:
            print("✗ Feature engineering failed - empty datasets")
            return 1

        print("\n" + "=" * 60)
        print("Feature Engineering Results")
        print("=" * 60)

        # VADER dataset summary
        print("\n→ VADER Feature Set:")
        vader_summary = combiner.get_feature_summary(vader_dataset, "VADER")
        print(f"  Total rows: {vader_summary['total_rows']}")
        print(f"  Total features: {vader_summary['total_features']}")
        print("  Feature breakdown:")
        for category, count in vader_summary["feature_categories"].items():
            print(f"    - {category}: {count}")

        # FinBERT dataset summary
        print("\n→ FinBERT Feature Set:")
        finbert_summary = combiner.get_feature_summary(finbert_dataset, "FinBERT")
        print(f"  Total rows: {finbert_summary['total_rows']}")
        print(f"  Total features: {finbert_summary['total_features']}")
        print("  Feature breakdown:")
        for category, count in finbert_summary["feature_categories"].items():
            print(f"    - {category}: {count}")

        # Show sample features from each
        print("\n→ Sample VADER features:")
        vader_cols = [col for col in vader_dataset.columns if "vader" in col.lower()][:5]
        print(f"  {vader_cols}")

        print("\n→ Sample FinBERT features:")
        finbert_cols = [col for col in finbert_dataset.columns if "finbert" in col.lower()][:5]
        print(f"  {finbert_cols}")

        print("\n→ Sample Price features (shared by both):")
        price_cols = [
            col
            for col in vader_dataset.columns
            if any(x in col for x in ["price", "return", "sma", "rsi"])
        ][:5]
        print(f"  {price_cols}")

        print("\n→ Sample Temporal features (shared by both):")
        temporal_cols = [
            col for col in vader_dataset.columns if any(x in col for x in ["hour", "day", "is_"])
        ][:5]
        print(f"  {temporal_cols}")

        # Check for NaN values
        print("\n→ Data Quality Check:")
        vader_nan_pct = (
            vader_dataset.isnull().sum().sum() / (vader_dataset.shape[0] * vader_dataset.shape[1])
        ) * 100
        finbert_nan_pct = (
            finbert_dataset.isnull().sum().sum()
            / (finbert_dataset.shape[0] * finbert_dataset.shape[1])
        ) * 100

        print(f"  VADER dataset missing values: {vader_nan_pct:.2f}%")
        print(f"  FinBERT dataset missing values: {finbert_nan_pct:.2f}%")

        # Save sample data
        print("\n→ Saving sample datasets...")
        vader_dataset.head(100).to_csv("data/ml_datasets/vader_features_sample.csv", index=False)
        finbert_dataset.head(100).to_csv(
            "data/ml_datasets/finbert_features_sample.csv", index=False
        )
        print("  Saved to data/ml_datasets/")

        print("\n" + "=" * 60)
        print("✓ Feature Engineering Complete")
        print("=" * 60)
        print("\nTwo separate feature sets created successfully:")
        print(
            f"  - VADER dataset: {vader_dataset.shape[0]} rows × {vader_dataset.shape[1]} features"
        )
        print(
            f"  - FinBERT dataset: {finbert_dataset.shape[0]} rows × {finbert_dataset.shape[1]} features"
        )

        return 0

    except Exception as e:
        print(f"\n✗ Feature engineering failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
