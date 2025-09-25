"""
Integration tests for Food Delivery AI Toolkit

Tests the interaction between all AI agents to ensure
they work together seamlessly.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock

from src import (
    FoodDeliveryAI,
    OrderManager,
    DeliveryOptimizer,
    InventoryManager,
    CustomerExperienceHub,
    FinancialAnalytics
)

from src.order_manager import MenuItem, OrderChannel, OrderStatus
from src.delivery_optimizer import Location, Driver, DriverStatus
from src.inventory_manager import Ingredient, Supplier, InventoryStatus
from src.customer_experience import CustomerTier, FeedbackType

@pytest.fixture
def food_delivery_ai():
    """Create a configured Food Delivery AI system for testing"""
    ai_system = FoodDeliveryAI()

    # Setup restaurant
    restaurant_config = {
        'name': 'Test Restaurant',
        'address': 'Test Address',
        'latitude': 53.3498,
        'longitude': -6.2603,
        'platforms': ['uber_eats', 'phone']
    }

    ai_system.setup_restaurant(restaurant_config)
    return ai_system

@pytest.fixture
def sample_ingredients():
    """Create sample ingredients for testing"""
    return [
        Ingredient("flour", "Flour", 20.0, "kg", 5.0, 50.0, 1.50, "supplier_1",
                  datetime.now() + timedelta(days=30), InventoryStatus.IN_STOCK),
        Ingredient("cheese", "Mozzarella", 10.0, "kg", 2.0, 25.0, 8.00, "supplier_1",
                  datetime.now() + timedelta(days=10), InventoryStatus.IN_STOCK)
    ]

@pytest.fixture
def sample_menu_items():
    """Create sample menu items for testing"""
    return [
        MenuItem("pizza", "Test Pizza", "Pizza", 15.99, 15.99, 20,
                {"flour": 0.3, "cheese": 0.2}, ["gluten", "dairy"],
                ["vegetarian"], 80.0, 0.60, "available", 20)
    ]

@pytest.fixture
def sample_customer_data():
    """Create sample customer data for testing"""
    return {
        'name': 'Test Customer',
        'email': 'test@example.com',
        'phone': '+353871234567',
        'address': 'Test Address, Dublin',
        'dietary_restrictions': [],
        'accept_marketing': True
    }

@pytest.mark.asyncio
class TestOrderToDeliveryFlow:
    """Test the complete flow from order creation to delivery"""

    async def test_complete_order_flow(self, food_delivery_ai, sample_ingredients,
                                     sample_menu_items, sample_customer_data):
        """Test complete order processing flow"""
        ai_system = food_delivery_ai

        # Setup inventory
        supplier = Supplier("supplier_1", "Test Supplier", "test@supplier.com",
                           ["Monday"], 100.0, 2, 4.5)
        ai_system.inventory_manager.add_supplier(supplier)

        for ingredient in sample_ingredients:
            ai_system.inventory_manager.add_ingredient(ingredient)

        for menu_item in sample_menu_items:
            ai_system.inventory_manager.add_menu_item(menu_item)

        # Register customer
        customer = ai_system.customer_hub.register_customer(sample_customer_data)

        # Add driver
        driver = Driver("driver_1", "Test Driver", "+353871111111",
                       Location(53.3500, -6.2600, "Driver Location"),
                       DriverStatus.AVAILABLE, "scooter", 3, [], 4.8, 100, 50.0)
        ai_system.delivery_optimizer.add_driver(driver)

        # Create order
        order_data = {
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'address': customer.address,
                'dietary_restrictions': customer.dietary_restrictions,
                'loyalty_points': customer.loyalty_points,
                'order_history': []
            },
            'items': [
                {'menu_item_id': 'pizza', 'quantity': 1, 'modifications': []}
            ],
            'channel': 'uber_eats',
            'special_instructions': 'Test order',
            'delivery_zone': 'standard'
        }

        order = await ai_system.order_manager.create_order(order_data)

        # Verify order creation
        assert order.id is not None
        assert order.total_amount > 0
        assert order.status == OrderStatus.RECEIVED

        # Update order status
        await ai_system.order_manager.update_order_status(order.id, OrderStatus.CONFIRMED)
        await ai_system.order_manager.update_order_status(order.id, OrderStatus.PREPARING)

        # Verify inventory was updated
        flour_ingredient = ai_system.inventory_manager.ingredients["flour"]
        cheese_ingredient = ai_system.inventory_manager.ingredients["cheese"]

        # Should have decreased by recipe amounts
        assert flour_ingredient.current_stock < 20.0
        assert cheese_ingredient.current_stock < 10.0

        # Create delivery order and assign driver
        from src.delivery_optimizer import DeliveryOrder
        delivery_order = DeliveryOrder(
            order_id=order.id,
            customer_location=Location(53.3520, -6.2650, customer.address),
            customer_name=customer.name,
            customer_phone=customer.phone,
            items_count=1,
            total_value=order.total_amount,
            special_instructions="Test order",
            ready_time=datetime.now() + timedelta(minutes=20),
            target_delivery_time=order.estimated_delivery_time,
            priority=3,
            status="pending"
        )

        ai_system.delivery_optimizer.add_delivery_order(delivery_order)
        assigned_driver = await ai_system.delivery_optimizer.assign_optimal_driver(delivery_order)

        assert assigned_driver is not None
        assert assigned_driver == "driver_1"

        # Update customer after order
        await ai_system.customer_hub.update_customer_after_order(
            customer.id, order.total_amount, ['pizza']
        )

        # Verify customer was updated
        updated_customer = ai_system.customer_hub.customers[customer.id]
        assert updated_customer.total_orders == 1
        assert updated_customer.total_spent == order.total_amount
        assert updated_customer.loyalty_points > 0

        # Analyze financials
        financial_data = {
            'order_id': order.id,
            'total_amount': order.total_amount,
            'platform': 'uber_eats',
            'items': order.items,
            'prep_time': 20,
            'delivery_distance': 3.0
        }

        order_financials = await ai_system.financial_analytics.analyze_order_profitability(financial_data)

        assert order_financials.gross_revenue == order.total_amount
        assert order_financials.platform_fee > 0  # Should have Uber Eats commission
        assert order_financials.profit != 0

@pytest.mark.asyncio
class TestInventoryOrderIntegration:
    """Test integration between inventory and order management"""

    async def test_inventory_affects_menu_availability(self, food_delivery_ai,
                                                     sample_ingredients, sample_menu_items):
        """Test that low inventory affects menu item availability"""
        ai_system = food_delivery_ai

        # Setup inventory with low stock
        low_stock_ingredient = Ingredient(
            "cheese", "Mozzarella", 0.1, "kg", 2.0, 25.0, 8.00, "supplier_1",
            datetime.now() + timedelta(days=10), InventoryStatus.OUT_OF_STOCK
        )

        ai_system.inventory_manager.add_ingredient(low_stock_ingredient)
        ai_system.inventory_manager.add_menu_item(sample_menu_items[0])

        # Update menu availability
        await ai_system.inventory_manager._update_menu_availability()

        # Menu item should be unavailable due to lack of cheese
        pizza_item = ai_system.inventory_manager.menu_items["pizza"]
        assert pizza_item.status.value == "unavailable"

    async def test_order_triggers_reorder(self, food_delivery_ai, sample_customer_data):
        """Test that orders trigger automatic reordering when stock is low"""
        ai_system = food_delivery_ai

        # Setup supplier
        supplier = Supplier("supplier_1", "Test Supplier", "test@supplier.com",
                           ["Monday"], 50.0, 2, 4.5)  # Low minimum order
        ai_system.inventory_manager.add_supplier(supplier)

        # Setup low stock ingredient
        low_ingredient = Ingredient(
            "flour", "Flour", 2.0, "kg", 5.0, 50.0, 1.50, "supplier_1",
            datetime.now() + timedelta(days=30), InventoryStatus.LOW_STOCK
        )
        ai_system.inventory_manager.add_ingredient(low_ingredient)

        # Use stock (simulating order)
        await ai_system.inventory_manager.update_stock("flour", 1.5, "order")

        # Should trigger auto-reorder
        assert len(ai_system.inventory_manager.purchase_orders) > 0

@pytest.mark.asyncio
class TestCustomerExperienceIntegration:
    """Test customer experience integration with other systems"""

    async def test_feedback_affects_future_orders(self, food_delivery_ai, sample_customer_data):
        """Test that customer feedback affects future order handling"""
        ai_system = food_delivery_ai

        # Register customer
        customer = ai_system.customer_hub.register_customer(sample_customer_data)

        # Submit complaint
        complaint_data = {
            'type': 'complaint',
            'rating': 2,
            'subject': 'Poor service',
            'message': 'Order was late and cold'
        }

        feedback_id = await ai_system.customer_hub.collect_feedback(customer.id, complaint_data)

        # Verify feedback was processed
        feedback = ai_system.customer_hub.feedback[feedback_id]
        assert feedback.status == "pending"

        # Verify customer received acknowledgment notification
        customer_notifications = [
            n for n in ai_system.customer_hub.notifications.values()
            if n.customer_id == customer.id
        ]

        # Should have welcome + feedback acknowledgment notifications
        assert len(customer_notifications) >= 2

    async def test_loyalty_points_integration(self, food_delivery_ai, sample_customer_data):
        """Test that loyalty points are correctly awarded and tracked"""
        ai_system = food_delivery_ai

        # Register customer
        customer = ai_system.customer_hub.register_customer(sample_customer_data)
        initial_points = customer.loyalty_points

        # Process order
        order_value = 25.50
        await ai_system.customer_hub.update_customer_after_order(
            customer.id, order_value, ['pizza']
        )

        # Verify points were awarded
        updated_customer = ai_system.customer_hub.customers[customer.id]
        assert updated_customer.loyalty_points > initial_points

        # Verify loyalty record was created
        customer_rewards = [
            r for r in ai_system.customer_hub.loyalty_rewards.values()
            if r.customer_id == customer.id
        ]
        assert len(customer_rewards) > 0

@pytest.mark.asyncio
class TestFinancialAnalyticsIntegration:
    """Test financial analytics integration with other systems"""

    async def test_comprehensive_financial_tracking(self, food_delivery_ai):
        """Test that all financial transactions are properly tracked"""
        ai_system = food_delivery_ai

        # Process mock order financial data
        order_data = {
            'order_id': 'test_order_1',
            'total_amount': 20.00,
            'platform': 'uber_eats',
            'items': [{'item_id': 'pizza', 'quantity': 1}],
            'prep_time': 15,
            'delivery_distance': 2.5
        }

        order_financials = await ai_system.financial_analytics.analyze_order_profitability(order_data)

        # Verify all costs are calculated
        assert order_financials.gross_revenue == 20.00
        assert order_financials.platform_fee > 0  # Uber Eats commission
        assert order_financials.ingredient_cost > 0
        assert order_financials.labor_cost > 0
        assert order_financials.delivery_cost > 0

        # Verify profit calculation
        total_costs = (order_financials.ingredient_cost +
                      order_financials.labor_cost +
                      order_financials.delivery_cost)
        expected_profit = order_financials.net_revenue - total_costs

        assert abs(order_financials.profit - expected_profit) < 0.01  # Allow for rounding

        # Verify transactions were recorded
        assert len(ai_system.financial_analytics.transactions) > 0

    async def test_platform_fee_calculation(self, food_delivery_ai):
        """Test that platform fees are calculated correctly for different platforms"""
        ai_system = food_delivery_ai

        platforms_and_fees = [
            ('direct', 0.0),
            ('uber_eats', 0.30),
            ('deliveroo', 0.28),
            ('just_eat', 0.14)
        ]

        for platform, expected_rate in platforms_and_fees:
            order_data = {
                'order_id': f'test_order_{platform}',
                'total_amount': 100.00,  # Easy to calculate percentages
                'platform': platform,
                'items': [],
                'prep_time': 15,
                'delivery_distance': 2.5
            }

            order_financials = await ai_system.financial_analytics.analyze_order_profitability(order_data)
            expected_fee = 100.00 * expected_rate

            assert abs(order_financials.platform_fee - expected_fee) < 0.01

@pytest.mark.asyncio
class TestSystemResilience:
    """Test system behavior under various conditions"""

    async def test_handles_missing_ingredients(self, food_delivery_ai, sample_customer_data):
        """Test system behavior when ingredients are missing"""
        ai_system = food_delivery_ai

        # Try to create order without setting up ingredients
        customer = ai_system.customer_hub.register_customer(sample_customer_data)

        order_data = {
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'address': customer.address,
                'dietary_restrictions': [],
                'loyalty_points': 0,
                'order_history': []
            },
            'items': [
                {'menu_item_id': 'nonexistent_item', 'quantity': 1, 'modifications': []}
            ],
            'channel': 'direct',
            'special_instructions': '',
            'delivery_zone': 'standard'
        }

        # Should handle gracefully without crashing
        order = await ai_system.order_manager.create_order(order_data)
        assert order is not None

    async def test_handles_no_available_drivers(self, food_delivery_ai, sample_customer_data):
        """Test system behavior when no drivers are available"""
        ai_system = food_delivery_ai

        # Create delivery order without adding any drivers
        from src.delivery_optimizer import DeliveryOrder
        delivery_order = DeliveryOrder(
            order_id="test_order",
            customer_location=Location(53.3520, -6.2650, "Test Address"),
            customer_name="Test Customer",
            customer_phone="+353871234567",
            items_count=1,
            total_value=20.00,
            special_instructions="",
            ready_time=datetime.now() + timedelta(minutes=20),
            target_delivery_time=datetime.now() + timedelta(minutes=45),
            priority=3,
            status="pending"
        )

        ai_system.delivery_optimizer.add_delivery_order(delivery_order)

        # Should return None when no drivers available
        assigned_driver = await ai_system.delivery_optimizer.assign_optimal_driver(delivery_order)
        assert assigned_driver is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])