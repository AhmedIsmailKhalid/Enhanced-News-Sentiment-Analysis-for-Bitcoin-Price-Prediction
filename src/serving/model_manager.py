"""
Model management for production serving
Handles loading, versioning, and model selection
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

from src.shared.logging import get_logger


class ModelManager:
    """Manage trained models for production serving"""
    
    def __init__(self, model_dir: str = "models/saved_models"):
        self.logger = get_logger(__name__)
        self.model_dir = Path(model_dir)
        self.loaded_models = {}
        
    def load_model(
        self, 
        feature_set: str, 
        model_type: str,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load a trained model
        
        Args:
            feature_set: 'vader' or 'finbert'
            model_type: 'logistic_regression', 'random_forest', 'gradient_boosting'
            version: Specific version timestamp (if None, loads latest)
            
        Returns:
            Dictionary with model and metadata
        """
        model_path = self.model_dir / feature_set / model_type
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model path not found: {model_path}")
        
        # Find model files
        model_files = sorted(model_path.glob("model_*.pkl"))
        
        if not model_files:
            raise FileNotFoundError(f"No models found in {model_path}")
        
        # Select version
        if version:
            model_file = model_path / f"model_{version}.pkl"
            if not model_file.exists():
                raise FileNotFoundError(f"Model version not found: {version}")
        else:
            model_file = model_files[-1]  # Latest
        
        # Load model
        self.logger.info(f"Loading model: {model_file}")
        model = joblib.load(model_file)
        
        # Load metadata
        metadata_file = model_file.parent / model_file.name.replace("model_", "metadata_").replace(".pkl", ".json")
        metadata = {}
        
        if metadata_file.exists():
            import json
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        
        # Cache loaded model
        cache_key = f"{feature_set}_{model_type}"
        self.loaded_models[cache_key] = {
            'model': model,
            'metadata': metadata,
            'loaded_at': datetime.now(),
            'version': model_file.stem.replace('model_', '')
        }
        
        self.logger.info(f"Model loaded successfully: {cache_key}")
        
        return self.loaded_models[cache_key]
    
    def get_model(self, feature_set: str, model_type: str) -> Dict[str, Any]:
        """Get cached model or load if not cached"""
        cache_key = f"{feature_set}_{model_type}"
        
        if cache_key not in self.loaded_models:
            return self.load_model(feature_set, model_type)
        
        return self.loaded_models[cache_key]
    
    def list_available_models(self) -> Dict[str, list]:
        """List all available models"""
        available = {
            'vader': [],
            'finbert': []
        }
        
        for feature_set in ['vader', 'finbert']:
            feature_path = self.model_dir / feature_set
            if feature_path.exists():
                for model_dir in feature_path.iterdir():
                    if model_dir.is_dir():
                        model_files = list(model_dir.glob("model_*.pkl"))
                        if model_files:
                            available[feature_set].append({
                                'model_type': model_dir.name,
                                'versions': len(model_files),
                                'latest': model_files[-1].stem.replace('model_', '')
                            })
        
        return available
    
    def reload_model(self, feature_set: str, model_type: str):
        """Reload model (hot-swap)"""
        cache_key = f"{feature_set}_{model_type}"
        
        if cache_key in self.loaded_models:
            del self.loaded_models[cache_key]
        
        return self.load_model(feature_set, model_type)