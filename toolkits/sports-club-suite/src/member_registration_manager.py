#!/usr/bin/env python3
"""
Sports Club Member Registration Manager
Practical member management with SQLite database and real validation
"""

import re
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from database import ClubDatabase
import phonenumbers
from email_validator import validate_email, EmailNotValidError

class MemberRegistrationManager:
    """Simple, practical member management system"""

    def __init__(self, db_path: str = "club_database.db"):
        self.db = ClubDatabase(db_path)
        self.membership_fees = {
            'Full Member': 100.0,
            'Family Member': 75.0,
            'Student Member': 50.0,
            'Social Member': 25.0
        }
        self.family_discount = 0.10  # 10% discount for families

    def register_member(self, member_data: Dict[str, Any]) -> int:
        """Register a new member with realistic validation"""

        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in member_data or not member_data[field].strip():
                raise ValueError(f"Required field '{field}' is missing")

        # Validate email
        try:
            validated_email = validate_email(member_data['email'])
            member_data['email'] = validated_email.email
        except EmailNotValidError:
            raise ValueError("Invalid email address")

        # Validate phone number if provided
        if member_data.get('phone'):
            try:
                # Assume Irish numbers if no country code
                phone_str = member_data['phone']
                if not phone_str.startswith('+'):
                    phone_str = '+353' + phone_str.lstrip('0')

                parsed_phone = phonenumbers.parse(phone_str, None)
                if not phonenumbers.is_valid_number(parsed_phone):
                    raise ValueError("Invalid phone number")

                member_data['phone'] = phonenumbers.format_number(
                    parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL
                )
            except phonenumbers.NumberParseException:
                raise ValueError("Invalid phone number format")

        # Add member to database
        try:
            member_id = self.db.add_member(member_data)
            return member_id
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("Email address already registered")
            raise ValueError(f"Registration failed: {str(e)}")

    def get_members(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all members"""
        return self.db.get_members(active_only)

    def get_member_by_id(self, member_id: int) -> Optional[Dict[str, Any]]:
        """Get member by ID"""
        return self.db.get_member_by_id(member_id)

    def search_members(self, search_term: str) -> List[Dict[str, Any]]:
        """Search members by name or email"""
        all_members = self.db.get_members()
        search_term = search_term.lower()

        results = []
        for member in all_members:
            if (search_term in member['first_name'].lower() or
                search_term in member['last_name'].lower() or
                search_term in member['email'].lower()):
                results.append(member)

        return results

    def calculate_member_fees(self, member_id: int) -> Dict[str, float]:
        """Calculate fees for a member"""
        member = self.db.get_member_by_id(member_id)
        if not member:
            raise ValueError("Member not found")

        membership_type = member.get('membership_type', 'Full Member')
        base_fee = self.membership_fees.get(membership_type, 100.0)

        # Apply family discount if applicable
        family_discount = 0.0
        if member.get('family_id'):
            # Count family members
            family_members = [m for m in self.db.get_members()
                            if m.get('family_id') == member['family_id']]
            if len(family_members) > 1:
                family_discount = base_fee * self.family_discount

        total_fee = base_fee - family_discount

        return {
            'base_fee': base_fee,
            'family_discount': family_discount,
            'total_fee': total_fee,
            'membership_type': membership_type
        }

    def process_payment(self, member_id: int, amount: float,
                       payment_method: str = 'Cash', notes: str = '') -> int:
        """Process payment for member"""
        member = self.db.get_member_by_id(member_id)
        if not member:
            raise ValueError("Member not found")

        payment_data = {
            'member_id': member_id,
            'amount': amount,
            'payment_type': 'Membership Fee',
            'payment_method': payment_method,
            'status': 'Completed',
            'description': notes,
            'payment_date': date.today().isoformat()
        }

        return self.db.add_payment(payment_data)

    def get_member_payments(self, member_id: int) -> List[Dict[str, Any]]:
        """Get payment history for member"""
        return self.db.get_member_payments(member_id)

    def get_payment_summary(self) -> Dict[str, Any]:
        """Get payment summary for all members"""
        members = self.db.get_members()
        summary = {
            'total_members': len(members),
            'paid_members': 0,
            'total_collected': 0.0,
            'total_outstanding': 0.0
        }

        for member in members:
            payments = self.db.get_member_payments(member['id'])
            total_paid = sum(p['amount'] for p in payments if p['status'] == 'Completed')
            member_fees = self.calculate_member_fees(member['id'])

            if total_paid >= member_fees['total_fee']:
                summary['paid_members'] += 1

            summary['total_collected'] += total_paid
            outstanding = max(0, member_fees['total_fee'] - total_paid)
            summary['total_outstanding'] += outstanding

        return summary

    def generate_member_list_csv(self) -> str:
        """Generate CSV export of members"""
        members = self.db.get_members()

        csv_lines = [
            'ID,First Name,Last Name,Email,Phone,Membership Type,Registration Date,Status'
        ]

        for member in members:
            csv_lines.append(
                f"{member['id']},"
                f"\"{member['first_name']}\","
                f"\"{member['last_name']}\","
                f"{member['email']},"
                f"{member.get('phone', '')},"
                f"\"{member.get('membership_type', '')}\","
                f"{member.get('registration_date', '')},"
                f"{member.get('status', 'Active')}"
            )

        return '\n'.join(csv_lines)

    def get_membership_statistics(self) -> Dict[str, Any]:
        """Get basic membership statistics"""
        members = self.db.get_members()

        # Count by membership type
        type_counts = {}
        for member in members:
            mtype = member.get('membership_type', 'Unknown')
            type_counts[mtype] = type_counts.get(mtype, 0) + 1

        # Count families
        family_ids = set()
        for member in members:
            if member.get('family_id'):
                family_ids.add(member['family_id'])

        # Payment statistics
        payment_summary = self.get_payment_summary()

        return {
            'total_members': len(members),
            'membership_types': type_counts,
            'family_groups': len(family_ids),
            'payment_collection_rate': (
                payment_summary['paid_members'] / len(members) * 100
                if members else 0
            ),
            'total_revenue': payment_summary['total_collected'],
            'outstanding_fees': payment_summary['total_outstanding']
        }

    def send_payment_reminders(self) -> List[Dict[str, Any]]:
        """Generate list of members needing payment reminders"""
        members = self.db.get_members()
        reminders = []

        for member in members:
            payments = self.db.get_member_payments(member['id'])
            total_paid = sum(p['amount'] for p in payments if p['status'] == 'Completed')
            fees = self.calculate_member_fees(member['id'])

            if total_paid < fees['total_fee']:
                outstanding = fees['total_fee'] - total_paid
                reminders.append({
                    'member_id': member['id'],
                    'name': f"{member['first_name']} {member['last_name']}",
                    'email': member['email'],
                    'phone': member.get('phone'),
                    'outstanding_amount': outstanding,
                    'total_fee': fees['total_fee'],
                    'amount_paid': total_paid
                })

        return sorted(reminders, key=lambda x: x['outstanding_amount'], reverse=True)


# Example usage and testing
if __name__ == "__main__":
    # Initialize the system
    manager = MemberRegistrationManager()

    # Test member registration
    test_member = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '0871234567',
        'address': '123 Test Street, Dublin',
        'membership_type': 'Full Member',
        'emergency_contact_name': 'Jane Doe',
        'emergency_contact_phone': '0879876543'
    }

    try:
        member_id = manager.register_member(test_member)
        print(f"✅ Registered member ID: {member_id}")

        # Calculate fees
        fees = manager.calculate_member_fees(member_id)
        print(f"💰 Fees: €{fees['total_fee']:.2f}")

        # Process payment
        payment_id = manager.process_payment(
            member_id, fees['total_fee'], 'Credit Card', 'Annual membership fee'
        )
        print(f"💳 Payment processed ID: {payment_id}")

        # Get statistics
        stats = manager.get_membership_statistics()
        print(f"📊 Statistics: {stats}")

    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")