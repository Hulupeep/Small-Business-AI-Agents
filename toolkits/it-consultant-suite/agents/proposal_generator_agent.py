"""
Proposal & Quote Generator Agent for IT Consultants
Automates technical proposal writing, cost estimation, and SOW creation
"""

import json
import yaml
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import pandas as pd
from enum import Enum

class ProjectComplexity(Enum):
    SIMPLE = 1.0
    MODERATE = 1.5
    COMPLEX = 2.0
    ENTERPRISE = 3.0

class ServiceType(Enum):
    CONSULTATION = "consultation"
    IMPLEMENTATION = "implementation"
    MIGRATION = "migration"
    OPTIMIZATION = "optimization"
    SECURITY_AUDIT = "security_audit"
    TRAINING = "training"

@dataclass
class ProjectRequirement:
    description: str
    category: str
    estimated_hours: float
    complexity_factor: float
    dependencies: List[str]
    deliverables: List[str]

@dataclass
class ProposalData:
    client_name: str
    project_title: str
    requirements: List[ProjectRequirement]
    total_hours: float
    total_cost: float
    timeline_weeks: int
    risk_factors: List[str]
    deliverables: List[str]
    terms: Dict[str, str]

class ProposalGeneratorAgent:
    """
    Comprehensive proposal generation agent that creates technical proposals,
    estimates costs, and generates SOWs for IT consulting projects.
    """

    def __init__(self, config_path: str = "config/pricing_models.yaml"):
        self.config = self._load_config(config_path)
        self.hourly_rates = self._load_hourly_rates()
        self.proposal_templates = self._load_templates()
        self.historical_data = self._load_historical_data()

    def _load_config(self, config_path: str) -> Dict:
        """Load pricing and configuration settings"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return self._default_config()

    def _default_config(self) -> Dict:
        """Default configuration if file not found"""
        return {
            'base_hourly_rate': 95,  # EUR per hour
            'complexity_multipliers': {
                'simple': 1.0,
                'moderate': 1.5,
                'complex': 2.0,
                'enterprise': 3.0
            },
            'service_multipliers': {
                'consultation': 1.0,
                'implementation': 1.2,
                'migration': 1.5,
                'optimization': 1.1,
                'security_audit': 1.8,
                'training': 0.8
            },
            'overhead_percentage': 0.15,
            'profit_margin': 0.25
        }

    def _load_hourly_rates(self) -> Dict[str, float]:
        """Load hourly rates by service type and complexity"""
        base_rate = self.config['base_hourly_rate']
        return {
            'strategy_consultation': base_rate * 1.2,
            'technical_implementation': base_rate,
            'project_management': base_rate * 0.9,
            'training_delivery': base_rate * 0.8,
            'emergency_support': base_rate * 1.5,
            'security_assessment': base_rate * 1.4
        }

    def _load_templates(self) -> Dict:
        """Load proposal templates"""
        return {
            'executive_summary': """
**Executive Summary**

{client_name} has identified the need for {project_type} to {business_objective}.
Our comprehensive approach will deliver {key_benefits} while ensuring {risk_mitigation}.

**Key Deliverables:**
{deliverables_list}

**Investment:** €{total_cost:,.2f}
**Timeline:** {timeline_weeks} weeks
**ROI:** {estimated_roi}
""",
            'technical_approach': """
**Technical Approach**

**Current State Analysis:**
{current_state}

**Proposed Solution:**
{proposed_solution}

**Implementation Methodology:**
{methodology}

**Technology Stack:**
{tech_stack}
""",
            'risk_assessment': """
**Risk Assessment & Mitigation**

{risk_analysis}

**Contingency Planning:**
{contingency_plan}
""",
            'timeline': """
**Project Timeline**

{timeline_breakdown}

**Critical Dependencies:**
{dependencies}
""",
            'investment': """
**Investment Breakdown**

{cost_breakdown}

