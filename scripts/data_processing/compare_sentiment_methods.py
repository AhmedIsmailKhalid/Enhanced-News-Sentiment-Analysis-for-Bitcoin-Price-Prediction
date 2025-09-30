"""
Compare VADER vs FinBERT sentiment analysis on sample articles
"""
# ruff : noqa : E402

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.text_processing.vader_analyzer import VADERAnalyzer
from src.data_processing.text_processing.finbert_analyzer import FinBERTAnalyzer
from src.shared.database import SessionLocal
from src.shared.logging import setup_logging
from src.shared.models import NewsData


def main():
    setup_logging(log_level="INFO")
    
    print("="*60)
    print("VADER vs FinBERT Comparison")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Get sample articles
        articles = db.query(NewsData).limit(5).all()
        
        if not articles:
            print("✗ No articles found. Run data collection first.")
            return 1
        
        print(f"\n→ Analyzing {len(articles)} sample articles...\n")
        
        # Initialize analyzers
        print("Initializing VADER...")
        vader = VADERAnalyzer()
        
        print("Initializing FinBERT (this may take a moment)...")
        finbert = FinBERTAnalyzer()
        
        print("\n")
        
        for i, article in enumerate(articles, 1):
            print(f"Article {i}:")
            print(f"Title: {article.title}")
            print(f"Source: {article.data_source}")
            print(f"Content preview: {article.content[:100]}...")
            
            # VADER analysis
            vader_scores = vader.analyze(article.content)
            vader_category = vader.categorize_sentiment(vader_scores['compound'])
            
            # FinBERT analysis
            finbert_scores = finbert.analyze(article.content)
            finbert_category = finbert.categorize_sentiment(finbert_scores['compound'])
            
            print("\nVADER:")
            print(f"  Compound: {vader_scores['compound']:.3f}")
            print(f"  Category: {vader_category}")
            
            print("\nFinBERT:")
            print(f"  Compound: {finbert_scores['compound']:.3f}")
            print(f"  Positive: {finbert_scores['positive']:.3f}")
            print(f"  Negative: {finbert_scores['negative']:.3f}")
            print(f"  Neutral:  {finbert_scores['neutral']:.3f}")
            print(f"  Confidence: {finbert_scores['confidence']:.3f}")
            print(f"  Category: {finbert_category}")
            
            # Agreement check
            agreement = "✓ AGREE" if vader_category == finbert_category else "✗ DISAGREE"
            print(f"\nAgreement: {agreement}")
            
            print("\n" + "-"*60 + "\n")
        
        print("="*60)
        print("✓ Comparison complete")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())