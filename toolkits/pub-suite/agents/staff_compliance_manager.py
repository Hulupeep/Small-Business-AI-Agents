"""
Staff Rota & Compliance Manager Agent
Ensures proper staffing, training, and regulatory compliance for pub operations
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class StaffRole(Enum):
    MANAGER = "manager"
    BARTENDER = "bartender"
    SERVER = "server"
    KITCHEN_STAFF = "kitchen_staff"
    SECURITY = "security"
    CLEANER = "cleaner"

class ShiftType(Enum):
    MORNING = "morning"      # 11:00-15:00
    AFTERNOON = "afternoon"  # 15:00-19:00
    EVENING = "evening"      # 19:00-23:00
    LATE = "late"           # 23:00-02:00
    FULL_DAY = "full_day"   # 11:00-23:00

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"
    EXPIRED = "expired"

@dataclass
class StaffMember:
    staff_id: str
    name: str
    role: StaffRole
    phone: str
    email: str
    date_of_birth: datetime
    start_date: datetime
    hourly_rate: float
    max_hours_per_week: int = 40
    availability: Dict[str, List[str]] = field(default_factory=dict)  # day: [shift_types]
    certifications: Dict[str, datetime] = field(default_factory=dict)  # cert_name: expiry_date
    performance_rating: float = 8.0
    active: bool = True

@dataclass
class Shift:
    shift_id: str
    date: datetime
    shift_type: ShiftType
    role_required: StaffRole
    staff_assigned: Optional[str] = None
    start_time: datetime = None
    end_time: datetime = None
    hourly_rate: float = 0.0
    special_requirements: List[str] = field(default_factory=list)

@dataclass
class ComplianceItem:
    item_id: str
    category: str
    description: str
    required_for_roles: List[StaffRole]
    renewal_period_days: int
    staff_id: str
    issue_date: datetime
    expiry_date: datetime
    status: ComplianceStatus

class StaffComplianceManager:
    """AI agent for staff scheduling and compliance management"""

    def __init__(self, pub_config: Dict):
        self.pub_config = pub_config
        self.staff_members: Dict[str, StaffMember] = {}
        self.shifts: Dict[str, Shift] = {}
        self.compliance_items: Dict[str, ComplianceItem] = {}
        self.demand_predictor = DemandPredictor()
        self.compliance_tracker = ComplianceTracker()

    async def smart_staff_scheduling(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate optimal staff schedule based on predicted demand"""

        schedule = {}
        total_scheduled_hours = 0
        total_labor_cost = 0

        current_date = start_date
        while current_date <= end_date:
            daily_schedule = await self._schedule_daily_shifts(current_date)
            schedule[current_date.strftime('%Y-%m-%d')] = daily_schedule

            # Calculate daily totals
            for shift in daily_schedule:
                if shift['staff_assigned']:
                    shift_hours = shift['duration_hours']
                    total_scheduled_hours += shift_hours
                    total_labor_cost += shift_hours * shift['hourly_rate']

            current_date += timedelta(days=1)

        # Check for scheduling conflicts and gaps
        conflicts = await self._detect_scheduling_conflicts(schedule)
        coverage_gaps = await self._identify_coverage_gaps(schedule)

        return {
            'schedule': schedule,
            'total_scheduled_hours': total_scheduled_hours,
            'total_labor_cost': total_labor_cost,
            'scheduling_conflicts': conflicts,
            'coverage_gaps': coverage_gaps,
            'optimization_suggestions': await self._generate_schedule_optimizations(schedule)
        }

    async def manage_training_certifications(self) -> Dict:
        """Track and manage staff training and certifications"""

        training_status = {}
        renewal_alerts = []
        training_needs = []

        for staff_id, staff in self.staff_members.items():
            if not staff.active:
                continue

            # Check required certifications for role
            required_certs = await self._get_required_certifications(staff.role)

            staff_cert_status = {}
            for cert_name in required_certs:
                cert_status = await self._check_certification_status(staff_id, cert_name)
                staff_cert_status[cert_name] = cert_status

                # Check for upcoming renewals (within 30 days)
                if cert_status['status'] == 'expiring_soon':
                    renewal_alerts.append({
                        'staff_id': staff_id,
                        'staff_name': staff.name,
                        'certification': cert_name,
                        'expiry_date': cert_status['expiry_date'],
                        'days_until_expiry': cert_status['days_until_expiry']
                    })

                # Check for missing or expired certifications
                elif cert_status['status'] in ['missing', 'expired']:
                    training_needs.append({
                        'staff_id': staff_id,
                        'staff_name': staff.name,
                        'certification': cert_name,
                        'urgency': 'high' if cert_status['status'] == 'expired' else 'medium',
                        'estimated_cost': cert_status['training_cost']
                    })

            training_status[staff_id] = {
                'name': staff.name,
                'role': staff.role.value,
                'certifications': staff_cert_status,
                'overall_compliance': await self._calculate_compliance_score(staff_cert_status)
            }

        return {
            'training_status': training_status,
            'renewal_alerts': renewal_alerts,
            'training_needs': training_needs,
            'compliance_summary': await self._generate_compliance_summary(),
            'training_budget_estimate': sum(item['estimated_cost'] for item in training_needs)
        }

    async def age_verification_protocols(self) -> Dict:
        """Manage age verification protocols and reminders"""

        protocols = {
            'id_checking_policy': {
                'challenge_25_policy': True,
                'acceptable_id_types': [
                    'Driving Licence',
                    'Passport',
                    'National Age Card',
                    'Garda Age Card'
                ],
                'verification_steps': [
                    'Check photo matches person',
                    'Verify date of birth',
                    'Check for tampering',
                    'When in doubt, refuse sale'
                ]
            },
            'staff_reminders': await self._generate_age_verification_reminders(),
            'refusal_procedures': {
                'polite_explanation': 'Required by law to check ID for anyone who appears under 25',
                'escalation_to_manager': True,
                'incident_recording': True
            },
            'training_requirements': await self._get_age_verification_training_needs()
        }

        # Generate daily briefing for staff
        daily_briefing = await self._create_daily_age_verification_briefing()

        return {
            'protocols': protocols,
            'daily_briefing': daily_briefing,
            'recent_incidents': await self._get_recent_age_verification_incidents(),
            'compliance_score': await self._calculate_age_verification_compliance()
        }

    async def closing_time_procedures(self) -> Dict:
        """Manage closing time procedures and security protocols"""

        current_time = datetime.now()
        pub_hours = self.pub_config.get('operating_hours', {})
        day_name = current_time.strftime('%A').lower()

        closing_time = await self._determine_closing_time(day_name, current_time)
        time_until_close = (closing_time - current_time).total_seconds() / 60  # minutes

        # Generate closing procedures checklist
        procedures = await self._generate_closing_procedures(time_until_close)

        # Security protocols
        security_protocols = {
            'cash_handling': [
                'Count till contents',
                'Complete cash reconciliation',
                'Store cash in safe',
                'Record any discrepancies'
            ],
            'premises_security': [
                'Check all doors and windows',
                'Set alarm system',
                'Ensure beer garden is secure',
                'Lock cellar and stock areas'
            ],
            'cleaning_checklist': [
                'Clean and sanitize bar area',
                'Empty bins and replace liners',
                'Clean toilets',
                'Mop floors',
                'Stack chairs and clean tables'
            ],
            'equipment_shutdown': [
                'Turn off taps and check lines',
                'Switch off kitchen equipment',
                'Turn off music system',
                'Dim lights but leave security lighting'
            ]
        }

        return {
            'closing_time': closing_time,
            'time_until_close': time_until_close,
            'closing_procedures': procedures,
            'security_protocols': security_protocols,
            'staff_assignments': await self._assign_closing_duties(),
            'manager_final_checks': await self._generate_manager_checklist()
        }

    async def compliance_monitoring(self) -> Dict:
        """Monitor regulatory compliance across all areas"""

        compliance_areas = {
            'licensing': await self._check_licensing_compliance(),
            'health_safety': await self._check_health_safety_compliance(),
            'employment_law': await self._check_employment_compliance(),
            'data_protection': await self._check_data_protection_compliance(),
            'fire_safety': await self._check_fire_safety_compliance()
        }

        # Calculate overall compliance score
        overall_score = await self._calculate_overall_compliance_score(compliance_areas)

        # Generate compliance report
        compliance_report = {
            'overall_score': overall_score,
            'compliance_areas': compliance_areas,
            'critical_issues': await self._identify_critical_compliance_issues(compliance_areas),
            'improvement_recommendations': await self._generate_compliance_recommendations(compliance_areas),
            'next_inspection_dates': await self._get_upcoming_inspections()
        }

        return compliance_report

    async def _schedule_daily_shifts(self, date: datetime) -> List[Dict]:
        """Schedule shifts for a specific day"""

        day_name = date.strftime('%A').lower()
        predicted_demand = await self.demand_predictor.predict_daily_demand(date)

        # Determine required staffing levels
        required_staff = await self._calculate_required_staffing(predicted_demand, day_name)

        daily_shifts = []

        # Create shifts based on requirements
        for shift_type, roles_needed in required_staff.items():
            for role, count in roles_needed.items():
                for i in range(count):
                    shift_times = await self._get_shift_times(shift_type, date)

                    shift = {
                        'shift_id': f"{date.strftime('%Y%m%d')}_{shift_type}_{role}_{i+1}",
                        'date': date,
                        'shift_type': shift_type,
                        'role_required': role,
                        'start_time': shift_times['start'],
                        'end_time': shift_times['end'],
                        'duration_hours': shift_times['duration'],
                        'staff_assigned': await self._assign_best_staff(
                            role, shift_times['start'], shift_times['end'], date
                        ),
                        'hourly_rate': 0.0,
                        'special_requirements': []
                    }

                    # Set hourly rate if staff assigned
                    if shift['staff_assigned']:
                        staff = self.staff_members.get(shift['staff_assigned'])
                        if staff:
                            shift['hourly_rate'] = staff.hourly_rate

                    daily_shifts.append(shift)

        return daily_shifts

    async def _get_required_certifications(self, role: StaffRole) -> List[str]:
        """Get required certifications for staff role"""

        certification_requirements = {
            StaffRole.MANAGER: [
                'Personal Licence Holder',
                'Food Safety Level 3',
                'First Aid',
                'Fire Safety'
            ],
            StaffRole.BARTENDER: [
                'Responsible Service of Alcohol',
                'Food Safety Level 2'
            ],
            StaffRole.SERVER: [
                'Food Safety Level 2',
                'Responsible Service of Alcohol'
            ],
            StaffRole.KITCHEN_STAFF: [
                'Food Safety Level 2',
                'HACCP'
            ],
            StaffRole.SECURITY: [
                'PSA Security Licence',
                'Conflict Resolution Training'
            ],
            StaffRole.CLEANER: [
                'COSHH Training'
            ]
        }

        return certification_requirements.get(role, [])

    async def _check_certification_status(self, staff_id: str, cert_name: str) -> Dict:
        """Check certification status for staff member"""

        staff = self.staff_members.get(staff_id)
        if not staff:
            return {'status': 'staff_not_found'}

        cert_expiry = staff.certifications.get(cert_name)

        if not cert_expiry:
            return {
                'status': 'missing',
                'message': f'{cert_name} certification not found',
                'training_cost': await self._get_training_cost(cert_name)
            }

        current_date = datetime.now()
        days_until_expiry = (cert_expiry - current_date).days

        if days_until_expiry < 0:
            return {
                'status': 'expired',
                'expiry_date': cert_expiry,
                'days_overdue': abs(days_until_expiry),
                'training_cost': await self._get_training_cost(cert_name)
            }
        elif days_until_expiry <= 30:
            return {
                'status': 'expiring_soon',
                'expiry_date': cert_expiry,
                'days_until_expiry': days_until_expiry,
                'renewal_cost': await self._get_renewal_cost(cert_name)
            }
        else:
            return {
                'status': 'valid',
                'expiry_date': cert_expiry,
                'days_until_expiry': days_until_expiry
            }

    async def _determine_closing_time(self, day_name: str, current_time: datetime) -> datetime:
        """Determine closing time based on licence and day of week"""

        standard_hours = {
            'monday': '23:00',
            'tuesday': '23:00',
            'wednesday': '23:00',
            'thursday': '23:30',
            'friday': '01:00',
            'saturday': '01:00',
            'sunday': '23:00'
        }

        # Check for special events that might extend hours
        special_events = await self._check_special_event_extensions(current_time.date())

        base_closing = standard_hours.get(day_name, '23:00')
        closing_hour, closing_minute = map(int, base_closing.split(':'))

        closing_time = current_time.replace(
            hour=closing_hour,
            minute=closing_minute,
            second=0,
            microsecond=0
        )

        # Handle next day closing times
        if closing_hour < 12:  # Next day closing
            closing_time += timedelta(days=1)

        # Apply special event extensions
        if special_events:
            for event in special_events:
                if event.get('extended_hours'):
                    extension = timedelta(hours=event['extended_hours'])
                    closing_time += extension

        return closing_time

    async def record_incident(self, incident_data: Dict) -> Dict:
        """Record compliance or safety incident"""

        incident_id = f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        incident = {
            'incident_id': incident_id,
            'timestamp': datetime.now(),
            'type': incident_data.get('type', 'general'),
            'description': incident_data.get('description', ''),
            'staff_involved': incident_data.get('staff_involved', []),
            'customers_involved': incident_data.get('customers_involved', []),
            'action_taken': incident_data.get('action_taken', ''),
            'follow_up_required': incident_data.get('follow_up_required', False),
            'reported_by': incident_data.get('reported_by', ''),
            'severity': incident_data.get('severity', 'low')
        }

        # Store incident (in real implementation, this would go to database)

        # Trigger any required notifications
        notifications = await self._trigger_incident_notifications(incident)

        return {
            'incident_id': incident_id,
            'recorded': True,
            'notifications_sent': notifications,
            'follow_up_actions': await self._generate_follow_up_actions(incident)
        }


