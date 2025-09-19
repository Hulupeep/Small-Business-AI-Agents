"""
Natural Language Processing utilities for the Meeting Scheduler Agent.

Handles:
- Intent recognition for scheduling requests
- Entity extraction (dates, times, attendees)
- Context understanding and ambiguity resolution
- Multi-language support
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExtractedEntity:
    """Extracted entity from text"""
    type: str  # date, time, duration, person, location
    value: Any
    confidence: float
    start_pos: int
    end_pos: int
    original_text: str

@dataclass
class SchedulingIntent:
    """Parsed scheduling intent"""
    action: str  # schedule, reschedule, cancel, find_time
    confidence: float
    entities: List[ExtractedEntity]
    meeting_title: Optional[str]
    raw_text: str

class NLPProcessor:
    """
    Natural Language Processing engine for understanding scheduling requests.
    """

    def __init__(self):
        # Compile regex patterns for better performance
        self._compile_patterns()

        # Intent keywords
        self.intent_patterns = {
            'schedule': [
                'schedule', 'book', 'arrange', 'set up', 'organize', 'plan',
                'create meeting', 'new meeting', 'meeting with'
            ],
            'reschedule': [
                'reschedule', 'move', 'change', 'shift', 'postpone',
                'delay', 'push back', 'move meeting'
            ],
            'cancel': [
                'cancel', 'delete', 'remove', 'call off', 'abort',
                'cancel meeting', 'delete meeting'
            ],
            'find_time': [
                'find time', 'when can', 'availability', 'free time',
                'when are you free', 'possible times'
            ]
        }

    def _compile_patterns(self):
        """Compile regex patterns for entity extraction"""

        # Date patterns
        self.date_patterns = [
            # Absolute dates
            r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})\b',  # YYYY/MM/DD
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?\b',
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})(?:st|nd|rd|th)?\b',

            # Relative dates
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(next|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(next|this)\s+(week|month)\b',
            r'\bin\s+(\d+)\s+(days?|weeks?|months?)\b',
        ]

        # Time patterns
        self.time_patterns = [
            r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)\b',
            r'\b(\d{1,2})\s*(am|pm|AM|PM)\b',
            r'\b(\d{1,2}):(\d{2})\b',  # 24-hour format
            r'\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)?\b',
            r'\b(morning|afternoon|evening|night|noon|midnight)\b',
        ]

        # Duration patterns
        self.duration_patterns = [
            r'\b(\d+)\s*(hour|hr)s?\b',
            r'\b(\d+)\s*(minute|min)s?\b',
            r'\b(\d+)h\s*(\d+)m\b',
            r'\b(\d+):(\d+)\s*(long|duration)\b',
            r'\bfor\s+(\d+)\s*(hour|hr|minute|min)s?\b',
        ]

        # Email patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # Location patterns
        self.location_patterns = [
            r'\b(?:at|in|location:?)\s+([A-Za-z0-9\s,.-]+?)(?:\s+on|\s+with|\s+at|\.|$)',
            r'\broom\s+([A-Za-z0-9]+)\b',
            r'\bbuilding\s+([A-Za-z0-9\s]+)\b',
            r'\boffice\s+([A-Za-z0-9\s]+)\b',
        ]

        # Compile all patterns
        self.compiled_date_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.date_patterns]
        self.compiled_time_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.time_patterns]
        self.compiled_duration_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.duration_patterns]
        self.compiled_email_pattern = re.compile(self.email_pattern)
        self.compiled_location_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.location_patterns]

    def process_scheduling_request(self, text: str) -> SchedulingIntent:
        """
        Main processing function to extract scheduling intent and entities.
        """
        try:
            # Detect intent
            action, confidence = self._detect_intent(text)

            # Extract entities
            entities = self._extract_entities(text)

            # Extract meeting title
            meeting_title = self._extract_meeting_title(text, action)

            return SchedulingIntent(
                action=action,
                confidence=confidence,
                entities=entities,
                meeting_title=meeting_title,
                raw_text=text
            )

        except Exception as e:
            logger.error(f"Error processing scheduling request: {e}")
            return SchedulingIntent(
                action='schedule',
                confidence=0.1,
                entities=[],
                meeting_title='Meeting',
                raw_text=text
            )

    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """Detect the scheduling intent from text"""
        text_lower = text.lower()
        intent_scores = {}

        for intent, keywords in self.intent_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight longer keywords more heavily
                    score += len(keyword.split()) * 0.3

            intent_scores[intent] = score

        # Find the highest scoring intent
        if not intent_scores or max(intent_scores.values()) == 0:
            return 'schedule', 0.5  # Default to schedule with medium confidence

        best_intent = max(intent_scores, key=intent_scores.get)
        max_score = intent_scores[best_intent]

        # Normalize confidence (rough approximation)
        confidence = min(1.0, max_score / 2.0)

        return best_intent, confidence

    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract all entities from text"""
        entities = []

        # Extract dates
        entities.extend(self._extract_dates(text))

        # Extract times
        entities.extend(self._extract_times(text))

        # Extract durations
        entities.extend(self._extract_durations(text))

        # Extract emails (people)
        entities.extend(self._extract_emails(text))

        # Extract locations
        entities.extend(self._extract_locations(text))

        return entities

    def _extract_dates(self, text: str) -> List[ExtractedEntity]:
        """Extract date entities from text"""
        entities = []

        for pattern in self.compiled_date_patterns:
            for match in pattern.finditer(text):
                date_text = match.group(0)
                parsed_date = self._parse_date(date_text)

                if parsed_date:
                    entity = ExtractedEntity(
                        type='date',
                        value=parsed_date,
                        confidence=0.9,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_text=date_text
                    )
                    entities.append(entity)

        return entities

    def _extract_times(self, text: str) -> List[ExtractedEntity]:
        """Extract time entities from text"""
        entities = []

        for pattern in self.compiled_time_patterns:
            for match in pattern.finditer(text):
                time_text = match.group(0)
                parsed_time = self._parse_time(time_text)

                if parsed_time:
                    entity = ExtractedEntity(
                        type='time',
                        value=parsed_time,
                        confidence=0.8,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_text=time_text
                    )
                    entities.append(entity)

        return entities

    def _extract_durations(self, text: str) -> List[ExtractedEntity]:
        """Extract duration entities from text"""
        entities = []

        for pattern in self.compiled_duration_patterns:
            for match in pattern.finditer(text):
                duration_text = match.group(0)
                parsed_duration = self._parse_duration(duration_text)

                if parsed_duration:
                    entity = ExtractedEntity(
                        type='duration',
                        value=parsed_duration,
                        confidence=0.8,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_text=duration_text
                    )
                    entities.append(entity)

        return entities

    def _extract_emails(self, text: str) -> List[ExtractedEntity]:
        """Extract email addresses (people) from text"""
        entities = []

        for match in self.compiled_email_pattern.finditer(text):
            email = match.group(0)
            entity = ExtractedEntity(
                type='person',
                value=email,
                confidence=0.95,
                start_pos=match.start(),
                end_pos=match.end(),
                original_text=email
            )
            entities.append(entity)

        return entities

    def _extract_locations(self, text: str) -> List[ExtractedEntity]:
        """Extract location entities from text"""
        entities = []

        for pattern in self.compiled_location_patterns:
            for match in pattern.finditer(text):
                location_text = match.group(1) if match.groups() else match.group(0)
                location_text = location_text.strip()

                if len(location_text) > 2:  # Filter out very short matches
                    entity = ExtractedEntity(
                        type='location',
                        value=location_text,
                        confidence=0.7,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        original_text=match.group(0)
                    )
                    entities.append(entity)

        return entities

    def _extract_meeting_title(self, text: str, action: str) -> Optional[str]:
        """Extract meeting title from text"""
        try:
            # Common patterns for meeting titles
            title_patterns = [
                r'(?:schedule|book|arrange)\s+(?:a\s+)?(?:meeting\s+)?(?:for\s+)?(.+?)(?:\s+with|\s+on|\s+at|$)',
                r'(?:meeting\s+)?(?:about|regarding|for)\s+(.+?)(?:\s+with|\s+on|\s+at|$)',
                r'(?:discuss|talk about|go over)\s+(.+?)(?:\s+with|\s+on|\s+at|$)',
                r'(.+?)\s+meeting(?:\s+with|\s+on|\s+at|$)',
            ]

            for pattern in title_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    # Clean up the title
                    title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
                    title = title.strip('.').strip(',').strip()

                    if len(title) > 3 and len(title) < 100:  # Reasonable title length
                        return title

            # Fallback: extract first meaningful phrase
            words = text.split()
            if len(words) > 2:
                # Try to find a noun phrase
                for i in range(len(words) - 1):
                    phrase = ' '.join(words[i:i+3])
                    if not any(word.lower() in ['schedule', 'book', 'arrange', 'meeting', 'with', 'on', 'at'] for word in phrase.split()):
                        return phrase

            return 'Meeting'  # Default title

        except Exception as e:
            logger.error(f"Error extracting meeting title: {e}")
            return 'Meeting'

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        try:
            date_text = date_text.lower().strip()

            # Handle relative dates
            if date_text == 'today':
                return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_text == 'tomorrow':
                return (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_text == 'yesterday':
                return (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

            # Handle "next/this day"
            weekday_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }

            for day_name, day_num in weekday_map.items():
                if day_name in date_text:
                    today = datetime.now()
                    days_ahead = day_num - today.weekday()

                    if 'next' in date_text:
                        if days_ahead <= 0:  # Target day has passed this week
                            days_ahead += 7
                    elif 'this' in date_text:
                        if days_ahead < 0:  # Target day has passed this week
                            days_ahead += 7

                    target_date = today + timedelta(days=days_ahead)
                    return target_date.replace(hour=0, minute=0, second=0, microsecond=0)

            # Handle absolute dates (simplified parsing)
            # This could be expanded with more sophisticated date parsing libraries
            date_patterns = [
                r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # MM/DD/YYYY
                r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})',  # YYYY/MM/DD
            ]

            for pattern in date_patterns:
                match = re.match(pattern, date_text)
                if match:
                    parts = [int(x) for x in match.groups()]
                    if len(parts) == 3:
                        # Assume first pattern is MM/DD/YYYY
                        if parts[2] > 1900:  # Year is last
                            return datetime(parts[2], parts[0], parts[1])
                        else:  # Year is first
                            return datetime(parts[0], parts[1], parts[2])

            return None

        except Exception as e:
            logger.error(f"Error parsing date '{date_text}': {e}")
            return None

    def _parse_time(self, time_text: str) -> Optional[dict]:
        """Parse time string to time information"""
        try:
            time_text = time_text.lower().strip()

            # Handle named times
            named_times = {
                'morning': 9,
                'afternoon': 14,
                'evening': 18,
                'night': 20,
                'noon': 12,
                'midnight': 0
            }

            for name, hour in named_times.items():
                if name in time_text:
                    return {'hour': hour, 'minute': 0}

            # Parse specific times
            # Pattern: HH:MM AM/PM
            pattern = r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?'
            match = re.search(pattern, time_text)

            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                period = match.group(3)

                # Convert to 24-hour format
                if period:
                    if period == 'pm' and hour != 12:
                        hour += 12
                    elif period == 'am' and hour == 12:
                        hour = 0

                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return {'hour': hour, 'minute': minute}

            return None

        except Exception as e:
            logger.error(f"Error parsing time '{time_text}': {e}")
            return None

    def _parse_duration(self, duration_text: str) -> Optional[int]:
        """Parse duration string to minutes"""
        try:
            duration_text = duration_text.lower().strip()

            # Extract numbers and units
            hour_match = re.search(r'(\d+)\s*(?:hour|hr)s?', duration_text)
            minute_match = re.search(r'(\d+)\s*(?:minute|min)s?', duration_text)

            total_minutes = 0

            if hour_match:
                total_minutes += int(hour_match.group(1)) * 60

            if minute_match:
                total_minutes += int(minute_match.group(1))

            # Handle HH:MM format
            time_match = re.search(r'(\d+):(\d+)', duration_text)
            if time_match and total_minutes == 0:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                total_minutes = hours * 60 + minutes

            return total_minutes if total_minutes > 0 else None

        except Exception as e:
            logger.error(f"Error parsing duration '{duration_text}': {e}")
            return None

    def combine_date_time(self, date_entity: ExtractedEntity,
                         time_entity: ExtractedEntity) -> Optional[datetime]:
        """Combine separate date and time entities into a single datetime"""
        try:
            if date_entity.type != 'date' or time_entity.type != 'time':
                return None

            date_value = date_entity.value
            time_value = time_entity.value

            if isinstance(date_value, datetime) and isinstance(time_value, dict):
                combined = date_value.replace(
                    hour=time_value['hour'],
                    minute=time_value['minute']
                )
                return combined

            return None

        except Exception as e:
            logger.error(f"Error combining date and time: {e}")
            return None

    def resolve_ambiguous_times(self, entities: List[ExtractedEntity]) -> List[datetime]:
        """Resolve ambiguous time references to specific datetimes"""
        resolved_times = []

        try:
            # Find date and time entities
            date_entities = [e for e in entities if e.type == 'date']
            time_entities = [e for e in entities if e.type == 'time']

            # If we have both dates and times, combine them
            if date_entities and time_entities:
                for date_entity in date_entities:
                    for time_entity in time_entities:
                        combined = self.combine_date_time(date_entity, time_entity)
                        if combined:
                            resolved_times.append(combined)

            # If we only have times, assume today or next business day
            elif time_entities and not date_entities:
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                for time_entity in time_entities:
                    if isinstance(time_entity.value, dict):
                        combined = today.replace(
                            hour=time_entity.value['hour'],
                            minute=time_entity.value['minute']
                        )
                        # If the time has passed today, assume tomorrow
                        if combined < datetime.now():
                            combined += timedelta(days=1)
                        resolved_times.append(combined)

            # If we only have dates, assume a default time (2 PM)
            elif date_entities and not time_entities:
                for date_entity in date_entities:
                    if isinstance(date_entity.value, datetime):
                        combined = date_entity.value.replace(hour=14, minute=0)
                        resolved_times.append(combined)

            return resolved_times

        except Exception as e:
            logger.error(f"Error resolving ambiguous times: {e}")
            return []