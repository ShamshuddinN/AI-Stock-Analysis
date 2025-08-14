#!/usr/bin/env python3
"""
Demo script showcasing NSE News Analysis System capabilities
"""
import sys
import time
from datetime import datetime
from utils import load_nse_companies
from analyzer import NewsAnalyzer

def demo_company_analysis():
    """Demo the analysis of sample news articles"""
    print("📰 Demo: News Analysis for Investment Insights")
    print("=" * 60)
    
    # Load companies data
    print("📊 Loading NSE companies database...")
    companies_df = load_nse_companies()
    print(f"   ✅ Loaded {len(companies_df)} NSE-listed companies")
    
    # Initialize analyzer
    print("\n🤖 Initializing AI-powered news analyzer...")
    analyzer = NewsAnalyzer()
    print("   ✅ Sentiment analysis engine ready")
    print("   ✅ Investment keyword database loaded")
    
    # Sample news articles for demo
    sample_articles = [
        {
            'title': 'Reliance Industries announces ₹75,000 crore investment in renewable energy projects',
            'content': 'Reliance Industries Limited has announced a massive investment of Rs 75,000 crores in renewable energy projects over the next 3 years. The company plans to set up solar manufacturing facilities and expand its green energy portfolio. This strategic move aligns with India\'s carbon neutrality goals and is expected to boost RIL\'s long-term growth prospects. Market analysts have upgraded their rating for the stock.',
            'source': 'Economic Times',
            'url': 'https://economictimes.indiatimes.com/sample1',
            'published_date': datetime.now()
        },
        {
            'title': 'TCS bags multi-billion dollar deal from major European bank',
            'content': 'Tata Consultancy Services has secured a $2.5 billion, 10-year contract from a leading European banking institution for digital transformation services. This deal includes cloud migration, AI implementation, and cybersecurity solutions. The contract is expected to contribute significantly to TCS revenue growth and strengthen its position in the European market.',
            'source': 'Business Standard',
            'url': 'https://business-standard.com/sample2',
            'published_date': datetime.now()
        },
        {
            'title': 'HDFC Bank reports strong quarterly results, beats estimates',
            'content': 'HDFC Bank has reported robust quarterly earnings with net profit growing 20% year-on-year. The bank\'s asset quality improved with reduced NPAs and strong deposit growth. Management expressed optimism about future outlook and announced plans for branch expansion. The results exceeded market expectations.',
            'source': 'Mint',
            'url': 'https://livemint.com/sample3',
            'published_date': datetime.now()
        },
        {
            'title': 'Adani Group faces scrutiny over debt levels amid regulatory concerns',
            'content': 'Adani Group companies are under increased scrutiny from regulators regarding their debt levels and corporate governance practices. Credit rating agencies have flagged concerns about the group\'s leverage ratios. The situation has led to volatility in Adani stock prices and raised questions about the sustainability of the group\'s aggressive expansion plans.',
            'source': 'MoneyControl',
            'url': 'https://moneycontrol.com/sample4',
            'published_date': datetime.now()
        }
    ]
    
    print(f"\n🔍 Analyzing {len(sample_articles)} sample news articles...")
    print("-" * 60)
    
    # Analyze each article
    analyzed_articles = []
    for i, article in enumerate(sample_articles, 1):
        print(f"\n📝 Article {i}: {article['title'][:60]}...")
        
        # Perform comprehensive analysis
        analysis = analyzer.analyze_article(article, companies_df)
        analyzed_articles.append(analysis)
        
        # Display key insights
        print(f"   🎯 Investment Score: {analysis.get('investment_score', 0):.3f}/1.000")
        print(f"   💭 Sentiment: {analysis.get('sentiment_label', 'N/A')} ({analysis.get('sentiment_score', 0):.2f})")
        print(f"   📈 Impact Category: {analysis.get('impact_category', 'N/A')}")
        
        # Show matched companies
        companies = analysis.get('matched_companies', [])
        if companies:
            company_symbols = [c['symbol'] for c in companies[:3]]
            print(f"   🏢 Companies: {', '.join(company_symbols)}")
        else:
            print("   🏢 Companies: None detected")
        
        # Show key investment keywords found
        keywords = analysis.get('keywords_found', {})
        all_keywords = []
        for category, kw_list in keywords.items():
            all_keywords.extend(kw_list[:2])  # Top 2 per category
        
        if all_keywords:
            print(f"   🔑 Key Terms: {', '.join(all_keywords[:4])}")
        
        time.sleep(0.5)  # Small delay for dramatic effect
    
    # Generate summary insights
    print("\n" + "=" * 60)
    print("📊 INVESTMENT INSIGHTS SUMMARY")
    print("=" * 60)
    
    summary = analyzer.generate_summary_insights(analyzed_articles)
    
    print(f"📰 Articles Analyzed: {summary.get('total_articles', 0)}")
    print(f"🎯 High-Relevance News: {summary.get('highly_relevant_articles', 0)}")
    print(f"📈 Average Investment Score: {summary.get('average_investment_score', 0):.3f}")
    print(f"💭 Average Sentiment: {summary.get('average_sentiment_score', 0):.3f}")
    
    # Sentiment breakdown
    sentiment_dist = summary.get('sentiment_distribution', {})
    print(f"\n🎨 Sentiment Distribution:")
    for sentiment, count in sentiment_dist.items():
        percentage = (count / summary.get('valid_articles', 1)) * 100
        print(f"   {sentiment}: {count} articles ({percentage:.1f}%)")
    
    # Top companies mentioned
    top_companies = summary.get('top_companies_mentioned', {})
    if top_companies:
        print(f"\n🏆 Most Mentioned Companies:")
        for company, mentions in list(top_companies.items())[:5]:
            print(f"   {company}: {mentions} mentions")
    
    # Investment recommendations based on analysis
    print(f"\n💡 INVESTMENT INSIGHTS:")
    
    # Rank articles by investment score
    relevant_articles = [a for a in analyzed_articles if a.get('investment_score', 0) > 0.5]
    relevant_articles.sort(key=lambda x: x.get('investment_score', 0), reverse=True)
    
    for i, article in enumerate(relevant_articles[:3], 1):
        companies = [c['symbol'] for c in article.get('matched_companies', [])][:2]
        print(f"\n   {i}. Investment Opportunity (Score: {article.get('investment_score', 0):.3f})")
        print(f"      Companies: {', '.join(companies) if companies else 'Market-wide'}")
        print(f"      Sentiment: {article.get('sentiment_label', 'N/A')}")
        print(f"      News: {article.get('title', 'No title')[:70]}...")
    
    print(f"\n🎯 SYSTEM CAPABILITIES DEMONSTRATED:")
    print("   ✅ Multi-source news analysis")
    print("   ✅ AI-powered sentiment analysis")
    print("   ✅ Company name matching & recognition")
    print("   ✅ Investment-focused keyword extraction")
    print("   ✅ Quantitative investment scoring")
    print("   ✅ Structured insights generation")
    
    print(f"\n📝 Note: This demo uses sample articles. The full system can:")
    print("   • Scrape real-time news from multiple sources")
    print("   • Analyze 100+ articles automatically")
    print("   • Track 2000+ NSE-listed companies")
    print("   • Provide interactive dashboard visualization")
    print("   • Generate detailed investment reports")
    
    return analyzed_articles, summary

