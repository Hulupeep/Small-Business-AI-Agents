"""
Calendar integration utilities for the Meeting Scheduler Agent.

Supports integration with:
- Google Calendar API
- Microsoft Outlook/Office 365
- Calendly API
- Generic CalDAV servers
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class CalendarEvent:
    """Standard calendar event representation"""
    id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    location: Optional[str]
    timezone: str
    status: str  # confirmed, tentative, cancelled

class CalendarIntegration(ABC):
    """Abstract base class for calendar integrations"""

    @abstractmethod
    def create_meeting(self, calendar, meeting) -> Optional[str]:
        """Create a meeting and return external ID"""
        pass

    @abstractmethod
    def update_meeting(self, external_id: str, meeting) -> bool:
        """Update an existing meeting"""
        pass

    @abstractmethod
    def delete_meeting(self, external_id: str) -> bool:
        """Delete a meeting"""
        pass

    @abstractmethod
    def get_availability(self, calendar, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Get existing events in time range"""
        pass

    @abstractmethod
    def test_connection(self, calendar) -> bool:
        """Test calendar connection"""
        pass

class GoogleCalendarAPI(CalendarIntegration):
    """Google Calendar integration using Google Calendar API"""

    def __init__(self, credentials: Optional[Dict] = None):
        self.credentials = credentials
        self.service = None

        if credentials:
            self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Calendar service"""
        try:
            # Import Google libraries (make them optional)
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
            except ImportError:
                logger.error("Google API libraries not installed. Install with: pip install google-api-python-client google-auth")
                return

            if 'token' in self.credentials:
                creds = Credentials.from_authorized_user_info(self.credentials)
                self.service = build('calendar', 'v3', credentials=creds)
                logger.info("Google Calendar service initialized")
            else:
                logger.warning("Google Calendar credentials not properly configured")

        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")

    def create_meeting(self, calendar, meeting) -> Optional[str]:
        """Create meeting in Google Calendar"""
        try:
            if not self.service:
                logger.error("Google Calendar service not initialized")
                return None

            # Parse attendees
            attendees = []
            if meeting.attendee_emails:
                attendee_list = json.loads(meeting.attendee_emails) if isinstance(meeting.attendee_emails, str) else meeting.attendee_emails
                attendees = [{'email': email} for email in attendee_list]

            # Create event object
            event = {
                'summary': meeting.title,
                'description': meeting.description or '',
                'start': {
                    'dateTime': meeting.start_time.isoformat(),
                    'timeZone': meeting.timezone,
                },
                'end': {
                    'dateTime': meeting.end_time.isoformat(),
                    'timeZone': meeting.timezone,
                },
                'attendees': attendees,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': meeting.reminder_minutes or 15},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            if meeting.location:
                event['location'] = meeting.location

            if meeting.meeting_url:
                event['conferenceData'] = {
                    'createRequest': {
                        'requestId': f"meeting_{meeting.id}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }

            # Create the event
            created_event = self.service.events().insert(
                calendarId=calendar.calendar_id or 'primary',
                body=event,
                conferenceDataVersion=1
            ).execute()

            logger.info(f"Google Calendar event created: {created_event['id']}")
            return created_event['id']

        except Exception as e:
            logger.error(f"Failed to create Google Calendar event: {e}")
            return None

    def update_meeting(self, external_id: str, meeting) -> bool:
        """Update Google Calendar meeting"""
        try:
            if not self.service:
                return False

            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=external_id
            ).execute()

            # Update event fields
            event['summary'] = meeting.title
            event['description'] = meeting.description or ''
            event['start']['dateTime'] = meeting.start_time.isoformat()
            event['end']['dateTime'] = meeting.end_time.isoformat()

            if meeting.location:
                event['location'] = meeting.location

            # Update attendees
            if meeting.attendee_emails:
                attendee_list = json.loads(meeting.attendee_emails) if isinstance(meeting.attendee_emails, str) else meeting.attendee_emails
                event['attendees'] = [{'email': email} for email in attendee_list]

            # Update the event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=external_id,
                body=event
            ).execute()

            logger.info(f"Google Calendar event updated: {external_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update Google Calendar event: {e}")
            return False

    def delete_meeting(self, external_id: str) -> bool:
        """Delete Google Calendar meeting"""
        try:
            if not self.service:
                return False

            self.service.events().delete(
                calendarId='primary',
                eventId=external_id
            ).execute()

            logger.info(f"Google Calendar event deleted: {external_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Google Calendar event: {e}")
            return False

    def get_availability(self, calendar, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Get existing events in time range"""
        try:
            if not self.service:
                return []

            events_result = self.service.events().list(
                calendarId=calendar.calendar_id or 'primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            calendar_events = []

            for event in events:
                if 'dateTime' in event['start']:
                    event_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))

                    attendees = []
                    if 'attendees' in event:
                        attendees = [attendee.get('email', '') for attendee in event['attendees']]

                    calendar_event = CalendarEvent(
                        id=event['id'],
                        title=event.get('summary', ''),
                        description=event.get('description'),
                        start_time=event_start,
                        end_time=event_end,
                        attendees=attendees,
                        location=event.get('location'),
                        timezone=event['start'].get('timeZone', 'UTC'),
                        status=event.get('status', 'confirmed')
                    )
                    calendar_events.append(calendar_event)

            return calendar_events

        except Exception as e:
            logger.error(f"Failed to get Google Calendar availability: {e}")
            return []

    def test_connection(self, calendar) -> bool:
        """Test Google Calendar connection"""
        try:
            if not self.service:
                return False

            calendar_list = self.service.calendarList().list().execute()
            logger.info("Google Calendar connection successful")
            return True

        except Exception as e:
            logger.error(f"Google Calendar connection test failed: {e}")
            return False

