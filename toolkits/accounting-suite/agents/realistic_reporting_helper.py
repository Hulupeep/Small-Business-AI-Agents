"""
Reporting Helper Agent
Basic reporting tools and dashboard data generation
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import csv
import os

@dataclass
class FinancialSummary:
    period: str
    income: float
    expenses: float
    net_profit: float
    expense_categories: Dict[str, float]
    top_clients: List[Tuple[str, float]]
    monthly_trend: List[Dict]

@dataclass
class ClientSummary:
    client_id: str
    client_name: str
    total_billed: float
    total_paid: float
    outstanding_balance: float
    last_payment_date: Optional[datetime.date]
    invoice_count: int

class ReportingHelper:
    """
    Basic reporting and dashboard data generation
    Provides simple financial summaries and client reports
    """

    def __init__(self):
        self.expense_categories = {
            'office_supplies': 'Office Supplies',
            'travel': 'Travel & Transportation',
            'meals': 'Meals & Entertainment',
            'utilities': 'Utilities',
            'rent': 'Rent & Facilities',
            'professional_services': 'Professional Services',
            'marketing': 'Marketing & Advertising',
            'software': 'Software & Subscriptions',
            'equipment': 'Equipment & Hardware',
            'insurance': 'Insurance',
            'uncategorized': 'Other Expenses'
        }

    def generate_monthly_summary(self, expenses: List[Dict], invoices: List[Dict],
                                payments: List[Dict] = None) -> FinancialSummary:
        """Generate monthly financial summary"""

        # Determine period
        today = datetime.date.today()
        period_start = today.replace(day=1)
        period = today.strftime("%B %Y")

        # Calculate total income from invoices
        monthly_invoices = [
            inv for inv in invoices
            if self._is_in_period(inv.get('date'), period_start)
        ]
        total_income = sum(inv.get('total', 0) for inv in monthly_invoices)

        # Calculate total expenses
        monthly_expenses = [
            exp for exp in expenses
            if self._is_in_period(exp.get('date'), period_start)
        ]
        total_expenses = sum(exp.get('amount', 0) for exp in monthly_expenses)

        # Group expenses by category
        category_totals = {}
        for expense in monthly_expenses:
            category = expense.get('category', 'uncategorized')
            category_name = self.expense_categories.get(category, 'Other')
            category_totals[category_name] = category_totals.get(category_name, 0) + expense.get('amount', 0)

        # Sort categories by amount
        sorted_categories = dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))

        # Calculate net profit
        net_profit = total_income - total_expenses

        # Get top clients by billing
        client_totals = {}
        for invoice in monthly_invoices:
            client_name = invoice.get('client_name', 'Unknown')
            client_totals[client_name] = client_totals.get(client_name, 0) + invoice.get('total', 0)

        top_clients = sorted(client_totals.items(), key=lambda x: x[1], reverse=True)[:5]

        # Generate 6-month trend (simplified)
        monthly_trend = self._generate_monthly_trend(expenses, invoices)

        return FinancialSummary(
            period=period,
            income=round(total_income, 2),
            expenses=round(total_expenses, 2),
            net_profit=round(net_profit, 2),
            expense_categories=sorted_categories,
            top_clients=top_clients,
            monthly_trend=monthly_trend
        )

    def generate_client_report(self, invoices: List[Dict], payments: List[Dict] = None) -> List[ClientSummary]:
        """Generate client summary report"""

        if payments is None:
            payments = []

        # Group invoices by client
        client_data = {}
        for invoice in invoices:
            client_id = invoice.get('client_id', 'unknown')
            client_name = invoice.get('client_name', 'Unknown Client')

            if client_id not in client_data:
                client_data[client_id] = {
                    'name': client_name,
                    'invoices': [],
                    'total_billed': 0,
                    'invoice_count': 0
                }

            client_data[client_id]['invoices'].append(invoice)
            client_data[client_id]['total_billed'] += invoice.get('total', 0)
            client_data[client_id]['invoice_count'] += 1

        # Calculate payments by client
        client_payments = {}
        for payment in payments:
            client_id = payment.get('client_id', 'unknown')
            client_payments[client_id] = client_payments.get(client_id, 0) + payment.get('amount', 0)

        # Find last payment date by client
        client_last_payment = {}
        for payment in payments:
            client_id = payment.get('client_id', 'unknown')
            payment_date = self._parse_date(payment.get('date'))
            if payment_date:
                if client_id not in client_last_payment or payment_date > client_last_payment[client_id]:
                    client_last_payment[client_id] = payment_date

        # Create client summaries
        client_summaries = []
        for client_id, data in client_data.items():
            total_paid = client_payments.get(client_id, 0)
            outstanding = data['total_billed'] - total_paid

            summary = ClientSummary(
                client_id=client_id,
                client_name=data['name'],
                total_billed=round(data['total_billed'], 2),
                total_paid=round(total_paid, 2),
                outstanding_balance=round(outstanding, 2),
                last_payment_date=client_last_payment.get(client_id),
                invoice_count=data['invoice_count']
            )
            client_summaries.append(summary)

        # Sort by outstanding balance (highest first)
        client_summaries.sort(key=lambda x: x.outstanding_balance, reverse=True)

        return client_summaries

    def generate_expense_breakdown(self, expenses: List[Dict],
                                 start_date: datetime.date = None,
                                 end_date: datetime.date = None) -> Dict:
        """Generate detailed expense breakdown"""

        if start_date is None:
            start_date = datetime.date.today().replace(day=1)  # Start of current month
        if end_date is None:
            end_date = datetime.date.today()

        # Filter expenses by date range
        filtered_expenses = []
        for expense in expenses:
            expense_date = self._parse_date(expense.get('date'))
            if expense_date and start_date <= expense_date <= end_date:
                filtered_expenses.append(expense)

        # Group by category
        category_breakdown = {}
        for expense in filtered_expenses:
            category = expense.get('category', 'uncategorized')
            category_name = self.expense_categories.get(category, 'Other')

            if category_name not in category_breakdown:
                category_breakdown[category_name] = {
                    'total': 0,
                    'count': 0,
                    'items': []
                }

            amount = expense.get('amount', 0)
            category_breakdown[category_name]['total'] += amount
            category_breakdown[category_name]['count'] += 1
            category_breakdown[category_name]['items'].append({
                'date': expense.get('date'),
                'description': expense.get('description', ''),
                'amount': amount,
                'vendor': expense.get('vendor', '')
            })

        # Sort categories by total amount
        sorted_breakdown = dict(sorted(category_breakdown.items(), key=lambda x: x[1]['total'], reverse=True))

        # Calculate totals
        total_expenses = sum(cat['total'] for cat in category_breakdown.values())
        total_items = sum(cat['count'] for cat in category_breakdown.values())

        report = {
            'period': f"{start_date} to {end_date}",
            'total_expenses': round(total_expenses, 2),
            'total_items': total_items,
            'average_expense': round(total_expenses / total_items, 2) if total_items > 0 else 0,
            'categories': sorted_breakdown,
            'generated_at': datetime.datetime.now().isoformat()
        }

        return report

    def generate_dashboard_data(self, expenses: List[Dict], invoices: List[Dict],
                              clients: List[Dict] = None) -> Dict:
        """Generate dashboard overview data"""

        if clients is None:
            clients = []

        today = datetime.date.today()
        current_month_start = today.replace(day=1)

        # Current month metrics
        current_month_expenses = [
            exp for exp in expenses
            if self._is_in_period(exp.get('date'), current_month_start)
        ]
        current_month_income = sum(
            inv.get('total', 0) for inv in invoices
            if self._is_in_period(inv.get('date'), current_month_start)
        )

        # Previous month for comparison
        if current_month_start.month == 1:
            prev_month_start = datetime.date(current_month_start.year - 1, 12, 1)
        else:
            prev_month_start = current_month_start.replace(month=current_month_start.month - 1)

        prev_month_expenses = [
            exp for exp in expenses
            if self._is_in_period(exp.get('date'), prev_month_start) and
               exp.get('date', '') < current_month_start.isoformat()
        ]

        current_month_expense_total = sum(exp.get('amount', 0) for exp in current_month_expenses)
        prev_month_expense_total = sum(exp.get('amount', 0) for exp in prev_month_expenses)

        # Calculate change percentage
        expense_change = 0
        if prev_month_expense_total > 0:
            expense_change = ((current_month_expense_total - prev_month_expense_total) / prev_month_expense_total) * 100

        # Outstanding invoices
        outstanding_invoices = [
            inv for inv in invoices
            if inv.get('status', '').lower() != 'paid'
        ]
        outstanding_amount = sum(inv.get('total', 0) - inv.get('paid_amount', 0) for inv in outstanding_invoices)

        # Overdue invoices
        overdue_invoices = []
        for invoice in outstanding_invoices:
            due_date = self._parse_date(invoice.get('due_date'))
            if due_date and due_date < today:
                overdue_invoices.append(invoice)

        # Top expense categories this month
        category_totals = {}
        for expense in current_month_expenses:
            category = expense.get('category', 'uncategorized')
            category_name = self.expense_categories.get(category, 'Other')
            category_totals[category_name] = category_totals.get(category_name, 0) + expense.get('amount', 0)

        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]

        dashboard = {
            'current_month': {
                'income': round(current_month_income, 2),
                'expenses': round(current_month_expense_total, 2),
                'net_profit': round(current_month_income - current_month_expense_total, 2),
                'expense_change_percent': round(expense_change, 1)
            },
            'outstanding': {
                'invoice_count': len(outstanding_invoices),
                'total_amount': round(outstanding_amount, 2)
            },
            'overdue': {
                'invoice_count': len(overdue_invoices),
                'total_amount': round(sum(inv.get('total', 0) for inv in overdue_invoices), 2)
            },
            'top_expense_categories': top_categories,
            'total_clients': len(clients),
            'total_invoices_ytd': len(invoices),
            'last_updated': datetime.datetime.now().isoformat()
        }

        return dashboard

    def export_to_csv(self, data: List[Dict], filename: str, headers: List[str] = None):
        """Export data to CSV file"""

        if not data:
            return

        if headers is None:
            headers = list(data[0].keys())

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    def export_summary_to_json(self, summary: FinancialSummary, filename: str):
        """Export financial summary to JSON"""

        # Convert to dictionary and handle dates
        summary_dict = {
            'period': summary.period,
            'income': summary.income,
            'expenses': summary.expenses,
            'net_profit': summary.net_profit,
            'expense_categories': summary.expense_categories,
            'top_clients': summary.top_clients,
            'monthly_trend': summary.monthly_trend,
            'generated_at': datetime.datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(summary_dict, f, indent=2, default=str)

    def _generate_monthly_trend(self, expenses: List[Dict], invoices: List[Dict]) -> List[Dict]:
        """Generate 6-month trend data"""

        today = datetime.date.today()
        trend_data = []

        for i in range(6):
            # Calculate month
            if today.month - i <= 0:
                month = today.month - i + 12
                year = today.year - 1
            else:
                month = today.month - i
                year = today.year

            month_start = datetime.date(year, month, 1)
            month_name = month_start.strftime("%b %Y")

            # Calculate month totals
            month_expenses = sum(
                exp.get('amount', 0) for exp in expenses
                if self._is_in_period(exp.get('date'), month_start)
            )

            month_income = sum(
                inv.get('total', 0) for inv in invoices
                if self._is_in_period(inv.get('date'), month_start)
            )

            trend_data.append({
                'month': month_name,
                'income': round(month_income, 2),
                'expenses': round(month_expenses, 2),
                'profit': round(month_income - month_expenses, 2)
            })

        return list(reversed(trend_data))  # Chronological order

    def _is_in_period(self, date_str: Optional[str], period_start: datetime.date) -> bool:
        """Check if date string is in the specified period (month)"""

        if not date_str:
            return False

        date_obj = self._parse_date(date_str)
        if not date_obj:
            return False

        # Check if date is in the same month and year as period_start
        return (date_obj.year == period_start.year and
                date_obj.month == period_start.month)

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime.date]:
        """Parse various date formats"""

        if not date_str:
            return None

        try:
            # Try different date formats
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']

            for fmt in formats:
                try:
                    return datetime.datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue

            # If none work, return None
            return None

        except Exception:
            return None

    def generate_profit_loss_statement(self, invoices: List[Dict], expenses: List[Dict],
                                     start_date: datetime.date, end_date: datetime.date) -> Dict:
        """Generate basic Profit & Loss statement"""

        # Filter data by date range
        period_invoices = [
            inv for inv in invoices
            if self._date_in_range(inv.get('date'), start_date, end_date)
        ]

        period_expenses = [
            exp for exp in expenses
            if self._date_in_range(exp.get('date'), start_date, end_date)
        ]

        # Calculate revenue
        total_revenue = sum(inv.get('total', 0) for inv in period_invoices)

        # Calculate expenses by category
        expense_categories = {}
        for expense in period_expenses:
            category = expense.get('category', 'uncategorized')
            category_name = self.expense_categories.get(category, 'Other Expenses')
            expense_categories[category_name] = expense_categories.get(category_name, 0) + expense.get('amount', 0)

        total_expenses = sum(expense_categories.values())
        net_profit = total_revenue - total_expenses

        # Calculate margins
        gross_margin = (total_revenue / total_revenue * 100) if total_revenue > 0 else 0
        net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

        pl_statement = {
            'period': f"{start_date} to {end_date}",
            'revenue': {
                'total_revenue': round(total_revenue, 2),
                'invoice_count': len(period_invoices)
            },
            'expenses': expense_categories,
            'totals': {
                'total_expenses': round(total_expenses, 2),
                'net_profit': round(net_profit, 2),
                'gross_margin_percent': round(gross_margin, 1),
                'net_margin_percent': round(net_margin, 1)
            },
            'generated_at': datetime.datetime.now().isoformat()
        }

        return pl_statement

    def _date_in_range(self, date_str: Optional[str], start_date: datetime.date,
                       end_date: datetime.date) -> bool:
        """Check if date string is within the specified range"""

        date_obj = self._parse_date(date_str)
        if not date_obj:
            return False

        return start_date <= date_obj <= end_date

# Example usage
if __name__ == "__main__":
    # Initialize reporting helper
    reporter = ReportingHelper()

    # Sample data for testing
    sample_expenses = [
        {
            'date': '2024-01-15',
            'amount': 150.00,
            'category': 'office_supplies',
            'description': 'Office supplies purchase',
            'vendor': 'Office Depot'
        },
        {
            'date': '2024-01-20',
            'amount': 85.50,
            'category': 'meals',
            'description': 'Client lunch meeting',
            'vendor': 'Restaurant ABC'
        }
    ]

    sample_invoices = [
        {
            'date': '2024-01-10',
            'client_id': 'client1',
            'client_name': 'ABC Corp',
            'total': 2500.00,
            'status': 'sent'
        },
        {
            'date': '2024-01-25',
            'client_id': 'client2',
            'client_name': 'XYZ LLC',
            'total': 1800.00,
            'status': 'paid'
        }
    ]

    # Generate dashboard data
    dashboard = reporter.generate_dashboard_data(sample_expenses, sample_invoices)
    print("Dashboard generated:")
    print(f"Current month income: ${dashboard['current_month']['income']:,.2f}")
    print(f"Current month expenses: ${dashboard['current_month']['expenses']:,.2f}")
    print(f"Net profit: ${dashboard['current_month']['net_profit']:,.2f}")

    print("\nReporting helper initialized successfully!")