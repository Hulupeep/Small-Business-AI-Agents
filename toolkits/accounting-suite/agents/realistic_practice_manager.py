"""
Practice Management Agent
Simplified practice management for small accounting firms
"""

import datetime
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json

@dataclass
class Client:
    id: str
    name: str
    email: str
    phone: str
    address: str
    business_type: str  # sole_proprietor, partnership, corporation, llc
    tax_id: Optional[str] = None
    billing_rate: float = 0.0
    status: str = "active"  # active, inactive, prospective
    notes: str = ""
    created_date: datetime.date = None

@dataclass
class Task:
    id: str
    client_id: str
    title: str
    description: str
    due_date: datetime.date
    status: str = "pending"  # pending, in_progress, completed, cancelled
    priority: str = "medium"  # low, medium, high, urgent
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    assigned_to: str = ""
    created_date: datetime.date = None

@dataclass
class TimeEntry:
    id: str
    client_id: str
    task_id: Optional[str]
    date: datetime.date
    hours: float
    description: str
    billable_rate: float = 0.0
    billable: bool = True
    staff_member: str = ""

class SimplePracticeManager:
    """
    Simplified practice management for small accounting firms
    Handles basic client management, task tracking, and time recording
    """

    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.tasks: Dict[str, Task] = {}
        self.time_entries: List[TimeEntry] = []

        # Common accounting tasks and their typical timeframes
        self.standard_tasks = {
            'monthly_bookkeeping': {
                'title': 'Monthly Bookkeeping',
                'description': 'Record transactions, reconcile accounts, prepare monthly statements',
                'estimated_hours': 8.0,
                'priority': 'medium'
            },
            'quarterly_taxes': {
                'title': 'Quarterly Tax Filing',
                'description': 'Prepare and file quarterly tax returns',
                'estimated_hours': 4.0,
                'priority': 'high'
            },
            'annual_tax_return': {
                'title': 'Annual Tax Return',
                'description': 'Prepare annual tax return',
                'estimated_hours': 12.0,
                'priority': 'high'
            },
            'financial_statements': {
                'title': 'Financial Statements',
                'description': 'Prepare monthly/quarterly financial statements',
                'estimated_hours': 6.0,
                'priority': 'medium'
            },
            'payroll_processing': {
                'title': 'Payroll Processing',
                'description': 'Process payroll and file payroll taxes',
                'estimated_hours': 3.0,
                'priority': 'high'
            },
            'audit_preparation': {
                'title': 'Audit Preparation',
                'description': 'Prepare documents and schedules for audit',
                'estimated_hours': 20.0,
                'priority': 'urgent'
            }
        }

    def add_client(self, client_data: Dict) -> str:
        """Add a new client to the practice"""

        client_id = str(uuid.uuid4())[:8]

        client = Client(
            id=client_id,
            name=client_data['name'],
            email=client_data['email'],
            phone=client_data.get('phone', ''),
            address=client_data.get('address', ''),
            business_type=client_data.get('business_type', 'sole_proprietor'),
            tax_id=client_data.get('tax_id'),
            billing_rate=float(client_data.get('billing_rate', 0)),
            status=client_data.get('status', 'active'),
            notes=client_data.get('notes', ''),
            created_date=datetime.date.today()
        )

        self.clients[client_id] = client
        return client_id

    def update_client(self, client_id: str, updates: Dict) -> bool:
        """Update client information"""

        if client_id not in self.clients:
            return False

        client = self.clients[client_id]

        # Update allowed fields
        allowed_fields = ['name', 'email', 'phone', 'address', 'business_type',
                         'tax_id', 'billing_rate', 'status', 'notes']

        for field, value in updates.items():
            if field in allowed_fields and hasattr(client, field):
                setattr(client, field, value)

        return True

    def get_client(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        return self.clients.get(client_id)

    def list_clients(self, status: str = None) -> List[Client]:
        """List all clients, optionally filtered by status"""

        if status:
            return [client for client in self.clients.values() if client.status == status]
        else:
            return list(self.clients.values())

    def create_task(self, task_data: Dict) -> str:
        """Create a new task"""

        task_id = str(uuid.uuid4())[:8]

        # Get standard task template if provided
        task_type = task_data.get('task_type')
        if task_type in self.standard_tasks:
            template = self.standard_tasks[task_type]
            task_data.setdefault('title', template['title'])
            task_data.setdefault('description', template['description'])
            task_data.setdefault('estimated_hours', template['estimated_hours'])
            task_data.setdefault('priority', template['priority'])

        task = Task(
            id=task_id,
            client_id=task_data['client_id'],
            title=task_data['title'],
            description=task_data.get('description', ''),
            due_date=self._parse_date(task_data['due_date']),
            status=task_data.get('status', 'pending'),
            priority=task_data.get('priority', 'medium'),
            estimated_hours=float(task_data.get('estimated_hours', 0)),
            assigned_to=task_data.get('assigned_to', ''),
            created_date=datetime.date.today()
        )

        self.tasks[task_id] = task
        return task_id

    def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update task information"""

        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        # Update allowed fields
        allowed_fields = ['title', 'description', 'due_date', 'status', 'priority',
                         'estimated_hours', 'actual_hours', 'assigned_to']

        for field, value in updates.items():
            if field in allowed_fields and hasattr(task, field):
                if field == 'due_date':
                    value = self._parse_date(value)
                elif field in ['estimated_hours', 'actual_hours']:
                    value = float(value)
                setattr(task, field, value)

        return True

    def get_tasks_for_client(self, client_id: str, status: str = None) -> List[Task]:
        """Get tasks for a specific client"""

        client_tasks = [task for task in self.tasks.values() if task.client_id == client_id]

        if status:
            client_tasks = [task for task in client_tasks if task.status == status]

        # Sort by due date
        client_tasks.sort(key=lambda t: t.due_date)
        return client_tasks

    def get_overdue_tasks(self) -> List[Task]:
        """Get all overdue tasks"""

        today = datetime.date.today()
        overdue = [
            task for task in self.tasks.values()
            if task.due_date < today and task.status not in ['completed', 'cancelled']
        ]

        overdue.sort(key=lambda t: t.due_date)
        return overdue

    def get_upcoming_tasks(self, days: int = 7) -> List[Task]:
        """Get tasks due within the specified number of days"""

        today = datetime.date.today()
        cutoff = today + datetime.timedelta(days=days)

        upcoming = [
            task for task in self.tasks.values()
            if today <= task.due_date <= cutoff and task.status not in ['completed', 'cancelled']
        ]

        upcoming.sort(key=lambda t: t.due_date)
        return upcoming

    def log_time_entry(self, entry_data: Dict) -> str:
        """Log a time entry"""

        entry_id = str(uuid.uuid4())[:8]

        # Get client billing rate if not provided
        billable_rate = entry_data.get('billable_rate', 0)
        if billable_rate == 0 and entry_data.get('client_id'):
            client = self.get_client(entry_data['client_id'])
            if client:
                billable_rate = client.billing_rate

        entry = TimeEntry(
            id=entry_id,
            client_id=entry_data['client_id'],
            task_id=entry_data.get('task_id'),
            date=self._parse_date(entry_data['date']),
            hours=float(entry_data['hours']),
            description=entry_data['description'],
            billable_rate=billable_rate,
            billable=entry_data.get('billable', True),
            staff_member=entry_data.get('staff_member', '')
        )

        self.time_entries.append(entry)

        # Update task actual hours if task_id provided
        if entry.task_id and entry.task_id in self.tasks:
            self.tasks[entry.task_id].actual_hours += entry.hours

        return entry_id

    def get_time_entries_for_client(self, client_id: str, start_date: datetime.date = None,
                                   end_date: datetime.date = None) -> List[TimeEntry]:
        """Get time entries for a client within date range"""

        client_entries = [entry for entry in self.time_entries if entry.client_id == client_id]

        if start_date:
            client_entries = [entry for entry in client_entries if entry.date >= start_date]

        if end_date:
            client_entries = [entry for entry in client_entries if entry.date <= end_date]

        client_entries.sort(key=lambda e: e.date, reverse=True)
        return client_entries

    def get_billable_hours_summary(self, start_date: datetime.date, end_date: datetime.date) -> Dict:
        """Get summary of billable hours for period"""

        period_entries = [
            entry for entry in self.time_entries
            if start_date <= entry.date <= end_date and entry.billable
        ]

        # Group by client
        client_summaries = {}
        total_hours = 0
        total_revenue = 0

        for entry in period_entries:
            client_id = entry.client_id
            client = self.get_client(client_id)
            client_name = client.name if client else 'Unknown'

            if client_id not in client_summaries:
                client_summaries[client_id] = {
                    'client_name': client_name,
                    'total_hours': 0,
                    'total_amount': 0,
                    'entries': []
                }

            client_summaries[client_id]['total_hours'] += entry.hours
            client_summaries[client_id]['total_amount'] += entry.hours * entry.billable_rate
            client_summaries[client_id]['entries'].append(entry)

            total_hours += entry.hours
            total_revenue += entry.hours * entry.billable_rate

        summary = {
            'period': f"{start_date} to {end_date}",
            'total_billable_hours': round(total_hours, 2),
            'total_revenue': round(total_revenue, 2),
            'average_rate': round(total_revenue / total_hours, 2) if total_hours > 0 else 0,
            'client_breakdown': client_summaries,
            'entry_count': len(period_entries)
        }

        return summary

    def create_recurring_tasks(self, client_id: str, business_type: str = None) -> List[str]:
        """Create standard recurring tasks for a client based on business type"""

        client = self.get_client(client_id)
        if not client:
            return []

        if business_type is None:
            business_type = client.business_type

        created_tasks = []
        today = datetime.date.today()

        # Monthly tasks
        monthly_due = datetime.date(today.year, today.month, 15)  # 15th of current month
        if monthly_due < today:
            # Next month
            if today.month == 12:
                monthly_due = datetime.date(today.year + 1, 1, 15)
            else:
                monthly_due = datetime.date(today.year, today.month + 1, 15)

        # Quarterly tasks
        quarter_months = [3, 6, 9, 12]
        next_quarter_month = min([m for m in quarter_months if m > today.month] or [3])
        if next_quarter_month == 3:
            quarter_year = today.year + 1
        else:
            quarter_year = today.year
        quarterly_due = datetime.date(quarter_year, next_quarter_month, 15)

        # Annual tasks (typically due by tax deadline)
        if today.month <= 4:
            annual_due = datetime.date(today.year, 4, 15)
        else:
            annual_due = datetime.date(today.year + 1, 4, 15)

        # Create tasks based on business type
        task_schedule = {
            'sole_proprietor': [
                ('monthly_bookkeeping', monthly_due),
                ('quarterly_taxes', quarterly_due),
                ('annual_tax_return', annual_due)
            ],
            'partnership': [
                ('monthly_bookkeeping', monthly_due),
                ('quarterly_taxes', quarterly_due),
                ('annual_tax_return', datetime.date(today.year + 1, 3, 15))  # Partnership deadline
            ],
            'corporation': [
                ('monthly_bookkeeping', monthly_due),
                ('quarterly_taxes', quarterly_due),
                ('annual_tax_return', datetime.date(today.year + 1, 3, 15)),  # Corporate deadline
                ('financial_statements', monthly_due)
            ],
            'llc': [
                ('monthly_bookkeeping', monthly_due),
                ('quarterly_taxes', quarterly_due),
                ('annual_tax_return', annual_due)
            ]
        }

        tasks_to_create = task_schedule.get(business_type, task_schedule['sole_proprietor'])

        for task_type, due_date in tasks_to_create:
            task_id = self.create_task({
                'client_id': client_id,
                'task_type': task_type,
                'due_date': due_date
            })
            created_tasks.append(task_id)

        return created_tasks

    def get_practice_dashboard(self) -> Dict:
        """Get practice overview dashboard data"""

        today = datetime.date.today()

        # Active clients
        active_clients = len([c for c in self.clients.values() if c.status == 'active'])

        # Task statistics
        pending_tasks = len([t for t in self.tasks.values() if t.status == 'pending'])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == 'in_progress'])
        completed_tasks = len([t for t in self.tasks.values() if t.status == 'completed'])
        overdue_tasks = len(self.get_overdue_tasks())
        upcoming_tasks = len(self.get_upcoming_tasks())

        # This month's time entries
        month_start = today.replace(day=1)
        this_month_entries = [
            entry for entry in self.time_entries
            if entry.date >= month_start and entry.billable
        ]

        total_hours_this_month = sum(entry.hours for entry in this_month_entries)
        total_revenue_this_month = sum(entry.hours * entry.billable_rate for entry in this_month_entries)

        # Recent activity (last 7 days)
        week_ago = today - datetime.timedelta(days=7)
        recent_time_entries = len([
            entry for entry in self.time_entries
            if entry.date >= week_ago
        ])

        dashboard = {
            'clients': {
                'active_count': active_clients,
                'total_count': len(self.clients)
            },
            'tasks': {
                'pending': pending_tasks,
                'in_progress': in_progress_tasks,
                'completed': completed_tasks,
                'overdue': overdue_tasks,
                'upcoming_7_days': upcoming_tasks
            },
            'this_month': {
                'billable_hours': round(total_hours_this_month, 1),
                'revenue': round(total_revenue_this_month, 2),
                'average_rate': round(total_revenue_this_month / total_hours_this_month, 2) if total_hours_this_month > 0 else 0
            },
            'recent_activity': {
                'time_entries_last_7_days': recent_time_entries
            },
            'last_updated': datetime.datetime.now().isoformat()
        }

        return dashboard

    def export_client_data(self) -> List[Dict]:
        """Export client data for reporting"""

        client_data = []
        for client in self.clients.values():
            # Get task and time summary for each client
            client_tasks = self.get_tasks_for_client(client.id)
            client_time = self.get_time_entries_for_client(client.id)

            total_billed_hours = sum(entry.hours for entry in client_time if entry.billable)
            total_revenue = sum(entry.hours * entry.billable_rate for entry in client_time if entry.billable)

            client_export = asdict(client)
            client_export.update({
                'total_tasks': len(client_tasks),
                'completed_tasks': len([t for t in client_tasks if t.status == 'completed']),
                'total_billed_hours': round(total_billed_hours, 2),
                'total_revenue': round(total_revenue, 2),
                'last_time_entry': client_time[0].date.isoformat() if client_time else None
            })

            # Convert dates to strings for JSON compatibility
            if client_export['created_date']:
                client_export['created_date'] = client_export['created_date'].isoformat()

            client_data.append(client_export)

        return client_data

    def _parse_date(self, date_input) -> datetime.date:
        """Parse various date input formats"""

        if isinstance(date_input, datetime.date):
            return date_input

        if isinstance(date_input, str):
            try:
                return datetime.datetime.strptime(date_input, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.datetime.strptime(date_input, '%m/%d/%Y').date()
                except ValueError:
                    return datetime.date.today()

        return datetime.date.today()

    def save_data(self, filename: str):
        """Save all practice data to JSON file"""

        data = {
            'clients': {cid: asdict(client) for cid, client in self.clients.items()},
            'tasks': {tid: asdict(task) for tid, task in self.tasks.items()},
            'time_entries': [asdict(entry) for entry in self.time_entries],
            'exported_at': datetime.datetime.now().isoformat()
        }

        # Convert dates to strings for JSON serialization
        def convert_dates(obj):
            if isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(item) for item in obj]
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            else:
                return obj

        data = convert_dates(data)

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_data(self, filename: str):
        """Load practice data from JSON file"""

        try:
            with open(filename, 'r') as f:
                data = json.load(f)

            # Load clients
            for cid, client_data in data.get('clients', {}).items():
                client_data['created_date'] = datetime.datetime.fromisoformat(client_data['created_date']).date() if client_data.get('created_date') else None
                self.clients[cid] = Client(**client_data)

            # Load tasks
            for tid, task_data in data.get('tasks', {}).items():
                task_data['due_date'] = datetime.datetime.fromisoformat(task_data['due_date']).date()
                task_data['created_date'] = datetime.datetime.fromisoformat(task_data['created_date']).date() if task_data.get('created_date') else None
                self.tasks[tid] = Task(**task_data)

            # Load time entries
            for entry_data in data.get('time_entries', []):
                entry_data['date'] = datetime.datetime.fromisoformat(entry_data['date']).date()
                self.time_entries.append(TimeEntry(**entry_data))

            return True

        except Exception as e:
            print(f"Error loading data: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize practice manager
    pm = SimplePracticeManager()

    # Add sample client
    client_id = pm.add_client({
        'name': 'ABC Manufacturing LLC',
        'email': 'contact@abcmanufacturing.com',
        'phone': '(555) 123-4567',
        'address': '123 Industrial Blvd, Business City, ST 12345',
        'business_type': 'llc',
        'billing_rate': 150.00,
        'notes': 'Monthly bookkeeping and quarterly tax prep'
    })

    print(f"Added client: {client_id}")

    # Create recurring tasks
    task_ids = pm.create_recurring_tasks(client_id)
    print(f"Created {len(task_ids)} recurring tasks")

    # Log some time
    time_entry_id = pm.log_time_entry({
        'client_id': client_id,
        'date': datetime.date.today(),
        'hours': 3.5,
        'description': 'Monthly bookkeeping - reconciled bank accounts',
        'staff_member': 'John Accountant'
    })

    print(f"Logged time entry: {time_entry_id}")

    # Get dashboard
    dashboard = pm.get_practice_dashboard()
    print(f"Dashboard - Active clients: {dashboard['clients']['active_count']}")
    print(f"Pending tasks: {dashboard['tasks']['pending']}")

    print("Practice manager initialized successfully!")