"""
Model training pipeline for Bitcoin price prediction
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier

from src.shared.logging import get_logger


class ModelTrainer:
    """Train and evaluate classification models"""

    def __init__(self, model_save_dir: str = "models/saved_models"):
        self.logger = get_logger(__name__)
        self.model_save_dir = Path(model_save_dir)
        self.model_save_dir.mkdir(parents=True, exist_ok=True)

        # Available models
        self.model_configs = {
            "logistic_regression": {
                "model": LogisticRegression(
                    max_iter=1000, random_state=42, class_weight="balanced"
                ),
                "name": "Logistic Regression",
            },
            "random_forest": {
                "model": RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,  # Add depth limit (was None)
                    min_samples_split=20,  # Require more samples to split (was 2)
                    min_samples_leaf=10,  # Require more samples in leaf (was 1)
                    max_features="sqrt",  # Reduce features per tree
                    random_state=42,
                    class_weight="balanced",
                ),
                "name": "Random Forest",
            },
            "gradient_boosting": {
                "model": GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                ),
                "name": "Gradient Boosting",
            },
            "lgbm": {
                "model": LGBMClassifier(
                    n_estimators=100,
                    max_depth=4,
                    learning_rate=0.05,
                    num_leaves=15,  # Limit tree complexity
                    min_child_samples=20,  # Require more samples
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_alpha=0.1,
                    reg_lambda=1.0,
                    random_state=42,
                ),
                "name": "Light GBM",
            },
            "xgboost": {
                "model": XGBClassifier(
                    n_estimators=100,
                    max_depth=4,
                    learning_rate=0.05,
                    min_child_weight=20,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    reg_alpha=0.1,
                    reg_lambda=1.0,
                    random_state=42,
                ),
                "name": "XGBoost",
            },
        }

    def train_model(
        self,
        model_type: str,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Dict[str, Any]:
        """
        Train a single model

        Args:
            model_type: Type of model ('logistic_regression', 'random_forest', 'gradient_boosting')
            X_train: Training features
            y_train: Training target
            X_val: Validation features (optional)
            y_val: Validation target (optional)

        Returns:
            Dictionary with trained model and metrics
        """
        if model_type not in self.model_configs:
            raise ValueError(f"Unknown model type: {model_type}")

        config = self.model_configs[model_type]
        model = config["model"]
        model_name = config["name"]

        self.logger.info(f"Training {model_name}...")

        # Train model
        start_time = datetime.now()
        model.fit(X_train, y_train)
        training_time = (datetime.now() - start_time).total_seconds()

        # Training metrics
        train_pred = model.predict(X_train)
        train_metrics = self._calculate_metrics(y_train, train_pred, model, X_train)

        self.logger.info(f"{model_name} - Train Accuracy: {train_metrics['accuracy']:.4f}")

        # Validation metrics if provided
        val_metrics = None
        if X_val is not None and y_val is not None:
            val_pred = model.predict(X_val)
            val_metrics = self._calculate_metrics(y_val, val_pred, model, X_val)
            self.logger.info(f"{model_name} - Val Accuracy: {val_metrics['accuracy']:.4f}")

        return {
            "model": model,
            "model_type": model_type,
            "model_name": model_name,
            "train_metrics": train_metrics,
            "val_metrics": val_metrics,
            "training_time": training_time,
            "feature_importance": self._get_feature_importance(model, X_train.columns),
        }

    def train_all_models(
        self, X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame, y_val: pd.Series
    ) -> Dict[str, Dict[str, Any]]:
        """Train all available models"""
        results = {}

        for model_type in self.model_configs.keys():
            try:
                result = self.train_model(model_type, X_train, y_train, X_val, y_val)
                results[model_type] = result
            except Exception as e:
                self.logger.error(f"Failed to train {model_type}: {e}")
                continue

        return results

    def evaluate_model(self, model: Any, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Evaluate model on test set"""
        y_pred = model.predict(X_test)

        metrics = self._calculate_metrics(y_test, y_pred, model, X_test)

        # Add confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        metrics["confusion_matrix"] = cm.tolist()

        # Add classification report
        metrics["classification_report"] = classification_report(y_test, y_pred, output_dict=True)

        return metrics

    def _calculate_metrics(
        self, y_true: pd.Series, y_pred: np.ndarray, model: Any, X: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1_score": f1_score(y_true, y_pred, zero_division=0),
        }

        # Add ROC AUC if model has predict_proba
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X)[:, 1]
            metrics["roc_auc"] = roc_auc_score(y_true, y_proba)

        return metrics

    def _get_feature_importance(
        self, model: Any, feature_names: pd.Index
    ) -> Optional[Dict[str, float]]:
        """Extract feature importance if available"""
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            return dict(zip(feature_names, importances.tolist()))
        elif hasattr(model, "coef_"):
            # For logistic regression, use absolute coefficients
            importances = np.abs(model.coef_[0])
            return dict(zip(feature_names, importances.tolist()))
        return None

    def save_model(
        self, model: Any, model_name: str, feature_set_name: str, metadata: Dict[str, Any]
    ) -> str:
        """
        Save trained model with metadata

        Returns:
            Path to saved model
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = self.model_save_dir / feature_set_name / model_name
        model_dir.mkdir(parents=True, exist_ok=True)

        # Save model
        model_path = model_dir / f"model_{timestamp}.pkl"
        joblib.dump(model, model_path)

        # Save metadata
        metadata_path = model_dir / f"metadata_{timestamp}.json"
        import json

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        self.logger.info(f"Model saved to {model_path}")

        return str(model_path)

    def compare_models(self, results: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """Compare all trained models"""
        comparison_data = []

        for model_type, result in results.items():
            row = {
                "model": result["model_name"],
                "train_accuracy": result["train_metrics"]["accuracy"],
                "train_f1": result["train_metrics"]["f1_score"],
                "val_accuracy": result["val_metrics"]["accuracy"]
                if result["val_metrics"]
                else None,
                "val_f1": result["val_metrics"]["f1_score"] if result["val_metrics"] else None,
                "training_time": result["training_time"],
            }
            comparison_data.append(row)

        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values("val_accuracy", ascending=False)

        return comparison_df
