#!/usr/bin/env python3
"""
Sports Club Fixture & Event Coordinator
Basic event scheduling with calendar integration and simple notifications
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any
from database import ClubDatabase
from icalendar import Calendar, Event
import pytz

class FixtureEventCoordinator:
    """Simple fixture and event scheduling system"""

    def __init__(self, db_path: str = "club_database.db"):
        self.db = ClubDatabase(db_path)

    def create_event(self, event_data: Dict[str, Any]) -> int:
        """Create a new event/fixture"""
        required_fields = ['title', 'event_type', 'event_date']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Required field '{field}' is missing")

        # Validate event date
        try:
            if isinstance(event_data['event_date'], str):
                event_datetime = datetime.fromisoformat(event_data['event_date'])
            else:
                event_datetime = event_data['event_date']

            if event_datetime < datetime.now():
                raise ValueError("Cannot schedule events in the past")

        except (ValueError, TypeError):
            raise ValueError("Invalid event date format")

        return self.db.add_event(event_data)

    def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming events within specified days"""
        events = self.db.get_events(future_only=True)

        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        filtered_events = []
        for event in events:
            event_date = datetime.fromisoformat(event['event_date'])
            if event_date <= cutoff_date:
                filtered_events.append(event)

        return sorted(filtered_events, key=lambda x: x['event_date'])

    def get_events_for_date(self, target_date: date) -> List[Dict[str, Any]]:
        """Get all events for a specific date"""
        all_events = self.db.get_events(future_only=False)

        matching_events = []
        for event in all_events:
            event_date = datetime.fromisoformat(event['event_date']).date()
            if event_date == target_date:
                matching_events.append(event)

        return sorted(matching_events, key=lambda x: x['event_date'])

    def check_availability(self, event_date: datetime, location: str = None) -> Dict[str, Any]:
        """Check if date/location is available for new event"""
        # Get events for the same day
        day_events = self.get_events_for_date(event_date.date())

        conflicts = []
        for event in day_events:
            existing_datetime = datetime.fromisoformat(event['event_date'])
            time_diff = abs((existing_datetime - event_date).total_seconds() / 3600)

            # Check for conflicts within 2 hours
            if time_diff < 2:
                conflict_info = {
                    'event_title': event['title'],
                    'event_time': existing_datetime.strftime('%H:%M'),
                    'location': event.get('location', 'Unknown')
                }

                # If location specified, only flag if same location
                if location and event.get('location') == location:
                    conflicts.append(conflict_info)
                elif not location:
                    conflicts.append(conflict_info)

        return {
            'available': len(conflicts) == 0,
            'conflicts': conflicts,
            'recommendation': self._get_alternative_times(event_date) if conflicts else None
        }

    def _get_alternative_times(self, original_datetime: datetime) -> List[str]:
        """Suggest alternative times for the same day"""
        alternatives = []
        base_date = original_datetime.date()

        # Suggest times: 10:00, 14:00, 16:00, 19:00
        suggested_times = [10, 14, 16, 19]

        for hour in suggested_times:
            alt_datetime = datetime.combine(base_date, datetime.min.time().replace(hour=hour))

            # Check if this time is available
            availability = self.check_availability(alt_datetime)
            if availability['available']:
                alternatives.append(alt_datetime.strftime('%H:%M'))

        return alternatives

    def register_member_for_event(self, event_id: int, member_id: int, notes: str = None) -> int:
        """Register a member for an event"""
        # Check if event exists
        events = self.db.get_events()
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            raise ValueError("Event not found")

        # Check if member exists
        member = self.db.get_member_by_id(member_id)
        if not member:
            raise ValueError("Member not found")

        # Check capacity if set
        if event.get('max_participants'):
            # Count existing registrations (would need new DB method)
            # For now, just proceed

        return self.db.register_for_event(event_id, member_id, notes)

    def generate_ical_calendar(self, include_past: bool = False) -> str:
        """Generate iCal calendar file for import"""
        cal = Calendar()
        cal.add('prodid', '-//Sports Club//Event Calendar//EN')
        cal.add('version', '2.0')

        events = self.db.get_events(future_only=not include_past)

        for event_data in events:
            event = Event()
            event.add('uid', f"event_{event_data['id']}@sportsclub.local")
            event.add('summary', event_data['title'])

            # Parse datetime
            event_datetime = datetime.fromisoformat(event_data['event_date'])

            # Make timezone-aware (assume local timezone)
            local_tz = pytz.timezone('Europe/Dublin')  # Change as needed
            if event_datetime.tzinfo is None:
                event_datetime = local_tz.localize(event_datetime)

            event.add('dtstart', event_datetime)
            event.add('dtend', event_datetime + timedelta(hours=2))  # Default 2-hour duration

            if event_data.get('description'):
                event.add('description', event_data['description'])

            if event_data.get('location'):
                event.add('location', event_data['location'])

            cal.add_component(event)

        return cal.to_ical().decode('utf-8')

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get basic event statistics"""
        all_events = self.db.get_events(future_only=False)
        upcoming_events = self.db.get_events(future_only=True)

        # Count by type
        type_counts = {}
        for event in all_events:
            event_type = event.get('event_type', 'Unknown')
            type_counts[event_type] = type_counts.get(event_type, 0) + 1

        # This month's events
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        this_month_events = []
        for event in all_events:
            event_date = datetime.fromisoformat(event['event_date'])
            if month_start <= event_date <= month_end:
                this_month_events.append(event)

        return {
            'total_events': len(all_events),
            'upcoming_events': len(upcoming_events),
            'events_this_month': len(this_month_events),
            'events_by_type': type_counts
        }

    def send_event_reminders(self, days_before: int = 3) -> List[Dict[str, Any]]:
        """Generate list of events needing reminders"""
        upcoming_events = self.get_upcoming_events(days_ahead=days_before)

        reminders = []
        for event in upcoming_events:
            event_datetime = datetime.fromisoformat(event['event_date'])
            days_until = (event_datetime.date() - date.today()).days

            if days_until <= days_before and days_until >= 0:
                reminders.append({
                    'event_id': event['id'],
                    'title': event['title'],
                    'event_date': event['event_date'],
                    'location': event.get('location'),
                    'days_until': days_until,
                    'event_type': event.get('event_type')
                })

        return reminders

    def get_weekly_schedule(self, week_start: date = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get events organized by day for a week"""
        if not week_start:
            week_start = date.today() - timedelta(days=date.today().weekday())

        week_end = week_start + timedelta(days=6)

        # Get all events in the week
        all_events = self.db.get_events(future_only=False)
        week_events = []

        for event in all_events:
            event_date = datetime.fromisoformat(event['event_date']).date()
            if week_start <= event_date <= week_end:
                week_events.append(event)

        # Organize by day
        weekly_schedule = {
            'Monday': [],
            'Tuesday': [],
            'Wednesday': [],
            'Thursday': [],
            'Friday': [],
            'Saturday': [],
            'Sunday': []
        }

        for event in week_events:
            event_date = datetime.fromisoformat(event['event_date'])
            day_name = event_date.strftime('%A')
            weekly_schedule[day_name].append({
                'id': event['id'],
                'title': event['title'],
                'time': event_date.strftime('%H:%M'),
                'location': event.get('location', ''),
                'type': event.get('event_type', '')
            })

        # Sort events by time within each day
        for day in weekly_schedule:
            weekly_schedule[day].sort(key=lambda x: x['time'])

        return weekly_schedule

    def export_events_csv(self, include_past: bool = False) -> str:
        """Export events to CSV format"""
        events = self.db.get_events(future_only=not include_past)

        csv_lines = [
            'ID,Title,Type,Date,Time,Location,Description,Created By'
        ]

        for event in events:
            event_datetime = datetime.fromisoformat(event['event_date'])

            csv_lines.append(
                f"{event['id']},"
                f"\"{event['title']}\","
                f"\"{event.get('event_type', '')}\","
                f"{event_datetime.strftime('%Y-%m-%d')},"
                f"{event_datetime.strftime('%H:%M')},"
                f"\"{event.get('location', '')}\","
                f"\"{event.get('description', '')}\","
                f"\"{event.get('created_by', '')}\""
            )

        return '\n'.join(csv_lines)


