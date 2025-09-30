"""
FinBERT sentiment analyzer implementation
Transformer-based financial sentiment analysis
"""
from typing import Any, Dict

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .base_sentiment import BaseSentimentAnalyzer


class FinBERTAnalyzer(BaseSentimentAnalyzer):
    """FinBERT sentiment analyzer for financial text"""
    
    def __init__(self):
        super().__init__(name="FinBERT")
        
        self.model_name = "ProsusAI/finbert"
        self.max_length = 512
        
        # Load model and tokenizer
        self.logger.info(f"Loading FinBERT model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # Set to evaluation mode
        self.model.eval()
        
        # Label mapping
        self.labels = ['positive', 'negative', 'neutral']
        
        self.logger.info("FinBERT analyzer initialized")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using FinBERT
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores:
                - compound: Overall sentiment (-1 to 1)
                - positive: Positive probability (0 to 1)
                - neutral: Neutral probability (0 to 1)
                - negative: Negative probability (0 to 1)
                - confidence: Model confidence (0 to 1)
        """
        if not text or not isinstance(text, str):
            self.logger.warning("Invalid text provided for analysis")
            return self._empty_scores()
        
        try:
            # Truncate text if too long
            text = text[:2000]  # Reasonable limit for news articles
            
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length,
                padding=True
            )
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Extract probabilities
            probs = predictions[0].tolist()
            
            # Map to our format (positive, negative, neutral)
            positive_score = probs[0]
            negative_score = probs[1]
            neutral_score = probs[2]
            
            # Calculate compound score (-1 to 1)
            compound = positive_score - negative_score
            
            # Get confidence (max probability)
            confidence = max(probs)
            
            return {
                'compound': compound,
                'positive': positive_score,
                'neutral': neutral_score,
                'negative': negative_score,
                'confidence': confidence
            }
            
        except Exception as e:
            self.logger.error(f"FinBERT analysis failed: {e}")
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
            'negative': 0.0,
            'confidence': 0.0
        }