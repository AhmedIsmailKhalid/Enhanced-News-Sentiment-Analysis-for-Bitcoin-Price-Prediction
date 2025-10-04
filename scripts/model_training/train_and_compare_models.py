"""
Train models on both VADER and FinBERT feature sets and compare
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.evaluation.financial_metrics import FinancialMetrics
from src.models.evaluation.model_comparator import ModelComparator
from src.models.training_pipeline.data_preparation import DataPreparation
from src.models.training_pipeline.model_trainer import ModelTrainer
from src.shared.logging import setup_logging


def main():
    setup_logging(log_level="INFO")
    
    print("="*60)
    print("Model Training & Comparison Pipeline")
    print("="*60)
    
    # Initialize components
    data_prep = DataPreparation(prediction_horizon_hours=1)
    trainer = ModelTrainer()
    comparator = ModelComparator()
    financial_metrics = FinancialMetrics() # noqa
    
    # Results storage
    all_results = {
        'vader': {},
        'finbert': {}
    }
    
    # Train on both feature sets
    for feature_set in ['vader', 'finbert']:
        print(f"\n{'='*60}")
        print(f"Training on {feature_set.upper()} Feature Set")
        print("="*60)
        
        # Load features
        print(f"\n Loading {feature_set} features from database...")
        features_df = data_prep.load_features_from_db(
            feature_set_name=feature_set,
            target_db="neondb_production",
            min_samples=30
        )
        
        if features_df.empty:
            print(f"✗ Insufficient data for {feature_set} training")
            continue
        
        # Prepare train/val/test splits
        print("\n Preparing data splits...")
        splits = data_prep.prepare_train_test_split(
            features_df,
            test_size=0.2,
            validation_size=0.1
        )
        
        if not splits:
            print(f"✗ Data preparation failed for {feature_set}")
            continue
        
        # Scale features
        print("\n Scaling features...")
        X_train_scaled, X_val_scaled, X_test_scaled = data_prep.scale_features(
            splits['X_train'],
            splits['X_val'],
            splits['X_test']
        )
        
        # Train all models
        print("\n Training models...")
        results = trainer.train_all_models(
            X_train_scaled,
            splits['y_train'],
            X_val_scaled,
            splits['y_val']
        )
        
        # Store results
        all_results[feature_set] = {
            'model_results': results,
            'splits': splits,
            'scaled_data': {
                'X_test': X_test_scaled,
                'y_test': splits['y_test']
            }
        }
        
        # Show model comparison for this feature set
        print(f"\n {feature_set.upper()} Model Performance:")
        comparison = trainer.compare_models(results)
        print(comparison.to_string(index=False))
        
        # Evaluate best model on test set
        best_model_type = comparison.iloc[0]['model']
        best_model_key = [k for k, v in results.items() 
                          if v['model_name'] == best_model_type][0]
        best_model = results[best_model_key]['model']
        
        print(f"\n Evaluating best model ({best_model_type}) on test set...")
        test_metrics = trainer.evaluate_model(
            best_model,
            X_test_scaled,
            splits['y_test']
        )
        
        print(f"  Test Accuracy: {test_metrics['accuracy']:.4f}")
        print(f"  Test F1 Score: {test_metrics['f1_score']:.4f}")
        print(f"  Test ROC AUC: {test_metrics.get('roc_auc', 'N/A'):.4f}" 
              if 'roc_auc' in test_metrics else "")
        
        # Save best model
        print("\n Saving best model...")
        model_path = trainer.save_model(
            best_model,
            best_model_key,
            feature_set,
            {
                'feature_set': feature_set,
                'model_type': best_model_key,
                'test_metrics': test_metrics,
                'feature_columns': splits['feature_columns']
            }
        )
        print(f"  Saved to: {model_path}")
    
    # Compare VADER vs FinBERT
    print(f"\n{'='*60}")
    print("VADER vs FinBERT Comparison")
    print("="*60)
    
    if 'vader' in all_results and 'finbert' in all_results:
        if (all_results['vader']['model_results'] and 
            all_results['finbert']['model_results']):
            
            # Generate comparison report
            comparison_df = comparator.compare_feature_sets(
                all_results['vader']['model_results'],
                all_results['finbert']['model_results']
            )
            
            print("\n Model Performance Comparison:")
            print(comparison_df.to_string(index=False))
            
            # Statistical significance test (using best models)
            print("\n Statistical Significance Test:")
            
            # Get predictions from best models
            vader_best = max(
                all_results['vader']['model_results'].values(),
                key=lambda x: x['val_metrics']['accuracy']
            )
            finbert_best = max(
                all_results['finbert']['model_results'].values(),
                key=lambda x: x['val_metrics']['accuracy']
            )
            
            vader_pred = vader_best['model'].predict(
                all_results['vader']['scaled_data']['X_test']
            )
            finbert_pred = finbert_best['model'].predict(
                all_results['finbert']['scaled_data']['X_test']
            )
            
            sig_test = comparator.statistical_significance_test(
                vader_pred,
                finbert_pred,
                all_results['vader']['scaled_data']['y_test'].values
            )
            
            print(f"  McNemar's Chi-squared: {sig_test['mcnemar_chi2']:.4f}")
            print(f"  P-value: {sig_test['p_value']:.4f}")
            print(f"  Significant difference: {'Yes' if sig_test['significant'] else 'No'}")
            
            # Overall winner
            print(f"\n Overall Winner: {comparator._determine_overall_winner(comparison_df)}")
    
    print("\n" + "="*60)
    print("✓ Training and comparison complete")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())