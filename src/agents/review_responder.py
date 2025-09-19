"""
Review Response Agent - Professional Review Management and Response Generation

This agent monitors and responds to customer reviews across multiple platforms,
providing value worth $3000+/month through improved reputation management.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

import aiohttp
import nltk
from textblob import TextBlob
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.sentiment import SentimentIntensityAnalyzer


class ReviewPlatform(Enum):
    """Supported review platforms"""
    GOOGLE = "google"
    YELP = "yelp"
    TRIPADVISOR = "tripadvisor"
    FACEBOOK = "facebook"
    AMAZON = "amazon"
    TRUSTPILOT = "trustpilot"


class SentimentScore(Enum):
    """Review sentiment categories"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class UrgencyLevel(Enum):
    """Response urgency levels"""
    CRITICAL = "critical"  # Very negative, viral potential
    HIGH = "high"         # Negative, needs quick response
    MEDIUM = "medium"     # Mixed sentiment
    LOW = "low"          # Positive reviews


@dataclass
class Review:
    """Review data structure"""
    id: str
    platform: ReviewPlatform
    rating: float
    title: str
    content: str
    author: str
    date: datetime
    sentiment: SentimentScore
    urgency: UrgencyLevel
    keywords: List[str]
    issues: List[str]
    response_generated: bool = False
    response_sent: bool = False


@dataclass
class ResponseTemplate:
    """Response template structure"""
    sentiment: SentimentScore
    template: str
    keywords: List[str]
    tone: str


