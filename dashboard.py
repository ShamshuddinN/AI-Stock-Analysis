"""
Interactive Dashboard for NSE News Analysis and Investment Insights
"""
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from collections import Counter
import json

from config import DASHBOARD_CONFIG, OUTPUT_DIR
from utils import load_from_json, save_to_json

logger = logging.getLogger(__name__)

class NewsDashboard:
    """Interactive dashboard for news analysis visualization"""
    
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
        self.data_cache = {}
    
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("NSE Companies News Analysis Dashboard", 
                       className="text-center mb-4"),
                html.Hr(),
            ], className="header"),
            
            # Control Panel
            html.Div([
                html.Div([
                    html.Label("Select Time Range:"),
                    dcc.Dropdown(
                        id="time-range-dropdown",
                        options=[
                            {"label": "Last 24 Hours", "value": 1},
                            {"label": "Last 3 Days", "value": 3},
                            {"label": "Last Week", "value": 7},
                            {"label": "Last Month", "value": 30}
                        ],
                        value=7,
                        className="mb-3"
                    )
                ], className="col-md-3"),
                
                html.Div([
                    html.Label("Sentiment Filter:"),
                    dcc.Dropdown(
                        id="sentiment-filter",
                        options=[
                            {"label": "All", "value": "all"},
                            {"label": "Positive", "value": "Positive"},
                            {"label": "Negative", "value": "Negative"},
                            {"label": "Neutral", "value": "Neutral"}
                        ],
                        value="all",
                        className="mb-3"
                    )
                ], className="col-md-3"),
                
                html.Div([
                    html.Label("Min Relevance Score:"),
                    dcc.Slider(
                        id="relevance-slider",
                        min=0,
                        max=1,
                        value=0.3,
                        step=0.1,
                        marks={i/10: str(i/10) for i in range(0, 11, 2)},
                        className="mb-3"
                    )
                ], className="col-md-3"),
                
                html.Div([
                    html.Button(
                        "Refresh Data",
                        id="refresh-button",
                        className="btn btn-primary",
                        n_clicks=0
                    )
                ], className="col-md-3")
            ], className="row control-panel mb-4"),
            
            # Summary Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.H4(id="total-articles-card", className="card-title"),
                        html.P("Total Articles", className="card-text")
                    ], className="card-body")
                ], className="card col-md-2"),
                
                html.Div([
                    html.Div([
                        html.H4(id="relevant-articles-card", className="card-title"),
                        html.P("Relevant Articles", className="card-text")
                    ], className="card-body")
                ], className="card col-md-2"),
                
                html.Div([
                    html.Div([
                        html.H4(id="companies-mentioned-card", className="card-title"),
                        html.P("Companies Mentioned", className="card-text")
                    ], className="card-body")
                ], className="card col-md-2"),
                
                html.Div([
                    html.Div([
                        html.H4(id="avg-sentiment-card", className="card-title"),
                        html.P("Avg Sentiment Score", className="card-text")
                    ], className="card-body")
                ], className="card col-md-2"),
                
                html.Div([
                    html.Div([
                        html.H4(id="positive-news-card", className="card-title"),
                        html.P("Positive News %", className="card-text")
                    ], className="card-body")
                ], className="card col-md-2"),
                
                html.Div([
                    html.Div([
                        html.H4(id="high-impact-card", className="card-title"),
                        html.P("High Impact News", className="card-text")
                    ], className="card-body")
                ], className="card col-md-2")
            ], className="row summary-cards mb-4"),
            
            # Main Content Tabs
            dcc.Tabs(id="main-tabs", value="overview", children=[
                dcc.Tab(label="Overview", value="overview"),
                dcc.Tab(label="Company Analysis", value="companies"),
                dcc.Tab(label="Sentiment Trends", value="sentiment"),
                dcc.Tab(label="Investment Insights", value="insights"),
                dcc.Tab(label="Article Details", value="articles")
            ]),
            
            # Tab Content
            html.Div(id="tab-content", className="mt-4"),
            
            # Data Store
            dcc.Store(id="analysis-data-store"),
            dcc.Store(id="filtered-data-store"),
            
            # Auto-refresh interval
            dcc.Interval(
                id="interval-component",
                interval=DASHBOARD_CONFIG['refresh_interval'] * 1000,  # in milliseconds
                n_intervals=0
            )
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            Output("analysis-data-store", "data"),
            [Input("interval-component", "n_intervals"),
             Input("refresh-button", "n_clicks")]
        )
        def load_analysis_data(n_intervals, n_clicks):
            """Load analysis data from storage"""
            try:
                # Load latest analysis results
                analysis_file = OUTPUT_DIR / "latest_analysis.json"
                data = load_from_json(analysis_file)
                
                if data:
                    logger.info(f"Loaded analysis data with {len(data.get('articles', []))} articles")
                    return data
                else:
                    return {"articles": [], "summary": {}, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Error loading analysis data: {e}")
                return {"articles": [], "summary": {}, "error": str(e)}
        
        @self.app.callback(
            Output("filtered-data-store", "data"),
            [Input("analysis-data-store", "data"),
             Input("time-range-dropdown", "value"),
             Input("sentiment-filter", "value"),
             Input("relevance-slider", "value")]
        )
        def filter_data(analysis_data, time_range, sentiment_filter, min_relevance):
            """Filter data based on user selections"""
            if not analysis_data or not analysis_data.get("articles"):
                return {"articles": [], "summary": {}}
            
            articles = analysis_data["articles"]
            
            # Time range filter
            cutoff_date = datetime.now() - timedelta(days=time_range)
            filtered_articles = []
            
            for article in articles:
                # Check date
                pub_date_str = article.get("published_date")
                if pub_date_str:
                    try:
                        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                        if pub_date < cutoff_date:
                            continue
                    except:
                        pass  # Include if date parsing fails
                
                # Check sentiment
                if sentiment_filter != "all":
                    if article.get("sentiment_label") != sentiment_filter:
                        continue
                
                # Check relevance
                if article.get("relevance_score", 0) < min_relevance:
                    continue
                
                filtered_articles.append(article)
            
            # Generate filtered summary
            summary = self.generate_summary(filtered_articles)
            
            return {"articles": filtered_articles, "summary": summary}
        
        # Summary cards callbacks
        @self.app.callback(
            [Output("total-articles-card", "children"),
             Output("relevant-articles-card", "children"),
             Output("companies-mentioned-card", "children"),
             Output("avg-sentiment-card", "children"),
             Output("positive-news-card", "children"),
             Output("high-impact-card", "children")],
            [Input("filtered-data-store", "data")]
        )
        def update_summary_cards(filtered_data):
            """Update summary cards"""
            if not filtered_data or not filtered_data.get("articles"):
                return "0", "0", "0", "0.0", "0%", "0"
            
            summary = filtered_data["summary"]
            articles = filtered_data["articles"]
            
            total_articles = len(articles)
            relevant_articles = len([a for a in articles if a.get("relevance_score", 0) > 0.5])
            
            # Count unique companies
            companies = set()
            for article in articles:
                for company in article.get("matched_companies", []):
                    companies.add(company["symbol"])
            
            avg_sentiment = summary.get("average_sentiment_score", 0)
            positive_pct = summary.get("sentiment_distribution", {}).get("Positive", 0)
            total_valid = sum(summary.get("sentiment_distribution", {}).values())
            positive_pct = round((positive_pct / total_valid) * 100 if total_valid > 0 else 0, 1)
            
            high_impact = len([a for a in articles if a.get("investment_score", 0) > 0.7])
            
            return (
                str(total_articles),
                str(relevant_articles),
                str(len(companies)),
                f"{avg_sentiment:.2f}",
                f"{positive_pct}%",
                str(high_impact)
            )
        
        @self.app.callback(
            Output("tab-content", "children"),
            [Input("main-tabs", "value"),
             Input("filtered-data-store", "data")]
        )
        def render_tab_content(active_tab, filtered_data):
            """Render content based on active tab"""
            if not filtered_data or not filtered_data.get("articles"):
                return html.Div("No data available", className="text-center")
            
            if active_tab == "overview":
                return self.render_overview_tab(filtered_data)
            elif active_tab == "companies":
                return self.render_companies_tab(filtered_data)
            elif active_tab == "sentiment":
                return self.render_sentiment_tab(filtered_data)
            elif active_tab == "insights":
                return self.render_insights_tab(filtered_data)
            elif active_tab == "articles":
                return self.render_articles_tab(filtered_data)
            
            return html.Div("Tab content not implemented")
    
    def generate_summary(self, articles):
        """Generate summary statistics from articles"""
        if not articles:
            return {}
        
        valid_articles = [a for a in articles if "error" not in a]
        
        # Sentiment distribution
        sentiment_labels = [a.get("sentiment_label", "Neutral") for a in valid_articles]
        sentiment_dist = dict(Counter(sentiment_labels))
        
        # Impact distribution
        impact_categories = [a.get("impact_category", "Neutral") for a in valid_articles]
        impact_dist = dict(Counter(impact_categories))
        
        # Average scores
        avg_sentiment = np.mean([a.get("sentiment_score", 0) for a in valid_articles]) if valid_articles else 0
        avg_relevance = np.mean([a.get("relevance_score", 0) for a in valid_articles]) if valid_articles else 0
        avg_investment = np.mean([a.get("investment_score", 0) for a in valid_articles]) if valid_articles else 0
        
        return {
            "total_articles": len(articles),
            "valid_articles": len(valid_articles),
            "sentiment_distribution": sentiment_dist,
            "impact_distribution": impact_dist,
            "average_sentiment_score": round(avg_sentiment, 3),
            "average_relevance_score": round(avg_relevance, 3),
            "average_investment_score": round(avg_investment, 3)
        }
    
    def render_overview_tab(self, filtered_data):
        """Render overview tab content"""
        summary = filtered_data["summary"]
        
        # Sentiment distribution pie chart
        sentiment_fig = px.pie(
            values=list(summary.get("sentiment_distribution", {}).values()),
            names=list(summary.get("sentiment_distribution", {}).keys()),
            title="Sentiment Distribution"
        )
        
        # Impact distribution bar chart
        impact_fig = px.bar(
            x=list(summary.get("impact_distribution", {}).keys()),
            y=list(summary.get("impact_distribution", {}).values()),
            title="Investment Impact Categories"
        )
        
        return html.Div([
            html.Div([
                dcc.Graph(figure=sentiment_fig)
            ], className="col-md-6"),
            html.Div([
                dcc.Graph(figure=impact_fig)
            ], className="col-md-6")
        ], className="row")
    
    def render_companies_tab(self, filtered_data):
        """Render companies analysis tab"""
        articles = filtered_data["articles"]
        
        # Count company mentions
        company_counts = Counter()
        company_sentiments = {}
        
        for article in articles:
            sentiment = article.get("sentiment_score", 0)
            for company in article.get("matched_companies", []):
                symbol = company["symbol"]
                company_counts[symbol] += 1
                
                if symbol not in company_sentiments:
                    company_sentiments[symbol] = []
                company_sentiments[symbol].append(sentiment)
        
        # Top 15 mentioned companies
        top_companies = company_counts.most_common(15)
        if not top_companies:
            return html.Div("No companies found in the data", className="text-center")
        
        # Create company analysis chart
        company_names = [comp[0] for comp in top_companies]
        mention_counts = [comp[1] for comp in top_companies]
        avg_sentiments = [np.mean(company_sentiments.get(comp[0], [0])) for comp in top_companies]
        
        fig = go.Figure()
        
        # Add mention count bars
        fig.add_trace(go.Bar(
            name='Mention Count',
            x=company_names,
            y=mention_counts,
            yaxis='y',
            marker_color='lightblue'
        ))
        
        # Add average sentiment line
        fig.add_trace(go.Scatter(
            name='Avg Sentiment',
            x=company_names,
            y=avg_sentiments,
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title='Top Companies: Mentions vs Average Sentiment',
            xaxis=dict(tickangle=45),
            yaxis=dict(title='Mention Count', side='left'),
            yaxis2=dict(title='Average Sentiment', side='right', overlaying='y'),
            height=500
        )
        
        # Company table
        company_table_data = []
        for symbol in company_names:
            sentiments = company_sentiments.get(symbol, [0])
            company_table_data.append({
                'Symbol': symbol,
                'Mentions': company_counts[symbol],
                'Avg Sentiment': round(np.mean(sentiments), 3),
                'Sentiment Std': round(np.std(sentiments), 3) if len(sentiments) > 1 else 0,
                'Latest Sentiment': round(sentiments[-1], 3) if sentiments else 0
            })
        
        table = dash_table.DataTable(
            data=company_table_data,
            columns=[{"name": col, "id": col} for col in company_table_data[0].keys()],
            style_cell={'textAlign': 'center'},
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Avg Sentiment} > 0.1', 'column_id': 'Avg Sentiment'},
                    'backgroundColor': '#d4edda',
                    'color': 'black',
                },
                {
                    'if': {'filter_query': '{Avg Sentiment} < -0.1', 'column_id': 'Avg Sentiment'},
                    'backgroundColor': '#f8d7da',
                    'color': 'black',
                }
            ]
        )
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H4("Company Details"),
            table
        ])
    
    def render_sentiment_tab(self, filtered_data):
        """Render sentiment trends tab"""
        articles = filtered_data["articles"]
        
        # Create time series of sentiment
        sentiment_data = []
        for article in articles:
            pub_date = article.get("published_date")
            if pub_date:
                try:
                    date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    sentiment_data.append({
                        'date': date_obj.date(),
                        'sentiment': article.get("sentiment_score", 0),
                        'impact': article.get("impact_category", "Neutral")
                    })
                except:
                    continue
        
        if not sentiment_data:
            return html.Div("No sentiment data available", className="text-center")
        
        # Group by date and calculate daily averages
        df = pd.DataFrame(sentiment_data)
        daily_sentiment = df.groupby('date').agg({
            'sentiment': ['mean', 'count'],
            'impact': lambda x: x.mode().iloc[0] if len(x) > 0 else 'Neutral'
        }).reset_index()
        
        daily_sentiment.columns = ['date', 'avg_sentiment', 'article_count', 'dominant_impact']
        
        # Create sentiment trend chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_sentiment['date'],
            y=daily_sentiment['avg_sentiment'],
            mode='lines+markers',
            name='Daily Avg Sentiment',
            line=dict(color='blue', width=2),
            marker=dict(size=daily_sentiment['article_count'] * 2)  # Size by article count
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
        fig.add_hline(y=0.1, line_dash="dot", line_color="green", annotation_text="Positive Threshold")
        fig.add_hline(y=-0.1, line_dash="dot", line_color="red", annotation_text="Negative Threshold")
        
        fig.update_layout(
            title='Sentiment Trend Over Time',
            xaxis_title='Date',
            yaxis_title='Average Sentiment Score',
            height=400
        )
        
        return html.Div([
            dcc.Graph(figure=fig),
            html.P("Note: Marker size indicates the number of articles per day")
        ])
    
    def render_insights_tab(self, filtered_data):
        """Render investment insights tab"""
        articles = filtered_data["articles"]
        
        # Get top insights
        high_impact_articles = sorted(
            [a for a in articles if a.get("investment_score", 0) > 0.6],
            key=lambda x: x.get("investment_score", 0),
            reverse=True
        )[:10]
        
        if not high_impact_articles:
            return html.Div("No high-impact investment news found", className="text-center")
        
        # Create insights cards
        insight_cards = []
        for i, article in enumerate(high_impact_articles):
            companies_text = ", ".join([c["symbol"] for c in article.get("matched_companies", [])][:3])
            
            card = html.Div([
                html.Div([
                    html.H5(f"#{i+1}: {article.get('title', 'No Title')[:80]}...", 
                           className="card-title"),
                    html.P([
                        html.Strong("Companies: "), companies_text or "N/A",
                        html.Br(),
                        html.Strong("Investment Score: "), 
                        f"{article.get('investment_score', 0):.3f}",
                        html.Br(),
                        html.Strong("Sentiment: "), 
                        f"{article.get('sentiment_label', 'N/A')} ({article.get('sentiment_score', 0):.2f})",
                        html.Br(),
                        html.Strong("Impact: "), article.get('impact_category', 'N/A'),
                        html.Br(),
                        html.Strong("Source: "), article.get('source', 'N/A')
                    ], className="card-text"),
                    html.A("Read Article", href=article.get('url', '#'), 
                          className="btn btn-sm btn-primary", target="_blank")
                ], className="card-body")
            ], className="card mb-3")
            
            insight_cards.append(card)
        
        return html.Div([
            html.H4("Top Investment Insights"),
            html.Div(insight_cards)
        ])
    
    def render_articles_tab(self, filtered_data):
        """Render detailed articles tab"""
        articles = filtered_data["articles"]
        
        # Prepare table data
        table_data = []
        for article in articles[:50]:  # Limit to 50 articles for performance
            companies_text = ", ".join([c["symbol"] for c in article.get("matched_companies", [])][:3])
            
            table_data.append({
                'Title': article.get('title', 'No Title')[:80] + "...",
                'Companies': companies_text or "N/A",
                'Source': article.get('source', 'N/A'),
                'Sentiment': article.get('sentiment_label', 'N/A'),
                'Sentiment Score': round(article.get('sentiment_score', 0), 3),
                'Investment Score': round(article.get('investment_score', 0), 3),
                'Relevance Score': round(article.get('relevance_score', 0), 3),
                'Impact': article.get('impact_category', 'N/A'),
                'URL': article.get('url', '#')
            })
        
        if not table_data:
            return html.Div("No articles available", className="text-center")
        
        table = dash_table.DataTable(
            data=table_data,
            columns=[
                {"name": "Title", "id": "Title", "presentation": "markdown"},
                {"name": "Companies", "id": "Companies"},
                {"name": "Source", "id": "Source"},
                {"name": "Sentiment", "id": "Sentiment"},
                {"name": "Sentiment Score", "id": "Sentiment Score", "type": "numeric", "format": {"specifier": ".3f"}},
                {"name": "Investment Score", "id": "Investment Score", "type": "numeric", "format": {"specifier": ".3f"}},
                {"name": "Relevance Score", "id": "Relevance Score", "type": "numeric", "format": {"specifier": ".3f"}},
                {"name": "Impact", "id": "Impact"}
            ],
            style_cell={
                'textAlign': 'left',
                'maxWidth': '200px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Investment Score} > 0.7'},
                    'backgroundColor': '#d4edda'
                },
                {
                    'if': {'filter_query': '{Sentiment} = "Positive"'},
                    'color': 'green'
                },
                {
                    'if': {'filter_query': '{Sentiment} = "Negative"'},
                    'color': 'red'
                }
            ],
            sort_action="native",
            filter_action="native",
            page_action="native",
            page_current=0,
            page_size=20
        )
        
        return html.Div([
            html.H4("Detailed Articles"),
            table
        ])
    
    def run(self, debug=None, port=None, host=None):
        """Run the dashboard"""
        debug = debug if debug is not None else DASHBOARD_CONFIG['debug']
        port = port if port is not None else DASHBOARD_CONFIG['port']
        host = host if host is not None else DASHBOARD_CONFIG['host']
        
        logger.info(f"Starting dashboard on {host}:{port}")
        self.app.run(debug=debug, port=port, host=host)

def main():
    """Run the dashboard"""
    dashboard = NewsDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
