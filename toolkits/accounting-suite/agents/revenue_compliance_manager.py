"""
Revenue Compliance Manager Agent
Handles all Irish Revenue compliance, ROS integration, and tax calculations
"""

import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TaxYear(Enum):
    CURRENT = "2024"
    PREVIOUS = "2023"

class EntityType(Enum):
    SOLE_TRADER = "sole_trader"
    LIMITED_COMPANY = "limited_company"
    PARTNERSHIP = "partnership"

@dataclass
class TaxCalculation:
    gross_income: float
    income_tax: float
    usc: float
    prsi: float
    total_liability: float
    credits_available: float
    net_liability: float

@dataclass
class DeadlineAlert:
    client_id: str
    deadline_type: str
    due_date: datetime.date
    days_remaining: int
    priority: str
    form_required: str

class RevenueComplianceManager:
    """
    Irish Revenue Compliance Manager
    Handles ROS integration, tax calculations, and deadline management
    """

    def __init__(self):
        self.current_tax_year = 2024
        self.vat_rates = {
            'standard': 0.23,
            'reduced_accommodation': 0.135,
            'reduced_restaurant': 0.135,
            'super_reduced_newspapers': 0.09,
            'zero': 0.0
        }

        # 2024 Irish tax rates and bands
        self.income_tax_bands = {
            'single': 42000,  # Standard rate band
            'married_joint': 84000,
            'married_separate': 42000
        }

        self.corporation_tax_rates = {
            'trading_income': 0.125,  # 12.5%
            'passive_income': 0.25,   # 25%
            'close_company_surcharge': 0.20
        }

        # Revenue deadlines by entity type
        self.revenue_deadlines = {
            'sole_trader': {
                'form_11': {'month': 10, 'day': 31},  # October 31st
                'preliminary_tax': {'month': 10, 'day': 31}
            },
            'limited_company': {
                'corporation_tax': {'months_after_year_end': 9},
                'annual_return': {'month': 11, 'day': 30}  # CRO filing
            },
            'vat_registered': {
                'vat_return_bi_monthly': [1, 3, 5, 7, 9, 11],  # 19th of following month
                'vat_return_monthly': list(range(1, 13))
            }
        }

    def calculate_income_tax(self, income: float, filing_status: str = 'single') -> TaxCalculation:
        """Calculate Irish personal income tax, USC, and PRSI"""

        # Income tax calculation
        standard_rate_band = self.income_tax_bands[filing_status]

        if income <= standard_rate_band:
            income_tax = income * 0.20
        else:
            income_tax = (standard_rate_band * 0.20) + ((income - standard_rate_band) * 0.40)

        # USC calculation (2024 rates)
        usc = self._calculate_usc(income)

        # PRSI calculation (4% on income over €352 per week)
        weekly_income = income / 52
        if weekly_income > 352:
            prsi = income * 0.04
        else:
            prsi = 0

        # Standard tax credits (2024)
        personal_credit = 1875  # Single person
        employee_credit = 1875
        total_credits = personal_credit + employee_credit

        gross_liability = income_tax + usc + prsi
        net_liability = max(0, gross_liability - total_credits)

        return TaxCalculation(
            gross_income=income,
            income_tax=income_tax,
            usc=usc,
            prsi=prsi,
            total_liability=gross_liability,
            credits_available=total_credits,
            net_liability=net_liability
        )

    def _calculate_usc(self, income: float) -> float:
        """Calculate Universal Social Charge"""
        usc_bands = [
            (12012, 0.005),   # 0.5% on first €12,012
            (25760, 0.02),    # 2% on next €13,748
            (70044, 0.04),    # 4% on next €44,284
            (float('inf'), 0.08)  # 8% on balance
        ]

        usc_total = 0
        remaining_income = income
        previous_threshold = 0

        for threshold, rate in usc_bands:
            if remaining_income <= 0:
                break

            taxable_in_band = min(remaining_income, threshold - previous_threshold)
            usc_total += taxable_in_band * rate
            remaining_income -= taxable_in_band
            previous_threshold = threshold

        return usc_total

    def calculate_corporation_tax(self, trading_profit: float, passive_income: float = 0) -> Dict:
        """Calculate Irish corporation tax"""

        trading_tax = trading_profit * self.corporation_tax_rates['trading_income']
        passive_tax = passive_income * self.corporation_tax_rates['passive_income']

        total_profit = trading_profit + passive_income
        total_tax = trading_tax + passive_tax

        # Close company surcharge check (undistributed profits)
        distributable_profit = total_profit - total_tax

        return {
            'trading_profit': trading_profit,
            'passive_income': passive_income,
            'trading_tax': trading_tax,
            'passive_tax': passive_tax,
            'total_tax': total_tax,
            'distributable_profit': distributable_profit,
            'effective_rate': (total_tax / total_profit) * 100 if total_profit > 0 else 0
        }

    def calculate_vat_liability(self, transactions: List[Dict]) -> Dict:
        """Calculate VAT liability from transaction data"""

        output_vat = 0  # VAT charged on sales
        input_vat = 0   # VAT paid on purchases

        for transaction in transactions:
            vat_rate = transaction.get('vat_rate', 0)
            amount = transaction.get('net_amount', 0)
            transaction_type = transaction.get('type')  # 'sale' or 'purchase'

            vat_amount = amount * vat_rate

            if transaction_type == 'sale':
                output_vat += vat_amount
            elif transaction_type == 'purchase':
                input_vat += vat_amount

        net_vat_due = output_vat - input_vat

        return {
            'output_vat': round(output_vat, 2),
            'input_vat': round(input_vat, 2),
            'net_vat_due': round(net_vat_due, 2),
            'return_period': datetime.date.today().strftime('%Y-%m')
        }

    def get_upcoming_deadlines(self, client_data: List[Dict]) -> List[DeadlineAlert]:
        """Generate deadline alerts for all clients"""

        alerts = []
        today = datetime.date.today()

        for client in client_data:
            client_id = client['id']
            entity_type = client['entity_type']
            year_end = client.get('year_end', datetime.date(today.year, 12, 31))

            if entity_type == 'sole_trader':
                # Form 11 deadline (October 31st)
                form_11_deadline = datetime.date(today.year, 10, 31)
                if form_11_deadline >= today:
                    days_remaining = (form_11_deadline - today).days
                    priority = 'HIGH' if days_remaining <= 30 else 'MEDIUM'

                    alerts.append(DeadlineAlert(
                        client_id=client_id,
                        deadline_type='Form 11 Filing',
                        due_date=form_11_deadline,
                        days_remaining=days_remaining,
                        priority=priority,
                        form_required='Form 11'
                    ))

            elif entity_type == 'limited_company':
                # Corporation tax deadline (9 months after year-end)
                ct_deadline = year_end + datetime.timedelta(days=275)  # Approx 9 months
                if ct_deadline >= today:
                    days_remaining = (ct_deadline - today).days
                    priority = 'HIGH' if days_remaining <= 30 else 'MEDIUM'

                    alerts.append(DeadlineAlert(
                        client_id=client_id,
                        deadline_type='Corporation Tax',
                        due_date=ct_deadline,
                        days_remaining=days_remaining,
                        priority=priority,
                        form_required='CT1'
                    ))

        # Sort by days remaining (most urgent first)
        alerts.sort(key=lambda x: x.days_remaining)
        return alerts

    def validate_vat_number(self, vat_number: str) -> bool:
        """Validate Irish VAT number format"""

        # Irish VAT numbers: IE + 7 digits + 1 letter + 1 letter/digit
        # or IE + 7 digits + 2 letters
        if not vat_number.startswith('IE'):
            return False

        if len(vat_number) != 10:
            return False

        # Remove IE prefix
        number_part = vat_number[2:]

        # Check format: 7 digits + 1 letter + 1 letter/digit
        if len(number_part) == 8:
            return (number_part[:7].isdigit() and
                    number_part[7].isalpha() and
                    (number_part[8].isalpha() or number_part[8].isdigit()))

        return False

    def generate_ros_xml(self, return_data: Dict, return_type: str) -> str:
        """Generate ROS-compliant XML for electronic filing"""

        timestamp = datetime.datetime.now().isoformat()

        if return_type == 'VAT3':
            xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<ROS_VAT3_Return xmlns="http://www.revenue.ie/schemas/vat">
    <Header>
        <Timestamp>{timestamp}</Timestamp>
        <TaxNumber>{return_data['tax_number']}</TaxNumber>
        <Period>{return_data['period']}</Period>
    </Header>
    <VATLiability>
        <OutputVAT>{return_data['output_vat']}</OutputVAT>
        <InputVAT>{return_data['input_vat']}</InputVAT>
        <NetVATDue>{return_data['net_vat_due']}</NetVATDue>
    </VATLiability>
