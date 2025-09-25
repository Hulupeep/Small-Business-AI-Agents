"""
Farm Shop & Market Sales Agent
Complete point-of-sale and inventory management for direct sales
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)

class SaleType(Enum):
    FARM_SHOP = "farm_shop"
    FARMERS_MARKET = "farmers_market"
    ONLINE_ORDER = "online_order"
    PRE_ORDER = "pre_order"
    CSA_BOX = "csa_box"

class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    CONTACTLESS = "contactless"
    MOBILE_PAY = "mobile_pay"
    BANK_TRANSFER = "bank_transfer"

class ProductCategory(Enum):
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    HERBS = "herbs"
    DAIRY = "dairy"
    MEAT = "meat"
    EGGS = "eggs"
    PRESERVED = "preserved"
    BAKED_GOODS = "baked_goods"

@dataclass
class Product:
    product_id: str
    name: str
    category: ProductCategory
    price_per_unit: Decimal
    unit: str  # kg, piece, liter, etc.
    current_stock: float
    minimum_stock: float
    seasonal_availability: List[int]  # months 1-12
    storage_requirements: str
    shelf_life_days: int
    organic: bool = False
    local_source: bool = True

@dataclass
class SaleItem:
    product_id: str
    quantity: float
    unit_price: Decimal
    total_price: Decimal
    discount_applied: Decimal = Decimal('0')

@dataclass
class Customer:
    customer_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    loyalty_points: int = 0
    csa_member: bool = False
    preferred_contact: str = "email"
    purchase_history: List[str] = field(default_factory=list)

@dataclass
class Sale:
    sale_id: str
    customer_id: Optional[str]
    sale_type: SaleType
    items: List[SaleItem]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    payment_method: PaymentMethod
    sale_date: datetime
    location: str
    notes: str = ""

class FarmShopSales:
    """
    Comprehensive sales management system for farm shops,
    farmers markets, and direct sales operations.
    """

    def __init__(self, farm_config: Dict):
        self.farm_config = farm_config
        self.products: Dict[str, Product] = {}
        self.customers: Dict[str, Customer] = {}
        self.sales: Dict[str, Sale] = {}
        self.csa_boxes: Dict[str, Dict] = {}
        self.pre_orders: Dict[str, Dict] = {}
        self.seasonal_prices: Dict[str, Dict] = {}
        self.loyalty_rules: Dict = {}

    async def initialize(self):
        """Initialize the sales management system"""
        logger.info("Initializing Farm Shop Sales system")
        await self._load_product_catalog()
        await self._setup_loyalty_program()
        await self._load_seasonal_pricing()
        logger.info("Farm Shop Sales system initialized successfully")

    async def _load_product_catalog(self):
        """Load product catalog with seasonal items"""
        # Sample products - in production would load from database
        sample_products = [
            {
                'name': 'Organic Tomatoes',
                'category': ProductCategory.VEGETABLES,
                'price_per_unit': Decimal('4.50'),
                'unit': 'kg',
                'current_stock': 150.0,
                'minimum_stock': 20.0,
                'seasonal_availability': [5, 6, 7, 8, 9, 10],
                'storage_requirements': 'cool_dry',
                'shelf_life_days': 7,
                'organic': True
            },
            {
                'name': 'Fresh Eggs',
                'category': ProductCategory.EGGS,
                'price_per_unit': Decimal('3.20'),
                'unit': 'dozen',
                'current_stock': 50.0,
                'minimum_stock': 10.0,
                'seasonal_availability': list(range(1, 13)),
                'storage_requirements': 'refrigerated',
                'shelf_life_days': 14,
                'organic': True
            },
            {
                'name': 'Raw Milk',
                'category': ProductCategory.DAIRY,
                'price_per_unit': Decimal('1.80'),
                'unit': 'liter',
                'current_stock': 200.0,
                'minimum_stock': 50.0,
                'seasonal_availability': list(range(1, 13)),
                'storage_requirements': 'refrigerated',
                'shelf_life_days': 3,
                'organic': False
            }
        ]

        for product_data in sample_products:
            product_id = f"prod_{uuid.uuid4().hex[:8]}"
            product = Product(
                product_id=product_id,
                **product_data
            )
            self.products[product_id] = product

        logger.info(f"Loaded {len(self.products)} products into catalog")

    async def _setup_loyalty_program(self):
        """Setup customer loyalty program rules"""
        self.loyalty_rules = {
            'points_per_euro': 1,
            'discount_threshold': 100,  # points needed for discount
            'discount_percentage': 5,   # 5% discount
            'bonus_multiplier_days': [6, 7],  # weekend bonus
            'bonus_multiplier': 1.5
        }

    async def _load_seasonal_pricing(self):
        """Load seasonal pricing adjustments"""
        # Price multipliers by month for different categories
        self.seasonal_prices = {
            ProductCategory.VEGETABLES: {
                1: 1.3, 2: 1.3, 3: 1.2, 4: 1.1, 5: 1.0,
                6: 0.8, 7: 0.7, 8: 0.7, 9: 0.8, 10: 0.9,
                11: 1.1, 12: 1.2
            },
            ProductCategory.FRUITS: {
                1: 1.4, 2: 1.4, 3: 1.3, 4: 1.2, 5: 1.1,
                6: 0.9, 7: 0.7, 8: 0.6, 9: 0.7, 10: 0.8,
                11: 1.2, 12: 1.3
            }
        }

    async def add_product(self, product_data: Dict) -> str:
        """Add new product to catalog"""
        product_id = f"prod_{uuid.uuid4().hex[:8]}"

        product = Product(
            product_id=product_id,
            name=product_data['name'],
            category=ProductCategory(product_data['category']),
            price_per_unit=Decimal(str(product_data['price_per_unit'])),
            unit=product_data['unit'],
            current_stock=product_data['current_stock'],
            minimum_stock=product_data['minimum_stock'],
            seasonal_availability=product_data['seasonal_availability'],
            storage_requirements=product_data['storage_requirements'],
            shelf_life_days=product_data['shelf_life_days'],
            organic=product_data.get('organic', False),
            local_source=product_data.get('local_source', True)
        )

        self.products[product_id] = product
        logger.info(f"Added product {product_id}: {product.name}")
        return product_id

    async def register_customer(self, customer_data: Dict) -> str:
        """Register new customer"""
        customer_id = f"cust_{uuid.uuid4().hex[:8]}"

        customer = Customer(
            customer_id=customer_id,
            name=customer_data['name'],
            email=customer_data.get('email'),
            phone=customer_data.get('phone'),
            csa_member=customer_data.get('csa_member', False),
            preferred_contact=customer_data.get('preferred_contact', 'email')
        )

        self.customers[customer_id] = customer
        logger.info(f"Registered customer {customer_id}: {customer.name}")
        return customer_id

    async def update_inventory(self, product_id: str, quantity_change: float, reason: str):
        """Update product inventory"""
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        old_stock = product.current_stock
        product.current_stock += quantity_change

        if product.current_stock < 0:
            product.current_stock = 0
            logger.warning(f"Stock for {product.name} went negative, set to 0")

        logger.info(f"Updated inventory for {product.name}: {old_stock} -> {product.current_stock} ({reason})")

        # Check if below minimum stock
        if product.current_stock <= product.minimum_stock:
            logger.warning(f"Low stock alert: {product.name} ({product.current_stock} {product.unit})")

    async def calculate_seasonal_price(self, product_id: str, date: Optional[datetime] = None) -> Decimal:
        """Calculate price with seasonal adjustments"""
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if date is None:
            date = datetime.now()

        month = date.month
        base_price = product.price_per_unit

        # Check if product is in season
        if month not in product.seasonal_availability:
            # Out of season - significant price increase or unavailable
            return base_price * Decimal('2.0')

        # Apply seasonal pricing
        seasonal_multiplier = self.seasonal_prices.get(product.category, {}).get(month, 1.0)
        adjusted_price = base_price * Decimal(str(seasonal_multiplier))

        return adjusted_price.quantize(Decimal('0.01'))

    async def process_sale(self, sale_data: Dict) -> str:
        """Process a complete sale transaction"""
        sale_id = f"sale_{uuid.uuid4().hex[:8]}"
        sale_items = []
        subtotal = Decimal('0')

        # Process each item
        for item_data in sale_data['items']:
            product_id = item_data['product_id']
            quantity = float(item_data['quantity'])

            product = self.products.get(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")

            if product.current_stock < quantity:
                raise ValueError(f"Insufficient stock for {product.name}")

            # Calculate price (with seasonal adjustment)
            unit_price = await self.calculate_seasonal_price(product_id)
            total_price = unit_price * Decimal(str(quantity))

            sale_item = SaleItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )

            sale_items.append(sale_item)
            subtotal += total_price

            # Update inventory
            await self.update_inventory(product_id, -quantity, f"Sale {sale_id}")

        # Apply customer discount if applicable
        customer_id = sale_data.get('customer_id')
        discount_amount = Decimal('0')

        if customer_id:
            customer = self.customers.get(customer_id)
            if customer and customer.loyalty_points >= self.loyalty_rules['discount_threshold']:
                discount_percentage = Decimal(str(self.loyalty_rules['discount_percentage'] / 100))
                discount_amount = subtotal * discount_percentage
                customer.loyalty_points -= self.loyalty_rules['discount_threshold']

        # Calculate tax (assuming 9% VAT on food)
        tax_rate = Decimal('0.09')
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * tax_rate
        total_amount = taxable_amount + tax_amount

        # Create sale record
        sale = Sale(
            sale_id=sale_id,
            customer_id=customer_id,
            sale_type=SaleType(sale_data['sale_type']),
            items=sale_items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            payment_method=PaymentMethod(sale_data['payment_method']),
            sale_date=datetime.now(),
            location=sale_data.get('location', 'farm_shop'),
            notes=sale_data.get('notes', '')
        )

        self.sales[sale_id] = sale

        # Award loyalty points
        if customer_id:
            await self._award_loyalty_points(customer_id, total_amount, sale.sale_date)

        logger.info(f"Processed sale {sale_id}: €{total_amount:.2f}")
        return sale_id

    async def _award_loyalty_points(self, customer_id: str, amount: Decimal, sale_date: datetime):
        """Award loyalty points to customer"""
        customer = self.customers.get(customer_id)
        if not customer:
            return

        base_points = int(amount * self.loyalty_rules['points_per_euro'])

        # Weekend bonus
        if sale_date.weekday() + 1 in self.loyalty_rules['bonus_multiplier_days']:
            base_points = int(base_points * self.loyalty_rules['bonus_multiplier'])

        customer.loyalty_points += base_points
        logger.info(f"Awarded {base_points} loyalty points to {customer.name}")

    async def create_pre_order(self, order_data: Dict) -> str:
        """Create pre-order for future pickup"""
        order_id = f"preorder_{uuid.uuid4().hex[:8]}"

        pre_order = {
            'order_id': order_id,
            'customer_id': order_data['customer_id'],
            'items': order_data['items'],
            'pickup_date': datetime.fromisoformat(order_data['pickup_date']),
            'total_amount': Decimal(str(order_data['total_amount'])),
            'status': 'confirmed',
            'payment_status': order_data.get('payment_status', 'pending'),
            'notes': order_data.get('notes', '')
        }

        self.pre_orders[order_id] = pre_order
        logger.info(f"Created pre-order {order_id} for customer {order_data['customer_id']}")
        return order_id

    async def manage_csa_boxes(self, week_date: datetime) -> Dict[str, List]:
        """Manage CSA (Community Supported Agriculture) box preparation"""
        csa_customers = [c for c in self.customers.values() if c.csa_member]

        if not csa_customers:
            return {'boxes': [], 'message': 'No CSA members found'}

        # Determine seasonal produce for boxes
        current_month = week_date.month
        available_products = [
            p for p in self.products.values()
            if current_month in p.seasonal_availability and p.current_stock > 0
        ]

        # Create standard box composition
        box_contents = await self._create_standard_csa_box(available_products)

        csa_boxes = []
        for customer in csa_customers:
            box_id = f"csa_{customer.customer_id}_{week_date.strftime('%Y%m%d')}"

            csa_box = {
                'box_id': box_id,
                'customer_id': customer.customer_id,
                'customer_name': customer.name,
                'week_date': week_date,
                'contents': box_contents.copy(),
                'total_value': sum(item['total_price'] for item in box_contents),
                'status': 'prepared',
                'pickup_instructions': 'Available for pickup Friday-Sunday'
            }

            csa_boxes.append(csa_box)
            self.csa_boxes[box_id] = csa_box

        logger.info(f"Prepared {len(csa_boxes)} CSA boxes for week of {week_date}")
        return {'boxes': csa_boxes, 'total_boxes': len(csa_boxes)}

    async def _create_standard_csa_box(self, available_products: List[Product]) -> List[Dict]:
        """Create standard CSA box composition"""
        box_contents = []

        # Box composition rules
        composition_rules = {
            ProductCategory.VEGETABLES: {'min_items': 4, 'max_items': 6, 'total_kg': 3.0},
            ProductCategory.FRUITS: {'min_items': 2, 'max_items': 3, 'total_kg': 1.5},
            ProductCategory.HERBS: {'min_items': 1, 'max_items': 2, 'total_kg': 0.2},
            ProductCategory.EGGS: {'min_items': 0, 'max_items': 1, 'total_units': 1},
            ProductCategory.DAIRY: {'min_items': 0, 'max_items': 1, 'total_liters': 1.0}
        }

        for category, rules in composition_rules.items():
            category_products = [p for p in available_products if p.category == category]

            if category_products:
                selected_count = min(rules['max_items'], len(category_products))
                selected_products = category_products[:selected_count]

                for product in selected_products:
                    if category == ProductCategory.VEGETABLES:
                        quantity = rules['total_kg'] / selected_count
                    elif category == ProductCategory.FRUITS:
                        quantity = rules['total_kg'] / selected_count
                    elif category == ProductCategory.HERBS:
                        quantity = rules['total_kg'] / selected_count
                    elif category == ProductCategory.EGGS:
                        quantity = rules['total_units']
                    elif category == ProductCategory.DAIRY:
                        quantity = rules['total_liters']
                    else:
                        quantity = 1.0

                    price = await self.calculate_seasonal_price(product.product_id)

                    box_contents.append({
                        'product_id': product.product_id,
                        'product_name': product.name,
                        'quantity': quantity,
                        'unit': product.unit,
                        'unit_price': price,
                        'total_price': price * Decimal(str(quantity))
                    })

        return box_contents

    async def generate_sales_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate comprehensive sales report"""
        relevant_sales = [
            sale for sale in self.sales.values()
            if start_date <= sale.sale_date <= end_date
        ]

        if not relevant_sales:
            return {'message': 'No sales in specified period'}

        # Calculate metrics
        total_revenue = sum(sale.total_amount for sale in relevant_sales)
        total_transactions = len(relevant_sales)
        average_transaction = total_revenue / total_transactions if total_transactions > 0 else Decimal('0')

        # Revenue by sale type
        revenue_by_type = {}
        for sale in relevant_sales:
            sale_type = sale.sale_type.value
            revenue_by_type[sale_type] = revenue_by_type.get(sale_type, Decimal('0')) + sale.total_amount

        # Revenue by product category
        revenue_by_category = {}
        for sale in relevant_sales:
            for item in sale.items:
                product = self.products.get(item.product_id)
                if product:
                    category = product.category.value
                    revenue_by_category[category] = revenue_by_category.get(category, Decimal('0')) + item.total_price

        # Top selling products
        product_sales = {}
        for sale in relevant_sales:
            for item in sale.items:
                product_id = item.product_id
                if product_id not in product_sales:
                    product_sales[product_id] = {'quantity': 0, 'revenue': Decimal('0')}
                product_sales[product_id]['quantity'] += item.quantity
                product_sales[product_id]['revenue'] += item.total_price

        top_products = sorted(
            product_sales.items(),
            key=lambda x: x[1]['revenue'],
            reverse=True
        )[:10]

        report = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_revenue': float(total_revenue),
                'total_transactions': total_transactions,
                'average_transaction': float(average_transaction),
                'currency': 'EUR'
            },
            'revenue_by_type': {k: float(v) for k, v in revenue_by_type.items()},
            'revenue_by_category': {k: float(v) for k, v in revenue_by_category.items()},
            'top_products': [
                {
                    'product_id': pid,
                    'product_name': self.products[pid].name if pid in self.products else 'Unknown',
                    'quantity_sold': data['quantity'],
                    'revenue': float(data['revenue'])
                }
                for pid, data in top_products
            ]
        }

        return report

    async def get_inventory_status(self) -> Dict:
        """Get current inventory status with alerts"""
        inventory_status = {
            'total_products': len(self.products),
            'low_stock_alerts': [],
            'out_of_stock': [],
            'overstocked': [],
            'seasonal_unavailable': []
        }

        current_month = datetime.now().month

        for product in self.products.values():
            # Check stock levels
            if product.current_stock <= 0:
                inventory_status['out_of_stock'].append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'category': product.category.value
                })
            elif product.current_stock <= product.minimum_stock:
                inventory_status['low_stock_alerts'].append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'current_stock': product.current_stock,
                    'minimum_stock': product.minimum_stock,
                    'unit': product.unit
                })
            elif product.current_stock > product.minimum_stock * 5:
                inventory_status['overstocked'].append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'current_stock': product.current_stock,
                    'shelf_life_days': product.shelf_life_days
                })

            # Check seasonal availability
            if current_month not in product.seasonal_availability:
                inventory_status['seasonal_unavailable'].append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'available_months': product.seasonal_availability
                })

        return inventory_status

    async def suggest_upsells(self, current_cart: List[Dict]) -> List[Dict]:
        """Suggest complementary products for upselling"""
        suggestions = []

        # Analyze current cart
        cart_categories = set()
        cart_product_ids = set()

        for item in current_cart:
            product = self.products.get(item['product_id'])
            if product:
                cart_categories.add(product.category)
                cart_product_ids.add(product.product_id)

        # Suggest complementary items
        complementary_rules = {
            ProductCategory.VEGETABLES: [ProductCategory.HERBS, ProductCategory.DAIRY],
            ProductCategory.FRUITS: [ProductCategory.DAIRY, ProductCategory.BAKED_GOODS],
            ProductCategory.MEAT: [ProductCategory.VEGETABLES, ProductCategory.HERBS],
            ProductCategory.EGGS: [ProductCategory.DAIRY, ProductCategory.BAKED_GOODS]
        }

        for category in cart_categories:
            complement_categories = complementary_rules.get(category, [])

            for complement_category in complement_categories:
                complement_products = [
                    p for p in self.products.values()
                    if (p.category == complement_category and
                        p.product_id not in cart_product_ids and
                        p.current_stock > 0 and
                        datetime.now().month in p.seasonal_availability)
                ]

                if complement_products:
                    # Pick top 2 products by popularity (simplified)
                    for product in complement_products[:2]:
                        price = await self.calculate_seasonal_price(product.product_id)
                        suggestions.append({
                            'product_id': product.product_id,
                            'name': product.name,
                            'category': product.category.value,
                            'price': float(price),
                            'unit': product.unit,
                            'reason': f"Complements your {category.value} selection"
                        })

        return suggestions[:5]  # Limit to 5 suggestions

# Example usage and testing
async def main():
    """Example usage of Farm Shop Sales system"""
    farm_config = {
        'name': 'Green Valley Farm',
        'vat_rate': 0.09
    }

    sales_system = FarmShopSales(farm_config)
    await sales_system.initialize()

    # Register a customer
    customer_data = {
        'name': 'John Smith',
        'email': 'john@example.com',
        'phone': '+31612345678',
        'csa_member': True
    }
    customer_id = await sales_system.register_customer(customer_data)

    # Process a sale
    sale_data = {
        'customer_id': customer_id,
        'sale_type': 'farm_shop',
        'payment_method': 'card',
        'location': 'Green Valley Farm Shop',
        'items': [
            {'product_id': list(sales_system.products.keys())[0], 'quantity': 2.5},
            {'product_id': list(sales_system.products.keys())[1], 'quantity': 1}
        ]
    }

    sale_id = await sales_system.process_sale(sale_data)
    print(f"Processed sale: {sale_id}")

    # Generate sales report
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    report = await sales_system.generate_sales_report(start_date, end_date)
    print("Sales Report:", report)

    # Check inventory status
    inventory = await sales_system.get_inventory_status()
    print("Inventory Status:", inventory)

if __name__ == "__main__":
    asyncio.run(main())