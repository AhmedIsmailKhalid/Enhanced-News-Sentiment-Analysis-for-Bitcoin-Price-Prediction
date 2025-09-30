"""
Create database tables for Bitcoin Sentiment MLOps
"""
# ruff : noqa

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text

from src.shared.database import Base, engine

# Import models before creating tables to register them with Base
from src.shared.models import CollectionMetadata, FeatureData, NewsData, PriceData, SentimentData


def create_tables() -> bool:
    """Create all database tables"""
    print("=" * 60)
    print("Creating Database Tables")
    print("=" * 60)
    
    try:
        print("\n→ Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema='public' ORDER BY table_name"
            ))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"\n✓ Created {len(tables)} tables:")
                for table in tables:
                    print(f"  • {table}")
            else:
                print("\n✗ No tables found after creation")
                return False
        
        print("\n" + "=" * 60)
        print("✓ Database setup completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Failed to create tables: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)