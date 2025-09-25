"""
Simple Web Dashboard for Accounting Practice
FastAPI-based dashboard showing key metrics and data
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import datetime
from typing import List, Dict
import json
import os

# Import our realistic agents
from agents.realistic_practice_manager import SimplePracticeManager
from agents.realistic_reporting_helper import ReportingHelper
from agents.realistic_document_processor import DocumentProcessor
from agents.realistic_invoice_generator import InvoiceGenerator, ClientInfo

app = FastAPI(title="Accounting Practice Dashboard")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Initialize agents
practice_manager = SimplePracticeManager()
reporting_helper = ReportingHelper()
document_processor = DocumentProcessor()

# Sample business info for invoice generator
business_info = {
    'name': 'Professional Accounting Services',
    'address': '123 Business Street, Suite 100\nBusiness City, ST 12345',
    'phone': '(555) 123-4567',
    'email': 'info@professionalaccounting.com',
    'default_tax_rate': 0.0875
}
invoice_generator = InvoiceGenerator(business_info)

# Load sample data on startup
@app.on_event("startup")
async def load_sample_data():
    """Load some sample data for demonstration"""

    # Check if we have existing data
    if os.path.exists('practice_data.json'):
        practice_manager.load_data('practice_data.json')
        return

    # Create sample clients
    client1_id = practice_manager.add_client({
        'name': 'ABC Manufacturing LLC',
        'email': 'contact@abcmanufacturing.com',
        'phone': '(555) 123-4567',
        'address': '123 Industrial Blvd, Business City, ST 12345',
        'business_type': 'llc',
        'billing_rate': 150.00,
        'notes': 'Monthly bookkeeping client'
    })

    client2_id = practice_manager.add_client({
        'name': 'Retail Store Inc',
        'email': 'accounting@retailstore.com',
        'phone': '(555) 987-6543',
        'address': '456 Commerce Ave, Retail Town, ST 67890',
        'business_type': 'corporation',
        'billing_rate': 125.00,
        'notes': 'Quarterly tax prep and annual review'
    })

    # Create recurring tasks
    practice_manager.create_recurring_tasks(client1_id)
    practice_manager.create_recurring_tasks(client2_id)

    # Add some time entries
    today = datetime.date.today()
    for i in range(10):
        entry_date = today - datetime.timedelta(days=i)
        practice_manager.log_time_entry({
            'client_id': client1_id if i % 2 == 0 else client2_id,
            'date': entry_date,
            'hours': 2.5 + (i % 3),
            'description': f'Daily bookkeeping work - {entry_date.strftime("%B %d")}',
            'staff_member': 'Main Accountant'
        })

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""

    # Get dashboard data
    dashboard_data = practice_manager.get_practice_dashboard()

    # Get upcoming tasks
    upcoming_tasks = practice_manager.get_upcoming_tasks(7)
    overdue_tasks = practice_manager.get_overdue_tasks()

    # Get recent time entries
    recent_entries = []
    cutoff_date = datetime.date.today() - datetime.timedelta(days=7)
    all_entries = practice_manager.time_entries
    recent_entries = [
        entry for entry in all_entries
        if entry.date >= cutoff_date
    ]
    recent_entries.sort(key=lambda x: x.date, reverse=True)
    recent_entries = recent_entries[:10]  # Last 10 entries

    # Add client names to recent entries
    for entry in recent_entries:
        client = practice_manager.get_client(entry.client_id)
        entry.client_name = client.name if client else 'Unknown'

    # Add client names to tasks
    for task in upcoming_tasks + overdue_tasks:
        client = practice_manager.get_client(task.client_id)
        task.client_name = client.name if client else 'Unknown'

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "dashboard": dashboard_data,
        "upcoming_tasks": upcoming_tasks[:10],
        "overdue_tasks": overdue_tasks[:10],
        "recent_entries": recent_entries
    })

@app.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request):
    """Clients management page"""

    clients = practice_manager.list_clients()

    # Add summary data for each client
    for client in clients:
        client_tasks = practice_manager.get_tasks_for_client(client.id)
        client_time = practice_manager.get_time_entries_for_client(client.id)

        client.total_tasks = len(client_tasks)
        client.completed_tasks = len([t for t in client_tasks if t.status == 'completed'])
        client.total_hours = sum(entry.hours for entry in client_time if entry.billable)
        client.total_revenue = sum(entry.hours * entry.billable_rate for entry in client_time if entry.billable)

    return templates.TemplateResponse("clients.html", {
        "request": request,
        "clients": clients
    })

@app.get("/client/{client_id}", response_class=HTMLResponse)
async def client_detail(request: Request, client_id: str):
    """Individual client detail page"""

    client = practice_manager.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Get client tasks
    tasks = practice_manager.get_tasks_for_client(client_id)

    # Get client time entries (last 30 days)
    cutoff_date = datetime.date.today() - datetime.timedelta(days=30)
    time_entries = practice_manager.get_time_entries_for_client(client_id, start_date=cutoff_date)

    # Calculate summary stats
    total_hours = sum(entry.hours for entry in time_entries if entry.billable)
    total_revenue = sum(entry.hours * entry.billable_rate for entry in time_entries if entry.billable)

    return templates.TemplateResponse("client_detail.html", {
        "request": request,
        "client": client,
        "tasks": tasks,
        "time_entries": time_entries[:20],  # Show last 20 entries
        "total_hours": round(total_hours, 1),
        "total_revenue": round(total_revenue, 2)
    })

@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request):
    """Tasks management page"""

    all_tasks = list(practice_manager.tasks.values())

    # Add client names
    for task in all_tasks:
        client = practice_manager.get_client(task.client_id)
        task.client_name = client.name if client else 'Unknown'

    # Sort by due date
    all_tasks.sort(key=lambda t: t.due_date)

    # Group by status
    pending_tasks = [t for t in all_tasks if t.status == 'pending']
    in_progress_tasks = [t for t in all_tasks if t.status == 'in_progress']
    completed_tasks = [t for t in all_tasks if t.status == 'completed']
    overdue_tasks = practice_manager.get_overdue_tasks()

    # Add client names to overdue tasks
    for task in overdue_tasks:
        client = practice_manager.get_client(task.client_id)
        task.client_name = client.name if client else 'Unknown'

    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completed_tasks": completed_tasks[:20],  # Show last 20 completed
        "overdue_tasks": overdue_tasks
    })

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Reports and analytics page"""

    # Generate monthly summary
    sample_expenses = []  # Would be loaded from document processor
    sample_invoices = []  # Would be generated from practice data

    # Convert practice data to invoice format for reporting
    current_month = datetime.date.today().replace(day=1)
    this_month_entries = [
        entry for entry in practice_manager.time_entries
        if entry.date >= current_month and entry.billable
    ]

    # Group by client for invoice simulation
    client_revenue = {}
    for entry in this_month_entries:
        if entry.client_id not in client_revenue:
            client = practice_manager.get_client(entry.client_id)
            client_revenue[entry.client_id] = {
                'client_name': client.name if client else 'Unknown',
                'total': 0,
                'date': entry.date.isoformat()
            }
        client_revenue[entry.client_id]['total'] += entry.hours * entry.billable_rate

    sample_invoices = list(client_revenue.values())

    # Get billable hours summary
    hours_summary = practice_manager.get_billable_hours_summary(current_month, datetime.date.today())

    # Generate dashboard data for charts
    dashboard_data = reporting_helper.generate_dashboard_data(sample_expenses, sample_invoices)

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "hours_summary": hours_summary,
        "dashboard_data": dashboard_data
    })

