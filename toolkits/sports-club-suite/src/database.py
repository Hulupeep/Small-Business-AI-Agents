#!/usr/bin/env python3
"""
Sports Club Database Models and Setup
Simple SQLite-based database for practical club management
"""

import sqlite3
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import os

class ClubDatabase:
    """Simple SQLite database for sports club management"""

    def __init__(self, db_path: str = "club_database.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def init_database(self):
        """Initialize database with required tables"""
        conn = self.get_connection()

        # Members table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                address TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                membership_type TEXT DEFAULT 'Member',
                family_id TEXT,
                status TEXT DEFAULT 'Active',
                registration_date DATE DEFAULT CURRENT_DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Payments table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                amount DECIMAL(10,2) NOT NULL,
                payment_type TEXT NOT NULL,
                payment_method TEXT,
                stripe_payment_id TEXT,
                status TEXT DEFAULT 'Pending',
                description TEXT,
                payment_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')

        # Events/Fixtures table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_type TEXT NOT NULL,
                event_date DATETIME NOT NULL,
                location TEXT,
                cost DECIMAL(10,2) DEFAULT 0,
                max_participants INTEGER,
                registration_deadline DATETIME,
                status TEXT DEFAULT 'Scheduled',
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Event registrations
        conn.execute('''
            CREATE TABLE IF NOT EXISTS event_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                member_id INTEGER,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                payment_status TEXT DEFAULT 'Unpaid',
                notes TEXT,
                FOREIGN KEY (event_id) REFERENCES events (id),
                FOREIGN KEY (member_id) REFERENCES members (id),
                UNIQUE(event_id, member_id)
            )
        ''')

        # Volunteers table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS volunteers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                role TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                hours_logged DECIMAL(5,2) DEFAULT 0,
                certifications TEXT,
                background_check_date DATE,
                status TEXT DEFAULT 'Active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
        ''')

        # Communications log
        conn.execute('''
            CREATE TABLE IF NOT EXISTS communications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_type TEXT NOT NULL,
                recipient_id INTEGER,
                message_type TEXT NOT NULL,
                subject TEXT,
                message TEXT NOT NULL,
                sent_method TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Club settings
        conn.execute('''
            CREATE TABLE IF NOT EXISTS club_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_member(self, member_data: Dict[str, Any]) -> int:
        """Add new member to database"""
        conn = self.get_connection()

        cursor = conn.execute('''
            INSERT INTO members (
                first_name, last_name, email, phone, date_of_birth, address,
                emergency_contact_name, emergency_contact_phone, membership_type, family_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            member_data['first_name'],
            member_data['last_name'],
            member_data['email'],
            member_data.get('phone'),
            member_data.get('date_of_birth'),
            member_data.get('address'),
            member_data.get('emergency_contact_name'),
            member_data.get('emergency_contact_phone'),
            member_data.get('membership_type', 'Member'),
            member_data.get('family_id')
        ))

        member_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return member_id

    def get_members(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all members"""
        conn = self.get_connection()

        query = "SELECT * FROM members"
        if active_only:
            query += " WHERE status = 'Active'"
        query += " ORDER BY last_name, first_name"

        cursor = conn.execute(query)
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return members

    def get_member_by_id(self, member_id: int) -> Optional[Dict[str, Any]]:
        """Get member by ID"""
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        conn.close()
        return dict(member) if member else None

    def add_payment(self, payment_data: Dict[str, Any]) -> int:
        """Add payment record"""
        conn = self.get_connection()

        cursor = conn.execute('''
            INSERT INTO payments (
                member_id, amount, payment_type, payment_method,
                stripe_payment_id, status, description, payment_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment_data['member_id'],
            payment_data['amount'],
            payment_data['payment_type'],
            payment_data.get('payment_method'),
            payment_data.get('stripe_payment_id'),
            payment_data.get('status', 'Pending'),
            payment_data.get('description'),
            payment_data.get('payment_date')
        ))

        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id

    def get_member_payments(self, member_id: int) -> List[Dict[str, Any]]:
        """Get payments for a member"""
        conn = self.get_connection()
        cursor = conn.execute('''
            SELECT * FROM payments
            WHERE member_id = ?
            ORDER BY created_at DESC
        ''', (member_id,))
        payments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return payments

    def add_event(self, event_data: Dict[str, Any]) -> int:
        """Add new event"""
        conn = self.get_connection()

        cursor = conn.execute('''
            INSERT INTO events (
                title, description, event_type, event_date, location,
                cost, max_participants, registration_deadline, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data['title'],
            event_data.get('description'),
            event_data['event_type'],
            event_data['event_date'],
            event_data.get('location'),
            event_data.get('cost', 0),
            event_data.get('max_participants'),
            event_data.get('registration_deadline'),
            event_data.get('created_by')
        ))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def get_events(self, future_only: bool = True) -> List[Dict[str, Any]]:
        """Get events"""
        conn = self.get_connection()

        query = "SELECT * FROM events"
        if future_only:
            query += " WHERE event_date >= datetime('now')"
        query += " ORDER BY event_date"

        cursor = conn.execute(query)
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events

    def register_for_event(self, event_id: int, member_id: int, notes: str = None) -> int:
        """Register member for event"""
        conn = self.get_connection()

        cursor = conn.execute('''
            INSERT OR IGNORE INTO event_registrations (event_id, member_id, notes)
            VALUES (?, ?, ?)
        ''', (event_id, member_id, notes))

        registration_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return registration_id

    def log_communication(self, comm_data: Dict[str, Any]) -> int:
        """Log communication sent"""
        conn = self.get_connection()

        cursor = conn.execute('''
            INSERT INTO communications (
                recipient_type, recipient_id, message_type, subject,
                message, sent_method, status, sent_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            comm_data['recipient_type'],
            comm_data.get('recipient_id'),
            comm_data['message_type'],
            comm_data.get('subject'),
            comm_data['message'],
            comm_data['sent_method'],
            comm_data.get('status', 'Sent'),
            comm_data.get('sent_at', datetime.now())
        ))

        comm_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return comm_id

    def get_club_statistics(self) -> Dict[str, Any]:
        """Get basic club statistics"""
        conn = self.get_connection()

        # Member count
        cursor = conn.execute("SELECT COUNT(*) FROM members WHERE status = 'Active'")
        member_count = cursor.fetchone()[0]

        # Payment statistics
        cursor = conn.execute('''
            SELECT
                SUM(CASE WHEN status = 'Completed' THEN amount ELSE 0 END) as paid,
                SUM(CASE WHEN status = 'Pending' THEN amount ELSE 0 END) as pending,
                COUNT(*) as total_payments
            FROM payments
        ''')
        payment_stats = dict(cursor.fetchone())

        # Event count
        cursor = conn.execute("SELECT COUNT(*) FROM events WHERE event_date >= date('now')")
        upcoming_events = cursor.fetchone()[0]

        conn.close()

        return {
            'total_members': member_count,
            'payments_received': payment_stats['paid'] or 0,
            'payments_pending': payment_stats['pending'] or 0,
            'total_payments': payment_stats['total_payments'] or 0,
            'upcoming_events': upcoming_events
        }

def setup_sample_data(db: ClubDatabase):
    """Setup sample data for testing"""

    # Add sample members
    sample_members = [
        {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'john.smith@email.com',
            'phone': '0871234567',
            'address': '123 Main St, Dublin',
            'membership_type': 'Full Member',
            'emergency_contact_name': 'Mary Smith',
            'emergency_contact_phone': '0879876543'
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'email': 'sarah.johnson@email.com',
            'phone': '0862345678',
            'address': '456 Oak Ave, Cork',
            'membership_type': 'Family Member',
            'family_id': 'JOHN001'
        },
        {
            'first_name': 'Mike',
            'last_name': 'O\'Brien',
            'email': 'mike.obrien@email.com',
            'phone': '0853456789',
            'membership_type': 'Student Member'
        }
    ]

    for member_data in sample_members:
        member_id = db.add_member(member_data)

        # Add sample payment for each member
        db.add_payment({
            'member_id': member_id,
            'amount': 50.00,
            'payment_type': 'Membership Fee',
            'status': 'Completed',
            'payment_date': date.today().isoformat()
        })

    # Add sample events
    sample_events = [
        {
            'title': 'Championship Match vs Rivals',
            'description': 'Important championship match',
            'event_type': 'Match',
            'event_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'location': 'Home Ground',
            'created_by': 'System'
        },
        {
            'title': 'Annual General Meeting',
            'description': 'Club AGM - all members welcome',
            'event_type': 'Meeting',
            'event_date': (datetime.now() + timedelta(days=14)).isoformat(),
            'location': 'Clubhouse',
            'created_by': 'System'
        }
    ]

    for event_data in sample_events:
        db.add_event(event_data)


if __name__ == "__main__":
    # Initialize database
    print("Setting up club database...")
    db = ClubDatabase()

    # Add sample data
    print("Adding sample data...")
    setup_sample_data(db)

    # Show statistics
    stats = db.get_club_statistics()
    print(f"Database setup complete!")
    print(f"Members: {stats['total_members']}")
    print(f"Payments received: €{stats['payments_received']:.2f}")
    print(f"Upcoming events: {stats['upcoming_events']}")