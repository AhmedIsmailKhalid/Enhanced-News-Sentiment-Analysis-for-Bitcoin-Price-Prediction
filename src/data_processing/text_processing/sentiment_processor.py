"""
Unified sentiment processing with VADER and FinBERT
"""
from datetime import datetime
from typing import Dict

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.shared.database import SessionLocal
from src.shared.logging import get_logger
from src.shared.models import NewsData, SentimentData

from .finbert_analyzer import FinBERTAnalyzer
from .vader_analyzer import VADERAnalyzer


class SentimentProcessor:
    """Process sentiment for collected news articles"""
    
    def __init__(self, use_finbert: bool = True):
        """
        Initialize sentiment processor
        
        Args:
            use_finbert: Whether to use FinBERT (slower but more accurate)
        """
        self.logger = get_logger(__name__)
        
        # Initialize VADER (always use)
        self.vader = VADERAnalyzer()
        
        # Initialize FinBERT (optional)
        self.use_finbert = use_finbert
        self.finbert = FinBERTAnalyzer() if use_finbert else None
        
        self.logger.info(f"Sentiment processor initialized (FinBERT: {use_finbert})")
    
    def process_unprocessed_articles(self, target_db: str = "local") -> int:
        """
        Process all articles without sentiment analysis
        
        Args:
            target_db: Target database (local, neondb_production, neondb_backup)
            
        Returns:
            Number of articles processed
        """
        # Get appropriate session
        if target_db == "local":
            db = SessionLocal()
        else:
            from src.data_collection.collectors.base_collector import BaseCollector

            # Create temporary collector to get session factory
            temp_collector = BaseCollector.__new__(BaseCollector)
            SessionFactory = temp_collector._get_session_factory(target_db)
            db = SessionFactory()
        
        try:
            # Find articles without sentiment
            articles = db.query(NewsData).filter(
                ~NewsData.id.in_(
                    db.query(SentimentData.news_data_id)
                )
            ).all()
            
            if not articles:
                self.logger.info("No unprocessed articles found")
                return 0
            
            self.logger.info(f"Processing {len(articles)} articles")
            
            processed_count = 0
            for article in articles:
                try:
                    sentiment_data = self.analyze_article(article)
                    db.add(sentiment_data)
                    processed_count += 1
                    
                    # Commit in batches of 10
                    if processed_count % 10 == 0:
                        db.commit()
                        self.logger.info(f"Processed {processed_count}/{len(articles)} articles")
                        
                except Exception as e:
                    self.logger.error(f"Failed to process article {article.id}: {e}")
                    continue
            
            # Final commit
            db.commit()
            
            self.logger.info(f"Successfully processed {processed_count} articles")
            return processed_count
            
        finally:
            db.close()
    
    def analyze_article(self, article: NewsData) -> SentimentData:
        """
        Analyze sentiment for a single article
        
        Args:
            article: NewsData object
            
        Returns:
            SentimentData object
        """
        # Analyze with VADER
        vader_scores = self.vader.analyze(article.content)
        
        # Analyze with FinBERT if enabled
        if self.use_finbert and self.finbert:
            finbert_scores = self.finbert.analyze(article.content)
        else:
            finbert_scores = None
        
        # Calculate combined sentiment (average of VADER and FinBERT if available)
        if finbert_scores:
            combined_sentiment = (vader_scores['compound'] + finbert_scores['compound']) / 2
        else:
            combined_sentiment = vader_scores['compound']
        
        # Categorize sentiment
        sentiment_category = self.vader.categorize_sentiment(combined_sentiment)
        
        # Create sentiment data object
        sentiment_data = SentimentData(
            news_data_id=article.id,
            vader_compound=vader_scores['compound'],
            vader_positive=vader_scores['positive'],
            vader_neutral=vader_scores['neutral'],
            vader_negative=vader_scores['negative'],
            finbert_compound=finbert_scores['compound'] if finbert_scores else None,
            finbert_positive=finbert_scores['positive'] if finbert_scores else None,
            finbert_neutral=finbert_scores['neutral'] if finbert_scores else None,
            finbert_negative=finbert_scores['negative'] if finbert_scores else None,
            combined_sentiment=combined_sentiment,
            sentiment_category=sentiment_category,
            processed_at=datetime.utcnow(),
            model_version=f"vader_3.3.2{'_finbert_prosusai' if self.use_finbert else ''}"
        )
        
        return sentiment_data
    
    def get_sentiment_statistics(self, db: Session) -> Dict:
        """Get statistics about processed sentiments"""
        total = db.query(SentimentData).count()
        
        by_category = db.execute(text("""
            SELECT sentiment_category, COUNT(*) as count
            FROM sentiment_data
            GROUP BY sentiment_category
        """)).fetchall()
        
        avg_vader = db.execute(text("""
            SELECT AVG(vader_compound) as avg_vader
            FROM sentiment_data
        """)).fetchone()
        
        return {
            'total_processed': total,
            'by_category': {row[0]: row[1] for row in by_category},
            'average_vader_compound': float(avg_vader[0]) if avg_vader[0] else 0.0
        }