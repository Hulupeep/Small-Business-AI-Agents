"""
Social Media & Marketing Agent

Automates Instagram posts, creates engaging content, tracks performance,
and manages marketing campaigns. Saves hours weekly while boosting engagement.
"""

import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid

@dataclass
class SocialPost:
    """Represents a social media post."""
    post_id: str
    platform: str  # instagram, facebook, twitter
    content: str
    image_path: Optional[str] = None
    hashtags: List[str] = field(default_factory=list)
    scheduled_time: Optional[datetime] = None
    posted_time: Optional[datetime] = None
    engagement: Dict = field(default_factory=dict)  # likes, comments, shares
    performance_score: float = 0.0

@dataclass
class ContentTemplate:
    """Template for generating social media content."""
    template_type: str  # new_arrival, sale, styling_tip, behind_scenes
    content_template: str
    hashtag_groups: List[List[str]]
    best_times: List[str]  # ["10:00", "14:00", "18:00"]
    frequency: str  # daily, weekly, monthly

@dataclass
class InfluencerCollaboration:
    """Represents an influencer collaboration."""
    collab_id: str
    influencer_name: str
    instagram_handle: str
    follower_count: int
    engagement_rate: float
    collaboration_type: str  # gifted, paid, ambassador
    products_featured: List[str]
    start_date: datetime
    end_date: datetime
    performance_metrics: Dict = field(default_factory=dict)

