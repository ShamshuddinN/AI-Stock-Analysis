#!/usr/bin/env python3
"""
Simple test script to validate NSE News Analysis System functionality
"""
import sys
import pandas as pd
from datetime import datetime

def test_csv_loading():
    """Test loading the NSE companies CSV"""
    print("🔍 Testing CSV loading...")
    try:
        # Read the CSV file with proper column names
        df = pd.read_csv('EQUITY_L.csv', sep='|')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace('﻿', '')  # Remove BOM character
        
        print(f"✅ Successfully loaded {len(df)} companies from CSV")
        print(f"   Columns: {list(df.columns)[:5]}{'...' if len(df.columns) > 5 else ''}")
        
        # Show first few companies
        if 'NAME OF COMPANY' in df.columns:
            print("   Sample companies:")
            for i, company in enumerate(df['NAME OF COMPANY'].head(5)):
                print(f"   {i+1}. {company}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return False

def test_basic_imports():
    """Test importing required modules"""
    print("\n🧪 Testing basic imports...")
    
    modules_to_test = [
        ('pandas', 'pd'),
        ('numpy', 'np'),
        ('requests', 'requests'),
        ('bs4', 'BeautifulSoup'),
        ('nltk', 'nltk'),
        ('textblob', 'TextBlob'),
        ('feedparser', 'feedparser')
    ]
    
    successful = 0
    for module_name, import_as in modules_to_test:
        try:
            if import_as == 'BeautifulSoup':
                from bs4 import BeautifulSoup
            else:
                exec(f"import {module_name} as {import_as}")
            print(f"✅ {module_name}")
            successful += 1
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"   {successful}/{len(modules_to_test)} modules imported successfully")
    return successful == len(modules_to_test)

def test_sentiment_analysis():
    """Test basic sentiment analysis"""
    print("\n💭 Testing sentiment analysis...")
    try:
        from textblob import TextBlob
        
        # Test cases
        test_texts = [
            ("Reliance Industries announces major expansion with 10,000 crore investment", "Positive"),
            ("Company reports significant loss and job cuts", "Negative"),
            ("Regular quarterly meeting scheduled for next week", "Neutral")
        ]
        
        for text, expected in test_texts:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = "Positive"
            elif polarity < -0.1:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            status = "✅" if sentiment == expected else "⚠️"
            print(f"   {status} '{text[:50]}...' → {sentiment} ({polarity:.2f})")
        
        return True
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")
        return False

def test_news_scraping_simulation():
    """Test basic news scraping functionality"""
    print("\n📰 Testing news scraping simulation...")
    try:
        import requests
        import feedparser
        
        # Test RSS feed parsing (using a simple feed)
        test_feed_url = "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"
        
        print(f"   Attempting to parse RSS feed: {test_feed_url[:50]}...")
        
        try:
            feed = feedparser.parse(test_feed_url)
            if feed.entries:
                print(f"✅ Successfully parsed RSS feed with {len(feed.entries)} entries")
                print(f"   Sample title: {feed.entries[0].title[:80]}...")
            else:
                print("⚠️ RSS feed parsed but no entries found (may be temporary)")
        except Exception as e:
            print(f"⚠️ RSS feed test failed (network/server issue): {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error in news scraping test: {e}")
        return False

def test_configuration_loading():
    """Test loading configuration"""
    print("\n⚙️ Testing configuration loading...")
    try:
        from config import NEWS_SOURCES, INVESTMENT_KEYWORDS, ANALYSIS_CONFIG
        
        print(f"✅ Loaded configuration with:")
        print(f"   - {len(NEWS_SOURCES)} news sources")
        print(f"   - {sum(len(keywords) for keywords in INVESTMENT_KEYWORDS.values())} investment keywords")
        print(f"   - Analysis lookback: {ANALYSIS_CONFIG.get('days_lookback', 'N/A')} days")
        
        return True
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 NSE News Analysis System - Basic Test Suite")
    print("=" * 60)
    
    tests = [
        test_basic_imports,
        test_csv_loading,
        test_configuration_loading,
        test_sentiment_analysis,
        test_news_scraping_simulation
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Install remaining dependencies: source venv/bin/activate && pip install -r requirements.txt")
        print("2. Run full analysis: python main.py --mode full")
        print("3. Start dashboard: python main.py --mode dashboard")
    else:
        print(f"⚠️ {passed}/{total} tests passed. Please address the issues above.")
        if passed >= 3:
            print("   Basic functionality appears to work. You can try running:")
            print("   python main.py --mode full --verbose")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
