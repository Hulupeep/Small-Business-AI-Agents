"""
Financial Analytics AI Agent

Provides comprehensive business intelligence, profitability analysis,
cost tracking, and financial optimization for food delivery operations.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TransactionType(Enum):
    REVENUE = "revenue"
    COST = "cost"
    REFUND = "refund"
    FEE = "fee"
    TIP = "tip"

class PlatformType(Enum):
    DIRECT = "direct"
    UBER_EATS = "uber_eats"
    DELIVEROO = "deliveroo"
    JUST_EAT = "just_eat"

class CostCategory(Enum):
    INGREDIENTS = "ingredients"
    LABOR = "labor"
    DELIVERY = "delivery"
    PLATFORM_FEES = "platform_fees"
    OVERHEAD = "overhead"
    MARKETING = "marketing"

@dataclass
class Transaction:
    id: str
    type: TransactionType
    amount: float
    currency: str
    category: Optional[CostCategory]
    platform: PlatformType
    order_id: Optional[str]
    driver_id: Optional[str]
    timestamp: datetime
    description: str
    tax_amount: float

@dataclass
class OrderFinancials:
    order_id: str
    gross_revenue: float
    net_revenue: float
    ingredient_cost: float
    labor_cost: float
    delivery_cost: float
    platform_fee: float
    profit: float
    profit_margin: float
    platform: PlatformType
    timestamp: datetime

@dataclass
class DriverPerformance:
    driver_id: str
    driver_name: str
    total_deliveries: int
    total_distance: float
    total_time: int  # minutes
    total_earnings: float
    average_rating: float
    fuel_efficiency: float
    orders_per_hour: float

@dataclass
class PlatformMetrics:
    platform: PlatformType
    total_orders: int
    gross_revenue: float
    commission_paid: float
    net_revenue: float
    average_order_value: float
    commission_rate: float

class FinancialAnalytics:
    """
    AI-powered financial analytics system that provides comprehensive
    business intelligence and profitability optimization.
    """

    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
        self.order_financials: Dict[str, OrderFinancials] = {}
        self.driver_performance: Dict[str, DriverPerformance] = {}
        self.platform_rates = {
            PlatformType.DIRECT: 0.0,
            PlatformType.UBER_EATS: 0.30,
            PlatformType.DELIVEROO: 0.28,
            PlatformType.JUST_EAT: 0.14
        }
        self.fixed_costs = {
            "rent": 2500.0,
            "insurance": 300.0,
            "utilities": 400.0,
            "software": 200.0
        }
        self.hourly_labor_rate = 12.50

    def record_transaction(self, transaction: Transaction) -> None:
        """Record a financial transaction"""
        self.transactions[transaction.id] = transaction
        logger.info(f"Recorded transaction: {transaction.type.value} €{transaction.amount}")

    async def analyze_order_profitability(self, order_data: Dict[str, Any]) -> OrderFinancials:
        """Analyze the profitability of a specific order"""
        order_id = order_data['order_id']
        gross_revenue = order_data['total_amount']
        platform = PlatformType(order_data.get('platform', 'direct'))

        # Calculate platform commission
        commission_rate = self.platform_rates[platform]
        platform_fee = gross_revenue * commission_rate

        # Calculate ingredient costs
        ingredient_cost = await self._calculate_ingredient_cost(order_data['items'])

        # Calculate labor cost (prep time * hourly rate)
        prep_time_hours = order_data.get('prep_time', 15) / 60
        labor_cost = prep_time_hours * self.hourly_labor_rate

        # Calculate delivery cost
        delivery_cost = await self._calculate_delivery_cost(order_data)

        # Calculate net revenue and profit
        net_revenue = gross_revenue - platform_fee
        total_costs = ingredient_cost + labor_cost + delivery_cost
        profit = net_revenue - total_costs
        profit_margin = (profit / gross_revenue) * 100 if gross_revenue > 0 else 0

        order_financials = OrderFinancials(
            order_id=order_id,
            gross_revenue=gross_revenue,
            net_revenue=net_revenue,
            ingredient_cost=ingredient_cost,
            labor_cost=labor_cost,
            delivery_cost=delivery_cost,
            platform_fee=platform_fee,
            profit=profit,
            profit_margin=profit_margin,
            platform=platform,
            timestamp=datetime.now()
        )

        self.order_financials[order_id] = order_financials

        # Record transactions
        await self._record_order_transactions(order_financials)

        logger.info(f"Order {order_id} profit: €{profit:.2f} ({profit_margin:.1f}%)")
        return order_financials

    async def _calculate_ingredient_cost(self, items: List[Dict[str, Any]]) -> float:
        """Calculate total ingredient cost for order items"""
        total_cost = 0.0

        # Sample ingredient costs (in real implementation, get from inventory system)
        ingredient_costs = {
            'pizza_margherita': 3.50,
            'pasta_carbonara': 2.80,
            'caesar_salad': 2.20,
            'chicken_burger': 4.20,
            'fries': 0.80
        }

        for item in items:
            item_id = item.get('item_id', '')
            quantity = item.get('quantity', 1)
            base_cost = ingredient_costs.get(item_id, 3.00)  # Default cost
            total_cost += base_cost * quantity

        return total_cost

    async def _calculate_delivery_cost(self, order_data: Dict[str, Any]) -> float:
        """Calculate delivery cost including driver payment and fuel"""
        delivery_distance = order_data.get('delivery_distance', 3.0)  # km

        # Base delivery fee + distance-based cost
        base_fee = 3.50
        distance_cost = delivery_distance * 0.50
        fuel_cost = delivery_distance * 0.15  # Fuel cost per km

        return base_fee + distance_cost + fuel_cost

    async def _record_order_transactions(self, order_financials: OrderFinancials) -> None:
        """Record all transactions related to an order"""
        # Revenue transaction
        revenue_transaction = Transaction(
            id=f"rev_{order_financials.order_id}",
            type=TransactionType.REVENUE,
            amount=order_financials.gross_revenue,
            currency="EUR",
            category=None,
            platform=order_financials.platform,
            order_id=order_financials.order_id,
            driver_id=None,
            timestamp=order_financials.timestamp,
            description=f"Order revenue from {order_financials.platform.value}",
            tax_amount=order_financials.gross_revenue * 0.23  # 23% VAT
        )

        # Platform fee transaction
        if order_financials.platform_fee > 0:
            fee_transaction = Transaction(
                id=f"fee_{order_financials.order_id}",
                type=TransactionType.FEE,
                amount=order_financials.platform_fee,
                currency="EUR",
                category=CostCategory.PLATFORM_FEES,
                platform=order_financials.platform,
                order_id=order_financials.order_id,
                driver_id=None,
                timestamp=order_financials.timestamp,
                description=f"Platform commission to {order_financials.platform.value}",
                tax_amount=0
            )
            self.record_transaction(fee_transaction)

        # Cost transactions
        cost_transactions = [
            (order_financials.ingredient_cost, CostCategory.INGREDIENTS, "Ingredient costs"),
            (order_financials.labor_cost, CostCategory.LABOR, "Kitchen labor"),
            (order_financials.delivery_cost, CostCategory.DELIVERY, "Delivery costs")
        ]

        for amount, category, description in cost_transactions:
            if amount > 0:
                cost_transaction = Transaction(
                    id=f"cost_{category.value}_{order_financials.order_id}",
                    type=TransactionType.COST,
                    amount=amount,
                    currency="EUR",
                    category=category,
                    platform=order_financials.platform,
                    order_id=order_financials.order_id,
                    driver_id=None,
                    timestamp=order_financials.timestamp,
                    description=description,
                    tax_amount=0
                )
                self.record_transaction(cost_transaction)

        self.record_transaction(revenue_transaction)

    def analyze_driver_performance(self, driver_data: List[Dict[str, Any]]) -> Dict[str, DriverPerformance]:
        """Analyze driver performance metrics"""
        driver_metrics = {}

        for data in driver_data:
            driver_id = data['driver_id']

            # Calculate performance metrics
            orders_per_hour = data['total_deliveries'] / (data['total_time'] / 60) if data['total_time'] > 0 else 0
            fuel_efficiency = data['total_distance'] / data.get('fuel_used', 1) if data.get('fuel_used', 0) > 0 else 0

            performance = DriverPerformance(
                driver_id=driver_id,
                driver_name=data['driver_name'],
                total_deliveries=data['total_deliveries'],
                total_distance=data['total_distance'],
                total_time=data['total_time'],
                total_earnings=data['total_earnings'],
                average_rating=data['average_rating'],
                fuel_efficiency=fuel_efficiency,
                orders_per_hour=orders_per_hour
            )

            driver_metrics[driver_id] = performance
            self.driver_performance[driver_id] = performance

        return driver_metrics

    def get_platform_analysis(self, period_days: int = 30) -> Dict[PlatformType, PlatformMetrics]:
        """Analyze performance by delivery platform"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        platform_data = {}

        for platform in PlatformType:
            # Get orders for this platform
            platform_orders = [
                order for order in self.order_financials.values()
                if order.platform == platform and order.timestamp >= cutoff_date
            ]

            if platform_orders:
                total_orders = len(platform_orders)
                gross_revenue = sum(order.gross_revenue for order in platform_orders)
                commission_paid = sum(order.platform_fee for order in platform_orders)
                net_revenue = sum(order.net_revenue for order in platform_orders)
                avg_order_value = gross_revenue / total_orders
                commission_rate = self.platform_rates[platform]

                metrics = PlatformMetrics(
                    platform=platform,
                    total_orders=total_orders,
                    gross_revenue=gross_revenue,
                    commission_paid=commission_paid,
                    net_revenue=net_revenue,
                    average_order_value=avg_order_value,
                    commission_rate=commission_rate
                )

                platform_data[platform] = metrics

        return platform_data

    def identify_peak_hours(self, period_days: int = 30) -> Dict[str, Any]:
        """Identify peak hours for revenue optimization"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        hourly_data = {}

        # Analyze orders by hour
        for order in self.order_financials.values():
            if order.timestamp >= cutoff_date:
                hour = order.timestamp.hour

                if hour not in hourly_data:
                    hourly_data[hour] = {
                        'order_count': 0,
                        'total_revenue': 0,
                        'total_profit': 0
                    }

                hourly_data[hour]['order_count'] += 1
                hourly_data[hour]['total_revenue'] += order.gross_revenue
                hourly_data[hour]['total_profit'] += order.profit

        # Calculate averages and identify peaks
        for hour_data in hourly_data.values():
            hour_data['avg_order_value'] = hour_data['total_revenue'] / hour_data['order_count']
            hour_data['avg_profit_per_order'] = hour_data['total_profit'] / hour_data['order_count']

        # Find peak hours
        if hourly_data:
            max_orders_hour = max(hourly_data, key=lambda x: hourly_data[x]['order_count'])
            max_revenue_hour = max(hourly_data, key=lambda x: hourly_data[x]['total_revenue'])
            max_profit_hour = max(hourly_data, key=lambda x: hourly_data[x]['total_profit'])

            return {
                'hourly_breakdown': hourly_data,
                'peak_orders_hour': max_orders_hour,
                'peak_revenue_hour': max_revenue_hour,
                'peak_profit_hour': max_profit_hour,
                'surge_recommendations': self._generate_surge_recommendations(hourly_data)
            }

        return {}

    def _generate_surge_recommendations(self, hourly_data: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate surge pricing recommendations"""
        recommendations = []

        if not hourly_data:
            return recommendations

        # Calculate average orders per hour
        avg_orders = sum(data['order_count'] for data in hourly_data.values()) / len(hourly_data)

        for hour, data in hourly_data.items():
            if data['order_count'] > avg_orders * 1.5:  # 50% above average
                surge_multiplier = min(1.5, data['order_count'] / avg_orders)

                recommendations.append({
                    'hour': hour,
                    'current_orders': data['order_count'],
                    'suggested_surge': round(surge_multiplier, 1),
                    'potential_revenue_increase': data['total_revenue'] * (surge_multiplier - 1)
                })

        return sorted(recommendations, key=lambda x: x['potential_revenue_increase'], reverse=True)

    def generate_daily_cash_reconciliation(self, date: datetime) -> Dict[str, Any]:
        """Generate daily cash reconciliation report"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        # Get all transactions for the day
        daily_transactions = [
            t for t in self.transactions.values()
            if start_date <= t.timestamp < end_date
        ]

        # Categorize transactions
        revenue_transactions = [t for t in daily_transactions if t.type == TransactionType.REVENUE]
        cost_transactions = [t for t in daily_transactions if t.type == TransactionType.COST]
        fee_transactions = [t for t in daily_transactions if t.type == TransactionType.FEE]

        # Calculate totals
        total_revenue = sum(t.amount for t in revenue_transactions)
        total_costs = sum(t.amount for t in cost_transactions)
        total_fees = sum(t.amount for t in fee_transactions)

        # Break down by payment method (cash vs card/digital)
        cash_revenue = sum(t.amount for t in revenue_transactions if t.platform == PlatformType.DIRECT)
        digital_revenue = total_revenue - cash_revenue

        # Calculate net profit
        net_profit = total_revenue - total_costs - total_fees

        # Get daily orders
        daily_orders = [
            o for o in self.order_financials.values()
            if start_date <= o.timestamp < end_date
        ]

        return {
            'date': date.strftime('%Y-%m-%d'),
            'total_orders': len(daily_orders),
            'gross_revenue': round(total_revenue, 2),
            'cash_revenue': round(cash_revenue, 2),
            'digital_revenue': round(digital_revenue, 2),
            'total_costs': round(total_costs, 2),
            'platform_fees': round(total_fees, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin': round((net_profit / total_revenue * 100), 2) if total_revenue > 0 else 0,
            'average_order_value': round(total_revenue / len(daily_orders), 2) if daily_orders else 0,
            'cost_breakdown': self._get_cost_breakdown(cost_transactions),
            'platform_breakdown': self._get_platform_breakdown(daily_orders)
        }

    def _get_cost_breakdown(self, cost_transactions: List[Transaction]) -> Dict[str, float]:
        """Break down costs by category"""
        breakdown = {}

        for transaction in cost_transactions:
            if transaction.category:
                category = transaction.category.value
                breakdown[category] = breakdown.get(category, 0) + transaction.amount

        return {k: round(v, 2) for k, v in breakdown.items()}

    def _get_platform_breakdown(self, daily_orders: List[OrderFinancials]) -> Dict[str, Dict[str, Any]]:
        """Break down revenue by platform"""
        breakdown = {}

        for order in daily_orders:
            platform = order.platform.value

            if platform not in breakdown:
                breakdown[platform] = {
                    'orders': 0,
                    'revenue': 0,
                    'profit': 0
                }

            breakdown[platform]['orders'] += 1
            breakdown[platform]['revenue'] += order.gross_revenue
            breakdown[platform]['profit'] += order.profit

        # Round values
        for platform_data in breakdown.values():
            platform_data['revenue'] = round(platform_data['revenue'], 2)
            platform_data['profit'] = round(platform_data['profit'], 2)

        return breakdown

    def forecast_revenue(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Forecast revenue for upcoming days"""
        # Get historical data for trend analysis
        historical_days = 30
        cutoff_date = datetime.now() - timedelta(days=historical_days)

        # Group orders by day
        daily_revenue = {}
        for order in self.order_financials.values():
            if order.timestamp >= cutoff_date:
                date_key = order.timestamp.date()
                daily_revenue[date_key] = daily_revenue.get(date_key, 0) + order.gross_revenue

        if len(daily_revenue) < 7:
            # Not enough data for reliable forecast
            return []

        # Calculate trend (simple linear regression)
        revenues = list(daily_revenue.values())
        avg_revenue = sum(revenues) / len(revenues)

        # Day of week patterns
        weekday_multipliers = {
            0: 0.8,  # Monday
            1: 0.9,  # Tuesday
            2: 1.0,  # Wednesday
            3: 1.1,  # Thursday
            4: 1.3,  # Friday
            5: 1.4,  # Saturday
            6: 1.2   # Sunday
        }

        forecast = []

        for i in range(days_ahead):
            future_date = datetime.now().date() + timedelta(days=i+1)
            weekday = future_date.weekday()

            # Apply day-of-week multiplier
            predicted_revenue = avg_revenue * weekday_multipliers[weekday]

            # Add some randomness for confidence intervals
            confidence_low = predicted_revenue * 0.8
            confidence_high = predicted_revenue * 1.2

            forecast.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_revenue': round(predicted_revenue, 2),
                'confidence_low': round(confidence_low, 2),
                'confidence_high': round(confidence_high, 2)
            })

        return forecast

    def get_comprehensive_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive financial analytics"""
        cutoff_date = datetime.now() - timedelta(days=period_days)

        # Filter recent data
        recent_orders = [
            order for order in self.order_financials.values()
            if order.timestamp >= cutoff_date
        ]

        if not recent_orders:
            return {}

        # Calculate key metrics
        total_orders = len(recent_orders)
        total_revenue = sum(order.gross_revenue for order in recent_orders)
        total_profit = sum(order.profit for order in recent_orders)
        avg_order_value = total_revenue / total_orders
        profit_margin = (total_profit / total_revenue) * 100

        # Platform analysis
        platform_metrics = self.get_platform_analysis(period_days)

        # Peak hours analysis
        peak_analysis = self.identify_peak_hours(period_days)

        # Driver performance
        top_drivers = sorted(
            self.driver_performance.values(),
            key=lambda x: x.orders_per_hour,
            reverse=True
        )[:5]

        return {
            'period_days': period_days,
            'summary': {
                'total_orders': total_orders,
                'total_revenue': round(total_revenue, 2),
                'total_profit': round(total_profit, 2),
                'profit_margin': round(profit_margin, 2),
                'average_order_value': round(avg_order_value, 2)
            },
            'platform_performance': {
                platform.value: asdict(metrics) for platform, metrics in platform_metrics.items()
            },
            'peak_hours': peak_analysis,
            'top_drivers': [asdict(driver) for driver in top_drivers],
            'revenue_forecast': self.forecast_revenue(7)
        }

# Example usage
if __name__ == "__main__":
    async def demo():
        analytics = FinancialAnalytics()

        # Sample order data
        order_data = {
            'order_id': 'ORD_001',
            'total_amount': 28.50,
            'platform': 'uber_eats',
            'items': [
                {'item_id': 'pizza_margherita', 'quantity': 1},
                {'item_id': 'fries', 'quantity': 1}
            ],
            'prep_time': 20,
            'delivery_distance': 4.5
        }

        # Analyze order profitability
        order_financials = await analytics.analyze_order_profitability(order_data)
        print(f"Order profit: €{order_financials.profit:.2f} ({order_financials.profit_margin:.1f}%)")

        # Sample driver data
        driver_data = [
            {
                'driver_id': 'driver_001',
                'driver_name': 'John Smith',
                'total_deliveries': 25,
                'total_distance': 125.0,
                'total_time': 300,  # 5 hours
                'total_earnings': 87.50,
                'average_rating': 4.8,
                'fuel_used': 8.5
            }
        ]

        # Analyze driver performance
        driver_metrics = analytics.analyze_driver_performance(driver_data)
        print(f"Driver performance: {driver_metrics}")

        # Generate daily reconciliation
        today_reconciliation = analytics.generate_daily_cash_reconciliation(datetime.now())
        print(f"Daily reconciliation: {today_reconciliation}")

        # Get comprehensive analytics
        comprehensive = analytics.get_comprehensive_analytics(30)
        print(f"Comprehensive analytics: {comprehensive}")

    asyncio.run(demo())