class SocialMediaManager:
    """
    AI-powered social media and marketing automation system.

    Key Features:
    - Auto-generate Instagram posts with trending hashtags
    - Create outfit inspiration and styling content
    - Schedule posts for optimal engagement times
    - Track performance and adjust strategy
    - Manage influencer collaborations
    - Generate marketing campaigns
    """

    def __init__(self, store_name: str = "Threads & Things",
                 instagram_handle: str = "@threadsandthings"):
        self.store_name = store_name
        self.instagram_handle = instagram_handle
        self.posts = []
        self.templates = self._initialize_templates()
        self.collaborations = []
        self.hashtag_performance = {}

    def _initialize_templates(self) -> List[ContentTemplate]:
        """Initialize content templates for different types of posts."""
        return [
            ContentTemplate(
                template_type="new_arrival",
                content_template="✨ New arrival alert! {item_description} {styling_suggestion} Available now at {store_name}! {call_to_action}",
                hashtag_groups=[
                    ["#NewArrival", "#Fashion", "#Style", "#Shopping"],
                    ["#Boutique", "#ShopLocal", "#WomensStyle"],
                    ["#OOTD", "#FashionInspo", "#Trendy", "#Chic"]
                ],
                best_times=["10:00", "14:00", "18:00"],
                frequency="daily"
            ),
            ContentTemplate(
                template_type="styling_tip",
                content_template="💡 Styling tip: {styling_advice} Try pairing {item1} with {item2} for {occasion}. {confidence_boost}",
                hashtag_groups=[
                    ["#StylingTip", "#FashionAdvice", "#StyleGuide"],
                    ["#PersonalStyle", "#FashionTips", "#OutfitIdeas"],
                    ["#ConfidentStyle", "#FashionInspiration"]
                ],
                best_times=["09:00", "13:00", "17:00"],
                frequency="weekly"
            ),
            ContentTemplate(
                template_type="behind_scenes",
                content_template="👗 Behind the scenes at {store_name}! {activity_description} We love {personal_touch} {community_feeling}",
                hashtag_groups=[
                    ["#BehindTheScenes", "#SmallBusiness", "#ShopLocal"],
                    ["#BoutiqueLife", "#TeamWork", "#Passion"],
                    ["#LocalBusiness", "#Community", "#Authentic"]
                ],
                best_times=["11:00", "15:00", "19:00"],
                frequency="weekly"
            ),
            ContentTemplate(
                template_type="sale_promotion",
                content_template="🔥 {sale_type} {discount_info} {urgency_message} Shop now: {call_to_action} {limited_time}",
                hashtag_groups=[
                    ["#Sale", "#Discount", "#Shopping", "#Deal"],
                    ["#LimitedTime", "#Fashion", "#Savings"],
                    ["#ShopNow", "#Offer", "#Boutique"]
                ],
                best_times=["12:00", "16:00", "20:00"],
                frequency="weekly"
            ),
            ContentTemplate(
                template_type="customer_feature",
                content_template="💖 Looking gorgeous in {item_name}! Thank you {customer_name} for choosing {store_name}! {styling_compliment} {encourage_tagging}",
                hashtag_groups=[
                    ["#CustomerLove", "#StyleStar", "#HappyCustomer"],
                    ["#OutfitGoals", "#Confidence", "#Beautiful"],
                    ["#Community", "#Fashion", "#Inspiration"]
                ],
                best_times=["10:30", "14:30", "18:30"],
                frequency="weekly"
            )
        ]

    def generate_new_arrival_post(self, item_name: str, price: float,
                                 category: str, unique_features: List[str]) -> SocialPost:
        """Generate an engaging post for new arrivals."""

        # Styling suggestions based on category
        styling_suggestions = {
            "dresses": ["Perfect for date nights 💕", "Ideal for special occasions ✨", "Great for both work and weekend 👗"],
            "tops": ["Pairs beautifully with jeans or skirts 👚", "Perfect layering piece 🧥", "Dress up or down effortlessly 💫"],
            "accessories": ["The perfect finishing touch ✨", "Elevates any outfit instantly 💎", "A must-have for your collection 👜"],
            "shoes": ["Comfortable AND stylish 👠", "Goes with everything in your wardrobe 👡", "Your feet will thank you! 💕"]
        }

        # Call to action variations
        call_to_actions = [
            "DM us for sizing or to hold your piece! 💌",
            "Visit us on Shop Street or message for details! 🏪",
            "Limited pieces available - don't miss out! ⚡",
            "Tag a friend who would love this! 👯‍♀️"
        ]

        template = next(t for t in self.templates if t.template_type == "new_arrival")

        content = template.content_template.format(
            item_description=f"This gorgeous {item_name} (€{price:.0f})",
            styling_suggestion=random.choice(styling_suggestions.get(category, ["Absolutely stunning! ✨"])),
            store_name=self.store_name,
            call_to_action=random.choice(call_to_actions)
        )

        # Select hashtags
        selected_hashtags = []
        for group in template.hashtag_groups:
            selected_hashtags.extend(random.sample(group, min(2, len(group))))

        # Add item-specific hashtags
        if "unique" in " ".join(unique_features).lower():
            selected_hashtags.append("#OneOfAKind")
        if price < 50:
            selected_hashtags.append("#Affordable")
        elif price > 150:
            selected_hashtags.append("#Luxury")

        post = SocialPost(
            post_id=str(uuid.uuid4())[:8],
            platform="instagram",
            content=content,
            hashtags=selected_hashtags[:15],  # Instagram limit
            scheduled_time=self._get_optimal_posting_time(template.best_times)
        )

        self.posts.append(post)
        return post

    def generate_styling_tip_post(self, item1: str, item2: str, occasion: str) -> SocialPost:
        """Generate a styling tip post featuring specific items."""

        styling_advice = [
            "The secret to effortless style? Mixing textures and proportions! 🎨",
            "When in doubt, add one statement piece to elevate your look ✨",
            "Color coordination doesn't mean everything has to match perfectly! 🌈",
            "The best accessory you can wear is confidence! 💪",
            "Great style is about feeling comfortable in your own skin 💕"
        ]

        confidence_boosts = [
            "You'll feel unstoppable! 💪",
            "Confidence level: 100! ✨",
            "Get ready to turn heads! 👀",
            "You've got this! 💕",
            "Own your style! 🔥"
        ]

        template = next(t for t in self.templates if t.template_type == "styling_tip")

        content = template.content_template.format(
            styling_advice=random.choice(styling_advice),
            item1=item1,
            item2=item2,
            occasion=occasion,
            confidence_boost=random.choice(confidence_boosts)
        )

        # Select hashtags
        selected_hashtags = []
        for group in template.hashtag_groups:
            selected_hashtags.extend(random.sample(group, min(3, len(group))))

        post = SocialPost(
            post_id=str(uuid.uuid4())[:8],
            platform="instagram",
            content=content,
            hashtags=selected_hashtags[:15],
            scheduled_time=self._get_optimal_posting_time(template.best_times)
        )

        self.posts.append(post)
        return post

    def generate_sale_post(self, sale_type: str, discount_percentage: float,
                          items_on_sale: List[str], end_date: datetime) -> SocialPost:
        """Generate an engaging sale promotion post."""

        sale_types = {
            "flash": "⚡ FLASH SALE ALERT!",
            "weekend": "🌟 Weekend Special!",
            "seasonal": "🍂 Seasonal Sale!",
            "clearance": "🏷️ Clearance Event!",
            "birthday": "🎉 Birthday Sale!"
        }

        urgency_messages = [
            "Don't sleep on this one! 😴",
            "Your wardrobe will thank you! 👗",
            "These prices won't last long! ⏰",
            "Treat yourself - you deserve it! 💎"
        ]

        days_left = (end_date - datetime.now()).days
        if days_left <= 1:
            limited_time = "Ends tonight! ⏰"
        elif days_left <= 3:
            limited_time = f"Only {days_left} days left! 📅"
        else:
            limited_time = f"Until {end_date.strftime('%B %d')}! 📅"

        template = next(t for t in self.templates if t.template_type == "sale_promotion")

        content = template.content_template.format(
            sale_type=sale_types.get(sale_type, "🔥 SALE!"),
            discount_info=f"{discount_percentage:.0f}% off {', '.join(items_on_sale[:3])}{'...' if len(items_on_sale) > 3 else ''}!",
            urgency_message=random.choice(urgency_messages),
            call_to_action="Visit us or DM for details!",
            limited_time=limited_time
        )

        # Select hashtags
        selected_hashtags = []
        for group in template.hashtag_groups:
            selected_hashtags.extend(random.sample(group, min(3, len(group))))

        post = SocialPost(
            post_id=str(uuid.uuid4())[:8],
            platform="instagram",
            content=content,
            hashtags=selected_hashtags[:15],
            scheduled_time=self._get_optimal_posting_time(template.best_times)
        )

        self.posts.append(post)
        return post

    def generate_behind_scenes_post(self, activity: str) -> SocialPost:
        """Generate a behind-the-scenes post to build community."""

        activities = {
            "styling": "Creating the perfect outfit combinations for our lovely customers! 💕",
            "inventory": "Carefully selecting each piece that comes into our boutique ✨",
            "window_display": "Setting up our window display - can't wait for you to see it! 🪟",
            "customer_service": "Helping our amazing customers find their perfect pieces! 🛍️",
            "new_arrivals": "Unpacking gorgeous new arrivals - it's like Christmas morning! 🎁"
        }

        personal_touches = [
            "the personal touch we put into everything we do! 💝",
            "getting to know each customer's unique style! 👗",
            "being part of your fashion journey! ✨",
            "helping you feel confident and beautiful! 💪",
            "the smile on your face when you find 'the one'! 😊"
        ]

        community_feelings = [
            "Thank you for supporting our small business! 🏪",
            "You make what we do so rewarding! 💕",
            "Our customers are the best! 🌟",
            "Grateful for this amazing community! 🤗",
            "You inspire us every day! ✨"
        ]

        template = next(t for t in self.templates if t.template_type == "behind_scenes")

        content = template.content_template.format(
            store_name=self.store_name,
            activity_description=activities.get(activity, f"Working hard on {activity}!"),
            personal_touch=random.choice(personal_touches),
            community_feeling=random.choice(community_feelings)
        )

        # Select hashtags
        selected_hashtags = []
        for group in template.hashtag_groups:
            selected_hashtags.extend(random.sample(group, min(3, len(group))))

        post = SocialPost(
            post_id=str(uuid.uuid4())[:8],
            platform="instagram",
            content=content,
            hashtags=selected_hashtags[:15],
            scheduled_time=self._get_optimal_posting_time(template.best_times)
        )

        self.posts.append(post)
        return post

    def _get_optimal_posting_time(self, preferred_times: List[str]) -> datetime:
        """Calculate optimal posting time based on performance data."""
        # For now, randomly select from preferred times
        # In production, this would analyze engagement data
        time_str = random.choice(preferred_times)
        hour, minute = map(int, time_str.split(':'))

        # Schedule for next occurrence of this time
        now = datetime.now()
        scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if scheduled <= now:
            scheduled += timedelta(days=1)

        return scheduled

    def track_post_performance(self, post_id: str, likes: int, comments: int,
                             shares: int, saves: int) -> Dict:
        """Track and analyze post performance."""
        post = next((p for p in self.posts if p.post_id == post_id), None)
        if not post:
            return {"error": "Post not found"}

        post.engagement = {
            'likes': likes,
            'comments': comments,
            'shares': shares,
            'saves': saves,
            'total_engagement': likes + comments + shares + saves
        }

        # Calculate performance score (weighted)
        post.performance_score = (
            likes * 1 +
            comments * 3 +  # Comments are more valuable
            shares * 5 +    # Shares are very valuable
            saves * 4       # Saves indicate high interest
        )

        # Update hashtag performance
        for hashtag in post.hashtags:
            if hashtag not in self.hashtag_performance:
                self.hashtag_performance[hashtag] = {'total_posts': 0, 'total_engagement': 0}

            self.hashtag_performance[hashtag]['total_posts'] += 1
            self.hashtag_performance[hashtag]['total_engagement'] += post.engagement['total_engagement']

        return {
            'post_id': post_id,
            'performance_score': post.performance_score,
            'engagement_rate': post.engagement['total_engagement'],
            'top_performing_hashtags': self._get_top_hashtags(5)
        }

    def _get_top_hashtags(self, limit: int = 10) -> List[Tuple[str, float]]:
        """Get top performing hashtags based on engagement."""
        hashtag_scores = []

        for hashtag, data in self.hashtag_performance.items():
            if data['total_posts'] > 0:
                avg_engagement = data['total_engagement'] / data['total_posts']
                hashtag_scores.append((hashtag, avg_engagement))

        return sorted(hashtag_scores, key=lambda x: x[1], reverse=True)[:limit]

    def schedule_content_calendar(self, days_ahead: int = 7) -> List[SocialPost]:
        """Generate a content calendar for the next N days."""
        calendar = []
        start_date = datetime.now()

        for day in range(days_ahead):
            date = start_date + timedelta(days=day)
            day_name = date.strftime('%A')

            # Content strategy by day of week
            if day_name in ['Monday', 'Wednesday', 'Friday']:
                # New arrival or styling tip
                post_type = random.choice(['new_arrival', 'styling_tip'])
            elif day_name in ['Tuesday', 'Thursday']:
                # Behind scenes or customer feature
                post_type = random.choice(['behind_scenes', 'customer_feature'])
            elif day_name == 'Saturday':
                # Sale or promotion
                post_type = 'sale_promotion'
            else:  # Sunday
                # Inspirational or styling tip
                post_type = 'styling_tip'

            # Generate appropriate post (simplified for demo)
            if post_type == 'new_arrival':
                post = self.generate_new_arrival_post(
                    "Sample Item", 89.99, "dresses", ["unique", "trending"]
                )
            elif post_type == 'styling_tip':
                post = self.generate_styling_tip_post(
                    "blazer", "jeans", "work meetings"
                )
            elif post_type == 'behind_scenes':
                post = self.generate_behind_scenes_post("styling")
            elif post_type == 'sale_promotion':
                post = self.generate_sale_post(
                    "weekend", 20, ["dresses", "tops"], date + timedelta(days=2)
                )

            # Adjust scheduled time to the target date
            post.scheduled_time = date.replace(
                hour=post.scheduled_time.hour,
                minute=post.scheduled_time.minute
            )

            calendar.append(post)

        return calendar

    def generate_weekly_social_report(self) -> Dict:
        """Generate weekly social media performance report."""
        week_ago = datetime.now() - timedelta(days=7)
        weekly_posts = [p for p in self.posts
                       if p.posted_time and p.posted_time >= week_ago]

        if not weekly_posts:
            return {"message": "No posts in the last week"}

        total_engagement = sum(p.engagement.get('total_engagement', 0) for p in weekly_posts)
        avg_performance = sum(p.performance_score for p in weekly_posts) / len(weekly_posts)

        # Best performing post
        best_post = max(weekly_posts, key=lambda p: p.performance_score)

        # Content type performance
        content_types = {}
        for post in weekly_posts:
            content_type = post.content.split()[0]  # First word as type indicator
            if content_type not in content_types:
                content_types[content_type] = {'posts': 0, 'engagement': 0}
            content_types[content_type]['posts'] += 1
            content_types[content_type]['engagement'] += post.engagement.get('total_engagement', 0)

        return {
            'week_ending': datetime.now().strftime('%Y-%m-%d'),
            'total_posts': len(weekly_posts),
            'total_engagement': total_engagement,
            'average_performance_score': avg_performance,
            'best_performing_post': {
                'content': best_post.content[:100] + "...",
                'engagement': best_post.engagement.get('total_engagement', 0),
                'performance_score': best_post.performance_score
            },
            'top_hashtags': self._get_top_hashtags(5),
            'content_type_performance': content_types,
            'recommendations': self._generate_content_recommendations(weekly_posts)
        }

    def _generate_content_recommendations(self, posts: List[SocialPost]) -> List[str]:
        """Generate recommendations based on performance analysis."""
        recommendations = []

        if not posts:
            return ["Start posting regularly to build engagement!"]

        # Analyze engagement patterns
        avg_engagement = sum(p.engagement.get('total_engagement', 0) for p in posts) / len(posts)

        if avg_engagement < 50:
            recommendations.append("Try using more engaging hashtags and asking questions in posts")

        # Check posting frequency
        if len(posts) < 5:
            recommendations.append("Increase posting frequency to 1-2 times per day for better reach")

        # Hashtag analysis
        top_hashtags = self._get_top_hashtags(3)
        if top_hashtags:
            recommendations.append(f"Keep using high-performing hashtags like {top_hashtags[0][0]}")

        recommendations.append("Engage with customer comments within 2 hours for better algorithm performance")
        recommendations.append("Share user-generated content to build community")

        return recommendations

