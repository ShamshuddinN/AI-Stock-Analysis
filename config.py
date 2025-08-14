"""
Configuration settings for NSE News Scraper
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'
LOGS_DIR = BASE_DIR / 'logs'

# Create directories if they don't exist
for dir_path in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Input files
NSE_COMPANIES_FILE = BASE_DIR / 'EQUITY_L.csv'

# News sources configuration
NEWS_SOURCES = {
    'economic_times': {
        'base_url': 'https://economictimes.indiatimes.com',
        'search_url': 'https://economictimes.indiatimes.com/markets/stocks/news',
        'rss_feeds': [
            'https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms',
            'https://economictimes.indiatimes.com/news/company/corporate-trends/rssfeeds/13358266.cms'
        ]
    },
    'business_standard': {
        'base_url': 'https://www.business-standard.com',
        'search_url': 'https://www.business-standard.com/markets/news',
        'rss_feeds': [
            'https://www.business-standard.com/rss/markets-106.rss',
            'https://www.business-standard.com/rss/companies-101.rss'
        ]
    },
    'mint': {
        'base_url': 'https://www.livemint.com',
        'search_url': 'https://www.livemint.com/market',
        'rss_feeds': [
            'https://www.livemint.com/rss/markets',
            'https://www.livemint.com/rss/companies'
        ]
    },
    'moneycontrol': {
        'base_url': 'https://www.moneycontrol.com',
        'search_url': 'https://www.moneycontrol.com/news/business/',
        'rss_feeds': [
            'https://www.moneycontrol.com/rss/business.xml',
            'https://www.moneycontrol.com/rss/results.xml'
        ]
    }
}

# Investment-relevant keywords for filtering news
INVESTMENT_KEYWORDS = {
    'positive': [
        'new project', 'expansion', 'investment', 'acquisition', 'merger',
        'contract', 'order', 'partnership', 'launch', 'growth', 'profit',
        'revenue increase', 'earnings beat', 'dividend', 'buyback',
        'capacity expansion', 'new facility', 'joint venture', 'collaboration',
        'funding', 'ipo', 'listing', 'upgraded', 'outperform', 'buy rating',
        'tie-up', 'agreement', 'approval', 'license', 'patent', 'innovation',
        'technology', 'digital transformation', 'renewable energy', 'green',
        'sustainable', 'export', 'international expansion'
    ],
    'negative': [
        'loss', 'decline', 'fall', 'drop', 'downgrade', 'sell rating',
        'bankruptcy', 'debt', 'lawsuit', 'fine', 'penalty', 'investigation',
        'scandal', 'fraud', 'closure', 'layoff', 'restructuring', 'warning',
        'miss', 'disappointing', 'weak', 'poor performance', 'regulatory action',
        'suspension', 'delisting', 'default', 'impairment', 'write-off'
    ],
    'neutral': [
        'announcement', 'statement', 'results', 'quarterly', 'annual',
        'meeting', 'conference', 'presentation', 'update', 'report',
        'guidance', 'outlook', 'forecast', 'management change', 'appointment'
    ]
}

# Scraping settings
SCRAPING_CONFIG = {
    'delay_between_requests': 2,  # seconds
    'max_retries': 3,
    'timeout': 30,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
}

# Analysis settings
ANALYSIS_CONFIG = {
    'sentiment_threshold': 0.1,  # Threshold for neutral sentiment
    'relevance_threshold': 0.3,  # Threshold for news relevance
    'days_lookback': 7,  # Number of days to look back for news
    'min_article_length': 100,  # Minimum article length in characters
    'max_articles_per_company': 10  # Maximum articles to process per company
}

# Dashboard settings
DASHBOARD_CONFIG = {
    'port': 8050,
    'debug': True,
    'host': '127.0.0.1',
    'refresh_interval': 300  # seconds
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOGS_DIR / 'news_scraper.log'
}