**Payment Schedule:**
{payment_terms}
"""
        }

    def _load_historical_data(self) -> Dict:
        """Load historical project data for better estimates"""
        # Mock historical data - in real implementation, would load from database
        return {
            'fintech_migration': {'avg_hours': 320, 'complexity': 2.2, 'success_rate': 0.92},
            'ecommerce_optimization': {'avg_hours': 180, 'complexity': 1.5, 'success_rate': 0.95},
            'healthcare_compliance': {'avg_hours': 240, 'complexity': 2.0, 'success_rate': 0.88},
            'security_audit': {'avg_hours': 120, 'complexity': 1.8, 'success_rate': 0.98}
        }

    def analyze_requirements(self, client_brief: str, industry: str) -> List[ProjectRequirement]:
        """
        Analyze client requirements and break down into components
        """
        print(f"🔍 Analyzing requirements for {industry} project...")

        # Mock requirement analysis - in real implementation, would use NLP
        requirements_map = {
            'fintech': [
                ProjectRequirement(
                    description="PCI DSS compliance assessment and implementation",
                    category="security",
                    estimated_hours=80,
                    complexity_factor=1.8,
                    dependencies=[],
                    deliverables=["Compliance gap analysis", "Implementation plan", "Security documentation"]
                ),
                ProjectRequirement(
                    description="Payment gateway integration and optimization",
                    category="integration",
                    estimated_hours=120,
                    complexity_factor=2.0,
                    dependencies=["Security assessment"],
                    deliverables=["API integration", "Testing suite", "Performance optimization"]
                ),
                ProjectRequirement(
                    description="Real-time fraud detection system",
                    category="development",
                    estimated_hours=160,
                    complexity_factor=2.5,
                    dependencies=["Payment gateway"],
                    deliverables=["ML model", "Monitoring dashboard", "Alert system"]
                )
            ],
            'ecommerce': [
                ProjectRequirement(
                    description="Website performance optimization",
                    category="optimization",
                    estimated_hours=60,
                    complexity_factor=1.3,
                    dependencies=[],
                    deliverables=["Performance audit", "Optimization implementation", "Monitoring setup"]
                ),
                ProjectRequirement(
                    description="Inventory management system integration",
                    category="integration",
                    estimated_hours=100,
                    complexity_factor=1.8,
                    dependencies=["Performance optimization"],
                    deliverables=["API integration", "Data synchronization", "Reporting dashboard"]
                )
            ],
            'healthtech': [
                ProjectRequirement(
                    description="HIPAA compliance implementation",
                    category="compliance",
                    estimated_hours=90,
                    complexity_factor=2.0,
                    dependencies=[],
                    deliverables=["Gap analysis", "Policy documentation", "Staff training"]
                ),
                ProjectRequirement(
                    description="Patient data encryption and security",
                    category="security",
                    estimated_hours=70,
                    complexity_factor=1.9,
                    dependencies=["HIPAA compliance"],
                    deliverables=["Encryption implementation", "Access controls", "Audit trails"]
                )
            ]
        }

        return requirements_map.get(industry, [
            ProjectRequirement(
                description="Custom technology consultation",
                category="consultation",
                estimated_hours=40,
                complexity_factor=1.0,
                dependencies=[],
                deliverables=["Analysis report", "Recommendations", "Implementation roadmap"]
            )
        ])

    def estimate_costs(self, requirements: List[ProjectRequirement], service_type: ServiceType) -> Tuple[float, Dict]:
        """
        Estimate project costs based on requirements
        """
        print("💰 Calculating project costs...")

        base_rate = self.hourly_rates['technical_implementation']
        service_multiplier = self.config['service_multipliers'][service_type.value]

        cost_breakdown = {
            'line_items': [],
            'subtotal': 0,
            'overhead': 0,
            'total': 0
        }

        total_hours = 0
        for req in requirements:
            hours = req.estimated_hours * req.complexity_factor
            rate = base_rate * service_multiplier
            line_cost = hours * rate

            cost_breakdown['line_items'].append({
                'description': req.description,
                'hours': hours,
                'rate': rate,
                'cost': line_cost
            })

            total_hours += hours
            cost_breakdown['subtotal'] += line_cost

        # Add overhead and profit margin
        overhead = cost_breakdown['subtotal'] * self.config['overhead_percentage']
        profit = cost_breakdown['subtotal'] * self.config['profit_margin']

        cost_breakdown['overhead'] = overhead
        cost_breakdown['profit'] = profit
        cost_breakdown['total'] = cost_breakdown['subtotal'] + overhead + profit

        return total_hours, cost_breakdown

    def estimate_timeline(self, requirements: List[ProjectRequirement], team_size: int = 1) -> Dict:
        """
        Estimate project timeline considering dependencies
        """
        print("📅 Calculating project timeline...")

        # Build dependency graph
        req_map = {req.description: req for req in requirements}
        timeline_phases = []

        # Phase 1: Requirements with no dependencies
        phase_1 = [req for req in requirements if not req.dependencies]
        if phase_1:
            phase_1_hours = sum(req.estimated_hours * req.complexity_factor for req in phase_1)
            timeline_phases.append({
                'phase': 'Phase 1 - Foundation',
                'requirements': [req.description for req in phase_1],
                'hours': phase_1_hours,
                'weeks': max(1, phase_1_hours / (40 * team_size))  # 40 hours per week per team member
            })

        # Phase 2: Requirements with dependencies
        remaining_reqs = [req for req in requirements if req.dependencies]
        if remaining_reqs:
            phase_2_hours = sum(req.estimated_hours * req.complexity_factor for req in remaining_reqs)
            timeline_phases.append({
                'phase': 'Phase 2 - Implementation',
                'requirements': [req.description for req in remaining_reqs],
                'hours': phase_2_hours,
                'weeks': max(1, phase_2_hours / (40 * team_size))
            })

        total_weeks = sum(phase['weeks'] for phase in timeline_phases)

        return {
            'phases': timeline_phases,
            'total_weeks': int(total_weeks) + 1,  # Add buffer week
            'critical_path': self._identify_critical_path(requirements),
            'milestones': self._generate_milestones(timeline_phases)
        }

    def _identify_critical_path(self, requirements: List[ProjectRequirement]) -> List[str]:
        """Identify critical path through project requirements"""
        # Simplified critical path - in real implementation would use proper scheduling algorithms
        critical_reqs = sorted(requirements, key=lambda x: x.estimated_hours * x.complexity_factor, reverse=True)
        return [req.description for req in critical_reqs[:3]]

    def _generate_milestones(self, phases: List[Dict]) -> List[Dict]:
        """Generate project milestones"""
        milestones = []
        week_counter = 0

        for i, phase in enumerate(phases):
            week_counter += int(phase['weeks'])
            milestones.append({
                'milestone': f"{phase['phase']} Complete",
                'week': week_counter,
                'deliverables': phase['requirements']
            })

        return milestones

    def assess_risks(self, requirements: List[ProjectRequirement], industry: str) -> List[Dict]:
        """
        Assess project risks and mitigation strategies
        """
        print("⚠️ Assessing project risks...")

        risk_database = {
            'fintech': [
                {
                    'risk': 'Regulatory compliance changes during project',
                    'probability': 'Medium',
                    'impact': 'High',
                    'mitigation': 'Regular compliance reviews and flexible architecture'
                },
                {
                    'risk': 'Integration complexity with legacy systems',
                    'probability': 'High',
                    'impact': 'Medium',
                    'mitigation': 'Thorough system analysis and API abstraction layers'
                }
            ],
            'ecommerce': [
                {
                    'risk': 'Peak season traffic disruption',
                    'probability': 'Medium',
                    'impact': 'High',
                    'mitigation': 'Staged deployment and comprehensive load testing'
                },
                {
                    'risk': 'Third-party service dependencies',
                    'probability': 'High',
                    'impact': 'Medium',
                    'mitigation': 'Fallback mechanisms and SLA monitoring'
                }
            ],
            'healthtech': [
                {
                    'risk': 'Patient data security breach',
                    'probability': 'Low',
                    'impact': 'Critical',
                    'mitigation': 'Multi-layer security, encryption, and regular audits'
                },
                {
                    'risk': 'HIPAA compliance violations',
                    'probability': 'Medium',
                    'impact': 'High',
                    'mitigation': 'Compliance monitoring and staff training'
                }
            ]
        }

        # Technical risks based on requirements
        technical_risks = []
        total_complexity = sum(req.complexity_factor for req in requirements)

        if total_complexity > 6:
            technical_risks.append({
                'risk': 'High project complexity may lead to scope creep',
                'probability': 'Medium',
                'impact': 'Medium',
                'mitigation': 'Detailed change management process and regular reviews'
            })

        if len(requirements) > 5:
            technical_risks.append({
                'risk': 'Multiple integration points increase failure risk',
                'probability': 'Medium',
                'impact': 'Medium',
                'mitigation': 'Incremental integration testing and rollback procedures'
            })

        industry_risks = risk_database.get(industry, [])
        return industry_risks + technical_risks

    def generate_proposal(self, client_name: str, project_brief: str, industry: str,
                         service_type: ServiceType = ServiceType.IMPLEMENTATION) -> ProposalData:
        """
        Generate complete proposal based on client requirements
        """
        print(f"📝 Generating proposal for {client_name}...")

        # Analyze requirements
        requirements = self.analyze_requirements(project_brief, industry)

        # Estimate costs and timeline
        total_hours, cost_breakdown = self.estimate_costs(requirements, service_type)
        timeline = self.estimate_timeline(requirements)

        # Assess risks
        risks = self.assess_risks(requirements, industry)

        # Compile deliverables
        all_deliverables = []
        for req in requirements:
            all_deliverables.extend(req.deliverables)

        proposal = ProposalData(
            client_name=client_name,
            project_title=f"{industry.title()} {service_type.value.replace('_', ' ').title()} Project",
            requirements=requirements,
            total_hours=total_hours,
            total_cost=cost_breakdown['total'],
            timeline_weeks=timeline['total_weeks'],
            risk_factors=[risk['risk'] for risk in risks],
            deliverables=list(set(all_deliverables)),  # Remove duplicates
            terms=self._generate_terms()
        )

        print(f"✅ Proposal generated: €{proposal.total_cost:,.2f} over {proposal.timeline_weeks} weeks")
        return proposal

    def _generate_terms(self) -> Dict[str, str]:
        """Generate standard contract terms"""
        return {
            'payment_schedule': '30% upfront, 40% at 50% completion, 30% on delivery',
            'payment_terms': 'Net 30 days',
            'warranty': '90 days post-delivery support included',
            'change_requests': 'Additional work billed at standard rates',
            'intellectual_property': 'Client owns all deliverables upon final payment',
            'confidentiality': 'Mutual NDA required before project commencement'
        }

    def format_proposal_document(self, proposal: ProposalData) -> str:
        """
        Format the complete proposal document
        """
        print("📄 Formatting proposal document...")

        # Calculate ROI estimate
        estimated_savings = proposal.total_cost * 2.5  # Conservative ROI estimate
        roi_months = 12

        # Format deliverables list
        deliverables_list = '\n'.join([f"• {deliverable}" for deliverable in proposal.deliverables])

        # Format cost breakdown
        cost_breakdown_text = f"""
