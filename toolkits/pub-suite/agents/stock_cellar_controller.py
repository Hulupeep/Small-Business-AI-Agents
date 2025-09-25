"""
Stock & Cellar Controller Agent
Optimizes inventory and ensures perfect pints through intelligent monitoring
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class BeerLineStatus(Enum):
    OPTIMAL = "optimal"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"

class StockStatus(Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ORDERED = "ordered"

@dataclass
class BeerLine:
    line_id: str
    beer_name: str
    keg_size: float  # liters
    current_volume: float
    pressure: float  # PSI
    temperature: float  # Celsius
    flow_rate: float  # ml/second
    last_cleaned: datetime
    status: BeerLineStatus = BeerLineStatus.OPTIMAL
    quality_score: float = 10.0

@dataclass
class StockItem:
    item_id: str
    name: str
    category: str
    current_stock: int
    min_threshold: int
    max_capacity: int
    unit_cost: float
    supplier: str
    last_delivery: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    status: StockStatus = StockStatus.IN_STOCK

@dataclass
class WastageRecord:
    item_id: str
    quantity: float
    reason: str
    cost_impact: float
    timestamp: datetime
    staff_member: str

class StockCellarController:
    """AI agent for cellar management and inventory optimization"""

    def __init__(self, pub_config: Dict):
        self.pub_config = pub_config
        self.beer_lines: Dict[str, BeerLine] = self._initialize_beer_lines()
        self.stock_items: Dict[str, StockItem] = self._initialize_stock()
        self.wastage_records: List[WastageRecord] = []
        self.consumption_patterns = ConsumptionAnalyzer()
        self.supplier_manager = SupplierManager()

    def _initialize_beer_lines(self) -> Dict[str, BeerLine]:
        """Initialize beer line monitoring configuration"""
        lines = {}
        beer_config = self.pub_config.get('beer_lines', [])

        for config in beer_config:
            line = BeerLine(
                line_id=config['line_id'],
                beer_name=config['beer_name'],
                keg_size=config.get('keg_size', 50.0),  # Standard 50L keg
                current_volume=config.get('current_volume', 50.0),
                pressure=config.get('pressure', 12.0),
                temperature=config.get('temperature', 4.0),
                flow_rate=config.get('flow_rate', 25.0),
                last_cleaned=datetime.now() - timedelta(days=1)
            )
            lines[config['line_id']] = line

        return lines

    def _initialize_stock(self) -> Dict[str, StockItem]:
        """Initialize stock monitoring"""
        stock = {}
        stock_config = self.pub_config.get('stock_items', [])

        for config in stock_config:
            item = StockItem(
                item_id=config['item_id'],
                name=config['name'],
                category=config['category'],
                current_stock=config.get('current_stock', 0),
                min_threshold=config.get('min_threshold', 5),
                max_capacity=config.get('max_capacity', 50),
                unit_cost=config.get('unit_cost', 0.0),
                supplier=config.get('supplier', '')
            )
            stock[config['item_id']] = item

        return stock

    async def monitor_beer_lines(self) -> Dict:
        """Continuous monitoring of beer line quality and status"""
        line_status = {}

        for line_id, line in self.beer_lines.items():
            # Simulate sensor readings (in real implementation, these come from IoT sensors)
            current_readings = await self._get_line_readings(line_id)

            # Update line data
            line.pressure = current_readings['pressure']
            line.temperature = current_readings['temperature']
            line.flow_rate = current_readings['flow_rate']
            line.current_volume = current_readings['volume']

            # Analyze line status
            status_analysis = await self._analyze_line_status(line)
            line.status = status_analysis['status']
            line.quality_score = status_analysis['quality_score']

            line_status[line_id] = {
                'beer_name': line.beer_name,
                'status': line.status.value,
                'quality_score': line.quality_score,
                'volume_remaining': line.current_volume,
                'estimated_empty_time': await self._estimate_keg_empty_time(line),
                'recommendations': status_analysis['recommendations']
            }

        return {
            'timestamp': datetime.now(),
            'lines': line_status,
            'overall_status': await self._calculate_overall_cellar_status()
        }

    async def predict_keg_changes(self) -> Dict:
        """Predict when kegs need changing and optimize replacement timing"""
        predictions = {}

        for line_id, line in self.beer_lines.items():
            if line.current_volume <= 0:
                predictions[line_id] = {
                    'status': 'immediate_change_required',
                    'estimated_time': datetime.now(),
                    'priority': 'critical'
                }
                continue

            # Calculate consumption rate based on historical data
            consumption_rate = await self.consumption_patterns.get_consumption_rate(
                line.beer_name,
                datetime.now().hour,
                datetime.now().weekday()
            )

            # Estimate when keg will be empty
            estimated_empty_time = await self._estimate_keg_empty_time(line)

            # Determine optimal change time (before it's completely empty)
            optimal_change_time = estimated_empty_time - timedelta(minutes=15)

            predictions[line_id] = {
                'beer_name': line.beer_name,
                'current_volume': line.current_volume,
                'consumption_rate': consumption_rate,  # ml/minute
                'estimated_empty_time': estimated_empty_time,
                'optimal_change_time': optimal_change_time,
                'priority': self._determine_change_priority(line, estimated_empty_time)
            }

        return {
            'predictions': predictions,
            'change_schedule': await self._optimize_change_schedule(predictions)
        }

    async def manage_inventory_tracking(self) -> Dict:
        """Real-time inventory tracking with smart ordering"""
        inventory_status = {}

        for item_id, item in self.stock_items.items():
            # Check current stock levels
            current_status = await self._assess_stock_status(item)
            item.status = current_status

            # Calculate reorder point based on consumption patterns
            reorder_point = await self._calculate_reorder_point(item)

            # Generate order recommendation if needed
            order_recommendation = None
            if item.current_stock <= reorder_point:
                order_recommendation = await self._generate_order_recommendation(item)

            inventory_status[item_id] = {
                'name': item.name,
                'category': item.category,
                'current_stock': item.current_stock,
                'status': item.status.value,
                'reorder_point': reorder_point,
                'days_until_empty': await self._calculate_days_until_empty(item),
                'order_recommendation': order_recommendation
            }

        return {
            'timestamp': datetime.now(),
            'inventory': inventory_status,
            'total_value': await self._calculate_total_inventory_value(),
            'low_stock_alerts': await self._get_low_stock_alerts()
        }

    async def automate_supplier_orders(self) -> Dict:
        """Automated supplier ordering based on intelligent predictions"""
        order_recommendations = []

        for item_id, item in self.stock_items.items():
            if item.status in [StockStatus.LOW_STOCK, StockStatus.OUT_OF_STOCK]:
                # Generate order recommendation
                recommendation = await self._generate_order_recommendation(item)

                if recommendation:
                    # Check supplier availability and pricing
                    supplier_info = await self.supplier_manager.check_availability(
                        item.supplier, item_id, recommendation['quantity']
                    )

                    if supplier_info['available']:
                        order_recommendations.append({
                            'item_id': item_id,
                            'item_name': item.name,
                            'supplier': item.supplier,
                            'quantity': recommendation['quantity'],
                            'unit_cost': supplier_info['unit_cost'],
                            'total_cost': supplier_info['total_cost'],
                            'delivery_date': supplier_info['delivery_date'],
                            'urgency': recommendation['urgency']
                        })

        # Auto-approve low-cost, routine orders
        auto_approved = []
        manual_review = []

        for order in order_recommendations:
            if (order['total_cost'] <= self.pub_config.get('auto_order_limit', 200) and
                order['urgency'] != 'critical'):
                auto_approved.append(order)
                await self._submit_order(order)
            else:
                manual_review.append(order)

        return {
            'auto_approved_orders': auto_approved,
            'manual_review_required': manual_review,
            'total_auto_approved_value': sum(o['total_cost'] for o in auto_approved)
        }

    async def track_wastage_analytics(self) -> Dict:
        """Comprehensive wastage tracking and analysis"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Calculate wastage by time period
        daily_wastage = await self._calculate_wastage(today, today)
        weekly_wastage = await self._calculate_wastage(week_ago, today)
        monthly_wastage = await self._calculate_wastage(month_ago, today)

        # Analyze wastage by category
        wastage_by_category = await self._analyze_wastage_by_category(week_ago, today)

        # Identify top wastage items
        top_wastage_items = await self._identify_top_wastage_items(week_ago, today)

        # Generate reduction recommendations
        reduction_recommendations = await self._generate_wastage_reduction_tips()

        return {
            'daily_wastage': daily_wastage,
            'weekly_wastage': weekly_wastage,
            'monthly_wastage': monthly_wastage,
            'wastage_by_category': wastage_by_category,
            'top_wastage_items': top_wastage_items,
            'reduction_recommendations': reduction_recommendations,
            'cost_impact': {
                'daily': daily_wastage['total_cost'],
                'weekly': weekly_wastage['total_cost'],
                'monthly': monthly_wastage['total_cost']
            }
        }

    async def _get_line_readings(self, line_id: str) -> Dict:
        """Simulate getting readings from beer line sensors"""
        # In real implementation, this would interface with IoT sensors
        import random

        line = self.beer_lines[line_id]

        # Simulate normal fluctuations
        return {
            'pressure': line.pressure + random.uniform(-0.5, 0.5),
            'temperature': line.temperature + random.uniform(-0.2, 0.2),
            'flow_rate': line.flow_rate + random.uniform(-2, 2),
            'volume': max(0, line.current_volume - random.uniform(0, 0.5))  # Gradual decrease
        }

    async def _analyze_line_status(self, line: BeerLine) -> Dict:
        """Analyze beer line status and quality"""
        status = BeerLineStatus.OPTIMAL
        quality_score = 10.0
        recommendations = []

        # Check temperature (optimal: 3-5°C)
        if line.temperature < 2 or line.temperature > 6:
            status = BeerLineStatus.WARNING
            quality_score -= 2
            recommendations.append(f"Temperature outside optimal range: {line.temperature}°C")

        # Check pressure (optimal: 10-14 PSI for most beers)
        if line.pressure < 8 or line.pressure > 16:
            status = BeerLineStatus.WARNING
            quality_score -= 1.5
            recommendations.append(f"Pressure outside optimal range: {line.pressure} PSI")

        # Check volume
        if line.current_volume <= 2:
            status = BeerLineStatus.CRITICAL
            quality_score -= 3
            recommendations.append("Keg nearly empty - prepare for change")

        # Check cleaning schedule
        days_since_clean = (datetime.now() - line.last_cleaned).days
        if days_since_clean >= 7:
            status = BeerLineStatus.WARNING
            quality_score -= 2
            recommendations.append(f"Line cleaning overdue by {days_since_clean - 7} days")

        return {
            'status': status,
            'quality_score': max(0, quality_score),
            'recommendations': recommendations
        }

    async def _estimate_keg_empty_time(self, line: BeerLine) -> datetime:
        """Estimate when keg will be empty based on consumption patterns"""
        if line.current_volume <= 0:
            return datetime.now()

        # Get current consumption rate
        consumption_rate = await self.consumption_patterns.get_consumption_rate(
            line.beer_name,
            datetime.now().hour,
            datetime.now().weekday()
        )

        if consumption_rate <= 0:
            return datetime.now() + timedelta(days=30)  # Very low consumption

        # Calculate minutes until empty
        minutes_remaining = (line.current_volume * 1000) / consumption_rate  # Convert L to mL

        return datetime.now() + timedelta(minutes=minutes_remaining)

    def _determine_change_priority(self, line: BeerLine, estimated_empty_time: datetime) -> str:
        """Determine priority level for keg change"""
        time_until_empty = (estimated_empty_time - datetime.now()).total_seconds() / 3600  # hours

        if time_until_empty <= 0.5:  # 30 minutes or less
            return 'critical'
        elif time_until_empty <= 2:  # 2 hours or less
            return 'high'
        elif time_until_empty <= 6:  # 6 hours or less
            return 'medium'
        else:
            return 'low'

    async def _calculate_overall_cellar_status(self) -> str:
        """Calculate overall cellar operational status"""
        critical_lines = sum(1 for line in self.beer_lines.values()
                           if line.status == BeerLineStatus.CRITICAL)
        warning_lines = sum(1 for line in self.beer_lines.values()
                          if line.status == BeerLineStatus.WARNING)

        if critical_lines > 0:
            return 'critical'
        elif warning_lines > len(self.beer_lines) * 0.3:  # More than 30% warning
            return 'warning'
        else:
            return 'optimal'

    async def record_wastage(self, item_id: str, quantity: float,
                           reason: str, staff_member: str) -> Dict:
        """Record wastage incident for tracking and analysis"""
        item = self.stock_items.get(item_id)
        if not item:
            return {'error': 'Item not found'}

        cost_impact = quantity * item.unit_cost

        wastage_record = WastageRecord(
            item_id=item_id,
            quantity=quantity,
            reason=reason,
            cost_impact=cost_impact,
            timestamp=datetime.now(),
            staff_member=staff_member
        )

        self.wastage_records.append(wastage_record)

        # Update stock levels
        item.current_stock = max(0, item.current_stock - quantity)

        return {
            'recorded': True,
            'cost_impact': cost_impact,
            'remaining_stock': item.current_stock,
            'wastage_id': len(self.wastage_records)
        }


