"""
Customer Experience Hub AI Agent

Handles customer communication, loyalty programs, feedback management,
and personalized recommendations for enhanced customer engagement.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class CustomerTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class FeedbackType(Enum):
    COMPLIMENT = "compliment"
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"
    REVIEW = "review"

class NotificationType(Enum):
    ORDER_STATUS = "order_status"
    PROMOTION = "promotion"
    LOYALTY_REWARD = "loyalty_reward"
    DELIVERY_UPDATE = "delivery_update"
    FEEDBACK_REQUEST = "feedback_request"

@dataclass
class Customer:
    id: str
    name: str
    email: str
    phone: str
    address: str
    registration_date: datetime
    tier: CustomerTier
    loyalty_points: int
    total_orders: int
    total_spent: float
    favorite_items: List[str]
    dietary_restrictions: List[str]
    communication_preferences: Dict[str, bool]
    last_order_date: Optional[datetime]

@dataclass
class LoyaltyReward:
    id: str
    customer_id: str
    points_earned: int
    points_redeemed: int
    reward_type: str
    description: str
    created_date: datetime
    expiry_date: Optional[datetime]
    used: bool

@dataclass
class Feedback:
    id: str
    customer_id: str
    order_id: Optional[str]
    type: FeedbackType
    rating: Optional[int]  # 1-5 stars
    subject: str
    message: str
    created_date: datetime
    status: str  # pending, acknowledged, resolved
    response: Optional[str]
    response_date: Optional[datetime]

@dataclass
class Notification:
    id: str
    customer_id: str
    type: NotificationType
    title: str
    message: str
    sent_date: datetime
    read: bool
    clicked: bool

class CustomerExperienceHub:
    """
    AI-powered customer experience management system that handles
    communication, loyalty programs, feedback, and personalization.
    """

    def __init__(self):
        self.customers: Dict[str, Customer] = {}
        self.loyalty_rewards: Dict[str, LoyaltyReward] = {}
        self.feedback: Dict[str, Feedback] = {}
        self.notifications: Dict[str, Notification] = {}
        self.loyalty_tiers = {
            CustomerTier.BRONZE: {"min_spent": 0, "points_multiplier": 1.0},
            CustomerTier.SILVER: {"min_spent": 500, "points_multiplier": 1.2},
            CustomerTier.GOLD: {"min_spent": 1500, "points_multiplier": 1.5},
            CustomerTier.PLATINUM: {"min_spent": 3000, "points_multiplier": 2.0}
        }

    def register_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """Register new customer in the system"""
        customer_id = f"cust_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.customers) + 1}"

        customer = Customer(
            id=customer_id,
            name=customer_data['name'],
            email=customer_data['email'],
            phone=customer_data['phone'],
            address=customer_data['address'],
            registration_date=datetime.now(),
            tier=CustomerTier.BRONZE,
            loyalty_points=0,
            total_orders=0,
            total_spent=0.0,
            favorite_items=[],
            dietary_restrictions=customer_data.get('dietary_restrictions', []),
            communication_preferences={
                'email': True,
                'sms': True,
                'push': True,
                'promotional': customer_data.get('accept_marketing', True)
            },
            last_order_date=None
        )

        self.customers[customer_id] = customer

        # Send welcome notification
        asyncio.create_task(self._send_welcome_message(customer))

        logger.info(f"Registered new customer: {customer.name} ({customer_id})")
        return customer

    async def _send_welcome_message(self, customer: Customer) -> None:
        """Send welcome message to new customer"""
        await self.send_notification(
            customer.id,
            NotificationType.PROMOTION,
            "Welcome to our restaurant!",
            f"Hi {customer.name}! Get 10% off your first order with code WELCOME10. Start earning loyalty points with every order!"
        )

    async def update_customer_after_order(self, customer_id: str, order_value: float,
                                        items: List[str]) -> None:
        """Update customer data after order completion"""
        if customer_id not in self.customers:
            return

        customer = self.customers[customer_id]

        # Update order statistics
        customer.total_orders += 1
        customer.total_spent += order_value
        customer.last_order_date = datetime.now()

        # Update favorite items (simple frequency-based)
        for item in items:
            if item not in customer.favorite_items:
                customer.favorite_items.append(item)
            # Keep only top 5 favorites (in real implementation, use proper ranking)
            customer.favorite_items = customer.favorite_items[:5]

        # Calculate loyalty points
        points_earned = await self._calculate_loyalty_points(customer, order_value)
        customer.loyalty_points += points_earned

        # Check for tier upgrade
        new_tier = self._calculate_customer_tier(customer.total_spent)
        if new_tier != customer.tier:
            old_tier = customer.tier
            customer.tier = new_tier
            await self._notify_tier_upgrade(customer, old_tier, new_tier)

        # Create loyalty reward record
        if points_earned > 0:
            await self._create_loyalty_record(customer_id, points_earned, order_value)

        logger.info(f"Updated customer {customer.name}: +{points_earned} points, tier: {customer.tier.value}")

    async def _calculate_loyalty_points(self, customer: Customer, order_value: float) -> int:
        """Calculate loyalty points for order"""
        base_points = int(order_value)  # 1 point per euro
        tier_multiplier = self.loyalty_tiers[customer.tier]["points_multiplier"]

        # Bonus points for dietary restrictions (encourage inclusive ordering)
        dietary_bonus = 5 if customer.dietary_restrictions else 0

        # Birthday bonus (check if within 7 days of birthday)
        birthday_bonus = 0
        # In real implementation, check actual birthday

        total_points = int((base_points * tier_multiplier) + dietary_bonus + birthday_bonus)
        return total_points

    def _calculate_customer_tier(self, total_spent: float) -> CustomerTier:
        """Calculate customer tier based on total spending"""
        for tier in reversed(list(CustomerTier)):
            if total_spent >= self.loyalty_tiers[tier]["min_spent"]:
                return tier
        return CustomerTier.BRONZE

    async def _notify_tier_upgrade(self, customer: Customer, old_tier: CustomerTier,
                                 new_tier: CustomerTier) -> None:
        """Notify customer of tier upgrade"""
        await self.send_notification(
            customer.id,
            NotificationType.LOYALTY_REWARD,
            f"Congratulations! You're now {new_tier.value.title()}!",
            f"You've been upgraded from {old_tier.value.title()} to {new_tier.value.title()}! "
            f"Enjoy {self.loyalty_tiers[new_tier]['points_multiplier']}x points on all orders."
        )

    async def _create_loyalty_record(self, customer_id: str, points_earned: int,
                                   order_value: float) -> None:
        """Create loyalty reward record"""
        reward_id = f"reward_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}"

        reward = LoyaltyReward(
            id=reward_id,
            customer_id=customer_id,
            points_earned=points_earned,
            points_redeemed=0,
            reward_type="order_points",
            description=f"Points earned from order (€{order_value:.2f})",
            created_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=365),  # Points expire in 1 year
            used=False
        )

        self.loyalty_rewards[reward_id] = reward

    async def send_notification(self, customer_id: str, notification_type: NotificationType,
                              title: str, message: str) -> str:
        """Send notification to customer"""
        if customer_id not in self.customers:
            return ""

        customer = self.customers[customer_id]

        # Check communication preferences
        if notification_type == NotificationType.PROMOTION:
            if not customer.communication_preferences.get('promotional', True):
                return ""

        notification_id = f"notif_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}"

        notification = Notification(
            id=notification_id,
            customer_id=customer_id,
            type=notification_type,
            title=title,
            message=message,
            sent_date=datetime.now(),
            read=False,
            clicked=False
        )

        self.notifications[notification_id] = notification

        # Send via preferred channels
        await self._deliver_notification(customer, notification)

        logger.info(f"Sent notification to {customer.name}: {title}")
        return notification_id

    async def _deliver_notification(self, customer: Customer, notification: Notification) -> None:
        """Deliver notification via customer's preferred channels"""
        preferences = customer.communication_preferences

        if preferences.get('email', True):
            await self._send_email(customer.email, notification.title, notification.message)

        if preferences.get('sms', True):
            await self._send_sms(customer.phone, notification.message)

        if preferences.get('push', True):
            await self._send_push_notification(customer.id, notification.title, notification.message)

    async def _send_email(self, email: str, subject: str, message: str) -> None:
        """Send email notification"""
        # In real implementation, use email service
        logger.info(f"Email sent to {email}: {subject}")

    async def _send_sms(self, phone: str, message: str) -> None:
        """Send SMS notification"""
        # In real implementation, use SMS service
        logger.info(f"SMS sent to {phone}: {message[:50]}...")

    async def _send_push_notification(self, customer_id: str, title: str, message: str) -> None:
        """Send push notification"""
        # In real implementation, use push notification service
        logger.info(f"Push notification sent to {customer_id}: {title}")

    async def collect_feedback(self, customer_id: str, feedback_data: Dict[str, Any]) -> str:
        """Collect customer feedback"""
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}"

        feedback = Feedback(
            id=feedback_id,
            customer_id=customer_id,
            order_id=feedback_data.get('order_id'),
            type=FeedbackType(feedback_data['type']),
            rating=feedback_data.get('rating'),
            subject=feedback_data['subject'],
            message=feedback_data['message'],
            created_date=datetime.now(),
            status="pending",
            response=None,
            response_date=None
        )

        self.feedback[feedback_id] = feedback

        # Auto-process based on type and content
        await self._process_feedback(feedback)

        logger.info(f"Collected feedback from customer {customer_id}: {feedback.type.value}")
        return feedback_id

    async def _process_feedback(self, feedback: Feedback) -> None:
        """Process feedback using AI sentiment analysis"""
        # Auto-acknowledge all feedback
        await self.send_notification(
            feedback.customer_id,
            NotificationType.FEEDBACK_REQUEST,
            "Thank you for your feedback!",
            "We've received your feedback and our team will review it shortly. Your opinion helps us improve!"
        )

        # Priority handling for complaints
        if feedback.type == FeedbackType.COMPLAINT:
            await self._handle_complaint(feedback)
        elif feedback.type == FeedbackType.COMPLIMENT:
            await self._handle_compliment(feedback)

    async def _handle_complaint(self, feedback: Feedback) -> None:
        """Handle customer complaints with priority"""
        # Extract complaint severity (in real implementation, use NLP)
        severity = "medium"  # Default

        if any(word in feedback.message.lower() for word in ["terrible", "awful", "never again", "disgusting"]):
            severity = "high"
        elif any(word in feedback.message.lower() for word in ["disappointed", "expected better", "not happy"]):
            severity = "medium"
        else:
            severity = "low"

        # Assign to appropriate team member based on severity
        if severity == "high":
            # Immediate manager attention
            logger.warning(f"HIGH PRIORITY COMPLAINT: Feedback {feedback.id} requires immediate attention")

        # Auto-response for complaints
        response = await self._generate_complaint_response(feedback)
        await self.respond_to_feedback(feedback.id, response)

        # Offer compensation for high-severity complaints
        if severity == "high":
            await self._offer_compensation(feedback.customer_id)

    async def _handle_compliment(self, feedback: Feedback) -> None:
        """Handle positive feedback"""
        customer = self.customers[feedback.customer_id]

        # Award bonus loyalty points for positive feedback
        bonus_points = 25
        customer.loyalty_points += bonus_points

        await self.send_notification(
            feedback.customer_id,
            NotificationType.LOYALTY_REWARD,
            "Bonus points for your feedback!",
            f"Thank you for your kind words! We've added {bonus_points} bonus points to your account."
        )

    async def _generate_complaint_response(self, feedback: Feedback) -> str:
        """Generate personalized response to complaint"""
        customer = self.customers[feedback.customer_id]

        # Template-based response (in real implementation, use AI)
        responses = {
            "food_quality": f"Dear {customer.name}, we sincerely apologize for the food quality issue. "
                          f"We take this very seriously and are investigating with our kitchen team.",
            "delivery": f"Dear {customer.name}, we're sorry about the delivery experience. "
                       f"We're working with our delivery partners to improve service.",
            "service": f"Dear {customer.name}, we apologize for the poor service experience. "
                      f"We're reviewing our processes to ensure this doesn't happen again."
        }

        # Simple keyword matching for demo
        for category, response in responses.items():
            if category in feedback.message.lower():
                return response

        # Default response
        return (f"Dear {customer.name}, thank you for bringing this to our attention. "
               f"We take all feedback seriously and are investigating the issue. "
               f"We'll be in touch soon with an update.")

    async def _offer_compensation(self, customer_id: str) -> None:
        """Offer compensation for serious complaints"""
        customer = self.customers[customer_id]

        # Determine compensation based on customer tier
        compensation = {
            CustomerTier.BRONZE: {"type": "discount", "value": 20},
            CustomerTier.SILVER: {"type": "discount", "value": 25},
            CustomerTier.GOLD: {"type": "free_meal", "value": 30},
            CustomerTier.PLATINUM: {"type": "free_meal", "value": 50}
        }

        comp = compensation[customer.tier]

        if comp["type"] == "discount":
            message = f"As an apology, we'd like to offer you {comp['value']}% off your next order. Use code SORRY{comp['value']}."
        else:
            message = f"As an apology, we'd like to offer you a complimentary meal up to €{comp['value']}. Use code FREEMEAL."

        await self.send_notification(
            customer_id,
            NotificationType.PROMOTION,
            "We'd like to make it right",
            message
        )

    async def respond_to_feedback(self, feedback_id: str, response: str) -> bool:
        """Respond to customer feedback"""
        if feedback_id not in self.feedback:
            return False

        feedback_item = self.feedback[feedback_id]
        feedback_item.response = response
        feedback_item.response_date = datetime.now()
        feedback_item.status = "acknowledged"

        # Send response notification
        await self.send_notification(
            feedback_item.customer_id,
            NotificationType.FEEDBACK_REQUEST,
            "Response to your feedback",
            response
        )

        return True

    def generate_reorder_suggestions(self, customer_id: str) -> List[Dict[str, Any]]:
        """Generate personalized reorder suggestions"""
        if customer_id not in self.customers:
            return []

        customer = self.customers[customer_id]
        suggestions = []

        # Suggest favorite items
        for item in customer.favorite_items[:3]:
            suggestions.append({
                "item": item,
                "reason": "One of your favorites",
                "confidence": 0.9
            })

        # Suggest based on dietary restrictions
        if "vegan" in customer.dietary_restrictions:
            suggestions.append({
                "item": "Vegan Buddha Bowl",
                "reason": "Perfect for your vegan diet",
                "confidence": 0.8
            })

        # Suggest based on tier
        if customer.tier in [CustomerTier.GOLD, CustomerTier.PLATINUM]:
            suggestions.append({
                "item": "Premium Truffle Pizza",
                "reason": "Exclusive item for premium members",
                "confidence": 0.7
            })

        return suggestions

    async def send_reorder_reminder(self, customer_id: str) -> None:
        """Send personalized reorder reminder"""
        if customer_id not in self.customers:
            return

        customer = self.customers[customer_id]

        # Only send if last order was more than 7 days ago
        if (customer.last_order_date and
            datetime.now() - customer.last_order_date < timedelta(days=7)):
            return

        suggestions = self.generate_reorder_suggestions(customer_id)

        if suggestions:
            top_suggestion = suggestions[0]
            message = (f"Missing our {top_suggestion['item']}? "
                      f"It's been a while since your last order. "
                      f"Get 15% off when you order today with code COMEBACK15!")

            await self.send_notification(
                customer_id,
                NotificationType.PROMOTION,
                "We miss you!",
                message
            )

    def get_customer_analytics(self) -> Dict[str, Any]:
        """Get comprehensive customer analytics"""
        total_customers = len(self.customers)

        if total_customers == 0:
            return {}

        # Tier distribution
        tier_counts = {}
        total_spent = 0
        total_orders = 0

        for customer in self.customers.values():
            tier = customer.tier.value
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            total_spent += customer.total_spent
            total_orders += customer.total_orders

        # Feedback analytics
        feedback_counts = {}
        for feedback_item in self.feedback.values():
            feedback_type = feedback_item.type.value
            feedback_counts[feedback_type] = feedback_counts.get(feedback_type, 0) + 1

        # Calculate averages
        avg_order_value = total_spent / total_orders if total_orders > 0 else 0
        avg_customer_value = total_spent / total_customers

        return {
            'total_customers': total_customers,
            'tier_distribution': tier_counts,
            'total_revenue': round(total_spent, 2),
            'total_orders': total_orders,
            'average_order_value': round(avg_order_value, 2),
            'average_customer_value': round(avg_customer_value, 2),
            'feedback_distribution': feedback_counts,
            'loyalty_points_distributed': sum(c.loyalty_points for c in self.customers.values())
        }

# Example usage
if __name__ == "__main__":
    async def demo():
        experience_hub = CustomerExperienceHub()

        # Register sample customer
        customer_data = {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'phone': '+353 87 987 6543',
            'address': '456 Customer St, Dublin 1',
            'dietary_restrictions': ['vegan'],
            'accept_marketing': True
        }

        customer = experience_hub.register_customer(customer_data)
        print(f"Registered customer: {customer.name}")

        # Simulate order completion
        await experience_hub.update_customer_after_order(
            customer.id, 28.50, ['Vegan Buddha Bowl', 'Fresh Juice']
        )

        # Collect feedback
        feedback_data = {
            'type': 'compliment',
            'rating': 5,
            'subject': 'Great food!',
            'message': 'The vegan bowl was absolutely delicious. Will definitely order again!'
        }

        feedback_id = await experience_hub.collect_feedback(customer.id, feedback_data)
        print(f"Collected feedback: {feedback_id}")

        # Generate reorder suggestions
        suggestions = experience_hub.generate_reorder_suggestions(customer.id)
        print(f"Reorder suggestions: {suggestions}")

        # Get analytics
        analytics = experience_hub.get_customer_analytics()
        print(f"Customer analytics: {analytics}")

    asyncio.run(demo())