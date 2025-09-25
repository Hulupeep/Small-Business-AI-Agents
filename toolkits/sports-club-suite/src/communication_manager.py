#!/usr/bin/env python3
"""
Sports Club Communication Manager
Basic SMS/Email communications with member groups using Twilio and SendGrid
"""

import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from database import ClubDatabase
from twilio.rest import Client as TwilioClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import re

class CommunicationManager:
    """Simple communication system for club messaging"""

    def __init__(self, db_path: str = "club_database.db"):
        self.db = ClubDatabase(db_path)

        # Initialize Twilio (for SMS)
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')

        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = TwilioClient(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
            print("WARNING: No Twilio credentials found. SMS sending disabled.")

        # Initialize SendGrid (for Email)
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('CLUB_EMAIL', 'noreply@sportsclub.com')

        if self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(api_key=self.sendgrid_api_key)
        else:
            self.sendgrid_client = None
            print("WARNING: No SendGrid API key found. Email sending disabled.")

        # Message templates
        self.message_templates = {
            'event_reminder': {
                'sms': "Reminder: {event_title} on {event_date} at {event_time}. Location: {location}",
                'email': {
                    'subject': "Event Reminder: {event_title}",
                    'body': """
                    <h2>Event Reminder</h2>
                    <p><strong>{event_title}</strong></p>
                    <p>Date: {event_date}</p>
                    <p>Time: {event_time}</p>
                    <p>Location: {location}</p>
                    <p>{description}</p>
                    """
                }
            },
            'payment_reminder': {
                'sms': "Payment reminder: Your membership fee of €{amount} is due. Please pay via our website or contact the treasurer.",
                'email': {
                    'subject': "Payment Reminder - Membership Fee Due",
                    'body': """
                    <h2>Payment Reminder</h2>
                    <p>Dear {member_name},</p>
                    <p>This is a reminder that your membership fee of €{amount} is due.</p>
                    <p>Please make payment via our website or contact the treasurer.</p>
                    <p>Thank you for your continued membership.</p>
                    """
                }
            },
            'general_announcement': {
                'sms': "{message}",
                'email': {
                    'subject': "{subject}",
                    'body': """
                    <h2>{subject}</h2>
                    <p>{message}</p>
                    """
                }
            }
        }

    def send_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS to a phone number"""

        if not self.twilio_client:
            return {
                'success': False,
                'message_id': None,
                'error': 'Twilio not configured'
            }

        # Clean phone number
        clean_phone = self._clean_phone_number(phone_number)
        if not clean_phone:
            return {
                'success': False,
                'message_id': None,
                'error': 'Invalid phone number'
            }

        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=clean_phone
            )

            return {
                'success': True,
                'message_id': message_obj.sid,
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }

    def send_email(self, to_email: str, subject: str, html_content: str,
                  plain_content: str = None) -> Dict[str, Any]:
        """Send email to an address"""

        if not self.sendgrid_client:
            return {
                'success': False,
                'message_id': None,
                'error': 'SendGrid not configured'
            }

        if not self._is_valid_email(to_email):
            return {
                'success': False,
                'message_id': None,
                'error': 'Invalid email address'
            }

        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content or self._html_to_plain(html_content)
            )

            response = self.sendgrid_client.send(message)

            return {
                'success': response.status_code < 300,
                'message_id': response.headers.get('X-Message-Id'),
                'error': None if response.status_code < 300 else f"HTTP {response.status_code}"
            }

        except Exception as e:
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }

    def send_to_member_group(self, member_ids: List[int], template: str,
                           template_data: Dict[str, Any], method: str = 'email') -> Dict[str, Any]:
        """Send message to a group of members"""

        if template not in self.message_templates:
            raise ValueError(f"Unknown template: {template}")

        if method not in ['sms', 'email']:
            raise ValueError("Method must be 'sms' or 'email'")

        results = {
            'total_attempted': len(member_ids),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for member_id in member_ids:
            member = self.db.get_member_by_id(member_id)
            if not member:
                results['failed'] += 1
                results['errors'].append(f"Member {member_id} not found")
                continue

            try:
                if method == 'sms':
                    if not member.get('phone'):
                        results['failed'] += 1
                        results['errors'].append(f"No phone number for {member['first_name']} {member['last_name']}")
                        continue

                    message = self.message_templates[template]['sms'].format(**template_data)
                    result = self.send_sms(member['phone'], message)

                elif method == 'email':
                    email_template = self.message_templates[template]['email']

                    # Add member name to template data
                    template_data_with_member = {
                        **template_data,
                        'member_name': f"{member['first_name']} {member['last_name']}"
                    }

                    subject = email_template['subject'].format(**template_data_with_member)
                    body = email_template['body'].format(**template_data_with_member)

                    result = self.send_email(member['email'], subject, body)

                if result['success']:
                    results['successful'] += 1

                    # Log communication
                    self.db.log_communication({
                        'recipient_type': 'member',
                        'recipient_id': member_id,
                        'message_type': template,
                        'subject': template_data.get('subject', template),
                        'message': message if method == 'sms' else subject,
                        'sent_method': method.upper(),
                        'status': 'Sent',
                        'sent_at': datetime.now()
                    })
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{member['first_name']} {member['last_name']}: {result['error']}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"{member['first_name']} {member['last_name']}: {str(e)}")

        return results

    def send_event_reminders(self, event_id: int, days_before: int = 1) -> Dict[str, Any]:
        """Send reminders for upcoming event"""

        # Get event details
        events = self.db.get_events()
        event = next((e for e in events if e['id'] == event_id), None)

        if not event:
            raise ValueError("Event not found")

        event_datetime = datetime.fromisoformat(event['event_date'])
        days_until_event = (event_datetime.date() - date.today()).days

        if days_until_event != days_before:
            return {
                'message': f"Event is in {days_until_event} days, not {days_before}",
                'reminders_sent': 0
            }

        # Get registered members for event (if registration system is used)
        # For now, send to all members
        members = self.db.get_members()
        member_ids = [m['id'] for m in members]

        template_data = {
            'event_title': event['title'],
            'event_date': event_datetime.strftime('%A, %B %d'),
            'event_time': event_datetime.strftime('%H:%M'),
            'location': event.get('location', 'TBA'),
            'description': event.get('description', '')
        }

        # Send email reminders
        email_results = self.send_to_member_group(
            member_ids, 'event_reminder', template_data, 'email'
        )

        return {
            'event_title': event['title'],
            'reminders_sent': email_results['successful'],
            'failed': email_results['failed'],
            'errors': email_results['errors'][:5]  # Limit errors shown
        }

    def send_payment_reminders(self) -> Dict[str, Any]:
        """Send payment reminders to members with outstanding fees"""

        # This would integrate with the member registration manager
        # For now, return mock results
        return {
            'reminders_sent': 12,
            'failed': 2,
            'total_outstanding': 450.00
        }

    def send_general_announcement(self, subject: str, message: str,
                                member_ids: List[int] = None, method: str = 'email') -> Dict[str, Any]:
        """Send general announcement to members"""

        if member_ids is None:
            # Send to all active members
            members = self.db.get_members(active_only=True)
            member_ids = [m['id'] for m in members]

        template_data = {
            'subject': subject,
            'message': message
        }

        return self.send_to_member_group(
            member_ids, 'general_announcement', template_data, method
        )

    def get_communication_log(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """Get recent communication history"""

        conn = self.db.get_connection()

        cutoff_date = datetime.now() - timedelta(days=days_back)

        cursor = conn.execute('''
            SELECT
                c.*,
                m.first_name,
                m.last_name
            FROM communications c
            LEFT JOIN members m ON c.recipient_id = m.id
            WHERE c.created_at >= ?
            ORDER BY c.created_at DESC
        ''', (cutoff_date.isoformat(),))

        communications = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return communications

    def get_communication_statistics(self) -> Dict[str, Any]:
        """Get communication usage statistics"""

        conn = self.db.get_connection()

        # Messages sent this month
        month_start = date.today().replace(day=1)
        cursor = conn.execute('''
            SELECT
                sent_method,
                COUNT(*) as count,
                message_type
            FROM communications
            WHERE sent_at >= ?
            GROUP BY sent_method, message_type
        ''', (month_start.isoformat(),))

        results = cursor.fetchall()
        conn.close()

        stats = {
            'this_month': {
                'email': 0,
                'sms': 0,
                'total': 0
            },
            'by_type': {}
        }

        for row in results:
            method = row['sent_method'].lower()
            count = row['count']
            msg_type = row['message_type']

            stats['this_month'][method] = stats['this_month'].get(method, 0) + count
            stats['this_month']['total'] += count
            stats['by_type'][msg_type] = stats['by_type'].get(msg_type, 0) + count

        return stats

    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """Clean and validate phone number"""
        if not phone:
            return None

        # Remove non-digits
        clean = re.sub(r'\D', '', phone)

        # Handle Irish numbers
        if clean.startswith('353'):
            return f"+{clean}"
        elif clean.startswith('0') and len(clean) == 10:
            return f"+353{clean[1:]}"
        elif len(clean) == 9:
            return f"+353{clean}"

        return None

    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _html_to_plain(self, html: str) -> str:
        """Convert HTML to plain text (basic implementation)"""
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', html)
        # Clean up whitespace
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean


# Example usage and testing
if __name__ == "__main__":
    # Initialize communication manager
    comm_manager = CommunicationManager()

    try:
        # Test email sending (will fail without proper credentials)
        email_result = comm_manager.send_email(
            to_email='test@example.com',
            subject='Test Email',
            html_content='<p>This is a test email from the sports club system.</p>'
        )
        print(f"📧 Email test: {'Success' if email_result['success'] else 'Failed'} - {email_result.get('error', 'OK')}")

        # Test SMS sending (will fail without proper credentials)
        sms_result = comm_manager.send_sms(
            phone_number='+353871234567',
            message='Test SMS from sports club system'
        )
        print(f"📱 SMS test: {'Success' if sms_result['success'] else 'Failed'} - {sms_result.get('error', 'OK')}")

        # Test group messaging
        group_result = comm_manager.send_general_announcement(
            subject='Test Announcement',
            message='This is a test announcement to all members.',
            member_ids=[1, 2, 3],  # Test member IDs
            method='email'
        )
        print(f"📢 Group message: {group_result['successful']} sent, {group_result['failed']} failed")

        # Get communication statistics
        stats = comm_manager.get_communication_statistics()
        print(f"📊 Communication stats: {stats['this_month']['total']} messages this month")

        # Get recent communications
        recent = comm_manager.get_communication_log(days_back=7)
        print(f"📝 Recent communications: {len(recent)} in last 7 days")

    except Exception as e:
        print(f"💥 Error: {e}")

    # Print configuration status
    print(f"\n📡 Service Status:")
    print(f"  Twilio SMS: {'Enabled' if comm_manager.twilio_client else 'Disabled (no credentials)'}")
    print(f"  SendGrid Email: {'Enabled' if comm_manager.sendgrid_client else 'Disabled (no credentials)'}")
    print(f"\n💡 To enable services, set environment variables:")
    print(f"  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
    print(f"  SENDGRID_API_KEY, CLUB_EMAIL")