def show_next_steps():
    """Show next steps for using the system"""
    print("\n" + "🚀 NEXT STEPS" + "")
    print("=" * 60)
    print("1. 🔄 Full Analysis:")
    print("   python main.py --mode full")
    print("   → Scrapes latest news from multiple sources")
    print("   → Analyzes top 50 NSE companies")
    print("   → Generates comprehensive investment report")
    
    print("\n2. 📊 Interactive Dashboard:")
    print("   python main.py --mode dashboard")
    print("   → Opens web interface at http://localhost:8050")
    print("   → Real-time charts and filtering")
    print("   → Company-wise analysis")
    
    print("\n3. 🎯 Targeted Company Analysis:")
    print("   python main.py --mode companies --companies RELIANCE TCS HDFCBANK")
    print("   → Analyzes specific companies of interest")
    print("   → Perfect for portfolio monitoring")
    
    print("\n4. 📈 Advanced Usage:")
    print("   • Schedule daily analysis with cron jobs")
    print("   • Export results to CSV/Excel")
    print("   • Integrate with trading platforms")
    print("   • Set up email alerts for high-impact news")

def main():
    """Main demo function"""
    print(f"\n🏦 NSE Companies News Analysis System - LIVE DEMO")
    print(f"⏰ Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run the demo analysis
        articles, summary = demo_company_analysis()
        
        # Show next steps
        show_next_steps()
        
        print(f"\n✨ Demo completed successfully!")
        print(f"🎉 Ready to analyze real market data for investment insights!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        print("💡 Try running: python test_system.py first")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