</ROS_VAT3_Return>"""

        elif return_type == 'CT1':
            xml_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<ROS_CT1_Return xmlns="http://www.revenue.ie/schemas/ct">
    <Header>
        <Timestamp>{timestamp}</Timestamp>
        <CompanyNumber>{return_data['company_number']}</CompanyNumber>
        <YearEnd>{return_data['year_end']}</YearEnd>
    </Header>
    <TaxLiability>
        <TradingProfit>{return_data['trading_profit']}</TradingProfit>
        <CorporationTax>{return_data['corporation_tax']}</CorporationTax>
    </TaxLiability>
</ROS_CT1_Return>"""

        return xml_template

    def submit_to_ros(self, xml_data: str, certificate_path: str) -> Dict:
        """Submit return to Revenue Online Service"""

        # This would integrate with actual ROS API
        # Requires digital certificate authentication

        submission_result = {
            'submission_id': f"ROS_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'status': 'SUBMITTED',
            'timestamp': datetime.datetime.now().isoformat(),
            'acknowledgment_code': 'ACK_12345'
        }

        return submission_result

    def monitor_compliance_status(self, client_list: List[str]) -> Dict:
        """Monitor overall compliance status across all clients"""

        total_clients = len(client_list)
        compliant_clients = 0
        overdue_returns = 0
        pending_submissions = 0

        # This would query actual ROS status for each client
        # For demo purposes, using sample data

        compliance_report = {
            'total_clients': total_clients,
            'compliance_rate': (compliant_clients / total_clients) * 100,
            'overdue_returns': overdue_returns,
            'pending_submissions': pending_submissions,
            'next_major_deadline': datetime.date(2024, 10, 31),
            'high_priority_alerts': 5
        }

        return compliance_report

# Example usage
if __name__ == "__main__":
    rcm = RevenueComplianceManager()

    # Test income tax calculation
    tax_calc = rcm.calculate_income_tax(75000, 'single')
    print(f"Tax liability for €75,000 income: €{tax_calc.net_liability:.2f}")

    # Test corporation tax calculation
    corp_tax = rcm.calculate_corporation_tax(500000, 50000)
    print(f"Corporation tax on €500k trading + €50k passive: €{corp_tax['total_tax']:.2f}")

    # Test VAT number validation
    valid_vat = rcm.validate_vat_number("IE1234567A1")
    print(f"VAT number validation: {valid_vat}")