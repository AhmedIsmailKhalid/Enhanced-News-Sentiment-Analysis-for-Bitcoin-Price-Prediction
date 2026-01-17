"""
Create tables in NeonDB (production and backup branches)
"""
# ruff : noqa

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from src.shared.database import Base
from src.shared.models import CollectionMetadata, FeatureData, NewsData, PriceData, SentimentData

load_dotenv(".env.dev")


def create_tables_in_neondb(db_url: str, db_name: str) -> bool:
    """Create tables in specified NeonDB branch"""
    print(f"\n→ Creating tables in NeonDB ({db_name})...")

    try:
        engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(bind=engine)

        # Verify
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='public' ORDER BY table_name"
                )
            )
            tables = [row[0] for row in result]

            if tables:
                print(f"✓ Created {len(tables)} tables in {db_name}:")
                for table in tables:
                    print(f"  • {table}")
                return True
            else:
                print(f"✗ No tables found in {db_name}")
                return False

    except Exception as e:
        print(f"✗ Failed to create tables in {db_name}: {e}")
        return False


def main():
    print("=" * 60)
    print("Creating Tables in NeonDB")
    print("=" * 60)

    prod_url = os.getenv("NEONDB_PRODUCTION_URL")
    backup_url = os.getenv("NEONDB_BACKUP_URL")

    if not prod_url:
        print("\n✗ NEONDB_PRODUCTION_URL not configured in .env.dev")
        return False

    # Create in production branch
    prod_success = create_tables_in_neondb(prod_url, "Production")

    # Create in backup branch (if configured)
    backup_success = True
    if backup_url:
        backup_success = create_tables_in_neondb(backup_url, "Backup")

    if prod_success and backup_success:
        print("\n" + "=" * 60)
        print("✓ NeonDB tables created successfully!")
        print("=" * 60)
        return True
    else:
        print("\n✗ Failed to create some NeonDB tables")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
