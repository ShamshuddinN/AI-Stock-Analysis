"""
News scraper for NSE companies from multiple sources
"""
import requests
import feedparser
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
import re
from newspaper import Article
from googlesearch import search

from config import NEWS_SOURCES, SCRAPING_CONFIG, ANALYSIS_CONFIG
from utils import get_random_delay, get_random_user_agent, normalize_date

logger = logging.getLogger(__name__)

class NewsSource:
    """Base class for news sources"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_page(self, url: str, retries: int = 3) -> Optional[str]:
        """Get page content with retries"""
        for attempt in range(retries):
            try:
                time.sleep(get_random_delay())
                response = self.session.get(url, timeout=SCRAPING_CONFIG['timeout'])
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    def parse_rss_feed(self, feed_url: str) -> List[Dict]:
        """Parse RSS feed and extract articles"""
        articles = []
        try:
            logger.info(f"Parsing RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'description': entry.get('description', ''),
                    'published': entry.get('published', ''),
                    'source': self.name,
                    'source_url': feed_url
                }
                
                # Parse publication date
                if article['published']:
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                        article['published_date'] = pub_date
                    except:
                        article['published_date'] = None
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
        
        return articles
    
    def search_company_news(self, company_name: str, max_results: int = 5) -> List[Dict]:
        """Search for company-specific news"""
        articles = []
        try:
            # Create search query
            query = f"{company_name} site:{self.config['base_url'].replace('https://', '')}"
            logger.info(f"Searching for: {query}")
            
            # Use Google search for specific company news
            search_results = search(query, num_results=max_results, sleep_interval=2)
            
            for url in search_results:
                if self.config['base_url'] in url:
                    article_data = self.extract_article_content(url)
                    if article_data:
                        article_data['source'] = self.name
                        articles.append(article_data)
                        
        except Exception as e:
            logger.error(f"Error searching news for {company_name}: {e}")
        
        return articles
    
    def extract_article_content(self, url: str) -> Optional[Dict]:
        """Extract full article content from URL"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            return {
                'title': article.title,
                'content': article.text,
                'url': url,
                'published_date': article.publish_date,
                'authors': article.authors,
                'summary': article.summary if hasattr(article, 'summary') else '',
                'keywords': article.keywords if hasattr(article, 'keywords') else []
            }
        except Exception as e:
            logger.warning(f"Failed to extract content from {url}: {e}")
            return None

