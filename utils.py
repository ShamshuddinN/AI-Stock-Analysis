"""
Utility functions for the NSE News Scraper
"""
import logging
import pandas as pd
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import random
from fake_useragent import UserAgent
from config import LOGGING_CONFIG, NSE_COMPANIES_FILE

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file']),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def load_nse_companies() -> pd.DataFrame:
    """Load NSE companies from CSV file"""
    try:
        # Read the CSV file normally - it's a standard CSV
        df = pd.read_csv(NSE_COMPANIES_FILE)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Rename columns for easier access
        column_mapping = {
            'SYMBOL': 'symbol',
            'NAME OF COMPANY': 'company_name',
            'SERIES': 'series',
            'DATE OF LISTING': 'listing_date',
            'PAID UP VALUE': 'paid_up_value',
            'MARKET LOT': 'market_lot',
            'ISIN NUMBER': 'isin',
            'FACE VALUE': 'face_value'
        }
        
        # Only rename columns that exist
        existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=existing_columns)
        
        # Clean and standardize data if we have data
        if not df.empty:
            if 'company_name' in df.columns:
                df['company_name'] = df['company_name'].str.strip()
                df['company_name_clean'] = df['company_name'].apply(clean_company_name)
            
            if 'symbol' in df.columns:
                df['symbol'] = df['symbol'].str.strip().str.upper()
                # Remove empty rows
                df = df[df['symbol'].str.len() > 0]
        
        logger = logging.getLogger(__name__)
        logger.info(f"Loaded {len(df)} NSE companies")
        return df
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading NSE companies: {e}")
        return pd.DataFrame()

def clean_company_name(name: str) -> str:
    """Clean company name for better matching"""
    if pd.isna(name):
        return ""
    
    # Remove common suffixes and prefixes
    suffixes_to_remove = [
        ' limited', ' ltd', ' ltd.', ' corporation', ' corp', ' corp.',
        ' company', ' co', ' co.', ' inc', ' inc.', ' llc',
        ' private limited', ' pvt ltd', ' pvt. ltd.',
        ' public limited', ' plc'
    ]
    
    name_clean = name.lower()
    for suffix in suffixes_to_remove:
        name_clean = name_clean.replace(suffix, '')
    
    # Remove special characters and extra spaces
    name_clean = re.sub(r'[^\w\s]', ' ', name_clean)
    name_clean = re.sub(r'\s+', ' ', name_clean).strip()
    
    return name_clean

def extract_company_variants(company_name: str) -> List[str]:
    """Generate various name variants for better matching"""
    variants = [company_name]
    
    # Add cleaned version
    clean_name = clean_company_name(company_name)
    if clean_name and clean_name != company_name.lower():
        variants.append(clean_name)
    
    # Add acronym if applicable
    words = clean_name.split()
    if len(words) > 1:
        acronym = ''.join([word[0].upper() for word in words if word])
        if len(acronym) > 1:
            variants.append(acronym)
    
    # Add partial matches (first 2-3 significant words)
    if len(words) >= 2:
        partial = ' '.join(words[:min(3, len(words))])
        variants.append(partial)
    
    return list(set(variants))

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts"""
    if not text1 or not text2:
        return 0.0
    
    text1_words = set(text1.lower().split())
    text2_words = set(text2.lower().split())
    
    intersection = len(text1_words.intersection(text2_words))
    union = len(text1_words.union(text2_words))
    
    return intersection / union if union > 0 else 0.0

def is_business_hours() -> bool:
    """Check if current time is within business hours (9 AM - 6 PM IST)"""
    now = datetime.now()
    return 9 <= now.hour <= 18

def get_random_delay() -> float:
    """Get random delay between requests to avoid being blocked"""
    base_delay = 1.0 if is_business_hours() else 0.5
    return base_delay + random.uniform(0, 1)

def get_random_user_agent() -> str:
    """Get a random user agent string"""
    try:
        ua = UserAgent()
        return ua.random
    except:
        # Fallback user agents
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(agents)

def normalize_date(date_str: str) -> Optional[datetime]:
    """Normalize various date formats to datetime object"""
    if not date_str:
        return None
    
    # Common date formats
    formats = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None

def extract_numbers_from_text(text: str) -> List[float]:
    """Extract numerical values from text"""
    # Pattern to match numbers with units (crores, lakhs, etc.)
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:crores?|cr\.?)',
        r'(\d+(?:\.\d+)?)\s*(?:lakhs?|lakh)',
        r'(\d+(?:\.\d+)?)\s*(?:thousands?|k)',
        r'(\d+(?:\.\d+)?)\s*(?:millions?|mn\.?)',
        r'(\d+(?:\.\d+)?)\s*(?:billions?|bn\.?)',
        r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)',
    ]
    
    numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Remove commas and convert to float
                num = float(match.replace(',', ''))
                numbers.append(num)
            except ValueError:
                continue
    
    return numbers

def categorize_news_impact(keywords_found: Dict[str, List[str]], sentiment_score: float) -> str:
    """Categorize news impact based on keywords and sentiment"""
    positive_count = len(keywords_found.get('positive', []))
    negative_count = len(keywords_found.get('negative', []))
    
    if positive_count > negative_count and sentiment_score > 0.1:
        return 'Highly Positive'
    elif positive_count > 0 and sentiment_score > 0.05:
        return 'Positive'
    elif negative_count > positive_count and sentiment_score < -0.1:
        return 'Highly Negative'
    elif negative_count > 0 and sentiment_score < -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def calculate_investment_score(article_data: Dict) -> float:
    """Calculate investment relevance score based on various factors"""
    score = 0.0
    
    # Sentiment contribution (40% weight)
    sentiment = article_data.get('sentiment_score', 0)
    sentiment_weight = abs(sentiment) * 0.4
    score += sentiment_weight
    
    # Keywords contribution (30% weight)
    keywords = article_data.get('keywords_found', {})
    keyword_score = 0
    for category, words in keywords.items():
        if category == 'positive':
            keyword_score += len(words) * 0.1
        elif category == 'negative':
            keyword_score += len(words) * 0.1
        else:  # neutral
            keyword_score += len(words) * 0.05
    
    score += min(keyword_score, 0.3)  # Cap at 30%
    
    # Recency contribution (20% weight)
    pub_date = article_data.get('published_date')
    if pub_date:
        days_old = (datetime.now() - pub_date).days
        recency_score = max(0, (7 - days_old) / 7) * 0.2
        score += recency_score
    
    # Source credibility (10% weight)
    source = article_data.get('source', '').lower()
    credible_sources = ['economic times', 'business standard', 'mint', 'moneycontrol']
    if any(cs in source for cs in credible_sources):
        score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0

def save_to_json(data: Dict, filename: str) -> None:
    """Save data to JSON file with proper datetime serialization"""
    import json
    from pathlib import Path
    
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)

def load_from_json(filename: str) -> Dict:
    """Load data from JSON file"""
    import json
    from pathlib import Path
    
    filepath = Path(filename)
    if not filepath.exists():
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error loading JSON file {filename}: {e}")
        return {}

# Initialize logging
logger = setup_logging()
