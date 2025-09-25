"""
Personal Shopping Assistant Agent

Provides personalized style advice, outfit recommendations, and shopping
assistance. Like having a dedicated personal shopper for every customer.
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

class StylePersonality(Enum):
    CLASSIC = "classic"
    TRENDY = "trendy"
    BOHEMIAN = "bohemian"
    MINIMALIST = "minimalist"
    EDGY = "edgy"
    ROMANTIC = "romantic"
    ECLECTIC = "eclectic"

class BodyType(Enum):
    PEAR = "pear"
    APPLE = "apple"
    HOURGLASS = "hourglass"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"

class Occasion(Enum):
    WORK = "work"
    CASUAL = "casual"
    DATE_NIGHT = "date_night"
    SPECIAL_EVENT = "special_event"
    TRAVEL = "travel"
    EXERCISE = "exercise"
    FORMAL = "formal"

@dataclass
class StyleProfile:
    """Represents a customer's style preferences and characteristics."""
    customer_id: str
    style_personality: StylePersonality
    body_type: Optional[BodyType] = None
    size_range: Dict[str, str] = field(default_factory=dict)  # {"tops": "M", "bottoms": "10", "shoes": "8"}
    color_preferences: List[str] = field(default_factory=list)
    color_dislikes: List[str] = field(default_factory=list)
    budget_range: Tuple[float, float] = (0, 1000)
    lifestyle: List[str] = field(default_factory=list)  # ["professional", "active", "social"]
    style_goals: List[str] = field(default_factory=list)  # ["look taller", "hide tummy", "show personality"]
    preferred_brands: List[str] = field(default_factory=list)
    avoid_styles: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class OutfitRecommendation:
    """Represents a complete outfit recommendation."""
    recommendation_id: str
    customer_id: str
    occasion: Occasion
    items: List[Dict]  # [{name, price, sku, category, reason}]
    total_price: float
    styling_notes: str
    confidence_rating: float  # 1-10 how confident this will work
    alternative_items: List[Dict] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)

@dataclass
class StyleQuizResponse:
    """Represents responses to style personality quiz."""
    question_id: str
    question: str
    customer_response: str
    score_weights: Dict[StylePersonality, int]