class DemandPredictor:
    """Predicts staffing demand based on various factors"""

    async def predict_daily_demand(self, date: datetime) -> Dict:
        """Predict customer demand for specific date"""

        base_demand = await self._get_base_demand(date.weekday())

        # Adjust for special factors
        weather_factor = await self._get_weather_impact(date)
        event_factor = await self._get_event_impact(date)
        seasonal_factor = await self._get_seasonal_factor(date)

        total_demand = base_demand * weather_factor * event_factor * seasonal_factor

        return {
            'date': date,
            'base_demand': base_demand,
            'weather_factor': weather_factor,
            'event_factor': event_factor,
            'seasonal_factor': seasonal_factor,
            'predicted_customers': int(total_demand),
            'confidence': 0.85  # Prediction confidence
        }

    async def _get_base_demand(self, weekday: int) -> float:
        """Get base demand by day of week"""
        # Monday=0, Sunday=6
        base_demands = [60, 65, 70, 85, 120, 150, 140]  # Mon-Sun
        return base_demands[weekday]


class ComplianceTracker:
    """Tracks compliance across various regulatory areas"""

    async def check_licence_compliance(self) -> Dict:
        """Check pub licence compliance"""

        return {
            'premises_licence': {
                'status': 'valid',
                'expiry_date': datetime(2024, 12, 31),
                'renewal_required': False
            },
            'personal_licence': {
                'status': 'valid',
                'holder': 'Manager Name',
                'expiry_date': datetime(2026, 6, 15)
            },
            'music_licence': {
                'status': 'valid',
                'prs_ppl_licence': True,
                'live_music_permitted': True
            }
        }