# Example usage and testing
if __name__ == "__main__":
    # Initialize the coordinator
    coordinator = FixtureEventCoordinator()

    # Create sample events
    sample_events = [
        {
            'title': 'Training Session',
            'description': 'Weekly team training',
            'event_type': 'Training',
            'event_date': (datetime.now() + timedelta(days=2)).isoformat(),
            'location': 'Main Pitch',
            'created_by': 'Coach'
        },
        {
            'title': 'Championship Match vs Rovers',
            'description': 'Important league match',
            'event_type': 'Match',
            'event_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'location': 'Home Ground',
            'max_participants': 22,
            'created_by': 'Manager'
        },
        {
            'title': 'Club Meeting',
            'description': 'Monthly committee meeting',
            'event_type': 'Meeting',
            'event_date': (datetime.now() + timedelta(days=14)).isoformat(),
            'location': 'Clubhouse',
            'created_by': 'Secretary'
        }
    ]

    try:
        created_events = []
        for event_data in sample_events:
            event_id = coordinator.create_event(event_data)
            created_events.append(event_id)
            print(f"✅ Created event: {event_data['title']} (ID: {event_id})")

        # Check availability
        test_datetime = datetime.now() + timedelta(days=2, hours=1)
        availability = coordinator.check_availability(test_datetime, 'Main Pitch')
        print(f"📅 Availability check: {availability}")

        # Get upcoming events
        upcoming = coordinator.get_upcoming_events(days_ahead=30)
        print(f"🗓️  Upcoming events: {len(upcoming)}")

        # Generate calendar
        ical_calendar = coordinator.generate_ical_calendar()
        print(f"📅 Generated iCal calendar ({len(ical_calendar)} characters)")

        # Get statistics
        stats = coordinator.get_event_statistics()
        print(f"📊 Event statistics: {stats}")

        # Get weekly schedule
        weekly = coordinator.get_weekly_schedule()
        print(f"📅 Weekly schedule: {sum(len(events) for events in weekly.values())} events this week")

    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")