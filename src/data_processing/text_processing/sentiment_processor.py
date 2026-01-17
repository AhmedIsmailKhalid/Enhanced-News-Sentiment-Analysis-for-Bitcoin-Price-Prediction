"""
Unified sentiment processing with VADER and FinBERT
Both models always run to capture different sentiment aspects
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
    """Process sentiment for collected news articles using both VADER and FinBERT"""

    def __init__(self):
        """Initialize sentiment processor with both analyzers"""
        self.logger = get_logger(__name__)

        # Initialize both analyzers
        self.logger.info("Initializing VADER analyzer...")
        self.vader = VADERAnalyzer()

        self.logger.info("Initializing FinBERT analyzer (this may take a moment)...")
        self.finbert = FinBERTAnalyzer()

        self.logger.info("Both sentiment analyzers initialized successfully")

    def process_unprocessed_articles(self, target_db: str = "local") -> int:
        """
        Process all articles without sentiment analysis using both VADER and FinBERT

        Args:
            target_db: Target database (local, neondb_production, neondb_backup)

        Returns:
            Number of articles processed
        """
        # Get appropriate session
        if target_db == "local":
            db = SessionLocal()
        elif target_db == "neondb_production":
            import os

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            db_url = os.getenv("NEONDB_PRODUCTION_URL")
            if not db_url:
                raise ValueError("NEONDB_PRODUCTION_URL not configured")
            engine = create_engine(db_url)
            SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionFactory()
        elif target_db == "neondb_backup":
            import os

            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            db_url = os.getenv("NEONDB_BACKUP_URL")
            if not db_url:
                raise ValueError("NEONDB_BACKUP_URL not configured")
            engine = create_engine(db_url)
            SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionFactory()
        else:
            raise ValueError(f"Unknown target_db: {target_db}")

        try:
            # Find articles without sentiment
            articles = (
                db.query(NewsData)
                .filter(~NewsData.id.in_(db.query(SentimentData.news_data_id)))  # <-- CORRECT
                .all()
            )

            if not articles:
                self.logger.info("No unprocessed articles found")
                return 0

            self.logger.info(f"Processing {len(articles)} articles with VADER + FinBERT")

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

            self.logger.info(f"Successfully processed {processed_count} articles with both models")
            return processed_count

        finally:
            db.close()

    def analyze_article(self, article: NewsData) -> SentimentData:
        """
        Analyze sentiment for a single article using both VADER and FinBERT

        Args:
            article: NewsData object

        Returns:
            SentimentData object with scores from both models
        """
        # Analyze with VADER
        self.logger.debug(f"Analyzing article {article.id} with VADER...")
        vader_scores = self.vader.analyze(article.content)

        # Analyze with FinBERT
        self.logger.debug(f"Analyzing article {article.id} with FinBERT...")
        finbert_scores = self.finbert.analyze(article.content)

        # Calculate combined sentiment (average of both models)
        combined_sentiment = (vader_scores["compound"] + finbert_scores["compound"]) / 2

        # Categorize sentiment using combined score
        sentiment_category = self.vader.categorize_sentiment(combined_sentiment)

        # Create sentiment data object with both model scores
        sentiment_data = SentimentData(
            news_data_id=article.id,
            # VADER scores
            vader_compound=vader_scores["compound"],
            vader_positive=vader_scores["positive"],
            vader_neutral=vader_scores["neutral"],
            vader_negative=vader_scores["negative"],
            # FinBERT scores
            finbert_compound=finbert_scores["compound"],
            finbert_positive=finbert_scores["positive"],
            finbert_neutral=finbert_scores["neutral"],
            finbert_negative=finbert_scores["negative"],
            finbert_confidence=finbert_scores["confidence"],
            # Combined metrics
            combined_sentiment=combined_sentiment,
            sentiment_category=sentiment_category,
            # Metadata
            processed_at=datetime.utcnow(),
            model_version="vader_3.3.2_finbert_prosusai",
        )

        return sentiment_data

    def get_sentiment_statistics(self, db: Session) -> Dict:
        """Get statistics about processed sentiments"""
        total = db.query(SentimentData).count()

        by_category = db.execute(
            text(
                """
            SELECT sentiment_category, COUNT(*) as count
            FROM sentiment_data
            GROUP BY sentiment_category
        """
            )
        ).fetchall()

        avg_scores = db.execute(
            text(
                """
            SELECT 
                AVG(vader_compound) as avg_vader,
                AVG(finbert_compound) as avg_finbert,
                AVG(combined_sentiment) as avg_combined
            FROM sentiment_data
        """
            )
        ).fetchone()

        return {
            "total_processed": total,
            "by_category": {row[0]: row[1] for row in by_category},
            "average_vader_compound": float(avg_scores[0]) if avg_scores[0] else 0.0,
            "average_finbert_compound": float(avg_scores[1]) if avg_scores[1] else 0.0,
            "average_combined_sentiment": float(avg_scores[2]) if avg_scores[2] else 0.0,
        }