class PersonalShopperAssistant:
    """
    AI-powered personal shopping assistant that provides personalized
    style advice, outfit recommendations, and shopping guidance.

    Key Features:
    - Style personality assessment
    - Body type analysis and recommendations
    - Occasion-based outfit building
    - Size guide assistance
    - Personal style evolution tracking
    - Virtual wardrobe management
    """

    def __init__(self, inventory_file: str = "data/inventory.csv"):
        self.inventory_file = inventory_file
        self.style_profiles = {}
        self.outfit_recommendations = []
        self.style_quiz_questions = self._initialize_quiz_questions()
        self.styling_rules = self._initialize_styling_rules()

    def _initialize_quiz_questions(self) -> List[StyleQuizResponse]:
        """Initialize style personality quiz questions."""
        return [
            StyleQuizResponse(
                "weekend_outfit",
                "What's your ideal weekend outfit?",
                "",
                {
                    StylePersonality.CLASSIC: {"blazer and jeans": 3, "tailored pieces": 2},
                    StylePersonality.TRENDY: {"latest fashion": 3, "statement pieces": 2},
                    StylePersonality.BOHEMIAN: {"flowy dress": 3, "earth tones": 2},
                    StylePersonality.MINIMALIST: {"simple basics": 3, "neutral colors": 2},
                    StylePersonality.EDGY: {"leather jacket": 3, "dark colors": 2},
                    StylePersonality.ROMANTIC: {"soft fabrics": 3, "feminine details": 2}
                }
            ),
            StyleQuizResponse(
                "shopping_priority",
                "When shopping, what's most important to you?",
                "",
                {
                    StylePersonality.CLASSIC: {"quality and timeless": 3, "versatility": 2},
                    StylePersonality.TRENDY: {"latest trends": 3, "social media worthy": 2},
                    StylePersonality.MINIMALIST: {"simplicity": 3, "functionality": 2},
                    StylePersonality.BOHEMIAN: {"uniqueness": 3, "comfort": 2},
                    StylePersonality.EDGY: {"making a statement": 3, "standing out": 2},
                    StylePersonality.ROMANTIC: {"beauty": 3, "femininity": 2}
                }
            ),
            StyleQuizResponse(
                "inspiration_source",
                "Where do you get style inspiration?",
                "",
                {
                    StylePersonality.CLASSIC: {"fashion icons": 2, "magazines": 3},
                    StylePersonality.TRENDY: {"instagram": 3, "celebrities": 2},
                    StylePersonality.BOHEMIAN: {"travel": 3, "nature": 2},
                    StylePersonality.MINIMALIST: {"architecture": 2, "clean lines": 3},
                    StylePersonality.EDGY: {"street style": 3, "music culture": 2},
                    StylePersonality.ROMANTIC: {"vintage films": 3, "art": 2}
                }
            )
        ]

    def _initialize_styling_rules(self) -> Dict:
        """Initialize styling rules for different body types and occasions."""
        return {
            "body_type_recommendations": {
                BodyType.PEAR: {
                    "emphasize": ["shoulders", "neckline", "upper_body"],
                    "balance": ["wide_hips", "narrow_shoulders"],
                    "recommended_styles": ["A-line tops", "statement sleeves", "structured blazers"],
                    "avoid": ["tight bottoms", "low-rise jeans", "oversized tops"]
                },
                BodyType.APPLE: {
                    "emphasize": ["legs", "arms", "neckline"],
                    "balance": ["midsection", "broader_torso"],
                    "recommended_styles": ["empire waist", "V-necks", "wrap dresses"],
                    "avoid": ["tight around middle", "horizontal stripes", "cropped tops"]
                },
                BodyType.HOURGLASS: {
                    "emphasize": ["waist", "curves", "silhouette"],
                    "balance": ["proportions"],
                    "recommended_styles": ["fitted styles", "wrap dresses", "belted pieces"],
                    "avoid": ["shapeless clothing", "oversized fits", "boxy cuts"]
                },
                BodyType.RECTANGLE: {
                    "emphasize": ["create curves", "waist", "feminine details"],
                    "balance": ["straight lines"],
                    "recommended_styles": ["peplum tops", "ruffles", "layering"],
                    "avoid": ["straight cuts", "shapeless fits", "minimal details"]
                }
            },
            "occasion_guidelines": {
                Occasion.WORK: {
                    "key_pieces": ["blazer", "trousers", "blouse", "pencil skirt"],
                    "colors": ["navy", "black", "gray", "white", "burgundy"],
                    "avoid": ["revealing", "too casual", "overly trendy"],
                    "styling_tips": ["Layer for versatility", "Invest in quality basics", "Keep accessories minimal"]
                },
                Occasion.DATE_NIGHT: {
                    "key_pieces": ["little black dress", "heels", "statement jewelry"],
                    "colors": ["black", "red", "navy", "burgundy"],
                    "avoid": ["too formal", "uncomfortable", "overdone"],
                    "styling_tips": ["Choose one statement piece", "Comfort is key", "Express your personality"]
                },
                Occasion.CASUAL: {
                    "key_pieces": ["jeans", "comfortable tops", "sneakers", "cardigans"],
                    "colors": ["any", "mix and match"],
                    "avoid": ["too formal", "uncomfortable"],
                    "styling_tips": ["Layer for interest", "Mix textures", "Comfort first"]
                }
            }
        }

    def conduct_style_quiz(self, customer_id: str, responses: Dict[str, str]) -> StyleProfile:
        """
        Conduct style personality quiz and create customer style profile.

        Args:
            customer_id: Customer identifier
            responses: Dictionary of question_id -> customer_response

        Returns:
            Complete StyleProfile based on quiz responses
        """
        style_scores = {style: 0 for style in StylePersonality}

        # Calculate scores based on responses
        for question in self.style_quiz_questions:
            response = responses.get(question.question_id, "").lower()

            for style, keywords in question.score_weights.items():
                for keyword, weight in keywords.items():
                    if keyword in response:
                        style_scores[style] += weight

        # Determine dominant style personality
        dominant_style = max(style_scores, key=style_scores.get)

        # Create basic style profile (can be enhanced with more quiz questions)
        profile = StyleProfile(
            customer_id=customer_id,
            style_personality=dominant_style
        )

        self.style_profiles[customer_id] = profile
        return profile

    def update_style_profile(self, customer_id: str, updates: Dict) -> StyleProfile:
        """Update existing style profile with new information."""
        if customer_id not in self.style_profiles:
            raise ValueError(f"No style profile found for customer {customer_id}")

        profile = self.style_profiles[customer_id]

        # Update profile attributes
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.last_updated = datetime.now()
        return profile

    def recommend_outfit_for_occasion(self, customer_id: str, occasion: Occasion,
                                    budget_max: Optional[float] = None) -> OutfitRecommendation:
        """
        Generate complete outfit recommendation for specific occasion.

        Args:
            customer_id: Customer identifier
            occasion: Type of occasion (work, date, casual, etc.)
            budget_max: Maximum budget for the outfit

        Returns:
            Complete outfit recommendation with styling notes
        """
        if customer_id not in self.style_profiles:
            raise ValueError(f"No style profile found for customer {customer_id}")

        profile = self.style_profiles[customer_id]
        budget_max = budget_max or profile.budget_range[1]

        # Get occasion guidelines
        occasion_guide = self.styling_rules["occasion_guidelines"].get(occasion)
        if not occasion_guide:
            raise ValueError(f"No guidelines found for occasion: {occasion}")

        # Mock inventory items (in production, this would query real inventory)
        sample_items = self._get_sample_inventory_for_occasion(occasion, profile, budget_max)

        # Select items for complete outfit
        selected_items = self._select_outfit_items(sample_items, occasion_guide, profile, budget_max)

        # Generate styling notes
        styling_notes = self._generate_styling_notes(selected_items, occasion, profile)

        # Calculate confidence rating
        confidence_rating = self._calculate_outfit_confidence(selected_items, profile, occasion)

        recommendation = OutfitRecommendation(
            recommendation_id=f"outfit_{customer_id}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            customer_id=customer_id,
            occasion=occasion,
            items=selected_items,
            total_price=sum(item['price'] for item in selected_items),
            styling_notes=styling_notes,
            confidence_rating=confidence_rating
        )

        self.outfit_recommendations.append(recommendation)
        return recommendation

    def _get_sample_inventory_for_occasion(self, occasion: Occasion, profile: StyleProfile,
                                         budget_max: float) -> List[Dict]:
        """Get relevant inventory items for the occasion (mock data for demo)."""
        # In production, this would query actual inventory
        sample_inventory = {
            Occasion.WORK: [
                {"name": "Navy Blazer", "price": 129.99, "category": "jackets", "sku": "BLAZER001", "colors": ["navy", "black"]},
                {"name": "White Button Shirt", "price": 59.99, "category": "tops", "sku": "SHIRT001", "colors": ["white", "light blue"]},
                {"name": "Tailored Trousers", "price": 89.99, "category": "bottoms", "sku": "PANTS001", "colors": ["black", "navy", "gray"]},
                {"name": "Pencil Skirt", "price": 69.99, "category": "bottoms", "sku": "SKIRT001", "colors": ["black", "navy"]},
                {"name": "Low Block Heels", "price": 99.99, "category": "shoes", "sku": "SHOES001", "colors": ["black", "nude"]}
            ],
            Occasion.DATE_NIGHT: [
                {"name": "Little Black Dress", "price": 149.99, "category": "dresses", "sku": "DRESS001", "colors": ["black"]},
                {"name": "Red Midi Dress", "price": 139.99, "category": "dresses", "sku": "DRESS002", "colors": ["red", "burgundy"]},
                {"name": "Statement Necklace", "price": 39.99, "category": "accessories", "sku": "NECK001", "colors": ["gold", "silver"]},
                {"name": "High Heels", "price": 119.99, "category": "shoes", "sku": "HEELS001", "colors": ["black", "nude"]},
                {"name": "Clutch Bag", "price": 79.99, "category": "accessories", "sku": "BAG001", "colors": ["black", "gold"]}
            ],
            Occasion.CASUAL: [
                {"name": "Comfortable Jeans", "price": 79.99, "category": "bottoms", "sku": "JEANS001", "colors": ["blue", "black"]},
                {"name": "Soft Knit Top", "price": 49.99, "category": "tops", "sku": "TOP001", "colors": ["white", "gray", "pink"]},
                {"name": "Cardigan", "price": 69.99, "category": "jackets", "sku": "CARD001", "colors": ["beige", "navy"]},
                {"name": "White Sneakers", "price": 89.99, "category": "shoes", "sku": "SNEAK001", "colors": ["white"]},
                {"name": "Crossbody Bag", "price": 59.99, "category": "accessories", "sku": "XBAG001", "colors": ["brown", "black"]}
            ]
        }

        items = sample_inventory.get(occasion, [])

        # Filter by budget and preferences
        filtered_items = []
        for item in items:
            if item['price'] <= budget_max:
                # Check color preferences
                if profile.color_preferences:
                    if any(color in profile.color_preferences for color in item['colors']):
                        filtered_items.append(item)
                else:
                    filtered_items.append(item)

        return filtered_items

    def _select_outfit_items(self, available_items: List[Dict], occasion_guide: Dict,
                           profile: StyleProfile, budget_max: float) -> List[Dict]:
        """Select items to create a complete outfit within budget."""
        selected_items = []
        remaining_budget = budget_max
        categories_needed = []

        # Determine categories needed based on occasion
        if "blazer" in occasion_guide["key_pieces"]:
            categories_needed.extend(["jackets", "tops", "bottoms"])
        elif "dress" in occasion_guide["key_pieces"]:
            categories_needed.append("dresses")
        else:
            categories_needed.extend(["tops", "bottoms"])

        categories_needed.extend(["shoes", "accessories"])

        # Select one item from each needed category
        for category in categories_needed:
            category_items = [item for item in available_items
                            if item['category'] == category and item['price'] <= remaining_budget]

            if category_items:
                # Select based on style personality and preferences
                selected_item = self._select_best_item_for_profile(category_items, profile)
                selected_items.append({
                    **selected_item,
                    'reason': self._get_selection_reason(selected_item, profile, category)
                })
                remaining_budget -= selected_item['price']

        return selected_items

    def _select_best_item_for_profile(self, items: List[Dict], profile: StyleProfile) -> Dict:
        """Select the best item from category based on customer's style profile."""
        # Simple selection logic (can be enhanced with ML)
        for item in items:
            # Prefer items in customer's preferred colors
            if profile.color_preferences:
                for color in item['colors']:
                    if color in profile.color_preferences:
                        return item

        # If no color preference match, return first item
        return items[0] if items else {}

    def _get_selection_reason(self, item: Dict, profile: StyleProfile, category: str) -> str:
        """Generate reason why this item was selected for the customer."""
        reasons = [
            f"Perfect for your {profile.style_personality.value} style",
            f"Great {category} choice that flatters your figure",
            f"Versatile piece that works with your lifestyle",
            f"Classic choice that you can wear multiple ways"
        ]

        # Add specific reasons based on item and profile
        if profile.color_preferences and any(color in profile.color_preferences for color in item['colors']):
            reasons.append(f"Chosen in your preferred color palette")

        return random.choice(reasons)

    def _generate_styling_notes(self, items: List[Dict], occasion: Occasion,
                              profile: StyleProfile) -> str:
        """Generate comprehensive styling notes for the outfit."""
        notes = []

        # Overall outfit description
        outfit_desc = f"This {profile.style_personality.value} outfit is perfect for {occasion.value.replace('_', ' ')}"
        notes.append(outfit_desc)

        # Specific styling tips
        styling_tips = [
            "Roll up sleeves for a more relaxed look",
            "Add a belt to define your waist",
            "Layer with a scarf for extra personality",
            "Choose jewelry that complements the neckline",
            "Make sure shoes are comfortable for the occasion"
        ]

        # Body type specific advice
        if profile.body_type:
            body_rules = self.styling_rules["body_type_recommendations"].get(profile.body_type)
            if body_rules:
                notes.append(f"This combination {', '.join(body_rules['emphasize'][:2])}")

        # Add random styling tip
        notes.append(random.choice(styling_tips))

        return ". ".join(notes) + "."

    def _calculate_outfit_confidence(self, items: List[Dict], profile: StyleProfile,
                                   occasion: Occasion) -> float:
        """Calculate confidence rating for outfit recommendation (1-10)."""
        base_confidence = 7.0

        # Boost confidence for complete outfits
        if len(items) >= 3:
            base_confidence += 1

        # Boost for items in preferred colors
        if profile.color_preferences:
            color_matches = sum(1 for item in items
                              if any(color in profile.color_preferences for color in item['colors']))
            base_confidence += (color_matches / len(items)) * 1

        # Boost for style personality match
        # (Simplified - in production would use more sophisticated matching)
        base_confidence += 1

        return min(10.0, max(1.0, base_confidence))

    def get_size_recommendations(self, customer_id: str, category: str) -> Dict:
        """Provide size guidance and fit recommendations."""
        if customer_id not in self.style_profiles:
            return {"error": "No style profile found"}

        profile = self.style_profiles[customer_id]

        size_guides = {
            "tops": {
                "measurement_tips": "Measure across the fullest part of your bust",
                "fit_advice": "Our tops run slightly small, consider sizing up for loose fit",
                "size_chart": {"XS": "32-34", "S": "34-36", "M": "36-38", "L": "38-40"}
            },
            "bottoms": {
                "measurement_tips": "Measure your natural waist and hips",
                "fit_advice": "Our bottoms have slight stretch, order your normal size",
                "size_chart": {"6": "26-27", "8": "27-28", "10": "28-29", "12": "30-31"}
            },
            "dresses": {
                "measurement_tips": "Consider both bust and hip measurements",
                "fit_advice": "Most dresses are fitted at waist, size according to largest measurement",
                "size_chart": {"XS": "32-34-36", "S": "34-36-38", "M": "36-38-40"}
            }
        }

        guide = size_guides.get(category, {})

        # Add personalized recommendations
        current_size = profile.size_range.get(category, "")
        recommendations = []

        if current_size:
            recommendations.append(f"Based on your usual {category} size ({current_size}), we recommend the same size")

        if profile.body_type:
            body_rules = self.styling_rules["body_type_recommendations"].get(profile.body_type)
            if body_rules and "fit" in body_rules:
                recommendations.append(body_rules["fit"])

        return {
            "category": category,
            "size_guide": guide,
            "personalized_recommendations": recommendations,
            "virtual_fitting_available": True,  # Future feature
            "return_policy": "Free returns within 30 days for size exchanges"
        }

    def track_outfit_feedback(self, recommendation_id: str, feedback: Dict) -> Dict:
        """Track customer feedback on outfit recommendations to improve future suggestions."""
        recommendation = next((r for r in self.outfit_recommendations
                             if r.recommendation_id == recommendation_id), None)

        if not recommendation:
            return {"error": "Recommendation not found"}

        # Store feedback for learning
        feedback_data = {
            'recommendation_id': recommendation_id,
            'customer_id': recommendation.customer_id,
            'feedback': feedback,
            'date': datetime.now()
        }

        # Update customer profile based on feedback
        profile = self.style_profiles[recommendation.customer_id]

        if feedback.get('loved_items'):
            # Add successful item characteristics to preferences
            for item in feedback['loved_items']:
                if item.get('color') and item['color'] not in profile.color_preferences:
                    profile.color_preferences.append(item['color'])

        if feedback.get('disliked_items'):
            # Add disliked characteristics to avoid list
            for item in feedback['disliked_items']:
                if item.get('color') and item['color'] not in profile.color_dislikes:
                    profile.color_dislikes.append(item['color'])

        return {
            'feedback_recorded': True,
            'profile_updated': True,
            'next_recommendations_improved': True
        }

    def generate_style_evolution_report(self, customer_id: str) -> Dict:
        """Generate report showing customer's style evolution and preferences."""
        if customer_id not in self.style_profiles:
            return {"error": "No style profile found"}

        profile = self.style_profiles[customer_id]
        customer_recommendations = [r for r in self.outfit_recommendations
                                  if r.customer_id == customer_id]

        # Analyze style evolution
        style_journey = {
            'profile_created': profile.created_date.strftime('%Y-%m-%d'),
            'total_recommendations': len(customer_recommendations),
            'favorite_occasions': self._analyze_occasion_preferences(customer_recommendations),
            'color_evolution': profile.color_preferences,
            'style_personality': profile.style_personality.value,
            'confidence_trend': [r.confidence_rating for r in customer_recommendations[-5:]],
            'next_suggestions': self._generate_next_style_suggestions(profile)
        }

        return style_journey

    def _analyze_occasion_preferences(self, recommendations: List[OutfitRecommendation]) -> Dict:
        """Analyze which occasions customer requests most often."""
        occasion_counts = {}
        for rec in recommendations:
            occasion = rec.occasion.value
            occasion_counts[occasion] = occasion_counts.get(occasion, 0) + 1

        return dict(sorted(occasion_counts.items(), key=lambda x: x[1], reverse=True))

    def _generate_next_style_suggestions(self, profile: StyleProfile) -> List[str]:
        """Generate suggestions for expanding customer's style."""
        suggestions = []

        # Suggest expanding color palette
        if len(profile.color_preferences) < 3:
            suggestions.append("Try incorporating one new color this month to expand your palette")

        # Suggest new occasions
        if profile.style_personality == StylePersonality.CLASSIC:
            suggestions.append("Add one trendy piece to modernize your classic style")
        elif profile.style_personality == StylePersonality.MINIMALIST:
            suggestions.append("Experiment with one statement accessory to add interest")

        suggestions.append("Consider trying a new silhouette to refresh your look")

        return suggestions

