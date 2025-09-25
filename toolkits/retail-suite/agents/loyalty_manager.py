"""
Loyalty & Customer Relations Agent

Manages digital loyalty programs, tracks customer purchase history,
sends personalized offers, and builds lasting customer relationships.
No more lost loyalty cards or forgotten birthdays!
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import uuid

@dataclass
class Customer:
    """Represents a customer with loyalty program data."""
    customer_id: str
    name: str
    email: str
    phone: str
    birthday: Optional[datetime] = None
    join_date: datetime = field(default_factory=datetime.now)
    total_spent: float = 0.0
    total_visits: int = 0
    points_balance: int = 0
    tier: str = "Bronze"  # Bronze, Silver, Gold, VIP
    preferences: Dict = field(default_factory=dict)
    last_visit: Optional[datetime] = None
    last_purchase_amount: float = 0.0
    favorite_categories: List[str] = field(default_factory=list)
    notes: str = ""

@dataclass
class Purchase:
    """Represents a customer purchase."""
    purchase_id: str
    customer_id: str
    date: datetime
    items: List[Dict]  # [{name, price, category, sku}]
    total_amount: float
    points_earned: int
    payment_method: str

@dataclass
class LoyaltyReward:
    """Represents a loyalty reward or offer."""
    reward_id: str
    customer_id: str
    reward_type: str  # discount, free_item, early_access, birthday_gift
    value: float
    description: str
    expiry_date: datetime
    used: bool = False
    used_date: Optional[datetime] = None

class LoyaltyManager:
    """
    AI-powered loyalty and customer relationship management system.

    Key Features:
    - Digital loyalty tracking (no more lost cards!)
    - Automatic points calculation and tier management
    - Personalized birthday and anniversary offers
    - VIP early access to new collections
    - Purchase history analysis for recommendations
    - Automated customer communication
    """

    def __init__(self, customers_file: str = "data/customers.csv",
                 purchases_file: str = "data/purchases.csv"):
        self.customers_file = customers_file
        self.purchases_file = purchases_file
        self.customers = self._load_customers()
        self.purchases = self._load_purchases()
        self.rewards = []

        # Loyalty program configuration
        self.points_per_euro = 1  # 1 point per €1 spent
        self.tier_thresholds = {
            'Bronze': 0,
            'Silver': 500,   # €500 total spent
            'Gold': 1500,    # €1500 total spent
            'VIP': 3000      # €3000 total spent
        }
        self.tier_benefits = {
            'Bronze': {'discount': 0, 'early_access_days': 0, 'birthday_bonus': 50},
            'Silver': {'discount': 0.05, 'early_access_days': 1, 'birthday_bonus': 100},
            'Gold': {'discount': 0.10, 'early_access_days': 3, 'birthday_bonus': 200},
            'VIP': {'discount': 0.15, 'early_access_days': 7, 'birthday_bonus': 300}
        }

    def _load_customers(self) -> Dict[str, Customer]:
        """Load customers from CSV file."""
        customers = {}
        try:
            df = pd.read_csv(self.customers_file)
            for _, row in df.iterrows():
                customer = Customer(
                    customer_id=row['customer_id'],
                    name=row['name'],
                    email=row['email'],
                    phone=row.get('phone', ''),
                    birthday=pd.to_datetime(row.get('birthday')) if row.get('birthday') else None,
                    join_date=pd.to_datetime(row.get('join_date', datetime.now())),
                    total_spent=float(row.get('total_spent', 0)),
                    total_visits=int(row.get('total_visits', 0)),
                    points_balance=int(row.get('points_balance', 0)),
                    tier=row.get('tier', 'Bronze'),
                    last_visit=pd.to_datetime(row.get('last_visit')) if row.get('last_visit') else None,
                    favorite_categories=row.get('favorite_categories', '').split(',') if row.get('favorite_categories') else [],
                    notes=row.get('notes', '')
                )
                customers[customer.customer_id] = customer
        except FileNotFoundError:
            print(f"Customers file {self.customers_file} not found. Starting with empty database.")

        return customers

    def _load_purchases(self) -> List[Purchase]:
        """Load purchase history from CSV file."""
        purchases = []
        try:
            df = pd.read_csv(self.purchases_file)
            for _, row in df.iterrows():
                purchase = Purchase(
                    purchase_id=row['purchase_id'],
                    customer_id=row['customer_id'],
                    date=pd.to_datetime(row['date']),
                    items=json.loads(row.get('items', '[]')),
                    total_amount=float(row['total_amount']),
                    points_earned=int(row.get('points_earned', 0)),
                    payment_method=row.get('payment_method', 'cash')
                )
                purchases.append(purchase)
        except FileNotFoundError:
            print(f"Purchases file {self.purchases_file} not found. Starting with empty history.")

        return purchases

    def register_customer(self, name: str, email: str, phone: str = "",
                         birthday: str = "") -> Customer:
        """Register a new customer in the loyalty program."""
        customer_id = str(uuid.uuid4())[:8]

        birthday_date = None
        if birthday:
            try:
                birthday_date = datetime.strptime(birthday, '%Y-%m-%d')
            except ValueError:
                print(f"Invalid birthday format: {birthday}. Use YYYY-MM-DD")

        customer = Customer(
            customer_id=customer_id,
            name=name,
            email=email,
            phone=phone,
            birthday=birthday_date
        )

        self.customers[customer_id] = customer
        return customer

    def process_purchase(self, customer_id: str, items: List[Dict],
                        total_amount: float, payment_method: str = "card") -> Dict:
        """
        Process a customer purchase and update loyalty data.

        Args:
            customer_id: Customer identifier
            items: List of items purchased [{name, price, category, sku}]
            total_amount: Total purchase amount
            payment_method: How customer paid

        Returns:
            Dictionary with purchase summary and loyalty updates
        """
        if customer_id not in self.customers:
            return {"error": f"Customer {customer_id} not found"}

        customer = self.customers[customer_id]

        # Create purchase record
        purchase = Purchase(
            purchase_id=str(uuid.uuid4())[:8],
            customer_id=customer_id,
            date=datetime.now(),
            items=items,
            total_amount=total_amount,
            points_earned=int(total_amount * self.points_per_euro),
            payment_method=payment_method
        )

        self.purchases.append(purchase)

        # Update customer data
        old_tier = customer.tier
        customer.total_spent += total_amount
        customer.total_visits += 1
        customer.points_balance += purchase.points_earned
        customer.last_visit = datetime.now()
        customer.last_purchase_amount = total_amount

        # Update favorite categories
        categories = [item.get('category', '') for item in items if item.get('category')]
        for category in categories:
            if category and category not in customer.favorite_categories:
                customer.favorite_categories.append(category)

        # Check for tier upgrade
        new_tier = self._calculate_tier(customer.total_spent)
        tier_upgraded = new_tier != old_tier
        customer.tier = new_tier

        # Generate response
        response = {
            'purchase_id': purchase.purchase_id,
            'points_earned': purchase.points_earned,
            'total_points': customer.points_balance,
            'current_tier': customer.tier,
            'tier_upgraded': tier_upgraded,
            'next_tier_progress': self._get_next_tier_progress(customer),
            'personalized_message': self._generate_purchase_message(customer, purchase, tier_upgraded)
        }

        return response

    def _calculate_tier(self, total_spent: float) -> str:
        """Calculate customer tier based on total spending."""
        for tier in ['VIP', 'Gold', 'Silver', 'Bronze']:
            if total_spent >= self.tier_thresholds[tier]:
                return tier
        return 'Bronze'

    def _get_next_tier_progress(self, customer: Customer) -> Dict:
        """Calculate progress towards next tier."""
        current_threshold = self.tier_thresholds[customer.tier]
        next_tiers = ['Silver', 'Gold', 'VIP']

        for tier in next_tiers:
            if self.tier_thresholds[tier] > current_threshold:
                needed = self.tier_thresholds[tier] - customer.total_spent
                return {
                    'next_tier': tier,
                    'amount_needed': max(0, needed),
                    'progress_percentage': min(100, (customer.total_spent / self.tier_thresholds[tier]) * 100)
                }

        return {'next_tier': None, 'amount_needed': 0, 'progress_percentage': 100}

    def _generate_purchase_message(self, customer: Customer, purchase: Purchase,
                                 tier_upgraded: bool) -> str:
        """Generate personalized thank you message after purchase."""
        messages = []

        # Basic thank you
        messages.append(f"Thank you for your purchase, {customer.name}!")

        # Points earned
        messages.append(f"You earned {purchase.points_earned} points today.")

        # Tier upgrade celebration
        if tier_upgraded:
            benefits = self.tier_benefits[customer.tier]
            messages.append(f"🎉 Congratulations! You've been upgraded to {customer.tier} tier!")
            if benefits['discount'] > 0:
                messages.append(f"You now get {benefits['discount']*100:.0f}% off all purchases!")
            if benefits['early_access_days'] > 0:
                messages.append(f"You get {benefits['early_access_days']} days early access to new arrivals!")

        # Progress to next tier
        progress = self._get_next_tier_progress(customer)
        if progress['next_tier']:
            messages.append(f"You're €{progress['amount_needed']:.0f} away from {progress['next_tier']} tier!")

        return " ".join(messages)

    def get_birthday_customers(self, days_ahead: int = 7) -> List[Customer]:
        """Get customers with birthdays in the next N days."""
        today = datetime.now().date()
        birthday_customers = []

        for customer in self.customers.values():
            if not customer.birthday:
                continue

            # Check if birthday is in the next N days (this year or next year)
            this_year_birthday = customer.birthday.replace(year=today.year).date()
            next_year_birthday = customer.birthday.replace(year=today.year + 1).date()

            days_to_birthday = min(
                (this_year_birthday - today).days,
                (next_year_birthday - today).days
            )

            if 0 <= days_to_birthday <= days_ahead:
                birthday_customers.append(customer)

        return birthday_customers

    def generate_birthday_offer(self, customer: Customer) -> LoyaltyReward:
        """Generate personalized birthday offer for customer."""
        bonus_points = self.tier_benefits[customer.tier]['birthday_bonus']

        reward = LoyaltyReward(
            reward_id=str(uuid.uuid4())[:8],
            customer_id=customer.customer_id,
            reward_type="birthday_gift",
            value=bonus_points,
            description=f"Happy Birthday! Here's {bonus_points} bonus points as our gift to you!",
            expiry_date=datetime.now() + timedelta(days=30)
        )

        self.rewards.append(reward)
        return reward

    def get_vip_customers(self) -> List[Customer]:
        """Get all VIP tier customers for special treatment."""
        return [customer for customer in self.customers.values() if customer.tier == 'VIP']

    def get_at_risk_customers(self, days_inactive: int = 60) -> List[Customer]:
        """Identify customers who haven't visited recently."""
        cutoff_date = datetime.now() - timedelta(days=days_inactive)
        at_risk = []

        for customer in self.customers.values():
            if customer.last_visit and customer.last_visit < cutoff_date:
                at_risk.append(customer)

        # Sort by total spent (focus on valuable customers first)
        at_risk.sort(key=lambda x: x.total_spent, reverse=True)
        return at_risk

    def generate_win_back_offer(self, customer: Customer) -> LoyaltyReward:
        """Generate win-back offer for inactive customers."""
        # Offer based on their historical spending
        if customer.total_spent > 1000:
            discount = 0.20  # 20% off for high-value customers
        elif customer.total_spent > 500:
            discount = 0.15  # 15% off for medium-value customers
        else:
            discount = 0.10  # 10% off for others

        reward = LoyaltyReward(
            reward_id=str(uuid.uuid4())[:8],
            customer_id=customer.customer_id,
            reward_type="win_back",
            value=discount,
            description=f"We miss you! Come back and get {discount*100:.0f}% off your next purchase.",
            expiry_date=datetime.now() + timedelta(days=14)
        )

        self.rewards.append(reward)
        return reward

    def get_customer_recommendations(self, customer_id: str) -> List[str]:
        """Generate personalized product recommendations for customer."""
        if customer_id not in self.customers:
            return []

        customer = self.customers[customer_id]
        recommendations = []

        # Based on favorite categories
        if customer.favorite_categories:
            recommendations.append(
                f"New arrivals in {', '.join(customer.favorite_categories[:2])} just came in!"
            )

        # Based on purchase history
        recent_purchases = [p for p in self.purchases
                          if p.customer_id == customer_id and
                          p.date > datetime.now() - timedelta(days=90)]

        if recent_purchases:
            recent_items = []
            for purchase in recent_purchases:
                recent_items.extend([item['name'] for item in purchase.items])

            recommendations.append(
                f"Based on your recent purchases, you might like items that complement {recent_items[-1]}."
            )

        # Tier-based recommendations
        if customer.tier in ['Gold', 'VIP']:
            recommendations.append(
                "As a valued customer, you get early access to our premium collection!"
            )

        return recommendations

    def generate_daily_loyalty_report(self) -> Dict:
        """Generate daily loyalty program report for store owner."""
        today = datetime.now().date()

        # New customers today
        new_customers_today = [c for c in self.customers.values()
                              if c.join_date.date() == today]

        # Purchases today
        purchases_today = [p for p in self.purchases if p.date.date() == today]

        # Birthday customers this week
        birthday_customers = self.get_birthday_customers(7)

        # At-risk customers
        at_risk = self.get_at_risk_customers(60)

        # Tier distribution
        tier_counts = {}
        for tier in ['Bronze', 'Silver', 'Gold', 'VIP']:
            tier_counts[tier] = len([c for c in self.customers.values() if c.tier == tier])

        return {
            'date': today.strftime('%Y-%m-%d'),
            'total_customers': len(self.customers),
            'new_customers_today': len(new_customers_today),
            'purchases_today': len(purchases_today),
            'revenue_today': sum(p.total_amount for p in purchases_today),
            'points_given_today': sum(p.points_earned for p in purchases_today),
            'birthday_customers_this_week': len(birthday_customers),
            'at_risk_customers': len(at_risk),
            'tier_distribution': tier_counts,
            'vip_customers': len([c for c in self.customers.values() if c.tier == 'VIP']),
            'average_transaction': sum(p.total_amount for p in purchases_today) / max(1, len(purchases_today))
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize loyalty manager
    loyalty = LoyaltyManager()

    # Register a new customer
    customer = loyalty.register_customer(
        name="Sarah Johnson",
        email="sarah@email.com",
        phone="+353-1-234-5678",
        birthday="1985-06-15"
    )

    print(f"Registered customer: {customer.name} (ID: {customer.customer_id})")

    # Process a purchase
    items = [
        {"name": "Floral Midi Dress", "price": 89.99, "category": "dresses", "sku": "DRESS001"},
        {"name": "Leather Handbag", "price": 129.99, "category": "accessories", "sku": "BAG001"}
    ]

    result = loyalty.process_purchase(
        customer_id=customer.customer_id,
        items=items,
        total_amount=219.98,
        payment_method="card"
    )

    print(f"\nPurchase processed:")
    print(f"Points earned: {result['points_earned']}")
    print(f"Message: {result['personalized_message']}")

    # Generate daily report
    report = loyalty.generate_daily_loyalty_report()
    print(f"\nDaily Loyalty Report for {report['date']}:")
    print(f"Total customers: {report['total_customers']}")
    print(f"Revenue today: €{report['revenue_today']:.2f}")
    print(f"VIP customers: {report['vip_customers']}")
    print(f"Tier distribution: {report['tier_distribution']}")