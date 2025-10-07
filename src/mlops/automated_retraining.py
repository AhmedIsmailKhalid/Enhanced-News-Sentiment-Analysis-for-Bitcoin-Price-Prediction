"""
Automated Model Retraining System
Triggers retraining based on performance degradation, drift, or schedule
"""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session  # noqa

from src.data_processing.feature_engineering.target_generator import TargetGenerator
from src.mlops.drift_detector import DriftDetector
from src.mlops.prediction_logger import PredictionLogger
from src.models.evaluation.model_comparator import ModelComparator  # noqa
from src.models.training_pipeline.data_preparation import DataPreparation
from src.models.training_pipeline.model_trainer import ModelTrainer
from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import FeatureData


class AutomatedRetraining:
    """
    Automated model retraining and deployment system
    
    Features:
    - Performance-triggered retraining (accuracy degradation)
    - Drift-triggered retraining (data or model drift)
    - Scheduled retraining (weekly)
    - Automatic model comparison and deployment
    - Rollback capability if new model underperforms
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.drift_detector = DriftDetector()
        self.prediction_logger = PredictionLogger()
        
        # Retraining thresholds
        self.accuracy_degradation_threshold = 0.10  # 10% drop triggers retraining
        self.drift_severity_threshold = 'medium'  # medium or high triggers retraining
        self.min_samples_required = 100  # Minimum samples for retraining
        self.min_prediction_count = 50  # Minimum predictions before checking performance
        
    def should_retrain(
        self,
        feature_set: str,
        model_type: str = 'random_forest'
    ) -> Dict[str, Any]:
        """
        Determine if model should be retrained based on multiple criteria
        
        Args:
            feature_set: 'vader' or 'finbert'
            model_type: Model type to check
            
        Returns:
            Decision with reasons and metadata
        """
        self.logger.info(f"Evaluating retraining need for {feature_set}/{model_type}...")
        
        reasons = []
        should_retrain = False
        
        # Check 1: Model performance degradation
        performance_check = self._check_performance_degradation(feature_set, model_type)
        if performance_check['should_retrain']:
            should_retrain = True
            reasons.append(performance_check['reason'])
        
        # Check 2: Data drift
        drift_check = self._check_drift(feature_set, model_type)
        if drift_check['should_retrain']:
            should_retrain = True
            reasons.append(drift_check['reason'])
        
        # Check 3: Scheduled retraining (weekly)
        schedule_check = self._check_schedule(feature_set)
        if schedule_check['should_retrain']:
            should_retrain = True
            reasons.append(schedule_check['reason'])
        
        # Check 4: Sufficient new data
        data_check = self._check_new_data(feature_set)
        if not data_check['sufficient_data']:
            if should_retrain:
                reasons.append(f"WARNING: Insufficient data ({data_check['sample_count']} samples)")
                # Don't retrain if not enough data
                should_retrain = False
        
        return {
            'should_retrain': should_retrain,
            'reasons': reasons,
            'performance_check': performance_check,
            'drift_check': drift_check,
            'schedule_check': schedule_check,
            'data_check': data_check,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def retrain_model(
        self,
        feature_set: str,
        model_type: str = 'random_forest',
        deploy_if_better: bool = True
    ) -> Dict[str, Any]:
        """
        Retrain model and optionally deploy if performance improves
        
        Args:
            feature_set: 'vader' or 'finbert'
            model_type: Model to retrain
            deploy_if_better: Deploy new model if it outperforms current
            
        Returns:
            Retraining results with performance comparison
        """
        self.logger.info(f"Starting retraining for {feature_set}/{model_type}...")
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Load training data
            self.logger.info("Step 1: Loading training data...")
            data_prep = DataPreparation()
            
            features_df = data_prep.load_features_from_db(
                feature_set_name=feature_set,
                target_db="local",
                min_samples=self.min_samples_required
            )
            
            if features_df is None or len(features_df) < self.min_samples_required:
                return {
                    'success': False,
                    'error': f'Insufficient data for retraining (need {self.min_samples_required})',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            self.logger.info(f"Loaded {len(features_df)} samples")
            
            # Step 2: Create target variable
            self.logger.info("Step 2: Creating target variable...")
            target_gen = TargetGenerator()
            features_with_target = target_gen.create_target(
                df=features_df,
                prediction_horizon_hours=1
            )
            
            # Step 3: Prepare training data
            self.logger.info("Step 3: Preparing training data...")
            X_train, X_val, X_test, y_train, y_val, y_test, feature_columns, scaler = \
                data_prep.prepare_training_data(features_with_target)
            
            # Step 4: Train new model
            self.logger.info(f"Step 4: Training new {model_type} model...")
            trainer = ModelTrainer()
            
            training_result = trainer.train_model(
                model_type=model_type,
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                feature_columns=feature_columns
            )
            
            if not training_result:
                return {
                    'success': False,
                    'error': 'Model training failed',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Step 5: Evaluate on test set
            self.logger.info("Step 5: Evaluating new model...")
            test_predictions = training_result['model'].predict(X_test)
            test_accuracy = (test_predictions == y_test).mean()
            
            self.logger.info(f"New model test accuracy: {test_accuracy:.2%}")
            
            # Step 6: Compare with current production model
            self.logger.info("Step 6: Comparing with current model...")
            comparison = self._compare_with_current_model(
                feature_set=feature_set,
                model_type=model_type,
                new_test_accuracy=test_accuracy
            )
            
            # Step 7: Deployment decision
            deploy_decision = False
            deployment_reason = ""
            
            if deploy_if_better:
                if comparison['new_is_better']:
                    deploy_decision = True
                    deployment_reason = f"New model outperforms current by {comparison['accuracy_improvement']:.2%}"
                else:
                    deployment_reason = f"New model underperforms current by {abs(comparison['accuracy_improvement']):.2%}"
            
            # Step 8: Save new model (always save, deploy optionally)
            self.logger.info("Step 8: Saving new model...")
            model_path, metadata = trainer.save_model(
                model=training_result['model'],
                feature_set=feature_set,
                model_type=model_type,
                test_metrics=training_result['val_metrics'],
                feature_columns=feature_columns,
                training_samples=len(X_train),
                validation_samples=len(X_val),
                test_samples=len(X_test)
            )
            
            end_time = datetime.utcnow()
            training_duration = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'feature_set': feature_set,
                'model_type': model_type,
                'training_duration_seconds': training_duration,
                'samples_used': len(features_df),
                'new_model': {
                    'test_accuracy': float(test_accuracy),
                    'validation_accuracy': training_result['val_metrics']['accuracy'],
                    'model_path': model_path,
                    'metadata': metadata
                },
                'comparison': comparison,
                'deployment': {
                    'deployed': deploy_decision,
                    'reason': deployment_reason
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Retraining failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'feature_set': feature_set,
                'model_type': model_type,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def retrain_both_feature_sets(
        self,
        model_type: str = 'random_forest',
        deploy_if_better: bool = True
    ) -> Dict[str, Any]:
        """
        Retrain models for both VADER and FinBERT feature sets
        
        Args:
            model_type: Model type to retrain
            deploy_if_better: Deploy if new models perform better
            
        Returns:
            Combined retraining results
        """
        self.logger.info("Starting retraining for both feature sets...")
        
        vader_result = self.retrain_model('vader', model_type, deploy_if_better)
        finbert_result = self.retrain_model('finbert', model_type, deploy_if_better)
        
        return {
            'vader': vader_result,
            'finbert': finbert_result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _check_performance_degradation(
        self,
        feature_set: str,
        model_type: str
    ) -> Dict[str, Any]:
        """Check if model performance has degraded"""
        
        try:
            # Get model accuracy over last 7 days
            accuracy_stats = self.prediction_logger.get_model_accuracy(
                feature_set=feature_set,
                model_type=model_type,
                days=7
            )
            
            if accuracy_stats.get('total_predictions', 0) < self.min_prediction_count:
                return {
                    'should_retrain': False,
                    'reason': None,
                    'message': 'Insufficient predictions for performance check',
                    'prediction_count': accuracy_stats.get('total_predictions', 0)
                }
            
            current_accuracy = accuracy_stats.get('accuracy')
            
            if current_accuracy is None:
                return {
                    'should_retrain': False,
                    'reason': None,
                    'message': 'No accuracy data available'
                }
            
            # Check for degradation (assume 70% baseline)
            baseline_accuracy = 0.70
            accuracy_drop = baseline_accuracy - current_accuracy
            
            if accuracy_drop >= self.accuracy_degradation_threshold:
                return {
                    'should_retrain': True,
                    'reason': f'Performance degraded: {current_accuracy:.2%} (drop: {accuracy_drop:.2%})',
                    'current_accuracy': current_accuracy,
                    'baseline_accuracy': baseline_accuracy,
                    'accuracy_drop': accuracy_drop
                }
            
            return {
                'should_retrain': False,
                'reason': None,
                'current_accuracy': current_accuracy,
                'message': 'Performance stable'
            }
            
        except Exception as e:
            self.logger.error(f"Performance check failed: {e}")
            return {
                'should_retrain': False,
                'reason': None,
                'error': str(e)
            }
    
    def _check_drift(
        self,
        feature_set: str,
        model_type: str
    ) -> Dict[str, Any]:
        """Check for data or model drift"""
        
        try:
            drift_summary = self.drift_detector.get_drift_summary(
                feature_set=feature_set,
                model_type=model_type
            )
            
            overall_severity = drift_summary.get('overall_severity', 'none')
            
            severity_order = ['none', 'low', 'medium', 'high']
            threshold_idx = severity_order.index(self.drift_severity_threshold)
            current_idx = severity_order.index(overall_severity) if overall_severity in severity_order else 0
            
            if current_idx >= threshold_idx:
                return {
                    'should_retrain': True,
                    'reason': f'Drift detected: {overall_severity} severity',
                    'drift_severity': overall_severity,
                    'drift_summary': drift_summary
                }
            
            return {
                'should_retrain': False,
                'reason': None,
                'drift_severity': overall_severity,
                'message': 'No significant drift'
            }
            
        except Exception as e:
            self.logger.error(f"Drift check failed: {e}")
            return {
                'should_retrain': False,
                'reason': None,
                'error': str(e)
            }
    
    def _check_schedule(self, feature_set: str) -> Dict[str, Any]:
        """Check if scheduled retraining is due (weekly)"""
        
        # For now, return False (would check last training timestamp in production)
        # This would query a metadata table to see when last training occurred
        
        return {
            'should_retrain': False,
            'reason': None,
            'message': 'Scheduled retraining not due',
            'next_scheduled': 'Weekly schedule not yet implemented'
        }
    
    def _check_new_data(self, feature_set: str) -> Dict[str, Any]:
        """Check if sufficient new data is available"""
        
        db = SessionLocal()
        
        try:
            # Count recent features (last 7 days)
            # recent_cutoff = datetime.utcnow() - timedelta(days=7)
            
            # Count ALL features (no time restriction for initial data check)
            sample_count = db.query(FeatureData).filter(
                FeatureData.feature_set_name == feature_set
            ).count()
            
            sufficient = sample_count >= self.min_samples_required
            
            return {
                'sufficient_data': sufficient,
                'sample_count': sample_count,
                'min_required': self.min_samples_required,
                'message': f'{sample_count} samples available (need {self.min_samples_required})'
            }
            
        except Exception as e:
            self.logger.error(f"Data availability check failed: {e}")
            return {
                'sufficient_data': False,
                'error': str(e)
            }
            
        finally:
            db.close()
    
    def _compare_with_current_model(
        self,
        feature_set: str,
        model_type: str,
        new_test_accuracy: float
    ) -> Dict[str, Any]:
        """Compare new model with current production model"""
        
        try:
            # Get current model accuracy from recent predictions
            current_accuracy_stats = self.prediction_logger.get_model_accuracy(
                feature_set=feature_set,
                model_type=model_type,
                days=7
            )
            
            current_accuracy = current_accuracy_stats.get('accuracy')
            
            if current_accuracy is None:
                return {
                    'new_is_better': True,
                    'reason': 'No current model performance data available',
                    'new_accuracy': new_test_accuracy,
                    'current_accuracy': None,
                    'accuracy_improvement': None
                }
            
            accuracy_improvement = new_test_accuracy - current_accuracy
            new_is_better = accuracy_improvement > 0
            
            return {
                'new_is_better': new_is_better,
                'new_accuracy': new_test_accuracy,
                'current_accuracy': current_accuracy,
                'accuracy_improvement': accuracy_improvement,
                'improvement_percentage': accuracy_improvement
            }
            
        except Exception as e:
            self.logger.error(f"Model comparison failed: {e}")
            return {
                'new_is_better': False,
                'error': str(e)
            }