class ConsumptionAnalyzer:
    """Analyzes consumption patterns for predictive ordering"""

    async def get_consumption_rate(self, beer_name: str, hour: int, weekday: int) -> float:
        """Get consumption rate based on historical patterns"""
        # Base consumption rates (ml/minute)
        base_rates = {
            'Guinness': 45,
            'Heineken': 35,
            'Smithwicks': 25,
            'Coors Light': 30
        }

        base_rate = base_rates.get(beer_name, 30)

        # Adjust for time of day
        hour_multipliers = {
            12: 0.3, 13: 0.5, 14: 0.4, 15: 0.3, 16: 0.4,
            17: 0.6, 18: 0.8, 19: 1.2, 20: 1.5, 21: 1.8,
            22: 1.6, 23: 1.2, 0: 0.8, 1: 0.4
        }

        hour_multiplier = hour_multipliers.get(hour, 0.2)

        # Adjust for day of week
        day_multipliers = [0.6, 0.7, 0.8, 0.9, 1.4, 1.8, 1.6]  # Mon-Sun
        day_multiplier = day_multipliers[weekday]

        return base_rate * hour_multiplier * day_multiplier


class SupplierManager:
    """Manages supplier relationships and ordering"""

    async def check_availability(self, supplier: str, item_id: str, quantity: int) -> Dict:
        """Check supplier availability and pricing"""
        # Simulate supplier API call
        return {
            'available': True,
            'unit_cost': 2.50,
            'total_cost': quantity * 2.50,
            'delivery_date': datetime.now() + timedelta(days=2)
        }


