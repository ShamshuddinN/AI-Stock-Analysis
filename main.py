"""
Main orchestration script for NSE News Analysis System
"""
import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import time

from config import OUTPUT_DIR, ANALYSIS_CONFIG
from utils import (
    setup_logging, 
    load_nse_companies, 
    save_to_json, 
    load_from_json
)
from scraper import NewsScraper
from analyzer import NewsAnalyzer
from dashboard import NewsDashboard

logger = logging.getLogger(__name__)

class NSENewsAnalysisSystem:
    """Main orchestration class for the NSE news analysis system"""
    
    def __init__(self):
        self.companies_df = None
        self.scraper = None
        self.analyzer = None
        self.dashboard = None
    
    def initialize(self):
        """Initialize all components"""
        logger.info("Initializing NSE News Analysis System...")
        
        # Load NSE companies data
        self.companies_df = load_nse_companies()
        if self.companies_df.empty:
            logger.error("Failed to load NSE companies data!")
            sys.exit(1)
        
        logger.info(f"Loaded {len(self.companies_df)} NSE companies")
        
        # Initialize components
        self.scraper = NewsScraper()
        self.analyzer = NewsAnalyzer()
        self.dashboard = NewsDashboard()
        
        logger.info("System initialization completed successfully")
    
    def run_full_analysis(self, 
                         top_companies: int = 50, 
                         general_news_limit: int = 100,
                         company_news_limit: int = 5) -> Dict:
        """Run complete news analysis pipeline"""
        logger.info("Starting full news analysis pipeline...")
        start_time = time.time()
        
        try:
            # Step 1: Scrape general business news
            logger.info("Step 1: Scraping general business news...")
            general_articles = self.scraper.get_general_news(
                limit_per_source=general_news_limit // 4
            )
            logger.info(f"Scraped {len(general_articles)} general articles")
            
            # Step 2: Filter recent articles
            logger.info("Step 2: Filtering recent articles...")
            recent_articles = self.scraper.filter_recent_articles(
                general_articles, 
                days_back=ANALYSIS_CONFIG['days_lookback']
            )
            logger.info(f"Found {len(recent_articles)} recent articles")
            
            # Step 3: Get company-specific news for top companies
            logger.info("Step 3: Fetching company-specific news...")
            top_company_names = self.get_top_companies(top_companies)
            company_articles_dict = self.scraper.get_company_specific_news(
                top_company_names[:20],  # Limit to avoid rate limiting
                max_per_company=company_news_limit
            )
            
            # Flatten company articles
            company_articles = []
            for company, articles in company_articles_dict.items():
                company_articles.extend(articles)
            
            logger.info(f"Scraped {len(company_articles)} company-specific articles")
            
            # Step 4: Combine and deduplicate articles
            all_articles = recent_articles + company_articles
            unique_articles = self.scraper._remove_duplicate_articles(all_articles)
            logger.info(f"Combined to {len(unique_articles)} unique articles")
            
            # Step 5: Enrich articles with full content (sample for performance)
            logger.info("Step 5: Enriching articles with full content...")
            sample_size = min(50, len(unique_articles))  # Limit for performance
            sample_articles = unique_articles[:sample_size]
            enriched_articles = self.scraper.enrich_articles_with_content(sample_articles)
            
            # Use remaining articles without full content enrichment
            remaining_articles = unique_articles[sample_size:]
            final_articles = enriched_articles + remaining_articles
            
            logger.info(f"Enriched {len(enriched_articles)} articles with full content")
            
            # Step 6: Analyze all articles
            logger.info("Step 6: Analyzing articles for sentiment and investment insights...")
            analyzed_articles = self.analyzer.batch_analyze_articles(
                final_articles, 
                self.companies_df
            )
            logger.info(f"Analyzed {len(analyzed_articles)} articles")
            
            # Step 7: Filter relevant articles
            logger.info("Step 7: Filtering relevant articles...")
            relevant_articles = self.analyzer.filter_relevant_articles(analyzed_articles)
            logger.info(f"Found {len(relevant_articles)} relevant articles")
            
            # Step 8: Generate summary insights
            logger.info("Step 8: Generating summary insights...")
            summary_insights = self.analyzer.generate_summary_insights(analyzed_articles)
            
            # Step 9: Compile final results
            results = {
                'timestamp': datetime.now().isoformat(),
                'execution_time_seconds': round(time.time() - start_time, 2),
                'total_articles_scraped': len(all_articles),
                'unique_articles': len(unique_articles),
                'analyzed_articles': len(analyzed_articles),
                'relevant_articles': len(relevant_articles),
                'articles': analyzed_articles,
                'relevant_articles_only': relevant_articles,
                'summary': summary_insights,
                'top_companies_analyzed': top_company_names[:20]
            }
            
            logger.info(f"Full analysis completed in {results['execution_time_seconds']} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Error in full analysis pipeline: {e}", exc_info=True)
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'articles': [],
                'summary': {}
            }
    
    def get_top_companies(self, limit: int = 50) -> List[str]:
        """Get list of top NSE companies by market cap or other criteria"""
        if self.companies_df.empty:
            return []
        
        # For now, just return the first N companies
        # In a production system, you might want to sort by market cap or other criteria
        top_companies = self.companies_df.head(limit)['company_name'].tolist()
        return [name for name in top_companies if name and len(name.strip()) > 0]
    
    def save_results(self, results: Dict, filename: str = None):
        """Save analysis results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nse_news_analysis_{timestamp}.json"
        
        filepath = OUTPUT_DIR / filename
        save_to_json(results, filepath)
        
        # Also save as latest analysis for dashboard
        latest_filepath = OUTPUT_DIR / "latest_analysis.json"
        save_to_json(results, latest_filepath)
        
        logger.info(f"Results saved to {filepath}")
        return filepath
    
    def run_analysis_for_companies(self, company_symbols: List[str], 
                                 max_articles_per_company: int = 10) -> Dict:
        """Run targeted analysis for specific companies"""
        logger.info(f"Running targeted analysis for companies: {company_symbols}")
        
        # Get company names from symbols
        company_names = []
        for symbol in company_symbols:
            company_row = self.companies_df[self.companies_df['symbol'] == symbol]
            if not company_row.empty:
                company_names.append(company_row.iloc[0]['company_name'])
            else:
                logger.warning(f"Company symbol {symbol} not found in NSE list")
        
        if not company_names:
            logger.error("No valid companies found for analysis")
            return {'error': 'No valid companies found', 'articles': []}
        
        # Scrape news for specific companies
        company_articles_dict = self.scraper.get_company_specific_news(
            company_names, 
            max_per_company=max_articles_per_company
        )
        
        # Flatten articles
        all_articles = []
        for company, articles in company_articles_dict.items():
            all_articles.extend(articles)
        
        # Analyze articles
        analyzed_articles = self.analyzer.batch_analyze_articles(
            all_articles, 
            self.companies_df
        )
        
        # Generate summary
        summary = self.analyzer.generate_summary_insights(analyzed_articles)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'target_companies': company_symbols,
            'articles': analyzed_articles,
            'summary': summary
        }
        
        logger.info(f"Targeted analysis completed for {len(company_names)} companies")
        return results
    
    def run_dashboard(self, port: int = None, debug: bool = None):
        """Run the interactive dashboard"""
        logger.info("Starting interactive dashboard...")
        if not self.dashboard:
            self.dashboard = NewsDashboard()
        
        self.dashboard.run(port=port, debug=debug)

def create_sample_report(results: Dict) -> str:
    """Create a sample text report from results"""
    if not results or 'articles' not in results:
        return "No data available for report generation."
    
    report_lines = [
        "=" * 60,
        "NSE COMPANIES NEWS ANALYSIS REPORT",
        "=" * 60,
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Analysis timestamp: {results.get('timestamp', 'N/A')}",
        f"Execution time: {results.get('execution_time_seconds', 'N/A')} seconds",
        "",
        "SUMMARY:",
        f"  Total articles analyzed: {len(results.get('articles', []))}",
        f"  Relevant articles: {results.get('relevant_articles', 0)}",
        "",
    ]
    
    # Add summary insights
    summary = results.get('summary', {})
    if summary:
        report_lines.extend([
            "SENTIMENT DISTRIBUTION:",
            f"  {summary.get('sentiment_distribution', {})}",
            "",
            "IMPACT DISTRIBUTION:",
            f"  {summary.get('impact_distribution', {})}",
            "",
            f"Average Sentiment Score: {summary.get('average_sentiment_score', 0):.3f}",
            f"Average Investment Score: {summary.get('average_investment_score', 0):.3f}",
            "",
        ])
    
    # Add top insights
    relevant_articles = results.get('relevant_articles_only', [])[:5]
    if relevant_articles:
        report_lines.extend([
            "TOP INVESTMENT INSIGHTS:",
            "-" * 30,
        ])
        
        for i, article in enumerate(relevant_articles, 1):
            companies = [c['symbol'] for c in article.get('matched_companies', [])][:3]
            report_lines.extend([
                f"{i}. {article.get('title', 'No Title')[:80]}...",
                f"   Companies: {', '.join(companies) if companies else 'N/A'}",
                f"   Sentiment: {article.get('sentiment_label', 'N/A')} ({article.get('sentiment_score', 0):.2f})",
                f"   Investment Score: {article.get('investment_score', 0):.3f}",
                f"   Source: {article.get('source', 'N/A')}",
                ""
            ])
    
    return "\n".join(report_lines)

def main():
    """Main function with CLI interface"""
    parser = argparse.ArgumentParser(description='NSE News Analysis System')
    parser.add_argument('--mode', choices=['full', 'companies', 'dashboard'], 
                       default='full', help='Analysis mode')
    parser.add_argument('--companies', nargs='+', help='Company symbols for targeted analysis')
    parser.add_argument('--top-companies', type=int, default=50, 
                       help='Number of top companies to analyze')
    parser.add_argument('--output', help='Output filename for results')
    parser.add_argument('--dashboard-port', type=int, default=8050, 
                       help='Port for dashboard')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize system
    system = NSENewsAnalysisSystem()
    system.initialize()
    
    # Run based on mode
    if args.mode == 'full':
        logger.info("Running full news analysis...")
        results = system.run_full_analysis(top_companies=args.top_companies)
        
        # Save results
        output_file = system.save_results(results, args.output)
        
        # Print summary report
        report = create_sample_report(results)
        print("\n" + report)
        print(f"\nDetailed results saved to: {output_file}")
        print(f"You can now run the dashboard with: python main.py --mode dashboard")
        
    elif args.mode == 'companies':
        if not args.companies:
            logger.error("Company symbols required for targeted analysis")
            sys.exit(1)
        
        logger.info(f"Running targeted analysis for: {args.companies}")
        results = system.run_analysis_for_companies(args.companies)
        
        # Save results
        output_file = system.save_results(results, args.output)
        
        # Print summary report
        report = create_sample_report(results)
        print("\n" + report)
        print(f"\nDetailed results saved to: {output_file}")
        
    elif args.mode == 'dashboard':
        logger.info("Starting interactive dashboard...")
        system.run_dashboard(port=args.dashboard_port)

if __name__ == "__main__":
    # Setup logging first
    setup_logging()
    main()