class EconomicTimesSource(NewsSource):
    """Economic Times specific scraper"""
    
    def get_latest_articles(self, limit: int = 20) -> List[Dict]:
        """Get latest articles from Economic Times"""
        articles = []
        
        # Get articles from RSS feeds
        for feed_url in self.config['rss_feeds']:
            feed_articles = self.parse_rss_feed(feed_url)
            articles.extend(feed_articles[:limit//len(self.config['rss_feeds'])])
        
        return articles

class BusinessStandardSource(NewsSource):
    """Business Standard specific scraper"""
    
    def get_latest_articles(self, limit: int = 20) -> List[Dict]:
        """Get latest articles from Business Standard"""
        articles = []
        
        # Get articles from RSS feeds
        for feed_url in self.config['rss_feeds']:
            feed_articles = self.parse_rss_feed(feed_url)
            articles.extend(feed_articles[:limit//len(self.config['rss_feeds'])])
        
        return articles

class MintSource(NewsSource):
    """Mint specific scraper"""
    
    def get_latest_articles(self, limit: int = 20) -> List[Dict]:
        """Get latest articles from Mint"""
        articles = []
        
        # Get articles from RSS feeds
        for feed_url in self.config['rss_feeds']:
            feed_articles = self.parse_rss_feed(feed_url)
            articles.extend(feed_articles[:limit//len(self.config['rss_feeds'])])
        
        return articles

class MoneyControlSource(NewsSource):
    """MoneyControl specific scraper"""
    
    def get_latest_articles(self, limit: int = 20) -> List[Dict]:
        """Get latest articles from MoneyControl"""
        articles = []
        
        # Get articles from RSS feeds
        for feed_url in self.config['rss_feeds']:
            feed_articles = self.parse_rss_feed(feed_url)
            articles.extend(feed_articles[:limit//len(self.config['rss_feeds'])])
        
        return articles

class NewsScraper:
    """Main news scraper coordinating multiple sources"""
    
    def __init__(self):
        self.sources = {
            'economic_times': EconomicTimesSource('Economic Times', NEWS_SOURCES['economic_times']),
            'business_standard': BusinessStandardSource('Business Standard', NEWS_SOURCES['business_standard']),
            'mint': MintSource('Mint', NEWS_SOURCES['mint']),
            'moneycontrol': MoneyControlSource('MoneyControl', NEWS_SOURCES['moneycontrol'])
        }
    
    def get_general_news(self, limit_per_source: int = 20) -> List[Dict]:
        """Get general business/market news from all sources"""
        all_articles = []
        
        for source_name, source in self.sources.items():
            try:
                logger.info(f"Fetching general news from {source_name}")
                articles = source.get_latest_articles(limit_per_source)
                all_articles.extend(articles)
                logger.info(f"Fetched {len(articles)} articles from {source_name}")
            except Exception as e:
                logger.error(f"Error fetching news from {source_name}: {e}")
        
        return all_articles
    
    def get_company_specific_news(self, companies: List[str], max_per_company: int = 5) -> Dict[str, List[Dict]]:
        """Get news for specific companies"""
        company_news = {}
        
        for company in companies:
            logger.info(f"Searching news for: {company}")
            company_articles = []
            
            for source_name, source in self.sources.items():
                try:
                    articles = source.search_company_news(company, max_per_company)
                    company_articles.extend(articles)
                except Exception as e:
                    logger.error(f"Error searching {company} news from {source_name}: {e}")
            
            # Remove duplicates based on title similarity
            unique_articles = self._remove_duplicate_articles(company_articles)
            company_news[company] = unique_articles[:max_per_company]
            
            logger.info(f"Found {len(company_news[company])} unique articles for {company}")
        
        return company_news
    
    def _remove_duplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        if not articles:
            return []
        
        unique_articles = []
        seen_titles = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if not title:
                continue
            
            is_duplicate = False
            for seen_title in seen_titles:
                # Calculate simple similarity
                similarity = len(set(title.split()) & set(seen_title.split())) / len(set(title.split()) | set(seen_title.split()))
                if similarity > 0.7:  # 70% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.append(title)
        
        return unique_articles
    
    def filter_recent_articles(self, articles: List[Dict], days_back: int = 7) -> List[Dict]:
        """Filter articles from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_articles = []
        
        for article in articles:
            pub_date = article.get('published_date')
            if pub_date and pub_date >= cutoff_date:
                recent_articles.append(article)
            elif not pub_date:
                # Include articles without date (might be recent)
                recent_articles.append(article)
        
        return recent_articles
    
    def enrich_articles_with_content(self, articles: List[Dict]) -> List[Dict]:
        """Download and parse full content for articles"""
        enriched_articles = []
        
        for article in articles:
            url = article.get('link') or article.get('url')
            if not url:
                continue
            
            # Try to get full content
            for source in self.sources.values():
                if source.config['base_url'] in url:
                    full_content = source.extract_article_content(url)
                    if full_content:
                        # Merge with existing data
                        article.update(full_content)
                        break
            
            enriched_articles.append(article)
        
        return enriched_articles

def main():
    """Test the scraper"""
    scraper = NewsScraper()
    
    # Test general news
    print("Fetching general news...")
    general_news = scraper.get_general_news(limit_per_source=5)
    print(f"Found {len(general_news)} articles")
    
    # Test company-specific news
    test_companies = ["Reliance Industries", "TCS", "HDFC Bank"]
    print(f"\nFetching news for companies: {test_companies}")
    company_news = scraper.get_company_specific_news(test_companies, max_per_company=3)
    
    for company, articles in company_news.items():
        print(f"\n{company}: {len(articles)} articles")
        for article in articles[:2]:  # Show first 2
            print(f"  - {article.get('title', 'No title')}")

if __name__ == "__main__":
    main()
