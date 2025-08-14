# NSE Companies News Analysis System

A comprehensive news scraping and analysis system for NSE-listed companies that helps identify investment opportunities through AI-powered sentiment analysis and structured insights.

## 🎯 Features

- **Multi-source News Scraping**: Automatically scrapes news from Economic Times, Business Standard, Mint, and MoneyControl
- **Intelligent Company Matching**: Advanced algorithms to match news articles with NSE companies
- **Sentiment Analysis**: AI-powered sentiment analysis using TextBlob and custom investment-focused keywords
- **Investment Scoring**: Proprietary scoring system to rank news relevance for investment decisions
- **Interactive Dashboard**: Beautiful web interface with real-time charts and insights
- **Automated Pipeline**: Complete end-to-end automation from scraping to structured insights

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   News Sources  │───▶│   Web Scraper   │───▶│    Analyzer     │
│                 │    │                 │    │                 │
│ • Economic Times│    │ • RSS Feeds     │    │ • Sentiment     │
│ • Bus. Standard │    │ • Direct Scrape │    │ • Keywords      │
│ • Mint          │    │ • Google Search │    │ • Company Match │
│ • MoneyControl  │    │ • Rate Limiting │    │ • Investment    │
└─────────────────┘    └─────────────────┘    │   Scoring       │
                                              └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │◀───│  Data Storage   │◀───│   Structured    │
│                 │    │                 │    │     Output      │
│ • Interactive   │    │ • JSON Files    │    │                 │
│ • Charts        │    │ • Analysis      │    │ • Ranked News   │
│ • Filtering     │    │   Results       │    │ • Investment    │
│ • Real-time     │    │ • History       │    │   Insights      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for news scraping
- At least 2GB RAM for analysis processing
- 1GB free disk space for data storage

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project to your desired location
cd /path/to/your/project

# Install required packages
pip install -r requirements.txt

# Download additional NLTK data (will be done automatically on first run)
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 2. Basic Usage

```bash
# Run full analysis (recommended for first time)
python main.py --mode full

# View results in interactive dashboard
python main.py --mode dashboard

# Analyze specific companies
python main.py --mode companies --companies RELIANCE TCS HDFCBANK

# Run with verbose logging
python main.py --mode full --verbose
```

### 3. Access Dashboard

After running the analysis, access the dashboard at:
```
http://localhost:8050
```

## 📊 Dashboard Features

### Overview Tab
- **Sentiment Distribution**: Pie chart showing positive/negative/neutral news distribution
- **Impact Categories**: Bar chart of investment impact categories
- **Summary Cards**: Quick metrics (total articles, companies mentioned, etc.)

### Company Analysis Tab
- **Top Mentioned Companies**: Interactive chart showing mention frequency vs sentiment
- **Company Details Table**: Sortable table with sentiment statistics per company

### Sentiment Trends Tab
- **Time Series Analysis**: Daily sentiment trends over time
- **Trend Indicators**: Visual markers for positive/negative thresholds

### Investment Insights Tab
- **Top Investment Opportunities**: Ranked list of high-impact news
- **Detailed Article Cards**: Company mentions, scores, and direct links

### Article Details Tab
- **Comprehensive Table**: All articles with sorting and filtering
- **Export Capabilities**: Download filtered results

## 🔧 Configuration

### Customizing News Sources

Edit `config.py` to modify news sources:

```python
NEWS_SOURCES = {
    'your_source': {
        'base_url': 'https://example.com',
        'rss_feeds': ['https://example.com/rss'],
        'search_url': 'https://example.com/search'
    }
}
```

### Investment Keywords

Modify investment-relevant keywords in `config.py`:

```python
INVESTMENT_KEYWORDS = {
    'positive': ['expansion', 'investment', 'growth', ...],
    'negative': ['loss', 'decline', 'lawsuit', ...],
    'neutral': ['announcement', 'meeting', 'report', ...]
}
```

### Analysis Parameters

Adjust analysis settings in `config.py`:

```python
ANALYSIS_CONFIG = {
    'sentiment_threshold': 0.1,
    'relevance_threshold': 0.3,
    'days_lookback': 7,
    'max_articles_per_company': 10
}
```

## 📁 Project Structure

```
ShareMIP/
├── EQUITY_L.csv           # NSE companies data
├── config.py              # Configuration settings
├── utils.py               # Utility functions
├── scraper.py             # News scraping logic
├── analyzer.py            # Analysis and ML models
├── dashboard.py           # Interactive web dashboard
├── main.py               # Main orchestration script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/                 # Temporary data storage
├── output/               # Analysis results
└── logs/                 # Log files
```

