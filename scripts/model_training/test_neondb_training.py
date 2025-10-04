"""
Test training pipeline with NeonDB production data
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.training_pipeline.data_preparation import DataPreparation
from src.models.training_pipeline.model_trainer import ModelTrainer
from src.shared.logging import setup_logging


def main():
    setup_logging(log_level="INFO")
    
    print("="*60)
    print("NeonDB Training Pipeline Test")
    print("="*60)
    
    data_prep = DataPreparation(prediction_horizon_hours=1)
    trainer = ModelTrainer()
    
    # Test with VADER features from NeonDB
    print("\n Loading VADER features from NeonDB...")
    vader_df = data_prep.load_features_from_db(
        feature_set_name='vader',
        target_db='neondb_production',
        min_samples=30
    )
    
    print(f"  Loaded {len(vader_df)} samples")
    print(f"  Features: {len(vader_df.columns)}")
    
    if len(vader_df) >= 30:
        print("\n Preparing data splits...")
        splits = data_prep.prepare_train_test_split(vader_df)
        
        print("\n Scaling features...")
        X_train, X_val, X_test = data_prep.scale_features(
            splits['X_train'],
            splits['X_val'],
            splits['X_test']
        )
        
        print("\n Training Random Forest model...")
        result = trainer.train_model(
            'random_forest',
            X_train,
            splits['y_train'],
            X_val,
            splits['y_val']
        )
        
        print("\n Training successful!")
        print(f"  Train Accuracy: {result['train_metrics']['accuracy']:.4f}")
        print(f"  Val Accuracy: {result['val_metrics']['accuracy']:.4f}")
        
    return 0


if __name__ == "__main__":
    sys.exit(main())