**Professional Services:** €{proposal.total_cost * 0.75:,.2f}
**Project Management:** €{proposal.total_cost * 0.15:,.2f}
**Quality Assurance:** €{proposal.total_cost * 0.10:,.2f}
**Total Investment:** €{proposal.total_cost:,.2f}
"""

        # Format timeline
        timeline_text = f"""
**Project Duration:** {proposal.timeline_weeks} weeks
**Estimated Start Date:** {(datetime.now() + timedelta(days=14)).strftime('%B %d, %Y')}
**Estimated Completion:** {(datetime.now() + timedelta(weeks=proposal.timeline_weeks + 2)).strftime('%B %d, %Y')}
"""

        # Format risk assessment
        risk_text = '\n'.join([f"• {risk}" for risk in proposal.risk_factors[:5]])

        document = f"""
# {proposal.project_title}
## Proposal for {proposal.client_name}

{self.proposal_templates['executive_summary'].format(
    client_name=proposal.client_name,
    project_type=proposal.project_title.lower(),
    business_objective="optimize technology infrastructure and improve operational efficiency",
    key_benefits="enhanced security, improved performance, and cost savings",
    risk_mitigation="minimal business disruption",
    deliverables_list=deliverables_list,
    total_cost=proposal.total_cost,
    timeline_weeks=proposal.timeline_weeks,
    estimated_roi=f"€{estimated_savings:,.0f} savings over {roi_months} months"
)}

