"""
Revenue Analytics Dashboard - AI Agent
Real-time tracking and optimization of all revenue streams
"""

import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import openai
import requests
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

class RevenueStream(Enum):
    COURSES = "courses"
    COACHING = "coaching"
    AFFILIATES = "affiliates"
    NEWSLETTERS = "newsletters"
    CONSULTING = "consulting"
    TEMPLATES = "templates"
    COMMUNITIES = "communities"

@dataclass
class RevenueMetric:
    stream: RevenueStream
    amount: float
    date: datetime
    source: str
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    attribution: Optional[Dict] = None

@dataclass
class CustomerMetric:
    customer_id: str
    email: str
    name: str
    acquisition_date: datetime
    lifetime_value: float
    total_purchases: int
    avg_order_value: float
    last_purchase_date: Optional[datetime]
    churn_probability: float
    segment: str

@dataclass
class ConversionMetric:
    funnel_stage: str
    visitors: int
    conversions: int
    conversion_rate: float
    revenue: float
    date: datetime
    source: str

class RevenueAnalyticsDashboard:
    def __init__(self, config: Dict):
        self.config = config
        self.openai_client = openai.OpenAI(api_key=config['openai_api_key'])
        self.db_path = config.get('database_path', 'revenue_analytics.db')

        # Initialize database
        self._init_database()

        # Revenue targets and benchmarks
        self.revenue_targets = {
            'monthly_total': 25000,
            'courses': 15000,
            'coaching': 6000,
            'affiliates': 2000,
            'newsletters': 1000,
            'consulting': 1000
        }

        # KPI thresholds
        self.kpi_thresholds = {
            'customer_ltv': 450,
            'churn_rate': 0.05,  # 5% monthly
            'conversion_rate': 0.08,  # 8% overall
            'avg_order_value': 150,
            'monthly_growth_rate': 0.15  # 15%
        }

    def _init_database(self):
        """Initialize database for revenue analytics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Revenue transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stream TEXT NOT NULL,
                amount REAL NOT NULL,
                date TIMESTAMP NOT NULL,
                source TEXT,
                customer_id TEXT,
                product_id TEXT,
                attribution TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Customer metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_metrics (
                customer_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                acquisition_date TIMESTAMP,
                lifetime_value REAL DEFAULT 0.0,
                total_purchases INTEGER DEFAULT 0,
                avg_order_value REAL DEFAULT 0.0,
                last_purchase_date TIMESTAMP,
                churn_probability REAL DEFAULT 0.0,
                segment TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Conversion funnel table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversion_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funnel_stage TEXT NOT NULL,
                visitors INTEGER NOT NULL,
                conversions INTEGER NOT NULL,
                conversion_rate REAL NOT NULL,
                revenue REAL DEFAULT 0.0,
                date TIMESTAMP NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Content attribution table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_attribution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                platform TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                leads_generated INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue_attributed REAL DEFAULT 0.0,
                date TIMESTAMP NOT NULL
            )
        ''')

        # Affiliate performance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affiliate_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                affiliate_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                sales INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0.0,
                commission REAL DEFAULT 0.0,
                click_through_rate REAL DEFAULT 0.0,
                conversion_rate REAL DEFAULT 0.0,
                date TIMESTAMP NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def track_revenue_transaction(self, transaction: RevenueMetric) -> Dict:
        """Track individual revenue transaction"""

        # Save to database
        self._save_revenue_transaction(transaction)

        # Update customer metrics
        if transaction.customer_id:
            self._update_customer_metrics(transaction.customer_id, transaction.amount)

        # Update real-time dashboard
        self._update_realtime_metrics(transaction)

        # Check for milestone achievements
        milestones = self._check_revenue_milestones()

        return {
            'transaction_recorded': True,
            'transaction_id': f"txn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'milestones_achieved': milestones,
            'updated_metrics': self._get_current_day_metrics()
        }

    def generate_revenue_dashboard(self, timeframe: str = "30_days") -> Dict:
        """Generate comprehensive revenue dashboard"""

        # Calculate date range
        end_date = datetime.now()
        if timeframe == "7_days":
            start_date = end_date - timedelta(days=7)
        elif timeframe == "30_days":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "90_days":
            start_date = end_date - timedelta(days=90)
        elif timeframe == "1_year":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)

        dashboard_data = {
            'timeframe': timeframe,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'summary_metrics': self._calculate_summary_metrics(start_date, end_date),
            'revenue_streams': self._analyze_revenue_streams(start_date, end_date),
            'customer_analytics': self._analyze_customer_metrics(start_date, end_date),
            'conversion_funnel': self._analyze_conversion_funnel(start_date, end_date),
            'content_attribution': self._analyze_content_attribution(start_date, end_date),
            'growth_trends': self._analyze_growth_trends(start_date, end_date),
            'forecasts': self._generate_revenue_forecasts(),
            'recommendations': self._generate_optimization_recommendations(),
            'alerts': self._check_performance_alerts()
        }

        return dashboard_data

    def _calculate_summary_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate high-level summary metrics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total revenue
        cursor.execute('''
            SELECT SUM(amount) as total_revenue
            FROM revenue_transactions
            WHERE date >= ? AND date <= ?
        ''', (start_date.isoformat(), end_date.isoformat()))

        total_revenue = cursor.fetchone()[0] or 0

        # Revenue by stream
        cursor.execute('''
            SELECT stream, SUM(amount) as revenue
            FROM revenue_transactions
            WHERE date >= ? AND date <= ?
            GROUP BY stream
        ''', (start_date.isoformat(), end_date.isoformat()))

        revenue_by_stream = dict(cursor.fetchall())

        # Customer metrics
        cursor.execute('''
            SELECT
                COUNT(DISTINCT customer_id) as unique_customers,
                AVG(amount) as avg_order_value,
                COUNT(*) as total_transactions
            FROM revenue_transactions
            WHERE date >= ? AND date <= ? AND customer_id IS NOT NULL
        ''', (start_date.isoformat(), end_date.isoformat()))

        customer_stats = cursor.fetchone()

        # Growth calculation (compare with previous period)
        period_days = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_days)
        prev_end = start_date

        cursor.execute('''
            SELECT SUM(amount) as prev_revenue
            FROM revenue_transactions
            WHERE date >= ? AND date <= ?
        ''', (prev_start.isoformat(), prev_end.isoformat()))

        prev_revenue = cursor.fetchone()[0] or 0
        growth_rate = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0

        conn.close()

        return {
            'total_revenue': round(total_revenue, 2),
            'revenue_by_stream': revenue_by_stream,
            'unique_customers': customer_stats[0] if customer_stats[0] else 0,
            'avg_order_value': round(customer_stats[1], 2) if customer_stats[1] else 0,
            'total_transactions': customer_stats[2] if customer_stats[2] else 0,
            'growth_rate': round(growth_rate, 2),
            'target_progress': round((total_revenue / self.revenue_targets['monthly_total']) * 100, 1)
        }

    def _analyze_revenue_streams(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze performance of each revenue stream"""

        conn = sqlite3.connect(self.db_path)

        # Revenue by stream over time
        query = '''
            SELECT
                stream,
                DATE(date) as day,
                SUM(amount) as daily_revenue,
                COUNT(*) as transactions
            FROM revenue_transactions
            WHERE date >= ? AND date <= ?
            GROUP BY stream, DATE(date)
            ORDER BY day
        '''

        df = pd.read_sql_query(query, conn, params=(start_date.isoformat(), end_date.isoformat()))

        # Calculate stream performance metrics
        stream_analysis = {}

        for stream in RevenueStream:
            stream_data = df[df['stream'] == stream.value]

            if not stream_data.empty:
                total_revenue = stream_data['daily_revenue'].sum()
                avg_daily = stream_data['daily_revenue'].mean()
                transaction_count = stream_data['transactions'].sum()
                trend = self._calculate_trend(stream_data['daily_revenue'].tolist())

                stream_analysis[stream.value] = {
                    'total_revenue': round(total_revenue, 2),
                    'avg_daily_revenue': round(avg_daily, 2),
                    'transaction_count': int(transaction_count),
                    'avg_transaction_value': round(total_revenue / transaction_count, 2) if transaction_count > 0 else 0,
                    'trend': trend,
                    'target_progress': round((total_revenue / self.revenue_targets.get(stream.value, 1000)) * 100, 1),
                    'daily_data': stream_data.to_dict('records')
                }
            else:
                stream_analysis[stream.value] = {
                    'total_revenue': 0,
                    'avg_daily_revenue': 0,
                    'transaction_count': 0,
                    'avg_transaction_value': 0,
                    'trend': 'no_data',
                    'target_progress': 0,
                    'daily_data': []
                }

        conn.close()
        return stream_analysis

    def _analyze_customer_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze customer behavior and lifetime value"""

        conn = sqlite3.connect(self.db_path)

        # Customer acquisition and retention
        cursor.execute('''
            SELECT
                COUNT(DISTINCT customer_id) as total_customers,
                AVG(lifetime_value) as avg_ltv,
                AVG(total_purchases) as avg_purchases_per_customer,
                AVG(churn_probability) as avg_churn_risk
            FROM customer_metrics
            WHERE acquisition_date >= ?
        ''', (start_date.isoformat(),))

        customer_stats = cursor.fetchone()

        # Customer segmentation
        cursor.execute('''
            SELECT
                segment,
                COUNT(*) as customer_count,
                AVG(lifetime_value) as avg_ltv,
                SUM(lifetime_value) as total_ltv
            FROM customer_metrics
            GROUP BY segment
        ''')

        segmentation_data = cursor.fetchall()

        # Customer lifetime value distribution
        cursor.execute('''
            SELECT lifetime_value
            FROM customer_metrics
            WHERE lifetime_value > 0
            ORDER BY lifetime_value
        ''')

        ltv_values = [row[0] for row in cursor.fetchall()]

        # Churn analysis
        cursor.execute('''
            SELECT
                COUNT(CASE WHEN churn_probability > 0.7 THEN 1 END) as high_churn_risk,
                COUNT(CASE WHEN churn_probability BETWEEN 0.3 AND 0.7 THEN 1 END) as medium_churn_risk,
                COUNT(CASE WHEN churn_probability < 0.3 THEN 1 END) as low_churn_risk
            FROM customer_metrics
        ''')

        churn_analysis = cursor.fetchone()

        conn.close()

        return {
            'total_customers': customer_stats[0] if customer_stats[0] else 0,
            'avg_lifetime_value': round(customer_stats[1], 2) if customer_stats[1] else 0,
            'avg_purchases_per_customer': round(customer_stats[2], 2) if customer_stats[2] else 0,
            'avg_churn_risk': round(customer_stats[3], 3) if customer_stats[3] else 0,
            'segmentation': [
                {
                    'segment': row[0],
                    'customer_count': row[1],
                    'avg_ltv': round(row[2], 2),
                    'total_ltv': round(row[3], 2)
                }
                for row in segmentation_data
            ],
            'ltv_distribution': {
                'p25': np.percentile(ltv_values, 25) if ltv_values else 0,
                'p50': np.percentile(ltv_values, 50) if ltv_values else 0,
                'p75': np.percentile(ltv_values, 75) if ltv_values else 0,
                'p90': np.percentile(ltv_values, 90) if ltv_values else 0
            },
            'churn_risk_distribution': {
                'high_risk': churn_analysis[0] if churn_analysis[0] else 0,
                'medium_risk': churn_analysis[1] if churn_analysis[1] else 0,
                'low_risk': churn_analysis[2] if churn_analysis[2] else 0
            }
        }

    def _analyze_conversion_funnel(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze conversion funnel performance"""

        conn = sqlite3.connect(self.db_path)

        # Funnel metrics by stage
        cursor.execute('''
            SELECT
                funnel_stage,
                SUM(visitors) as total_visitors,
                SUM(conversions) as total_conversions,
                AVG(conversion_rate) as avg_conversion_rate,
                SUM(revenue) as total_revenue
            FROM conversion_metrics
            WHERE date >= ? AND date <= ?
            GROUP BY funnel_stage
            ORDER BY
                CASE funnel_stage
                    WHEN 'awareness' THEN 1
                    WHEN 'interest' THEN 2
                    WHEN 'consideration' THEN 3
                    WHEN 'intent' THEN 4
                    WHEN 'purchase' THEN 5
                    ELSE 6
                END
        ''', (start_date.isoformat(), end_date.isoformat()))

        funnel_stages = cursor.fetchall()

        # Conversion funnel visualization data
        funnel_data = []
        for stage_data in funnel_stages:
            funnel_data.append({
                'stage': stage_data[0],
                'visitors': stage_data[1],
                'conversions': stage_data[2],
                'conversion_rate': round(stage_data[3], 3),
                'revenue': round(stage_data[4], 2)
            })

        # Calculate funnel drop-off rates
        drop_off_analysis = []
        for i in range(len(funnel_data) - 1):
            current_stage = funnel_data[i]
            next_stage = funnel_data[i + 1]

            drop_off_rate = 1 - (next_stage['visitors'] / current_stage['visitors']) if current_stage['visitors'] > 0 else 0

            drop_off_analysis.append({
                'from_stage': current_stage['stage'],
                'to_stage': next_stage['stage'],
                'drop_off_rate': round(drop_off_rate, 3),
                'lost_visitors': current_stage['visitors'] - next_stage['visitors']
            })

        conn.close()

        return {
            'funnel_stages': funnel_data,
            'drop_off_analysis': drop_off_analysis,
            'overall_conversion_rate': funnel_data[-1]['conversion_rate'] if funnel_data else 0,
            'bottleneck_stage': max(drop_off_analysis, key=lambda x: x['drop_off_rate'])['from_stage'] if drop_off_analysis else None
        }

    def _analyze_content_attribution(self, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze which content drives the most revenue"""

        conn = sqlite3.connect(self.db_path)

        # Top performing content
        cursor.execute('''
            SELECT
                content_id,
                content_type,
                platform,
                SUM(views) as total_views,
                SUM(clicks) as total_clicks,
                SUM(leads_generated) as total_leads,
                SUM(conversions) as total_conversions,
                SUM(revenue_attributed) as total_revenue,
                AVG(CAST(clicks AS FLOAT) / NULLIF(views, 0)) as avg_ctr,
                AVG(CAST(conversions AS FLOAT) / NULLIF(clicks, 0)) as avg_conversion_rate
            FROM content_attribution
            WHERE date >= ? AND date <= ?
            GROUP BY content_id, content_type, platform
            ORDER BY total_revenue DESC
            LIMIT 20
        ''', (start_date.isoformat(), end_date.isoformat()))

        top_content = cursor.fetchall()

        # Platform performance
        cursor.execute('''
            SELECT
                platform,
                SUM(revenue_attributed) as total_revenue,
                SUM(views) as total_views,
                SUM(conversions) as total_conversions,
                COUNT(DISTINCT content_id) as content_pieces
            FROM content_attribution
            WHERE date >= ? AND date <= ?
            GROUP BY platform
            ORDER BY total_revenue DESC
        ''', (start_date.isoformat(), end_date.isoformat()))

        platform_performance = cursor.fetchall()

        # Content type analysis
        cursor.execute('''
            SELECT
                content_type,
                SUM(revenue_attributed) as total_revenue,
                AVG(CAST(conversions AS FLOAT) / NULLIF(views, 0)) as avg_conversion_rate,
                COUNT(*) as content_count
            FROM content_attribution
            WHERE date >= ? AND date <= ?
            GROUP BY content_type
            ORDER BY total_revenue DESC
        ''', (start_date.isoformat(), end_date.isoformat()))

        content_type_analysis = cursor.fetchall()

        conn.close()

        return {
            'top_performing_content': [
                {
                    'content_id': row[0],
                    'content_type': row[1],
                    'platform': row[2],
                    'views': row[3],
                    'clicks': row[4],
                    'leads': row[5],
                    'conversions': row[6],
                    'revenue': round(row[7], 2),
                    'ctr': round(row[8], 3) if row[8] else 0,
                    'conversion_rate': round(row[9], 3) if row[9] else 0
                }
                for row in top_content
            ],
            'platform_performance': [
                {
                    'platform': row[0],
                    'revenue': round(row[1], 2),
                    'views': row[2],
                    'conversions': row[3],
                    'content_pieces': row[4],
                    'revenue_per_view': round(row[1] / row[2], 4) if row[2] > 0 else 0
                }
                for row in platform_performance
            ],
            'content_type_analysis': [
                {
                    'content_type': row[0],
                    'revenue': round(row[1], 2),
                    'avg_conversion_rate': round(row[2], 3) if row[2] else 0,
                    'content_count': row[3]
                }
                for row in content_type_analysis
            ]
        }

    def _generate_revenue_forecasts(self) -> Dict:
        """Generate AI-powered revenue forecasts"""

        # Get historical data for forecasting
        conn = sqlite3.connect(self.db_path)

        # Daily revenue for the last 90 days
        query = '''
            SELECT
                DATE(date) as day,
                SUM(amount) as daily_revenue
            FROM revenue_transactions
            WHERE date >= date('now', '-90 days')
            GROUP BY DATE(date)
            ORDER BY day
        '''

        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            return {'error': 'Insufficient data for forecasting'}

        # Simple trend-based forecasting
        daily_revenues = df['daily_revenue'].tolist()

        # Calculate moving averages
        if len(daily_revenues) >= 7:
            weekly_avg = np.mean(daily_revenues[-7:])
        else:
            weekly_avg = np.mean(daily_revenues)

        if len(daily_revenues) >= 30:
            monthly_avg = np.mean(daily_revenues[-30:])
        else:
            monthly_avg = np.mean(daily_revenues)

        # Calculate trend
        if len(daily_revenues) >= 14:
            recent_avg = np.mean(daily_revenues[-7:])
            previous_avg = np.mean(daily_revenues[-14:-7])
            trend_factor = recent_avg / previous_avg if previous_avg > 0 else 1.0
        else:
            trend_factor = 1.0

        # Generate forecasts
        forecasts = {
            'next_7_days': round(weekly_avg * 7 * trend_factor, 2),
            'next_30_days': round(monthly_avg * 30 * trend_factor, 2),
            'next_90_days': round(monthly_avg * 90 * trend_factor, 2),
            'confidence_level': 'medium' if len(daily_revenues) >= 30 else 'low',
            'trend_direction': 'up' if trend_factor > 1.05 else 'down' if trend_factor < 0.95 else 'stable',
            'trend_factor': round(trend_factor, 3)
        }

        # AI-powered insights
        insights_prompt = f"""
        Analyze revenue forecasting data and provide insights:

        Historical daily average: ${monthly_avg:.2f}
        Recent trend factor: {trend_factor:.3f}
        Data points available: {len(daily_revenues)}

        30-day forecast: ${forecasts['next_30_days']:.2f}
        Monthly target: ${self.revenue_targets['monthly_total']:.2f}

        Provide:
        1. Forecast accuracy assessment
        2. Key factors that could impact forecast
        3. Specific recommendations to hit targets
        4. Risk factors to monitor

        Return as JSON.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": insights_prompt}],
                temperature=0.7
            )

            ai_insights = json.loads(response.choices[0].message.content)
            forecasts['ai_insights'] = ai_insights
        except:
            forecasts['ai_insights'] = {
                'accuracy': 'Data-driven forecast based on recent trends',
                'recommendations': ['Monitor daily progress toward targets', 'Focus on high-converting content']
            }

        return forecasts

    def _generate_optimization_recommendations(self) -> List[Dict]:
        """Generate AI-powered optimization recommendations"""

        # Get current performance data
        current_metrics = self._get_current_month_metrics()

        recommendations_prompt = f"""
        Analyze revenue performance and generate optimization recommendations:

        Current Month Metrics:
        {json.dumps(current_metrics, indent=2)}

        Revenue Targets:
        {json.dumps(self.revenue_targets, indent=2)}

        Generate 5-8 specific, actionable recommendations to:
        1. Increase revenue by 20-30%
        2. Improve conversion rates
        3. Optimize high-performing channels
        4. Address underperforming areas
        5. Reduce customer churn

        Each recommendation should include:
        - Priority level (high/medium/low)
        - Expected impact (revenue increase %)
        - Implementation difficulty (easy/medium/hard)
        - Timeline (days/weeks to implement)
        - Specific next steps

        Focus on AI/productivity niche micro-influencer strategies.
        Return as JSON array.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": recommendations_prompt}],
                temperature=0.7
            )

            recommendations = json.loads(response.choices[0].message.content)
            return recommendations if isinstance(recommendations, list) else recommendations.get('recommendations', [])
        except:
            # Fallback recommendations
            return [
                {
                    'title': 'Optimize high-performing content',
                    'description': 'Double down on content that drives the most revenue',
                    'priority': 'high',
                    'expected_impact': '15-25%',
                    'difficulty': 'easy',
                    'timeline': '1-2 weeks'
                },
                {
                    'title': 'Implement upsell sequences',
                    'description': 'Add automated upsells to increase average order value',
                    'priority': 'high',
                    'expected_impact': '20-35%',
                    'difficulty': 'medium',
                    'timeline': '2-3 weeks'
                }
            ]

    def predict_customer_lifetime_value(self, customer_id: str) -> Dict:
        """Predict customer lifetime value using AI"""

        # Get customer data
        customer_data = self._get_customer_data(customer_id)

        if not customer_data:
            return {'error': 'Customer not found'}

        # Historical purchase patterns
        purchase_history = self._get_customer_purchase_history(customer_id)

        # Simple LTV prediction based on patterns
        if len(purchase_history) >= 2:
            avg_order_value = np.mean([p['amount'] for p in purchase_history])
            purchase_frequency = len(purchase_history) / max((datetime.now() - datetime.fromisoformat(customer_data['acquisition_date'])).days / 30, 1)
            estimated_lifespan = 24  # 24 months average

            predicted_ltv = avg_order_value * purchase_frequency * estimated_lifespan
        else:
            # Use industry averages
            predicted_ltv = customer_data.get('avg_order_value', 100) * 3

        # Churn risk assessment
        days_since_last_purchase = (datetime.now() - datetime.fromisoformat(customer_data.get('last_purchase_date', datetime.now().isoformat()))).days
        churn_risk = min(days_since_last_purchase / 90, 1.0)  # Higher risk after 90 days

        return {
            'customer_id': customer_id,
            'current_ltv': customer_data.get('lifetime_value', 0),
            'predicted_ltv': round(predicted_ltv, 2),
            'ltv_growth_potential': round(predicted_ltv - customer_data.get('lifetime_value', 0), 2),
            'churn_risk': round(churn_risk, 3),
            'recommended_actions': self._get_ltv_optimization_actions(churn_risk, predicted_ltv)
        }

    def generate_revenue_report(self, report_type: str = "monthly") -> Dict:
        """Generate comprehensive revenue report"""

        if report_type == "monthly":
            start_date = datetime.now().replace(day=1)
            end_date = datetime.now()
        elif report_type == "quarterly":
            # Calculate quarter start
            current_quarter = (datetime.now().month - 1) // 3
            start_date = datetime.now().replace(month=current_quarter * 3 + 1, day=1)
            end_date = datetime.now()
        else:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

        report = {
            'report_type': report_type,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'executive_summary': self._generate_executive_summary(start_date, end_date),
            'detailed_metrics': self.generate_revenue_dashboard("30_days"),
            'goal_tracking': self._track_goal_progress(start_date, end_date),
            'comparative_analysis': self._generate_comparative_analysis(start_date, end_date),
            'action_items': self._generate_action_items(),
            'generated_at': datetime.now().isoformat()
        }

        return report

    # Helper methods
    def _save_revenue_transaction(self, transaction: RevenueMetric):
        """Save revenue transaction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO revenue_transactions
            (stream, amount, date, source, customer_id, product_id, attribution)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction.stream.value,
            transaction.amount,
            transaction.date.isoformat(),
            transaction.source,
            transaction.customer_id,
            transaction.product_id,
            json.dumps(transaction.attribution) if transaction.attribution else None
        ))

        conn.commit()
        conn.close()

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values"""
        if len(values) < 2:
            return "insufficient_data"

        recent_avg = np.mean(values[-len(values)//3:]) if len(values) >= 3 else values[-1]
        early_avg = np.mean(values[:len(values)//3]) if len(values) >= 3 else values[0]

        if recent_avg > early_avg * 1.1:
            return "strong_up"
        elif recent_avg > early_avg * 1.05:
            return "up"
        elif recent_avg < early_avg * 0.9:
            return "strong_down"
        elif recent_avg < early_avg * 0.95:
            return "down"
        else:
            return "stable"

    def _get_current_month_metrics(self) -> Dict:
        """Get current month performance metrics"""
        start_of_month = datetime.now().replace(day=1)
        return self._calculate_summary_metrics(start_of_month, datetime.now())

    # Additional helper methods would be implemented for:
    # - Customer data retrieval
    # - Goal tracking
    # - Comparative analysis
    # - Action item generation
    # - Real-time updates
    # - Alert monitoring


# Example usage
if __name__ == "__main__":
    config = {
        'openai_api_key': 'your-openai-key',
        'database_path': 'revenue_analytics.db'
    }

    dashboard = RevenueAnalyticsDashboard(config)

    # Track a revenue transaction
    transaction = RevenueMetric(
        stream=RevenueStream.COURSES,
        amount=297.0,
        date=datetime.now(),
        source='linkedin_organic',
        customer_id='customer_123',
        product_id='productivity_mastery',
        attribution={'content_id': 'post_456', 'platform': 'linkedin'}
    )

    result = dashboard.track_revenue_transaction(transaction)
    print("Transaction tracked:", result)

    # Generate dashboard
    dashboard_data = dashboard.generate_revenue_dashboard("30_days")
    print("Dashboard generated:", json.dumps(dashboard_data, indent=2, default=str))