"""
Test all database connections and perform basic operations
"""
# ruff: noqa: E402

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(".env.dev")


def test_database_operations(db_url: str, db_name: str) -> bool:
    """Test database with actual CRUD operations"""
    print(f"\n{'='*60}")
    print(f"Testing: {db_name}")
    print("=" * 60)

    try:
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # Test 1: Insert test data
            print("\n→ Test 1: Inserting test data...")
            conn.execute(
                text(
                    """
                INSERT INTO collection_metadata 
                (collector_name, collection_type, status, start_time, records_collected)
                VALUES 
                ('test_collector', 'test', 'success', NOW(), 100)
            """
                )
            )
            conn.commit()
            print("✓ Insert successful")

            # Test 2: Query test data
            print("\n→ Test 2: Querying test data...")
            result = conn.execute(
                text(
                    """
                SELECT collector_name, collection_type, records_collected 
                FROM collection_metadata 
                WHERE collector_name = 'test_collector'
            """
                )
            )
            row = result.fetchone()

            if row:
                print(f"✓ Query successful: {row[0]}, {row[1]}, {row[2]} records")
            else:
                print("✗ Query returned no results")
                return False

            # Test 3: Update test data
            print("\n→ Test 3: Updating test data...")
            conn.execute(
                text(
                    """
                UPDATE collection_metadata 
                SET records_collected = 150 
                WHERE collector_name = 'test_collector'
            """
                )
            )
            conn.commit()
            print("✓ Update successful")

            # Test 4: Verify update
            print("\n→ Test 4: Verifying update...")
            result = conn.execute(
                text(
                    """
                SELECT records_collected 
                FROM collection_metadata 
                WHERE collector_name = 'test_collector'
            """
                )
            )
            row = result.fetchone()

            if row and row[0] == 150:
                print(f"✓ Verification successful: {row[0]} records")
            else:
                print("✗ Verification failed")
                return False

            # Test 5: Delete test data
            print("\n→ Test 5: Cleaning up test data...")
            conn.execute(
                text(
                    """
                DELETE FROM collection_metadata 
                WHERE collector_name = 'test_collector'
            """
                )
            )
            conn.commit()
            print("✓ Cleanup successful")

            # Test 6: Table relationships
            print("\n→ Test 6: Testing table relationships...")

            # Use unique URL to avoid conflicts
            import time

            unique_url = f"http://test.com/article-{int(time.time())}"

            # Insert news data with explicit collected_at
            conn.execute(
                text(
                    """
                INSERT INTO news_data 
                (title, url, content, data_source, word_count, collected_at)
                VALUES 
                ('Test Article', :url, 'Test content', 'test', 10, NOW())
                RETURNING id
            """
                ),
                {"url": unique_url},
            )
            result = conn.execute(text("SELECT currval('news_data_id_seq')"))
            news_id = result.fetchone()[0]
            conn.commit()

            # Insert sentiment data
            conn.execute(
                text(
                    """
                INSERT INTO sentiment_data 
                (news_data_id, vader_compound, vader_positive, vader_neutral, vader_negative,
                combined_sentiment, sentiment_category)
                VALUES 
                (:news_id, 0.5, 0.6, 0.3, 0.1, 0.5, 'positive')
            """
                ),
                {"news_id": news_id},
            )
            conn.commit()

            # Query joined data
            result = conn.execute(
                text(
                    """
                SELECT n.title, s.sentiment_category, s.combined_sentiment
                FROM news_data n
                JOIN sentiment_data s ON n.id = s.news_data_id
                WHERE n.id = :news_id
            """
                ),
                {"news_id": news_id},
            )
            row = result.fetchone()

            if row:
                print(f"✓ Relationship test successful: {row[0]} -> {row[1]}")
            else:
                print("✗ Relationship test failed")
                return False

            # Cleanup
            conn.execute(
                text("DELETE FROM sentiment_data WHERE news_data_id = :news_id"),
                {"news_id": news_id},
            )
            conn.execute(text("DELETE FROM news_data WHERE id = :news_id"), {"news_id": news_id})
            conn.commit()
            print("✓ Relationship test cleanup successful")

        print(f"\n{'='*60}")
        print(f"✓ All tests passed for {db_name}")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed for {db_name}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("Database Connection & Operations Test")
    print("=" * 60)

    results = {}

    # Test local PostgreSQL
    local_url = os.getenv("DATABASE_URL")
    if local_url:
        results["Local PostgreSQL"] = test_database_operations(local_url, "Local PostgreSQL")
    else:
        print("\n✗ DATABASE_URL not configured")
        results["Local PostgreSQL"] = False

    # Test NeonDB Production
    prod_url = os.getenv("NEONDB_PRODUCTION_URL")
    if prod_url:
        results["NeonDB Production"] = test_database_operations(prod_url, "NeonDB Production")
    else:
        print("\n⚠ NEONDB_PRODUCTION_URL not configured - skipping")

    # Test NeonDB Backup
    backup_url = os.getenv("NEONDB_BACKUP_URL")
    if backup_url:
        results["NeonDB Backup"] = test_database_operations(backup_url, "NeonDB Backup")
    else:
        print("\n⚠ NEONDB_BACKUP_URL not configured - skipping")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for db_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {db_name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✓ All database tests passed!")
        return 0
    else:
        print("\n✗ Some database tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
