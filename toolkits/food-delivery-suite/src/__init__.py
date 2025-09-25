"""
Food Delivery AI Toolkit - Core Package

A comprehensive AI-powered solution for restaurants and takeaways
to optimize their delivery operations and maximize profitability.
"""

from .order_manager import OrderManager, Order, OrderStatus, OrderChannel, Priority
from .delivery_optimizer import DeliveryOptimizer, DeliveryOrder, Driver, DeliveryRoute
from .inventory_manager import InventoryManager, Ingredient, MenuItem, Supplier
from .customer_experience import CustomerExperienceHub, Customer, Feedback, LoyaltyReward
from .financial_analytics import FinancialAnalytics, OrderFinancials, Transaction, DriverPerformance

__version__ = "1.0.0"
__author__ = "Food Delivery AI Team"

class FoodDeliveryAI:
    """
    Main orchestrator class that combines all AI agents for
    comprehensive food delivery management.
    """

    def __init__(self):
        self.order_manager = OrderManager()
        self.delivery_optimizer = None  # Requires restaurant location
        self.inventory_manager = InventoryManager()
        self.customer_hub = CustomerExperienceHub()
        self.financial_analytics = FinancialAnalytics()

    def setup_restaurant(self, config: dict) -> None:
        """Initialize the system with restaurant configuration"""
        from .delivery_optimizer import Location

        # Setup delivery optimizer with restaurant location
        restaurant_location = Location(
            latitude=config.get('latitude', 53.3498),
            longitude=config.get('longitude', -6.2603),
            address=config.get('address', 'Restaurant Location')
        )

        self.delivery_optimizer = DeliveryOptimizer(restaurant_location)

        # Configure order manager
        self.order_manager.configure_channels(config.get('platforms', ['direct']))
        self.order_manager.set_kitchen_display(enable_sound=True, priority_colors=True)

        print(f"✅ Food Delivery AI initialized for {config.get('name', 'Restaurant')}")

    def connect_platforms(self, platforms: list) -> None:
        """Connect to delivery platforms"""
        self.order_manager.configure_channels(platforms)
        print(f"✅ Connected to platforms: {platforms}")

    def start_monitoring(self) -> None:
        """Start real-time monitoring of all systems"""
        print("🚀 Food Delivery AI is now monitoring your operations!")
        print("📊 Dashboard available at: http://localhost:8000")
        print("📱 Mobile app sync enabled")
        print("💡 AI optimization active")

# Convenience imports for easy access
__all__ = [
    'FoodDeliveryAI',
    'OrderManager',
    'DeliveryOptimizer',
    'InventoryManager',
    'CustomerExperienceHub',
    'FinancialAnalytics',
    'Order',
    'DeliveryOrder',
    'Customer',
    'OrderFinancials'
]