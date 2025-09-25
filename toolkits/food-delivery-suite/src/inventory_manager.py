"""
Menu & Inventory Management AI Agent

Handles real-time inventory tracking, menu availability,
demand forecasting, and automated supplier management.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class InventoryStatus(Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ORDERED = "ordered"
    EXPIRED = "expired"

class MenuStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    LIMITED = "limited"
    SEASONAL = "seasonal"

@dataclass
class Ingredient:
    id: str
    name: str
    current_stock: float
    unit: str  # kg, liters, pieces, etc.
    min_threshold: float
    max_capacity: float
    cost_per_unit: float
    supplier_id: str
    expiry_date: Optional[datetime]
    status: InventoryStatus

@dataclass
class MenuItem:
    id: str
    name: str
    category: str
    base_price: float
    current_price: float
    prep_time: int
    ingredients: Dict[str, float]  # ingredient_id: quantity_needed
    allergens: List[str]
    dietary_info: List[str]
    popularity_score: float
    profit_margin: float
    status: MenuStatus
    daily_sales: int

@dataclass
class Supplier:
    id: str
    name: str
    contact_info: str
    delivery_days: List[str]
    min_order_value: float
    lead_time_days: int
    reliability_score: float

@dataclass
class PurchaseOrder:
    id: str
    supplier_id: str
    items: Dict[str, float]  # ingredient_id: quantity
    total_cost: float
    order_date: datetime
    expected_delivery: datetime
    status: str

class InventoryManager:
    """
    AI-powered inventory and menu management system that handles
    stock tracking, demand forecasting, and automated ordering.
    """

    def __init__(self):
        self.ingredients: Dict[str, Ingredient] = {}
        self.menu_items: Dict[str, MenuItem] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.sales_history: List[Dict[str, Any]] = []
        self.waste_tracking: List[Dict[str, Any]] = []
        self.price_optimization_enabled = True

    def add_ingredient(self, ingredient: Ingredient) -> None:
        """Add ingredient to inventory system"""
        self.ingredients[ingredient.id] = ingredient
        logger.info(f"Added ingredient: {ingredient.name}")

    def add_menu_item(self, menu_item: MenuItem) -> None:
        """Add menu item to system"""
        self.menu_items[menu_item.id] = menu_item
        logger.info(f"Added menu item: {menu_item.name}")

    def add_supplier(self, supplier: Supplier) -> None:
        """Add supplier to system"""
        self.suppliers[supplier.id] = supplier
        logger.info(f"Added supplier: {supplier.name}")

    async def update_stock(self, ingredient_id: str, quantity_used: float,
                          reason: str = "sale") -> bool:
        """Update ingredient stock levels"""
        if ingredient_id not in self.ingredients:
            return False

        ingredient = self.ingredients[ingredient_id]

        # Update stock
        ingredient.current_stock -= quantity_used

        # Update status based on stock level
        if ingredient.current_stock <= 0:
            ingredient.status = InventoryStatus.OUT_OF_STOCK
        elif ingredient.current_stock <= ingredient.min_threshold:
            ingredient.status = InventoryStatus.LOW_STOCK
        else:
            ingredient.status = InventoryStatus.IN_STOCK

        # Log the usage
        self._log_ingredient_usage(ingredient_id, quantity_used, reason)

        # Check if we need to update menu availability
        await self._update_menu_availability()

        # Check if we need to reorder
        if ingredient.status == InventoryStatus.LOW_STOCK:
            await self._check_auto_reorder(ingredient_id)

        logger.info(f"Updated stock for {ingredient.name}: {ingredient.current_stock} {ingredient.unit}")
        return True

    def _log_ingredient_usage(self, ingredient_id: str, quantity: float, reason: str) -> None:
        """Log ingredient usage for analytics"""
        usage_log = {
            'ingredient_id': ingredient_id,
            'quantity': quantity,
            'reason': reason,
            'timestamp': datetime.now(),
            'remaining_stock': self.ingredients[ingredient_id].current_stock
        }
        # In real implementation, store in database

    async def _update_menu_availability(self) -> None:
        """Update menu item availability based on ingredient stock"""
        for menu_item in self.menu_items.values():
            available = True
            limited = False

            for ingredient_id, required_qty in menu_item.ingredients.items():
                if ingredient_id in self.ingredients:
                    ingredient = self.ingredients[ingredient_id]

                    if ingredient.status == InventoryStatus.OUT_OF_STOCK:
                        available = False
                        break
                    elif ingredient.current_stock < required_qty * 10:  # Less than 10 servings
                        limited = True

            # Update menu item status
            if not available:
                menu_item.status = MenuStatus.UNAVAILABLE
            elif limited:
                menu_item.status = MenuStatus.LIMITED
            else:
                menu_item.status = MenuStatus.AVAILABLE

        # Notify all platforms of menu changes
        await self._notify_menu_updates()

    async def _notify_menu_updates(self) -> None:
        """Notify all delivery platforms of menu availability changes"""
        unavailable_items = [
            item.name for item in self.menu_items.values()
            if item.status == MenuStatus.UNAVAILABLE
        ]

        limited_items = [
            item.name for item in self.menu_items.values()
            if item.status == MenuStatus.LIMITED
        ]

        if unavailable_items or limited_items:
            # In real implementation, update delivery platform APIs
            logger.info(f"Menu updates - Unavailable: {unavailable_items}, Limited: {limited_items}")

    async def _check_auto_reorder(self, ingredient_id: str) -> None:
        """Check if ingredient needs automatic reordering"""
        ingredient = self.ingredients[ingredient_id]

        # Calculate optimal order quantity
        order_quantity = await self._calculate_optimal_order_quantity(ingredient_id)

        if order_quantity > 0:
            await self.create_purchase_order(ingredient.supplier_id, {ingredient_id: order_quantity})

    async def _calculate_optimal_order_quantity(self, ingredient_id: str) -> float:
        """Calculate optimal order quantity using demand forecasting"""
        ingredient = self.ingredients[ingredient_id]

        # Get usage history for the past 30 days
        daily_usage = await self._get_daily_usage(ingredient_id, days=30)

        if not daily_usage:
            # No history, order to max capacity
            return ingredient.max_capacity - ingredient.current_stock

        # Calculate average daily usage
        avg_daily_usage = sum(daily_usage) / len(daily_usage)

        # Factor in supplier lead time and safety buffer
        supplier = self.suppliers[ingredient.supplier_id]
        safety_days = 3  # Extra buffer days
        total_days = supplier.lead_time_days + safety_days

        # Calculate required quantity
        required_quantity = avg_daily_usage * total_days

        # Don't exceed max capacity
        order_quantity = min(
            ingredient.max_capacity - ingredient.current_stock,
            required_quantity
        )

        return max(0, order_quantity)

    async def _get_daily_usage(self, ingredient_id: str, days: int) -> List[float]:
        """Get daily usage history for ingredient"""
        # In real implementation, query from database
        # For demo, return simulated data
        import random
        return [random.uniform(2, 8) for _ in range(days)]

    async def create_purchase_order(self, supplier_id: str,
                                  items: Dict[str, float]) -> str:
        """Create purchase order for ingredients"""
        if supplier_id not in self.suppliers:
            raise ValueError(f"Unknown supplier: {supplier_id}")

        supplier = self.suppliers[supplier_id]

        # Calculate total cost
        total_cost = 0
        for ingredient_id, quantity in items.items():
            if ingredient_id in self.ingredients:
                ingredient = self.ingredients[ingredient_id]
                total_cost += ingredient.cost_per_unit * quantity

        # Check minimum order value
        if total_cost < supplier.min_order_value:
            logger.warning(f"Order total {total_cost} below minimum {supplier.min_order_value}")
            return ""

        # Create purchase order
        order_id = f"PO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{supplier_id}"

        order = PurchaseOrder(
            id=order_id,
            supplier_id=supplier_id,
            items=items,
            total_cost=total_cost,
            order_date=datetime.now(),
            expected_delivery=datetime.now() + timedelta(days=supplier.lead_time_days),
            status="pending"
        )

        self.purchase_orders[order_id] = order

        # Update ingredient status to ORDERED
        for ingredient_id in items:
            if ingredient_id in self.ingredients:
                self.ingredients[ingredient_id].status = InventoryStatus.ORDERED

        # Send order to supplier (in real implementation)
        await self._send_order_to_supplier(order)

        logger.info(f"Created purchase order {order_id} for €{total_cost:.2f}")
        return order_id

    async def _send_order_to_supplier(self, order: PurchaseOrder) -> None:
        """Send purchase order to supplier"""
        supplier = self.suppliers[order.supplier_id]

        order_details = {
            'order_id': order.id,
            'supplier': supplier.name,
            'items': [
                {
                    'ingredient': self.ingredients[ing_id].name,
                    'quantity': qty,
                    'unit': self.ingredients[ing_id].unit
                }
                for ing_id, qty in order.items.items()
                if ing_id in self.ingredients
            ],
            'total_cost': order.total_cost,
            'expected_delivery': order.expected_delivery.strftime('%Y-%m-%d')
        }

        # In real implementation, send email/API call to supplier
        logger.info(f"Sent order to {supplier.name}: {order_details}")

    async def receive_delivery(self, order_id: str, received_items: Dict[str, float]) -> bool:
        """Process delivery receipt and update inventory"""
        if order_id not in self.purchase_orders:
            return False

        order = self.purchase_orders[order_id]

        # Update ingredient stocks
        for ingredient_id, quantity in received_items.items():
            if ingredient_id in self.ingredients:
                ingredient = self.ingredients[ingredient_id]
                ingredient.current_stock += quantity
                ingredient.status = InventoryStatus.IN_STOCK

        # Update order status
        order.status = "received"

        # Update menu availability
        await self._update_menu_availability()

        logger.info(f"Received delivery for order {order_id}")
        return True

    def track_waste(self, ingredient_id: str, quantity: float, reason: str) -> None:
        """Track food waste for analytics"""
        waste_entry = {
            'ingredient_id': ingredient_id,
            'quantity': quantity,
            'reason': reason,
            'cost': self.ingredients[ingredient_id].cost_per_unit * quantity,
            'timestamp': datetime.now()
        }

        self.waste_tracking.append(waste_entry)

        # Update stock
        if ingredient_id in self.ingredients:
            self.ingredients[ingredient_id].current_stock -= quantity

        logger.info(f"Tracked waste: {quantity} {self.ingredients[ingredient_id].unit} of {self.ingredients[ingredient_id].name}")

    async def forecast_demand(self, menu_item_id: str, days_ahead: int = 7) -> List[float]:
        """Forecast demand for menu item using AI"""
        if menu_item_id not in self.menu_items:
            return []

        menu_item = self.menu_items[menu_item_id]

        # Get historical sales data
        historical_sales = await self._get_sales_history(menu_item_id, days=30)

        if len(historical_sales) < 7:
            # Not enough data, use current popularity
            avg_daily_sales = menu_item.daily_sales
            return [float(avg_daily_sales)] * days_ahead

        # Simple trend analysis (in real implementation, use more sophisticated ML)
        recent_avg = sum(historical_sales[-7:]) / 7
        older_avg = sum(historical_sales[-14:-7]) / 7 if len(historical_sales) >= 14 else recent_avg

        trend_factor = recent_avg / older_avg if older_avg > 0 else 1.0

        # Consider day of week patterns
        forecast = []
        for i in range(days_ahead):
            future_date = datetime.now() + timedelta(days=i+1)
            day_of_week = future_date.weekday()

            # Weekend typically has higher sales
            day_multiplier = 1.3 if day_of_week >= 5 else 1.0

            predicted_sales = recent_avg * trend_factor * day_multiplier
            forecast.append(max(0, predicted_sales))

        return forecast

    async def _get_sales_history(self, menu_item_id: str, days: int) -> List[float]:
        """Get sales history for menu item"""
        # In real implementation, query from database
        # For demo, return simulated data
        import random
        base_sales = self.menu_items[menu_item_id].daily_sales
        return [random.uniform(base_sales * 0.7, base_sales * 1.3) for _ in range(days)]

    async def optimize_pricing(self, menu_item_id: str) -> float:
        """AI-powered dynamic pricing optimization"""
        if not self.price_optimization_enabled or menu_item_id not in self.menu_items:
            return 0

        menu_item = self.menu_items[menu_item_id]

        # Calculate ingredient cost
        ingredient_cost = 0
        for ingredient_id, quantity in menu_item.ingredients.items():
            if ingredient_id in self.ingredients:
                ingredient_cost += self.ingredients[ingredient_id].cost_per_unit * quantity

        # Base price calculation
        target_margin = 0.65  # 65% margin
        suggested_price = ingredient_cost / (1 - target_margin)

        # Adjust based on popularity
        popularity_factor = min(2.0, menu_item.popularity_score / 50)
        suggested_price *= popularity_factor

        # Adjust based on availability
        if menu_item.status == MenuStatus.LIMITED:
            suggested_price *= 1.1  # 10% increase for limited items

        # Don't change price too drastically
        max_change = menu_item.base_price * 0.2  # Max 20% change
        suggested_price = max(
            menu_item.base_price - max_change,
            min(menu_item.base_price + max_change, suggested_price)
        )

        # Update menu item price
        old_price = menu_item.current_price
        menu_item.current_price = round(suggested_price, 2)

        logger.info(f"Price optimization for {menu_item.name}: €{old_price:.2f} -> €{suggested_price:.2f}")
        return suggested_price

    def get_low_stock_alerts(self) -> List[Dict[str, Any]]:
        """Get list of ingredients with low stock"""
        alerts = []

        for ingredient in self.ingredients.values():
            if ingredient.status == InventoryStatus.LOW_STOCK:
                alerts.append({
                    'ingredient_id': ingredient.id,
                    'name': ingredient.name,
                    'current_stock': ingredient.current_stock,
                    'unit': ingredient.unit,
                    'min_threshold': ingredient.min_threshold,
                    'supplier': self.suppliers[ingredient.supplier_id].name if ingredient.supplier_id in self.suppliers else 'Unknown'
                })

        return alerts

    def get_waste_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get waste analytics for specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_waste = [
            entry for entry in self.waste_tracking
            if entry['timestamp'] >= cutoff_date
        ]

        if not recent_waste:
            return {}

        total_waste_cost = sum(entry['cost'] for entry in recent_waste)

        # Group by ingredient
        waste_by_ingredient = {}
        for entry in recent_waste:
            ingredient_id = entry['ingredient_id']
            if ingredient_id not in waste_by_ingredient:
                waste_by_ingredient[ingredient_id] = {
                    'name': self.ingredients[ingredient_id].name,
                    'total_quantity': 0,
                    'total_cost': 0,
                    'incidents': 0
                }
            waste_by_ingredient[ingredient_id]['total_quantity'] += entry['quantity']
            waste_by_ingredient[ingredient_id]['total_cost'] += entry['cost']
            waste_by_ingredient[ingredient_id]['incidents'] += 1

        return {
            'total_waste_cost': total_waste_cost,
            'waste_incidents': len(recent_waste),
            'daily_average_waste': total_waste_cost / days,
            'waste_by_ingredient': waste_by_ingredient
        }

    def get_inventory_analytics(self) -> Dict[str, Any]:
        """Get comprehensive inventory analytics"""
        total_ingredients = len(self.ingredients)

        status_counts = {}
        total_inventory_value = 0

        for ingredient in self.ingredients.values():
            status = ingredient.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            total_inventory_value += ingredient.current_stock * ingredient.cost_per_unit

        # Menu availability
        menu_status_counts = {}
        for menu_item in self.menu_items.values():
            status = menu_item.status.value
            menu_status_counts[status] = menu_status_counts.get(status, 0) + 1

        return {
            'total_ingredients': total_ingredients,
            'inventory_status': status_counts,
            'total_inventory_value': round(total_inventory_value, 2),
            'menu_items_total': len(self.menu_items),
            'menu_availability': menu_status_counts,
            'pending_orders': len([po for po in self.purchase_orders.values() if po.status == 'pending']),
            'low_stock_alerts': len(self.get_low_stock_alerts())
        }

# Example usage
if __name__ == "__main__":
    async def demo():
        inventory_manager = InventoryManager()

        # Add sample supplier
        supplier = Supplier(
            id="supplier_001",
            name="Fresh Foods Ltd",
            contact_info="orders@freshfoods.ie",
            delivery_days=["Monday", "Wednesday", "Friday"],
            min_order_value=100.0,
            lead_time_days=2,
            reliability_score=4.7
        )
        inventory_manager.add_supplier(supplier)

        # Add sample ingredients
        tomatoes = Ingredient(
            id="tomatoes",
            name="Fresh Tomatoes",
            current_stock=15.0,
            unit="kg",
            min_threshold=5.0,
            max_capacity=50.0,
            cost_per_unit=2.50,
            supplier_id="supplier_001",
            expiry_date=datetime.now() + timedelta(days=5),
            status=InventoryStatus.IN_STOCK
        )

        cheese = Ingredient(
            id="mozzarella",
            name="Mozzarella Cheese",
            current_stock=3.0,  # Low stock
            unit="kg",
            min_threshold=5.0,
            max_capacity=30.0,
            cost_per_unit=8.50,
            supplier_id="supplier_001",
            expiry_date=datetime.now() + timedelta(days=10),
            status=InventoryStatus.LOW_STOCK
        )

        inventory_manager.add_ingredient(tomatoes)
        inventory_manager.add_ingredient(cheese)

        # Add sample menu item
        pizza = MenuItem(
            id="pizza_margherita",
            name="Pizza Margherita",
            category="Pizza",
            base_price=12.99,
            current_price=12.99,
            prep_time=15,
            ingredients={"tomatoes": 0.15, "mozzarella": 0.20},
            allergens=["gluten", "dairy"],
            dietary_info=["vegetarian"],
            popularity_score=85.0,
            profit_margin=0.65,
            status=MenuStatus.AVAILABLE,
            daily_sales=25
        )

        inventory_manager.add_menu_item(pizza)

        # Simulate sales and stock updates
        await inventory_manager.update_stock("tomatoes", 2.5, "pizza sales")
        await inventory_manager.update_stock("mozzarella", 1.0, "pizza sales")

        # Check low stock alerts
        alerts = inventory_manager.get_low_stock_alerts()
        print(f"Low stock alerts: {alerts}")

        # Get analytics
        analytics = inventory_manager.get_inventory_analytics()
        print(f"Inventory analytics: {analytics}")

        # Forecast demand
        forecast = await inventory_manager.forecast_demand("pizza_margherita", 7)
        print(f"7-day demand forecast: {forecast}")

    asyncio.run(demo())