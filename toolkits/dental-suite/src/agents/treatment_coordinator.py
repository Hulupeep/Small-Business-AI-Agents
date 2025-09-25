"""
Treatment Plan Coordinator Agent
Intelligent treatment planning and cost management
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json

class TreatmentCoordinator:
    """AI-powered treatment planning and coordination"""

    def __init__(self, llm: ChatOpenAI, practice_config: Dict[str, Any]):
        self.llm = llm
        self.practice_config = practice_config
        self.treatment_database = self._initialize_treatment_database()
        self.insurance_providers = self._initialize_insurance_data()

    def _initialize_treatment_database(self) -> Dict[str, Any]:
        """Initialize treatment cost and duration database"""
        return {
            'checkup': {
                'base_cost': 75,
                'duration': 30,
                'materials': ['examination_gloves', 'dental_mirror'],
                'complexity': 'low'
            },
            'cleaning': {
                'base_cost': 85,
                'duration': 45,
                'materials': ['ultrasonic_scaler', 'polishing_paste'],
                'complexity': 'low'
            },
            'filling_amalgam': {
                'base_cost': 120,
                'duration': 60,
                'materials': ['amalgam', 'local_anaesthetic', 'dental_dam'],
                'complexity': 'medium'
            },
            'filling_composite': {
                'base_cost': 150,
                'duration': 75,
                'materials': ['composite_resin', 'bonding_agent', 'local_anaesthetic'],
                'complexity': 'medium'
            },
            'root_canal': {
                'base_cost': 450,
                'duration': 90,
                'materials': ['endodontic_files', 'gutta_percha', 'local_anaesthetic'],
                'complexity': 'high'
            },
            'crown': {
                'base_cost': 650,
                'duration': 120,
                'materials': ['crown_material', 'impression_material', 'temporary_crown'],
                'complexity': 'high'
            },
            'extraction': {
                'base_cost': 85,
                'duration': 45,
                'materials': ['extraction_forceps', 'local_anaesthetic', 'gauze'],
                'complexity': 'medium'
            },
            'whitening': {
                'base_cost': 350,
                'duration': 60,
                'materials': ['whitening_gel', 'mouth_trays', 'barrier_gel'],
                'complexity': 'low'
            }
        }

    def _initialize_insurance_data(self) -> Dict[str, Any]:
        """Initialize insurance provider information"""
        return {
            'VHI': {
                'checkup_coverage': 0.8,
                'cleaning_coverage': 0.7,
                'filling_coverage': 0.6,
                'major_coverage': 0.5,
                'annual_limit': 1500
            },
            'Laya': {
                'checkup_coverage': 0.75,
                'cleaning_coverage': 0.65,
                'filling_coverage': 0.55,
                'major_coverage': 0.45,
                'annual_limit': 1200
            },
            'Irish_Life_Health': {
                'checkup_coverage': 0.85,
                'cleaning_coverage': 0.75,
                'filling_coverage': 0.65,
                'major_coverage': 0.55,
                'annual_limit': 1800
            },
            'PRSI': {
                'checkup_coverage': 1.0,
                'cleaning_coverage': 0.0,
                'filling_coverage': 0.0,
                'major_coverage': 0.0,
                'annual_limit': 200
            }
        }

    def create_treatment_plan(self, patient_id: str, treatments: List[str],
                            patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive treatment plan with cost estimates"""

        total_cost = 0
        total_duration = 0
        treatment_details = []

        for treatment in treatments:
            if treatment in self.treatment_database:
                treatment_info = self.treatment_database[treatment]

                # Apply complexity modifiers based on patient profile
                cost_modifier = self._calculate_cost_modifier(treatment, patient_profile)
                adjusted_cost = treatment_info['base_cost'] * cost_modifier

                treatment_detail = {
                    'treatment': treatment,
                    'base_cost': treatment_info['base_cost'],
                    'adjusted_cost': round(adjusted_cost, 2),
                    'duration': treatment_info['duration'],
                    'complexity': treatment_info['complexity'],
                    'materials': treatment_info['materials']
                }

                treatment_details.append(treatment_detail)
                total_cost += adjusted_cost
                total_duration += treatment_info['duration']

        # Calculate insurance coverage
        insurance_info = self._calculate_insurance_coverage(
            treatments, total_cost, patient_profile.get('insurance_provider')
        )

        # Generate payment plan options
        payment_plans = self._generate_payment_plans(
            total_cost - insurance_info['covered_amount'], patient_profile
        )

        treatment_plan = {
            'patient_id': patient_id,
            'plan_id': f"TP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'treatments': treatment_details,
            'total_cost': round(total_cost, 2),
            'total_duration': total_duration,
            'estimated_visits': self._calculate_visits(treatments),
            'insurance': insurance_info,
            'payment_plans': payment_plans,
            'created_at': datetime.now().isoformat(),
            'valid_until': (datetime.now().replace(month=datetime.now().month + 3)).isoformat()
        }

        return treatment_plan

    def _calculate_cost_modifier(self, treatment: str, patient_profile: Dict[str, Any]) -> float:
        """Calculate cost modifier based on patient complexity"""

        modifier = 1.0

        # Age-based modifiers
        age = patient_profile.get('age', 40)
        if age > 65:
            modifier += 0.15  # Elderly patients may require more care
        elif age < 18:
            modifier += 0.1   # Pediatric care adjustments

        # Medical history modifiers
        medical_conditions = patient_profile.get('medical_conditions', [])
        if 'diabetes' in medical_conditions:
            modifier += 0.1
        if 'heart_disease' in medical_conditions:
            modifier += 0.15
        if 'anxiety' in medical_conditions:
            modifier += 0.05

        # Previous treatment history
        previous_treatments = patient_profile.get('previous_treatments', [])
        if len(previous_treatments) > 5:
            modifier -= 0.05  # Loyal patient discount

        return max(0.8, min(1.5, modifier))  # Cap between 80% and 150%

    def _calculate_insurance_coverage(self, treatments: List[str], total_cost: float,
                                    insurance_provider: Optional[str]) -> Dict[str, Any]:
        """Calculate insurance coverage for treatment plan"""

        if not insurance_provider or insurance_provider not in self.insurance_providers:
            return {
                'provider': 'None',
                'covered_amount': 0,
                'patient_portion': total_cost,
                'coverage_details': []
            }

        provider_info = self.insurance_providers[insurance_provider]
        covered_amount = 0
        coverage_details = []

        for treatment in treatments:
            coverage_rate = 0

            if treatment in ['checkup']:
                coverage_rate = provider_info['checkup_coverage']
            elif treatment in ['cleaning']:
                coverage_rate = provider_info['cleaning_coverage']
            elif treatment in ['filling_amalgam', 'filling_composite']:
                coverage_rate = provider_info['filling_coverage']
            else:
                coverage_rate = provider_info['major_coverage']

            treatment_cost = self.treatment_database[treatment]['base_cost']
            treatment_covered = treatment_cost * coverage_rate
            covered_amount += treatment_covered

            coverage_details.append({
                'treatment': treatment,
                'cost': treatment_cost,
                'coverage_rate': coverage_rate,
                'covered_amount': treatment_covered,
                'patient_pays': treatment_cost - treatment_covered
            })

        # Apply annual limit
        annual_limit = provider_info['annual_limit']
        if covered_amount > annual_limit:
            covered_amount = annual_limit

        return {
            'provider': insurance_provider,
            'covered_amount': round(covered_amount, 2),
            'patient_portion': round(total_cost - covered_amount, 2),
            'annual_limit': annual_limit,
            'coverage_details': coverage_details
        }

    def _generate_payment_plans(self, patient_portion: float,
                               patient_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate flexible payment plan options"""

        plans = []

        # Single payment (with discount)
        plans.append({
            'type': 'single_payment',
            'description': 'Pay in full (5% discount)',
            'amount': round(patient_portion * 0.95, 2),
            'payments': 1,
            'interest_rate': 0,
            'total_cost': round(patient_portion * 0.95, 2)
        })

        # 3-month plan
        monthly_amount_3 = patient_portion / 3
        plans.append({
            'type': '3_month_plan',
            'description': '3 monthly payments (no interest)',
            'amount': round(monthly_amount_3, 2),
            'payments': 3,
            'interest_rate': 0,
            'total_cost': round(patient_portion, 2)
        })

        # 6-month plan
        monthly_amount_6 = (patient_portion * 1.03) / 6  # 3% interest
        plans.append({
            'type': '6_month_plan',
            'description': '6 monthly payments (3% interest)',
            'amount': round(monthly_amount_6, 2),
            'payments': 6,
            'interest_rate': 0.03,
            'total_cost': round(patient_portion * 1.03, 2)
        })

        # 12-month plan (for high-cost treatments)
        if patient_portion > 500:
            monthly_amount_12 = (patient_portion * 1.06) / 12  # 6% interest
            plans.append({
                'type': '12_month_plan',
                'description': '12 monthly payments (6% interest)',
                'amount': round(monthly_amount_12, 2),
                'payments': 12,
                'interest_rate': 0.06,
                'total_cost': round(patient_portion * 1.06, 2)
            })

        return plans

    def _calculate_visits(self, treatments: List[str]) -> int:
        """Calculate estimated number of visits"""

        visit_requirements = {
            'checkup': 1,
            'cleaning': 1,
            'filling_amalgam': 1,
            'filling_composite': 1,
            'root_canal': 2,  # Initial treatment + follow-up
            'crown': 3,       # Preparation, impression, fitting
            'extraction': 1,
            'whitening': 2    # Initial + follow-up
        }

        total_visits = sum(visit_requirements.get(treatment, 1) for treatment in treatments)
        return max(1, total_visits)

    def verify_insurance(self, patient_id: str, insurance_details: Dict[str, Any]) -> Dict[str, Any]:
        """Verify insurance coverage and eligibility"""

        provider = insurance_details.get('provider')
        policy_number = insurance_details.get('policy_number')

        # Simulate insurance verification
        # In production, this would connect to insurance provider APIs

        if provider in self.insurance_providers:
            verification_result = {
                'verified': True,
                'provider': provider,
                'policy_number': policy_number,
                'coverage_details': self.insurance_providers[provider],
                'verification_date': datetime.now().isoformat(),
                'status': 'active'
            }
        else:
            verification_result = {
                'verified': False,
                'provider': provider,
                'error': 'Provider not recognized or policy inactive',
                'verification_date': datetime.now().isoformat(),
                'status': 'inactive'
            }

        return verification_result

    def generate_consent_form(self, treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate treatment-specific consent form"""

        treatments = [t['treatment'] for t in treatment_plan['treatments']]

        consent_sections = {
            'treatment_description': self._generate_treatment_description(treatments),
            'risks_and_complications': self._generate_risks_section(treatments),
            'alternatives': self._generate_alternatives_section(treatments),
            'post_treatment_care': self._generate_care_instructions(treatments),
            'financial_agreement': self._generate_financial_terms(treatment_plan)
        }

        consent_form = {
            'form_id': f"CF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'patient_id': treatment_plan['patient_id'],
            'treatment_plan_id': treatment_plan['plan_id'],
            'sections': consent_sections,
            'created_at': datetime.now().isoformat(),
            'requires_signature': True,
            'digital_signature_enabled': True
        }

        return consent_form

    def _generate_treatment_description(self, treatments: List[str]) -> str:
        """Generate comprehensive treatment description"""

        descriptions = {
            'checkup': 'Comprehensive oral examination including visual inspection and diagnostic assessment',
            'cleaning': 'Professional tooth cleaning including plaque and tartar removal',
            'filling_amalgam': 'Tooth restoration using amalgam filling material',
            'filling_composite': 'Tooth restoration using tooth-colored composite material',
            'root_canal': 'Endodontic treatment to remove infected or damaged tooth pulp',
            'crown': 'Full tooth coverage restoration to protect and strengthen damaged tooth',
            'extraction': 'Surgical removal of tooth that cannot be restored',
            'whitening': 'Professional tooth whitening treatment to improve tooth color'
        }

        return '. '.join([descriptions.get(treatment, f'Treatment: {treatment}')
                         for treatment in treatments])

    def _generate_risks_section(self, treatments: List[str]) -> str:
        """Generate risks and complications section"""

        common_risks = "Common risks include temporary discomfort, swelling, or sensitivity."

        specific_risks = []
        if any(t in ['root_canal', 'extraction'] for t in treatments):
            specific_risks.append("Risk of infection or nerve damage")
        if any(t in ['crown', 'filling_composite'] for t in treatments):
            specific_risks.append("Possible allergic reaction to materials")
        if 'whitening' in treatments:
            specific_risks.append("Temporary tooth sensitivity")

        return f"{common_risks} {' '.join(specific_risks)}"

    def _generate_alternatives_section(self, treatments: List[str]) -> str:
        """Generate treatment alternatives section"""

        alternatives = {
            'filling_amalgam': 'Alternative: Composite filling, crown, or extraction',
            'root_canal': 'Alternative: Tooth extraction with bridge or implant',
            'crown': 'Alternative: Large filling or extraction',
            'extraction': 'Alternative: Root canal treatment and crown'
        }

        return '. '.join([alternatives.get(treatment, 'No alternative treatment available')
                         for treatment in treatments if treatment in alternatives])

    def _generate_care_instructions(self, treatments: List[str]) -> str:
        """Generate post-treatment care instructions"""

        instructions = []

        if any(t in ['filling_amalgam', 'filling_composite'] for t in treatments):
            instructions.append("Avoid hard foods for 24 hours")
        if any(t in ['root_canal', 'extraction'] for t in treatments):
            instructions.append("Take prescribed medication as directed")
        if 'crown' in treatments:
            instructions.append("Avoid sticky foods and maintain good oral hygiene")
        if 'whitening' in treatments:
            instructions.append("Avoid staining foods and beverages for 48 hours")

        return '. '.join(instructions) if instructions else "Follow standard post-treatment care guidelines"

    def _generate_financial_terms(self, treatment_plan: Dict[str, Any]) -> str:
        """Generate financial agreement terms"""

        total_cost = treatment_plan['total_cost']
        insurance_covered = treatment_plan['insurance']['covered_amount']
        patient_portion = treatment_plan['insurance']['patient_portion']

        return f"Total treatment cost: €{total_cost}. Insurance coverage: €{insurance_covered}. Patient responsibility: €{patient_portion}. Payment plans available."

def create_treatment_coordinator_agent(llm: ChatOpenAI, practice_config: Dict[str, Any]) -> AgentExecutor:
    """Create the treatment coordinator agent with tools"""

    coordinator = TreatmentCoordinator(llm, practice_config)

    tools = [
        Tool(
            name="create_treatment_plan",
            description="Create comprehensive treatment plan with cost estimates",
            func=lambda query: coordinator.create_treatment_plan(**json.loads(query))
        ),
        Tool(
            name="verify_insurance",
            description="Verify patient insurance coverage and eligibility",
            func=lambda query: coordinator.verify_insurance(**json.loads(query))
        ),
        Tool(
            name="generate_consent_form",
            description="Generate treatment-specific consent form",
            func=lambda query: coordinator.generate_consent_form(json.loads(query))
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI treatment coordinator for a dental practice.
        You create detailed treatment plans, verify insurance coverage, generate
        accurate cost estimates, and create consent forms. Always provide clear,
        accurate information and multiple payment options.

        Practice Configuration:
        - Treatments Available: {treatments}
        - Insurance Providers: {insurance_providers}
        - Payment Options: Multiple plans available

        Be thorough, accurate, and helpful in your treatment planning."""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)