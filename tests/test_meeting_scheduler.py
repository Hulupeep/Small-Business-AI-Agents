"""
Comprehensive tests for the Meeting Scheduler Agent.

Tests cover:
- Natural language processing for scheduling requests
- Calendar conflict detection and resolution
- Timezone handling
- Business impact calculations
- Integration with calendar systems
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
import pytz

from src.agents.meeting_scheduler import (
    MeetingSchedulerAgent, SchedulingSuggestion, ConflictInfo
)
from src.database.models import (
    DatabaseManager, Calendar, Meeting, SchedulingRequest,
    ConflictResolution, BusinessMetric, Base
)
from src.utils.nlp_processor import NLPProcessor, SchedulingIntent, ExtractedEntity

class TestMeetingSchedulerAgent:
    """Test suite for Meeting Scheduler Agent"""

    @pytest.fixture
    def db_manager(self):
        """Create test database"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return DatabaseManager("sqlite:///:memory:")

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'database_url': 'sqlite:///:memory:',
            'notifications': {
                'email_enabled': False,  # Disable for testing
                'smtp_host': 'test.smtp.com',
                'smtp_username': 'test@test.com',
                'smtp_password': 'password',
                'from_email': 'test@test.com'
            },
            'google_credentials': None,
            'outlook_credentials': None,
            'calendly_credentials': None
        }

    @pytest.fixture
    def agent(self, sample_config):
        """Create test agent instance"""
        with patch('src.agents.meeting_scheduler.NotificationManager'), \
             patch('src.agents.meeting_scheduler.GoogleCalendarAPI'), \
             patch('src.agents.meeting_scheduler.OutlookAPI'), \
             patch('src.agents.meeting_scheduler.CalendlyAPI'):
            return MeetingSchedulerAgent(sample_config)

    @pytest.fixture
    def sample_calendar_data(self, agent):
        """Create sample calendar and meeting data"""
        session = agent.db_manager.get_session()

        # Create calendar
        calendar = Calendar(
            name="Test Calendar",
            owner_email="test@example.com",
            calendar_id="test_calendar_123",
            provider="google",
            timezone="UTC",
            is_primary=True,
            is_active=True
        )
        session.add(calendar)
        session.flush()

        # Create existing meeting (for conflict testing)
        existing_meeting = Meeting(
            calendar_id=calendar.id,
            title="Existing Meeting",
            start_time=datetime.utcnow() + timedelta(days=1, hours=14),  # Tomorrow 2 PM
            end_time=datetime.utcnow() + timedelta(days=1, hours=15),    # Tomorrow 3 PM
            timezone="UTC",
            organizer_email="test@example.com",
            status="scheduled"
        )
        session.add(existing_meeting)

        session.commit()
        agent.db_manager.close_session(session)

        return {
            'calendar_id': calendar.id,
            'existing_meeting_id': existing_meeting.id
        }

    def test_natural_language_processing(self, agent):
        """Test natural language processing of scheduling requests"""
        test_requests = [
            "Schedule a meeting with john@example.com tomorrow at 2 PM",
            "Book a 1-hour discussion about project updates next Monday at 10 AM",
            "Arrange a call with the team on Friday afternoon",
            "Set up a meeting for budget review with mary@example.com next week"
        ]

        for request_text in test_requests:
            result = agent.process_natural_language_request(
                request_text, "requester@example.com"
            )

            assert 'request_id' in result
            assert 'parsed_intent' in result
            assert 'suggested_times' in result
            assert result['status'] in ['suggestions_ready', 'error']

            if result['status'] == 'suggestions_ready':
                intent = result['parsed_intent']
                assert hasattr(intent, 'action')
                assert hasattr(intent, 'title')
                assert hasattr(intent, 'duration_minutes')

    def test_conflict_detection(self, agent, sample_calendar_data):
        """Test calendar conflict detection"""
        session = agent.db_manager.get_session()

        # Test time that conflicts with existing meeting
        conflict_start = datetime.utcnow() + timedelta(days=1, hours=14, minutes=30)
        conflict_end = datetime.utcnow() + timedelta(days=1, hours=15, minutes=30)

        conflicts = agent._check_for_conflicts(
            conflict_start, conflict_end, ["test@example.com"], session
        )

        assert len(conflicts) > 0
        assert any(conflict.conflict_type == 'time_overlap' for conflict in conflicts)

        # Test time that doesn't conflict
        no_conflict_start = datetime.utcnow() + timedelta(days=1, hours=16)
        no_conflict_end = datetime.utcnow() + timedelta(days=1, hours=17)

        no_conflicts = agent._check_for_conflicts(
            no_conflict_start, no_conflict_end, ["test@example.com"], session
        )

        assert len(no_conflicts) == 0

        agent.db_manager.close_session(session)

    def test_optimal_time_finding(self, agent, sample_calendar_data):
        """Test optimal meeting time finding"""
        attendees = ["test@example.com", "attendee2@example.com"]
        duration = 60  # 1 hour
        start_range = datetime.utcnow() + timedelta(days=1)
        end_range = datetime.utcnow() + timedelta(days=7)

        suggestions = agent.find_optimal_meeting_time(
            attendees, duration, (start_range, end_range)
        )

        assert len(suggestions) > 0
        assert all(isinstance(s, SchedulingSuggestion) for s in suggestions)

        # Verify suggestions are sorted by confidence
        for i in range(1, len(suggestions)):
            assert suggestions[i-1].confidence_score >= suggestions[i].confidence_score

        # Verify meeting duration is respected
        for suggestion in suggestions:
            duration_minutes = (suggestion.end_time - suggestion.suggested_time).total_seconds() / 60
            assert abs(duration_minutes - duration) < 1  # Allow for small rounding differences

    def test_timezone_handling(self, agent):
        """Test timezone conversion functionality"""
        test_cases = [
            ("2023-12-25 14:00:00", "America/New_York", "UTC"),
            ("2023-06-15 09:30:00", "America/Los_Angeles", "America/New_York"),
            ("2023-03-10 16:45:00", "Europe/London", "Asia/Tokyo")
        ]

        for time_str, from_tz, to_tz in test_cases:
            result = agent.handle_timezone_conversion(time_str, from_tz, to_tz)

            assert 'original_time' in result
            assert 'converted_time' in result
            assert 'utc_time' in result
            assert result['original_timezone'] == from_tz
            assert result['converted_timezone'] == to_tz

    def test_meeting_scheduling_workflow(self, agent, sample_calendar_data):
        """Test complete meeting scheduling workflow"""
        # Step 1: Process natural language request
        request_text = "Schedule a team standup tomorrow at 10 AM with team@example.com"
        result = agent.process_natural_language_request(
            request_text, "organizer@example.com"
        )

        assert result['status'] == 'suggestions_ready'
        request_id = result['request_id']

        # Step 2: Schedule the meeting using first suggestion
        with patch.object(agent, '_create_external_meeting', return_value='external_123'):
            schedule_result = agent.schedule_meeting(request_id, 0)

            assert schedule_result['status'] == 'success'
            assert 'meeting_id' in schedule_result
            assert 'scheduled_time' in schedule_result

    def test_conflict_resolution(self, agent, sample_calendar_data):
        """Test automatic conflict resolution"""
        session = agent.db_manager.get_session()

        # Create a meeting that will have conflicts
        calendar = session.query(Calendar).first()
        conflicting_meeting = Meeting(
            calendar_id=calendar.id,
            title="Conflicting Meeting",
            start_time=datetime.utcnow() + timedelta(days=1, hours=14),  # Same time as existing
            end_time=datetime.utcnow() + timedelta(days=1, hours=15),
            timezone="UTC",
            organizer_email="organizer@example.com",
            attendee_emails='["test@example.com"]',
            status="scheduled"
        )
        session.add(conflicting_meeting)
        session.commit()

        # Test conflict resolution
        resolution_result = agent.resolve_scheduling_conflicts(conflicting_meeting.id)

        assert resolution_result['status'] in ['conflicts_resolved', 'no_conflicts', 'no_alternatives']

        if resolution_result['status'] == 'conflicts_resolved':
            assert 'suggested_alternative' in resolution_result
            assert 'confidence' in resolution_result

        agent.db_manager.close_session(session)

    def test_business_impact_calculation(self, agent):
        """Test business impact metrics calculation"""
        # Create sample business metrics
        session = agent.db_manager.get_session()

        metrics = [
            BusinessMetric(
                metric_type='time_saved',
                agent_type='meeting_scheduler',
                value=2.5,
                unit='hours',
                date_recorded=datetime.utcnow() - timedelta(days=5)
            ),
            BusinessMetric(
                metric_type='meeting_scheduled',
                agent_type='meeting_scheduler',
                value=1,
                unit='count',
                date_recorded=datetime.utcnow() - timedelta(days=3)
            ),
            BusinessMetric(
                metric_type='scheduling_request_processed',
                agent_type='meeting_scheduler',
                value=1,
                unit='count',
                date_recorded=datetime.utcnow() - timedelta(days=3)
            )
        ]

        for metric in metrics:
            session.add(metric)

        session.commit()

        # Calculate business impact
        impact = agent.calculate_business_impact()

        assert 'monthly_time_saved_hours' in impact
        assert 'weekly_time_saved_hours' in impact
        assert 'booking_success_rate_percentage' in impact
        assert 'annual_cost_savings' in impact
        assert 'roi_percentage' in impact

        assert impact['monthly_time_saved_hours'] >= 0
        assert impact['booking_success_rate_percentage'] >= 0

        agent.db_manager.close_session(session)

    def test_scheduling_optimization(self, agent, sample_calendar_data):
        """Test scheduling optimization features"""
        optimization_result = agent.run_scheduling_optimization()

        assert 'meetings_analyzed' in optimization_result
        assert 'conflicts_detected' in optimization_result
        assert 'optimizations_suggested' in optimization_result
        assert 'business_impact' in optimization_result

        assert optimization_result['meetings_analyzed'] >= 0
        assert optimization_result['conflicts_detected'] >= 0

    @patch('src.agents.meeting_scheduler.NotificationManager')
    def test_notification_integration(self, mock_notification_manager, agent, sample_calendar_data):
        """Test notification system integration"""
        # Mock the notification manager
        mock_notification = Mock()
        agent.notification_manager = mock_notification

        # Process a scheduling request which should trigger notifications
        request_text = "Schedule a meeting tomorrow"
        result = agent.process_natural_language_request(
            request_text, "test@example.com"
        )

        # If successful, schedule the meeting
        if result['status'] == 'suggestions_ready':
            with patch.object(agent, '_create_external_meeting', return_value='external_123'):
                schedule_result = agent.schedule_meeting(result['request_id'], 0)

                if schedule_result['status'] == 'success':
                    # Verify notifications were sent
                    assert mock_notification.send_email.called or \
                           mock_notification.send_notification.called

    def test_edge_cases_and_error_handling(self, agent):
        """Test edge cases and error handling"""
        # Test with malformed request
        result = agent.process_natural_language_request("", "test@example.com")
        assert 'status' in result

        # Test with non-existent request ID
        schedule_result = agent.schedule_meeting(99999, 0)
        assert schedule_result['status'] == 'error'

        # Test timezone conversion with invalid timezone
        tz_result = agent.handle_timezone_conversion(
            "2023-12-25 14:00:00", "Invalid/Timezone", "UTC"
        )
        assert 'status' in tz_result

    def test_multi_attendee_availability(self, agent, sample_calendar_data):
        """Test availability checking for multiple attendees"""
        attendees = ["attendee1@example.com", "attendee2@example.com", "attendee3@example.com"]
        duration = 60
        start_range = datetime.utcnow() + timedelta(days=1)
        end_range = datetime.utcnow() + timedelta(days=7)

        suggestions = agent.find_optimal_meeting_time(
            attendees, duration, (start_range, end_range)
        )

        # Should handle multiple attendees gracefully
        assert isinstance(suggestions, list)

        for suggestion in suggestions:
            assert hasattr(suggestion, 'all_attendees_available')
            assert hasattr(suggestion, 'confidence_score')

    def test_recurring_meeting_patterns(self, agent):
        """Test handling of recurring meeting patterns"""
        # This would test recurring meeting detection and scheduling
        # For now, test basic pattern recognition in NLP
        recurring_requests = [
            "Schedule weekly team meeting every Monday at 10 AM",
            "Book daily standup at 9 AM starting tomorrow",
            "Arrange monthly review meeting on first Friday of each month"
        ]

        for request in recurring_requests:
            result = agent.process_natural_language_request(
                request, "organizer@example.com"
            )

            # Should process without errors
            assert 'status' in result
            assert result['status'] in ['suggestions_ready', 'error']

