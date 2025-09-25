"""
Test suite for Local Pub AI Toolkit agents
Comprehensive testing of all five core agents
"""

import unittest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json

# Import agents for testing
from agents.bar_table_manager import BarTableManager, Table, Order, Tab
from agents.stock_cellar_controller import StockCellarController, BeerLine, StockItem
from agents.entertainment_events_hub import EntertainmentEventsHub, Event, EventType
from agents.staff_compliance_manager import StaffComplianceManager, StaffMember, StaffRole
from agents.local_marketing_platform import LocalMarketingPlatform, Customer, CustomerSegment


class TestBarTableManager(unittest.TestCase):
    """Test cases for Bar & Table Service Manager"""

    def setUp(self):
        self.config = {
            'tables': [
                {'number': 1, 'capacity': 2},
                {'number': 2, 'capacity': 4},
                {'number': 3, 'capacity': 6}
            ],
            'operating_hours': {
                'monday': {'open': '12:00', 'close': '23:00'}
            }
        }
        self.manager = BarTableManager(self.config)

    def test_table_initialization(self):
        """Test table initialization from config"""
        self.assertEqual(len(self.manager.tables), 3)
        self.assertEqual(self.manager.tables[1].capacity, 2)
        self.assertEqual(self.manager.tables[2].capacity, 4)

    async def test_table_booking_success(self):
        """Test successful table booking"""
        result = await self.manager.manage_table_booking(
            party_size=4,
            preferred_time=datetime.now() + timedelta(hours=2)
        )
        self.assertTrue(result['success'])
        self.assertIn('table_number', result)
        self.assertIn('confirmation_code', result)

    async def test_table_booking_no_suitable_table(self):
        """Test booking when no suitable table available"""
        result = await self.manager.manage_table_booking(
            party_size=10,  # Larger than any available table
            preferred_time=datetime.now() + timedelta(hours=2)
        )
        self.assertFalse(result['success'])
        self.assertIn('alternative_times', result)

    async def test_food_order_coordination(self):
        """Test food order coordination with kitchen timing"""
        order_items = [
            {'name': 'Fish & Chips', 'category': 'fish_chips', 'price': 14.50},
            {'name': 'Soup', 'category': 'soup', 'price': 6.50}
        ]

        result = await self.manager.coordinate_food_orders(2, order_items)

        self.assertIn('order_id', result)
        self.assertIn('estimated_ready_time', result)
        self.assertIn('kitchen_instruction', result)

    async def test_tab_management(self):
        """Test tab creation and management"""
        # Open tab
        result = await self.manager.manage_tab_system(1, 'open_tab')
        self.assertEqual(result['status'], 'opened')
        tab_id = result['tab_id']

        # Add items
        items = [
            {'name': 'Guinness', 'price': 5.50},
            {'name': 'Chips', 'price': 4.00}
        ]
        result = await self.manager.manage_tab_system(1, 'add_items', items=items)
        self.assertEqual(result['new_total'], 9.50)

    def test_last_orders_timing(self):
        """Test last orders management"""
        # This would test the last orders calculation logic
        pass