# Example usage and testing
if __name__ == "__main__":

    pub_config = {
        'beer_lines': [
            {'line_id': 'LINE1', 'beer_name': 'Guinness', 'keg_size': 50.0},
            {'line_id': 'LINE2', 'beer_name': 'Heineken', 'keg_size': 50.0},
            {'line_id': 'LINE3', 'beer_name': 'Smithwicks', 'keg_size': 30.0}
        ],
        'stock_items': [
            {
                'item_id': 'WINE001',
                'name': 'House Red Wine',
                'category': 'wine',
                'current_stock': 12,
                'min_threshold': 5,
                'unit_cost': 8.50,
                'supplier': 'WineSupplier Ltd'
            }
        ],
        'auto_order_limit': 200
    }

    async def test_controller():
        controller = StockCellarController(pub_config)

        # Test beer line monitoring
        line_status = await controller.monitor_beer_lines()
        print("Beer line status:", json.dumps(line_status, indent=2, default=str))

        # Test keg change predictions
        keg_predictions = await controller.predict_keg_changes()
        print("Keg change predictions:", json.dumps(keg_predictions, indent=2, default=str))

        # Test wastage recording
        wastage_result = await controller.record_wastage(
            'WINE001', 2, 'Broken bottle', 'John'
        )
        print("Wastage recorded:", wastage_result)

    # Run test
    asyncio.run(test_controller())