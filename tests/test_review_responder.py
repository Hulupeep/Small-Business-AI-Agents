"""
Test suite for Review Response Agent
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from src.agents.review_responder import (
    ReviewResponseAgent,
    Review,
    ReviewPlatform,
    SentimentScore,
    UrgencyLevel
)


@pytest.fixture
def agent():
    """Create ReviewResponseAgent instance for testing"""
    return ReviewResponseAgent()


@pytest.fixture
def sample_reviews():
    """Sample reviews for testing"""
    return [
        Review(
            id="review_1",
            platform=ReviewPlatform.GOOGLE,
            rating=5.0,
            title="",
            content="Excellent service! The staff was very helpful and professional.",
            author="John Smith",
            date=datetime.now(),
            sentiment=SentimentScore.VERY_POSITIVE,
            urgency=UrgencyLevel.LOW,
            keywords=["excellent", "helpful", "professional"],
            issues=[]
        ),
        Review(
            id="review_2",
            platform=ReviewPlatform.YELP,
            rating=2.0,
            title="Poor Experience",
            content="Poor experience. Long wait time and rude staff. Very disappointed.",
            author="Sarah Johnson",
            date=datetime.now() - timedelta(hours=2),
            sentiment=SentimentScore.NEGATIVE,
            urgency=UrgencyLevel.HIGH,
            keywords=["poor", "wait time", "rude"],
            issues=["service", "wait_time"]
        ),
        Review(
            id="review_3",
            platform=ReviewPlatform.TRIPADVISOR,
            rating=1.0,
            title="Terrible",
            content="Absolutely terrible experience. Dirty room, broken AC, and will share this on social media!",
            author="Angry Customer",
            date=datetime.now() - timedelta(minutes=30),
            sentiment=SentimentScore.VERY_NEGATIVE,
            urgency=UrgencyLevel.CRITICAL,
            keywords=["terrible", "dirty", "broken"],
            issues=["cleanliness", "quality"]
        )
    ]


class TestReviewResponseAgent:
    """Test cases for ReviewResponseAgent"""

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, agent):
        """Test sentiment analysis functionality"""
        # Very positive text
        sentiment = await agent.analyze_sentiment("Amazing service! Absolutely love this place!")
        assert sentiment in [SentimentScore.POSITIVE, SentimentScore.VERY_POSITIVE]

        # Negative text
        sentiment = await agent.analyze_sentiment("Terrible service, very disappointed")
        assert sentiment in [SentimentScore.NEGATIVE, SentimentScore.VERY_NEGATIVE]

        # Neutral text
        sentiment = await agent.analyze_sentiment("It was okay, nothing special")
        assert sentiment == SentimentScore.NEUTRAL

        # Empty text
        sentiment = await agent.analyze_sentiment("")
        assert sentiment == SentimentScore.NEUTRAL

    def test_urgency_determination(self, agent):
        """Test urgency level determination"""
        # Critical: Low rating with viral potential
        urgency = agent._determine_urgency(
            rating=1.0,
            sentiment=SentimentScore.VERY_NEGATIVE,
            content="Will share this on social media!"
        )
        assert urgency == UrgencyLevel.CRITICAL

        # High: Low rating
        urgency = agent._determine_urgency(
            rating=2.0,
            sentiment=SentimentScore.NEGATIVE,
            content="Poor service"
        )
        assert urgency == UrgencyLevel.HIGH

        # Low: High rating
        urgency = agent._determine_urgency(
            rating=5.0,
            sentiment=SentimentScore.VERY_POSITIVE,
            content="Great experience!"
        )
        assert urgency == UrgencyLevel.LOW

        # Medium: Neutral
        urgency = agent._determine_urgency(
            rating=3.0,
            sentiment=SentimentScore.NEUTRAL,
            content="It was okay"
        )
        assert urgency == UrgencyLevel.MEDIUM

    def test_keyword_extraction(self, agent):
        """Test keyword extraction from review text"""
        text = "The food was excellent and the service was outstanding"
        keywords = agent._extract_keywords(text)

        assert isinstance(keywords, list)
        assert len(keywords) <= 10
        # Should contain relevant adjectives and noun phrases
        assert any(keyword in ["excellent", "outstanding", "food", "service"] for keyword in keywords)

    def test_issue_identification(self, agent):
        """Test issue identification in reviews"""
        # Service issues
        issues = agent._identify_issues("The staff was very rude and unprofessional")
        assert "service" in issues

        # Quality issues
        issues = agent._identify_issues("The food quality was terrible and awful")
        assert "quality" in issues

        # Wait time issues
        issues = agent._identify_issues("Had to wait too long for service")
        assert "wait_time" in issues

        # Cleanliness issues
        issues = agent._identify_issues("The place was dirty and not clean")
        assert "cleanliness" in issues

        # No issues
        issues = agent._identify_issues("Everything was perfect")
        assert len(issues) == 0

    @pytest.mark.asyncio
    async def test_response_generation(self, agent, sample_reviews):
        """Test response generation for different sentiment types"""
        business_info = {
            "name": "Test Business",
            "phone": "(555) 123-4567",
            "email": "manager@test.com"
        }

        # Positive review response
        positive_review = sample_reviews[0]
        response = await agent.generate_response(positive_review, business_info)

        assert isinstance(response, str)
        assert len(response) > 0
        assert positive_review.author in response
        assert "thank" in response.lower()

        # Negative review response
        negative_review = sample_reviews[1]
        response = await agent.generate_response(negative_review, business_info)

        assert isinstance(response, str)
        assert len(response) > 0
        assert negative_review.author in response
        assert any(word in response.lower() for word in ["sorry", "apologize", "sincerely"])
        assert business_info["phone"] in response

    @pytest.mark.asyncio
    async def test_prioritize_responses(self, agent, sample_reviews):
        """Test review prioritization"""
        prioritized = await agent.prioritize_responses(sample_reviews)

        assert isinstance(prioritized, list)
        assert len(prioritized) == len(sample_reviews)

        # Critical urgency should be first
        assert prioritized[0].urgency == UrgencyLevel.CRITICAL

        # High urgency should come before low urgency
        high_urgency_indices = [i for i, r in enumerate(prioritized) if r.urgency == UrgencyLevel.HIGH]
        low_urgency_indices = [i for i, r in enumerate(prioritized) if r.urgency == UrgencyLevel.LOW]

        if high_urgency_indices and low_urgency_indices:
            assert min(high_urgency_indices) < min(low_urgency_indices)

    @pytest.mark.asyncio
    async def test_reputation_insights(self, agent, sample_reviews):
        """Test reputation insights generation"""
        insights = await agent.get_reputation_insights(sample_reviews)

        assert isinstance(insights, dict)
        assert "total_reviews" in insights
        assert "average_rating" in insights
        assert "sentiment_distribution" in insights
        assert "platform_distribution" in insights
        assert "common_issues" in insights
        assert "improvement_suggestions" in insights

        assert insights["total_reviews"] == len(sample_reviews)
        assert 1.0 <= insights["average_rating"] <= 5.0

        # Check sentiment distribution
        sentiment_dist = insights["sentiment_distribution"]
        total_sentiments = sum(sentiment_dist.values())
        assert total_sentiments == len(sample_reviews)

        # Check platform distribution
        platform_dist = insights["platform_distribution"]
        assert isinstance(platform_dist, dict)

    def test_specific_mention_extraction(self, agent):
        """Test extraction of specific mentions from reviews"""
        review = Mock()
        review.content = "The food was great and the service was excellent"

        mention = agent._extract_specific_mentions(review)
        assert mention in ["our food", "our service", "your experience with us"]

        # Test with no specific mentions
        review.content = "It was okay"
        mention = agent._extract_specific_mentions(review)
        assert mention == "your experience with us"

    def test_issue_specific_text_generation(self, agent):
        """Test generation of issue-specific response text"""
        # Service issues
        text = agent._generate_issue_specific_text(["service"])
        assert "service" in text.lower()

        # Quality issues
        text = agent._generate_issue_specific_text(["quality"])
        assert "quality" in text.lower()

        # Multiple issues
        text = agent._generate_issue_specific_text(["service", "cleanliness"])
        assert len(text) > 0

        # No issues
        text = agent._generate_issue_specific_text([])
        assert len(text) > 0

    def test_improvement_suggestions(self, agent, sample_reviews):
        """Test improvement suggestions generation"""
        suggestions = agent._generate_improvement_suggestions(sample_reviews)

        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5  # Should limit to top 5

        # Should suggest improvements based on negative reviews
        if any(r.sentiment in [SentimentScore.NEGATIVE, SentimentScore.VERY_NEGATIVE] for r in sample_reviews):
            assert len(suggestions) > 0

    @pytest.mark.asyncio
    async def test_monitor_reviews_mock(self, agent):
        """Test review monitoring with mocked API calls"""
        business_ids = {
            ReviewPlatform.GOOGLE: "test_place_id",
            ReviewPlatform.YELP: "test_business_id"
        }

        with patch.object(agent, '_fetch_platform_reviews', new_callable=AsyncMock) as mock_fetch:
            # Mock return value
            mock_review = Mock()
            mock_review.platform = ReviewPlatform.GOOGLE
            mock_review.urgency = UrgencyLevel.LOW
            mock_review.date = datetime.now()

            mock_fetch.return_value = [mock_review]

            reviews = await agent.monitor_reviews(business_ids)

            assert isinstance(reviews, list)
            assert len(reviews) >= 0
            # Should be called for each platform
            assert mock_fetch.call_count == len(business_ids)

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality"""
        async with ReviewResponseAgent() as agent:
            assert agent.session is not None

        # Session should be closed after exiting context
        assert agent.session.closed

    def test_response_template_loading(self, agent):
        """Test that response templates are properly loaded"""
        templates = agent.response_templates

        assert isinstance(templates, dict)
        assert len(templates) > 0

        # Should have templates for each sentiment type
        for sentiment in SentimentScore:
            assert sentiment in templates

        # Each template should have required fields
        for sentiment, template_list in templates.items():
            for template in template_list:
                assert hasattr(template, 'template')
                assert hasattr(template, 'sentiment')
                assert hasattr(template, 'keywords')
                assert hasattr(template, 'tone')

    @pytest.mark.asyncio
    async def test_process_review_data_google(self, agent):
        """Test processing Google review data"""
        google_data = {
            "text": "Great service!",
            "author_name": "Test User",
            "rating": 5,
            "time": int(datetime.now().timestamp()),
            "review_id": "google_test_1"
        }

        review = await agent._process_review_data(ReviewPlatform.GOOGLE, google_data)

        assert isinstance(review, Review)
        assert review.platform == ReviewPlatform.GOOGLE
        assert review.content == "Great service!"
        assert review.author == "Test User"
        assert review.rating == 5.0
        assert review.id == "google_test_1"

    @pytest.mark.asyncio
    async def test_process_review_data_yelp(self, agent):
        """Test processing Yelp review data"""
        yelp_data = {
            "text": "Good food",
            "user": {"name": "Yelp User"},
            "rating": 4,
            "time_created": datetime.now().isoformat(),
            "id": "yelp_test_1"
        }

        review = await agent._process_review_data(ReviewPlatform.YELP, yelp_data)

        assert isinstance(review, Review)
        assert review.platform == ReviewPlatform.YELP
        assert review.content == "Good food"
        assert review.author == "Yelp User"
        assert review.rating == 4.0
        assert review.id == "yelp_test_1"

    @pytest.mark.asyncio
    async def test_process_review_data_tripadvisor(self, agent):
        """Test processing TripAdvisor review data"""
        tripadvisor_data = {
            "text": "Nice hotel",
            "username": "TripAdvisor User",
            "rating": 4,
            "published_date": datetime.now().isoformat(),
            "id": "tripadvisor_test_1",
            "title": "Good Stay"
        }

        review = await agent._process_review_data(ReviewPlatform.TRIPADVISOR, tripadvisor_data)

        assert isinstance(review, Review)
        assert review.platform == ReviewPlatform.TRIPADVISOR
        assert review.content == "Nice hotel"
        assert review.author == "TripAdvisor User"
        assert review.rating == 4.0
        assert review.id == "tripadvisor_test_1"
        assert review.title == "Good Stay"

    def test_priority_score_calculation(self, agent, sample_reviews):
        """Test that priority scores are calculated and assigned"""
        prioritized = asyncio.run(agent.prioritize_responses(sample_reviews))

        for review in prioritized:
            assert hasattr(review, 'priority_score')
            assert isinstance(review.priority_score, (int, float))
            assert review.priority_score >= 0

        # Critical urgency should have highest priority score
        critical_reviews = [r for r in prioritized if r.urgency == UrgencyLevel.CRITICAL]
        low_reviews = [r for r in prioritized if r.urgency == UrgencyLevel.LOW]

        if critical_reviews and low_reviews:
            assert critical_reviews[0].priority_score > low_reviews[0].priority_score


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete workflow integration"""
    async with ReviewResponseAgent() as agent:
        # Mock business setup
        business_ids = {
            ReviewPlatform.GOOGLE: "test_place"
        }

        business_info = {
            "name": "Test Restaurant",
            "phone": "(555) 123-4567",
            "email": "manager@test.com"
        }

        # This would normally fetch real reviews, but uses mock data
        reviews = await agent.monitor_reviews(business_ids)

        # Should return some reviews (mocked)
        assert isinstance(reviews, list)

        if reviews:
            # Test prioritization
            prioritized = await agent.prioritize_responses(reviews)
            assert len(prioritized) == len(reviews)

            # Test response generation for first review
            if prioritized:
                response = await agent.generate_response(prioritized[0], business_info)
                assert isinstance(response, str)
                assert len(response) > 0

            # Test insights generation
            insights = await agent.get_reputation_insights(reviews)
            assert isinstance(insights, dict)
            assert "total_reviews" in insights


if __name__ == "__main__":
    pytest.main([__file__, "-v"])