## 🎯 Use Cases

### Investment Research
```bash
# Analyze top 100 companies for recent investment news
python main.py --mode full --top-companies 100

# Focus on specific sectors (manually select companies)
python main.py --mode companies --companies RELIANCE ONGC IOC BPCL
```

### Daily Monitoring
```bash
# Set up automated daily analysis (add to cron)
0 9 * * * /path/to/python /path/to/main.py --mode full --top-companies 200
```

### Portfolio Tracking
```bash
# Monitor your portfolio companies
python main.py --mode companies --companies INFY TCS HDFCBANK ICICIBANK SBIN
```

## 🎨 Example Insights

The system generates insights like:

```
TOP INVESTMENT INSIGHTS:
1. Reliance Industries announces major investment in renewable energy sector
   Companies: RELIANCE
   Sentiment: Positive (0.85)
   Investment Score: 0.892
   Source: Economic Times

2. TCS bags multi-million dollar contract from European bank
   Companies: TCS
   Sentiment: Positive (0.72)
   Investment Score: 0.834
   Source: Business Standard
```

## 📈 Investment Scoring Algorithm

Our proprietary scoring combines:

- **Sentiment Analysis (40%)**: TextBlob polarity + custom keywords
- **Keyword Relevance (30%)**: Investment-specific term density
- **Company Mentions (20%)**: Number and confidence of company matches
- **Source Credibility (10%)**: Reliability of news source

Formula: `Score = 0.4×|Sentiment| + 0.3×Keywords + 0.2×Companies + 0.1×Source`

## 🔍 Advanced Features

### Custom Company Lists
```python
# Create custom company analysis
companies = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]
results = system.run_analysis_for_companies(companies, max_articles_per_company=15)
```

### Filtering and Analysis
```python
# Filter by sentiment
positive_articles = [a for a in results['articles'] 
                    if a.get('sentiment_label') == 'Positive']

# High-impact investment news
high_impact = [a for a in results['articles'] 
               if a.get('investment_score', 0) > 0.8]
```

### Export Results
```python
import pandas as pd

# Convert to DataFrame for analysis
df = pd.DataFrame(results['articles'])
df.to_csv('investment_insights.csv', index=False)
```

## 🛠️ Troubleshooting

### Common Issues

**1. ImportError or ModuleNotFoundError**
```bash
pip install -r requirements.txt
pip install --upgrade pip
```

**2. Rate Limiting / Blocked Requests**
- The system includes built-in delays and retry logic
- Increase delays in `config.py` if needed:
```python
SCRAPING_CONFIG = {
    'delay_between_requests': 3,  # Increase from 2 to 3 seconds
}
```

**3. No Articles Found**
- Check internet connection
- Verify news source URLs are accessible
- Some sources may block automated requests temporarily

**4. Dashboard Not Loading**
```bash
# Try different port
python main.py --mode dashboard --dashboard-port 8051
```

**5. Memory Issues**
- Reduce the number of companies analyzed:
```bash
python main.py --mode full --top-companies 25
```

### Debugging

Enable verbose logging:
```bash
python main.py --mode full --verbose
```

Check log files:
```bash
cat logs/news_scraper.log
```

## 🔒 Ethical Considerations

- **Rate Limiting**: Built-in delays to respect website resources
- **Terms of Service**: Ensure compliance with news website terms
- **Data Usage**: For research and personal investment decisions only
- **Attribution**: Respect source attribution and copyright

## 🚀 Future Enhancements

### Planned Features

1. **Machine Learning Models**
   - LSTM for sentiment analysis
   - Market movement prediction
   - Risk assessment scoring

2. **Additional Data Sources**
   - Social media sentiment
   - Regulatory filings
   - Financial statements

3. **Advanced Analytics**
   - Sector-wise analysis
   - Peer comparison
   - Historical trend analysis

4. **Alerting System**
   - Email notifications
   - Slack integration
   - Custom alert rules

5. **Mobile App**
   - React Native dashboard
   - Push notifications
   - Offline reading

## 📞 Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review log files for detailed error messages
3. Create detailed issue reports with:
   - System information (OS, Python version)
   - Error logs
   - Steps to reproduce

## 📄 License

This project is for educational and research purposes. Please respect the terms of service of all news sources and use the data responsibly.

---

**Happy Investing! 📈**

*Remember: This tool provides analysis and insights but should not be the sole basis for investment decisions. Always consult with financial advisors and do your own research.*
# AI-Stock-Analysis