@app.get("/api/dashboard-data")
async def api_dashboard_data():
    """API endpoint for dashboard data"""

    dashboard_data = practice_manager.get_practice_dashboard()
    return JSONResponse(dashboard_data)

@app.get("/api/time-entries")
async def api_time_entries(client_id: str = None, days: int = 30):
    """API endpoint for time entries"""

    cutoff_date = datetime.date.today() - datetime.timedelta(days=days)

    if client_id:
        entries = practice_manager.get_time_entries_for_client(client_id, start_date=cutoff_date)
    else:
        entries = [entry for entry in practice_manager.time_entries if entry.date >= cutoff_date]

    # Convert to JSON-serializable format
    entries_data = []
    for entry in entries:
        client = practice_manager.get_client(entry.client_id)
        entries_data.append({
            'id': entry.id,
            'client_id': entry.client_id,
            'client_name': client.name if client else 'Unknown',
            'date': entry.date.isoformat(),
            'hours': entry.hours,
            'description': entry.description,
            'billable': entry.billable,
            'amount': entry.hours * entry.billable_rate if entry.billable else 0
        })

    return JSONResponse(entries_data)

# Create templates directory and basic templates
def create_templates():
    """Create basic HTML templates"""

    os.makedirs("templates", exist_ok=True)

    # Base template
    base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Accounting Practice Dashboard{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; padding: 10px 15px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
        .nav a:hover { background: #0056b3; }
        .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: inline-block; margin-right: 30px; }
        .metric-value { font-size: 2em; font-weight: bold; color: #28a745; }
        .metric-label { font-size: 0.9em; color: #666; }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
        .table th { background-color: #f8f9fa; }
        .status-pending { color: #ffc107; }
        .status-in-progress { color: #007bff; }
        .status-completed { color: #28a745; }
        .status-overdue { color: #dc3545; font-weight: bold; }
        .priority-high { color: #dc3545; }
        .priority-urgent { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Professional Accounting Services</h1>
            <div class="nav">
                <a href="/">Dashboard</a>
                <a href="/clients">Clients</a>
                <a href="/tasks">Tasks</a>
                <a href="/reports">Reports</a>
            </div>
        </div>

        {% block content %}{% endblock %}
    </div>
</body>
</html>
    """

    # Dashboard template
    dashboard_template = """
{% extends "base.html" %}

{% block title %}Dashboard - Accounting Practice{% endblock %}

{% block content %}
<div class="card">
    <h2>Practice Overview</h2>
    <div class="metric">
        <div class="metric-value">{{ dashboard.clients.active_count }}</div>
        <div class="metric-label">Active Clients</div>
    </div>
    <div class="metric">
        <div class="metric-value">{{ dashboard.tasks.pending }}</div>
        <div class="metric-label">Pending Tasks</div>
    </div>
    <div class="metric">
        <div class="metric-value">${{ "%.2f"|format(dashboard.this_month.revenue) }}</div>
        <div class="metric-label">This Month Revenue</div>
    </div>
    <div class="metric">
        <div class="metric-value">{{ dashboard.this_month.billable_hours }}</div>
        <div class="metric-label">Billable Hours</div>
    </div>
</div>

{% if overdue_tasks %}
<div class="card">
    <h3 style="color: #dc3545;">Overdue Tasks ({{ overdue_tasks|length }})</h3>
    <table class="table">
        <thead>
            <tr>
                <th>Client</th>
                <th>Task</th>
                <th>Due Date</th>
                <th>Priority</th>
            </tr>
        </thead>
        <tbody>
            {% for task in overdue_tasks %}
            <tr>
                <td><a href="/client/{{ task.client_id }}">{{ task.client_name }}</a></td>
                <td>{{ task.title }}</td>
                <td class="status-overdue">{{ task.due_date }}</td>
                <td class="priority-{{ task.priority }}">{{ task.priority.title() }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endif %}

<div class="card">
    <h3>Upcoming Tasks (Next 7 Days)</h3>
    <table class="table">
        <thead>
            <tr>
                <th>Client</th>
                <th>Task</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Priority</th>
            </tr>
        </thead>
        <tbody>
            {% for task in upcoming_tasks %}
            <tr>
                <td><a href="/client/{{ task.client_id }}">{{ task.client_name }}</a></td>
                <td>{{ task.title }}</td>
                <td>{{ task.due_date }}</td>
                <td class="status-{{ task.status }}">{{ task.status.replace('_', ' ').title() }}</td>
                <td class="priority-{{ task.priority }}">{{ task.priority.title() }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="card">
    <h3>Recent Time Entries</h3>
    <table class="table">
        <thead>
            <tr>
                <th>Date</th>
                <th>Client</th>
                <th>Description</th>
                <th>Hours</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for entry in recent_entries %}
            <tr>
                <td>{{ entry.date }}</td>
                <td><a href="/client/{{ entry.client_id }}">{{ entry.client_name }}</a></td>
                <td>{{ entry.description }}</td>
                <td>{{ entry.hours }}</td>
                <td>${{ "%.2f"|format(entry.hours * entry.billable_rate) if entry.billable else "0.00" }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
    """

    # Write templates
    with open("templates/base.html", "w") as f:
        f.write(base_template)

    with open("templates/dashboard.html", "w") as f:
        f.write(dashboard_template)

    # Create other template stubs
    simple_templates = {
        "clients.html": """
{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>Clients ({{ clients|length }})</h2>
    <table class="table">
        <thead>
            <tr><th>Name</th><th>Type</th><th>Status</th><th>Revenue</th><th>Hours</th></tr>
        </thead>
        <tbody>
            {% for client in clients %}
            <tr>
                <td><a href="/client/{{ client.id }}">{{ client.name }}</a></td>
                <td>{{ client.business_type.replace('_', ' ').title() }}</td>
                <td>{{ client.status.title() }}</td>
                <td>${{ "%.2f"|format(client.total_revenue) }}</td>
                <td>{{ client.total_hours }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
        """,
        "client_detail.html": """
{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>{{ client.name }}</h2>
    <p><strong>Type:</strong> {{ client.business_type.replace('_', ' ').title() }}</p>
    <p><strong>Email:</strong> {{ client.email }}</p>
    <p><strong>Phone:</strong> {{ client.phone }}</p>
    <p><strong>Billing Rate:</strong> ${{ client.billing_rate }}/hour</p>
</div>
<div class="card">
    <h3>Tasks</h3>
    <table class="table">
        <thead>
            <tr><th>Task</th><th>Due Date</th><th>Status</th><th>Progress</th></tr>
        </thead>
        <tbody>
            {% for task in tasks %}
            <tr>
                <td>{{ task.title }}</td>
                <td>{{ task.due_date }}</td>
                <td class="status-{{ task.status }}">{{ task.status.replace('_', ' ').title() }}</td>
                <td>{{ task.actual_hours }}/{{ task.estimated_hours }} hrs</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
        """,
        "tasks.html": """
{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>Tasks Overview</h2>
    <h3>Overdue ({{ overdue_tasks|length }})</h3>
    <table class="table">
        <thead><tr><th>Client</th><th>Task</th><th>Due Date</th></tr></thead>
        <tbody>
            {% for task in overdue_tasks %}
            <tr><td>{{ task.client_name }}</td><td>{{ task.title }}</td><td class="status-overdue">{{ task.due_date }}</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
        """,
        "reports.html": """
{% extends "base.html" %}
{% block content %}
<div class="card">
    <h2>Monthly Reports</h2>
    <div class="metric">
        <div class="metric-value">{{ hours_summary.total_billable_hours }}</div>
        <div class="metric-label">Total Hours</div>
    </div>
    <div class="metric">
        <div class="metric-value">${{ "%.2f"|format(hours_summary.total_revenue) }}</div>
        <div class="metric-label">Total Revenue</div>
    </div>
</div>
{% endblock %}
        """
    }

    for filename, content in simple_templates.items():
        with open(f"templates/{filename}", "w") as f:
            f.write(content)

if __name__ == "__main__":
    # Create templates if they don't exist
    create_templates()

    print("Starting Accounting Practice Dashboard...")
    print("Dashboard will be available at: http://localhost:8000")
    print("API endpoints available at: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000)