"""
Practice Management Hub Agent
Comprehensive practice workflow automation and staff management
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class StaffRole(Enum):
    PARTNER = "partner"
    MANAGER = "manager"
    SENIOR_ACCOUNTANT = "senior_accountant"
    ACCOUNTANT = "accountant"
    JUNIOR_ACCOUNTANT = "junior_accountant"
    ADMIN = "admin"

class ClientTier(Enum):
    PREMIUM = "premium"
    STANDARD = "standard"
    BASIC = "basic"

@dataclass
class Task:
    id: str
    client_id: str
    description: str
    assigned_to: str
    created_by: str
    due_date: datetime.date
    estimated_hours: float
    actual_hours: float = 0.0
    status: TaskStatus = TaskStatus.PENDING
    priority: str = "medium"
    task_type: str = "general"
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    completed_at: Optional[datetime.datetime] = None

@dataclass
class StaffMember:
    id: str
    name: str
    email: str
    role: StaffRole
    hourly_rate: float
    capacity_hours: float  # Weekly capacity
    specializations: List[str]
    current_workload: float = 0.0
    efficiency_rating: float = 1.0
    quality_score: float = 100.0
    active: bool = True

@dataclass
class Client:
    id: str
    name: str
    entity_type: str
    tier: ClientTier
    year_end: datetime.date
    billing_rate: float
    total_annual_fee: float
    contact_person: str
    email: str
    phone: str
    address: str
    last_contact: Optional[datetime.date] = None
    satisfaction_score: float = 100.0

@dataclass
class TimeEntry:
    id: str
    staff_id: str
    client_id: str
    task_id: str
    date: datetime.date
    hours: float
    description: str
    billable: bool = True
    rate: float = 0.0
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)

class PracticeManagementHub:
    """
    Complete practice management system for Irish accounting firms
    Handles workflow automation, staff management, and client relationships
    """

    def __init__(self):
        self.staff_members: Dict[str, StaffMember] = {}
        self.clients: Dict[str, Client] = {}
        self.tasks: Dict[str, Task] = {}
        self.time_entries: List[TimeEntry] = []

        # Irish accounting standards and deadlines
        self.standard_task_types = {
            'form_11_preparation': {'estimated_hours': 4, 'requires_role': 'accountant'},
            'corporation_tax_return': {'estimated_hours': 6, 'requires_role': 'senior_accountant'},
            'vat_return': {'estimated_hours': 2, 'requires_role': 'accountant'},
            'annual_accounts': {'estimated_hours': 12, 'requires_role': 'senior_accountant'},
            'management_accounts': {'estimated_hours': 8, 'requires_role': 'accountant'},
            'payroll_processing': {'estimated_hours': 3, 'requires_role': 'accountant'},
            'client_meeting': {'estimated_hours': 2, 'requires_role': 'manager'},
            'audit_preparation': {'estimated_hours': 20, 'requires_role': 'partner'}
        }

        # Peak season configurations (October-November)
        self.peak_season_multipliers = {
            'october': 1.4,
            'november': 1.6,
            'december': 1.2
        }

    def add_staff_member(self, staff_data: Dict) -> str:
        """Add new staff member to the practice"""

        staff_id = str(uuid.uuid4())[:8]

        staff_member = StaffMember(
            id=staff_id,
            name=staff_data['name'],
            email=staff_data['email'],
            role=StaffRole(staff_data['role']),
            hourly_rate=staff_data['hourly_rate'],
            capacity_hours=staff_data.get('capacity_hours', 40),
            specializations=staff_data.get('specializations', [])
        )

        self.staff_members[staff_id] = staff_member
        return staff_id

    def add_client(self, client_data: Dict) -> str:
        """Add new client to the practice"""

        client_id = str(uuid.uuid4())[:8]

        client = Client(
            id=client_id,
            name=client_data['name'],
            entity_type=client_data['entity_type'],
            tier=ClientTier(client_data.get('tier', 'standard')),
            year_end=client_data['year_end'],
            billing_rate=client_data['billing_rate'],
            total_annual_fee=client_data['total_annual_fee'],
            contact_person=client_data['contact_person'],
            email=client_data['email'],
            phone=client_data['phone'],
            address=client_data['address']
        )

        self.clients[client_id] = client
        return client_id

    def create_task(self, task_data: Dict) -> str:
        """Create new task with automatic assignment"""

        task_id = str(uuid.uuid4())[:8]

        # Get task configuration
        task_config = self.standard_task_types.get(
            task_data['task_type'],
            {'estimated_hours': 4, 'requires_role': 'accountant'}
        )

        # Auto-assign to best available staff member
        assigned_staff = self._auto_assign_task(
            task_data['task_type'],
            task_config['requires_role'],
            task_data['due_date']
        )

        task = Task(
            id=task_id,
            client_id=task_data['client_id'],
            description=task_data['description'],
            assigned_to=assigned_staff,
            created_by=task_data['created_by'],
            due_date=task_data['due_date'],
            estimated_hours=task_config['estimated_hours'],
            task_type=task_data['task_type'],
            priority=task_data.get('priority', 'medium')
        )

        self.tasks[task_id] = task

        # Update staff workload
        if assigned_staff in self.staff_members:
            self.staff_members[assigned_staff].current_workload += task.estimated_hours

        return task_id

    def _auto_assign_task(self, task_type: str, required_role: str, due_date: datetime.date) -> str:
        """Automatically assign task to best available staff member"""

        # Filter staff by role capability
        eligible_staff = []
        role_hierarchy = {
            'partner': 5,
            'manager': 4,
            'senior_accountant': 3,
            'accountant': 2,
            'junior_accountant': 1,
            'admin': 0
        }

        required_level = role_hierarchy.get(required_role, 0)

        for staff_id, staff in self.staff_members.items():
            if not staff.active:
                continue

            staff_level = role_hierarchy.get(staff.role.value, 0)
            if staff_level >= required_level:
                eligible_staff.append(staff)

        if not eligible_staff:
            # Return first available staff if no match
            return list(self.staff_members.keys())[0] if self.staff_members else ""

        # Score staff members based on workload, efficiency, and specialization
        best_staff = None
        best_score = float('inf')

        for staff in eligible_staff:
            # Calculate availability score (lower is better)
            workload_score = staff.current_workload / staff.capacity_hours
            efficiency_score = 1 / max(staff.efficiency_rating, 0.1)
            quality_score = (100 - staff.quality_score) / 100

            # Bonus for specialization
            specialization_bonus = 0
            if task_type in staff.specializations:
                specialization_bonus = -0.2  # Reduce score (better)

            total_score = workload_score + efficiency_score + quality_score + specialization_bonus

            if total_score < best_score:
                best_score = total_score
                best_staff = staff

        return best_staff.id if best_staff else ""

    def create_annual_workflow(self, client_id: str) -> List[str]:
        """Create complete annual workflow for a client"""

        if client_id not in self.clients:
            return []

        client = self.clients[client_id]
        year_end = client.year_end
        current_year = datetime.date.today().year

        # Calculate key dates
        accounts_due = year_end + datetime.timedelta(days=275)  # 9 months for limited companies
        tax_due = year_end + datetime.timedelta(days=275)
        annual_return_due = datetime.date(current_year, 11, 30)  # CRO deadline

        tasks_created = []

        if client.entity_type == 'limited_company':
            # Corporation tax return
            ct_task_id = self.create_task({
                'client_id': client_id,
                'description': f'Corporation Tax Return for {client.name}',
                'task_type': 'corporation_tax_return',
                'due_date': tax_due,
                'created_by': 'system',
                'priority': 'high'
            })
            tasks_created.append(ct_task_id)

            # Annual accounts preparation
            accounts_task_id = self.create_task({
                'client_id': client_id,
                'description': f'Annual Accounts for {client.name}',
                'task_type': 'annual_accounts',
                'due_date': accounts_due,
                'created_by': 'system',
                'priority': 'high'
            })
            tasks_created.append(accounts_task_id)

            # CRO Annual Return
            cro_task_id = self.create_task({
                'client_id': client_id,
                'description': f'CRO Annual Return for {client.name}',
                'task_type': 'annual_return',
                'due_date': annual_return_due,
                'created_by': 'system',
                'priority': 'medium'
            })
            tasks_created.append(cro_task_id)

        elif client.entity_type == 'sole_trader':
            # Form 11 preparation
            form11_due = datetime.date(current_year, 10, 31)
            form11_task_id = self.create_task({
                'client_id': client_id,
                'description': f'Form 11 Preparation for {client.name}',
                'task_type': 'form_11_preparation',
                'due_date': form11_due,
                'created_by': 'system',
                'priority': 'high'
            })
            tasks_created.append(form11_task_id)

        # Monthly VAT returns (if VAT registered)
        # This would check client VAT registration status
        vat_registered = True  # Placeholder
        if vat_registered:
            for month in range(1, 13):
                vat_due = datetime.date(current_year, month, 19)
                if vat_due > datetime.date.today():
                    vat_task_id = self.create_task({
                        'client_id': client_id,
                        'description': f'VAT Return {month:02d}/{current_year} for {client.name}',
                        'task_type': 'vat_return',
                        'due_date': vat_due,
                        'created_by': 'system',
                        'priority': 'medium'
                    })
                    tasks_created.append(vat_task_id)

        return tasks_created

    def get_staff_workload_analysis(self) -> Dict:
        """Analyze current staff workload and capacity"""

        analysis = {
            'total_staff': len(self.staff_members),
            'total_capacity': 0,
            'total_workload': 0,
            'utilization_rate': 0,
            'staff_details': [],
            'overloaded_staff': [],
            'available_capacity': 0
        }

        for staff_id, staff in self.staff_members.items():
            if not staff.active:
                continue

            utilization = (staff.current_workload / staff.capacity_hours) * 100

            staff_detail = {
                'id': staff_id,
                'name': staff.name,
                'role': staff.role.value,
                'capacity': staff.capacity_hours,
                'workload': staff.current_workload,
                'utilization': utilization,
                'efficiency': staff.efficiency_rating,
                'quality_score': staff.quality_score
            }

            analysis['staff_details'].append(staff_detail)
            analysis['total_capacity'] += staff.capacity_hours
            analysis['total_workload'] += staff.current_workload

            if utilization > 100:
                analysis['overloaded_staff'].append(staff_detail)

        if analysis['total_capacity'] > 0:
            analysis['utilization_rate'] = (analysis['total_workload'] / analysis['total_capacity']) * 100
            analysis['available_capacity'] = analysis['total_capacity'] - analysis['total_workload']

        return analysis

    def get_peak_season_planning(self) -> Dict:
        """Generate peak season (Oct-Nov) capacity planning"""

        current_workload = self.get_staff_workload_analysis()
        current_month = datetime.date.today().month

        peak_planning = {
            'current_utilization': current_workload['utilization_rate'],
            'peak_months': ['october', 'november'],
            'additional_capacity_needed': 0,
            'recommended_actions': [],
            'temporary_staff_needed': 0,
            'overtime_projections': {}
        }

        # Check if we're in or approaching peak season
        if current_month in [9, 10, 11]:  # Sept, Oct, Nov
            month_name = datetime.date.today().strftime('%B').lower()
            multiplier = self.peak_season_multipliers.get(month_name, 1.0)

            projected_workload = current_workload['total_workload'] * multiplier
            capacity_shortfall = projected_workload - current_workload['total_capacity']

            if capacity_shortfall > 0:
                peak_planning['additional_capacity_needed'] = capacity_shortfall
                peak_planning['temporary_staff_needed'] = capacity_shortfall / 40  # Assuming 40hr/week

                peak_planning['recommended_actions'] = [
                    f"Hire {int(capacity_shortfall / 40) + 1} temporary staff members",
                    "Implement overtime scheduling for existing staff",
                    "Prioritize high-value clients",
                    "Consider extending some deadlines where possible",
                    "Increase automation usage"
                ]

        return peak_planning

    def log_time_entry(self, time_data: Dict) -> str:
        """Log time entry for billing and tracking"""

        entry_id = str(uuid.uuid4())[:8]

        # Get staff billing rate
        staff = self.staff_members.get(time_data['staff_id'])
        billing_rate = staff.hourly_rate if staff else 0

        # Get client billing rate (may override staff rate)
        client = self.clients.get(time_data['client_id'])
        if client:
            billing_rate = client.billing_rate

        time_entry = TimeEntry(
            id=entry_id,
            staff_id=time_data['staff_id'],
            client_id=time_data['client_id'],
            task_id=time_data['task_id'],
            date=time_data['date'],
            hours=time_data['hours'],
            description=time_data['description'],
            billable=time_data.get('billable', True),
            rate=billing_rate
        )

        self.time_entries.append(time_entry)

        # Update task progress
        if time_data['task_id'] in self.tasks:
            task = self.tasks[time_data['task_id']]
            task.actual_hours += time_data['hours']

            # Auto-complete task if hours exceed estimate significantly
            if task.actual_hours >= task.estimated_hours and task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.datetime.now()

        return entry_id

    def generate_billing_report(self, client_id: str, period_start: datetime.date,
                               period_end: datetime.date) -> Dict:
        """Generate client billing report"""

        client = self.clients.get(client_id)
        if not client:
            return {}

        # Filter time entries for this client and period
        relevant_entries = [
            entry for entry in self.time_entries
            if (entry.client_id == client_id and
                period_start <= entry.date <= period_end and
                entry.billable)
        ]

        # Calculate totals
        total_hours = sum(entry.hours for entry in relevant_entries)
        total_amount = sum(entry.hours * entry.rate for entry in relevant_entries)

        # Group by staff member
        staff_breakdown = {}
        for entry in relevant_entries:
            staff = self.staff_members.get(entry.staff_id)
            staff_name = staff.name if staff else "Unknown"

            if staff_name not in staff_breakdown:
                staff_breakdown[staff_name] = {
                    'hours': 0,
                    'amount': 0,
                    'rate': entry.rate
                }

            staff_breakdown[staff_name]['hours'] += entry.hours
            staff_breakdown[staff_name]['amount'] += entry.hours * entry.rate

        # Group by task type
        task_breakdown = {}
        for entry in relevant_entries:
            task = self.tasks.get(entry.task_id)
            task_type = task.task_type if task else "General"

            if task_type not in task_breakdown:
                task_breakdown[task_type] = {
                    'hours': 0,
                    'amount': 0
                }

            task_breakdown[task_type]['hours'] += entry.hours
            task_breakdown[task_type]['amount'] += entry.hours * entry.rate

        billing_report = {
            'client_name': client.name,
            'period': f"{period_start} to {period_end}",
            'total_hours': total_hours,
            'total_amount': total_amount,
            'average_rate': total_amount / total_hours if total_hours > 0 else 0,
            'staff_breakdown': staff_breakdown,
            'task_breakdown': task_breakdown,
            'entries': [
                {
                    'date': entry.date.isoformat(),
                    'staff': self.staff_members[entry.staff_id].name if entry.staff_id in self.staff_members else "Unknown",
                    'description': entry.description,
                    'hours': entry.hours,
                    'rate': entry.rate,
                    'amount': entry.hours * entry.rate
                }
                for entry in relevant_entries
            ]
        }

        return billing_report

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""

        today = datetime.date.today()
        overdue_tasks = []

        for task in self.tasks.values():
            if task.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                if task.due_date < today:
                    task.status = TaskStatus.OVERDUE
                    overdue_tasks.append(task)

        return overdue_tasks

    def get_practice_dashboard(self) -> Dict:
        """Generate comprehensive practice dashboard"""

        today = datetime.date.today()

        # Count tasks by status
        task_counts = {status.value: 0 for status in TaskStatus}
        for task in self.tasks.values():
            task_counts[task.status.value] += 1

        # Get overdue tasks
        overdue_tasks = self.get_overdue_tasks()

        # Calculate weekly revenue
        week_start = today - datetime.timedelta(days=today.weekday())
        week_end = week_start + datetime.timedelta(days=6)

        weekly_revenue = sum(
            entry.hours * entry.rate
            for entry in self.time_entries
            if week_start <= entry.date <= week_end and entry.billable
        )

        # Staff utilization
        workload_analysis = self.get_staff_workload_analysis()

        # Peak season planning
        peak_planning = self.get_peak_season_planning()

        dashboard = {
            'date': today.isoformat(),
            'task_summary': task_counts,
            'overdue_tasks': len(overdue_tasks),
            'total_clients': len(self.clients),
            'active_staff': len([s for s in self.staff_members.values() if s.active]),
            'weekly_revenue': weekly_revenue,
            'staff_utilization': workload_analysis['utilization_rate'],
            'peak_season_alert': peak_planning.get('additional_capacity_needed', 0) > 0,
            'recent_completions': len([
                t for t in self.tasks.values()
                if t.completed_at and t.completed_at.date() >= today - datetime.timedelta(days=7)
            ]),
            'upcoming_deadlines': len([
                t for t in self.tasks.values()
                if t.due_date <= today + datetime.timedelta(days=7)
                and t.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
            ])
        }

        return dashboard

# Example usage
if __name__ == "__main__":
    pmh = PracticeManagementHub()

    # Add sample staff
    eileen_id = pmh.add_staff_member({
        'name': 'Eileen Murphy',
        'email': 'eileen@murphyaccounting.ie',
        'role': 'partner',
        'hourly_rate': 150,
        'capacity_hours': 40,
        'specializations': ['audit', 'tax_planning']
    })

    # Add sample client
    client_id = pmh.add_client({
        'name': 'ABC Manufacturing Ltd',
        'entity_type': 'limited_company',
        'tier': 'premium',
        'year_end': datetime.date(2024, 12, 31),
        'billing_rate': 120,
        'total_annual_fee': 15000,
        'contact_person': 'John Smith',
        'email': 'john@abcmanufacturing.ie',
        'phone': '+353-1-234-5678',
        'address': 'Dublin, Ireland'
    })

    # Create annual workflow
    workflow_tasks = pmh.create_annual_workflow(client_id)
    print(f"Created {len(workflow_tasks)} tasks for annual workflow")

    # Generate dashboard
    dashboard = pmh.get_practice_dashboard()
    print(f"Practice Dashboard - Total clients: {dashboard['total_clients']}, Staff utilization: {dashboard['staff_utilization']:.1f}%")