class ReviewResponseAgent:
    """
    Professional review monitoring and response generation agent.

    Features:
    - Multi-platform review monitoring
    - Advanced sentiment analysis
    - Urgency detection and prioritization
    - Personalized response generation
    - Reputation management insights
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None

        # Initialize sentiment analyzer
        self.vader_analyzer = SentimentIntensityAnalyzer()

        # Initialize advanced sentiment model
        self.sentiment_model = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            return_all_scores=True
        )

        # Platform configurations
        self.platform_configs = {
            ReviewPlatform.GOOGLE: {
                "api_endpoint": "https://maps.googleapis.com/maps/api/place",
                "headers": {"User-Agent": "ReviewBot/1.0"},
                "rate_limit": 1.0  # seconds between requests
            },
            ReviewPlatform.YELP: {
                "api_endpoint": "https://api.yelp.com/v3/businesses",
                "headers": {"Authorization": "Bearer {api_key}"},
                "rate_limit": 2.0
            },
            ReviewPlatform.TRIPADVISOR: {
                "api_endpoint": "https://api.tripadvisor.com/api/partner/2.0",
                "headers": {"X-TripAdvisor-API-Key": "{api_key}"},
                "rate_limit": 3.0
            }
        }

        # Response templates
        self.response_templates = self._load_response_templates()

        # Issue keywords
        self.issue_keywords = {
            "service": ["service", "staff", "rude", "unprofessional", "slow"],
            "quality": ["quality", "poor", "bad", "terrible", "awful"],
            "pricing": ["expensive", "overpriced", "cost", "price", "money"],
            "cleanliness": ["dirty", "clean", "hygiene", "mess", "sanitary"],
            "wait_time": ["wait", "slow", "delay", "queue", "time"],
            "product": ["product", "item", "defective", "broken", "faulty"]
        }

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _load_response_templates(self) -> Dict[SentimentScore, List[ResponseTemplate]]:
        """Load response templates for different sentiments"""
        return {
            SentimentScore.VERY_POSITIVE: [
                ResponseTemplate(
                    sentiment=SentimentScore.VERY_POSITIVE,
                    template="Thank you so much for your wonderful {rating}-star review, {name}! We're thrilled that you had such an excellent experience with {specific_mention}. Your kind words mean the world to us and motivate our team to continue delivering exceptional service. We look forward to serving you again soon!",
                    keywords=["excellent", "wonderful", "amazing", "outstanding"],
                    tone="enthusiastic"
                )
            ],
            SentimentScore.POSITIVE: [
                ResponseTemplate(
                    sentiment=SentimentScore.POSITIVE,
                    template="Thank you for your positive review, {name}! We're delighted to hear that you enjoyed {specific_mention}. Your feedback helps us continue improving our services. We appreciate your business and hope to see you again!",
                    keywords=["good", "nice", "pleasant", "satisfied"],
                    tone="appreciative"
                )
            ],
            SentimentScore.NEUTRAL: [
                ResponseTemplate(
                    sentiment=SentimentScore.NEUTRAL,
                    template="Thank you for taking the time to share your feedback, {name}. We appreciate your {rating}-star review and your honest assessment of {specific_mention}. We're always working to improve our services and would welcome the opportunity to provide you with an even better experience in the future.",
                    keywords=["okay", "average", "decent", "fair"],
                    tone="professional"
                )
            ],
            SentimentScore.NEGATIVE: [
                ResponseTemplate(
                    sentiment=SentimentScore.NEGATIVE,
                    template="Thank you for bringing this to our attention, {name}. We sincerely apologize for the issues you experienced with {specific_mention}. This is not the standard of service we strive for. We would like to make this right - please contact us directly at {contact_info} so we can address your concerns personally and improve your experience.",
                    keywords=["disappointed", "unsatisfied", "problem", "issue"],
                    tone="apologetic"
                )
            ],
            SentimentScore.VERY_NEGATIVE: [
                ResponseTemplate(
                    sentiment=SentimentScore.VERY_NEGATIVE,
                    template="We are deeply sorry about your experience, {name}, and we take your concerns very seriously. The issues you've described with {specific_mention} are completely unacceptable and do not reflect our values or standards. We would like to speak with you immediately to resolve this situation - please call us at {contact_info} or email {email}. We are committed to making this right and preventing similar issues in the future.",
                    keywords=["terrible", "awful", "worst", "horrible"],
                    tone="urgent_apologetic"
                )
            ]
        }

    async def monitor_reviews(self, business_ids: Dict[ReviewPlatform, str]) -> List[Review]:
        """Monitor reviews across multiple platforms"""
        reviews = []

        for platform, business_id in business_ids.items():
            try:
                platform_reviews = await self._fetch_platform_reviews(platform, business_id)
                reviews.extend(platform_reviews)

                # Rate limiting
                await asyncio.sleep(self.platform_configs[platform]["rate_limit"])

            except Exception as e:
                self.logger.error(f"Error fetching reviews from {platform.value}: {e}")

        # Sort by urgency and date
        reviews.sort(key=lambda r: (r.urgency.value, r.date), reverse=True)

        return reviews

    async def _fetch_platform_reviews(self, platform: ReviewPlatform, business_id: str) -> List[Review]:
        """Fetch reviews from a specific platform"""
        reviews = []

        if platform == ReviewPlatform.GOOGLE:
            reviews = await self._fetch_google_reviews(business_id)
        elif platform == ReviewPlatform.YELP:
            reviews = await self._fetch_yelp_reviews(business_id)
        elif platform == ReviewPlatform.TRIPADVISOR:
            reviews = await self._fetch_tripadvisor_reviews(business_id)

        return reviews

    async def _fetch_google_reviews(self, place_id: str) -> List[Review]:
        """Fetch Google My Business reviews"""
        reviews = []

        # Mock implementation - in production, use Google My Business API
        mock_reviews = [
            {
                "author_name": "John Smith",
                "rating": 5,
                "text": "Excellent service! The staff was very helpful and professional.",
                "time": int(datetime.now().timestamp()),
                "review_id": "google_1"
            },
            {
                "author_name": "Sarah Johnson",
                "rating": 2,
                "text": "Poor experience. Long wait time and rude staff. Very disappointed.",
                "time": int((datetime.now() - timedelta(hours=2)).timestamp()),
                "review_id": "google_2"
            }
        ]

        for review_data in mock_reviews:
            review = await self._process_review_data(
                ReviewPlatform.GOOGLE,
                review_data
            )
            reviews.append(review)

        return reviews

    async def _fetch_yelp_reviews(self, business_id: str) -> List[Review]:
        """Fetch Yelp reviews"""
        reviews = []

        # Mock implementation - in production, use Yelp Fusion API
        mock_reviews = [
            {
                "user": {"name": "Mike Davis"},
                "rating": 4,
                "text": "Good food and decent service. Would come back again.",
                "time_created": datetime.now().isoformat(),
                "id": "yelp_1"
            }
        ]

        for review_data in mock_reviews:
            review = await self._process_review_data(
                ReviewPlatform.YELP,
                review_data
            )
            reviews.append(review)

        return reviews

    async def _fetch_tripadvisor_reviews(self, business_id: str) -> List[Review]:
        """Fetch TripAdvisor reviews"""
        reviews = []

        # Mock implementation - in production, use TripAdvisor API
        mock_reviews = [
            {
                "username": "TravelLover2024",
                "rating": 3,
                "title": "Average experience",
                "text": "The location was okay but the room was not very clean.",
                "published_date": datetime.now().isoformat(),
                "id": "tripadvisor_1"
            }
        ]

        for review_data in mock_reviews:
            review = await self._process_review_data(
                ReviewPlatform.TRIPADVISOR,
                review_data
            )
            reviews.append(review)

        return reviews

    async def _process_review_data(self, platform: ReviewPlatform, data: Dict) -> Review:
        """Process raw review data into Review object"""
        # Extract review content based on platform
        if platform == ReviewPlatform.GOOGLE:
            content = data.get("text", "")
            author = data.get("author_name", "Anonymous")
            rating = float(data.get("rating", 0))
            review_id = data.get("review_id", "")
            date = datetime.fromtimestamp(data.get("time", datetime.now().timestamp()))
            title = ""
        elif platform == ReviewPlatform.YELP:
            content = data.get("text", "")
            author = data.get("user", {}).get("name", "Anonymous")
            rating = float(data.get("rating", 0))
            review_id = data.get("id", "")
            date = datetime.fromisoformat(data.get("time_created", datetime.now().isoformat()).replace('Z', '+00:00'))
            title = ""
        elif platform == ReviewPlatform.TRIPADVISOR:
            content = data.get("text", "")
            author = data.get("username", "Anonymous")
            rating = float(data.get("rating", 0))
            review_id = data.get("id", "")
            date = datetime.fromisoformat(data.get("published_date", datetime.now().isoformat()).replace('Z', '+00:00'))
            title = data.get("title", "")
        else:
            raise ValueError(f"Unsupported platform: {platform}")

        # Analyze sentiment
        sentiment = await self.analyze_sentiment(content)

        # Determine urgency
        urgency = self._determine_urgency(rating, sentiment, content)

        # Extract keywords and issues
        keywords = self._extract_keywords(content)
        issues = self._identify_issues(content)

        return Review(
            id=review_id,
            platform=platform,
            rating=rating,
            title=title,
            content=content,
            author=author,
            date=date,
            sentiment=sentiment,
            urgency=urgency,
            keywords=keywords,
            issues=issues
        )

    async def analyze_sentiment(self, text: str) -> SentimentScore:
        """Analyze sentiment using multiple models"""
        if not text.strip():
            return SentimentScore.NEUTRAL

        # VADER sentiment analysis
        vader_scores = self.vader_analyzer.polarity_scores(text)

        # RoBERTa sentiment analysis
        roberta_scores = self.sentiment_model(text)[0]

        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity

        # Combine scores (weighted average)
        vader_compound = vader_scores['compound']

        # Map RoBERTa labels to scores
        roberta_score = 0
        for score_dict in roberta_scores:
            if score_dict['label'] == 'LABEL_2':  # Positive
                roberta_score = score_dict['score']
            elif score_dict['label'] == 'LABEL_0':  # Negative
                roberta_score = -score_dict['score']

        # Weighted combination
        combined_score = (
            0.4 * vader_compound +
            0.4 * roberta_score +
            0.2 * textblob_polarity
        )

        # Map to sentiment categories
        if combined_score >= 0.6:
            return SentimentScore.VERY_POSITIVE
        elif combined_score >= 0.2:
            return SentimentScore.POSITIVE
        elif combined_score >= -0.2:
            return SentimentScore.NEUTRAL
        elif combined_score >= -0.6:
            return SentimentScore.NEGATIVE
        else:
            return SentimentScore.VERY_NEGATIVE

    def _determine_urgency(self, rating: float, sentiment: SentimentScore, content: str) -> UrgencyLevel:
        """Determine response urgency based on multiple factors"""
        # Check for viral potential keywords
        viral_keywords = ["viral", "social media", "facebook", "twitter", "instagram", "share", "tell everyone"]
        has_viral_potential = any(keyword in content.lower() for keyword in viral_keywords)

        # Check for escalation words
        escalation_words = ["manager", "corporate", "lawsuit", "attorney", "lawyer", "media", "report"]
        has_escalation = any(word in content.lower() for word in escalation_words)

        if rating <= 2 and (has_viral_potential or has_escalation):
            return UrgencyLevel.CRITICAL
        elif rating <= 2 or sentiment in [SentimentScore.NEGATIVE, SentimentScore.VERY_NEGATIVE]:
            return UrgencyLevel.HIGH
        elif rating == 3 or sentiment == SentimentScore.NEUTRAL:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from review text"""
        # Simple keyword extraction using TextBlob
        blob = TextBlob(text.lower())

        # Get noun phrases
        noun_phrases = [phrase for phrase in blob.noun_phrases if len(phrase.split()) <= 3]

        # Get adjectives that might indicate sentiment
        adjectives = []
        for word, pos in blob.tags:
            if pos.startswith('JJ'):  # Adjective
                adjectives.append(word)

        keywords = list(set(noun_phrases + adjectives))
        return keywords[:10]  # Limit to top 10

    def _identify_issues(self, text: str) -> List[str]:
        """Identify specific issues mentioned in the review"""
        text_lower = text.lower()
        identified_issues = []

        for issue_category, keywords in self.issue_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                identified_issues.append(issue_category)

        return identified_issues

    async def generate_response(self, review: Review, business_info: Dict[str, str]) -> str:
        """Generate personalized response to a review"""
        # Select appropriate template
        templates = self.response_templates.get(review.sentiment, [])
        if not templates:
            return "Thank you for your feedback. We appreciate your review."

        template = templates[0]  # Use first template for now

        # Extract specific mentions from the review
        specific_mentions = self._extract_specific_mentions(review)

        # Fill template variables
        response = template.template.format(
            name=review.author,
            rating=review.rating,
            specific_mention=specific_mentions or "your experience",
            contact_info=business_info.get("phone", "our customer service"),
            email=business_info.get("email", "customer@company.com")
        )

        # Personalize based on issues identified
        if review.issues:
            issue_text = self._generate_issue_specific_text(review.issues)
            response += f" {issue_text}"

        return response

    def _extract_specific_mentions(self, review: Review) -> str:
        """Extract specific things mentioned in the review"""
        # Look for specific service/product mentions
        text_lower = review.content.lower()

        service_mentions = []

        # Common business elements
        mentions = {
            "food": ["food", "meal", "dish", "cuisine", "menu"],
            "service": ["service", "staff", "waiter", "waitress", "server"],
            "atmosphere": ["atmosphere", "ambiance", "decor", "music", "lighting"],
            "location": ["location", "parking", "accessibility", "convenience"],
            "value": ["price", "value", "cost", "affordable", "expensive"]
        }

        for category, keywords in mentions.items():
            if any(keyword in text_lower for keyword in keywords):
                service_mentions.append(category)

        if service_mentions:
            return f"our {service_mentions[0]}"

        return "your experience with us"

    def _generate_issue_specific_text(self, issues: List[str]) -> str:
        """Generate issue-specific response text"""
        issue_responses = {
            "service": "We are reviewing our service procedures to ensure this doesn't happen again.",
            "quality": "We take quality seriously and are investigating this matter.",
            "pricing": "We strive to provide excellent value and will review our pricing structure.",
            "cleanliness": "Cleanliness is a top priority for us, and we are addressing this immediately.",
            "wait_time": "We are working to improve our efficiency to reduce wait times.",
            "product": "We are checking our quality control processes to prevent similar issues."
        }

        responses = [issue_responses.get(issue, "") for issue in issues if issue in issue_responses]

        if responses:
            return " ".join(responses)

        return "We are taking steps to improve based on your feedback."

    async def prioritize_responses(self, reviews: List[Review]) -> List[Review]:
        """Prioritize reviews for response based on urgency and business impact"""
        # Calculate response priority score
        for review in reviews:
            score = 0

            # Urgency weight
            urgency_weights = {
                UrgencyLevel.CRITICAL: 100,
                UrgencyLevel.HIGH: 75,
                UrgencyLevel.MEDIUM: 50,
                UrgencyLevel.LOW: 25
            }
            score += urgency_weights[review.urgency]

            # Recency weight (more recent = higher priority)
            hours_since = (datetime.now() - review.date).total_seconds() / 3600
            if hours_since <= 24:
                score += 30
            elif hours_since <= 48:
                score += 20
            elif hours_since <= 72:
                score += 10

            # Platform weight
            platform_weights = {
                ReviewPlatform.GOOGLE: 30,  # High visibility
                ReviewPlatform.YELP: 25,
                ReviewPlatform.TRIPADVISOR: 20,
                ReviewPlatform.FACEBOOK: 15,
                ReviewPlatform.AMAZON: 10,
                ReviewPlatform.TRUSTPILOT: 10
            }
            score += platform_weights.get(review.platform, 5)

            # Rating impact (lower ratings need faster response)
            if review.rating <= 2:
                score += 40
            elif review.rating <= 3:
                score += 20

            review.priority_score = score

        # Sort by priority score (highest first)
        return sorted(reviews, key=lambda r: getattr(r, 'priority_score', 0), reverse=True)

    async def get_reputation_insights(self, reviews: List[Review]) -> Dict[str, Any]:
        """Generate reputation management insights"""
        if not reviews:
            return {}

        total_reviews = len(reviews)

        # Sentiment distribution
        sentiment_counts = {}
        for sentiment in SentimentScore:
            sentiment_counts[sentiment.value] = sum(1 for r in reviews if r.sentiment == sentiment)

        # Average rating
        avg_rating = sum(r.rating for r in reviews) / total_reviews

        # Platform distribution
        platform_counts = {}
        for platform in ReviewPlatform:
            platform_counts[platform.value] = sum(1 for r in reviews if r.platform == platform)

        # Common issues
        all_issues = []
        for review in reviews:
            all_issues.extend(review.issues)

        issue_frequency = {}
        for issue in set(all_issues):
            issue_frequency[issue] = all_issues.count(issue)

        # Response rate
        total_responses = sum(1 for r in reviews if r.response_generated)
        response_rate = (total_responses / total_reviews) * 100 if total_reviews > 0 else 0

        # Urgency breakdown
        urgency_counts = {}
        for urgency in UrgencyLevel:
            urgency_counts[urgency.value] = sum(1 for r in reviews if r.urgency == urgency)

        return {
            "total_reviews": total_reviews,
            "average_rating": round(avg_rating, 2),
            "sentiment_distribution": sentiment_counts,
            "platform_distribution": platform_counts,
            "common_issues": dict(sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)),
            "response_rate": round(response_rate, 1),
            "urgency_breakdown": urgency_counts,
            "improvement_suggestions": self._generate_improvement_suggestions(reviews)
        }

    def _generate_improvement_suggestions(self, reviews: List[Review]) -> List[str]:
        """Generate actionable improvement suggestions"""
        suggestions = []

        # Analyze negative reviews for patterns
        negative_reviews = [r for r in reviews if r.sentiment in [SentimentScore.NEGATIVE, SentimentScore.VERY_NEGATIVE]]

        if len(negative_reviews) > len(reviews) * 0.3:  # More than 30% negative
            suggestions.append("Consider implementing staff training programs to address service quality issues")

        # Common issues analysis
        all_issues = []
        for review in negative_reviews:
            all_issues.extend(review.issues)

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Top issues
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        for issue, count in top_issues:
            if issue == "service":
                suggestions.append("Focus on customer service training and staff attitude improvement")
            elif issue == "wait_time":
                suggestions.append("Implement systems to reduce customer wait times")
            elif issue == "quality":
                suggestions.append("Review quality control processes and standards")
            elif issue == "cleanliness":
                suggestions.append("Enhance cleaning protocols and hygiene standards")
            elif issue == "pricing":
                suggestions.append("Review pricing strategy and value proposition")

        # Response time suggestions
        unresponded_critical = sum(1 for r in reviews if r.urgency == UrgencyLevel.CRITICAL and not r.response_generated)
        if unresponded_critical > 0:
            suggestions.append("Implement automated alerts for critical reviews requiring immediate response")

        return suggestions[:5]  # Limit to top 5 suggestions


