#!/usr/bin/env python3
"""
Sports Club Volunteer Management
Simple volunteer tracking with basic compliance date reminders
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from database import ClubDatabase
import pandas as pd

class VolunteerManager:
    """Simple volunteer tracking and management"""

    def __init__(self, db_path: str = "club_database.db"):
        self.db = ClubDatabase(db_path)

        # Standard volunteer roles
        self.volunteer_roles = [
            'Coach',
            'Assistant Coach',
            'Team Manager',
            'Referee',
            'Committee Member',
            'Groundskeeper',
            'First Aid',
            'Fundraising Committee',
            'Social Committee',
            'Youth Coordinator',
            'General Volunteer'
        ]

        # Compliance requirements (simplified)
        self.compliance_requirements = {
            'Coach': ['Background Check', 'Coaching Certificate'],
            'Team Manager': ['Background Check'],
            'Referee': ['Referee Course'],
            'First Aid': ['First Aid Certificate'],
            'Youth Coordinator': ['Background Check', 'Child Protection Course']
        }

    def add_volunteer(self, member_id: int, role: str, start_date: date = None,
                     certifications: List[str] = None) -> int:
        """Add volunteer role to member"""

        # Check member exists
        member = self.db.get_member_by_id(member_id)
        if not member:
            raise ValueError("Member not found")

        if role not in self.volunteer_roles:
            raise ValueError(f"Invalid role. Choose from: {', '.join(self.volunteer_roles)}")

        # Check if already a volunteer in this role
        conn = self.db.get_connection()
        existing = conn.execute('''
            SELECT id FROM volunteers
            WHERE member_id = ? AND role = ? AND status = 'Active'
        ''', (member_id, role)).fetchone()

        if existing:
            conn.close()
            raise ValueError("Member already has this volunteer role")

        # Insert volunteer record
        cursor = conn.execute('''
            INSERT INTO volunteers (
                member_id, role, start_date, certifications, status
            ) VALUES (?, ?, ?, ?, 'Active')
        ''', (
            member_id,
            role,
            (start_date or date.today()).isoformat(),
            ', '.join(certifications or [])
        ))

        volunteer_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return volunteer_id

    def log_volunteer_hours(self, member_id: int, hours: float, activity: str,
                          activity_date: date = None) -> None:
        """Log volunteer hours for a member"""

        member = self.db.get_member_by_id(member_id)
        if not member:
            raise ValueError("Member not found")

        if hours <= 0 or hours > 24:
            raise ValueError("Hours must be between 0 and 24")

        conn = self.db.get_connection()

        # Update total hours logged
        conn.execute('''
            UPDATE volunteers
            SET hours_logged = hours_logged + ?
            WHERE member_id = ? AND status = 'Active'
        ''', (hours, member_id))

        # Create activity log entry (simplified - just update notes)
        activity_entry = f"{activity_date or date.today()}: {activity} ({hours}h)"

        conn.execute('''
            UPDATE volunteers
            SET notes = COALESCE(notes || '\n', '') || ?
            WHERE member_id = ? AND status = 'Active'
        ''', (activity_entry, member_id))

        conn.commit()
        conn.close()

    def update_compliance_date(self, member_id: int, compliance_type: str,
                             completion_date: date) -> None:
        """Update compliance certification date"""

        conn = self.db.get_connection()

        # Simple approach - update the background_check_date field or notes
        if compliance_type.lower() == 'background check':
            conn.execute('''
                UPDATE volunteers
                SET background_check_date = ?
                WHERE member_id = ? AND status = 'Active'
            ''', (completion_date.isoformat(), member_id))
        else:
            # Store other certifications in notes
            cert_entry = f"{compliance_type}: {completion_date.isoformat()}"
            conn.execute('''
                UPDATE volunteers
                SET certifications = COALESCE(certifications || ', ', '') || ?
                WHERE member_id = ? AND status = 'Active'
            ''', (cert_entry, member_id))

        conn.commit()
        conn.close()

    def get_volunteers(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get list of all volunteers with member details"""

        conn = self.db.get_connection()

        query = '''
            SELECT
                v.id as volunteer_id,
                v.member_id,
                m.first_name,
                m.last_name,
                m.email,
                m.phone,
                v.role,
                v.start_date,
                v.hours_logged,
                v.certifications,
                v.background_check_date,
                v.status,
                v.notes
            FROM volunteers v
            JOIN members m ON v.member_id = m.id
        '''

        if active_only:
            query += " WHERE v.status = 'Active'"

        query += " ORDER BY m.last_name, m.first_name"

        cursor = conn.execute(query)
        volunteers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return volunteers

    def get_volunteer_by_member(self, member_id: int) -> List[Dict[str, Any]]:
        """Get all volunteer roles for a specific member"""

        conn = self.db.get_connection()

        cursor = conn.execute('''
            SELECT * FROM volunteers
            WHERE member_id = ?
            ORDER BY start_date DESC
        ''', (member_id,))

        volunteers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return volunteers

    def get_compliance_reminders(self, days_ahead: int = 90) -> List[Dict[str, Any]]:
        """Get volunteers needing compliance updates"""

        volunteers = self.get_volunteers(active_only=True)
        reminders = []

        cutoff_date = date.today() + timedelta(days=days_ahead)

        for volunteer in volunteers:
            member_name = f"{volunteer['first_name']} {volunteer['last_name']}"
            role = volunteer['role']

            # Check background check expiry (assume 3-year validity)
            if volunteer['background_check_date']:
                try:
                    bg_check_date = date.fromisoformat(volunteer['background_check_date'])
                    bg_expiry = bg_check_date + timedelta(days=1095)  # 3 years

                    if bg_expiry <= cutoff_date:
                        days_until_expiry = (bg_expiry - date.today()).days
                        reminders.append({
                            'volunteer_id': volunteer['volunteer_id'],
                            'member_id': volunteer['member_id'],
                            'name': member_name,
                            'role': role,
                            'compliance_type': 'Background Check',
                            'expiry_date': bg_expiry.isoformat(),
                            'days_until_expiry': days_until_expiry,
                            'priority': 'High' if days_until_expiry <= 30 else 'Medium'
                        })
                except ValueError:
                    # Invalid date format
                    pass
            else:
                # No background check on record
                if role in self.compliance_requirements and 'Background Check' in self.compliance_requirements[role]:
                    reminders.append({
                        'volunteer_id': volunteer['volunteer_id'],
                        'member_id': volunteer['member_id'],
                        'name': member_name,
                        'role': role,
                        'compliance_type': 'Background Check',
                        'expiry_date': 'Not on file',
                        'days_until_expiry': -999,
                        'priority': 'High'
                    })

        return sorted(reminders, key=lambda x: x['days_until_expiry'])

    def generate_volunteer_report(self) -> Dict[str, Any]:
        """Generate volunteer summary report"""

        volunteers = self.get_volunteers(active_only=True)

        # Count by role
        role_counts = {}
        total_hours = 0
        volunteers_with_bg_check = 0

        for volunteer in volunteers:
            role = volunteer['role']
            role_counts[role] = role_counts.get(role, 0) + 1

            if volunteer['hours_logged']:
                total_hours += volunteer['hours_logged']

            if volunteer['background_check_date']:
                volunteers_with_bg_check += 1

        # Calculate compliance rate
        total_volunteers = len(volunteers)
        compliance_rate = (volunteers_with_bg_check / total_volunteers * 100) if total_volunteers > 0 else 0

        return {
            'total_volunteers': total_volunteers,
            'volunteers_by_role': role_counts,
            'total_hours_logged': total_hours,
            'average_hours_per_volunteer': total_hours / total_volunteers if total_volunteers > 0 else 0,
            'background_check_compliance_rate': round(compliance_rate, 1),
            'volunteers_with_background_check': volunteers_with_bg_check
        }

    def export_volunteer_spreadsheet(self) -> str:
        """Export volunteers to CSV format for spreadsheet programs"""

        volunteers = self.get_volunteers(active_only=True)

        if not volunteers:
            return "No volunteers to export"

        # Prepare data for CSV
        csv_data = []
        for volunteer in volunteers:
            csv_data.append({
                'Member ID': volunteer['member_id'],
                'First Name': volunteer['first_name'],
                'Last Name': volunteer['last_name'],
                'Email': volunteer['email'],
                'Phone': volunteer.get('phone', ''),
                'Volunteer Role': volunteer['role'],
                'Start Date': volunteer['start_date'],
                'Hours Logged': volunteer['hours_logged'] or 0,
                'Background Check Date': volunteer['background_check_date'] or 'Not on file',
                'Certifications': volunteer['certifications'] or 'None',
                'Status': volunteer['status'],
                'Notes': volunteer['notes'] or ''
            })

        # Convert to CSV
        df = pd.DataFrame(csv_data)
        return df.to_csv(index=False)

    def import_volunteer_hours_csv(self, csv_content: str) -> Dict[str, Any]:
        """Import volunteer hours from CSV file"""

        try:
            df = pd.read_csv(StringIO(csv_content))

            required_columns = ['Member ID', 'Hours', 'Activity', 'Date']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")

            imported_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    member_id = int(row['Member ID'])
                    hours = float(row['Hours'])
                    activity = str(row['Activity'])
                    activity_date = date.fromisoformat(row['Date'])

                    self.log_volunteer_hours(member_id, hours, activity, activity_date)
                    imported_count += 1

                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")

            return {
                'imported_records': imported_count,
                'total_records': len(df),
                'errors': errors
            }

        except Exception as e:
            raise ValueError(f"CSV import failed: {str(e)}")

    def get_top_volunteers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top volunteers by hours logged"""

        volunteers = self.get_volunteers(active_only=True)

        # Sort by hours logged
        sorted_volunteers = sorted(
            volunteers,
            key=lambda x: x['hours_logged'] or 0,
            reverse=True
        )

        # Return top volunteers with formatted data
        top_volunteers = []
        for volunteer in sorted_volunteers[:limit]:
            top_volunteers.append({
                'name': f"{volunteer['first_name']} {volunteer['last_name']}",
                'role': volunteer['role'],
                'hours_logged': volunteer['hours_logged'] or 0,
                'start_date': volunteer['start_date']
            })

        return top_volunteers


# Example usage and testing
if __name__ == "__main__":
    # Initialize volunteer manager
    manager = VolunteerManager()

    # Test adding volunteer (assuming member ID 1 exists)
    try:
        volunteer_id = manager.add_volunteer(
            member_id=1,
            role='Coach',
            certifications=['Level 1 Coaching Certificate']
        )
        print(f"✅ Added volunteer role: ID {volunteer_id}")

        # Log some hours
        manager.log_volunteer_hours(
            member_id=1,
            hours=3.0,
            activity='Team training session'
        )
        print("⏰ Logged volunteer hours")

        # Update compliance
        manager.update_compliance_date(
            member_id=1,
            compliance_type='Background Check',
            completion_date=date(2023, 6, 15)
        )
        print("📋 Updated compliance date")

        # Get volunteers
        volunteers = manager.get_volunteers()
        print(f"👥 Found {len(volunteers)} active volunteers")

        # Generate report
        report = manager.generate_volunteer_report()
        print(f"📊 Volunteer report: {report['total_volunteers']} volunteers, {report['total_hours_logged']} total hours")

        # Check compliance reminders
        reminders = manager.get_compliance_reminders()
        print(f"⚠️  {len(reminders)} compliance reminders")

        # Export spreadsheet
        csv_export = manager.export_volunteer_spreadsheet()
        print(f"📁 Exported CSV: {len(csv_export.split(chr(10)))} lines")

        # Top volunteers
        top_volunteers = manager.get_top_volunteers(limit=5)
        print(f"🏆 Top volunteers: {[v['name'] for v in top_volunteers]}")

    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")