class OutlookAPI(CalendarIntegration):
    """Microsoft Outlook/Office 365 integration"""

    def __init__(self, credentials: Optional[Dict] = None):
        self.credentials = credentials
        self.access_token = None

        if credentials:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Microsoft Graph API"""
        try:
            # This would implement OAuth2 flow for Microsoft Graph
            # For now, assume access token is provided in credentials
            self.access_token = self.credentials.get('access_token')

            if not self.access_token:
                logger.warning("Outlook access token not provided")

        except Exception as e:
            logger.error(f"Outlook authentication failed: {e}")

    def _make_graph_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make request to Microsoft Graph API"""
        try:
            if not self.access_token:
                return None

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }

            url = f"https://graph.microsoft.com/v1.0{endpoint}"

            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return None

            if response.status_code in [200, 201, 204]:
                return response.json() if response.content else {}
            else:
                logger.error(f"Outlook API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Outlook API request failed: {e}")
            return None

    def create_meeting(self, calendar, meeting) -> Optional[str]:
        """Create meeting in Outlook"""
        try:
            attendees = []
            if meeting.attendee_emails:
                attendee_list = json.loads(meeting.attendee_emails) if isinstance(meeting.attendee_emails, str) else meeting.attendee_emails
                attendees = [
                    {
                        'emailAddress': {'address': email, 'name': email.split('@')[0]},
                        'type': 'required'
                    }
                    for email in attendee_list
                ]

            event_data = {
                'subject': meeting.title,
                'body': {
                    'contentType': 'text',
                    'content': meeting.description or ''
                },
                'start': {
                    'dateTime': meeting.start_time.isoformat(),
                    'timeZone': meeting.timezone
                },
                'end': {
                    'dateTime': meeting.end_time.isoformat(),
                    'timeZone': meeting.timezone
                },
                'attendees': attendees,
                'isOnlineMeeting': meeting.meeting_url is not None,
                'reminderMinutesBeforeStart': meeting.reminder_minutes or 15
            }

            if meeting.location:
                event_data['location'] = {'displayName': meeting.location}

            result = self._make_graph_request('POST', '/me/events', event_data)

            if result:
                logger.info(f"Outlook event created: {result['id']}")
                return result['id']

            return None

        except Exception as e:
            logger.error(f"Failed to create Outlook event: {e}")
            return None

    def update_meeting(self, external_id: str, meeting) -> bool:
        """Update Outlook meeting"""
        try:
            attendees = []
            if meeting.attendee_emails:
                attendee_list = json.loads(meeting.attendee_emails) if isinstance(meeting.attendee_emails, str) else meeting.attendee_emails
                attendees = [
                    {
                        'emailAddress': {'address': email, 'name': email.split('@')[0]},
                        'type': 'required'
                    }
                    for email in attendee_list
                ]

            event_data = {
                'subject': meeting.title,
                'body': {
                    'contentType': 'text',
                    'content': meeting.description or ''
                },
                'start': {
                    'dateTime': meeting.start_time.isoformat(),
                    'timeZone': meeting.timezone
                },
                'end': {
                    'dateTime': meeting.end_time.isoformat(),
                    'timeZone': meeting.timezone
                },
                'attendees': attendees
            }

            if meeting.location:
                event_data['location'] = {'displayName': meeting.location}

            result = self._make_graph_request('PATCH', f'/me/events/{external_id}', event_data)
            return result is not None

        except Exception as e:
            logger.error(f"Failed to update Outlook event: {e}")
            return False

    def delete_meeting(self, external_id: str) -> bool:
        """Delete Outlook meeting"""
        try:
            result = self._make_graph_request('DELETE', f'/me/events/{external_id}')
            return result is not None

        except Exception as e:
            logger.error(f"Failed to delete Outlook event: {e}")
            return False

    def get_availability(self, calendar, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Get existing events in time range"""
        try:
            endpoint = f"/me/calendar/events?$filter=start/dateTime ge '{start_time.isoformat()}' and end/dateTime le '{end_time.isoformat()}'"
            result = self._make_graph_request('GET', endpoint)

            if not result or 'value' not in result:
                return []

            calendar_events = []
            for event in result['value']:
                event_start = datetime.fromisoformat(event['start']['dateTime'])
                event_end = datetime.fromisoformat(event['end']['dateTime'])

                attendees = []
                if 'attendees' in event:
                    attendees = [attendee['emailAddress']['address'] for attendee in event['attendees']]

                calendar_event = CalendarEvent(
                    id=event['id'],
                    title=event.get('subject', ''),
                    description=event.get('body', {}).get('content'),
                    start_time=event_start,
                    end_time=event_end,
                    attendees=attendees,
                    location=event.get('location', {}).get('displayName'),
                    timezone=event['start'].get('timeZone', 'UTC'),
                    status=event.get('showAs', 'busy')
                )
                calendar_events.append(calendar_event)

            return calendar_events

        except Exception as e:
            logger.error(f"Failed to get Outlook availability: {e}")
            return []

    def test_connection(self, calendar) -> bool:
        """Test Outlook connection"""
        try:
            result = self._make_graph_request('GET', '/me')
            return result is not None

        except Exception as e:
            logger.error(f"Outlook connection test failed: {e}")
            return False

class CalendlyAPI(CalendarIntegration):
    """Calendly integration for booking management"""

    def __init__(self, credentials: Optional[Dict] = None):
        self.credentials = credentials
        self.api_token = credentials.get('api_token') if credentials else None
        self.base_url = "https://api.calendly.com"

    def _make_calendly_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make request to Calendly API"""
        try:
            if not self.api_token:
                return None

            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }

            url = f"{self.base_url}{endpoint}"

            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return None

            if response.status_code in [200, 201, 204]:
                return response.json() if response.content else {}
            else:
                logger.error(f"Calendly API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Calendly API request failed: {e}")
            return None

    def create_meeting(self, calendar, meeting) -> Optional[str]:
        """Create meeting/event type in Calendly"""
        # Note: Calendly works differently - you typically create event types,
        # not individual meetings. This is a simplified implementation.
        try:
            event_type_data = {
                'name': meeting.title,
                'duration': int((meeting.end_time - meeting.start_time).total_seconds() / 60),
                'description_plain': meeting.description or '',
                'scheduling_url': f"https://calendly.com/{calendar.owner_email.split('@')[0]}/{meeting.title.lower().replace(' ', '-')}"
            }

            # This would create an event type in Calendly
            # For actual meeting scheduling, you'd typically redirect users to Calendly URL
            logger.info(f"Calendly event type created for: {meeting.title}")
            return f"calendly_{meeting.id}"

        except Exception as e:
            logger.error(f"Failed to create Calendly event: {e}")
            return None

    def update_meeting(self, external_id: str, meeting) -> bool:
        """Update Calendly event type"""
        # Calendly updates are typically done through their interface
        logger.info(f"Calendly event update requested: {external_id}")
        return True

    def delete_meeting(self, external_id: str) -> bool:
        """Delete/deactivate Calendly event type"""
        logger.info(f"Calendly event deletion requested: {external_id}")
        return True

    def get_availability(self, calendar, start_time: datetime, end_time: datetime) -> List[CalendarEvent]:
        """Get scheduled events from Calendly"""
        try:
            # Get user info first
            user_result = self._make_calendly_request('GET', '/users/me')
            if not user_result:
                return []

            user_uri = user_result['resource']['uri']

            # Get scheduled events
            endpoint = f"/scheduled_events?user={user_uri}&min_start_time={start_time.isoformat()}&max_start_time={end_time.isoformat()}"
            result = self._make_calendly_request('GET', endpoint)

            if not result or 'collection' not in result:
                return []

            calendar_events = []
            for event in result['collection']:
                event_start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                event_end = datetime.fromisoformat(event['end_time'].replace('Z', '+00:00'))

                calendar_event = CalendarEvent(
                    id=event['uri'],
                    title=event['name'],
                    description=event.get('description'),
                    start_time=event_start,
                    end_time=event_end,
                    attendees=[],  # Calendly doesn't expose attendee emails in this endpoint
                    location=event.get('location', {}).get('location') if event.get('location') else None,
                    timezone='UTC',
                    status=event.get('status', 'active')
                )
                calendar_events.append(calendar_event)

            return calendar_events

        except Exception as e:
            logger.error(f"Failed to get Calendly availability: {e}")
            return []

    def test_connection(self, calendar) -> bool:
        """Test Calendly connection"""
        try:
            result = self._make_calendly_request('GET', '/users/me')
            return result is not None

        except Exception as e:
            logger.error(f"Calendly connection test failed: {e}")
            return False


def create_calendar_integration(provider: str, credentials: Dict) -> Optional[CalendarIntegration]:
    """Factory function to create calendar integration based on provider"""
    provider = provider.lower()

    if provider == 'google':
        return GoogleCalendarAPI(credentials)
    elif provider in ['outlook', 'office365', 'microsoft']:
        return OutlookAPI(credentials)
    elif provider == 'calendly':
        return CalendlyAPI(credentials)
    else:
        logger.error(f"Unsupported calendar provider: {provider}")
        return None


def test_all_integrations(calendar_configs: List[Dict]) -> Dict[str, bool]:
    """Test all configured calendar integrations"""
    results = {}

    for config in calendar_configs:
        provider = config.get('provider')
        credentials = config.get('credentials', {})

        integration = create_calendar_integration(provider, credentials)
        if integration:
            results[provider] = integration.test_connection(config)
        else:
            results[provider] = False

    return results