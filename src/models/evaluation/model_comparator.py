"""
Compare models trained on VADER vs FinBERT features
"""
from typing import Any, Dict

import numpy as np
import pandas as pd
from scipy import stats

from src.shared.logging import get_logger

from .financial_metrics import FinancialMetrics


class ModelComparator:
    """Compare model performance across feature sets"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.financial_metrics = FinancialMetrics()
    
    def compare_feature_sets(
        self,
        vader_results: Dict[str, Any],
        finbert_results: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Compare VADER vs FinBERT feature sets
        
        Args:
            vader_results: Results from VADER feature set models
            finbert_results: Results from FinBERT feature set models
            
        Returns:
            Comparison DataFrame
        """
        comparison_data = []
        
        # Compare each model type
        for model_type in vader_results.keys():
            if model_type not in finbert_results:
                continue
            
            vader_res = vader_results[model_type]
            finbert_res = finbert_results[model_type]
            
            row = {
                'model': vader_res['model_name'],
                'vader_val_accuracy': vader_res['val_metrics']['accuracy'],
                'vader_val_f1': vader_res['val_metrics']['f1_score'],
                'finbert_val_accuracy': finbert_res['val_metrics']['accuracy'],
                'finbert_val_f1': finbert_res['val_metrics']['f1_score'],
                'accuracy_diff': (
                    finbert_res['val_metrics']['accuracy'] - 
                    vader_res['val_metrics']['accuracy']
                ),
                'f1_diff': (
                    finbert_res['val_metrics']['f1_score'] - 
                    vader_res['val_metrics']['f1_score']
                )
            }
            comparison_data.append(row)
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Determine winner
        comparison_df['winner'] = comparison_df.apply(
            lambda x: 'FinBERT' if x['accuracy_diff'] > 0 else 
                     ('VADER' if x['accuracy_diff'] < 0 else 'Tie'),
            axis=1
        )
        
        return comparison_df
    
    def statistical_significance_test(
        self,
        vader_predictions: np.ndarray,
        finbert_predictions: np.ndarray,
        y_true: np.ndarray
    ) -> Dict[str, Any]:
        """
        Test if performance difference is statistically significant
        Uses McNemar's test for paired predictions
        """
        # Create contingency table
        # Both correct, both wrong, VADER correct/FinBERT wrong, vice versa
        both_correct = ((vader_predictions == y_true) & (finbert_predictions == y_true)).sum()
        both_wrong = ((vader_predictions != y_true) & (finbert_predictions != y_true)).sum()
        vader_only = ((vader_predictions == y_true) & (finbert_predictions != y_true)).sum()
        finbert_only = ((vader_predictions != y_true) & (finbert_predictions == y_true)).sum()
        
        # McNemar's test
        if vader_only + finbert_only > 0:
            chi2 = (abs(vader_only - finbert_only) - 1)**2 / (vader_only + finbert_only)
            p_value = 1 - stats.chi2.cdf(chi2, df=1)
        else:
            chi2 = 0
            p_value = 1.0
        
        return {
            'both_correct': int(both_correct),
            'both_wrong': int(both_wrong),
            'vader_only_correct': int(vader_only),
            'finbert_only_correct': int(finbert_only),
            'mcnemar_chi2': float(chi2),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    
    def generate_comparison_report(
        self,
        vader_results: Dict[str, Any],
        finbert_results: Dict[str, Any],
        vader_test_metrics: Dict[str, Any],
        finbert_test_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive comparison report"""
        
        # Model comparison
        model_comparison = self.compare_feature_sets(vader_results, finbert_results)
        
        report = {
            'model_comparison': model_comparison.to_dict('records'),
            'vader_best_model': model_comparison.loc[
                model_comparison['vader_val_accuracy'].idxmax()
            ].to_dict(),
            'finbert_best_model': model_comparison.loc[
                model_comparison['finbert_val_accuracy'].idxmax()
            ].to_dict(),
            'overall_winner': self._determine_overall_winner(model_comparison),
            'test_performance': {
                'vader': vader_test_metrics,
                'finbert': finbert_test_metrics
            }
        }
        
        return report
    
    def _determine_overall_winner(self, comparison_df: pd.DataFrame) -> str:
        """Determine overall winner across all models"""
        vader_wins = (comparison_df['winner'] == 'VADER').sum()
        finbert_wins = (comparison_df['winner'] == 'FinBERT').sum()
        ties = (comparison_df['winner'] == 'Tie').sum() # noqa
        
        if finbert_wins > vader_wins:
            return 'FinBERT'
        elif vader_wins > finbert_wins:
            return 'VADER'
        else:
            # Compare average accuracy
            avg_vader = comparison_df['vader_val_accuracy'].mean()
            avg_finbert = comparison_df['finbert_val_accuracy'].mean()
            return 'FinBERT' if avg_finbert > avg_vader else 'VADER'