# Usage example and testing
async def main():
    """Example usage of the Review Response Agent"""
    async with ReviewResponseAgent() as agent:
        # Example business IDs for different platforms
        business_ids = {
            ReviewPlatform.GOOGLE: "ChIJ123456789",
            ReviewPlatform.YELP: "business-123",
            ReviewPlatform.TRIPADVISOR: "d123456"
        }

        # Business information for responses
        business_info = {
            "name": "Sample Restaurant",
            "phone": "(555) 123-4567",
            "email": "manager@samplerestaurant.com"
        }

        print("🔍 Monitoring reviews across platforms...")
        reviews = await agent.monitor_reviews(business_ids)

        print(f"\n📊 Found {len(reviews)} reviews")

        # Prioritize responses
        prioritized_reviews = await agent.prioritize_responses(reviews)

        print("\n🎯 Processing high-priority reviews:")
        for review in prioritized_reviews[:3]:  # Top 3 priority
            print(f"\n📝 Review from {review.author} on {review.platform.value}")
            print(f"Rating: {review.rating}/5")
            print(f"Content: {review.content}")
            print(f"Sentiment: {review.sentiment.value}")
            print(f"Urgency: {review.urgency.value}")
            print(f"Issues: {', '.join(review.issues) if review.issues else 'None'}")

            # Generate response
            response = await agent.generate_response(review, business_info)
            print(f"\n💬 Generated Response:\n{response}")
            print("-" * 80)

        # Get reputation insights
        insights = await agent.get_reputation_insights(reviews)
        print(f"\n📈 Reputation Insights:")
        print(f"Average Rating: {insights['average_rating']}/5")
        print(f"Response Rate: {insights['response_rate']}%")
        print(f"Common Issues: {list(insights['common_issues'].keys())[:3]}")
        print(f"Improvement Suggestions:")
        for suggestion in insights['improvement_suggestions']:
            print(f"  • {suggestion}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the example
    asyncio.run(main())