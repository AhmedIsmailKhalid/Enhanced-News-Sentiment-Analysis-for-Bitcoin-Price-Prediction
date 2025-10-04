"""
Data preparation for ML model training
Loads features, creates targets, splits data
"""
from typing import Dict, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text

from src.data_processing.feature_engineering.target_generator import TargetGenerator
from src.shared.database import SessionLocal
from src.shared.logging import get_logger


class DataPreparation:
    """Prepare data for model training"""
    
    def __init__(self, prediction_horizon_hours: int = 1):
        self.logger = get_logger(__name__)
        self.target_generator = TargetGenerator(prediction_horizon_hours)
        self.scaler = StandardScaler()
    
    def load_features_from_db(
        self, 
        feature_set_name: str,
        target_db: str = "local",
        min_samples: int = 30
    ) -> pd.DataFrame:
        """
        Load features from database
        
        Args:
            feature_set_name: 'vader' or 'finbert'
            target_db: Database to load from
            min_samples: Minimum samples required
            
        Returns:
            DataFrame with features
        """
        db = self._get_session(target_db)
        
        try:
            query = text("""
                SELECT 
                    timestamp,
                    features
                FROM feature_data
                WHERE feature_set_name = :feature_set
                ORDER BY timestamp ASC
            """)
            
            result = db.execute(query, {'feature_set': feature_set_name})
            rows = result.fetchall()
            
            if len(rows) < min_samples:
                self.logger.warning(
                    f"Insufficient data: {len(rows)} samples (minimum: {min_samples})"
                )
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for row in rows:
                feature_dict = row.features.copy()
                feature_dict['timestamp'] = row.timestamp
                data.append(feature_dict)
            
            df = pd.DataFrame(data)
            
            self.logger.info(
                f"Loaded {len(df)} samples with {len(df.columns)} features "
                f"for {feature_set_name} dataset"
            )
            
            return df
            
        finally:
            db.close()
    
    def prepare_train_test_split(
        self,
        features_df: pd.DataFrame,
        test_size: float = 0.2,
        validation_size: float = 0.1,
        random_state: int = 42
    ) -> Dict[str, pd.DataFrame]:
        """
        Prepare train/validation/test splits with target variable
        
        Args:
            features_df: Features DataFrame
            test_size: Proportion for test set
            validation_size: Proportion for validation set
            random_state: Random seed
            
        Returns:
            Dictionary with train/val/test DataFrames
        """
        # Create target variable
        df_with_target = self.target_generator.create_target(features_df)
        
        if df_with_target.empty:
            self.logger.error("No data after target creation")
            return {}
        
        # Identify feature columns (exclude metadata and target)
        exclude_cols = [
            'timestamp', 'collected_at', 'processed_at', 
            'target', 'future_price', 'price_change_pct',
            'symbol', 'name', 'data_source'  # Add these non-numeric columns
        ]
        
        # Get all columns
        all_cols = df_with_target.columns.tolist()
        
        # Filter to only numeric columns
        feature_cols = []
        for col in all_cols:
            if col not in exclude_cols:
                # Check if column is numeric
                if pd.api.types.is_numeric_dtype(df_with_target[col]):
                    feature_cols.append(col)
                else:
                    self.logger.debug(f"Excluding non-numeric column: {col}")
        
        self.logger.info(f"Using {len(feature_cols)} numeric features for training")
        
        X = df_with_target[feature_cols]
        y = df_with_target['target']
        
        # First split: train+val vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Second split: train vs val
        val_size_adjusted = validation_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted, 
            random_state=random_state, stratify=y_temp
        )
        
        self.logger.info(
            f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}"
        )
        
        # Log class distribution
        self.logger.info(f"Train target distribution: {y_train.value_counts().to_dict()}")
        self.logger.info(f"Val target distribution: {y_val.value_counts().to_dict()}")
        self.logger.info(f"Test target distribution: {y_test.value_counts().to_dict()}")
        
        return {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test,
            'feature_columns': feature_cols
        }
    
    def scale_features(
        self, 
        X_train: pd.DataFrame,
        X_val: pd.DataFrame,
        X_test: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Scale features using StandardScaler
        Fit on train, transform all sets
        
        Returns:
            Tuple of (X_train_scaled, X_val_scaled, X_test_scaled)
        """
        # Fit scaler on training data only
        self.scaler.fit(X_train)
        
        # Transform all sets
        X_train_scaled = pd.DataFrame(
            self.scaler.transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        
        X_val_scaled = pd.DataFrame(
            self.scaler.transform(X_val),
            columns=X_val.columns,
            index=X_val.index
        )
        
        X_test_scaled = pd.DataFrame(
            self.scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )
        
        self.logger.info("Features scaled using StandardScaler")
        
        return X_train_scaled, X_val_scaled, X_test_scaled
    
    def _get_session(self, target_db: str):
        """Get database session"""
        if target_db == "local":
            return SessionLocal()
        elif target_db == "neondb_production":
            import os

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            db_url = os.getenv('NEONDB_PRODUCTION_URL')
            engine = create_engine(db_url)
            SessionFactory = sessionmaker(bind=engine)
            return SessionFactory()
        else:
            raise ValueError(f"Unknown target_db: {target_db}")