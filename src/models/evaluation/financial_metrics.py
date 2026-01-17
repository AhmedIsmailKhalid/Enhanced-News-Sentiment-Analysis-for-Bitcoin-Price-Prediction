"""
Financial-specific evaluation metrics for trading models
"""
from typing import Dict

import numpy as np
import pandas as pd

from src.shared.logging import get_logger


class FinancialMetrics:
    """Calculate financial performance metrics for predictions"""

    def __init__(self):
        self.logger = get_logger(__name__)

    def calculate_directional_accuracy(self, y_true: pd.Series, y_pred: np.ndarray) -> float:
        """
        Calculate directional accuracy
        Percentage of correct up/down predictions
        """
        return (y_true == y_pred).mean()

    def calculate_trading_performance(
        self,
        y_true: pd.Series,
        y_pred: np.ndarray,
        price_changes: pd.Series,
        transaction_cost: float = 0.001,  # 0.1% per trade
    ) -> Dict[str, float]:
        """
        Calculate trading performance metrics

        Args:
            y_true: Actual price direction (1=up, 0=down)
            y_pred: Predicted price direction
            price_changes: Actual price change percentages
            transaction_cost: Trading fee per transaction

        Returns:
            Dictionary with trading metrics
        """
        # Strategy: Long when predict up, short when predict down
        # Returns if prediction correct, -returns if wrong

        correct_predictions = y_true == y_pred  # noqa: F841

        # Calculate returns per trade
        trade_returns = []
        for i, (actual, predicted, price_change) in enumerate(zip(y_true, y_pred, price_changes)):
            if predicted == 1:  # Predicted up (go long)
                if actual == 1:  # Correct
                    trade_return = price_change - transaction_cost
                else:  # Wrong
                    trade_return = -abs(price_change) - transaction_cost
            else:  # Predicted down (go short)
                if actual == 0:  # Correct
                    trade_return = abs(price_change) - transaction_cost
                else:  # Wrong
                    trade_return = -price_change - transaction_cost

            trade_returns.append(trade_return)

        trade_returns = np.array(trade_returns)

        # Calculate metrics
        total_return = trade_returns.sum()
        avg_return = trade_returns.mean()
        winning_trades = (trade_returns > 0).sum()
        losing_trades = (trade_returns < 0).sum()
        win_rate = winning_trades / len(trade_returns) if len(trade_returns) > 0 else 0

        # Sharpe ratio (simplified, assuming daily returns)
        sharpe_ratio = trade_returns.mean() / trade_returns.std() if trade_returns.std() > 0 else 0

        # Maximum drawdown
        cumulative_returns = np.cumsum(trade_returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = cumulative_returns - running_max
        max_drawdown = drawdown.min()

        return {
            "total_return_pct": float(total_return),
            "avg_return_pct": float(avg_return),
            "win_rate": float(win_rate),
            "winning_trades": int(winning_trades),
            "losing_trades": int(losing_trades),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown_pct": float(max_drawdown),
            "total_trades": len(trade_returns),
        }

    def calculate_profit_factor(
        self, y_true: pd.Series, y_pred: np.ndarray, price_changes: pd.Series
    ) -> float:
        """
        Calculate profit factor
        Ratio of gross profit to gross loss
        """
        correct_predictions = y_true == y_pred

        gross_profit = price_changes[correct_predictions].abs().sum()
        gross_loss = price_changes[~correct_predictions].abs().sum()

        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        return float(profit_factor)
