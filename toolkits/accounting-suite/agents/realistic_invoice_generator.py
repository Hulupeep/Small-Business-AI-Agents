"""
Invoice Generation Agent
Realistic invoice generation with templates and client management
"""

import datetime
import json
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from jinja2 import Template
import os

@dataclass
class ClientInfo:
    name: str
    email: str
    address: str
    phone: str
    company_id: Optional[str] = None
    tax_id: Optional[str] = None
    billing_rate: float = 0.0
    payment_terms: int = 30  # days

@dataclass
class LineItem:
    description: str
    quantity: float
    rate: float
    amount: float
    tax_rate: float = 0.0

@dataclass
class Invoice:
    invoice_number: str
    date: datetime.date
    due_date: datetime.date
    client: ClientInfo
    line_items: List[LineItem]
    subtotal: float
    tax_amount: float
    total: float
    status: str = "draft"
    notes: str = ""
    payment_received: float = 0.0

class InvoiceGenerator:
    """
    Simple invoice generation system for small accounting practices
    """

    def __init__(self, business_info: Dict):
        self.business_info = business_info
        self.tax_rate = business_info.get('default_tax_rate', 0.0875)  # Default 8.75%
        self.invoice_counter = 1000  # Starting invoice number

        # Load HTML template
        self.html_template = self._get_html_template()

    def create_invoice(self, client: ClientInfo, line_items: List[Dict],
                      invoice_date: Optional[datetime.date] = None,
                      due_days: int = 30) -> Invoice:
        """Create a new invoice"""

        # Set dates
        if invoice_date is None:
            invoice_date = datetime.date.today()
        due_date = invoice_date + datetime.timedelta(days=due_days)

        # Convert line items to LineItem objects and calculate amounts
        processed_items = []
        subtotal = 0.0

        for item in line_items:
            line_item = LineItem(
                description=item['description'],
                quantity=float(item.get('quantity', 1)),
                rate=float(item.get('rate', 0)),
                amount=0.0,  # Will calculate
                tax_rate=float(item.get('tax_rate', 0))
            )

            # Calculate amount
            line_item.amount = line_item.quantity * line_item.rate
            subtotal += line_item.amount
            processed_items.append(line_item)

        # Calculate tax and total
        tax_amount = subtotal * self.tax_rate
        total = subtotal + tax_amount

        # Generate invoice number
        invoice_number = self._generate_invoice_number()

        invoice = Invoice(
            invoice_number=invoice_number,
            date=invoice_date,
            due_date=due_date,
            client=client,
            line_items=processed_items,
            subtotal=round(subtotal, 2),
            tax_amount=round(tax_amount, 2),
            total=round(total, 2),
            notes=line_items[0].get('notes', '') if line_items else ''
        )

        return invoice

    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        self.invoice_counter += 1
        year = datetime.date.today().year
        return f"INV-{year}-{self.invoice_counter:04d}"

    def generate_html_invoice(self, invoice: Invoice) -> str:
        """Generate HTML version of invoice"""

        template_data = {
            'business': self.business_info,
            'invoice': asdict(invoice),
            'invoice_date': invoice.date.strftime('%B %d, %Y'),
            'due_date': invoice.due_date.strftime('%B %d, %Y'),
            'generation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Process client data
        template_data['client'] = asdict(invoice.client)

        # Process line items for template
        template_data['line_items'] = []
        for item in invoice.line_items:
            template_data['line_items'].append({
                'description': item.description,
                'quantity': f"{item.quantity:g}",  # Remove trailing zeros
                'rate': f"${item.rate:,.2f}",
                'amount': f"${item.amount:,.2f}"
            })

        # Format monetary amounts
        template_data['subtotal_formatted'] = f"${invoice.subtotal:,.2f}"
        template_data['tax_formatted'] = f"${invoice.tax_amount:,.2f}"
        template_data['total_formatted'] = f"${invoice.total:,.2f}"
        template_data['tax_rate_percent'] = f"{self.tax_rate * 100:.2f}%"

        # Calculate balance due
        balance_due = invoice.total - invoice.payment_received
        template_data['balance_due'] = f"${balance_due:,.2f}"

        template = Template(self.html_template)
        return template.render(**template_data)

    def generate_simple_text_invoice(self, invoice: Invoice) -> str:
        """Generate simple text version of invoice"""

        text = f"""
INVOICE

Invoice #: {invoice.invoice_number}
Date: {invoice.date.strftime('%B %d, %Y')}
Due Date: {invoice.due_date.strftime('%B %d, %Y')}

FROM:
{self.business_info['name']}
{self.business_info.get('address', '')}
{self.business_info.get('phone', '')}
{self.business_info.get('email', '')}

TO:
{invoice.client.name}
{invoice.client.address}
{invoice.client.phone}
{invoice.client.email}

SERVICES/ITEMS:
{'Description':<40} {'Qty':<8} {'Rate':<12} {'Amount':<12}
{'-' * 72}
"""

        for item in invoice.line_items:
            text += f"{item.description:<40} {item.quantity:<8g} ${item.rate:<11,.2f} ${item.amount:<11,.2f}\n"

        text += f"""
{'-' * 72}
{'Subtotal:':<60} ${invoice.subtotal:>11,.2f}
{'Tax ({:.2f}%):':<60} ${invoice.tax_amount:>11,.2f}
{'TOTAL:':<60} ${invoice.total:>11,.2f}

Payment Terms: {invoice.client.payment_terms} days
"""

        if invoice.notes:
            text += f"\nNotes:\n{invoice.notes}\n"

        return text

    def create_time_based_invoice(self, client: ClientInfo, time_entries: List[Dict]) -> Invoice:
        """Create invoice from time tracking entries"""

        line_items = []

        # Group time entries by description/task
        grouped_entries = {}
        for entry in time_entries:
            key = entry.get('description', 'Professional Services')
            if key not in grouped_entries:
                grouped_entries[key] = {'hours': 0, 'rate': client.billing_rate}
            grouped_entries[key]['hours'] += float(entry.get('hours', 0))

        # Create line items from grouped entries
        for description, data in grouped_entries.items():
            line_items.append({
                'description': description,
                'quantity': data['hours'],
                'rate': data['rate'],
                'notes': f"Time period: {time_entries[0].get('period', 'Current month')}"
            })

        return self.create_invoice(client, line_items)

    def create_project_invoice(self, client: ClientInfo, project_details: Dict) -> Invoice:
        """Create invoice for project-based work"""

        line_items = []

        # Add project phases or deliverables
        for deliverable in project_details.get('deliverables', []):
            line_items.append({
                'description': deliverable['name'],
                'quantity': 1,
                'rate': deliverable['amount'],
                'notes': deliverable.get('description', '')
            })

        # Add expenses if any
        for expense in project_details.get('expenses', []):
            line_items.append({
                'description': f"Expense: {expense['description']}",
                'quantity': 1,
                'rate': expense['amount']
            })

        invoice = self.create_invoice(client, line_items)
        invoice.notes = project_details.get('notes', '')

        return invoice

    def save_invoice_data(self, invoice: Invoice, file_path: str):
        """Save invoice data to JSON file"""

        invoice_data = asdict(invoice)

        # Convert dates to strings for JSON serialization
        invoice_data['date'] = invoice.date.isoformat()
        invoice_data['due_date'] = invoice.due_date.isoformat()

        with open(file_path, 'w') as f:
            json.dump(invoice_data, f, indent=2)

    def load_invoice_data(self, file_path: str) -> Invoice:
        """Load invoice data from JSON file"""

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Convert date strings back to date objects
        data['date'] = datetime.datetime.fromisoformat(data['date']).date()
        data['due_date'] = datetime.datetime.fromisoformat(data['due_date']).date()

        # Reconstruct objects
        client = ClientInfo(**data['client'])
        line_items = [LineItem(**item) for item in data['line_items']]

        invoice = Invoice(
            invoice_number=data['invoice_number'],
            date=data['date'],
            due_date=data['due_date'],
            client=client,
            line_items=line_items,
            subtotal=data['subtotal'],
            tax_amount=data['tax_amount'],
            total=data['total'],
            status=data.get('status', 'draft'),
            notes=data.get('notes', ''),
            payment_received=data.get('payment_received', 0.0)
        )

        return invoice

    def get_invoice_summary(self, invoices: List[Invoice]) -> Dict:
        """Generate summary of invoices"""

        total_invoiced = sum(inv.total for inv in invoices)
        total_paid = sum(inv.payment_received for inv in invoices)
        outstanding = total_invoiced - total_paid

        # Count by status
        status_counts = {}
        for invoice in invoices:
            status = invoice.status
            status_counts[status] = status_counts.get(status, 0) + 1

        # Overdue invoices
        today = datetime.date.today()
        overdue = [inv for inv in invoices if inv.due_date < today and inv.payment_received < inv.total]

        summary = {
            'total_invoices': len(invoices),
            'total_invoiced': round(total_invoiced, 2),
            'total_paid': round(total_paid, 2),
            'outstanding_amount': round(outstanding, 2),
            'status_breakdown': status_counts,
            'overdue_count': len(overdue),
            'overdue_amount': round(sum(inv.total - inv.payment_received for inv in overdue), 2)
        }

        return summary

    def _get_html_template(self) -> str:
        """Get HTML template for invoice"""

        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice {{ invoice.invoice_number }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; }
        .business-info { float: left; width: 45%; }
        .client-info { float: right; width: 45%; text-align: right; }
        .invoice-details { clear: both; margin: 30px 0; }
        .line-items { margin: 20px 0; }
        .line-items table { width: 100%; border-collapse: collapse; }
        .line-items th, .line-items td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .line-items th { background-color: #f2f2f2; }
        .totals { float: right; width: 300px; margin-top: 20px; }
        .totals table { width: 100%; }
        .totals td { padding: 5px; border-bottom: 1px solid #ddd; }
        .total-row { font-weight: bold; font-size: 1.2em; }
        .footer { clear: both; margin-top: 50px; text-align: center; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>INVOICE</h1>
    </div>

    <div class="business-info">
        <h3>{{ business.name }}</h3>
        <p>{{ business.address | default('') }}</p>
        <p>{{ business.phone | default('') }}</p>
        <p>{{ business.email | default('') }}</p>
    </div>

    <div class="client-info">
        <h3>Bill To:</h3>
        <p><strong>{{ client.name }}</strong></p>
        <p>{{ client.address }}</p>
        <p>{{ client.phone }}</p>
        <p>{{ client.email }}</p>
    </div>

    <div class="invoice-details">
        <table>
            <tr>
                <td><strong>Invoice Number:</strong></td>
                <td>{{ invoice.invoice_number }}</td>
                <td><strong>Invoice Date:</strong></td>
                <td>{{ invoice_date }}</td>
            </tr>
            <tr>
                <td><strong>Due Date:</strong></td>
                <td>{{ due_date }}</td>
                <td><strong>Payment Terms:</strong></td>
                <td>{{ client.payment_terms }} days</td>
            </tr>
        </table>
    </div>

    <div class="line-items">
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Rate</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                {% for item in line_items %}
                <tr>
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.rate }}</td>
                    <td>{{ item.amount }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="totals">
        <table>
            <tr>
                <td>Subtotal:</td>
                <td>{{ subtotal_formatted }}</td>
            </tr>
            <tr>
                <td>Tax ({{ tax_rate_percent }}):</td>
                <td>{{ tax_formatted }}</td>
            </tr>
            <tr class="total-row">
                <td>Total:</td>
                <td>{{ total_formatted }}</td>
            </tr>
            <tr>
                <td>Balance Due:</td>
                <td><strong>{{ balance_due }}</strong></td>
            </tr>
        </table>
    </div>

    {% if invoice.notes %}
    <div class="notes">
        <h4>Notes:</h4>
        <p>{{ invoice.notes }}</p>
    </div>
    {% endif %}

    <div class="footer">
        <p>Thank you for your business!</p>
        <p>Generated on {{ generation_date }}</p>
    </div>
</body>
</html>
        """

# Example usage
if __name__ == "__main__":
    # Business information
    business_info = {
        'name': 'ABC Accounting Services',
        'address': '123 Main Street, Suite 100\nBusinesstown, ST 12345',
        'phone': '(555) 123-4567',
        'email': 'info@abcaccounting.com',
        'default_tax_rate': 0.0875
    }

    # Initialize invoice generator
    generator = InvoiceGenerator(business_info)

    # Create sample client
    client = ClientInfo(
        name="XYZ Corporation",
        email="billing@xyzcorp.com",
        address="456 Corporate Dr\nBusiness City, ST 67890",
        phone="(555) 987-6543",
        billing_rate=150.0,
        payment_terms=30
    )

    # Create sample invoice
    line_items = [
        {
            'description': 'Monthly bookkeeping services',
            'quantity': 1,
            'rate': 800.00
        },
        {
            'description': 'Tax preparation consultation',
            'quantity': 3,
            'rate': 150.00
        }
    ]

    invoice = generator.create_invoice(client, line_items)

    print("Sample Invoice Created:")
    print(f"Invoice Number: {invoice.invoice_number}")
    print(f"Total: ${invoice.total:,.2f}")

    # Generate HTML
    html_invoice = generator.generate_html_invoice(invoice)
    print(f"HTML invoice generated ({len(html_invoice)} characters)")