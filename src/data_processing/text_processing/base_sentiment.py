"""
Base class for sentiment analyzers
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from src.shared.logging import get_logger


class BaseSentimentAnalyzer(ABC):
    """Abstract base class for sentiment analyzers"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"{__name__}.{name}")
    
    @abstractmethod
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        pass
    
    @abstractmethod
    def get_compound_score(self, text: str) -> float:
        """
        Get single compound sentiment score
        
        Args:
            text: Text to analyze
            
        Returns:
            Compound sentiment score (-1 to 1)
        """
        pass
    
    def categorize_sentiment(self, compound_score: float) -> str:
        """
        Categorize sentiment based on compound score
        
        Args:
            compound_score: Compound sentiment score
            
        Returns:
            Sentiment category: 'positive', 'negative', or 'neutral'
        """
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'