"""
News analyzer for sentiment analysis and investment relevance scoring
"""
import logging
import re
import nltk
from textblob import TextBlob
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import numpy as np
from collections import Counter

from config import INVESTMENT_KEYWORDS, ANALYSIS_CONFIG
from utils import (
    extract_numbers_from_text, 
    categorize_news_impact, 
    calculate_investment_score,
    extract_company_variants,
    calculate_text_similarity
)

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class NewsAnalyzer:
    """Analyze news articles for investment insights"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.investment_keywords = INVESTMENT_KEYWORDS
        
        # Add more investment-specific terms
        self.investment_keywords['positive'].extend([
            'breakthrough', 'milestone', 'success', 'achievement', 'win',
            'record', 'strong performance', 'beat expectations', 'exceed',
            'surge', 'rally', 'boost', 'positive outlook', 'optimistic',
            'upgrade', 'recommend', 'target price', 'bull', 'momentum'
        ])
        
        self.investment_keywords['negative'].extend([
            'bear', 'pessimistic', 'concern', 'worry', 'risk', 'threat',
            'challenge', 'struggle', 'disappointing', 'miss estimates',
            'cut', 'reduce', 'lower', 'below expectations', 'uncertainty'
        ])
    
    def analyze_article(self, article: Dict, companies_df=None) -> Dict:
        """Comprehensive analysis of a single article"""
        analysis = {
            'article_id': article.get('url', article.get('link', '')),
            'title': article.get('title', ''),
            'source': article.get('source', ''),
            'published_date': article.get('published_date'),
            'url': article.get('url', article.get('link', '')),
        }
        
        # Get text content
        content = self._extract_text_content(article)
        if not content or len(content) < ANALYSIS_CONFIG['min_article_length']:
            analysis['error'] = 'Insufficient content'
            return analysis
        
        analysis['content_length'] = len(content)
        
        # Sentiment analysis
        sentiment_result = self.analyze_sentiment(content)
        analysis.update(sentiment_result)
        
        # Keyword analysis
        keywords_result = self.extract_investment_keywords(content)
        analysis.update(keywords_result)
        
        # Company matching
        if companies_df is not None:
            companies_result = self.match_companies(content, companies_df)
            analysis.update(companies_result)
        
        # Financial information extraction
        financial_result = self.extract_financial_info(content)
        analysis.update(financial_result)
        
        # Investment impact scoring
        analysis['investment_score'] = calculate_investment_score(analysis)
        analysis['impact_category'] = categorize_news_impact(
            analysis.get('keywords_found', {}), 
            analysis.get('sentiment_score', 0)
        )
        
        # Relevance scoring
        analysis['relevance_score'] = self._calculate_relevance_score(analysis)
        
        return analysis
    
    def _extract_text_content(self, article: Dict) -> str:
        """Extract and clean text content from article"""
        content_fields = ['content', 'description', 'summary', 'title']
        content_parts = []
        
        for field in content_fields:
            if field in article and article[field]:
                content_parts.append(str(article[field]))
        
        return ' '.join(content_parts).strip()
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            
            # Overall sentiment
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Sentence-level sentiment for more nuanced analysis
            sentences = sent_tokenize(text)
            sentence_sentiments = []
            
            for sentence in sentences:
                if len(sentence.split()) > 3:  # Skip very short sentences
                    sent_blob = TextBlob(sentence)
                    sentence_sentiments.append(sent_blob.sentiment.polarity)
            
            # Calculate additional metrics
            positive_sentences = len([s for s in sentence_sentiments if s > 0.1])
            negative_sentences = len([s for s in sentence_sentiments if s < -0.1])
            neutral_sentences = len(sentence_sentiments) - positive_sentences - negative_sentences
            
            return {
                'sentiment_score': polarity,
                'sentiment_subjectivity': subjectivity,
                'sentiment_label': self._get_sentiment_label(polarity),
                'positive_sentences': positive_sentences,
                'negative_sentences': negative_sentences,
                'neutral_sentences': neutral_sentences,
                'sentence_sentiments': sentence_sentiments
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_subjectivity': 0.0,
                'sentiment_label': 'Neutral',
                'error': str(e)
            }
    
    def _get_sentiment_label(self, polarity: float) -> str:
        """Convert polarity score to label"""
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    
    def extract_investment_keywords(self, text: str) -> Dict:
        """Extract and categorize investment-relevant keywords"""
        text_lower = text.lower()
        keywords_found = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        for category, keywords in self.investment_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    keywords_found[category].append(keyword)
        
        # Remove duplicates
        for category in keywords_found:
            keywords_found[category] = list(set(keywords_found[category]))
        
        # Calculate keyword density
        total_words = len(text.split())
        total_keywords = sum(len(kw_list) for kw_list in keywords_found.values())
        keyword_density = total_keywords / total_words if total_words > 0 else 0
        
        return {
            'keywords_found': keywords_found,
            'keyword_density': keyword_density,
            'total_investment_keywords': total_keywords
        }
    
    def match_companies(self, text: str, companies_df) -> Dict:
        """Match companies mentioned in the text"""
        matched_companies = []
        text_lower = text.lower()
        
        for _, row in companies_df.iterrows():
            company_name = row.get('company_name', '')
            symbol = row.get('symbol', '')
            
            if not company_name:
                continue
            
            # Generate name variants
            variants = extract_company_variants(company_name)
            if symbol:
                variants.append(symbol)
            
            # Check for matches
            for variant in variants:
                if len(variant) > 2 and variant.lower() in text_lower:
                    # Calculate confidence based on context
                    confidence = self._calculate_match_confidence(text, variant, company_name)
                    
                    if confidence > 0.3:  # Threshold for inclusion
                        matched_companies.append({
                            'symbol': symbol,
                            'company_name': company_name,
                            'matched_variant': variant,
                            'confidence': confidence
                        })
                        break  # Avoid multiple matches for same company
        
        # Remove duplicates and sort by confidence
        unique_companies = {}
        for company in matched_companies:
            symbol = company['symbol']
            if symbol not in unique_companies or company['confidence'] > unique_companies[symbol]['confidence']:
                unique_companies[symbol] = company
        
        sorted_companies = sorted(unique_companies.values(), key=lambda x: x['confidence'], reverse=True)
        
        return {
            'matched_companies': sorted_companies[:5],  # Top 5 matches
            'company_count': len(sorted_companies)
        }
    
    def _calculate_match_confidence(self, text: str, variant: str, full_name: str) -> float:
        """Calculate confidence score for company name matching"""
        text_lower = text.lower()
        variant_lower = variant.lower()
        
        confidence = 0.0
        
        # Base confidence for exact match
        if variant_lower in text_lower:
            confidence += 0.4
        
        # Boost if full company name is mentioned
        if full_name.lower() in text_lower:
            confidence += 0.3
        
        # Boost for context words
        context_words = ['company', 'limited', 'ltd', 'corporation', 'inc', 'announces', 'reports']
        words_around_match = self._get_words_around_match(text_lower, variant_lower, window=10)
        
        for word in context_words:
            if word in words_around_match:
                confidence += 0.1
        
        # Penalty for very common words that might cause false matches
        common_words = ['the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
        if variant_lower in common_words:
            confidence -= 0.5
        
        return min(confidence, 1.0)
    
    def _get_words_around_match(self, text: str, match: str, window: int = 10) -> List[str]:
        """Get words around a match for context analysis"""
        words = text.split()
        match_positions = []
        
        for i, word in enumerate(words):
            if match in word:
                match_positions.append(i)
        
        context_words = []
        for pos in match_positions:
            start = max(0, pos - window)
            end = min(len(words), pos + window + 1)
            context_words.extend(words[start:end])
        
        return context_words
    
    def extract_financial_info(self, text: str) -> Dict:
        """Extract financial information from text"""
        numbers = extract_numbers_from_text(text)
        
        # Extract percentage changes
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)'
        percentages = re.findall(percentage_pattern, text, re.IGNORECASE)
        percentages = [float(p) for p in percentages]
        
        # Extract financial metrics keywords
        financial_terms = [
            'revenue', 'profit', 'loss', 'earnings', 'ebitda', 'dividend',
            'market cap', 'valuation', 'investment', 'funding', 'debt',
            'cash flow', 'assets', 'liabilities', 'equity', 'roe', 'roa',
            'pe ratio', 'eps', 'book value', 'sales', 'growth'
        ]
        
        financial_mentions = []
        text_lower = text.lower()
        for term in financial_terms:
            if term in text_lower:
                financial_mentions.append(term)
        
        return {
            'financial_numbers': numbers,
            'percentages_mentioned': percentages,
            'financial_terms': financial_mentions,
            'financial_density': len(financial_mentions) / len(text.split()) if text else 0
        }
    
    def _calculate_relevance_score(self, analysis: Dict) -> float:
        """Calculate overall relevance score for investment decisions"""
        score = 0.0
        
        # Investment keywords weight (30%)
        keyword_score = min(analysis.get('total_investment_keywords', 0) * 0.05, 0.3)
        score += keyword_score
        
        # Sentiment strength (25%)
        sentiment_strength = abs(analysis.get('sentiment_score', 0)) * 0.25
        score += sentiment_strength
        
        # Company mentions (20%)
        company_score = min(analysis.get('company_count', 0) * 0.1, 0.2)
        score += company_score
        
        # Financial information (15%)
        financial_score = analysis.get('financial_density', 0) * 0.15
        score += financial_score
        
        # Content quality (10%)
        content_length = analysis.get('content_length', 0)
        quality_score = min(content_length / 1000, 1.0) * 0.1  # Normalize by 1000 chars
        score += quality_score
        
        return min(score, 1.0)
    
    def batch_analyze_articles(self, articles: List[Dict], companies_df=None) -> List[Dict]:
        """Analyze multiple articles in batch"""
        analyzed_articles = []
        
        for i, article in enumerate(articles):
            try:
                logger.info(f"Analyzing article {i+1}/{len(articles)}: {article.get('title', 'No title')[:50]}...")
                analysis = self.analyze_article(article, companies_df)
                analyzed_articles.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing article {i+1}: {e}")
                # Add basic error info
                analyzed_articles.append({
                    'article_id': article.get('url', article.get('link', f'article_{i}')),
                    'error': str(e),
                    'title': article.get('title', ''),
                    'source': article.get('source', '')
                })
        
        return analyzed_articles
    
    def filter_relevant_articles(self, analyzed_articles: List[Dict], 
                                min_relevance: float = None) -> List[Dict]:
        """Filter articles based on relevance score"""
        if min_relevance is None:
            min_relevance = ANALYSIS_CONFIG['relevance_threshold']
        
        relevant_articles = []
        for article in analyzed_articles:
            if article.get('relevance_score', 0) >= min_relevance:
                relevant_articles.append(article)
        
        # Sort by relevance score (descending)
        relevant_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_articles
    
    def generate_summary_insights(self, analyzed_articles: List[Dict]) -> Dict:
        """Generate summary insights from analyzed articles"""
        if not analyzed_articles:
            return {'error': 'No articles to analyze'}
        
        # Filter out articles with errors
        valid_articles = [a for a in analyzed_articles if 'error' not in a]
        
        if not valid_articles:
            return {'error': 'No valid articles found'}
        
        # Overall sentiment distribution
        sentiment_labels = [a.get('sentiment_label', 'Neutral') for a in valid_articles]
        sentiment_dist = dict(Counter(sentiment_labels))
        
        # Impact categories
        impact_categories = [a.get('impact_category', 'Neutral') for a in valid_articles]
        impact_dist = dict(Counter(impact_categories))
        
        # Top companies mentioned
        all_companies = []
        for article in valid_articles:
            companies = article.get('matched_companies', [])
            all_companies.extend([c['symbol'] for c in companies])
        
        top_companies = dict(Counter(all_companies).most_common(10))
        
        # Average scores
        avg_sentiment = np.mean([a.get('sentiment_score', 0) for a in valid_articles])
        avg_relevance = np.mean([a.get('relevance_score', 0) for a in valid_articles])
        avg_investment = np.mean([a.get('investment_score', 0) for a in valid_articles])
        
        # Most common keywords
        all_keywords = []
        for article in valid_articles:
            keywords = article.get('keywords_found', {})
            for category, kw_list in keywords.items():
                all_keywords.extend([(kw, category) for kw in kw_list])
        
        keyword_freq = Counter(all_keywords)
        top_keywords = keyword_freq.most_common(15)
        
        return {
            'total_articles': len(analyzed_articles),
            'valid_articles': len(valid_articles),
            'sentiment_distribution': sentiment_dist,
            'impact_distribution': impact_dist,
            'top_companies_mentioned': top_companies,
            'average_sentiment_score': round(avg_sentiment, 3),
            'average_relevance_score': round(avg_relevance, 3),
            'average_investment_score': round(avg_investment, 3),
            'top_keywords': top_keywords,
            'highly_relevant_articles': len([a for a in valid_articles if a.get('relevance_score', 0) > 0.6])
        }

def main():
    """Test the analyzer"""
    # Sample article for testing
    sample_article = {
        'title': 'Reliance Industries announces major investment in renewable energy sector',
        'content': 'Reliance Industries Limited has announced a significant investment of Rs 75,000 crores in renewable energy projects. The company plans to expand its green energy portfolio with new solar and wind projects. This move is expected to boost the company\'s growth prospects and align with India\'s carbon neutrality goals. Market experts have upgraded their rating for RIL stock.',
        'source': 'Economic Times',
        'url': 'https://example.com/test-article'
    }
    
    analyzer = NewsAnalyzer()
    result = analyzer.analyze_article(sample_article)
    
    print("Analysis Result:")
    for key, value in result.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