## Technical Requirements Analysis

**Identified Requirements:**
{chr(10).join([f"• {req.description} ({req.estimated_hours:.0f}h)" for req in proposal.requirements])}

## Project Timeline
{timeline_text}

## Investment Breakdown
{cost_breakdown_text}

## Risk Assessment
{risk_text}

## Terms & Conditions
{chr(10).join([f"**{key.replace('_', ' ').title()}:** {value}" for key, value in proposal.terms.items()])}

---

**Next Steps:**
1. Review and approve this proposal
2. Sign mutual NDA and service agreement
3. Schedule project kickoff meeting
4. Begin Phase 1 implementation

*This proposal is valid for 30 days from the date of submission.*

**Contact Information:**
Email: your.email@consultant.com
Phone: +44 xxx xxx xxxx
LinkedIn: linkedin.com/in/yourprofile
"""

        return document

    def optimize_pricing(self, proposal: ProposalData, client_budget: Optional[float] = None,
                        win_probability_target: float = 0.8) -> Dict:
        """
        Optimize pricing strategy based on client budget and win probability
        """
        print("💡 Optimizing pricing strategy...")

        original_cost = proposal.total_cost
        optimizations = []

        if client_budget and client_budget < original_cost:
            # Budget constraints - suggest optimizations
            reduction_needed = original_cost - client_budget
            reduction_percentage = reduction_needed / original_cost

            if reduction_percentage <= 0.15:  # Up to 15% reduction
                optimizations.append({
                    'strategy': 'Scope optimization',
                    'description': 'Reduce non-critical features',
                    'cost_reduction': reduction_needed,
                    'impact': 'Minimal impact on core objectives'
                })
            elif reduction_percentage <= 0.30:  # Up to 30% reduction
                optimizations.append({
                    'strategy': 'Phased approach',
                    'description': 'Implement in multiple phases',
                    'cost_reduction': reduction_needed,
                    'impact': 'Extended timeline but lower initial investment'
                })
            else:
                optimizations.append({
                    'strategy': 'Alternative solution',
                    'description': 'Recommend different approach',
                    'cost_reduction': reduction_needed,
                    'impact': 'May require compromise on requirements'
                })

        # Market positioning analysis
        market_position = self._analyze_market_position(original_cost, proposal.timeline_weeks)

        return {
            'original_cost': original_cost,
            'optimized_cost': client_budget if client_budget and client_budget < original_cost else original_cost,
            'optimizations': optimizations,
            'market_position': market_position,
            'win_probability': self._calculate_win_probability(proposal, client_budget),
            'recommendations': self._generate_pricing_recommendations(proposal, client_budget)
        }

    def _analyze_market_position(self, cost: float, timeline: int) -> Dict:
        """Analyze market position of the proposal"""
        cost_per_week = cost / timeline

        if cost_per_week < 5000:
            position = "competitive"
        elif cost_per_week < 8000:
            position = "market_rate"
        else:
            position = "premium"

        return {
            'position': position,
            'cost_per_week': cost_per_week,
            'market_benchmark': 6500  # EUR per week average
        }

    def _calculate_win_probability(self, proposal: ProposalData, client_budget: Optional[float]) -> float:
        """Calculate probability of winning the proposal"""
        base_probability = 0.7

        # Adjust based on budget fit
        if client_budget:
            budget_ratio = proposal.total_cost / client_budget
            if budget_ratio <= 0.8:
                base_probability += 0.2
            elif budget_ratio <= 1.0:
                base_probability += 0.1
            elif budget_ratio <= 1.2:
                base_probability -= 0.1
            else:
                base_probability -= 0.3

        # Adjust based on complexity
        avg_complexity = sum(req.complexity_factor for req in proposal.requirements) / len(proposal.requirements)
        if avg_complexity > 2.0:
            base_probability -= 0.1

        return max(0.1, min(0.95, base_probability))

    def _generate_pricing_recommendations(self, proposal: ProposalData, client_budget: Optional[float]) -> List[str]:
        """Generate pricing strategy recommendations"""
        recommendations = []

        if client_budget and client_budget < proposal.total_cost:
            recommendations.append("Consider offering a phased implementation approach")
            recommendations.append("Highlight ROI and cost savings in presentation")

        if proposal.total_cost > 50000:
            recommendations.append("Offer extended payment terms to improve cash flow")

        if len(proposal.requirements) > 3:
            recommendations.append("Present value-based pricing rather than hourly rates")

        recommendations.append("Include performance guarantees to justify premium pricing")

        return recommendations

# Example usage and testing
def main():
    """
    Example usage of the Proposal Generator Agent
    """
    agent = ProposalGeneratorAgent()

    # Generate proposal for fintech client
    client_brief = """
    We need to improve our payment processing security and ensure PCI DSS compliance.
    Currently experiencing issues with transaction delays and need better fraud detection.
    Budget range: €40,000 - €60,000
    """

    proposal = agent.generate_proposal(
        client_name="FinTech Innovations Ltd",
        project_brief=client_brief,
        industry="fintech",
        service_type=ServiceType.IMPLEMENTATION
    )

    print(f"\n📊 Proposal Summary:")
    print(f"   Client: {proposal.client_name}")
    print(f"   Total Cost: €{proposal.total_cost:,.2f}")
    print(f"   Timeline: {proposal.timeline_weeks} weeks")
    print(f"   Total Hours: {proposal.total_hours:.0f}")
    print(f"   Requirements: {len(proposal.requirements)}")
    print(f"   Deliverables: {len(proposal.deliverables)}")

    # Optimize pricing
    optimization = agent.optimize_pricing(proposal, client_budget=50000)
    print(f"\n💰 Pricing Optimization:")
    print(f"   Win Probability: {optimization['win_probability']:.1%}")
    print(f"   Market Position: {optimization['market_position']['position']}")

    # Generate formatted document
    document = agent.format_proposal_document(proposal)
    print(f"\n📄 Proposal document generated ({len(document)} characters)")

if __name__ == "__main__":
    main()