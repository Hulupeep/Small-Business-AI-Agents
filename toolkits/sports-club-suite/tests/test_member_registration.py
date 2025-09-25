#!/usr/bin/env python3
"""
Test Suite for GAA Member Registration Manager
Comprehensive tests for member registration, family management, and compliance
"""

import unittest
from datetime import date, datetime
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from member_registration_manager import (
    MemberRegistrationManager, Member, Family, AgeGrade,
    MembershipType, PaymentStatus, FeeStructure
)

class TestMemberRegistrationManager(unittest.TestCase):
    """Test cases for Member Registration Manager"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = MemberRegistrationManager()

    def test_member_registration_success(self):
        """Test successful member registration"""
        member_data = {
            'first_name': 'Seán',
            'surname': 'Murphy',
            'date_of_birth': '2010-05-15',
            'address': '123 Main Street, Cork',
            'phone': '0861234567',
            'email': 'sean.murphy@email.ie',
            'emergency_contact': 'Mary Murphy',
            'emergency_phone': '0879876543',
            'membership_type': 'Player',
            'photo_consent': True
        }

        member_id = self.manager.register_member(member_data)

        self.assertIsNotNone(member_id)
        self.assertIn(member_id, self.manager.members)

        member = self.manager.members[member_id]
        self.assertEqual(member.first_name, 'Seán')
        self.assertEqual(member.surname, 'Murphy')
        self.assertEqual(member.membership_type, MembershipType.PLAYER)
        self.assertTrue(member.is_active)

    def test_member_registration_missing_fields(self):
        """Test registration fails with missing required fields"""
        incomplete_data = {
            'first_name': 'John',
            'surname': 'Doe'
            # Missing required fields
        }

        with self.assertRaises(ValueError) as context:
            self.manager.register_member(incomplete_data)

        self.assertIn("Required field", str(context.exception))

    def test_invalid_email_format(self):
        """Test registration fails with invalid email"""
        member_data = {
            'first_name': 'John',
            'surname': 'Doe',
            'date_of_birth': '2010-05-15',
            'address': '123 Main Street, Cork',
            'phone': '0861234567',
            'email': 'invalid-email',  # Invalid format
            'emergency_contact': 'Jane Doe',
            'emergency_phone': '0879876543'
        }

        with self.assertRaises(ValueError) as context:
            self.manager.register_member(member_data)

        self.assertIn("Invalid email format", str(context.exception))

    def test_invalid_phone_format(self):
        """Test registration fails with invalid phone number"""
        member_data = {
            'first_name': 'John',
            'surname': 'Doe',
            'date_of_birth': '2010-05-15',
            'address': '123 Main Street, Cork',
            'phone': '123456',  # Invalid Irish phone format
            'email': 'john.doe@email.ie',
            'emergency_contact': 'Jane Doe',
            'emergency_phone': '0879876543'
        }

        with self.assertRaises(ValueError) as context:
            self.manager.register_member(member_data)

        self.assertIn("Invalid Irish phone number", str(context.exception))

    def test_age_grade_calculation(self):
        """Test age grade calculation based on GAA rules"""
        # Test U14 player (born in 2010, playing in 2024)
        member_data = {
            'first_name': 'Test',
            'surname': 'Player',
            'date_of_birth': '2010-08-15',
            'address': '123 Test Street',
            'phone': '0861234567',
            'email': 'test@email.ie',
            'emergency_contact': 'Test Contact',
            'emergency_phone': '0879876543'
        }

        member_id = self.manager.register_member(member_data)
        member = self.manager.members[member_id]

        calculated_grade = member.calculate_age_grade()
        self.assertEqual(calculated_grade, AgeGrade.U14)

    def test_family_membership_creation(self):
        """Test family membership management"""
        # Register first family member
        parent_data = {
            'first_name': 'John',
            'surname': 'O\'Brien',
            'date_of_birth': '1980-01-01',
            'address': '456 Family Street, Cork',
            'phone': '0861111111',
            'email': 'john.obrien@email.ie',
            'emergency_contact': 'Mary O\'Brien',
            'emergency_phone': '0862222222',
            'membership_type': 'Player',
            'family_id': 'OBRI001'
        }

        parent_id = self.manager.register_member(parent_data)

        # Register child in same family
        child_data = {
            'first_name': 'Paddy',
            'surname': 'O\'Brien',
            'date_of_birth': '2012-01-01',
            'address': '456 Family Street, Cork',
            'phone': '0861111111',
            'email': 'john.obrien@email.ie',
            'emergency_contact': 'John O\'Brien',
            'emergency_phone': '0862222222',
            'membership_type': 'Player',
            'family_id': 'OBRI001'
        }

        child_id = self.manager.register_member(child_data)

        # Check family was created
        self.assertIn('OBRI001', self.manager.families)
        family = self.manager.families['OBRI001']

        self.assertEqual(len(family.members), 2)
        self.assertIn(parent_id, family.members)
        self.assertIn(child_id, family.members)

    def test_family_discount_calculation(self):
        """Test family discount is applied correctly"""
        # Register two players in same family
        family_id = 'DISC001'

        member1_data = {
            'first_name': 'Player',
            'surname': 'One',
            'date_of_birth': '2010-01-01',
            'address': '789 Discount Street',
            'phone': '0863333333',
            'email': 'player1@email.ie',
            'emergency_contact': 'Parent One',
            'emergency_phone': '0864444444',
            'membership_type': 'Player',
            'family_id': family_id
        }

        member2_data = {
            'first_name': 'Player',
            'surname': 'Two',
            'date_of_birth': '2012-01-01',
            'address': '789 Discount Street',
            'phone': '0863333333',
            'email': 'player2@email.ie',
            'emergency_contact': 'Parent One',
            'emergency_phone': '0864444444',
            'membership_type': 'Player',
            'family_id': family_id
        }

        member1_id = self.manager.register_member(member1_data)
        member2_id = self.manager.register_member(member2_data)

        # Check family discount was applied
        family = self.manager.families[family_id]
        expected_base = 2 * self.manager.fee_structure.player_fee
        expected_discount = expected_base * self.manager.fee_structure.family_discount_percent
        expected_total = expected_base - expected_discount + (2 * self.manager.county_levy)

        self.assertEqual(family.discount_applied, expected_discount)
        self.assertEqual(family.total_fees, expected_total)

    def test_member_fee_calculation(self):
        """Test individual member fee calculation"""
        member_data = {
            'first_name': 'Single',
            'surname': 'Player',
            'date_of_birth': '2010-01-01',
            'address': '321 Single Street',
            'phone': '0865555555',
            'email': 'single@email.ie',
            'emergency_contact': 'Single Parent',
            'emergency_phone': '0866666666',
            'membership_type': 'Player'
        }

        member_id = self.manager.register_member(member_data)
        fees = self.manager.get_member_fees(member_id)

        expected_total = self.manager.fee_structure.player_fee + self.manager.county_levy

        self.assertEqual(fees['base_fee'], self.manager.fee_structure.player_fee)
        self.assertEqual(fees['county_levy'], self.manager.county_levy)
        self.assertEqual(fees['family_discount'], 0.0)
        self.assertEqual(fees['total_fee'], expected_total)

    def test_social_member_fees(self):
        """Test social member fee calculation"""
        member_data = {
            'first_name': 'Social',
            'surname': 'Member',
            'date_of_birth': '1970-01-01',
            'address': '654 Social Street',
            'phone': '0867777777',
            'email': 'social@email.ie',
            'emergency_contact': 'Social Contact',
            'emergency_phone': '0868888888',
            'membership_type': 'Social Member'
        }

        member_id = self.manager.register_member(member_data)
        fees = self.manager.get_member_fees(member_id)

        self.assertEqual(fees['base_fee'], self.manager.fee_structure.social_member_fee)
        self.assertEqual(fees['county_levy'], 0.0)  # No county levy for social members
        self.assertEqual(fees['total_fee'], self.manager.fee_structure.social_member_fee)

    def test_annual_age_grade_update(self):
        """Test annual age grade progression"""
        # Register a player who will progress age grades
        member_data = {
            'first_name': 'Progress',
            'surname': 'Player',
            'date_of_birth': '2008-06-15',  # Will be U16 currently
            'address': '987 Progress Street',
            'phone': '0869999999',
            'email': 'progress@email.ie',
            'emergency_contact': 'Progress Parent',
            'emergency_phone': '0860000000',
            'membership_type': 'Player'
        }

        member_id = self.manager.register_member(member_data)
        member = self.manager.members[member_id]

        # Manually set to U14 to test progression
        member.age_grade = AgeGrade.U14

        # Run annual update
        updates = self.manager.update_age_grades_annual()

        self.assertIn(member_id, updates)
        # Should progress from U14 to U16 (current age)
        self.assertEqual(member.age_grade, AgeGrade.U16)

    def test_registration_reminders(self):
        """Test registration renewal reminders"""
        # Create a member with old registration
        member_data = {
            'first_name': 'Old',
            'surname': 'Registration',
            'date_of_birth': '2010-01-01',
            'address': '111 Old Street',
            'phone': '0861010101',
            'email': 'old@email.ie',
            'emergency_contact': 'Old Contact',
            'emergency_phone': '0862020202',
            'membership_type': 'Player'
        }

        member_id = self.manager.register_member(member_data)
        member = self.manager.members[member_id]

        # Set registration to last year
        member.registration_date = date(2023, 1, 1)

        reminders = self.manager.generate_registration_reminders()

        self.assertEqual(len(reminders), 1)
        self.assertEqual(reminders[0]['member_id'], member_id)
        self.assertGreater(reminders[0]['days_overdue'], 0)

    def test_county_board_export(self):
        """Test county board data export"""
        # Register test members
        for i in range(3):
            member_data = {
                'first_name': f'Export{i}',
                'surname': 'Test',
                'date_of_birth': f'201{i}-01-01',
                'address': f'{i} Export Street',
                'phone': f'08610101{i:02d}',
                'email': f'export{i}@email.ie',
                'emergency_contact': f'Contact{i}',
                'emergency_phone': f'08620202{i:02d}',
                'membership_type': 'Player'
            }
            self.manager.register_member(member_data)

        export_data = self.manager.export_county_board_data()

        self.assertEqual(export_data['total_members'], 3)
        self.assertEqual(len(export_data['registrations']), 3)
        self.assertIn('members_by_grade', export_data)

    def test_membership_statistics(self):
        """Test membership statistics generation"""
        # Register diverse membership
        members_data = [
            ('Player1', 'Player', '2010-01-01'),
            ('Player2', 'Player', '2008-01-01'),
            ('Social1', 'Social Member', '1980-01-01'),
            ('Support1', 'Supporter', '1975-01-01')
        ]

        for name, membership_type, dob in members_data:
            member_data = {
                'first_name': name,
                'surname': 'Stats',
                'date_of_birth': dob,
                'address': '555 Stats Street',
                'phone': '0865555555',
                'email': f'{name.lower()}@email.ie',
                'emergency_contact': 'Stats Contact',
                'emergency_phone': '0866666666',
                'membership_type': membership_type
            }
            self.manager.register_member(member_data)

        stats = self.manager.get_membership_statistics()

        self.assertEqual(stats['total_members'], 4)
        self.assertEqual(stats['active_members'], 4)
        self.assertIn('Player', stats['by_membership_type'])
        self.assertIn('Social Member', stats['by_membership_type'])

    def test_unique_member_id_generation(self):
        """Test that member IDs are unique"""
        member_data = {
            'first_name': 'John',
            'surname': 'Smith',
            'date_of_birth': '2010-01-01',
            'address': '123 Test Street',
            'phone': '0861234567',
            'email': 'john1@email.ie',
            'emergency_contact': 'Jane Smith',
            'emergency_phone': '0879876543'
        }

        # Register multiple members with same name
        ids = []
        for i in range(3):
            member_data['email'] = f'john{i}@email.ie'
            member_id = self.manager.register_member(member_data)
            ids.append(member_id)

        # All IDs should be unique
        self.assertEqual(len(ids), len(set(ids)))

if __name__ == '__main__':
    unittest.main()