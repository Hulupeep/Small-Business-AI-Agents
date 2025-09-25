"""
Insurance & Billing Hub Agent
Automated financial management for dental practices
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json
import uuid

class InsuranceBillingHub:
    """AI-powered insurance and billing management"""

    def __init__(self, llm: ChatOpenAI, practice_config: Dict[str, Any]):
        self.llm = llm
        self.practice_config = practice_config
        self.claims_database = {}
        self.billing_database = {}
        self.payment_plans = {}
        self.outstanding_balances = {}
        self.insurance_providers = self._initialize_insurance_providers()
        self.treatment_codes = self._initialize_treatment_codes()

    def _initialize_insurance_providers(self) -> Dict[str, Any]:
        """Initialize Irish insurance provider information"""
        return {
            'VHI': {
                'api_endpoint': 'https://api.vhi.ie/claims',
                'coverage_levels': {
                    'Plan_A': {'preventive': 0.8, 'basic': 0.6, 'major': 0.5, 'annual_limit': 1500},
                    'Plan_B': {'preventive': 0.9, 'basic': 0.7, 'major': 0.6, 'annual_limit': 2000},
                    'Plan_C': {'preventive': 1.0, 'basic': 0.8, 'major': 0.7, 'annual_limit': 3000}
                },
                'claim_processing_time': 5,  # days
                'electronic_claims': True
            },
            'Laya': {
                'api_endpoint': 'https://api.layahealthcare.ie/claims',
                'coverage_levels': {
                    'Essential': {'preventive': 0.75, 'basic': 0.55, 'major': 0.45, 'annual_limit': 1200},
                    'Essential_Plus': {'preventive': 0.85, 'basic': 0.65, 'major': 0.55, 'annual_limit': 1800},
                    'Inspire': {'preventive': 0.95, 'basic': 0.75, 'major': 0.65, 'annual_limit': 2500}
                },
                'claim_processing_time': 7,
                'electronic_claims': True
            },
            'Irish_Life_Health': {
                'api_endpoint': 'https://api.irishlifehealth.ie/claims',
                'coverage_levels': {
                    'Health_Plan_1': {'preventive': 0.8, 'basic': 0.6, 'major': 0.5, 'annual_limit': 1400},
                    'Health_Plan_2': {'preventive': 0.9, 'basic': 0.7, 'major': 0.6, 'annual_limit': 2200},
                    'Health_Plan_3': {'preventive': 1.0, 'basic': 0.8, 'major': 0.7, 'annual_limit': 3500}
                },
                'claim_processing_time': 6,
                'electronic_claims': True
            },
            'PRSI': {
                'api_endpoint': 'https://api.hse.ie/prsi_dental',
                'coverage_levels': {
                    'Medical_Card': {'preventive': 1.0, 'basic': 0.0, 'major': 0.0, 'annual_limit': 200},
                    'GP_Visit_Card': {'preventive': 1.0, 'basic': 0.0, 'major': 0.0, 'annual_limit': 150}
                },
                'claim_processing_time': 14,
                'electronic_claims': False  # Manual processing
            }
        }

    def _initialize_treatment_codes(self) -> Dict[str, Any]:
        """Initialize dental treatment codes for billing"""
        return {
            'D0150': {'description': 'Comprehensive oral evaluation', 'category': 'preventive', 'fee': 75},
            'D0120': {'description': 'Periodic oral evaluation', 'category': 'preventive', 'fee': 65},
            'D1110': {'description': 'Adult prophylaxis', 'category': 'preventive', 'fee': 85},
            'D1120': {'description': 'Child prophylaxis', 'category': 'preventive', 'fee': 70},
            'D2140': {'description': 'Amalgam restoration - one surface', 'category': 'basic', 'fee': 120},
            'D2150': {'description': 'Amalgam restoration - two surfaces', 'category': 'basic', 'fee': 145},
            'D2330': {'description': 'Resin restoration - one surface', 'category': 'basic', 'fee': 150},
            'D2393': {'description': 'Resin restoration - four+ surfaces', 'category': 'basic', 'fee': 220},
            'D2740': {'description': 'Crown - porcelain/ceramic', 'category': 'major', 'fee': 650},
            'D2750': {'description': 'Crown - porcelain fused to metal', 'category': 'major', 'fee': 620},
            'D3310': {'description': 'Endodontic therapy - anterior', 'category': 'major', 'fee': 420},
            'D3320': {'description': 'Endodontic therapy - bicuspid', 'category': 'major', 'fee': 480},
            'D3330': {'description': 'Endodontic therapy - molar', 'category': 'major', 'fee': 550},
            'D7140': {'description': 'Extraction - erupted tooth', 'category': 'basic', 'fee': 85},
            'D7210': {'description': 'Extraction - impacted tooth', 'category': 'major', 'fee': 180},
            'D9110': {'description': 'Palliative emergency treatment', 'category': 'basic', 'fee': 75}
        }

    def submit_insurance_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit insurance claim with automated processing"""

        claim_id = f"CLM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Validate claim data
        validation_result = self._validate_claim_data(claim_data)
        if not validation_result['valid']:
            return {'success': False, 'errors': validation_result['errors']}

        # Calculate claim amounts
        claim_calculation = self._calculate_claim_amounts(claim_data)

        # Create claim record
        claim_record = {
            'claim_id': claim_id,
            'patient_id': claim_data['patient_id'],
            'provider': claim_data['insurance_provider'],
            'policy_number': claim_data['policy_number'],
            'treatment_codes': claim_data['treatment_codes'],
            'service_dates': claim_data['service_dates'],
            'dentist': claim_data['dentist'],
            'diagnosis_codes': claim_data.get('diagnosis_codes', []),
            'claim_amounts': claim_calculation,
            'status': 'submitted',
            'submission_method': self._determine_submission_method(claim_data['insurance_provider']),
            'submitted_at': datetime.now().isoformat(),
            'expected_processing_date': self._calculate_processing_date(claim_data['insurance_provider']),
            'claim_type': 'electronic' if self.insurance_providers[claim_data['insurance_provider']]['electronic_claims'] else 'manual'
        }

        # Submit to insurance provider (simulation)
        submission_result = self._submit_to_provider(claim_record)

        claim_record['submission_reference'] = submission_result['reference']
        claim_record['estimated_approval_probability'] = self._calculate_approval_probability(claim_record)

        self.claims_database[claim_id] = claim_record

        return {
            'success': True,
            'claim_id': claim_id,
            'submission_reference': submission_result['reference'],
            'estimated_processing_time': claim_record['expected_processing_date'],
            'estimated_amount': claim_calculation['estimated_payment'],
            'approval_probability': claim_record['estimated_approval_probability']
        }

    def _validate_claim_data(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate claim data before submission"""

        errors = []

        # Required fields validation
        required_fields = ['patient_id', 'insurance_provider', 'policy_number', 'treatment_codes', 'service_dates']
        for field in required_fields:
            if field not in claim_data or not claim_data[field]:
                errors.append(f"Missing required field: {field}")

        # Insurance provider validation
        if claim_data.get('insurance_provider') not in self.insurance_providers:
            errors.append(f"Unknown insurance provider: {claim_data.get('insurance_provider')}")

        # Treatment codes validation
        invalid_codes = []
        for code in claim_data.get('treatment_codes', []):
            if code not in self.treatment_codes:
                invalid_codes.append(code)
        if invalid_codes:
            errors.append(f"Invalid treatment codes: {', '.join(invalid_codes)}")

        # Date validation
        service_dates = claim_data.get('service_dates', [])
        for date_str in service_dates:
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format: {date_str}")

        return {'valid': len(errors) == 0, 'errors': errors}

    def _calculate_claim_amounts(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate claim amounts and patient responsibility"""

        provider = claim_data['insurance_provider']
        plan_level = claim_data.get('plan_level', 'Plan_A')

        total_fees = 0
        covered_amount = 0
        treatment_breakdown = []

        provider_info = self.insurance_providers[provider]
        coverage_levels = provider_info['coverage_levels'].get(plan_level, {})

        for code in claim_data['treatment_codes']:
            if code in self.treatment_codes:
                treatment_info = self.treatment_codes[code]
                fee = treatment_info['fee']
                category = treatment_info['category']

                # Determine coverage rate
                if category == 'preventive':
                    coverage_rate = coverage_levels.get('preventive', 0)
                elif category == 'basic':
                    coverage_rate = coverage_levels.get('basic', 0)
                elif category == 'major':
                    coverage_rate = coverage_levels.get('major', 0)
                else:
                    coverage_rate = 0

                covered_fee = fee * coverage_rate
                patient_portion = fee - covered_fee

                treatment_breakdown.append({
                    'code': code,
                    'description': treatment_info['description'],
                    'fee': fee,
                    'coverage_rate': coverage_rate,
                    'covered_amount': covered_fee,
                    'patient_portion': patient_portion
                })

                total_fees += fee
                covered_amount += covered_fee

        # Apply annual limit
        annual_limit = coverage_levels.get('annual_limit', 0)
        if covered_amount > annual_limit:
            excess = covered_amount - annual_limit
            covered_amount = annual_limit
            # Add excess to patient portion for last treatment
            if treatment_breakdown:
                treatment_breakdown[-1]['patient_portion'] += excess

        patient_responsibility = total_fees - covered_amount

        return {
            'total_fees': round(total_fees, 2),
            'covered_amount': round(covered_amount, 2),
            'patient_responsibility': round(patient_responsibility, 2),
            'estimated_payment': round(covered_amount * 0.95, 2),  # 95% approval estimate
            'treatment_breakdown': treatment_breakdown
        }

    def _determine_submission_method(self, provider: str) -> str:
        """Determine submission method based on provider capabilities"""

        if self.insurance_providers[provider]['electronic_claims']:
            return 'electronic'
        else:
            return 'manual'

    def _calculate_processing_date(self, provider: str) -> str:
        """Calculate expected processing date"""

        processing_days = self.insurance_providers[provider]['claim_processing_time']
        processing_date = datetime.now() + timedelta(days=processing_days)
        return processing_date.strftime('%Y-%m-%d')

    def _submit_to_provider(self, claim_record: Dict[str, Any]) -> Dict[str, Any]:
        """Submit claim to insurance provider (simulation)"""

        # Simulate API submission
        reference_number = f"REF_{uuid.uuid4().hex[:8].upper()}"

        return {
            'reference': reference_number,
            'status': 'received',
            'confirmation': f"Claim submitted successfully to {claim_record['provider']}"
        }

    def _calculate_approval_probability(self, claim_record: Dict[str, Any]) -> float:
        """Calculate likelihood of claim approval using AI"""

        base_probability = 0.85  # 85% base approval rate

        # Adjust based on claim characteristics
        adjustments = 0

        # Provider-specific adjustments
        if claim_record['provider'] == 'PRSI':
            adjustments -= 0.1  # Government claims more scrutinized
        elif claim_record['provider'] == 'VHI':
            adjustments += 0.05  # VHI has good approval rates

        # Treatment complexity adjustments
        major_treatments = [code for code in claim_record['treatment_codes']
                          if self.treatment_codes.get(code, {}).get('category') == 'major']
        if len(major_treatments) > 2:
            adjustments -= 0.1  # Multiple major treatments scrutinized more

        # Amount-based adjustments
        total_amount = claim_record['claim_amounts']['covered_amount']
        if total_amount > 1000:
            adjustments -= 0.05
        elif total_amount < 200:
            adjustments += 0.05

        final_probability = max(0.3, min(0.98, base_probability + adjustments))
        return round(final_probability, 2)

    def check_prsi_eligibility(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check PRSI dental eligibility"""

        # Simulate PRSI eligibility check
        pps_number = patient_data.get('pps_number')
        date_of_birth = patient_data.get('date_of_birth')

        if not pps_number or not date_of_birth:
            return {'eligible': False, 'error': 'Missing PPS number or date of birth'}

        # Simulate eligibility check (in production, connect to HSE API)
        eligibility_result = {
            'eligible': True,
            'card_type': 'medical_card',  # or 'gp_visit_card'
            'valid_until': '2024-12-31',
            'covered_services': ['examination', 'emergency_treatment'],
            'annual_allowance': 200,
            'remaining_allowance': 150,
            'last_checked': datetime.now().isoformat()
        }

        return eligibility_result

    def generate_private_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate private billing invoice"""

        invoice_id = f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Calculate invoice totals
        subtotal = 0
        line_items = []

        for item in invoice_data['items']:
            if item['code'] in self.treatment_codes:
                treatment_info = self.treatment_codes[item['code']]
                quantity = item.get('quantity', 1)
                unit_price = treatment_info['fee']
                line_total = unit_price * quantity

                line_items.append({
                    'code': item['code'],
                    'description': treatment_info['description'],
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': line_total
                })

                subtotal += line_total

        # Calculate VAT (23% in Ireland for private dental services)
        vat_rate = 0.23
        vat_amount = subtotal * vat_rate
        total_amount = subtotal + vat_amount

        invoice = {
            'invoice_id': invoice_id,
            'patient_id': invoice_data['patient_id'],
            'invoice_date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'dentist': invoice_data.get('dentist'),
            'service_dates': invoice_data.get('service_dates', []),
            'line_items': line_items,
            'subtotal': round(subtotal, 2),
            'vat_rate': vat_rate,
            'vat_amount': round(vat_amount, 2),
            'total_amount': round(total_amount, 2),
            'payment_terms': '30 days',
            'payment_methods': ['Cash', 'Card', 'Bank Transfer', 'Payment Plan'],
            'status': 'generated',
            'created_at': datetime.now().isoformat()
        }

        self.billing_database[invoice_id] = invoice

        return {'success': True, 'invoice': invoice}

    def create_payment_plan(self, payment_plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create flexible payment plan for patients"""

        plan_id = f"PP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        total_amount = payment_plan_data['total_amount']
        months = payment_plan_data['months']
        interest_rate = payment_plan_data.get('interest_rate', 0)

        # Calculate monthly payment
        if interest_rate > 0:
            monthly_interest_rate = interest_rate / 12
            monthly_payment = (total_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -months)
        else:
            monthly_payment = total_amount / months

        # Generate payment schedule
        payment_schedule = []
        current_date = datetime.now()

        for i in range(months):
            payment_date = current_date + timedelta(days=30 * (i + 1))
            payment_schedule.append({
                'payment_number': i + 1,
                'due_date': payment_date.strftime('%Y-%m-%d'),
                'amount': round(monthly_payment, 2),
                'status': 'pending'
            })

        payment_plan = {
            'plan_id': plan_id,
            'patient_id': payment_plan_data['patient_id'],
            'invoice_id': payment_plan_data.get('invoice_id'),
            'total_amount': total_amount,
            'monthly_payment': round(monthly_payment, 2),
            'months': months,
            'interest_rate': interest_rate,
            'total_with_interest': round(monthly_payment * months, 2),
            'payment_schedule': payment_schedule,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'automatic_payment': payment_plan_data.get('automatic_payment', False)
        }

        self.payment_plans[plan_id] = payment_plan

        return {'success': True, 'payment_plan': payment_plan}

    def track_outstanding_balances(self, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """Track and manage outstanding patient balances"""

        outstanding_summary = {
            'total_outstanding': 0,
            'aging_buckets': {
                '0-30_days': 0,
                '31-60_days': 0,
                '61-90_days': 0,
                '90+_days': 0
            },
            'patient_balances': []
        }

        # Analyze invoices and payment plans
        current_date = datetime.now()

        for invoice_id, invoice in self.billing_database.items():
            if patient_id and invoice['patient_id'] != patient_id:
                continue

            if invoice['status'] not in ['paid', 'cancelled']:
                days_overdue = (current_date - datetime.strptime(invoice['due_date'], '%Y-%m-%d')).days
                outstanding_amount = invoice['total_amount']

                # Determine aging bucket
                if days_overdue <= 30:
                    bucket = '0-30_days'
                elif days_overdue <= 60:
                    bucket = '31-60_days'
                elif days_overdue <= 90:
                    bucket = '61-90_days'
                else:
                    bucket = '90+_days'

                outstanding_summary['aging_buckets'][bucket] += outstanding_amount
                outstanding_summary['total_outstanding'] += outstanding_amount

                outstanding_summary['patient_balances'].append({
                    'patient_id': invoice['patient_id'],
                    'invoice_id': invoice_id,
                    'amount': outstanding_amount,
                    'due_date': invoice['due_date'],
                    'days_overdue': max(0, days_overdue),
                    'aging_bucket': bucket
                })

        # Round amounts
        outstanding_summary['total_outstanding'] = round(outstanding_summary['total_outstanding'], 2)
        for bucket in outstanding_summary['aging_buckets']:
            outstanding_summary['aging_buckets'][bucket] = round(outstanding_summary['aging_buckets'][bucket], 2)

        return outstanding_summary

    def send_payment_reminder(self, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send automated payment reminders"""

        patient_id = reminder_data['patient_id']
        reminder_type = reminder_data.get('type', 'gentle')

        # Generate personalized reminder message
        reminder_messages = {
            'gentle': "Friendly reminder that your dental treatment payment is due. We're here to help if you need to discuss payment options.",
            'firm': "Your dental treatment payment is now overdue. Please contact us immediately to arrange payment or discuss a payment plan.",
            'final': "Final notice: Your account is seriously overdue. Immediate payment is required to avoid collection proceedings."
        }

        reminder = {
            'reminder_id': f"REM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'patient_id': patient_id,
            'invoice_id': reminder_data.get('invoice_id'),
            'type': reminder_type,
            'message': reminder_messages[reminder_type],
            'method': reminder_data.get('method', 'email'),  # email, sms, letter
            'sent_at': datetime.now().isoformat(),
            'follow_up_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
        }

        return {'success': True, 'reminder': reminder}

def create_insurance_billing_agent(llm: ChatOpenAI, practice_config: Dict[str, Any]) -> AgentExecutor:
    """Create the insurance and billing hub agent with tools"""

    hub = InsuranceBillingHub(llm, practice_config)

    tools = [
        Tool(
            name="submit_insurance_claim",
            description="Submit insurance claim with automated processing",
            func=lambda query: hub.submit_insurance_claim(json.loads(query))
        ),
        Tool(
            name="check_prsi_eligibility",
            description="Check PRSI dental eligibility for patients",
            func=lambda query: hub.check_prsi_eligibility(json.loads(query))
        ),
        Tool(
            name="generate_private_invoice",
            description="Generate private billing invoice",
            func=lambda query: hub.generate_private_invoice(json.loads(query))
        ),
        Tool(
            name="create_payment_plan",
            description="Create flexible payment plan for patients",
            func=lambda query: hub.create_payment_plan(json.loads(query))
        ),
        Tool(
            name="track_outstanding_balances",
            description="Track and manage outstanding patient balances",
            func=lambda query: hub.track_outstanding_balances(**json.loads(query) if query.strip() else {})
        ),
        Tool(
            name="send_payment_reminder",
            description="Send automated payment reminders",
            func=lambda query: hub.send_payment_reminder(json.loads(query))
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI insurance and billing specialist for a dental practice.
        You handle insurance claims, PRSI eligibility, private billing, payment plans,
        and accounts receivable management. Always maximize reimbursement while
        maintaining compliance with Irish healthcare regulations.

        Practice Configuration:
        - Insurance Providers: {insurance_providers}
        - Treatment Codes: {treatment_codes}
        - Payment Terms: Standard 30 days
        - VAT Rate: 23% for private services

        Be accurate, efficient, and helpful in financial management."""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)