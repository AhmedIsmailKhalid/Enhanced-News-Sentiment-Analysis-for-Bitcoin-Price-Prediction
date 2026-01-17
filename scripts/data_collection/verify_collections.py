"""
Verify data collections in database
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from src.shared.database import engine


def main():
    print("=" * 60)
    print("Data Collection Verification")
    print("=" * 60)

    with engine.connect() as conn:
        # Check price data
        print("\n→ Price Data:")
        result = conn.execute(
            text(
                """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT symbol) as unique_symbols,
                MIN(collected_at) as first_collection,
                MAX(collected_at) as last_collection
            FROM price_data
        """
            )
        )
        row = result.fetchone()
        print(f"  Total Records: {row[0]}")
        print(f"  Unique Symbols: {row[1]}")
        print(f"  First Collection: {row[2]}")
        print(f"  Last Collection: {row[3]}")

        # Check news data
        print("\n→ News Data:")
        result = conn.execute(
            text(
                """
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT data_source) as unique_sources,
                AVG(word_count) as avg_word_count,
                MIN(collected_at) as first_collection,
                MAX(collected_at) as last_collection
            FROM news_data
        """
            )
        )
        row = result.fetchone()
        print(f"  Total Records: {row[0]}")
        print(f"  Unique Sources: {row[1]}")
        print(f"  Avg Word Count: {row[2]:.0f}")
        print(f"  First Collection: {row[3]}")
        print(f"  Last Collection: {row[4]}")

        # News by source
        print("\n→ News by Source:")
        result = conn.execute(
            text(
                """
            SELECT data_source, COUNT(*) as count
            FROM news_data
            GROUP BY data_source
            ORDER BY count DESC
        """
            )
        )
        for row in result:
            print(f"  {row[0]}: {row[1]} articles")

        # Collection metadata
        print("\n→ Collection Runs:")
        result = conn.execute(
            text(
                """
            SELECT 
                collector_name,
                status,
                records_collected,
                start_time
            FROM collection_metadata
            ORDER BY start_time DESC
            LIMIT 5
        """
            )
        )
        for row in result:
            print(f"  {row[0]}: {row[1]} - {row[2]} records at {row[3]}")

    print("\n" + "=" * 60)
    print("✓ Verification complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
