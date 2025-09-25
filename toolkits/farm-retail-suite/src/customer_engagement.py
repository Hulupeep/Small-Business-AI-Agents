"""
Customer Engagement Platform Agent
Direct customer relationship management and marketing automation
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from decimal import Decimal

logger = logging.getLogger(__name__)

class CommunicationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    FARM_NEWSLETTER = "farm_newsletter"
    SEASONAL_ALERT = "seasonal_alert"

class CustomerSegment(Enum):
    NEW_CUSTOMER = "new_customer"
    REGULAR_CUSTOMER = "regular_customer"
    VIP_CUSTOMER = "vip_customer"
    CSA_MEMBER = "csa_member"
    OCCASIONAL_VISITOR = "occasional_visitor"
    FARM_TOUR_ENTHUSIAST = "farm_tour_enthusiast"

class TourType(Enum):
    GENERAL_FARM_TOUR = "general_farm_tour"
    EDUCATIONAL_VISIT = "educational_visit"
    HARVEST_EXPERIENCE = "harvest_experience"
    SEASONAL_FESTIVAL = "seasonal_festival"
    PRIVATE_GROUP_TOUR = "private_group_tour"
    SCHOOL_VISIT = "school_visit"

class EventType(Enum):
    FARM_TOUR = "farm_tour"
    WORKSHOP = "workshop"
    SEASONAL_FESTIVAL = "seasonal_festival"
    HARVEST_DAY = "harvest_day"
    COOKING_CLASS = "cooking_class"
    EDUCATIONAL_PROGRAM = "educational_program"

@dataclass
class CustomerProfile:
    customer_id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    preferences: Dict
    segments: List[CustomerSegment]
    communication_preferences: List[CommunicationType]
    purchase_history: List[Dict] = field(default_factory=list)
    visit_history: List[Dict] = field(default_factory=list)
    dietary_restrictions: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    last_engagement: Optional[datetime] = None
    lifetime_value: Decimal = Decimal('0')
    loyalty_score: int = 0

@dataclass
class TourBooking:
    booking_id: str
    customer_id: str
    tour_type: TourType
    scheduled_date: datetime
    group_size: int
    special_requests: str
    price_per_person: Decimal
    total_price: Decimal
    status: str = "confirmed"
    payment_status: str = "pending"
    guide_assigned: Optional[str] = None

@dataclass
class MarketingCampaign:
    campaign_id: str
    name: str
    campaign_type: CommunicationType
    target_segments: List[CustomerSegment]
    content: Dict
    scheduled_date: datetime
    status: str = "draft"
    recipients: List[str] = field(default_factory=list)
    metrics: Dict = field(default_factory=dict)

@dataclass
class Recipe:
    recipe_id: str
    title: str
    ingredients: List[Dict]
    instructions: List[str]
    difficulty_level: str
    preparation_time: int  # minutes
    seasonal_ingredients: List[str]
    dietary_tags: List[str]  # vegetarian, vegan, gluten-free, etc.
    farm_products_used: List[str]

class CustomerEngagement:
    """
    Comprehensive customer engagement and marketing automation platform
    for building strong relationships with farm customers.
    """

    def __init__(self, farm_config: Dict):
        self.farm_config = farm_config
        self.customers: Dict[str, CustomerProfile] = {}
        self.tour_bookings: Dict[str, TourBooking] = {}
        self.campaigns: Dict[str, MarketingCampaign] = {}
        self.recipes: Dict[str, Recipe] = {}
        self.events: Dict[str, Dict] = {}
        self.seasonal_content: Dict[str, List] = {}

    async def initialize(self):
        """Initialize the customer engagement platform"""
        logger.info("Initializing Customer Engagement Platform")
        await self._load_customer_profiles()
        await self._setup_seasonal_content()
        await self._load_recipe_database()
        await self._setup_tour_schedules()
        logger.info("Customer Engagement Platform initialized successfully")

    async def _load_customer_profiles(self):
        """Load existing customer profiles and segmentation"""
        # Sample customer profiles - in production would load from database
        sample_customers = [
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@email.com',
                'phone': '+31612345678',
                'preferences': {
                    'organic_only': True,
                    'seasonal_produce': True,
                    'notification_frequency': 'weekly'
                },
                'segments': [CustomerSegment.CSA_MEMBER, CustomerSegment.VIP_CUSTOMER],
                'communication_preferences': [CommunicationType.EMAIL, CommunicationType.FARM_NEWSLETTER],
                'dietary_restrictions': ['gluten-free'],
                'interests': ['cooking', 'sustainable_farming', 'education']
            },
            {
                'name': 'Mark van der Berg',
                'email': 'mark.vdberg@example.com',
                'phone': '+31687654321',
                'preferences': {
                    'local_produce': True,
                    'farm_tours': True,
                    'notification_frequency': 'monthly'
                },
                'segments': [CustomerSegment.FARM_TOUR_ENTHUSIAST, CustomerSegment.REGULAR_CUSTOMER],
                'communication_preferences': [CommunicationType.EMAIL, CommunicationType.SMS],
                'interests': ['farm_tours', 'photography', 'family_activities']
            }
        ]

        for customer_data in sample_customers:
            customer_id = f"cust_{uuid.uuid4().hex[:8]}"
            customer = CustomerProfile(
                customer_id=customer_id,
                **customer_data
            )
            self.customers[customer_id] = customer

        logger.info(f"Loaded {len(self.customers)} customer profiles")

    async def _setup_seasonal_content(self):
        """Setup seasonal content templates and messaging"""
        self.seasonal_content = {
            'spring': [
                {
                    'type': 'availability_alert',
                    'title': 'Spring Vegetables Now Available!',
                    'content': 'Fresh spring onions, radishes, and early lettuce are ready for harvest.',
                    'products': ['spring_onions', 'radishes', 'lettuce']
                },
                {
                    'type': 'farm_update',
                    'title': 'Planting Season Update',
                    'content': 'See what we\'re planting this season and when to expect your favorites.',
                    'call_to_action': 'Book a spring planting tour'
                }
            ],
            'summer': [
                {
                    'type': 'harvest_festival',
                    'title': 'Summer Harvest Festival',
                    'content': 'Join us for our annual summer celebration with fresh produce, live music, and farm tours.',
                    'products': ['tomatoes', 'cucumbers', 'peppers', 'herbs']
                },
                {
                    'type': 'recipe_suggestion',
                    'title': 'Summer Salad Recipes',
                    'content': 'Make the most of summer vegetables with these fresh and healthy recipes.',
                    'recipes': ['garden_salad', 'gazpacho', 'ratatouille']
                }
            ],
            'autumn': [
                {
                    'type': 'harvest_participation',
                    'title': 'Join Our Harvest Days',
                    'content': 'Experience the satisfaction of harvesting your own vegetables and fruits.',
                    'products': ['apples', 'pumpkins', 'root_vegetables']
                },
                {
                    'type': 'preservation_workshop',
                    'title': 'Food Preservation Workshop',
                    'content': 'Learn traditional methods to preserve your harvest for winter.',
                    'skills': ['canning', 'fermenting', 'dehydrating']
                }
            ],
            'winter': [
                {
                    'type': 'storage_produce',
                    'title': 'Winter Storage Vegetables',
                    'content': 'Nutritious stored vegetables to keep you healthy through winter.',
                    'products': ['potatoes', 'carrots', 'cabbage', 'onions']
                },
                {
                    'type': 'planning_next_season',
                    'title': 'Planning Next Year\'s Garden',
                    'content': 'Workshop on planning your home garden for next growing season.',
                    'topics': ['seed_selection', 'garden_layout', 'crop_rotation']
                }
            ]
        }

    async def _load_recipe_database(self):
        """Load seasonal recipe database"""
        sample_recipes = [
            {
                'title': 'Fresh Garden Salad',
                'ingredients': [
                    {'item': 'mixed_lettuce', 'quantity': '200g', 'farm_product': True},
                    {'item': 'cherry_tomatoes', 'quantity': '150g', 'farm_product': True},
                    {'item': 'cucumber', 'quantity': '1 medium', 'farm_product': True},
                    {'item': 'olive_oil', 'quantity': '2 tbsp', 'farm_product': False},
                    {'item': 'balsamic_vinegar', 'quantity': '1 tbsp', 'farm_product': False}
                ],
                'instructions': [
                    'Wash and dry all vegetables thoroughly',
                    'Tear lettuce into bite-sized pieces',
                    'Slice tomatoes and cucumber',
                    'Combine vegetables in large bowl',
                    'Drizzle with olive oil and vinegar',
                    'Toss gently and serve immediately'
                ],
                'difficulty_level': 'easy',
                'preparation_time': 15,
                'seasonal_ingredients': ['lettuce', 'tomatoes', 'cucumber'],
                'dietary_tags': ['vegetarian', 'vegan', 'gluten-free'],
                'farm_products_used': ['mixed_lettuce', 'cherry_tomatoes', 'cucumber']
            },
            {
                'title': 'Roasted Root Vegetable Medley',
                'ingredients': [
                    {'item': 'carrots', 'quantity': '300g', 'farm_product': True},
                    {'item': 'potatoes', 'quantity': '400g', 'farm_product': True},
                    {'item': 'parsnips', 'quantity': '200g', 'farm_product': True},
                    {'item': 'fresh_herbs', 'quantity': '2 tbsp', 'farm_product': True},
                    {'item': 'olive_oil', 'quantity': '3 tbsp', 'farm_product': False}
                ],
                'instructions': [
                    'Preheat oven to 200°C',
                    'Wash and chop vegetables into similar sizes',
                    'Toss with olive oil and herbs',
                    'Spread on baking sheet',
                    'Roast for 35-40 minutes until tender',
                    'Season with salt and pepper before serving'
                ],
                'difficulty_level': 'easy',
                'preparation_time': 50,
                'seasonal_ingredients': ['carrots', 'potatoes', 'parsnips'],
                'dietary_tags': ['vegetarian', 'vegan', 'gluten-free'],
                'farm_products_used': ['carrots', 'potatoes', 'parsnips', 'fresh_herbs']
            }
        ]

        for recipe_data in sample_recipes:
            recipe_id = f"recipe_{uuid.uuid4().hex[:8]}"
            recipe = Recipe(
                recipe_id=recipe_id,
                **recipe_data
            )
            self.recipes[recipe_id] = recipe

        logger.info(f"Loaded {len(self.recipes)} recipes")

    async def _setup_tour_schedules(self):
        """Setup farm tour schedules and availability"""
        # Default tour offerings
        tour_offerings = {
            TourType.GENERAL_FARM_TOUR: {
                'duration': 90,  # minutes
                'max_group_size': 20,
                'price_per_person': Decimal('12.50'),
                'available_days': [5, 6, 7],  # Friday, Saturday, Sunday
                'times': ['10:00', '14:00', '16:00']
            },
            TourType.EDUCATIONAL_VISIT: {
                'duration': 120,
                'max_group_size': 30,
                'price_per_person': Decimal('8.00'),
                'available_days': [1, 2, 3, 4],  # Weekdays for schools
                'times': ['09:30', '13:30']
            },
            TourType.HARVEST_EXPERIENCE: {
                'duration': 180,
                'max_group_size': 15,
                'price_per_person': Decimal('25.00'),
                'available_days': [6, 7],  # Weekends only
                'times': ['09:00', '14:00']
            }
        }

        self.tour_offerings = tour_offerings

    async def add_customer(self, customer_data: Dict) -> str:
        """Add new customer to engagement platform"""
        customer_id = f"cust_{uuid.uuid4().hex[:8]}"

        customer = CustomerProfile(
            customer_id=customer_id,
            name=customer_data['name'],
            email=customer_data.get('email'),
            phone=customer_data.get('phone'),
            preferences=customer_data.get('preferences', {}),
            segments=[CustomerSegment(seg) for seg in customer_data.get('segments', ['new_customer'])],
            communication_preferences=[CommunicationType(pref) for pref in customer_data.get('communication_preferences', ['email'])],
            dietary_restrictions=customer_data.get('dietary_restrictions', []),
            interests=customer_data.get('interests', [])
        )

        self.customers[customer_id] = customer
        logger.info(f"Added customer {customer_id}: {customer.name}")

        # Send welcome message for new customers
        if CustomerSegment.NEW_CUSTOMER in customer.segments:
            await self._send_welcome_message(customer_id)

        return customer_id

    async def _send_welcome_message(self, customer_id: str):
        """Send welcome message to new customer"""
        customer = self.customers.get(customer_id)
        if not customer or not customer.email:
            return

        welcome_content = {
            'subject': f'Welcome to {self.farm_config["name"]}!',
            'body': f"""
            Dear {customer.name},

            Welcome to our farm family! We're excited to have you join our community of supporters who value fresh, local, sustainable agriculture.

            Here's what you can expect:
            • Weekly updates on what's fresh and available
            • Seasonal recipes featuring our produce
            • Invitations to farm tours and special events
            • First access to limited seasonal items

            Visit our farm shop or browse our online catalog to see what's available this week.

            Best regards,
            The {self.farm_config["name"]} Team
            """,
            'call_to_action': 'Book a farm tour',
            'call_to_action_url': f"{self.farm_config.get('website', '')}/book-tour"
        }

        await self._send_communication(customer_id, CommunicationType.EMAIL, welcome_content)

    async def book_farm_tour(self, booking_data: Dict) -> str:
        """Book farm tour for customer"""
        booking_id = f"tour_{uuid.uuid4().hex[:8]}"

        tour_type = TourType(booking_data['tour_type'])
        scheduled_date = datetime.fromisoformat(booking_data['scheduled_date'])
        group_size = int(booking_data['group_size'])

        # Get tour pricing
        tour_info = self.tour_offerings.get(tour_type)
        if not tour_info:
            raise ValueError(f"Tour type {tour_type.value} not available")

        price_per_person = tour_info['price_per_person']
        total_price = price_per_person * group_size

        # Check availability (simplified)
        if group_size > tour_info['max_group_size']:
            raise ValueError(f"Group size exceeds maximum of {tour_info['max_group_size']}")

        booking = TourBooking(
            booking_id=booking_id,
            customer_id=booking_data['customer_id'],
            tour_type=tour_type,
            scheduled_date=scheduled_date,
            group_size=group_size,
            special_requests=booking_data.get('special_requests', ''),
            price_per_person=price_per_person,
            total_price=total_price
        )

        self.tour_bookings[booking_id] = booking

        # Send confirmation
        await self._send_tour_confirmation(booking_id)

        logger.info(f"Booked tour {booking_id} for customer {booking_data['customer_id']}")
        return booking_id

    async def _send_tour_confirmation(self, booking_id: str):
        """Send tour booking confirmation"""
        booking = self.tour_bookings.get(booking_id)
        if not booking:
            return

        customer = self.customers.get(booking.customer_id)
        if not customer or not customer.email:
            return

        confirmation_content = {
            'subject': 'Farm Tour Booking Confirmation',
            'body': f"""
            Dear {customer.name},

            Your farm tour booking has been confirmed!

            Tour Details:
            • Type: {booking.tour_type.value.replace('_', ' ').title()}
            • Date: {booking.scheduled_date.strftime('%A, %B %d, %Y at %H:%M')}
            • Group Size: {booking.group_size} person(s)
            • Total Price: €{booking.total_price:.2f}

            What to Expect:
            • Meet at the farm shop 15 minutes before your tour
            • Wear comfortable walking shoes
            • Bring a hat and water bottle
            • Camera for memorable photos

            Special Requests: {booking.special_requests or 'None'}

            We look forward to showing you around our farm!

            Best regards,
            The {self.farm_config["name"]} Team
            """,
            'booking_reference': booking_id
        }

        await self._send_communication(booking.customer_id, CommunicationType.EMAIL, confirmation_content)

    async def send_seasonal_availability_alert(self, product_list: List[Dict]) -> Dict:
        """Send seasonal availability alerts to interested customers"""
        current_season = self._get_current_season()
        seasonal_content = self.seasonal_content.get(current_season, [])

        # Find relevant content for these products
        relevant_content = None
        for content in seasonal_content:
            if content['type'] == 'availability_alert':
                content_products = content.get('products', [])
                if any(product['name'] in content_products for product in product_list):
                    relevant_content = content
                    break

        if not relevant_content:
            # Create generic availability alert
            relevant_content = {
                'title': 'New Seasonal Produce Available!',
                'content': f'Fresh {current_season} produce is now ready for harvest and available in our farm shop.',
                'products': [product['name'] for product in product_list]
            }

        # Target customers interested in seasonal produce
        target_customers = [
            customer for customer in self.customers.values()
            if (customer.preferences.get('seasonal_produce', False) or
                'seasonal_produce' in customer.interests)
        ]

        notifications_sent = 0
        for customer in target_customers:
            if CommunicationType.EMAIL in customer.communication_preferences:
                alert_content = {
                    'subject': relevant_content['title'],
                    'body': f"""
                    Dear {customer.name},

                    {relevant_content['content']}

                    Available Now:
                    {chr(10).join([f"• {product['name']} - €{product['price']}/{product['unit']}" for product in product_list])}

                    Visit our farm shop or place an online order to get the freshest seasonal produce!

                    Best regards,
                    The {self.farm_config["name"]} Team
                    """,
                    'products': product_list
                }

                await self._send_communication(customer.customer_id, CommunicationType.EMAIL, alert_content)
                notifications_sent += 1

        return {
            'notifications_sent': notifications_sent,
            'target_customers': len(target_customers),
            'products_featured': len(product_list)
        }

    def _get_current_season(self) -> str:
        """Get current season based on date"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'

    async def suggest_recipes(self, customer_id: str, available_products: List[str]) -> List[Dict]:
        """Suggest recipes based on available products and customer preferences"""
        customer = self.customers.get(customer_id)
        if not customer:
            return []

        # Find recipes that use available products
        suitable_recipes = []

        for recipe in self.recipes.values():
            # Check if recipe uses farm products that are available
            recipe_farm_products = set(recipe.farm_products_used)
            available_farm_products = set(available_products)

            if recipe_farm_products.intersection(available_farm_products):
                # Check dietary restrictions
                if customer.dietary_restrictions:
                    if not all(restriction in recipe.dietary_tags for restriction in customer.dietary_restrictions):
                        continue

                # Calculate match score
                match_score = len(recipe_farm_products.intersection(available_farm_products)) / len(recipe_farm_products)

                suitable_recipes.append({
                    'recipe_id': recipe.recipe_id,
                    'title': recipe.title,
                    'difficulty_level': recipe.difficulty_level,
                    'preparation_time': recipe.preparation_time,
                    'match_score': match_score,
                    'farm_products_needed': list(recipe_farm_products.intersection(available_farm_products)),
                    'other_ingredients_needed': [
                        ing['item'] for ing in recipe.ingredients
                        if not ing.get('farm_product', False)
                    ]
                })

        # Sort by match score and limit to top 5
        suitable_recipes.sort(key=lambda x: x['match_score'], reverse=True)

        return suitable_recipes[:5]

    async def create_marketing_campaign(self, campaign_data: Dict) -> str:
        """Create targeted marketing campaign"""
        campaign_id = f"campaign_{uuid.uuid4().hex[:8]}"

        campaign = MarketingCampaign(
            campaign_id=campaign_id,
            name=campaign_data['name'],
            campaign_type=CommunicationType(campaign_data['type']),
            target_segments=[CustomerSegment(seg) for seg in campaign_data['target_segments']],
            content=campaign_data['content'],
            scheduled_date=datetime.fromisoformat(campaign_data['scheduled_date'])
        )

        # Find target customers
        target_customers = []
        for customer in self.customers.values():
            if any(segment in customer.segments for segment in campaign.target_segments):
                if campaign.campaign_type in customer.communication_preferences:
                    target_customers.append(customer.customer_id)

        campaign.recipients = target_customers
        self.campaigns[campaign_id] = campaign

        logger.info(f"Created campaign {campaign_id}: {campaign.name} targeting {len(target_customers)} customers")
        return campaign_id

    async def execute_campaign(self, campaign_id: str) -> Dict:
        """Execute marketing campaign"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return {'error': f'Campaign {campaign_id} not found'}

        if campaign.status != 'draft':
            return {'error': f'Campaign {campaign_id} already executed'}

        successful_sends = 0
        failed_sends = 0

        for customer_id in campaign.recipients:
            try:
                await self._send_communication(customer_id, campaign.campaign_type, campaign.content)
                successful_sends += 1
            except Exception as e:
                logger.error(f"Failed to send campaign to customer {customer_id}: {e}")
                failed_sends += 1

        # Update campaign metrics
        campaign.status = 'executed'
        campaign.metrics = {
            'sent_date': datetime.now().isoformat(),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'total_recipients': len(campaign.recipients),
            'delivery_rate': successful_sends / len(campaign.recipients) * 100 if campaign.recipients else 0
        }

        return campaign.metrics

    async def _send_communication(self, customer_id: str, comm_type: CommunicationType, content: Dict):
        """Send communication to customer"""
        customer = self.customers.get(customer_id)
        if not customer:
            return

        # Update last engagement
        customer.last_engagement = datetime.now()

        # In production, integrate with actual communication services
        logger.info(f"Sent {comm_type.value} to {customer.name}: {content.get('subject', 'Message')}")

    async def manage_csa_memberships(self) -> Dict:
        """Manage CSA (Community Supported Agriculture) memberships"""
        csa_members = [
            customer for customer in self.customers.values()
            if CustomerSegment.CSA_MEMBER in customer.segments
        ]

        membership_summary = {
            'total_members': len(csa_members),
            'active_members': len([c for c in csa_members if c.last_engagement and
                                 c.last_engagement >= datetime.now() - timedelta(days=30)]),
            'member_details': []
        }

        for member in csa_members:
            # Calculate weeks since last pickup/contact
            weeks_since_contact = 0
            if member.last_engagement:
                weeks_since_contact = (datetime.now() - member.last_engagement).days // 7

            member_info = {
                'customer_id': member.customer_id,
                'name': member.name,
                'email': member.email,
                'weeks_since_contact': weeks_since_contact,
                'lifetime_value': float(member.lifetime_value),
                'status': 'active' if weeks_since_contact < 4 else 'needs_attention'
            }

            membership_summary['member_details'].append(member_info)

        return membership_summary

    async def generate_customer_insights(self, customer_id: str) -> Dict:
        """Generate comprehensive customer insights"""
        customer = self.customers.get(customer_id)
        if not customer:
            return {'error': f'Customer {customer_id} not found'}

        # Calculate engagement metrics
        engagement_score = self._calculate_engagement_score(customer)

        # Analyze purchase patterns (would integrate with sales data)
        purchase_patterns = {
            'preferred_products': ['seasonal_vegetables', 'organic_produce'],  # Simplified
            'average_order_frequency': 'weekly',
            'preferred_communication': [pref.value for pref in customer.communication_preferences],
            'seasonal_preferences': self._analyze_seasonal_preferences(customer)
        }

        # Generate recommendations
        recommendations = []
        if engagement_score < 50:
            recommendations.append("Send re-engagement campaign with special offer")
        if CustomerSegment.CSA_MEMBER not in customer.segments and engagement_score > 70:
            recommendations.append("Invite to join CSA program")
        if 'farm_tours' in customer.interests and not customer.visit_history:
            recommendations.append("Offer complimentary farm tour")

        insights = {
            'customer_profile': {
                'name': customer.name,
                'segments': [seg.value for seg in customer.segments],
                'loyalty_score': customer.loyalty_score,
                'lifetime_value': float(customer.lifetime_value)
            },
            'engagement_metrics': {
                'engagement_score': engagement_score,
                'last_engagement': customer.last_engagement.isoformat() if customer.last_engagement else None,
                'communication_preferences': [pref.value for pref in customer.communication_preferences]
            },
            'purchase_patterns': purchase_patterns,
            'recommendations': recommendations
        }

        return insights

    def _calculate_engagement_score(self, customer: CustomerProfile) -> int:
        """Calculate customer engagement score (0-100)"""
        score = 0

        # Recent engagement (40 points max)
        if customer.last_engagement:
            days_since_engagement = (datetime.now() - customer.last_engagement).days
            if days_since_engagement <= 7:
                score += 40
            elif days_since_engagement <= 30:
                score += 30
            elif days_since_engagement <= 90:
                score += 20
            else:
                score += 10

        # Communication preferences (20 points max)
        score += min(len(customer.communication_preferences) * 10, 20)

        # Customer segments (20 points max)
        if CustomerSegment.VIP_CUSTOMER in customer.segments:
            score += 20
        elif CustomerSegment.CSA_MEMBER in customer.segments:
            score += 15
        elif CustomerSegment.REGULAR_CUSTOMER in customer.segments:
            score += 10

        # Interests and preferences (20 points max)
        if customer.interests:
            score += min(len(customer.interests) * 5, 20)

        return min(score, 100)

    def _analyze_seasonal_preferences(self, customer: CustomerProfile) -> Dict:
        """Analyze customer's seasonal preferences"""
        # Simplified analysis - in production would use purchase history
        return {
            'spring': ['fresh_greens', 'herbs'],
            'summer': ['tomatoes', 'berries'],
            'autumn': ['root_vegetables', 'apples'],
            'winter': ['stored_vegetables', 'preserved_goods']
        }

