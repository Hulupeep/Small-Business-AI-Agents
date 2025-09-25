"""
Sales Analytics & Insights Agent

Analyzes sales data, identifies trends, tracks performance metrics,
and provides actionable insights for inventory and business decisions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from collections import defaultdict
import statistics

@dataclass
class SalesMetric:
    """Represents a sales performance metric."""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    trend: str  # "up", "down", "stable"
    target_value: Optional[float] = None
    period: str = "daily"

@dataclass
class ProductPerformance:
    """Represents individual product performance data."""
    sku: str
    name: str
    category: str
    total_revenue: float
    units_sold: int
    profit_margin: float
    inventory_turns: float
    days_in_stock: int
    last_sale_date: Optional[datetime] = None
    performance_score: float = 0.0

@dataclass
class CustomerInsight:
    """Represents customer behavior insights."""
    customer_segment: str
    avg_transaction_value: float
    visit_frequency: float
    lifetime_value: float
    preferred_categories: List[str]
    churn_risk: float  # 0-1 probability
    segment_size: int

@dataclass
class SeasonalTrend:
    """Represents seasonal sales patterns."""
    period: str  # "spring", "summer", "fall", "winter", "holiday"
    revenue_multiplier: float
    top_categories: List[str]
    peak_months: List[str]
    recommended_inventory_increase: float

class AnalyticsEngine:
    """
    AI-powered sales analytics and business intelligence system.

    Key Features:
    - Real-time sales performance tracking
    - Product performance analysis and dead stock identification
    - Customer behavior and lifetime value analysis
    - Seasonal trend prediction and planning
    - Inventory optimization recommendations
    - Profit margin analysis and pricing insights
    """

    def __init__(self, sales_file: str = "data/sales.csv",
                 customers_file: str = "data/customers.csv",
                 inventory_file: str = "data/inventory.csv"):
        self.sales_file = sales_file
        self.customers_file = customers_file
        self.inventory_file = inventory_file

        self.sales_data = self._load_sales_data()
        self.customer_data = self._load_customer_data()
        self.inventory_data = self._load_inventory_data()

        self.performance_targets = {
            'daily_revenue': 800,
            'avg_transaction_value': 95,
            'conversion_rate': 0.25,
            'inventory_turnover': 6,
            'gross_margin': 0.60
        }

    def _load_sales_data(self) -> pd.DataFrame:
        """Load and process sales data."""
        try:
            df = pd.read_csv(self.sales_file)
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.month
            df['day_of_week'] = df['date'].dt.day_name()
            df['hour'] = df['date'].dt.hour
            return df
        except FileNotFoundError:
            print(f"Sales file {self.sales_file} not found. Using sample data.")
            return self._generate_sample_sales_data()

    def _load_customer_data(self) -> pd.DataFrame:
        """Load customer data."""
        try:
            df = pd.read_csv(self.customers_file)
            df['join_date'] = pd.to_datetime(df['join_date'])
            return df
        except FileNotFoundError:
            return pd.DataFrame()

    def _load_inventory_data(self) -> pd.DataFrame:
        """Load inventory data."""
        try:
            df = pd.read_csv(self.inventory_file)
            return df
        except FileNotFoundError:
            return pd.DataFrame()

    def _generate_sample_sales_data(self) -> pd.DataFrame:
        """Generate sample sales data for demonstration."""
        # Create 90 days of sample sales data
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        sample_data = []

        products = [
            {"sku": "DRESS001", "name": "Floral Midi Dress", "category": "dresses", "price": 89.99, "cost": 35},
            {"sku": "TOP001", "name": "Silk Blouse", "category": "tops", "price": 69.99, "cost": 25},
            {"sku": "JEANS001", "name": "High-waist Jeans", "category": "bottoms", "price": 79.99, "cost": 30},
            {"sku": "BAG001", "name": "Leather Handbag", "category": "accessories", "price": 129.99, "cost": 50},
            {"sku": "SHOES001", "name": "Block Heels", "category": "shoes", "price": 99.99, "cost": 40}
        ]

        for date in dates:
            # Simulate varying daily sales (weekends higher)
            base_sales = 8 if date.weekday() < 5 else 12
            daily_sales = np.random.poisson(base_sales)

            for _ in range(daily_sales):
                product = np.random.choice(products)
                customer_id = f"CUST{np.random.randint(1, 200):03d}"

                sample_data.append({
                    'date': date,
                    'customer_id': customer_id,
                    'sku': product['sku'],
                    'product_name': product['name'],
                    'category': product['category'],
                    'quantity': 1,
                    'unit_price': product['price'],
                    'total_amount': product['price'],
                    'cost': product['cost'],
                    'profit': product['price'] - product['cost']
                })

        df = pd.DataFrame(sample_data)
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour

        return df

    def calculate_daily_metrics(self, target_date: datetime = None) -> Dict[str, SalesMetric]:
        """Calculate key daily performance metrics."""
        if target_date is None:
            target_date = datetime.now().date()

        # Current day data
        current_day = self.sales_data[self.sales_data['date'].dt.date == target_date]

        # Previous day data for comparison
        previous_date = target_date - timedelta(days=1)
        previous_day = self.sales_data[self.sales_data['date'].dt.date == previous_date]

        metrics = {}

        # Daily Revenue
        current_revenue = current_day['total_amount'].sum()
        previous_revenue = previous_day['total_amount'].sum()
        revenue_change = ((current_revenue - previous_revenue) / max(previous_revenue, 1)) * 100

        metrics['daily_revenue'] = SalesMetric(
            metric_name="Daily Revenue",
            current_value=current_revenue,
            previous_value=previous_revenue,
            change_percentage=revenue_change,
            trend="up" if revenue_change > 5 else "down" if revenue_change < -5 else "stable",
            target_value=self.performance_targets['daily_revenue']
        )

        # Average Transaction Value
        current_atv = current_day['total_amount'].mean() if len(current_day) > 0 else 0
        previous_atv = previous_day['total_amount'].mean() if len(previous_day) > 0 else 0
        atv_change = ((current_atv - previous_atv) / max(previous_atv, 1)) * 100

        metrics['avg_transaction_value'] = SalesMetric(
            metric_name="Average Transaction Value",
            current_value=current_atv,
            previous_value=previous_atv,
            change_percentage=atv_change,
            trend="up" if atv_change > 5 else "down" if atv_change < -5 else "stable",
            target_value=self.performance_targets['avg_transaction_value']
        )

        # Transaction Count
        current_transactions = len(current_day)
        previous_transactions = len(previous_day)
        transaction_change = ((current_transactions - previous_transactions) / max(previous_transactions, 1)) * 100

        metrics['transaction_count'] = SalesMetric(
            metric_name="Transaction Count",
            current_value=current_transactions,
            previous_value=previous_transactions,
            change_percentage=transaction_change,
            trend="up" if transaction_change > 5 else "down" if transaction_change < -5 else "stable"
        )

        return metrics

    def analyze_product_performance(self, days_back: int = 30) -> List[ProductPerformance]:
        """Analyze individual product performance over specified period."""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_sales = self.sales_data[self.sales_data['date'] >= cutoff_date]

        # Group by product
        product_stats = recent_sales.groupby(['sku', 'product_name', 'category']).agg({
            'total_amount': 'sum',
            'quantity': 'sum',
            'profit': 'sum',
            'date': 'max'
        }).reset_index()

        performances = []
        for _, row in product_stats.iterrows():
            # Calculate performance score (revenue + profit margin + recency)
            revenue_score = min(row['total_amount'] / 1000, 1) * 40  # Max 40 points
            profit_margin = (row['profit'] / row['total_amount']) if row['total_amount'] > 0 else 0
            margin_score = profit_margin * 30  # Max 30 points

            # Recency score (more recent sales = higher score)
            days_since_sale = (datetime.now() - row['date']).days
            recency_score = max(0, 30 - days_since_sale) if days_since_sale <= 30 else 0

            performance_score = revenue_score + margin_score + recency_score

            performance = ProductPerformance(
                sku=row['sku'],
                name=row['product_name'],
                category=row['category'],
                total_revenue=row['total_amount'],
                units_sold=row['quantity'],
                profit_margin=profit_margin,
                inventory_turns=row['quantity'] / max(self._get_avg_inventory(row['sku']), 1),
                days_in_stock=days_back,
                last_sale_date=row['date'],
                performance_score=performance_score
            )
            performances.append(performance)

        # Sort by performance score
        performances.sort(key=lambda x: x.performance_score, reverse=True)
        return performances

    def _get_avg_inventory(self, sku: str) -> int:
        """Get average inventory level for a product (mock implementation)."""
        # In production, this would calculate from inventory history
        return 10  # Default average inventory

    def identify_dead_stock(self, days_without_sale: int = 30) -> List[Dict]:
        """Identify products that haven't sold in specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_without_sale)

        # Get all products that have sold
        sold_products = set(self.sales_data['sku'].unique())

        # Get recent sales
        recent_sales = self.sales_data[self.sales_data['date'] >= cutoff_date]
        recently_sold = set(recent_sales['sku'].unique())

        # Products that exist but haven't sold recently
        dead_stock_skus = sold_products - recently_sold

        dead_stock = []
        for sku in dead_stock_skus:
            product_sales = self.sales_data[self.sales_data['sku'] == sku]
            last_sale = product_sales['date'].max()

            # Get product details from last sale
            last_sale_row = product_sales[product_sales['date'] == last_sale].iloc[0]

            dead_stock.append({
                'sku': sku,
                'name': last_sale_row['product_name'],
                'category': last_sale_row['category'],
                'last_sale_date': last_sale,
                'days_since_sale': (datetime.now() - last_sale).days,
                'total_historical_revenue': product_sales['total_amount'].sum(),
                'recommendation': self._get_dead_stock_recommendation(
                    sku, (datetime.now() - last_sale).days
                )
            })

        return sorted(dead_stock, key=lambda x: x['days_since_sale'], reverse=True)

    def _get_dead_stock_recommendation(self, sku: str, days_since_sale: int) -> str:
        """Generate recommendation for dead stock items."""
        if days_since_sale > 90:
            return "Consider clearance sale (50%+ discount)"
        elif days_since_sale > 60:
            return "Mark down 30-40% or bundle with popular items"
        elif days_since_sale > 45:
            return "Promote on social media or offer 20% discount"
        else:
            return "Monitor for another 2 weeks, then consider promotion"

    def analyze_customer_segments(self) -> List[CustomerInsight]:
        """Analyze customer behavior and create actionable segments."""
        if self.sales_data.empty:
            return []

        # Calculate customer metrics
        customer_metrics = self.sales_data.groupby('customer_id').agg({
            'total_amount': ['sum', 'mean', 'count'],
            'date': ['min', 'max'],
            'category': lambda x: list(x.value_counts().head(3).index)
        }).reset_index()

        # Flatten column names
        customer_metrics.columns = [
            'customer_id', 'total_spent', 'avg_transaction', 'transaction_count',
            'first_purchase', 'last_purchase', 'top_categories'
        ]

        # Calculate additional metrics
        customer_metrics['days_active'] = (
            customer_metrics['last_purchase'] - customer_metrics['first_purchase']
        ).dt.days + 1

        customer_metrics['visit_frequency'] = (
            customer_metrics['transaction_count'] / customer_metrics['days_active']
        ).fillna(0)

        # Segment customers
        segments = []

        # VIP Customers (top 10% by spending)
        vip_threshold = customer_metrics['total_spent'].quantile(0.9)
        vip_customers = customer_metrics[customer_metrics['total_spent'] >= vip_threshold]

        if not vip_customers.empty:
            segments.append(CustomerInsight(
                customer_segment="VIP Customers",
                avg_transaction_value=vip_customers['avg_transaction'].mean(),
                visit_frequency=vip_customers['visit_frequency'].mean(),
                lifetime_value=vip_customers['total_spent'].mean(),
                preferred_categories=self._get_segment_top_categories(vip_customers),
                churn_risk=self._calculate_churn_risk(vip_customers),
                segment_size=len(vip_customers)
            ))

        # Regular Customers (middle 60%)
        regular_customers = customer_metrics[
            (customer_metrics['total_spent'] >= customer_metrics['total_spent'].quantile(0.3)) &
            (customer_metrics['total_spent'] < customer_metrics['total_spent'].quantile(0.9))
        ]

        if not regular_customers.empty:
            segments.append(CustomerInsight(
                customer_segment="Regular Customers",
                avg_transaction_value=regular_customers['avg_transaction'].mean(),
                visit_frequency=regular_customers['visit_frequency'].mean(),
                lifetime_value=regular_customers['total_spent'].mean(),
                preferred_categories=self._get_segment_top_categories(regular_customers),
                churn_risk=self._calculate_churn_risk(regular_customers),
                segment_size=len(regular_customers)
            ))

        # At-Risk Customers (haven't purchased in 60+ days)
        recent_date = datetime.now() - timedelta(days=60)
        at_risk = customer_metrics[customer_metrics['last_purchase'] < recent_date]

        if not at_risk.empty:
            segments.append(CustomerInsight(
                customer_segment="At-Risk Customers",
                avg_transaction_value=at_risk['avg_transaction'].mean(),
                visit_frequency=at_risk['visit_frequency'].mean(),
                lifetime_value=at_risk['total_spent'].mean(),
                preferred_categories=self._get_segment_top_categories(at_risk),
                churn_risk=0.8,  # High churn risk
                segment_size=len(at_risk)
            ))

        return segments

    def _get_segment_top_categories(self, segment_df: pd.DataFrame) -> List[str]:
        """Get top categories for a customer segment."""
        all_categories = []
        for categories in segment_df['top_categories']:
            all_categories.extend(categories)

        if not all_categories:
            return []

        category_counts = pd.Series(all_categories).value_counts()
        return category_counts.head(3).index.tolist()

    def _calculate_churn_risk(self, segment_df: pd.DataFrame) -> float:
        """Calculate churn risk for a customer segment."""
        now = datetime.now()
        recent_threshold = now - timedelta(days=45)

        recent_purchases = segment_df[segment_df['last_purchase'] >= recent_threshold]
        churn_risk = 1 - (len(recent_purchases) / len(segment_df))

        return round(churn_risk, 2)

    def analyze_peak_hours(self) -> Dict:
        """Analyze peak shopping hours and days."""
        if self.sales_data.empty:
            return {}

        # Hour analysis
        hourly_sales = self.sales_data.groupby('hour').agg({
            'total_amount': 'sum',
            'customer_id': 'count'
        }).reset_index()

        hourly_sales['avg_transaction'] = (
            hourly_sales['total_amount'] / hourly_sales['customer_id']
        )

        # Day of week analysis
        daily_sales = self.sales_data.groupby('day_of_week').agg({
            'total_amount': 'sum',
            'customer_id': 'count'
        }).reset_index()

        # Sort days properly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_sales['day_order'] = daily_sales['day_of_week'].map(
            {day: i for i, day in enumerate(day_order)}
        )
        daily_sales = daily_sales.sort_values('day_order')

        return {
            'peak_hours': {
                'best_revenue_hour': int(hourly_sales.loc[hourly_sales['total_amount'].idxmax(), 'hour']),
                'busiest_hour': int(hourly_sales.loc[hourly_sales['customer_id'].idxmax(), 'hour']),
                'best_atv_hour': int(hourly_sales.loc[hourly_sales['avg_transaction'].idxmax(), 'hour']),
                'hourly_breakdown': hourly_sales.to_dict('records')
            },
            'peak_days': {
                'best_revenue_day': daily_sales.loc[daily_sales['total_amount'].idxmax(), 'day_of_week'],
                'busiest_day': daily_sales.loc[daily_sales['customer_id'].idxmax(), 'day_of_week'],
                'daily_breakdown': daily_sales[['day_of_week', 'total_amount', 'customer_id']].to_dict('records')
            },
            'staffing_recommendations': self._generate_staffing_recommendations(hourly_sales, daily_sales)
        }

    def _generate_staffing_recommendations(self, hourly_sales: pd.DataFrame,
                                         daily_sales: pd.DataFrame) -> List[str]:
        """Generate staffing recommendations based on peak analysis."""
        recommendations = []

        # Find peak hours
        peak_hour = hourly_sales.loc[hourly_sales['customer_id'].idxmax(), 'hour']
        recommendations.append(f"Schedule extra staff around {peak_hour}:00-{peak_hour+2}:00")

        # Find peak days
        peak_day = daily_sales.loc[daily_sales['customer_id'].idxmax(), 'day_of_week']
        recommendations.append(f"Ensure full staffing on {peak_day}s")

        # Low traffic recommendations
        min_hour = hourly_sales.loc[hourly_sales['customer_id'].idxmin(), 'hour']
        recommendations.append(f"Consider reduced hours or inventory tasks at {min_hour}:00")

        return recommendations

    def predict_seasonal_trends(self) -> List[SeasonalTrend]:
        """Predict seasonal trends based on historical data."""
        if self.sales_data.empty:
            return []

        # Group by month
        monthly_sales = self.sales_data.groupby('month').agg({
            'total_amount': 'sum',
            'category': lambda x: list(x.value_counts().head(3).index)
        }).reset_index()

        # Calculate seasonal patterns
        avg_monthly_revenue = monthly_sales['total_amount'].mean()
        trends = []

        season_months = {
            'Spring': [3, 4, 5],
            'Summer': [6, 7, 8],
            'Fall': [9, 10, 11],
            'Winter': [12, 1, 2]
        }

        for season, months in season_months.items():
            season_data = monthly_sales[monthly_sales['month'].isin(months)]

            if not season_data.empty:
                season_revenue = season_data['total_amount'].sum()
                revenue_multiplier = season_revenue / (avg_monthly_revenue * len(months))

                # Get top categories for this season
                all_categories = []
                for categories in season_data['category']:
                    all_categories.extend(categories)

                top_categories = pd.Series(all_categories).value_counts().head(3).index.tolist()

                trends.append(SeasonalTrend(
                    period=season,
                    revenue_multiplier=revenue_multiplier,
                    top_categories=top_categories,
                    peak_months=[datetime(2024, m, 1).strftime('%B') for m in months],
                    recommended_inventory_increase=max(0, (revenue_multiplier - 1) * 100)
                ))

        return sorted(trends, key=lambda x: x.revenue_multiplier, reverse=True)

    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive business analytics report."""
        today = datetime.now().date()

        report = {
            'report_date': today.strftime('%Y-%m-%d'),
            'daily_metrics': self.calculate_daily_metrics(today),
            'product_performance': {
                'top_performers': self.analyze_product_performance(30)[:5],
                'dead_stock': self.identify_dead_stock(30)
            },
            'customer_insights': self.analyze_customer_segments(),
            'operational_insights': self.analyze_peak_hours(),
            'seasonal_trends': self.predict_seasonal_trends(),
            'recommendations': self._generate_actionable_recommendations()
        }

        return report

    def _generate_actionable_recommendations(self) -> List[str]:
        """Generate actionable business recommendations based on analysis."""
        recommendations = []

        # Product recommendations
        dead_stock = self.identify_dead_stock(30)
        if dead_stock:
            recommendations.append(
                f"Consider promotions for {len(dead_stock)} slow-moving items to clear inventory"
            )

        # Customer recommendations
        segments = self.analyze_customer_segments()
        at_risk_segment = next((s for s in segments if s.customer_segment == "At-Risk Customers"), None)
        if at_risk_segment and at_risk_segment.segment_size > 0:
            recommendations.append(
                f"Launch win-back campaign for {at_risk_segment.segment_size} at-risk customers"
            )

        # Operational recommendations
        peak_analysis = self.analyze_peak_hours()
        if peak_analysis:
            recommendations.append(
                f"Optimize staffing for peak hour ({peak_analysis['peak_hours']['busiest_hour']}:00)"
            )

        # Seasonal recommendations
        trends = self.predict_seasonal_trends()
        if trends:
            best_season = trends[0]
            recommendations.append(
                f"Prepare for {best_season.period} season - increase {best_season.top_categories[0]} inventory by {best_season.recommended_inventory_increase:.0f}%"
            )

        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Initialize analytics engine
    analytics = AnalyticsEngine()

    print("=== Retail Analytics Dashboard ===\n")

    # Daily metrics
    daily_metrics = analytics.calculate_daily_metrics()
    print("DAILY PERFORMANCE:")
    for metric_name, metric in daily_metrics.items():
        trend_icon = "📈" if metric.trend == "up" else "📉" if metric.trend == "down" else "➡️"
        print(f"{metric.metric_name}: €{metric.current_value:.2f} {trend_icon} ({metric.change_percentage:.1f}%)")

    # Product performance
    print(f"\nTOP PERFORMING PRODUCTS:")
    top_products = analytics.analyze_product_performance(30)[:5]
    for i, product in enumerate(top_products, 1):
        print(f"{i}. {product.name} - €{product.total_revenue:.2f} revenue, {product.units_sold} units")

    # Dead stock
    print(f"\nDEAD STOCK ALERTS:")
    dead_stock = analytics.identify_dead_stock(30)[:3]
    for item in dead_stock:
        print(f"- {item['name']}: {item['days_since_sale']} days since sale - {item['recommendation']}")

    # Customer segments
    print(f"\nCUSTOMER SEGMENTS:")
    segments = analytics.analyze_customer_segments()
    for segment in segments:
        print(f"- {segment.customer_segment}: {segment.segment_size} customers, €{segment.avg_transaction_value:.2f} ATV")

    # Peak hours
    print(f"\nOPERATIONAL INSIGHTS:")
    peak_analysis = analytics.analyze_peak_hours()
    if peak_analysis:
        print(f"Peak hour: {peak_analysis['peak_hours']['busiest_hour']}:00")
        print(f"Best revenue day: {peak_analysis['peak_days']['best_revenue_day']}")

    # Recommendations
    print(f"\nACTIONABLE RECOMMENDATIONS:")
    recommendations = analytics._generate_actionable_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    # Seasonal trends
    print(f"\nSEASONAL TRENDS:")
    trends = analytics.predict_seasonal_trends()
    for trend in trends[:2]:
        print(f"- {trend.period}: {trend.revenue_multiplier:.2f}x revenue, top category: {trend.top_categories[0] if trend.top_categories else 'N/A'}")