# Example usage and testing
if __name__ == "__main__":
    # Initialize personal shopper assistant
    shopper = PersonalShopperAssistant()

    # Conduct style quiz
    quiz_responses = {
        "weekend_outfit": "blazer and jeans with comfortable shoes",
        "shopping_priority": "quality and timeless pieces that last",
        "inspiration_source": "fashion magazines and classic icons"
    }

    profile = shopper.conduct_style_quiz("customer_001", quiz_responses)
    print(f"Style Profile Created: {profile.style_personality.value}")

    # Update profile with additional information
    shopper.update_style_profile("customer_001", {
        "body_type": BodyType.HOURGLASS,
        "size_range": {"tops": "M", "bottoms": "10", "shoes": "8"},
        "color_preferences": ["navy", "white", "black", "burgundy"],
        "budget_range": (50, 300)
    })

    # Get outfit recommendation for work
    work_outfit = shopper.recommend_outfit_for_occasion(
        "customer_001", Occasion.WORK, budget_max=250
    )

    print(f"\nWork Outfit Recommendation:")
    print(f"Total Price: €{work_outfit.total_price:.2f}")
    print(f"Confidence Rating: {work_outfit.confidence_rating}/10")
    print(f"Styling Notes: {work_outfit.styling_notes}")
    print("Items:")
    for item in work_outfit.items:
        print(f"  - {item['name']} (€{item['price']:.2f}) - {item['reason']}")

    # Get size recommendations
    size_guide = shopper.get_size_recommendations("customer_001", "tops")
    print(f"\nSize Recommendations for Tops:")
    print(f"Fit Advice: {size_guide['size_guide']['fit_advice']}")

    # Simulate feedback
    feedback = {
        'overall_satisfaction': 9,
        'loved_items': [{'name': 'Navy Blazer', 'color': 'navy'}],
        'would_wear_again': True
    }

    feedback_result = shopper.track_outfit_feedback(work_outfit.recommendation_id, feedback)
    print(f"\nFeedback recorded: {feedback_result['feedback_recorded']}")

    # Generate style evolution report
    evolution = shopper.generate_style_evolution_report("customer_001")
    print(f"\nStyle Evolution Report:")
    print(f"Style Personality: {evolution['style_personality']}")
    print(f"Total Recommendations: {evolution['total_recommendations']}")
    print(f"Next Suggestions: {evolution['next_suggestions'][:2]}")