# Example usage and testing
async def main():
    """Example usage of Customer Engagement Platform"""
    farm_config = {
        'name': 'Green Valley Farm',
        'website': 'https://greenvalleyfarm.com'
    }

    engagement = CustomerEngagement(farm_config)
    await engagement.initialize()

    # Add a new customer
    customer_data = {
        'name': 'Emma Wilson',
        'email': 'emma.wilson@email.com',
        'phone': '+31698765432',
        'preferences': {
            'organic_only': True,
            'seasonal_produce': True
        },
        'segments': ['regular_customer'],
        'communication_preferences': ['email'],
        'interests': ['cooking', 'nutrition']
    }

    customer_id = await engagement.add_customer(customer_data)
    print(f"Added customer: {customer_id}")

    # Book a farm tour
    booking_data = {
        'customer_id': customer_id,
        'tour_type': 'general_farm_tour',
        'scheduled_date': (datetime.now() + timedelta(days=7)).isoformat(),
        'group_size': 2,
        'special_requests': 'Interested in organic certification process'
    }

    booking_id = await engagement.book_farm_tour(booking_data)
    print(f"Booked tour: {booking_id}")

    # Send seasonal availability alert
    products = [
        {'name': 'spring_onions', 'price': '2.50', 'unit': 'bunch'},
        {'name': 'radishes', 'price': '3.00', 'unit': 'kg'}
    ]

    alert_result = await engagement.send_seasonal_availability_alert(products)
    print("Seasonal alert result:", alert_result)

    # Get customer insights
    insights = await engagement.generate_customer_insights(customer_id)
    print("Customer insights:", insights)

if __name__ == "__main__":
    asyncio.run(main())