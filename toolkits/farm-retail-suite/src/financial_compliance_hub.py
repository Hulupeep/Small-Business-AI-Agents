"""
Financial & Compliance Hub Agent
Comprehensive financial management and regulatory compliance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import uuid

logger = logging.getLogger(__name__)

class PaymentChannel(Enum):
    FARM_SHOP_CASH = "farm_shop_cash"
    FARM_SHOP_CARD = "farm_shop_card"
    FARMERS_MARKET = "farmers_market"
    ONLINE_PAYMENT = "online_payment"
    BANK_TRANSFER = "bank_transfer"
    B2B_INVOICE = "b2b_invoice"
    CSA_SUBSCRIPTION = "csa_subscription"

class GrantType(Enum):
    CAP_BPS = "cap_bps"  # Common Agricultural Policy Basic Payment Scheme
    RURAL_DEVELOPMENT = "rural_development"
    ORGANIC_CERTIFICATION = "organic_certification"
    ENVIRONMENTAL_STEWARDSHIP = "environmental_stewardship"
    YOUNG_FARMER = "young_farmer"
    INNOVATION = "innovation"
    CLIMATE_ACTION = "climate_action"

class CertificationStandard(Enum):
    ORGANIC_EU = "organic_eu"
    GLOBAL_GAP = "global_gap"
    BRC_FOOD_SAFETY = "brc_food_safety"
    IFS_FOOD = "ifs_food"
    RAINFOREST_ALLIANCE = "rainforest_alliance"
    FAIRTRADE = "fairtrade"

class ComplianceArea(Enum):
    FOOD_SAFETY = "food_safety"
    ORGANIC_STANDARDS = "organic_standards"
    ENVIRONMENTAL = "environmental"
    ANIMAL_WELFARE = "animal_welfare"
    WORKER_SAFETY = "worker_safety"
    DATA_PROTECTION = "data_protection"

@dataclass
class PaymentRecord:
    payment_id: str
    date: datetime
    amount: Decimal
    channel: PaymentChannel
    customer_id: Optional[str]
    order_id: Optional[str]
    vat_amount: Decimal
    net_amount: Decimal
    reconciled: bool = False
    notes: str = ""

@dataclass
class Grant:
    grant_id: str
    grant_type: GrantType
    title: str
    funding_body: str
    application_deadline: datetime
    funding_amount: Decimal
    eligibility_criteria: List[str]
    required_documents: List[str]
    status: str = "available"
    application_date: Optional[datetime] = None
    success_probability: float = 0.0

@dataclass
class ComplianceRecord:
    record_id: str
    compliance_area: ComplianceArea
    certification_standard: Optional[CertificationStandard]
    inspection_date: datetime
    inspector: str
    findings: List[Dict]
    corrective_actions: List[Dict]
    compliance_score: int  # 0-100
    next_inspection: Optional[datetime] = None
    certificate_expiry: Optional[datetime] = None

@dataclass
class FinancialMetrics:
    period_start: datetime
    period_end: datetime
    total_revenue: Decimal
    revenue_by_channel: Dict[PaymentChannel, Decimal]
    total_expenses: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    vat_collected: Decimal
    vat_payable: Decimal

class FinancialComplianceHub:
    """
    Comprehensive financial management and regulatory compliance system
    for agricultural businesses.
    """

    def __init__(self, farm_config: Dict):
        self.farm_config = farm_config
        self.payments: Dict[str, PaymentRecord] = {}
        self.grants: Dict[str, Grant] = {}
        self.compliance_records: Dict[str, ComplianceRecord] = {}
        self.expenses: Dict[str, Dict] = {}
        self.vat_rates = {
            'food_products': Decimal('0.09'),
            'services': Decimal('0.21'),
            'agricultural_inputs': Decimal('0.09')
        }

    async def initialize(self):
        """Initialize the financial and compliance management system"""
        logger.info("Initializing Financial & Compliance Hub")
        await self._load_grant_opportunities()
        await self._setup_compliance_framework()
        await self._load_expense_categories()
        logger.info("Financial & Compliance Hub initialized successfully")

    async def _load_grant_opportunities(self):
        """Load available grant opportunities"""
        # Sample grant opportunities - in production would integrate with funding databases
        sample_grants = [
            {
                'grant_type': GrantType.CAP_BPS,
                'title': 'Basic Payment Scheme 2024',
                'funding_body': 'European Commission - CAP',
                'application_deadline': datetime(2024, 5, 15),
                'funding_amount': Decimal('12500.00'),
                'eligibility_criteria': [
                    'Active farmer status',
                    'Minimum 5 hectares eligible land',
                    'Compliance with greening requirements'
                ],
                'required_documents': [
                    'Land register certificate',
                    'Crop declaration',
                    'Environmental compliance report'
                ]
            },
            {
                'grant_type': GrantType.ORGANIC_CERTIFICATION,
                'title': 'Organic Certification Support',
                'funding_body': 'Ministry of Agriculture',
                'application_deadline': datetime(2024, 8, 31),
                'funding_amount': Decimal('3500.00'),
                'eligibility_criteria': [
                    'Converting to organic production',
                    'Minimum 2-year conversion period',
                    'Certified organic inspector assessment'
                ],
                'required_documents': [
                    'Conversion plan',
                    'Organic management plan',
                    'Financial records'
                ]
            },
            {
                'grant_type': GrantType.ENVIRONMENTAL_STEWARDSHIP,
                'title': 'Agri-Environment Climate Scheme',
                'funding_body': 'Rural Payments Agency',
                'application_deadline': datetime(2024, 12, 31),
                'funding_amount': Decimal('8000.00'),
                'eligibility_criteria': [
                    'Environmental management commitment',
                    'Biodiversity enhancement measures',
                    '5-year scheme commitment'
                ],
                'required_documents': [
                    'Environmental assessment',
                    'Management plan',
                    'Monitoring proposals'
                ]
            }
        ]

        for grant_data in sample_grants:
            grant_id = f"grant_{uuid.uuid4().hex[:8]}"
            grant = Grant(
                grant_id=grant_id,
                **grant_data
            )
            self.grants[grant_id] = grant

        logger.info(f"Loaded {len(self.grants)} grant opportunities")

    async def _setup_compliance_framework(self):
        """Setup compliance monitoring framework"""
        # Sample compliance records - in production would load from inspections database
        sample_compliance = [
            {
                'compliance_area': ComplianceArea.ORGANIC_STANDARDS,
                'certification_standard': CertificationStandard.ORGANIC_EU,
                'inspection_date': datetime(2024, 6, 15),
                'inspector': 'SKAL Biocontrole - Inspector #456',
                'findings': [
                    {'area': 'Record keeping', 'status': 'compliant', 'notes': 'Excellent documentation'},
                    {'area': 'Input usage', 'status': 'compliant', 'notes': 'All inputs verified organic'},
                    {'area': 'Buffer zones', 'status': 'minor_issue', 'notes': 'Need 2m additional buffer on north field'}
                ],
                'corrective_actions': [
                    {'action': 'Extend buffer zone', 'deadline': datetime(2024, 8, 1), 'status': 'completed'}
                ],
                'compliance_score': 95,
                'next_inspection': datetime(2025, 6, 15),
                'certificate_expiry': datetime(2025, 12, 31)
            },
            {
                'compliance_area': ComplianceArea.FOOD_SAFETY,
                'certification_standard': CertificationStandard.BRC_FOOD_SAFETY,
                'inspection_date': datetime(2024, 4, 20),
                'inspector': 'Food Safety Authority - Team Delta',
                'findings': [
                    {'area': 'HACCP implementation', 'status': 'compliant', 'notes': 'Well documented system'},
                    {'area': 'Traceability', 'status': 'compliant', 'notes': 'Excellent tracking records'},
                    {'area': 'Storage facilities', 'status': 'compliant', 'notes': 'Temperature controls effective'}
                ],
                'corrective_actions': [],
                'compliance_score': 98,
                'next_inspection': datetime(2025, 4, 20)
            }
        ]

        for compliance_data in sample_compliance:
            record_id = f"compliance_{uuid.uuid4().hex[:8]}"
            record = ComplianceRecord(
                record_id=record_id,
                **compliance_data
            )
            self.compliance_records[record_id] = record

    async def _load_expense_categories(self):
        """Load expense tracking categories"""
        self.expense_categories = {
            'seeds_plants': {'vat_rate': 'agricultural_inputs', 'category': 'direct_costs'},
            'fertilizers': {'vat_rate': 'agricultural_inputs', 'category': 'direct_costs'},
            'pesticides': {'vat_rate': 'agricultural_inputs', 'category': 'direct_costs'},
            'feed': {'vat_rate': 'agricultural_inputs', 'category': 'direct_costs'},
            'fuel': {'vat_rate': 'services', 'category': 'operational'},
            'equipment_repair': {'vat_rate': 'services', 'category': 'operational'},
            'insurance': {'vat_rate': 'services', 'category': 'overhead'},
            'utilities': {'vat_rate': 'services', 'category': 'overhead'},
            'labor': {'vat_rate': None, 'category': 'labor'},
            'professional_services': {'vat_rate': 'services', 'category': 'overhead'}
        }

    async def record_payment(self, payment_data: Dict) -> str:
        """Record payment transaction"""
        payment_id = f"pay_{uuid.uuid4().hex[:8]}"

        amount = Decimal(str(payment_data['amount']))
        channel = PaymentChannel(payment_data['channel'])

        # Calculate VAT
        vat_rate = self.vat_rates.get('food_products', Decimal('0.09'))
        if channel in [PaymentChannel.B2B_INVOICE] and payment_data.get('vat_exempt', False):
            vat_rate = Decimal('0')

        # VAT calculation (amount includes VAT)
        vat_amount = amount * vat_rate / (Decimal('1') + vat_rate)
        net_amount = amount - vat_amount

        payment = PaymentRecord(
            payment_id=payment_id,
            date=datetime.fromisoformat(payment_data['date']),
            amount=amount,
            channel=channel,
            customer_id=payment_data.get('customer_id'),
            order_id=payment_data.get('order_id'),
            vat_amount=vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            net_amount=net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            notes=payment_data.get('notes', '')
        )

        self.payments[payment_id] = payment
        logger.info(f"Recorded payment {payment_id}: €{amount:.2f} via {channel.value}")
        return payment_id

    async def record_expense(self, expense_data: Dict) -> str:
        """Record business expense"""
        expense_id = f"exp_{uuid.uuid4().hex[:8]}"

        amount = Decimal(str(expense_data['amount']))
        category = expense_data['category']

        # Calculate VAT if applicable
        category_info = self.expense_categories.get(category, {})
        vat_rate_key = category_info.get('vat_rate')
        vat_amount = Decimal('0')

        if vat_rate_key and vat_rate_key in self.vat_rates:
            vat_rate = self.vat_rates[vat_rate_key]
            # Amount includes VAT
            vat_amount = amount * vat_rate / (Decimal('1') + vat_rate)

        net_amount = amount - vat_amount

        expense = {
            'expense_id': expense_id,
            'date': datetime.fromisoformat(expense_data['date']),
            'amount': amount,
            'net_amount': net_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'vat_amount': vat_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            'category': category,
            'description': expense_data['description'],
            'supplier': expense_data.get('supplier', ''),
            'invoice_number': expense_data.get('invoice_number', ''),
            'tax_deductible': category_info.get('category') in ['direct_costs', 'operational', 'overhead']
        }

        self.expenses[expense_id] = expense
        logger.info(f"Recorded expense {expense_id}: €{amount:.2f} for {category}")
        return expense_id

    async def reconcile_payments(self, bank_statement: List[Dict]) -> Dict:
        """Reconcile payments against bank statement"""
        reconciliation_results = {
            'matched_payments': [],
            'unmatched_bank_entries': [],
            'unmatched_payments': [],
            'discrepancies': []
        }

        # Get unreconciled payments
        unreconciled_payments = [p for p in self.payments.values() if not p.reconciled]

        # Attempt to match bank entries with payments
        for bank_entry in bank_statement:
            bank_amount = Decimal(str(bank_entry['amount']))
            bank_date = datetime.fromisoformat(bank_entry['date'])

            # Look for matching payment within 3 days
            matched_payment = None
            for payment in unreconciled_payments:
                date_diff = abs((payment.date - bank_date).days)
                amount_diff = abs(payment.amount - bank_amount)

                if date_diff <= 3 and amount_diff <= Decimal('0.01'):
                    matched_payment = payment
                    break

            if matched_payment:
                matched_payment.reconciled = True
                reconciliation_results['matched_payments'].append({
                    'payment_id': matched_payment.payment_id,
                    'bank_reference': bank_entry.get('reference', ''),
                    'amount': float(bank_amount),
                    'date': bank_date.isoformat()
                })
                unreconciled_payments.remove(matched_payment)
            else:
                reconciliation_results['unmatched_bank_entries'].append(bank_entry)

        # Record remaining unmatched payments
        for payment in unreconciled_payments:
            reconciliation_results['unmatched_payments'].append({
                'payment_id': payment.payment_id,
                'amount': float(payment.amount),
                'date': payment.date.isoformat(),
                'channel': payment.channel.value
            })

        return reconciliation_results

    async def analyze_grant_eligibility(self) -> Dict:
        """Analyze eligibility for available grants"""
        eligibility_analysis = {
            'eligible_grants': [],
            'partially_eligible': [],
            'ineligible_grants': [],
            'total_potential_funding': Decimal('0')
        }

        farm_characteristics = self._get_farm_characteristics()

        for grant in self.grants.values():
            if grant.status != 'available':
                continue

            eligibility_score = await self._calculate_grant_eligibility_score(grant, farm_characteristics)

            grant_info = {
                'grant_id': grant.grant_id,
                'title': grant.title,
                'funding_amount': float(grant.funding_amount),
                'deadline': grant.application_deadline.isoformat(),
                'eligibility_score': eligibility_score,
                'success_probability': self._estimate_success_probability(grant, farm_characteristics)
            }

            if eligibility_score >= 80:
                eligibility_analysis['eligible_grants'].append(grant_info)
                eligibility_analysis['total_potential_funding'] += grant.funding_amount
            elif eligibility_score >= 50:
                eligibility_analysis['partially_eligible'].append(grant_info)
            else:
                eligibility_analysis['ineligible_grants'].append(grant_info)

        eligibility_analysis['total_potential_funding'] = float(eligibility_analysis['total_potential_funding'])

        return eligibility_analysis

    def _get_farm_characteristics(self) -> Dict:
        """Get current farm characteristics for grant eligibility"""
        return {
            'total_area': self.farm_config.get('total_area', 50),
            'organic_certified': True,  # From compliance records
            'young_farmer': self.farm_config.get('farmer_age', 35) < 40,
            'environmental_measures': True,
            'direct_sales': True,
            'diversified_income': True
        }

    async def _calculate_grant_eligibility_score(self, grant: Grant, farm_chars: Dict) -> int:
        """Calculate eligibility score for specific grant"""
        score = 0

        if grant.grant_type == GrantType.CAP_BPS:
            if farm_chars['total_area'] >= 5:
                score += 40
            if farm_chars['environmental_measures']:
                score += 30
            score += 30  # Assume basic compliance met

        elif grant.grant_type == GrantType.ORGANIC_CERTIFICATION:
            if farm_chars['organic_certified']:
                score += 50
            else:
                score += 30  # Converting to organic
            if farm_chars['total_area'] >= 2:
                score += 25
            score += 25  # Assume documentation ready

        elif grant.grant_type == GrantType.ENVIRONMENTAL_STEWARDSHIP:
            if farm_chars['environmental_measures']:
                score += 40
            if farm_chars['organic_certified']:
                score += 30
            if farm_chars['total_area'] >= 10:
                score += 30

        elif grant.grant_type == GrantType.YOUNG_FARMER:
            if farm_chars['young_farmer']:
                score += 50
            if farm_chars['diversified_income']:
                score += 25
            if farm_chars['direct_sales']:
                score += 25

        return min(score, 100)

    def _estimate_success_probability(self, grant: Grant, farm_chars: Dict) -> float:
        """Estimate probability of grant application success"""
        base_probability = 0.3  # 30% base success rate

        # Adjust based on grant type competitiveness
        competitiveness_factors = {
            GrantType.CAP_BPS: 0.8,  # High success rate for eligible applicants
            GrantType.ORGANIC_CERTIFICATION: 0.6,
            GrantType.ENVIRONMENTAL_STEWARDSHIP: 0.4,
            GrantType.YOUNG_FARMER: 0.5,
            GrantType.INNOVATION: 0.2
        }

        adjusted_probability = base_probability * competitiveness_factors.get(grant.grant_type, 0.3)

        # Adjust based on farm characteristics
        if farm_chars['organic_certified']:
            adjusted_probability *= 1.2
        if farm_chars['young_farmer']:
            adjusted_probability *= 1.1
        if farm_chars['direct_sales']:
            adjusted_probability *= 1.1

        return min(adjusted_probability, 0.95)

    async def prepare_grant_application(self, grant_id: str) -> Dict:
        """Prepare grant application with required documentation"""
        grant = self.grants.get(grant_id)
        if not grant:
            return {'error': f'Grant {grant_id} not found'}

        application_package = {
            'grant_details': {
                'title': grant.title,
                'funding_amount': float(grant.funding_amount),
                'deadline': grant.application_deadline.isoformat()
            },
            'required_documents': grant.required_documents,
            'eligibility_checklist': grant.eligibility_criteria,
            'supporting_data': await self._gather_supporting_data(grant),
            'application_timeline': self._create_application_timeline(grant),
            'estimated_success_probability': self._estimate_success_probability(grant, self._get_farm_characteristics())
        }

        return application_package

    async def _gather_supporting_data(self, grant: Grant) -> Dict:
        """Gather supporting data for grant application"""
        supporting_data = {}

        # Financial data
        if grant.grant_type in [GrantType.CAP_BPS, GrantType.ORGANIC_CERTIFICATION]:
            recent_metrics = await self.generate_financial_report(
                datetime.now() - timedelta(days=365),
                datetime.now()
            )
            supporting_data['financial_summary'] = {
                'annual_revenue': float(recent_metrics.total_revenue),
                'profit_margin': float(recent_metrics.net_profit / recent_metrics.total_revenue * 100) if recent_metrics.total_revenue > 0 else 0
            }

        # Compliance data
        if grant.grant_type == GrantType.ORGANIC_CERTIFICATION:
            organic_compliance = [
                record for record in self.compliance_records.values()
                if record.compliance_area == ComplianceArea.ORGANIC_STANDARDS
            ]
            if organic_compliance:
                latest_record = max(organic_compliance, key=lambda x: x.inspection_date)
                supporting_data['organic_compliance'] = {
                    'compliance_score': latest_record.compliance_score,
                    'last_inspection': latest_record.inspection_date.isoformat(),
                    'certificate_expiry': latest_record.certificate_expiry.isoformat() if latest_record.certificate_expiry else None
                }

        return supporting_data

    def _create_application_timeline(self, grant: Grant) -> List[Dict]:
        """Create application preparation timeline"""
        deadline = grant.application_deadline
        today = datetime.now()
        days_until_deadline = (deadline - today).days

        timeline = []

        if days_until_deadline > 60:
            timeline.append({
                'task': 'Gather required documents',
                'deadline': (today + timedelta(days=14)).isoformat(),
                'priority': 'high'
            })
            timeline.append({
                'task': 'Prepare financial statements',
                'deadline': (today + timedelta(days=21)).isoformat(),
                'priority': 'high'
            })
            timeline.append({
                'task': 'Draft application',
                'deadline': (today + timedelta(days=35)).isoformat(),
                'priority': 'medium'
            })
            timeline.append({
                'task': 'Review and submit',
                'deadline': (deadline - timedelta(days=7)).isoformat(),
                'priority': 'high'
            })
        else:
            timeline.append({
                'task': 'URGENT: Expedited application preparation',
                'deadline': (deadline - timedelta(days=3)).isoformat(),
                'priority': 'critical'
            })

        return timeline

    async def generate_vat_return(self, period_start: datetime, period_end: datetime) -> Dict:
        """Generate VAT return for specified period"""
        period_payments = [
            p for p in self.payments.values()
            if period_start <= p.date <= period_end
        ]

        period_expenses = [
            e for e in self.expenses.values()
            if period_start <= datetime.fromisoformat(e['date']) <= period_end
        ]

        vat_collected = sum(p.vat_amount for p in period_payments)
        vat_paid = sum(Decimal(str(e['vat_amount'])) for e in period_expenses if e['vat_amount'] > 0)

        vat_return = {
            'period': {
                'start_date': period_start.isoformat(),
                'end_date': period_end.isoformat()
            },
            'vat_collected': float(vat_collected),
            'vat_paid': float(vat_paid),
            'net_vat_payable': float(vat_collected - vat_paid),
            'breakdown': {
                'sales_vat_9_percent': float(sum(p.vat_amount for p in period_payments if p.channel != PaymentChannel.B2B_INVOICE)),
                'sales_vat_exempt': float(sum(p.vat_amount for p in period_payments if p.channel == PaymentChannel.B2B_INVOICE)),
                'input_vat_recoverable': float(vat_paid)
            },
            'payment_due_date': (period_end + timedelta(days=30)).isoformat()
        }

        return vat_return

    async def generate_financial_report(self, start_date: datetime, end_date: datetime) -> FinancialMetrics:
        """Generate comprehensive financial report"""
        period_payments = [
            p for p in self.payments.values()
            if start_date <= p.date <= end_date
        ]

        period_expenses = [
            e for e in self.expenses.values()
            if start_date <= datetime.fromisoformat(e['date']) <= end_date
        ]

        # Calculate revenue by channel
        revenue_by_channel = {}
        total_revenue = Decimal('0')
        total_vat_collected = Decimal('0')

        for payment in period_payments:
            channel = payment.channel
            revenue_by_channel[channel] = revenue_by_channel.get(channel, Decimal('0')) + payment.net_amount
            total_revenue += payment.net_amount
            total_vat_collected += payment.vat_amount

        # Calculate expenses
        total_expenses = sum(Decimal(str(e['net_amount'])) for e in period_expenses)
        total_vat_paid = sum(Decimal(str(e['vat_amount'])) for e in period_expenses)

        # Calculate profit metrics
        gross_profit = total_revenue - sum(
            Decimal(str(e['net_amount'])) for e in period_expenses
            if self.expense_categories.get(e['category'], {}).get('category') == 'direct_costs'
        )

        net_profit = total_revenue - total_expenses

        return FinancialMetrics(
            period_start=start_date,
            period_end=end_date,
            total_revenue=total_revenue,
            revenue_by_channel=revenue_by_channel,
            total_expenses=total_expenses,
            gross_profit=gross_profit,
            net_profit=net_profit,
            vat_collected=total_vat_collected,
            vat_payable=total_vat_collected - total_vat_paid
        )

    async def check_compliance_status(self) -> Dict:
        """Check current compliance status across all areas"""
        compliance_status = {
            'overall_score': 0,
            'compliance_areas': {},
            'expiring_certificates': [],
            'required_actions': [],
            'inspection_schedule': []
        }

        total_score = 0
        area_count = 0

        for record in self.compliance_records.values():
            area = record.compliance_area.value
            compliance_status['compliance_areas'][area] = {
                'score': record.compliance_score,
                'last_inspection': record.inspection_date.isoformat(),
                'status': 'compliant' if record.compliance_score >= 85 else 'needs_attention'
            }

            total_score += record.compliance_score
            area_count += 1

            # Check for expiring certificates
            if record.certificate_expiry:
                days_until_expiry = (record.certificate_expiry - datetime.now()).days
                if days_until_expiry <= 90:
                    compliance_status['expiring_certificates'].append({
                        'area': area,
                        'expiry_date': record.certificate_expiry.isoformat(),
                        'days_remaining': days_until_expiry
                    })

            # Check for upcoming inspections
            if record.next_inspection:
                days_until_inspection = (record.next_inspection - datetime.now()).days
                if days_until_inspection <= 30:
                    compliance_status['inspection_schedule'].append({
                        'area': area,
                        'inspection_date': record.next_inspection.isoformat(),
                        'days_remaining': days_until_inspection
                    })

            # Generate required actions
            for action in record.corrective_actions:
                if action['status'] != 'completed':
                    compliance_status['required_actions'].append({
                        'area': area,
                        'action': action['action'],
                        'deadline': action['deadline'],
                        'priority': 'high' if (datetime.fromisoformat(action['deadline']) - datetime.now()).days <= 7 else 'medium'
                    })

        compliance_status['overall_score'] = int(total_score / area_count) if area_count > 0 else 0

        return compliance_status

# Example usage and testing
async def main():
    """Example usage of Financial & Compliance Hub"""
    farm_config = {
        'name': 'Green Valley Farm',
        'total_area': 50,
        'farmer_age': 32
    }

    financial_hub = FinancialComplianceHub(farm_config)
    await financial_hub.initialize()

    # Record a payment
    payment_data = {
        'amount': '125.50',
        'channel': 'farm_shop_card',
        'date': datetime.now().isoformat(),
        'customer_id': 'cust_001',
        'order_id': 'order_001'
    }

    payment_id = await financial_hub.record_payment(payment_data)
    print(f"Recorded payment: {payment_id}")

    # Record an expense
    expense_data = {
        'amount': '85.00',
        'category': 'seeds_plants',
        'date': datetime.now().isoformat(),
        'description': 'Organic tomato seeds',
        'supplier': 'Seeds R Us'
    }

    expense_id = await financial_hub.record_expense(expense_data)
    print(f"Recorded expense: {expense_id}")

    # Analyze grant eligibility
    grant_analysis = await financial_hub.analyze_grant_eligibility()
    print("Grant eligibility analysis:", grant_analysis)

    # Generate financial report
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    financial_report = await financial_hub.generate_financial_report(start_date, end_date)
    print(f"Financial Report - Revenue: €{financial_report.total_revenue:.2f}, Profit: €{financial_report.net_profit:.2f}")

    # Check compliance status
    compliance = await financial_hub.check_compliance_status()
    print("Compliance status:", compliance)

if __name__ == "__main__":
    asyncio.run(main())