"""
News data collector from RSS feeds
Collects Bitcoin news from CoinDesk, Cointelegraph, and Decrypt
"""
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from src.data_collection.collectors.base_collector import BaseCollector
from src.data_collection.validators.data_validator import DataValidator
from src.shared.models import NewsData

load_dotenv('.env.dev')


class NewsCollector(BaseCollector):
    """Collect Bitcoin news from multiple RSS feed sources"""
    
    def __init__(self, target_db: str = "local"):
        super().__init__(name="NewsCollector", collection_type="news", target_db=target_db)
        self.validator = DataValidator()
        
        # Request configuration
        self.request_delay = 3  # seconds between requests
        self.timeout = 10
        
        # Session with user agent
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # RSS feed sources
        self.sources = {
            'coindesk': {
                'enabled': True,
                'url': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
                'content_selectors': ['div.articleBody', 'div.at-content', 'article']
            },
            'cointelegraph': {
                'enabled': True,
                'url': 'https://cointelegraph.com/rss',
                'content_selectors': ['div.post-content', 'div.post__content', 'article']
            },
            'decrypt': {
                'enabled': True,
                'url': 'https://decrypt.co/feed',
                'content_selectors': ['div.post-content', 'div.entry-content', 'article']
            }
        }
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        Collect news articles from all enabled RSS sources
        
        Returns:
            List of article records
        """
        all_articles = []
        max_articles_per_source = int(os.getenv('MAX_ARTICLES_PER_SOURCE', 5))
        
        for source_name, config in self.sources.items():
            if not config['enabled']:
                continue
            
            try:
                self.logger.info(f"Collecting from {source_name}")
                articles = self._collect_from_rss(source_name, config, max_articles_per_source)
                all_articles.extend(articles)
                self.logger.info(f"Collected {len(articles)} articles from {source_name}")
                
                # Rate limiting
                time.sleep(self.request_delay)
                
            except Exception as e:
                self.logger.error(f"Failed to collect from {source_name}: {e}")
                continue
        
        # Remove duplicates by URL
        unique_articles = self._remove_duplicates(all_articles)
        self.logger.info(f"Total unique articles: {len(unique_articles)}")
        
        return unique_articles
    
    def _collect_from_rss(
        self,
        source_name: str,
        config: Dict[str, Any],
        max_articles: int
    ) -> List[Dict[str, Any]]:
        """
        Collect articles from a single RSS feed
        
        Args:
            source_name: Name of the source
            config: Source configuration
            max_articles: Maximum articles to collect
            
        Returns:
            List of article records
        """
        articles = []
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(config['url'])
            
            if feed.bozo:
                self.logger.warning(f"RSS feed has issues: {feed.bozo_exception}")
            
            if not feed.entries:
                self.logger.warning("No entries found in feed")
                return articles
            
            # Process entries
            for i, entry in enumerate(feed.entries[:max_articles]):
                try:
                    article_url = entry.get('link', '')
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    published_str = entry.get('published', '')
                    author = entry.get('author', None)
                    
                    # Parse published date
                    published_at = self._parse_date(published_str)
                    
                    # Try to extract full content
                    full_content = self._extract_content(article_url, config['content_selectors'])
                    
                    # Use full content if available, otherwise summary
                    content = full_content if full_content and len(full_content) > 100 else summary
                    
                    # Skip if content is insufficient
                    if not content or len(content.strip()) < 50:
                        self.logger.debug(f"Skipping article with insufficient content: {title[:50]}")
                        continue
                    
                    # Clean text
                    title = self._clean_text(title)
                    content = self._clean_text(content)
                    summary = self._clean_text(summary) if summary else None
                    
                    # Create article record
                    article = {
                        'title': title,
                        'url': article_url,
                        'content': content,
                        'summary': summary,
                        'author': author,
                        'published_at': published_at,
                        'data_source': source_name,
                        'collected_at': datetime.utcnow(),
                        'word_count': len(content.split()) if content else 0
                    }
                    
                    articles.append(article)
                    self.logger.debug(f"Added article: {title[:50]}...")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process entry {i}: {e}")
                    continue
                
                # Small delay between articles
                time.sleep(0.5)
            
        except Exception as e:
            self.logger.error(f"RSS collection failed: {e}")
        
        return articles
    
    def _extract_content(self, url: str, selectors: List[str]) -> str:
        """
        Extract full article content from URL
        
        Args:
            url: Article URL
            selectors: CSS selectors to try
            
        Returns:
            Extracted content or empty string
        """
        if not url or not url.startswith('http'):
            return ""
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for unwanted in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                unwanted.decompose()
            
            # Try provided selectors
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if len(content) > 100:
                        return content[:5000]  # Limit length
            
            # Fallback to common selectors
            fallback_selectors = ['article', '[role="main"]', 'main', '.article-content']
            for selector in fallback_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if len(content) > 100:
                        return content[:5000]
            
            return ""
            
        except Exception as e:
            self.logger.debug(f"Failed to extract content from {url}: {e}")
            return ""
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse published date from RSS feed"""
        if not date_str:
            return None
        
        try:
            parsed_time = feedparser._parse_date(date_str)
            if parsed_time:
                return datetime(*parsed_time[:6])
        except Exception:
            pass
        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags and entities
        text = re.sub(r'<[^>]+>', '', str(text))
        text = re.sub(r'&[a-zA-Z0-9#]+;', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate articles by URL"""
        seen_urls = set()
        unique = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(article)
        
        self.logger.info(f"Removed {len(articles) - len(unique)} duplicates")
        return unique
    
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """Validate news data using validator"""
        return self.validator.validate_news_data(data)
    
    def store_data(self, data: List[Dict[str, Any]], db: Session) -> int:
        """
        Store news data to database
        
        Args:
            data: List of validated article records
            db: Database session
            
        Returns:
            Number of records stored
        """
        stored_count = 0
        
        for record in data:
            # Check if URL already exists (skip duplicates)
            existing = db.query(NewsData).filter_by(url=record['url']).first()
            if existing:
                self.logger.debug(f"Skipping duplicate URL: {record['url']}")
                continue
            
            news_data = NewsData(
                title=record['title'],
                url=record['url'],
                content=record['content'],
                summary=record['summary'],
                author=record['author'],
                published_at=record['published_at'],
                data_source=record['data_source'],
                collected_at=record['collected_at'],
                word_count=record['word_count']
            )
            
            db.add(news_data)
            stored_count += 1
        
        db.commit()
        return stored_count