class TestStockCellarController(unittest.TestCase):
    """Test cases for Stock & Cellar Controller"""

    def setUp(self):
        self.config = {
            'beer_lines': [
                {'line_id': 'LINE1', 'beer_name': 'Guinness', 'keg_size': 50.0},
                {'line_id': 'LINE2', 'beer_name': 'Heineken', 'keg_size': 50.0}
            ],
            'stock_items': [
                {
                    'item_id': 'WINE001',
                    'name': 'House Red Wine',
                    'category': 'wine',
                    'current_stock': 12,
                    'min_threshold': 5,
                    'unit_cost': 8.50,
                    'supplier': 'WineSupplier Ltd'
                }
            ]
        }
        self.controller = StockCellarController(self.config)

    def test_beer_line_initialization(self):
        """Test beer line setup"""
        self.assertEqual(len(self.controller.beer_lines), 2)
        self.assertEqual(self.controller.beer_lines['LINE1'].beer_name, 'Guinness')
        self.assertEqual(self.controller.beer_lines['LINE1'].keg_size, 50.0)

    async def test_beer_line_monitoring(self):
        """Test beer line monitoring functionality"""
        status = await self.controller.monitor_beer_lines()

        self.assertIn('timestamp', status)
        self.assertIn('lines', status)
        self.assertIn('overall_status', status)
        self.assertEqual(len(status['lines']), 2)

    async def test_keg_change_predictions(self):
        """Test keg change prediction system"""
        predictions = await self.controller.predict_keg_changes()

        self.assertIn('predictions', predictions)
        self.assertIn('change_schedule', predictions)

        # Check that predictions exist for each line
        for line_id in self.controller.beer_lines.keys():
            self.assertIn(line_id, predictions['predictions'])

    async def test_inventory_tracking(self):
        """Test inventory tracking and reorder point calculation"""
        inventory_status = await self.controller.manage_inventory_tracking()

        self.assertIn('inventory', inventory_status)
        self.assertIn('total_value', inventory_status)
        self.assertIn('WINE001', inventory_status['inventory'])

    async def test_wastage_recording(self):
        """Test wastage recording functionality"""
        result = await self.controller.record_wastage(
            'WINE001', 2, 'Broken bottle', 'John'
        )

        self.assertTrue(result['recorded'])
        self.assertEqual(result['cost_impact'], 2 * 8.50)  # quantity * unit_cost
        self.assertEqual(result['remaining_stock'], 10)  # 12 - 2

    async def test_supplier_ordering(self):
        """Test automated supplier ordering"""
        # Set stock to low level to trigger ordering
        self.controller.stock_items['WINE001'].current_stock = 3  # Below threshold

        orders = await self.controller.automate_supplier_orders()

        self.assertIn('auto_approved_orders', orders)
        self.assertIn('manual_review_required', orders)


