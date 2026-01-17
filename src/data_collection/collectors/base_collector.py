"""
Abstract base class for all data collectors
Provides common functionality for data collection, validation, and storage
"""
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import CollectionMetadata

load_dotenv(".env.dev")


class BaseCollector(ABC):
    """
    Abstract base class for data collectors

    Provides:
    - Standardized collection workflow
    - Error handling and logging
    - Metadata tracking
    - Multi-database support (local, NeonDB production, NeonDB backup)
    """

    def __init__(self, name: str, collection_type: str, target_db: str = "local"):
        """
        Initialize collector

        Args:
            name: Collector name (e.g., "PriceCollector")
            collection_type: Type of data (e.g., "price", "news", "social")
            target_db: Target database ("local", "neondb_production", "neondb_backup")
        """
        self.name = name
        self.collection_type = collection_type
        self.target_db = target_db
        self.logger = get_logger(f"{__name__}.{name}")

        # Get appropriate session factory based on target
        self.SessionLocal = self._get_session_factory(target_db)

    def _get_session_factory(self, target_db: str):
        """
        Get session factory for target database

        Args:
            target_db: Target database identifier

        Returns:
            SessionLocal factory for the target database
        """
        if target_db == "local":
            return SessionLocal

        elif target_db == "neondb_production":
            db_url = os.getenv("NEONDB_PRODUCTION_URL")
            if not db_url:
                raise ValueError("NEONDB_PRODUCTION_URL not configured")
            engine = create_engine(db_url)
            return sessionmaker(autocommit=False, autoflush=False, bind=engine)

        elif target_db == "neondb_backup":
            db_url = os.getenv("NEONDB_BACKUP_URL")
            if not db_url:
                raise ValueError("NEONDB_BACKUP_URL not configured")
            engine = create_engine(db_url)
            return sessionmaker(autocommit=False, autoflush=False, bind=engine)

        else:
            raise ValueError(f"Unknown target_db: {target_db}")

    @abstractmethod
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect data from external source

        Must be implemented by subclasses

        Returns:
            List of data records as dictionaries
        """
        pass

    @abstractmethod
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate collected data

        Must be implemented by subclasses

        Args:
            data: List of data records to validate

        Returns:
            True if data is valid, False otherwise
        """
        pass

    @abstractmethod
    def store_data(self, data: List[Dict[str, Any]], db: Session) -> int:
        """
        Store validated data to database

        Must be implemented by subclasses

        Args:
            data: List of validated data records
            db: Database session

        Returns:
            Number of records stored
        """
        pass

    def run_collection(self) -> bool:
        """
        Execute complete collection workflow

        Workflow:
        1. Start collection (create metadata record)
        2. Collect data from source
        3. Validate collected data
        4. Store validated data
        5. Update metadata with results

        Returns:
            True if collection succeeded, False otherwise
        """
        db = self.SessionLocal()
        start_time = datetime.utcnow()
        records_collected = 0

        # Create collection metadata record
        metadata = CollectionMetadata(
            collector_name=self.name,
            collection_type=self.collection_type,
            status="running",
            start_time=start_time,
        )

        try:
            db.add(metadata)
            db.commit()

            self.logger.info(f"Starting {self.name} collection (target: {self.target_db})")

            # Step 1: Collect data
            self.logger.info("Collecting data from source")
            data = self.collect_data()

            if not data:
                self.logger.warning("No data collected from source")
                metadata.status = "success"
                metadata.records_collected = 0
                metadata.end_time = datetime.utcnow()
                db.commit()
                return True

            self.logger.info(f"Collected {len(data)} records")

            # Step 2: Validate data
            self.logger.info("Validating collected data")
            if not self.validate_data(data):
                raise ValueError("Data validation failed")

            self.logger.info("Data validation passed")

            # Step 3: Store data
            self.logger.info(f"Storing data to {self.target_db}")
            records_collected = self.store_data(data, db)

            # Update metadata
            metadata.status = "success"
            metadata.records_collected = records_collected
            metadata.end_time = datetime.utcnow()

            db.commit()

            self.logger.info(
                f"Collection completed successfully: {records_collected} records stored to {self.target_db}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Collection failed: {e}", exc_info=True)

            # Update metadata with error
            metadata.status = "error"
            metadata.error_message = str(e)[:500]
            metadata.end_time = datetime.utcnow()
            metadata.records_collected = records_collected

            try:
                db.commit()
            except Exception:
                db.rollback()

            return False

        finally:
            db.close()

    def test_connection(self) -> bool:
        """
        Test connection to data source

        Override in subclasses for source-specific testing

        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_data = self.collect_data()
            self.logger.info(
                f"Connection test successful: {len(test_data) if test_data else 0} records"
            )
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
