"""
VADER sentiment analyzer implementation
Fast, rule-based sentiment analysis
"""
from typing import Any, Dict

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .base_sentiment import BaseSentimentAnalyzer


class VADERAnalyzer(BaseSentimentAnalyzer):
    """VADER sentiment analyzer for social media and news text"""
    
    def __init__(self):
        super().__init__(name="VADER")
        self.analyzer = SentimentIntensityAnalyzer()
        self.logger.info("VADER analyzer initialized")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using VADER
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores:
                - compound: Overall sentiment (-1 to 1)
                - positive: Positive score (0 to 1)
                - neutral: Neutral score (0 to 1)
                - negative: Negative score (0 to 1)
        """
        if not text or not isinstance(text, str):
            self.logger.warning("Invalid text provided for analysis")
            return self._empty_scores()
        
        try:
            scores = self.analyzer.polarity_scores(text)
            
            return {
                'compound': scores['compound'],
                'positive': scores['pos'],
                'neutral': scores['neu'],
                'negative': scores['neg']
            }
        except Exception as e:
            self.logger.error(f"VADER analysis failed: {e}")
            return self._empty_scores()
    
    def get_compound_score(self, text: str) -> float:
        """Get compound sentiment score"""
        scores = self.analyze(text)
        return scores['compound']
    
    def _empty_scores(self) -> Dict[str, float]:
        """Return empty scores on error"""
        return {
            'compound': 0.0,
            'positive': 0.0,
            'neutral': 1.0,
            'negative': 0.0
        }