"""
Stock Query & Alternative Finder Agent

This agent handles real-time inventory queries, suggests alternatives when items
are out of stock, and manages customer hold requests. Perfect for boutique owners
who need instant stock information while serving customers.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import re

@dataclass
class InventoryItem:
    """Represents a single inventory item with all relevant details."""
    sku: str
    name: str
    category: str
    size: str
    color: str
    price: float
    quantity: int
    brand: str
    description: str
    tags: List[str]
    last_sold: Optional[datetime] = None
    hold_until: Optional[datetime] = None
    held_for: Optional[str] = None

@dataclass
class StockQuery:
    """Represents a customer stock inquiry."""
    customer_name: str
    item_description: str
    size_preference: Optional[str] = None
    color_preference: Optional[str] = None
    price_range: Optional[Tuple[float, float]] = None
    urgency: str = "normal"  # normal, urgent, casual

class StockAssistant:
    """
    AI-powered stock assistant that handles inventory queries and suggestions.

    Key Features:
    - Real-time stock checking
    - Smart alternative suggestions
    - Hold management
    - Back-in-stock notifications
    - Personal shopping recommendations
    """

    def __init__(self, inventory_file: str = "data/inventory.csv"):
        self.inventory_file = inventory_file
        self.inventory = self._load_inventory()
        self.hold_requests = {}
        self.notification_list = {}

    def _load_inventory(self) -> List[InventoryItem]:
        """Load inventory from CSV file."""
        try:
            df = pd.read_csv(self.inventory_file)
            inventory = []

            for _, row in df.iterrows():
                item = InventoryItem(
                    sku=row['sku'],
                    name=row['name'],
                    category=row['category'],
                    size=row.get('size', ''),
                    color=row.get('color', ''),
                    price=float(row['price']),
                    quantity=int(row['quantity']),
                    brand=row.get('brand', ''),
                    description=row.get('description', ''),
                    tags=row.get('tags', '').split(',') if row.get('tags') else [],
                    last_sold=pd.to_datetime(row.get('last_sold')) if row.get('last_sold') else None
                )
                inventory.append(item)

            return inventory
        except FileNotFoundError:
            print(f"Inventory file {self.inventory_file} not found. Using empty inventory.")
            return []

    def search_items(self, query: str, size: str = None, color: str = None) -> List[InventoryItem]:
        """Search inventory based on description, size, and color."""
        results = []
        query_words = query.lower().split()

        for item in self.inventory:
            if item.quantity <= 0:
                continue

            # Check if item matches query
            item_text = f"{item.name} {item.description} {item.brand} {' '.join(item.tags)}".lower()

            # Must match at least some query words
            matches = sum(1 for word in query_words if word in item_text)
            if matches == 0:
                continue

            # Filter by size if specified
            if size and item.size.lower() != size.lower():
                continue

            # Filter by color if specified
            if color and color.lower() not in item.color.lower():
                continue

            results.append(item)

        # Sort by relevance (number of matching words)
        results.sort(key=lambda x: sum(1 for word in query_words
                                     if word in f"{x.name} {x.description}".lower()),
                    reverse=True)

        return results

    def find_alternatives(self, original_item: InventoryItem, limit: int = 3) -> List[InventoryItem]:
        """Find similar items when original is out of stock."""
        alternatives = []

        for item in self.inventory:
            if item.sku == original_item.sku or item.quantity <= 0:
                continue

            similarity_score = 0

            # Same category gets high score
            if item.category == original_item.category:
                similarity_score += 3

            # Similar price range (+/- 30%)
            price_diff = abs(item.price - original_item.price) / original_item.price
            if price_diff <= 0.3:
                similarity_score += 2

            # Similar brand
            if item.brand == original_item.brand:
                similarity_score += 2

            # Similar tags
            common_tags = set(item.tags) & set(original_item.tags)
            similarity_score += len(common_tags)

            # Similar name words
            original_words = set(original_item.name.lower().split())
            item_words = set(item.name.lower().split())
            common_words = original_words & item_words
            similarity_score += len(common_words)

            if similarity_score > 0:
                alternatives.append((item, similarity_score))

        # Sort by similarity score and return top alternatives
        alternatives.sort(key=lambda x: x[1], reverse=True)
        return [item for item, score in alternatives[:limit]]

    def place_hold(self, item: InventoryItem, customer_name: str, duration_hours: int = 2) -> bool:
        """Place a hold on an item for a customer."""
        if item.quantity <= 0:
            return False

        hold_until = datetime.now() + timedelta(hours=duration_hours)
        item.hold_until = hold_until
        item.held_for = customer_name

        # Store in hold requests for tracking
        self.hold_requests[item.sku] = {
            'customer': customer_name,
            'hold_until': hold_until,
            'item_name': item.name
        }

        return True

    def check_holds(self) -> List[Dict]:
        """Check for expired holds and return list of items to release."""
        now = datetime.now()
        expired_holds = []

        for sku, hold_info in list(self.hold_requests.items()):
            if now > hold_info['hold_until']:
                # Release the hold
                for item in self.inventory:
                    if item.sku == sku:
                        item.hold_until = None
                        item.held_for = None
                        break

                expired_holds.append(hold_info)
                del self.hold_requests[sku]

        return expired_holds

    def add_notification_request(self, customer_email: str, item_description: str, size: str = None):
        """Add customer to notification list for when item becomes available."""
        key = f"{item_description}_{size}".lower()
        if key not in self.notification_list:
            self.notification_list[key] = []

        self.notification_list[key].append({
            'email': customer_email,
            'requested_at': datetime.now(),
            'item_description': item_description,
            'size': size
        })

    def process_stock_query(self, query: StockQuery) -> Dict:
        """
        Process a customer stock query and return comprehensive response.

        Returns a dictionary with:
        - available_items: List of matching items in stock
        - alternatives: List of alternative items if nothing matches exactly
        - hold_offer: Whether we can hold items
        - response_text: Natural language response for customer
        """

        # Search for matching items
        available_items = self.search_items(
            query.item_description,
            query.size_preference,
            query.color_preference
        )

        # Filter by price range if specified
        if query.price_range:
            min_price, max_price = query.price_range
            available_items = [item for item in available_items
                             if min_price <= item.price <= max_price]

        response = {
            'available_items': available_items,
            'alternatives': [],
            'hold_offer': False,
            'response_text': ''
        }

        if available_items:
            # We have exact matches
            primary_item = available_items[0]
            response['hold_offer'] = True

            if len(available_items) == 1:
                response['response_text'] = (
                    f"Great news! I have the {primary_item.name} in stock "
                    f"({primary_item.color} {primary_item.size}) for €{primary_item.price:.2f}. "
                    f"I can hold it for you for 2 hours if you'd like."
                )
            else:
                response['response_text'] = (
                    f"Perfect! I have {len(available_items)} options for you: "
                    f"{', '.join([f'{item.name} ({item.color} {item.size}, €{item.price:.2f})' for item in available_items[:3]])}. "
                    f"Would you like me to hold any of these for you?"
                )
        else:
            # No exact matches - suggest alternatives
            # Try to find the closest match for alternatives
            all_items = [item for item in self.inventory if item.quantity > 0]
            if all_items:
                # Use first available item as reference for alternatives
                reference_item = all_items[0]
                # Try to find something similar to what they're looking for
                for item in all_items:
                    if any(word in item.name.lower() for word in query.item_description.lower().split()):
                        reference_item = item
                        break

                alternatives = self.find_alternatives(reference_item)
                response['alternatives'] = alternatives

                if alternatives:
                    response['response_text'] = (
                        f"I don't have exactly what you're looking for in stock right now, "
                        f"but I have some beautiful alternatives: "
                        f"{', '.join([f'{item.name} ({item.color} {item.size}, €{item.price:.2f})' for item in alternatives[:2]])}. "
                        f"Would you like to see photos or set up a notification for when your preferred item arrives?"
                    )
                else:
                    response['response_text'] = (
                        f"I don't currently have that item in stock, but I'd be happy to "
                        f"add you to my notification list for when it arrives. I also get "
                        f"new arrivals every week - would you like me to show you what's new?"
                    )
            else:
                response['response_text'] = (
                    "I'm currently updating my inventory. Could you give me a few minutes "
                    "or would you prefer I call you back when I have the latest stock information?"
                )

        return response

    def generate_daily_stock_report(self) -> Dict:
        """Generate daily stock report for store owner."""
        now = datetime.now()

        # Low stock items (quantity <= 2)
        low_stock = [item for item in self.inventory if 0 < item.quantity <= 2]

        # Out of stock items
        out_of_stock = [item for item in self.inventory if item.quantity == 0]

        # Items on hold
        items_on_hold = [item for item in self.inventory if item.held_for]

        # Fast movers (items sold in last 7 days)
        week_ago = now - timedelta(days=7)
        fast_movers = [item for item in self.inventory
                      if item.last_sold and item.last_sold >= week_ago]

        return {
            'date': now.strftime('%Y-%m-%d'),
            'total_items': len(self.inventory),
            'total_value': sum(item.price * item.quantity for item in self.inventory),
            'low_stock_items': len(low_stock),
            'out_of_stock_items': len(out_of_stock),
            'items_on_hold': len(items_on_hold),
            'fast_movers': len(fast_movers),
            'low_stock_details': [
                f"{item.name} ({item.size} {item.color}) - {item.quantity} left"
                for item in low_stock[:5]
            ],
            'reorder_suggestions': [
                f"{item.name} - Last sold: {item.last_sold.strftime('%Y-%m-%d') if item.last_sold else 'Unknown'}"
                for item in out_of_stock if item.last_sold and item.last_sold >= week_ago
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the stock assistant
    assistant = StockAssistant()

    # Example query
    query = StockQuery(
        customer_name="Sarah",
        item_description="floral midi dress",
        size_preference="12",
        urgency="normal"
    )

    # Process the query
    response = assistant.process_stock_query(query)

    print("Stock Query Response:")
    print(response['response_text'])

    if response['available_items']:
        print(f"\nAvailable items: {len(response['available_items'])}")
        for item in response['available_items'][:3]:
            print(f"- {item.name} ({item.size} {item.color}) - €{item.price:.2f}")

    # Generate daily report
    report = assistant.generate_daily_stock_report()
    print(f"\nDaily Stock Report for {report['date']}:")
    print(f"Total items: {report['total_items']}")
    print(f"Total value: €{report['total_value']:.2f}")
    print(f"Low stock alerts: {report['low_stock_items']}")
    print(f"Items on hold: {report['items_on_hold']}")