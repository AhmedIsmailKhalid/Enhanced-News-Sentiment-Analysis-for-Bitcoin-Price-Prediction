"""
End-to-end prediction pipeline
Orchestrates feature retrieval, preprocessing, and model inference
"""
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.shared.logging import get_logger

from .feature_server import FeatureServer
from .model_manager import ModelManager


class PredictionPipeline:
    """Complete pipeline from features to predictions"""
    
    def __init__(self, target_db: str = "local"):
        self.logger = get_logger(__name__)
        self.model_manager = ModelManager()
        self.feature_server = FeatureServer()
        self.target_db = target_db
        self.scaler = StandardScaler()
        
    def predict(
        self,
        feature_set: str = 'vader',
        model_type: str = 'random_forest',
        use_cached_features: bool = True
    ) -> Dict[str, Any]:
        """
        Generate prediction
        
        Args:
            feature_set: 'vader' or 'finbert'
            model_type: Model to use for prediction
            use_cached_features: Use pre-computed features if True
            
        Returns:
            Prediction result dictionary
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Get features
            if use_cached_features:
                features = self.feature_server.get_latest_features(
                    feature_set, self.target_db
                )
            else:
                features = self.feature_server.compute_features_on_demand(
                    feature_set, self.target_db
                )
            
            if features is None or features.empty:
                return {
                    'success': False,
                    'error': 'No features available',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Step 2: Load model
            model_info = self.model_manager.get_model(feature_set, model_type)
            model = model_info['model']
            metadata = model_info['metadata']
            
            # Step 3: Prepare features for prediction
            feature_columns = metadata.get('feature_columns', [])
            
            # Filter to model's expected features and handle missing
            X = self._prepare_features(features, feature_columns)
            
            if X is None:
                return {
                    'success': False,
                    'error': 'Feature preparation failed',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Step 4: Scale features
            X_scaled = self.scaler.fit_transform(X.values.reshape(1, -1))
            
            # Step 5: Make prediction
            prediction = model.predict(X_scaled)[0]
            
            # Step 6: Get prediction probability if available
            probability = None
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X_scaled)[0]
                probability = {
                    'down': float(proba[0]),
                    'up': float(proba[1])
                }
            
            # Calculate response time
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'success': True,
                'prediction': {
                    'direction': 'up' if prediction == 1 else 'down',
                    'direction_numeric': int(prediction),
                    'probability': probability,
                    'confidence': float(max(proba)) if probability else None
                },
                'model_info': {
                    'feature_set': feature_set,
                    'model_type': model_type,
                    'model_version': model_info['version'],
                    'features_used': len(feature_columns)
                },
                'performance': {
                    'response_time_ms': round(response_time_ms, 2),
                    'cached_features': use_cached_features
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def predict_both_models(self, use_cached_features: bool = True) -> Dict[str, Any]:
        """
        Make predictions with both VADER and FinBERT models
        
        Args:
            use_cached_features: Use cached features (faster) or compute on-demand
        
        Returns:
            Dictionary with predictions from both models and agreement status
        """
        import time
        start_time = time.time()
        
        try:
            # Get features for both models
            if use_cached_features:
                vader_features = self.feature_server.get_latest_features('vader', self.target_db)
                finbert_features = self.feature_server.get_latest_features('finbert', self.target_db)
            else:
                vader_features = self.feature_server.compute_features_on_demand('vader', self.target_db)
                finbert_features = self.feature_server.compute_features_on_demand('finbert', self.target_db)
            
            # Load both models (will use cache if already loaded)
            vader_model_info = self.model_manager.get_model('vader', 'random_forest')
            finbert_model_info = self.model_manager.get_model('finbert', 'random_forest')
            
            # Make predictions (no need to pass use_cached_features to _make_single_prediction)
            vader_result = self._make_single_prediction(
                vader_features, 
                vader_model_info, 
                'vader'
            )
            finbert_result = self._make_single_prediction(
                finbert_features, 
                finbert_model_info, 
                'finbert'
            )
            
            # Check agreement
            agreement = (
                vader_result['prediction']['direction_numeric'] == 
                finbert_result['prediction']['direction_numeric']
            )
            
            # Calculate total time
            total_time = (time.time() - start_time) * 1000
            
            return {
                'vader': vader_result,
                'finbert': finbert_result,
                'agreement': agreement,
                'performance': {
                    'total_response_time_ms': total_time
                }
            }
            
        except Exception as e:
            self.logger.error(f"Dual prediction failed: {e}")
            raise

    def _make_single_prediction(self, features, model_info, feature_set):
        """Helper for making a single prediction"""
        try:
            model = model_info['model']
            metadata = model_info['metadata']
            feature_columns = metadata.get('feature_columns', [])
            
            X = self._prepare_features(features, feature_columns)
            if X is None:
                return {'success': False, 'error': 'Feature preparation failed'}
            
            X_scaled = self.scaler.fit_transform(X.values.reshape(1, -1))
            prediction = model.predict(X_scaled)[0]
            
            probability = None
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X_scaled)[0]
                probability = {'down': float(proba[0]), 'up': float(proba[1])}
            
            return {
                'success': True,
                'prediction': {
                    'direction': 'up' if prediction == 1 else 'down',
                    'direction_numeric': int(prediction),
                    'probability': probability,
                    'confidence': float(max(proba)) if probability else None
                },
                'model_info': {
                    'feature_set': feature_set,
                    'model_type': 'random_forest',
                    'model_version': model_info['version']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _prepare_features(
        self, 
        features: pd.Series, 
        expected_columns: list
    ) -> Optional[pd.Series]:
        """
        Prepare features for model input
        Handle missing features and column ordering
        """
        try:
            # Convert to dict if Series
            if isinstance(features, pd.Series):
                features_dict = features.to_dict()
            else:
                features_dict = features
            
            # Filter to numeric features only
            numeric_features = {}
            for col in expected_columns:
                if col in features_dict:
                    val = features_dict[col]
                    # Convert to float, use 0 if conversion fails
                    try:
                        numeric_features[col] = float(val) if val is not None else 0.0
                    except (ValueError, TypeError):
                        numeric_features[col] = 0.0
                else:
                    # Missing feature, use 0
                    numeric_features[col] = 0.0
                    self.logger.warning(f"Missing feature: {col}, using 0")
            
            # Create Series with correct order
            X = pd.Series(numeric_features)[expected_columns]
            
            return X
            
        except Exception as e:
            self.logger.error(f"Feature preparation failed: {e}")
            return None