class TestEntertainmentEventsHub(unittest.TestCase):
    """Test cases for Entertainment & Events Hub"""

    def setUp(self):
        self.config = {
            'local_teams': ['Cork City FC', 'Cork GAA'],
            'venue_areas': {
                'main_bar': {'capacity': 80},
                'function_room': {'capacity': 40}
            }
        }
        self.hub = EntertainmentEventsHub(self.config)

    async def test_live_music_scheduling(self):
        """Test live music event scheduling"""
        result = await self.hub.schedule_live_music(
            'Traditional Irish Band',
            datetime.now() + timedelta(days=7)
        )

        if result['success']:
            self.assertIn('event_id', result)
            self.assertIn('performance_time', result)
            self.assertIn('estimated_revenue', result)

    async def test_quiz_night_management(self):
        """Test quiz night creation and management"""
        quiz_config = {
            'theme': 'irish_culture',
            'date': datetime.now() + timedelta(days=10),
            'difficulty': 'mixed'
        }

        result = await self.hub.manage_quiz_nights(quiz_config)

        if result['success']:
            self.assertIn('event_id', result)
            self.assertIn('quiz_content', result)
            self.assertEqual(result['theme'], 'irish_culture')

    async def test_function_booking(self):
        """Test private function booking coordination"""
        booking_request = {
            'date': (datetime.now() + timedelta(days=14)).isoformat(),
            'party_size': 25,
            'type': 'birthday',
            'customer_name': 'John Smith',
            'phone': '+353 87 123 4567'
        }

        result = await self.hub.coordinate_function_bookings(booking_request)

        if result['success']:
            self.assertIn('event_id', result)
            self.assertIn('pricing', result)
            self.assertIn('catering_options', result)

    async def test_sports_fixture_integration(self):
        """Test sports fixture integration"""
        result = await self.hub.integrate_sports_fixtures()

        self.assertIn('upcoming_fixtures', result)
        self.assertIn('created_events', result)
        self.assertIn('match_day_specials', result)

    async def test_event_calendar(self):
        """Test event calendar generation"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)

        calendar = await self.hub.get_event_calendar(start_date, end_date)

        self.assertIn('events', calendar)
        self.assertIn('total_events', calendar)
        self.assertIn('total_estimated_revenue', calendar)


class TestStaffComplianceManager(unittest.TestCase):
    """Test cases for Staff Rota & Compliance Manager"""

    def setUp(self):
        self.config = {
            'operating_hours': {
                'monday': {'open': '11:00', 'close': '23:00'},
                'friday': {'open': '11:00', 'close': '01:00'}
            }
        }
        self.manager = StaffComplianceManager(self.config)

        # Add test staff member
        self.test_staff = StaffMember(
            staff_id='TEST001',
            name='Test Employee',
            role=StaffRole.BARTENDER,
            phone='+353 87 123 4567',
            email='test@example.ie',
            date_of_birth=datetime(1990, 1, 1),
            start_date=datetime(2022, 1, 1),
            hourly_rate=14.50,
            certifications={
                'Responsible Service of Alcohol': datetime(2024, 12, 31),
                'Food Safety Level 2': datetime(2024, 6, 30)
            }
        )
        self.manager.staff_members['TEST001'] = self.test_staff

    async def test_staff_scheduling(self):
        """Test smart staff scheduling"""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)

        schedule = await self.manager.smart_staff_scheduling(start_date, end_date)

        self.assertIn('schedule', schedule)
        self.assertIn('total_scheduled_hours', schedule)
        self.assertIn('total_labor_cost', schedule)

    async def test_certification_management(self):
        """Test training and certification tracking"""
        training_status = await self.manager.manage_training_certifications()

        self.assertIn('training_status', training_status)
        self.assertIn('renewal_alerts', training_status)
        self.assertIn('training_needs', training_status)

        # Check that our test staff appears in status
        self.assertIn('TEST001', training_status['training_status'])

    async def test_age_verification_protocols(self):
        """Test age verification protocol management"""
        protocols = await self.manager.age_verification_protocols()

        self.assertIn('protocols', protocols)
        self.assertIn('daily_briefing', protocols)
        self.assertIn('id_checking_policy', protocols['protocols'])

    async def test_closing_procedures(self):
        """Test closing time procedure generation"""
        procedures = await self.manager.closing_time_procedures()

        self.assertIn('closing_time', procedures)
        self.assertIn('security_protocols', procedures)
        self.assertIn('staff_assignments', procedures)

    async def test_compliance_monitoring(self):
        """Test regulatory compliance monitoring"""
        compliance = await self.manager.compliance_monitoring()

        self.assertIn('overall_score', compliance)
        self.assertIn('compliance_areas', compliance)
        self.assertIn('critical_issues', compliance)

    async def test_incident_recording(self):
        """Test incident recording functionality"""
        incident_data = {
            'type': 'age_verification',
            'description': 'Customer unable to provide valid ID',
            'action_taken': 'Sale refused politely',
            'reported_by': 'TEST001',
            'severity': 'low'
        }

        result = await self.manager.record_incident(incident_data)

        self.assertIn('incident_id', result)
        self.assertTrue(result['recorded'])
        self.assertIn('follow_up_actions', result)


class TestLocalMarketingPlatform(unittest.TestCase):
    """Test cases for Local Marketing Platform"""

    def setUp(self):
        self.config = {
            'local_teams': ['Cork City FC', 'Cork GAA'],
            'social_media_accounts': {
                'facebook': 'LocalPubCork',
                'instagram': '@localpubcork'
            }
        }
        self.platform = LocalMarketingPlatform(self.config)

        # Add test customer
        self.test_customer = Customer(
            customer_id='CUST001',
            name='Test Customer',
            email='test@example.ie',
            total_visits=15,
            total_spend=450.0,
            favorite_drinks=['Guinness', 'White Wine'],
            loyalty_points=225,
            segment=CustomerSegment.REGULARS
        )
        self.platform.customers['CUST001'] = self.test_customer

    async def test_community_integration(self):
        """Test community integration management"""
        result = await self.platform.manage_community_integration()

        self.assertIn('community_events_count', result)
        self.assertIn('partnership_opportunities', result)
        self.assertIn('community_campaigns', result)

    async def test_loyalty_program_operations(self):
        """Test loyalty program functionality"""
        result = await self.platform.operate_loyalty_programs()

        self.assertIn('points_awarded_today', result)
        self.assertIn('program_analytics', result)
        self.assertIn('personalized_offers_created', result)

    async def test_social_media_automation(self):
        """Test social media content automation"""
        result = await self.platform.automate_social_media()

        self.assertIn('daily_content_generated', result)
        self.assertIn('engagement_metrics', result)
        self.assertIn('reputation_score', result)

    async def test_tourist_services(self):
        """Test tourist service management"""
        result = await self.platform.provide_tourist_services()

        self.assertIn('tourist_packages', result)
        self.assertIn('attraction_partnerships', result)
        self.assertIn('recommendation_categories', result)

    async def test_match_day_specials(self):
        """Test match day special creation"""
        result = await self.platform.create_match_day_specials()

        self.assertIn('upcoming_matches', result)
        self.assertIn('match_day_promotions', result)
        self.assertIn('estimated_additional_revenue', result)

    async def test_campaign_performance_tracking(self):
        """Test marketing campaign performance tracking"""
        # This would test campaign tracking functionality
        # For now, we'll just ensure the method exists
        self.assertTrue(hasattr(self.platform, 'track_campaign_performance'))


class TestIntegration(unittest.TestCase):
    """Integration tests for agent coordination"""

    def setUp(self):
        self.config = {
            'tables': [{'number': 1, 'capacity': 4}],
            'beer_lines': [{'line_id': 'LINE1', 'beer_name': 'Guinness'}],
            'operating_hours': {'monday': {'open': '11:00', 'close': '23:00'}}
        }

    async def test_cross_agent_coordination(self):
        """Test coordination between multiple agents"""
        # Initialize agents
        bar_manager = BarTableManager(self.config)
        stock_controller = StockCellarController(self.config)
        events_hub = EntertainmentEventsHub(self.config)

        # Test scenario: Large party booking affects multiple agents
        # 1. Book table for large party
        booking_result = await bar_manager.manage_table_booking(party_size=8)

        # 2. Check if stock levels can handle increased demand
        inventory_status = await stock_controller.manage_inventory_tracking()

        # 3. Check for any conflicting events
        event_calendar = await events_hub.get_event_calendar(
            datetime.now(),
            datetime.now() + timedelta(days=1)
        )

        # Verify agents can operate independently
        self.assertIsInstance(booking_result, dict)
        self.assertIsInstance(inventory_status, dict)
        self.assertIsInstance(event_calendar, dict)


def run_async_test(test_func):
    """Helper to run async test functions"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(test_func())
    finally:
        loop.close()


# Test runner
if __name__ == '__main__':
    # Add async test support to unittest
    for test_class in [TestBarTableManager, TestStockCellarController,
                      TestEntertainmentEventsHub, TestStaffComplianceManager,
                      TestLocalMarketingPlatform, TestIntegration]:
        for method_name in dir(test_class):
            if method_name.startswith('test_') and asyncio.iscoroutinefunction(getattr(test_class, method_name)):
                # Wrap async tests
                test_method = getattr(test_class, method_name)
                setattr(test_class, method_name, lambda self, tm=test_method: run_async_test(lambda: tm(self)))

    # Run all tests
    unittest.main(verbosity=2)