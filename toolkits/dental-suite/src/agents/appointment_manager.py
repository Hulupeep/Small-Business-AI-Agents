"""
Patient Appointment Manager Agent
Intelligent scheduling system for dental practices
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from langchain_openai import ChatOpenAI
import json

class AppointmentManager:
    """AI-powered appointment management for dental practices"""

    def __init__(self, llm: ChatOpenAI, practice_config: Dict[str, Any]):
        self.llm = llm
        self.practice_config = practice_config
        self.appointments = {}  # In production, this would be a database
        self.waitlist = []
        self.patient_preferences = {}

    def book_appointment(self, patient_id: str, treatment_type: str,
                        preferred_date: str, preferred_time: str) -> Dict[str, Any]:
        """Smart appointment booking with optimization"""

        # Get treatment duration from configuration
        treatment_durations = {
            'checkup': 30,
            'cleaning': 45,
            'filling': 60,
            'root_canal': 90,
            'crown': 120,
            'extraction': 45,
            'whitening': 60,
            'emergency': 30
        }

        duration = treatment_durations.get(treatment_type, 60)

        # Find optimal slot using AI
        optimal_slot = self._find_optimal_slot(
            treatment_type, preferred_date, preferred_time, duration
        )

        if optimal_slot:
            appointment_id = f"APT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            appointment = {
                'id': appointment_id,
                'patient_id': patient_id,
                'treatment_type': treatment_type,
                'date': optimal_slot['date'],
                'time': optimal_slot['time'],
                'duration': duration,
                'dentist': optimal_slot['dentist'],
                'status': 'confirmed',
                'created_at': datetime.now().isoformat()
            }

            self.appointments[appointment_id] = appointment

            # Schedule reminders
            self._schedule_reminders(appointment)

            return {
                'success': True,
                'appointment': appointment,
                'confirmation_number': appointment_id
            }
        else:
            # Add to waitlist
            self.waitlist.append({
                'patient_id': patient_id,
                'treatment_type': treatment_type,
                'preferred_date': preferred_date,
                'preferred_time': preferred_time,
                'created_at': datetime.now().isoformat()
            })

            return {
                'success': False,
                'message': 'No available slots found. Added to waitlist.',
                'waitlist_position': len(self.waitlist)
            }

    def _find_optimal_slot(self, treatment_type: str, preferred_date: str,
                          preferred_time: str, duration: int) -> Optional[Dict[str, Any]]:
        """AI-powered slot optimization"""

        # Simulate finding available slots
        # In production, this would query the actual schedule database
        available_slots = [
            {'date': preferred_date, 'time': '09:00', 'dentist': 'Dr. Smith'},
            {'date': preferred_date, 'time': '14:30', 'dentist': 'Dr. Jones'},
            {'date': preferred_date, 'time': '16:00', 'dentist': 'Dr. Brown'}
        ]

        # AI scoring system for optimal slot selection
        best_slot = None
        best_score = 0

        for slot in available_slots:
            score = self._calculate_slot_score(
                slot, treatment_type, preferred_time, duration
            )
            if score > best_score:
                best_score = score
                best_slot = slot

        return best_slot

    def _calculate_slot_score(self, slot: Dict[str, Any], treatment_type: str,
                             preferred_time: str, duration: int) -> float:
        """Calculate optimization score for appointment slot"""

        score = 0.0

        # Time preference matching
        if slot['time'] == preferred_time:
            score += 50
        elif abs(self._time_to_minutes(slot['time']) -
                self._time_to_minutes(preferred_time)) <= 60:
            score += 30

        # Treatment type optimization
        treatment_scores = {
            'emergency': 100,  # Highest priority
            'checkup': 20,
            'cleaning': 25,
            'filling': 40,
            'root_canal': 60,
            'crown': 70
        }
        score += treatment_scores.get(treatment_type, 30)

        # Dentist specialization matching
        dentist_specializations = {
            'Dr. Smith': ['general', 'checkup', 'cleaning'],
            'Dr. Jones': ['surgery', 'extraction', 'root_canal'],
            'Dr. Brown': ['cosmetic', 'crown', 'whitening']
        }

        if treatment_type in dentist_specializations.get(slot['dentist'], []):
            score += 25

        return score

    def _time_to_minutes(self, time_str: str) -> int:
        """Convert time string to minutes since midnight"""
        hour, minute = map(int, time_str.split(':'))
        return hour * 60 + minute

    def _schedule_reminders(self, appointment: Dict[str, Any]) -> None:
        """Schedule appointment reminders"""

        reminder_schedule = [
            {'days_before': 7, 'method': 'email'},
            {'days_before': 1, 'method': 'sms'},
            {'hours_before': 2, 'method': 'voice_call'}
        ]

        for reminder in reminder_schedule:
            # In production, this would integrate with SMS/email services
            print(f"Scheduled {reminder['method']} reminder for {appointment['id']}")

    def handle_cancellation(self, appointment_id: str, reason: str = None) -> Dict[str, Any]:
        """Handle appointment cancellation and optimize waitlist"""

        if appointment_id not in self.appointments:
            return {'success': False, 'error': 'Appointment not found'}

        appointment = self.appointments[appointment_id]
        appointment['status'] = 'cancelled'
        appointment['cancellation_reason'] = reason
        appointment['cancelled_at'] = datetime.now().isoformat()

        # Try to fill slot from waitlist
        filled_from_waitlist = self._fill_from_waitlist(appointment)

        return {
            'success': True,
            'appointment_cancelled': appointment_id,
            'waitlist_filled': filled_from_waitlist
        }

    def _fill_from_waitlist(self, cancelled_appointment: Dict[str, Any]) -> bool:
        """Try to fill cancelled slot from waitlist"""

        for i, waitlist_item in enumerate(self.waitlist):
            if (waitlist_item['treatment_type'] == cancelled_appointment['treatment_type'] or
                cancelled_appointment['treatment_type'] == 'emergency'):

                # Book appointment for waitlist patient
                self.waitlist.pop(i)

                new_appointment = {
                    'id': f"APT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'patient_id': waitlist_item['patient_id'],
                    'treatment_type': waitlist_item['treatment_type'],
                    'date': cancelled_appointment['date'],
                    'time': cancelled_appointment['time'],
                    'duration': cancelled_appointment['duration'],
                    'dentist': cancelled_appointment['dentist'],
                    'status': 'confirmed',
                    'created_at': datetime.now().isoformat(),
                    'filled_from_waitlist': True
                }

                self.appointments[new_appointment['id']] = new_appointment

                # Send notification to patient
                print(f"Notified patient {waitlist_item['patient_id']} of available slot")
                return True

        return False

    def get_emergency_slots(self, date: str = None) -> List[Dict[str, Any]]:
        """Get available emergency appointment slots"""

        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        # Emergency slots are always reserved in the schedule
        emergency_slots = [
            {'date': date, 'time': '08:00', 'dentist': 'Dr. Smith', 'available': True},
            {'date': date, 'time': '13:00', 'dentist': 'Dr. Jones', 'available': True}
        ]

        return [slot for slot in emergency_slots if slot['available']]

    def schedule_recall(self, patient_id: str, last_visit_date: str) -> Dict[str, Any]:
        """Schedule 6-month recall appointment"""

        # Calculate recall date (6 months from last visit)
        last_visit = datetime.strptime(last_visit_date, '%Y-%m-%d')
        recall_date = last_visit + timedelta(days=180)  # 6 months

        # Get patient preferences
        preferences = self.patient_preferences.get(patient_id, {})
        preferred_time = preferences.get('preferred_time', '10:00')
        preferred_day = preferences.get('preferred_day', 'tuesday')

        # Find suitable recall slot
        return self.book_appointment(
            patient_id=patient_id,
            treatment_type='checkup',
            preferred_date=recall_date.strftime('%Y-%m-%d'),
            preferred_time=preferred_time
        )

def create_appointment_manager_agent(llm: ChatOpenAI, practice_config: Dict[str, Any]) -> AgentExecutor:
    """Create the appointment manager agent with tools"""

    manager = AppointmentManager(llm, practice_config)

    tools = [
        Tool(
            name="book_appointment",
            description="Book a new appointment for a patient",
            func=lambda query: manager.book_appointment(**json.loads(query))
        ),
        Tool(
            name="handle_cancellation",
            description="Cancel an appointment and manage waitlist",
            func=lambda query: manager.handle_cancellation(**json.loads(query))
        ),
        Tool(
            name="get_emergency_slots",
            description="Get available emergency appointment slots",
            func=manager.get_emergency_slots
        ),
        Tool(
            name="schedule_recall",
            description="Schedule 6-month recall appointment",
            func=lambda query: manager.schedule_recall(**json.loads(query))
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI appointment manager for a dental practice.
        You help patients book appointments, handle cancellations, manage waitlists,
        and schedule recall visits. Always prioritize emergency cases and optimize
        the schedule for maximum efficiency.

        Practice Configuration:
        - Dentists: {dentists}
        - Operating Hours: {operating_hours}
        - Emergency Slots: {emergency_slots}

        Be helpful, professional, and efficient in your responses."""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)