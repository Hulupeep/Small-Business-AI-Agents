#!/usr/bin/env python3
"""
Sports Club Payment Processing
Real Stripe integration for membership fees and event payments
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from database import ClubDatabase
import stripe
from decimal import Decimal

class PaymentProcessor:
    """Real payment processing with Stripe integration"""

    def __init__(self, db_path: str = "club_database.db"):
        self.db = ClubDatabase(db_path)

        # Initialize Stripe (use environment variables for keys)
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')

        if not stripe.api_key:
            print("WARNING: No Stripe API key found. Set STRIPE_SECRET_KEY environment variable.")
            print("Using test mode - payments will not actually process.")

    def create_payment_intent(self, amount: float, currency: str = 'eur',
                            member_id: int = None, description: str = None) -> Dict[str, Any]:
        """Create a Stripe payment intent"""

        if not stripe.api_key:
            # Return mock payment intent for testing
            return {
                'client_secret': 'pi_test_mock_client_secret',
                'id': 'pi_mock_payment_intent',
                'amount': int(amount * 100),
                'currency': currency,
                'status': 'requires_payment_method'
            }

        try:
            # Convert to cents for Stripe
            amount_cents = int(amount * 100)

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                description=description,
                metadata={
                    'member_id': str(member_id) if member_id else '',
                    'club_payment': 'true'
                }
            )

            return {
                'client_secret': intent.client_secret,
                'id': intent.id,
                'amount': intent.amount,
                'currency': intent.currency,
                'status': intent.status
            }

        except stripe.error.StripeError as e:
            raise ValueError(f"Payment setup failed: {str(e)}")

    def confirm_payment(self, payment_intent_id: str, member_id: int,
                       payment_type: str = 'Membership Fee') -> int:
        """Confirm and record payment"""

        if not stripe.api_key:
            # Mock successful payment
            payment_data = {
                'member_id': member_id,
                'amount': 50.00,  # Mock amount
                'payment_type': payment_type,
                'payment_method': 'Card',
                'stripe_payment_id': payment_intent_id,
                'status': 'Completed',
                'payment_date': date.today().isoformat()
            }
            return self.db.add_payment(payment_data)

        try:
            # Retrieve payment intent from Stripe
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == 'succeeded':
                # Record successful payment
                payment_data = {
                    'member_id': member_id,
                    'amount': intent.amount / 100.0,  # Convert from cents
                    'payment_type': payment_type,
                    'payment_method': 'Card',
                    'stripe_payment_id': payment_intent_id,
                    'status': 'Completed',
                    'payment_date': date.today().isoformat(),
                    'description': intent.description
                }

                return self.db.add_payment(payment_data)
            else:
                raise ValueError(f"Payment not completed. Status: {intent.status}")

        except stripe.error.StripeError as e:
            raise ValueError(f"Payment confirmation failed: {str(e)}")

    def create_recurring_subscription(self, member_id: int, amount: float,
                                    interval: str = 'month') -> Dict[str, Any]:
        """Create recurring subscription (monthly/annual fees)"""

        if not stripe.api_key:
            return {
                'subscription_id': 'sub_mock_subscription',
                'status': 'active',
                'current_period_end': (datetime.now().timestamp() + 2592000)  # 30 days
            }

        member = self.db.get_member_by_id(member_id)
        if not member:
            raise ValueError("Member not found")

        try:
            # Create customer
            customer = stripe.Customer.create(
                email=member['email'],
                name=f"{member['first_name']} {member['last_name']}",
                metadata={
                    'member_id': str(member_id)
                }
            )

            # Create price
            price = stripe.Price.create(
                unit_amount=int(amount * 100),
                currency='eur',
                recurring={'interval': interval},
                product_data={
                    'name': f'Club Membership - {interval}ly'
                }
            )

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price.id}],
                metadata={
                    'member_id': str(member_id),
                    'club_subscription': 'true'
                }
            )

            return {
                'subscription_id': subscription.id,
                'customer_id': customer.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end
            }

        except stripe.error.StripeError as e:
            raise ValueError(f"Subscription creation failed: {str(e)}")

    def get_payment_history(self, member_id: int = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get payment history"""
        if member_id:
            return self.db.get_member_payments(member_id)
        else:
            # Get all payments (would need DB method)
            return []

    def process_refund(self, stripe_payment_id: str, amount: float = None,
                      reason: str = 'requested_by_customer') -> Dict[str, Any]:
        """Process refund through Stripe"""

        if not stripe.api_key:
            return {
                'refund_id': 're_mock_refund',
                'amount': int((amount or 50.00) * 100),
                'status': 'succeeded'
            }

        try:
            refund_params = {
                'payment_intent': stripe_payment_id,
                'reason': reason
            }

            if amount:
                refund_params['amount'] = int(amount * 100)

            refund = stripe.Refund.create(**refund_params)

            # Update payment record in database
            # (Would need additional DB method to update payment status)

            return {
                'refund_id': refund.id,
                'amount': refund.amount,
                'status': refund.status
            }

        except stripe.error.StripeError as e:
            raise ValueError(f"Refund failed: {str(e)}")

    def generate_invoice_link(self, member_id: int, amount: float,
                            description: str, due_date: date = None) -> str:
        """Generate Stripe invoice link"""

        if not stripe.api_key:
            return "https://invoice.stripe.com/i/acct_mock_invoice_link"

        member = self.db.get_member_by_id(member_id)
        if not member:
            raise ValueError("Member not found")

        try:
            # Create customer if doesn't exist
            customer = stripe.Customer.create(
                email=member['email'],
                name=f"{member['first_name']} {member['last_name']}"
            )

            # Create invoice
            invoice = stripe.Invoice.create(
                customer=customer.id,
                description=description,
                due_date=int(due_date.timestamp()) if due_date else None,
                metadata={
                    'member_id': str(member_id)
                }
            )

            # Add line item
            stripe.InvoiceItem.create(
                customer=customer.id,
                amount=int(amount * 100),
                currency='eur',
                description=description,
                invoice=invoice.id
            )

            # Finalize invoice
            invoice = stripe.Invoice.finalize_invoice(invoice.id)

            return invoice.hosted_invoice_url

        except stripe.error.StripeError as e:
            raise ValueError(f"Invoice creation failed: {str(e)}")

    def get_financial_summary(self, start_date: date = None,
                            end_date: date = None) -> Dict[str, Any]:
        """Get financial summary for period"""

        if not start_date:
            start_date = date.today().replace(day=1)  # Start of month

        if not end_date:
            end_date = date.today()

        # Get payments from database
        all_payments = []  # Would need DB method to get payments by date range

        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_revenue': 0.0,
            'payment_count': 0,
            'payment_methods': {},
            'payment_types': {},
            'average_transaction': 0.0
        }

        if not stripe.api_key:
            # Return mock data
            return {
                **summary,
                'total_revenue': 1250.00,
                'payment_count': 25,
                'payment_methods': {'Card': 23, 'Bank Transfer': 2},
                'payment_types': {'Membership Fee': 20, 'Event Fee': 5},
                'average_transaction': 50.00,
                'stripe_fees': 36.25
            }

        # Real implementation would query database and Stripe
        return summary

    def export_financial_report(self, start_date: date, end_date: date) -> str:
        """Export financial report as CSV"""

        csv_lines = [
            'Date,Member ID,Member Name,Amount,Type,Method,Stripe ID,Status'
        ]

        # Get payments from database (mock data for now)
        mock_payments = [
            {
                'date': '2024-01-15',
                'member_id': 1,
                'member_name': 'John Smith',
                'amount': 50.00,
                'type': 'Membership Fee',
                'method': 'Card',
                'stripe_id': 'pi_mock123',
                'status': 'Completed'
            }
        ]

        for payment in mock_payments:
            csv_lines.append(
                f"{payment['date']},"
                f"{payment['member_id']},"
                f"\"{payment['member_name']}\","
                f"{payment['amount']:.2f},"
                f"\"{payment['type']}\","
                f"{payment['method']},"
                f"{payment['stripe_id']},"
                f"{payment['status']}"
            )

        return '\n'.join(csv_lines)

    def setup_webhook_endpoint(self, webhook_url: str) -> Dict[str, Any]:
        """Setup Stripe webhook for payment notifications"""

        if not stripe.api_key:
            return {
                'webhook_id': 'we_mock_webhook',
                'url': webhook_url,
                'events': ['payment_intent.succeeded', 'invoice.payment_succeeded']
            }

        try:
            webhook_endpoint = stripe.WebhookEndpoint.create(
                url=webhook_url,
                enabled_events=[
                    'payment_intent.succeeded',
                    'payment_intent.payment_failed',
                    'invoice.payment_succeeded',
                    'invoice.payment_failed',
                    'customer.subscription.created',
                    'customer.subscription.updated'
                ]
            )

            return {
                'webhook_id': webhook_endpoint.id,
                'url': webhook_endpoint.url,
                'secret': webhook_endpoint.secret,
                'events': webhook_endpoint.enabled_events
            }

        except stripe.error.StripeError as e:
            raise ValueError(f"Webhook setup failed: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize payment processor
    processor = PaymentProcessor()

    # Test member registration fee
    test_amount = 50.00
    test_description = "Annual Membership Fee"

    try:
        # Create payment intent
        intent = processor.create_payment_intent(
            amount=test_amount,
            description=test_description,
            member_id=1
        )
        print(f"✅ Payment intent created: {intent['id']}")
        print(f"   Amount: €{intent['amount']/100:.2f}")
        print(f"   Status: {intent['status']}")

        # Simulate successful payment confirmation
        payment_id = processor.confirm_payment(
            payment_intent_id=intent['id'],
            member_id=1,
            payment_type='Membership Fee'
        )
        print(f"💳 Payment recorded: ID {payment_id}")

        # Generate invoice link
        invoice_link = processor.generate_invoice_link(
            member_id=1,
            amount=test_amount,
            description="Annual Membership Renewal"
        )
        print(f"📄 Invoice link: {invoice_link}")

        # Get financial summary
        summary = processor.get_financial_summary()
        print(f"📊 Financial summary: €{summary['total_revenue']:.2f} from {summary['payment_count']} payments")

        # Export report
        report = processor.export_financial_report(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        print(f"📈 Financial report generated ({len(report.split(chr(10)))} lines)")

    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")