"""
Test suite for Email Campaign Writer Agent
Tests campaign creation, personalization, A/B testing, and performance tracking
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

from src.agents.email_campaign_writer import (
    EmailCampaignWriter,
    Customer,
    EmailCampaign,
    CampaignPerformance,
    CampaignType,
    SegmentCriteria
)


class TestEmailCampaignWriter:
    """Test suite for Email Campaign Writer Agent"""

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'openai_api_key': 'test-api-key',
            'personalization_rules': {
                'welcome_campaigns': {
                    'include_company_name': True,
                    'mention_signup_source': True
                }
            },
            'ab_testing': {
                'enabled': True,
                'split_ratio': 0.5,
                'winner_threshold': 0.05
            }
        }

    @pytest.fixture
    def email_writer(self, sample_config):
        """Create an Email Campaign Writer instance for testing"""
        return EmailCampaignWriter(sample_config)

    @pytest.fixture
    def sample_customer(self):
        """Sample customer for testing"""
        return Customer(
            id='cust_001',
            email='john@example.com',
            name='John Smith',
            purchase_history=[
                {
                    'date': datetime.now() - timedelta(days=30),
                    'amount': 299.99,
                    'category': 'software'
                }
            ],
            engagement_score=75.0,
            last_open=datetime.now() - timedelta(days=5),
            demographics={'company': 'Tech Corp', 'industry': 'technology'},
            lifecycle_stage='active'
        )

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Welcome to our platform, {first_name}!"
        return mock_response

    def test_initialization(self, email_writer, sample_config):
        """Test Email Campaign Writer initialization"""
        assert email_writer.config == sample_config
        assert len(email_writer.customers) == 0
        assert len(email_writer.campaigns) == 0
        assert email_writer.total_revenue_generated == 0.0
        assert email_writer.ab_test_config['enabled'] == True

    def test_customer_addition_and_segmentation(self, email_writer, sample_customer):
        """Test adding customers and automatic segmentation"""
        customer = email_writer.add_customer({
            'id': sample_customer.id,
            'email': sample_customer.email,
            'name': sample_customer.name,
            'purchase_history': sample_customer.purchase_history,
            'engagement_score': sample_customer.engagement_score,
            'last_open': sample_customer.last_open,
            'demographics': sample_customer.demographics,
            'lifecycle_stage': sample_customer.lifecycle_stage
        })

        assert customer.id in email_writer.customers

        # Check automatic segmentation
        assert 'medium_engagement' in email_writer.segments  # 75% engagement
        assert 'medium_value' in email_writer.segments       # $299.99 spent
        assert 'active' in email_writer.segments             # lifecycle stage
        assert customer.id in email_writer.segments['medium_engagement']

    @pytest.mark.asyncio
    async def test_campaign_creation(self, email_writer, mock_openai_response):
        """Test email campaign creation"""
        with patch.object(email_writer.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            campaign = await email_writer.create_campaign(
                campaign_name="Welcome Series",
                campaign_type=CampaignType.WELCOME,
                target_segments=['new'],
                send_time=datetime.now() + timedelta(hours=24)
            )

            assert isinstance(campaign, EmailCampaign)
            assert campaign.name == "Welcome Series"
            assert campaign.campaign_type == CampaignType.WELCOME
            assert len(campaign.subject_lines) >= 1
            assert len(campaign.content_variants) >= 1
            assert campaign.expected_open_rate > 0
            assert campaign.expected_ctr > 0

    @pytest.mark.asyncio
    async def test_subject_line_generation(self, email_writer, mock_openai_response):
        """Test subject line generation for different campaign types"""
        mock_openai_response.choices[0].message.content = "Welcome aboard!\nGet started today\nYour journey begins"

        with patch.object(email_writer.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            subject_lines = await email_writer._generate_subject_lines(
                CampaignType.WELCOME,
                ['new']
            )

            assert isinstance(subject_lines, list)
            assert len(subject_lines) == 3
            for subject in subject_lines:
                assert len(subject) <= 50  # Mobile optimization
                assert isinstance(subject, str)

    @pytest.mark.asyncio
    async def test_content_variant_generation(self, email_writer, mock_openai_response):
        """Test email content variant generation"""
        mock_openai_response.choices[0].message.content = "<h2>Welcome!</h2><p>Hello {first_name},</p><p>Welcome to our platform.</p>"

        with patch.object(email_writer.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            content_variants = await email_writer._generate_content_variants(
                CampaignType.WELCOME,
                ['new'],
                "Welcome to our platform!"
            )

            assert isinstance(content_variants, list)
            assert len(content_variants) == 2  # Direct and storytelling approaches
            for content in content_variants:
                assert '{first_name}' in content  # Should include personalization

    def test_segment_analysis(self, email_writer, sample_customer):
        """Test customer segment analysis"""
        # Add customers to segments
        email_writer.add_customer({
            'id': 'cust_001',
            'email': 'john@example.com',
            'name': 'John Smith',
            'purchase_history': [{'amount': 500}],
            'engagement_score': 80.0,
            'last_open': datetime.now() - timedelta(days=2),
            'lifecycle_stage': 'active'
        })

        analysis = email_writer._analyze_segments(['high_engagement', 'medium_value'])

        assert isinstance(analysis, str)
        assert 'customers' in analysis
        assert 'engagement' in analysis

    @pytest.mark.asyncio
    async def test_content_personalization(self, email_writer, sample_customer):
        """Test email content personalization"""
        # Add customer to writer
        email_writer.customers[sample_customer.id] = sample_customer

        content_template = """
        <h2>Hello {first_name},</h2>
        <p>Welcome to {company}!</p>
        <p>Your last purchase was in {favorite_category}.</p>
        <p>Total spent: {total_spent}</p>
        """

        campaign = EmailCampaign(
            id='camp_001',
            name='Test Campaign',
            campaign_type=CampaignType.WELCOME,
            subject_lines=['Welcome!'],
            content_variants=[content_template],
            target_segments=['active'],
            send_time=datetime.now(),
            personalization_fields=['first_name', 'company', 'favorite_category', 'total_spent']
        )

        personalized_content = await email_writer.personalize_content(
            sample_customer,
            content_template,
            campaign
        )

        assert 'John' in personalized_content  # First name
        assert '{first_name}' not in personalized_content  # Should be replaced
        assert '$299.99' in personalized_content  # Total spent

    def test_ab_test_setup(self, email_writer, sample_customer):
        """Test A/B test setup"""
        # Add customers
        for i in range(50):
            customer = Customer(
                id=f'cust_{i:03d}',
                email=f'user{i}@example.com',
                name=f'User {i}',
                purchase_history=[],
                engagement_score=50.0,
                lifecycle_stage='new'
            )
            email_writer.customers[customer.id] = customer

            # Add to new segment
            if 'new' not in email_writer.segments:
                email_writer.segments['new'] = []
            email_writer.segments['new'].append(customer.id)

        # Create campaign
        campaign = EmailCampaign(
            id='camp_test',
            name='A/B Test Campaign',
            campaign_type=CampaignType.WELCOME,
            subject_lines=['Subject A', 'Subject B'],
            content_variants=['Content A', 'Content B'],
            target_segments=['new'],
            send_time=datetime.now()
        )

        ab_config = email_writer.setup_ab_test(campaign)

        assert ab_config['enabled'] == True
        assert 'test_groups' in ab_config
        assert 'variant_a' in ab_config['test_groups']
        assert 'variant_b' in ab_config['test_groups']

        total_customers = len(ab_config['test_groups']['variant_a']['customers']) + \
                         len(ab_config['test_groups']['variant_b']['customers'])
        assert total_customers == 50

    def test_ab_test_insufficient_audience(self, email_writer):
        """Test A/B test with insufficient audience size"""
        # Create campaign with small audience
        campaign = EmailCampaign(
            id='camp_small',
            name='Small Campaign',
            campaign_type=CampaignType.WELCOME,
            subject_lines=['Subject A'],
            content_variants=['Content A'],
            target_segments=['nonexistent'],
            send_time=datetime.now()
        )

        ab_config = email_writer.setup_ab_test(campaign)

        assert ab_config['enabled'] == False
        assert 'reason' in ab_config

    def test_performance_tracking(self, email_writer):
        """Test campaign performance tracking"""
        performance_data = {
            'sent': 1000,
            'delivered': 980,
            'opened': 245,
            'clicked': 49,
            'converted': 12,
            'revenue_generated': 1800.0
        }

        performance = email_writer.track_campaign_performance(
            'camp_001',
            'variant_a',
            performance_data
        )

        assert isinstance(performance, CampaignPerformance)
        assert performance.campaign_id == 'camp_001'
        assert performance.open_rate == 25.0  # 245/980 * 100
        assert performance.click_through_rate == 5.0  # 49/980 * 100
        assert performance.conversion_rate > 0
        assert performance.revenue_per_email > 0

    def test_ab_test_analysis(self, email_writer):
        """Test A/B test results analysis"""
        # Add performance data for both variants
        variant_a_performance = CampaignPerformance(
            campaign_id='camp_001',
            variant_id='variant_a',
            sent=500,
            delivered=490,
            opened=122,  # 24.9% open rate
            clicked=24,  # 4.9% CTR
            converted=6,
            revenue_generated=900.0
        )

        variant_b_performance = CampaignPerformance(
            campaign_id='camp_001',
            variant_id='variant_b',
            sent=500,
            delivered=495,
            opened=148,  # 29.9% open rate
            clicked=35,  # 7.1% CTR
            converted=9,
            revenue_generated=1350.0
        )

        email_writer.performance_history.extend([variant_a_performance, variant_b_performance])

        analysis = email_writer.analyze_ab_test_results('camp_001')

        assert analysis['status'] == 'completed'
        assert 'variant_a' in analysis
        assert 'variant_b' in analysis
        assert analysis['comparison']['open_rate']['winner'] == 'variant_b'
        assert analysis['overall_winner'] == 'variant_b'

    def test_performance_prediction(self, email_writer):
        """Test campaign performance prediction"""
        # Add historical performance data
        for i in range(5):
            performance = CampaignPerformance(
                campaign_id=f'hist_{i}',
                variant_id='main',
                sent=1000,
                delivered=980,
                opened=200 + i * 10,  # Varying open rates
                clicked=40 + i * 5,   # Varying CTRs
                revenue_generated=500 + i * 100
            )
            email_writer.performance_history.append(performance)

        open_rate, ctr = email_writer._predict_campaign_performance(
            CampaignType.PROMOTIONAL,
            ['high_engagement'],
            ['Flash Sale: 50% Off!'],
            ['Limited time offer content']
        )

        assert 0 <= open_rate <= 100
        assert 0 <= ctr <= 100
        assert isinstance(open_rate, float)
        assert isinstance(ctr, float)

    def test_analytics_dashboard_generation(self, email_writer):
        """Test comprehensive analytics dashboard generation"""
        # Add sample performance data
        for i in range(10):
            performance = CampaignPerformance(
                campaign_id=f'camp_{i:03d}',
                variant_id='main',
                sent=1000,
                delivered=980,
                opened=196 + i * 5,  # 20-25% open rate
                clicked=39 + i * 2,   # 4-6% CTR
                converted=8 + i,      # 8-17 conversions
                revenue_generated=400 + i * 50  # $400-850 revenue
            )
            email_writer.performance_history.append(performance)

        dashboard = email_writer.get_analytics_dashboard()

        assert 'overview' in dashboard
        assert 'performance_improvements' in dashboard
        assert 'roi_metrics' in dashboard
        assert 'recommendations' in dashboard

        # Check overview metrics
        overview = dashboard['overview']
        assert overview['total_campaigns'] == 10
        assert overview['average_open_rate'] > 0
        assert overview['total_revenue_generated'] > 0

        # Check ROI metrics
        roi_metrics = dashboard['roi_metrics']
        assert roi_metrics['total_roi_value'] > 0
        assert roi_metrics['monthly_roi_estimate'] > 0

    def test_customer_segmentation_criteria(self, email_writer):
        """Test different customer segmentation criteria"""
        # High-value customer
        high_value_customer = Customer(
            id='high_val',
            email='highvalue@example.com',
            name='High Value',
            purchase_history=[
                {'amount': 1200, 'category': 'premium'},
                {'amount': 800, 'category': 'premium'}
            ],
            engagement_score=90.0,
            lifecycle_stage='champion'
        )

        # Low-engagement customer
        low_engagement_customer = Customer(
            id='low_eng',
            email='loweng@example.com',
            name='Low Engagement',
            purchase_history=[{'amount': 50}],
            engagement_score=25.0,
            lifecycle_stage='at_risk'
        )

        # Add customers
        email_writer.customers[high_value_customer.id] = high_value_customer
        email_writer.customers[low_engagement_customer.id] = low_engagement_customer

        # Test segmentation
        high_segments = email_writer._auto_segment_customer(high_value_customer)
        low_segments = email_writer._auto_segment_customer(low_engagement_customer)

        assert 'high_engagement' in high_segments
        assert 'high_value' in high_segments
        assert 'champion' in high_segments

        assert 'low_engagement' in low_segments
        assert 'low_value' in low_segments
        assert 'at_risk' in low_segments

    def test_campaign_automation_cycle(self, email_writer, mock_openai_response):
        """Test automated campaign creation cycle"""
        # Add customers for different segments
        customers_data = [
            {'id': 'new_1', 'lifecycle_stage': 'new', 'engagement_score': 50},
            {'id': 'dormant_1', 'lifecycle_stage': 'dormant', 'engagement_score': 20},
            {'id': 'high_val_1', 'purchase_history': [{'amount': 1500}], 'engagement_score': 80}
        ]

        for customer_data in customers_data:
            customer = Customer(
                id=customer_data['id'],
                email=f"{customer_data['id']}@example.com",
                name=customer_data['id'].title(),
                purchase_history=customer_data.get('purchase_history', []),
                engagement_score=customer_data['engagement_score'],
                lifecycle_stage=customer_data.get('lifecycle_stage', 'active')
            )
            email_writer.customers[customer.id] = customer
            email_writer._auto_segment_customer(customer)

        with patch.object(email_writer.openai_client.chat.completions, 'create', return_value=mock_openai_response):

            results = asyncio.run(email_writer.run_campaign_automation())

            assert 'automation_start' in results
            assert 'automation_end' in results
            assert results['campaigns_created'] > 0
            assert results['emails_personalized'] >= 0

    def test_error_handling_in_campaign_creation(self, email_writer):
        """Test error handling in campaign creation"""
        with patch.object(email_writer.openai_client.chat.completions, 'create', side_effect=Exception("API Error")):

            with pytest.raises(Exception):
                asyncio.run(email_writer.create_campaign(
                    "Test Campaign",
                    CampaignType.WELCOME,
                    ['new']
                ))

    def test_personalization_field_detection(self, email_writer):
        """Test automatic detection of available personalization fields"""
        # Add customer with various data fields
        customer = Customer(
            id='rich_data',
            email='rich@example.com',
            name='Rich Data',
            purchase_history=[
                {'amount': 299, 'category': 'software', 'date': datetime.now()}
            ],
            engagement_score=75.0,
            demographics={'company': 'TechCorp', 'industry': 'technology', 'location': 'SF'},
            preferences={'newsletter': True, 'marketing': False}
        )

        email_writer.customers[customer.id] = customer
        email_writer._auto_segment_customer(customer)

        fields = email_writer._get_personalization_fields(['medium_engagement'])

        assert 'first_name' in fields
        assert 'email' in fields
        assert 'company' in fields
        assert 'industry' in fields
        assert 'last_purchase_date' in fields
        assert 'pref_newsletter' in fields

    def test_revenue_per_email_calculation(self):
        """Test revenue per email calculation in performance metrics"""
        performance = CampaignPerformance(
            campaign_id='test',
            variant_id='main',
            sent=1000,
            delivered=980,
            revenue_generated=1960.0  # $2 per delivered email
        )

        assert performance.revenue_per_email == 2.0

    def test_conversion_rate_calculation(self):
        """Test conversion rate calculation in performance metrics"""
        performance = CampaignPerformance(
            campaign_id='test',
            variant_id='main',
            clicked=100,
            converted=25  # 25% of clickers converted
        )

        assert performance.conversion_rate == 25.0

    def test_zero_clicks_conversion_handling(self):
        """Test handling of zero clicks in conversion rate calculation"""
        performance = CampaignPerformance(
            campaign_id='test',
            variant_id='main',
            clicked=0,
            converted=0
        )

        assert performance.conversion_rate == 0.0

    @pytest.mark.parametrize("campaign_type,expected_baseline", [
        (CampaignType.WELCOME, 25.0),
        (CampaignType.PROMOTIONAL, 18.0),
        (CampaignType.NEWSLETTER, 22.0),
        (CampaignType.ABANDONED_CART, 45.0),
        (CampaignType.RE_ENGAGEMENT, 15.0)
    ])
    def test_campaign_type_performance_baselines(self, email_writer, campaign_type, expected_baseline):
        """Test that different campaign types have appropriate performance baselines"""
        open_rate, ctr = email_writer._predict_campaign_performance(
            campaign_type, ['general'], ['Test Subject'], ['Test Content']
        )

        # Should be close to expected baseline (within reasonable range)
        assert abs(open_rate - expected_baseline) < 10.0

    def test_recommendation_generation(self, email_writer):
        """Test analytics-based recommendation generation"""
        # Add performance data with mixed results
        good_performance = CampaignPerformance(
            campaign_id='good',
            variant_id='main',
            sent=1000,
            delivered=980,
            opened=294,  # 30% open rate
            clicked=59,  # 6% CTR
            converted=15  # 25% conversion rate
        )

        poor_performance = CampaignPerformance(
            campaign_id='poor',
            variant_id='main',
            sent=1000,
            delivered=980,
            opened=98,   # 10% open rate
            clicked=10,  # 1% CTR
            converted=1   # 10% conversion rate
        )

        email_writer.performance_history.extend([good_performance, poor_performance])

        dashboard = email_writer.get_analytics_dashboard()
        recommendations = dashboard['recommendations']

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should contain actionable recommendations
        recommendations_text = ' '.join(recommendations)
        assert any(keyword in recommendations_text.lower() for keyword in
                  ['subject', 'personalization', 'segment', 'test', 'improve'])


# Integration test class
class TestEmailCampaignWriterIntegration:
    """Integration tests for Email Campaign Writer"""

    @pytest.fixture
    def integration_config(self):
        """Configuration for integration testing"""
        return {
            'openai_api_key': 'test-key',
            'ab_testing': {'enabled': True, 'split_ratio': 0.5}
        }

    @pytest.mark.asyncio
    async def test_complete_email_workflow(self, integration_config):
        """Test complete email marketing workflow"""
        writer = EmailCampaignWriter(integration_config)

        # 1. Add customers
        customers = [
            {
                'id': 'cust_001',
                'email': 'john@example.com',
                'name': 'John Smith',
                'purchase_history': [{'amount': 299.99}],
                'engagement_score': 75.0,
                'lifecycle_stage': 'active'
            },
            {
                'id': 'cust_002',
                'email': 'jane@example.com',
                'name': 'Jane Doe',
                'purchase_history': [],
                'engagement_score': 90.0,
                'lifecycle_stage': 'new'
            }
        ]

        for customer_data in customers:
            writer.add_customer(customer_data)

        # 2. Create campaign
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Welcome {first_name}!"

        with patch.object(writer.openai_client.chat.completions, 'create', return_value=mock_response):

            campaign = await writer.create_campaign(
                "Welcome Campaign",
                CampaignType.WELCOME,
                ['new', 'active']
            )

            assert campaign is not None

            # 3. Setup A/B test
            ab_config = writer.setup_ab_test(campaign)

            # 4. Personalize content
            customer = writer.customers['cust_001']
            personalized = await writer.personalize_content(
                customer,
                campaign.content_variants[0],
                campaign
            )

            assert 'John' in personalized

            # 5. Track performance
            performance = writer.track_campaign_performance(
                campaign.id,
                'variant_a',
                {
                    'sent': 1000,
                    'delivered': 980,
                    'opened': 245,
                    'clicked': 49,
                    'converted': 12,
                    'revenue_generated': 1800.0
                }
            )

            assert performance.open_rate > 0

            # 6. Generate analytics
            dashboard = writer.get_analytics_dashboard()
            assert dashboard['overview']['total_campaigns'] == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])