# Example usage and testing
if __name__ == "__main__":
    # Initialize social media manager
    sm = SocialMediaManager("Threads & Things", "@threadsandthings")

    # Generate different types of posts
    print("=== Generated Social Media Posts ===\n")

    # New arrival post
    new_arrival = sm.generate_new_arrival_post(
        "Emerald Green Blazer", 129.99, "tops", ["unique", "trending", "versatile"]
    )
    print("NEW ARRIVAL POST:")
    print(f"Content: {new_arrival.content}")
    print(f"Hashtags: {' '.join(new_arrival.hashtags)}")
    print(f"Scheduled: {new_arrival.scheduled_time.strftime('%Y-%m-%d %H:%M')}\n")

    # Styling tip post
    styling_tip = sm.generate_styling_tip_post(
        "black ankle boots", "midi dress", "autumn dinners"
    )
    print("STYLING TIP POST:")
    print(f"Content: {styling_tip.content}")
    print(f"Hashtags: {' '.join(styling_tip.hashtags)}\n")

    # Sale post
    sale_post = sm.generate_sale_post(
        "flash", 25, ["dresses", "tops", "accessories"],
        datetime.now() + timedelta(days=2)
    )
    print("SALE POST:")
    print(f"Content: {sale_post.content}")
    print(f"Hashtags: {' '.join(sale_post.hashtags)}\n")

    # Generate weekly calendar
    print("=== 7-Day Content Calendar ===")
    calendar = sm.schedule_content_calendar(7)
    for i, post in enumerate(calendar, 1):
        print(f"Day {i} ({post.scheduled_time.strftime('%A')}): {post.content[:80]}...")

    # Simulate engagement tracking
    sm.track_post_performance(new_arrival.post_id, 45, 8, 3, 12)
    sm.track_post_performance(styling_tip.post_id, 32, 5, 1, 8)

    # Generate report
    print(f"\n=== Weekly Report ===")
    report = sm.generate_weekly_social_report()
    print(f"Total posts: {report.get('total_posts', 0)}")
    print(f"Total engagement: {report.get('total_engagement', 0)}")
    print(f"Recommendations: {report.get('recommendations', [])[:2]}")