# Example usage and testing
if __name__ == "__main__":

    pub_config = {
        'operating_hours': {
            'monday': {'open': '11:00', 'close': '23:00'},
            'friday': {'open': '11:00', 'close': '01:00'},
            'saturday': {'open': '11:00', 'close': '01:00'},
            'sunday': {'open': '12:00', 'close': '23:00'}
        },
        'auto_order_limit': 200
    }

    async def test_manager():
        manager = StaffComplianceManager(pub_config)

        # Add sample staff member
        staff = StaffMember(
            staff_id='STAFF001',
            name='John Doe',
            role=StaffRole.BARTENDER,
            phone='+353 87 123 4567',
            email='john@example.ie',
            date_of_birth=datetime(1990, 5, 15),
            start_date=datetime(2022, 1, 1),
            hourly_rate=14.50,
            certifications={
                'Responsible Service of Alcohol': datetime(2024, 12, 31),
                'Food Safety Level 2': datetime(2024, 6, 30)
            }
        )
        manager.staff_members['STAFF001'] = staff

        # Test staff scheduling
        schedule_result = await manager.smart_staff_scheduling(
            datetime.now(),
            datetime.now() + timedelta(days=7)
        )
        print("Schedule result:", json.dumps(schedule_result, indent=2, default=str))

        # Test training management
        training_result = await manager.manage_training_certifications()
        print("Training status:", json.dumps(training_result, indent=2, default=str))

        # Test compliance monitoring
        compliance_result = await manager.compliance_monitoring()
        print("Compliance status:", json.dumps(compliance_result, indent=2, default=str))

    # Run test
    asyncio.run(test_manager())