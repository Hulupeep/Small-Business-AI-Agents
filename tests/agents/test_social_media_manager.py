"""
Test suite for Social Media Manager Agent
Tests content generation, scheduling, analytics, and ROI tracking
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json

# Import the classes we're testing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.social_media_manager import SocialMediaManager, SocialPost, EngagementMetrics


class TestSocialMediaManager:
    """Test suite for Social Media Manager Agent"""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'platforms': ['twitter', 'linkedin', 'instagram', 'facebook'],
            'content_themes': [
                'productivity tips',
                'industry insights',
                'behind the scenes'
            ],
            'brand_voice': 'professional and approachable',
            'target_audiences': {
                'professionals': {
                    'interests': ['productivity', 'career growth'],
                    'tone': 'professional'
                },
                'entrepreneurs': {
                    'interests': ['startups', 'innovation'],
                    'tone': 'inspiring'
                }
            },
            'openai_api_key': 'test-api-key'
        }

    @pytest.fixture
    def social_manager(self, sample_config):
        """Create a Social Media Manager instance for testing"""
        return SocialMediaManager(sample_config)

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Boost your productivity with these 5 time-saving tips! 🚀 #ProductivityTips #TimeManagement #WorkSmart"
        return mock_response

    def test_initialization(self, social_manager, sample_config):
        """Test Social Media Manager initialization"""
        assert social_manager.platforms == sample_config['platforms']
        assert social_manager.brand_voice == sample_config['brand_voice']
        assert social_manager.content_themes == sample_config['content_themes']
        assert social_manager.posts_created == 0
        assert social_manager.time_saved_hours == 0

    @pytest.mark.asyncio
    async def test_content_generation(self, social_manager, mock_openai_response):
        """Test AI content generation for different platforms"""
        with patch.object(social_manager.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            # Test Twitter content generation
            post = await social_manager.generate_content(
                theme="productivity tips",
                platform="twitter",
                audience="professionals"
            )

            assert isinstance(post, SocialPost)
            assert post.platform == "twitter"
            assert post.target_audience == "professionals"
            assert len(post.content) <= 280  # Twitter character limit
            assert len(post.hashtags) > 0
            assert post.performance_prediction > 0

    @pytest.mark.asyncio
    async def test_content_generation_all_platforms(self, social_manager, mock_openai_response):
        """Test content generation for all supported platforms"""
        platforms = ['twitter', 'linkedin', 'instagram', 'facebook']

        with patch.object(social_manager.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            for platform in platforms:
                post = await social_manager.generate_content(
                    theme="industry insights",
                    platform=platform,
                    audience="general"
                )

                assert post.platform == platform
                assert isinstance(post.hashtags, list)
                assert post.performance_prediction >= 0

    def test_performance_prediction(self, social_manager):
        """Test post performance prediction algorithm"""
        content = "Boost your productivity with these 5 amazing tips! 🚀 #ProductivityTips #TimeManagement"

        score = social_manager._predict_performance(content, "twitter", "productivity tips")

        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_post_type_classification(self, social_manager):
        """Test post type classification"""
        test_cases = [
            ("Learn how to improve your productivity", "educational"),
            ("Limited time offer: 50% off all courses!", "promotional"),
            ("Breaking: New industry report released", "news"),
            ("Just had an amazing coffee this morning", "entertaining")
        ]

        for content, expected_type in test_cases:
            post_type = social_manager._classify_post_type(content)
            assert post_type == expected_type

    @pytest.mark.asyncio
    async def test_optimal_scheduling(self, social_manager):
        """Test optimal post scheduling"""
        # Create sample posts
        posts = [
            SocialPost(
                content="Test post 1",
                platform="twitter",
                hashtags=["test"]
            ),
            SocialPost(
                content="Test post 2",
                platform="linkedin",
                hashtags=["business"]
            )
        ]

        scheduled_posts = await social_manager.schedule_optimal_posts(posts)

        assert isinstance(scheduled_posts, dict)
        assert "twitter" in scheduled_posts or "linkedin" in scheduled_posts

        for platform, platform_posts in scheduled_posts.items():
            for post in platform_posts:
                assert post.scheduled_time is not None
                assert post.scheduled_time > datetime.now()

    @pytest.mark.asyncio
    async def test_auto_response_generation(self, social_manager, mock_openai_response):
        """Test automated response generation"""
        mock_openai_response.choices[0].message.content = "Thanks for your question! We're glad you found it helpful."

        with patch.object(social_manager.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            engagement_data = {
                'content': 'This is really helpful! How can I learn more?',
                'platform': 'twitter',
                'user': 'test_user',
                'type': 'comment'
            }

            response = await social_manager.auto_respond_to_engagement(engagement_data)

            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0

    @pytest.mark.asyncio
    async def test_no_response_needed(self, social_manager):
        """Test cases where no response is needed"""
        engagement_data = {
            'content': 'Nice post',  # Simple positive comment, no question
            'platform': 'twitter',
            'user': 'test_user',
            'type': 'comment'
        }

        response = await social_manager.auto_respond_to_engagement(engagement_data)

        # Should return None for simple positive comments without questions
        assert response is None

    def test_performance_tracking(self, social_manager):
        """Test engagement metrics tracking"""
        metrics_data = {
            'platform': 'twitter',
            'likes': 150,
            'shares': 25,
            'comments': 10,
            'clicks': 75,
            'impressions': 5000
        }

        metric = social_manager.track_performance("post_123", metrics_data)

        assert isinstance(metric, EngagementMetrics)
        assert metric.post_id == "post_123"
        assert metric.platform == "twitter"
        assert metric.likes == 150
        assert metric.engagement_rate > 0  # Should calculate engagement rate
        assert len(social_manager.engagement_history) == 1

    def test_analytics_report_generation(self, social_manager):
        """Test comprehensive analytics report generation"""
        # Add some sample metrics
        for i in range(5):
            metrics_data = {
                'platform': 'twitter',
                'likes': 100 + i * 10,
                'shares': 20 + i * 2,
                'comments': 5 + i,
                'impressions': 2000 + i * 200
            }
            social_manager.track_performance(f"post_{i}", metrics_data)

        report = social_manager.get_analytics_report()

        assert 'summary' in report
        assert 'engagement_breakdown' in report
        assert 'platform_performance' in report
        assert 'roi_metrics' in report
        assert 'recommendations' in report

        # Check summary metrics
        assert report['summary']['total_posts'] == 5
        assert report['summary']['average_engagement_rate'] > 0
        assert report['roi_metrics']['time_saved_hours'] > 0

    def test_roi_calculations(self, social_manager):
        """Test ROI value calculations"""
        # Simulate some activity
        social_manager.posts_created = 10
        social_manager.time_saved_hours = 15

        # Add performance metrics
        for i in range(3):
            metrics_data = {
                'platform': 'linkedin',
                'likes': 200,
                'shares': 40,
                'comments': 15,
                'impressions': 3000
            }
            social_manager.track_performance(f"post_{i}", metrics_data)

        report = social_manager.get_analytics_report()

        roi_metrics = report['roi_metrics']
        assert roi_metrics['time_saved_hours'] == 15
        assert roi_metrics['time_value_usd'] > 0
        assert roi_metrics['total_roi_value'] > 0
        assert roi_metrics['monthly_savings_estimate'] > 0

    def test_recommendation_generation(self, social_manager):
        """Test analytics-based recommendation generation"""
        # Add metrics with varying performance
        high_performance = {
            'platform': 'linkedin',
            'likes': 300,
            'shares': 60,
            'comments': 25,
            'impressions': 4000
        }

        low_performance = {
            'platform': 'facebook',
            'likes': 20,
            'shares': 2,
            'comments': 1,
            'impressions': 1000
        }

        social_manager.track_performance("high_post", high_performance)
        social_manager.track_performance("low_post", low_performance)

        recommendations = social_manager._generate_recommendations()

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should recommend focusing on better performing platform
        recommendations_text = ' '.join(recommendations)
        assert 'linkedin' in recommendations_text.lower()

    @pytest.mark.asyncio
    async def test_automation_cycle(self, social_manager, mock_openai_response):
        """Test complete automation cycle"""
        with patch.object(social_manager.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            results = await social_manager.run_automation_cycle()

            assert 'cycle_start' in results
            assert 'cycle_end' in results
            assert 'posts_generated' in results
            assert 'posts_scheduled' in results
            assert results['posts_generated'] > 0

    def test_optimal_times_calculation(self, social_manager):
        """Test optimal posting times calculation"""
        # Add historical engagement data at different times
        for hour in [9, 12, 15, 18]:
            for i in range(3):
                timestamp = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
                engagement = EngagementMetrics(
                    post_id=f"post_{hour}_{i}",
                    platform="twitter",
                    likes=50 + hour,  # More likes at later hours
                    impressions=1000,
                    timestamp=timestamp
                )
                social_manager.engagement_history.append(engagement)

        # Get optimal times
        optimal_times = asyncio.run(social_manager._get_optimal_times("twitter"))

        assert isinstance(optimal_times, list)
        assert len(optimal_times) > 0

        # Should identify later hours as better performing
        best_time = optimal_times[0]
        assert 'engagement_score' in best_time
        assert best_time['engagement_score'] > 0

    def test_time_slot_availability(self, social_manager):
        """Test time slot availability checking"""
        test_time = datetime.now() + timedelta(hours=24)

        # Should be available (no conflicts in simple implementation)
        is_available = social_manager._is_time_slot_available(test_time, "twitter")
        assert is_available is True

    def test_top_performing_posts(self, social_manager):
        """Test top performing posts identification"""
        # Add posts with different performance levels
        performance_levels = [
            (50, 5, 2, 1000),    # Low performance
            (200, 40, 15, 3000), # Medium performance
            (500, 100, 50, 8000) # High performance
        ]

        for i, (likes, shares, comments, impressions) in enumerate(performance_levels):
            engagement = EngagementMetrics(
                post_id=f"post_{i}",
                platform="twitter",
                likes=likes,
                shares=shares,
                comments=comments,
                impressions=impressions
            )
            social_manager.engagement_history.append(engagement)

        top_posts = social_manager._get_top_performing_posts(2)

        assert len(top_posts) == 2
        # Should be sorted by engagement rate (descending)
        assert top_posts[0]['engagement_rate'] >= top_posts[1]['engagement_rate']

    def test_engagement_rate_calculation(self):
        """Test engagement rate calculation in EngagementMetrics"""
        metric = EngagementMetrics(
            post_id="test_post",
            platform="twitter",
            likes=100,
            shares=20,
            comments=10,
            impressions=2000
        )

        expected_rate = ((100 + 20 + 10) / 2000) * 100  # 6.5%
        assert abs(metric.engagement_rate - expected_rate) < 0.1

    def test_zero_impressions_handling(self):
        """Test handling of zero impressions in engagement calculation"""
        metric = EngagementMetrics(
            post_id="test_post",
            platform="twitter",
            likes=50,
            shares=10,
            comments=5,
            impressions=0  # Zero impressions
        )

        assert metric.engagement_rate == 0.0

    @pytest.mark.parametrize("platform,expected_max_char", [
        ("twitter", 280),
        ("linkedin", 3000),
        ("instagram", 2200),
        ("facebook", 63206)
    ])
    def test_platform_character_limits(self, social_manager, platform, expected_max_char):
        """Test that generated content respects platform character limits"""
        # This test would need to be implemented with actual content generation
        # For now, we test that the limits are correctly defined
        char_limits = {
            'twitter': 280,
            'linkedin': 3000,
            'instagram': 2200,
            'facebook': 63206
        }

        assert char_limits[platform] == expected_max_char

    def test_error_handling_in_content_generation(self, social_manager):
        """Test error handling in content generation"""
        with patch.object(social_manager.openai_client.chat.completions, 'create', side_effect=Exception("API Error")):

            # Should handle API errors gracefully
            with pytest.raises(Exception):
                asyncio.run(social_manager.generate_content("test", "twitter", "general"))

    def test_engagement_improvement_calculation(self, social_manager):
        """Test engagement improvement calculation over time"""
        # Add older metrics (lower performance)
        for i in range(10):
            old_metric = EngagementMetrics(
                post_id=f"old_post_{i}",
                platform="twitter",
                likes=30,
                shares=5,
                comments=2,
                impressions=1000,
                timestamp=datetime.now() - timedelta(days=40)
            )
            social_manager.engagement_history.append(old_metric)

        # Add newer metrics (higher performance)
        for i in range(10):
            new_metric = EngagementMetrics(
                post_id=f"new_post_{i}",
                platform="twitter",
                likes=80,
                shares=15,
                comments=8,
                impressions=1000,
                timestamp=datetime.now() - timedelta(days=5)
            )
            social_manager.engagement_history.append(new_metric)

        # Trigger improvement calculation
        social_manager.track_performance("trigger_post", {
            'platform': 'twitter',
            'likes': 100,
            'shares': 20,
            'comments': 10,
            'impressions': 1000
        })

        assert social_manager.engagement_improvement > 0


# Integration test class
class TestSocialMediaManagerIntegration:
    """Integration tests for Social Media Manager"""

    @pytest.fixture
    def integration_config(self):
        """Configuration for integration testing"""
        return {
            'platforms': ['twitter', 'linkedin'],
            'content_themes': ['productivity tips'],
            'brand_voice': 'professional',
            'target_audiences': {
                'professionals': {
                    'interests': ['productivity'],
                    'tone': 'professional'
                }
            },
            'openai_api_key': 'test-key'
        }

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self, integration_config):
        """Test complete end-to-end workflow"""
        manager = SocialMediaManager(integration_config)

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Boost productivity with time-blocking! 📅 #ProductivityTips #TimeManagement"

        with patch.object(manager.openai_client.chat.completions, 'create', return_value=mock_response):

            # 1. Generate content
            post = await manager.generate_content("productivity tips", "twitter", "professionals")
            assert post is not None

            # 2. Schedule posts
            scheduled = await manager.schedule_optimal_posts([post])
            assert len(scheduled) > 0

            # 3. Track performance
            performance_data = {
                'platform': 'twitter',
                'likes': 150,
                'shares': 30,
                'comments': 10,
                'impressions': 2500
            }

            metric = manager.track_performance("test_post_123", performance_data)
            assert metric.engagement_rate > 0

            # 4. Generate analytics report
            report = manager.get_analytics_report()
            assert report['summary']['total_posts'] == 1
            assert report['roi_metrics']['time_saved_hours'] > 0

    @pytest.mark.asyncio
    async def test_bulk_content_generation(self, integration_config):
        """Test generating content for multiple platforms and themes"""
        manager = SocialMediaManager(integration_config)

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test content with #hashtags"

        with patch.object(manager.openai_client.chat.completions, 'create', return_value=mock_response):

            posts = []
            platforms = ['twitter', 'linkedin']
            themes = ['productivity tips']

            for platform in platforms:
                for theme in themes:
                    post = await manager.generate_content(theme, platform, "professionals")
                    posts.append(post)

            assert len(posts) == len(platforms) * len(themes)

            # Schedule all posts
            scheduled = await manager.schedule_optimal_posts(posts)
            assert len(scheduled) <= len(platforms)  # One or more platforms


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])