class TestNLPProcessor:
    """Test suite for Natural Language Processing components"""

    @pytest.fixture
    def nlp_processor(self):
        """Create NLP processor instance"""
        return NLPProcessor()

    def test_intent_detection(self, nlp_processor):
        """Test scheduling intent detection"""
        test_cases = [
            ("Schedule a meeting tomorrow", "schedule"),
            ("Reschedule the team meeting to next week", "reschedule"),
            ("Cancel Friday's presentation", "cancel"),
            ("Find time for a quick call", "find_time"),
            ("Book a conference room for the project review", "schedule")
        ]

        for text, expected_intent in test_cases:
            intent = nlp_processor.process_scheduling_request(text)
            assert intent.action == expected_intent

    def test_entity_extraction(self, nlp_processor):
        """Test entity extraction from text"""
        test_text = "Schedule a meeting with john@example.com tomorrow at 2:30 PM for 1 hour in conference room A"

        intent = nlp_processor.process_scheduling_request(test_text)

        # Check for extracted entities
        entity_types = [entity.type for entity in intent.entities]

        # Should extract email, time, duration, and location
        assert 'person' in entity_types  # email
        # Note: Depending on implementation, other entities might be extracted

    def test_time_parsing(self, nlp_processor):
        """Test time parsing capabilities"""
        time_expressions = [
            "2:30 PM",
            "14:30",
            "2 PM",
            "afternoon",
            "morning",
            "noon"
        ]

        for time_expr in time_expressions:
            parsed_time = nlp_processor._parse_time(time_expr)
            if parsed_time:
                assert 'hour' in parsed_time
                assert 'minute' in parsed_time
                assert 0 <= parsed_time['hour'] <= 23
                assert 0 <= parsed_time['minute'] <= 59

    def test_date_parsing(self, nlp_processor):
        """Test date parsing capabilities"""
        date_expressions = [
            "tomorrow",
            "next Monday",
            "December 25",
            "12/25/2023",
            "next week"
        ]

        for date_expr in date_expressions:
            parsed_date = nlp_processor._parse_date(date_expr)
            # Should either parse successfully or return None gracefully
            if parsed_date:
                assert isinstance(parsed_date, datetime)

    def test_duration_extraction(self, nlp_processor):
        """Test duration extraction from text"""
        duration_expressions = [
            "1 hour",
            "30 minutes",
            "2 hrs",
            "45 mins",
            "1h 30m"
        ]

        for duration_expr in duration_expressions:
            duration_minutes = nlp_processor._parse_duration(duration_expr)
            if duration_minutes:
                assert duration_minutes > 0
                assert duration_minutes <= 480  # Max 8 hours

    def test_meeting_title_extraction(self, nlp_processor):
        """Test meeting title extraction"""
        test_cases = [
            ("Schedule a project review meeting", "project review"),
            ("Book a call about budget planning", "budget planning"),
            ("Arrange a team standup", "team standup"),
            ("Meeting with the client tomorrow", "client")
        ]

        for text, expected_keyword in test_cases:
            title = nlp_processor._extract_meeting_title(text, "schedule")
            assert isinstance(title, str)
            assert len(title) > 0
            # Title should contain relevant keywords (case-insensitive)
            assert expected_keyword.lower() in title.lower() or title == "Meeting"

    def test_ambiguous_time_resolution(self, nlp_processor):
        """Test resolution of ambiguous time references"""
        # Create sample entities for testing
        date_entity = ExtractedEntity(
            type='date',
            value=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
            confidence=0.9,
            start_pos=0,
            end_pos=8,
            original_text="tomorrow"
        )

        time_entity = ExtractedEntity(
            type='time',
            value={'hour': 14, 'minute': 30},
            confidence=0.8,
            start_pos=9,
            end_pos=17,
            original_text="2:30 PM"
        )

        entities = [date_entity, time_entity]
        resolved_times = nlp_processor.resolve_ambiguous_times(entities)

        assert len(resolved_times) > 0
        assert all(isinstance(time, datetime) for time in resolved_times)

    def test_complex_scheduling_requests(self, nlp_processor):
        """Test complex, multi-part scheduling requests"""
        complex_requests = [
            "Schedule a 90-minute quarterly business review with the executive team next Thursday at 2 PM in the main conference room",
            "Book a follow-up call with john@example.com and mary@example.com tomorrow morning to discuss the project timeline",
            "Arrange a team lunch meeting for next Friday at noon, preferably at the office cafeteria"
        ]

        for request in complex_requests:
            intent = nlp_processor.process_scheduling_request(request)

            assert intent.action in ['schedule', 'reschedule', 'cancel', 'find_time']
            assert isinstance(intent.entities, list)
            assert intent.confidence > 0
            assert len(intent.meeting_title) > 0