"""
Order Management System - Core AI Agent for Food Delivery

Handles multi-channel order intake, processing, and tracking with
intelligent prioritization and real-time kitchen integration.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    RECEIVED = "received"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderChannel(Enum):
    PHONE = "phone"
    WEBSITE = "website"
    UBER_EATS = "uber_eats"
    DELIVEROO = "deliveroo"
    JUST_EAT = "just_eat"
    WALK_IN = "walk_in"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class MenuItem:
    id: str
    name: str
    prep_time: int  # minutes
    price: float
    allergens: List[str]
    dietary_info: List[str]
    ingredients: List[str]

@dataclass
class Customer:
    id: str
    name: str
    phone: str
    email: Optional[str]
    address: str
    dietary_restrictions: List[str]
    loyalty_points: int
    order_history: List[str]

@dataclass
class Order:
    id: str
    customer: Customer
    items: List[Dict[str, Any]]  # {menu_item: MenuItem, quantity: int, modifications: List[str]}
    channel: OrderChannel
    status: OrderStatus
    priority: Priority
    estimated_prep_time: int
    estimated_delivery_time: datetime
    special_instructions: str
    total_amount: float
    created_at: datetime
    updated_at: datetime

class OrderManager:
    """
    AI-powered order management system that handles multi-channel
    order intake, processing, and real-time tracking.
    """

    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.menu: Dict[str, MenuItem] = {}
        self.channels: List[OrderChannel] = []
        self.kitchen_display_config = {
            'enabled': False,
            'sound_alerts': True,
            'priority_colors': True,
            'auto_refresh': 30  # seconds
        }
        self.avg_prep_times = {}
        self.peak_hours = []

    def configure_channels(self, channels: List[str]) -> None:
        """Configure available order channels"""
        self.channels = [OrderChannel(channel) for channel in channels]
        logger.info(f"Configured channels: {[c.value for c in self.channels]}")

    def set_kitchen_display(self, enable_sound: bool = True,
                          priority_colors: bool = True,
                          auto_refresh: int = 30) -> None:
        """Configure kitchen display system"""
        self.kitchen_display_config.update({
            'enabled': True,
            'sound_alerts': enable_sound,
            'priority_colors': priority_colors,
            'auto_refresh': auto_refresh
        })

    def enable_dietary_tracking(self, dietary_types: List[str]) -> None:
        """Enable tracking of dietary restrictions"""
        self.supported_dietary_types = dietary_types
        logger.info(f"Enabled dietary tracking: {dietary_types}")

    async def create_order(self, order_data: Dict[str, Any]) -> Order:
        """Create new order with AI-powered processing"""
        order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.orders) + 1}"

        # Calculate estimated prep time using AI
        estimated_prep = self._calculate_prep_time(order_data['items'])

        # Determine priority based on multiple factors
        priority = self._calculate_priority(order_data, estimated_prep)

        # Estimate delivery time
        delivery_time = self._estimate_delivery_time(estimated_prep, order_data.get('delivery_zone'))

        order = Order(
            id=order_id,
            customer=Customer(**order_data['customer']),
            items=order_data['items'],
            channel=OrderChannel(order_data['channel']),
            status=OrderStatus.RECEIVED,
            priority=priority,
            estimated_prep_time=estimated_prep,
            estimated_delivery_time=delivery_time,
            special_instructions=order_data.get('special_instructions', ''),
            total_amount=self._calculate_total(order_data['items']),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.orders[order_id] = order

        # Send to kitchen display
        await self._update_kitchen_display(order)

        # Check for dietary restrictions and allergens
        await self._check_dietary_requirements(order)

        logger.info(f"Created order {order_id} with priority {priority.name}")
        return order

    def _calculate_prep_time(self, items: List[Dict[str, Any]]) -> int:
        """AI-powered prep time calculation based on items and kitchen load"""
        base_prep_time = 0

        for item_data in items:
            item_id = item_data['menu_item_id']
            quantity = item_data['quantity']

            if item_id in self.menu:
                item_prep_time = self.menu[item_id].prep_time
                # Adjust for quantity (not linear scaling)
                adjusted_time = item_prep_time * (1 + (quantity - 1) * 0.3)
                base_prep_time = max(base_prep_time, adjusted_time)

        # Adjust for current kitchen load
        current_load = len([o for o in self.orders.values()
                          if o.status in [OrderStatus.CONFIRMED, OrderStatus.PREPARING]])

        load_multiplier = 1 + (current_load * 0.1)

        # Check if it's peak hour
        current_hour = datetime.now().hour
        if current_hour in self.peak_hours:
            load_multiplier *= 1.2

        return int(base_prep_time * load_multiplier)

    def _calculate_priority(self, order_data: Dict[str, Any], prep_time: int) -> Priority:
        """Calculate order priority using AI scoring"""
        score = 0

        # Channel priority
        channel_scores = {
            OrderChannel.PHONE: 3,
            OrderChannel.WALK_IN: 4,
            OrderChannel.WEBSITE: 2,
            OrderChannel.UBER_EATS: 1,
            OrderChannel.DELIVEROO: 1,
            OrderChannel.JUST_EAT: 1
        }
        score += channel_scores.get(OrderChannel(order_data['channel']), 1)

        # Customer loyalty
        customer = order_data.get('customer', {})
        loyalty_points = customer.get('loyalty_points', 0)
        if loyalty_points > 1000:
            score += 2
        elif loyalty_points > 500:
            score += 1

        # Order value
        total_amount = self._calculate_total(order_data['items'])
        if total_amount > 50:
            score += 2
        elif total_amount > 30:
            score += 1

        # Delivery zone
        delivery_zone = order_data.get('delivery_zone', 'standard')
        if delivery_zone == 'close':
            score += 1

        # Convert score to priority
        if score >= 7:
            return Priority.URGENT
        elif score >= 5:
            return Priority.HIGH
        elif score >= 3:
            return Priority.MEDIUM
        else:
            return Priority.LOW

    def _estimate_delivery_time(self, prep_time: int, delivery_zone: str = 'standard') -> datetime:
        """Estimate delivery time based on prep time and zone"""
        zone_times = {
            'close': 10,      # minutes
            'standard': 20,
            'far': 35
        }

        delivery_travel_time = zone_times.get(delivery_zone, 20)
        total_time = prep_time + delivery_travel_time + 5  # 5 min buffer

        return datetime.now() + timedelta(minutes=total_time)

    def _calculate_total(self, items: List[Dict[str, Any]]) -> float:
        """Calculate order total"""
        total = 0.0
        for item_data in items:
            item_id = item_data['menu_item_id']
            quantity = item_data['quantity']
            if item_id in self.menu:
                total += self.menu[item_id].price * quantity
        return total

    async def _update_kitchen_display(self, order: Order) -> None:
        """Update kitchen display system"""
        if not self.kitchen_display_config['enabled']:
            return

        display_data = {
            'order_id': order.id,
            'items': order.items,
            'priority': order.priority.name,
            'special_instructions': order.special_instructions,
            'estimated_time': order.estimated_prep_time,
            'channel': order.channel.value
        }

        # In real implementation, this would send to actual kitchen display
        logger.info(f"Kitchen Display Update: {display_data}")

    async def _check_dietary_requirements(self, order: Order) -> None:
        """Check and flag dietary restrictions and allergens"""
        customer_restrictions = order.customer.dietary_restrictions

        for item_data in order.items:
            item_id = item_data['menu_item_id']
            if item_id in self.menu:
                menu_item = self.menu[item_id]

                # Check allergens
                for allergen in menu_item.allergens:
                    if any(restriction.lower() in allergen.lower()
                          for restriction in customer_restrictions):
                        logger.warning(f"ALLERGEN ALERT: Order {order.id} - {allergen}")

    async def update_order_status(self, order_id: str, status: OrderStatus) -> bool:
        """Update order status with notifications"""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]
        old_status = order.status
        order.status = status
        order.updated_at = datetime.now()

        # Send notifications based on status change
        await self._send_status_notification(order, old_status, status)

        logger.info(f"Order {order_id} status: {old_status.value} -> {status.value}")
        return True

    async def _send_status_notification(self, order: Order, old_status: OrderStatus,
                                      new_status: OrderStatus) -> None:
        """Send status notifications to customer"""
        notifications = {
            OrderStatus.CONFIRMED: "Your order has been confirmed and is being prepared!",
            OrderStatus.PREPARING: "Our chefs are working on your delicious meal!",
            OrderStatus.READY: "Your order is ready for pickup/delivery!",
            OrderStatus.OUT_FOR_DELIVERY: "Your order is on its way to you!",
            OrderStatus.DELIVERED: "Your order has been delivered. Enjoy your meal!"
        }

        if new_status in notifications:
            message = notifications[new_status]
            # In real implementation, send SMS/email/push notification
            logger.info(f"Notification to {order.customer.phone}: {message}")

    def get_kitchen_queue(self) -> List[Order]:
        """Get prioritized kitchen queue"""
        active_orders = [
            order for order in self.orders.values()
            if order.status in [OrderStatus.CONFIRMED, OrderStatus.PREPARING]
        ]

        # Sort by priority (highest first) then by creation time
        return sorted(active_orders,
                     key=lambda x: (-x.priority.value, x.created_at))

    def get_delivery_queue(self) -> List[Order]:
        """Get orders ready for delivery"""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.READY
        ]

    async def handle_modification(self, order_id: str, modifications: Dict[str, Any]) -> bool:
        """Handle order modifications"""
        if order_id not in self.orders:
            return False

        order = self.orders[order_id]

        # Only allow modifications if order hasn't started preparing
        if order.status not in [OrderStatus.RECEIVED, OrderStatus.CONFIRMED]:
            logger.warning(f"Cannot modify order {order_id} - already in preparation")
            return False

        # Apply modifications
        if 'items' in modifications:
            order.items = modifications['items']
            order.total_amount = self._calculate_total(order.items)
            order.estimated_prep_time = self._calculate_prep_time(order.items)

        if 'special_instructions' in modifications:
            order.special_instructions = modifications['special_instructions']

        order.updated_at = datetime.now()

        # Update kitchen display
        await self._update_kitchen_display(order)

        logger.info(f"Modified order {order_id}")
        return True

    def get_order_analytics(self) -> Dict[str, Any]:
        """Get comprehensive order analytics"""
        total_orders = len(self.orders)
        if total_orders == 0:
            return {}

        status_counts = {}
        channel_counts = {}
        avg_order_value = 0
        total_revenue = 0

        for order in self.orders.values():
            # Status distribution
            status = order.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            # Channel distribution
            channel = order.channel.value
            channel_counts[channel] = channel_counts.get(channel, 0) + 1

            # Revenue
            total_revenue += order.total_amount

        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'average_order_value': round(avg_order_value, 2),
            'status_distribution': status_counts,
            'channel_distribution': channel_counts,
            'completion_rate': (
                status_counts.get('delivered', 0) / total_orders * 100
                if total_orders > 0 else 0
            )
        }

# Example usage
if __name__ == "__main__":
    async def demo():
        order_manager = OrderManager()

        # Configure system
        order_manager.configure_channels(['uber_eats', 'phone', 'website'])
        order_manager.set_kitchen_display(enable_sound=True, priority_colors=True)
        order_manager.enable_dietary_tracking(['gluten_free', 'vegan', 'halal'])

        # Add sample menu item
        order_manager.menu['pizza_margherita'] = MenuItem(
            id='pizza_margherita',
            name='Pizza Margherita',
            prep_time=15,
            price=12.99,
            allergens=['gluten', 'dairy'],
            dietary_info=['vegetarian'],
            ingredients=['flour', 'tomato', 'mozzarella', 'basil']
        )

        # Create sample order
        order_data = {
            'customer': {
                'id': 'cust_001',
                'name': 'John Doe',
                'phone': '+353 87 123 4567',
                'email': 'john@example.com',
                'address': '123 Main St, Dublin',
                'dietary_restrictions': [],
                'loyalty_points': 750,
                'order_history': []
            },
            'items': [
                {
                    'menu_item_id': 'pizza_margherita',
                    'quantity': 2,
                    'modifications': ['extra cheese']
                }
            ],
            'channel': 'uber_eats',
            'special_instructions': 'Please ring doorbell',
            'delivery_zone': 'standard'
        }

        # Process order
        order = await order_manager.create_order(order_data)
        print(f"Created order: {order.id}")

        # Update status
        await order_manager.update_order_status(order.id, OrderStatus.CONFIRMED)
        await order_manager.update_order_status(order.id, OrderStatus.PREPARING)

        # Get analytics
        analytics = order_manager.get_order_analytics()
        print(f"Analytics: {analytics}")

    asyncio.run(demo())