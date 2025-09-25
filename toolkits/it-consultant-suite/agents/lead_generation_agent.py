"""
Lead Generation & Outreach Agent for IT Consultants
Automates prospect discovery, LinkedIn outreach, and company analysis
"""

import asyncio
import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import yaml
from bs4 import BeautifulSoup
import pandas as pd

@dataclass
class Prospect:
    company_name: str
    industry: str
    size: str
    website: str
    tech_stack: List[str]
    decision_makers: List[Dict]
    pain_points: List[str]
    contact_score: float
    last_contacted: Optional[datetime] = None

class LeadGenerationAgent:
    """
    Comprehensive lead generation agent that identifies, analyzes, and engages
    with potential clients for IT consulting services.
    """

    def __init__(self, config_path: str = "config/linkedin_automation.yaml"):
        self.config = self._load_config(config_path)
        self.prospects_db = []
        self.outreach_templates = self._load_templates()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration settings"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return self._default_config()

    def _default_config(self) -> Dict:
        """Default configuration if file not found"""
        return {
            'target_industries': ['fintech', 'healthtech', 'ecommerce', 'manufacturing'],
            'company_size_range': ['50-200', '200-1000'],
            'geographic_focus': ['UK', 'EU', 'North America'],
            'tech_stack_indicators': ['WordPress', 'Shopify', 'Salesforce', 'AWS'],
            'outreach_limits': {
                'linkedin_daily': 50,
                'email_daily': 100
            }
        }

    def _load_templates(self) -> Dict:
        """Load outreach message templates"""
        return {
            'linkedin_connection': {
                'fintech': "Hi {name}, I noticed your work in fintech security. I help companies like {company} implement robust compliance solutions. Would love to connect!",
                'healthtech': "Hi {name}, Your healthcare technology initiatives caught my attention. I specialize in HIPAA-compliant infrastructure for companies like {company}.",
                'ecommerce': "Hi {name}, I see {company} is scaling rapidly. I help e-commerce companies optimize their tech stack for growth and security.",
                'default': "Hi {name}, I help companies optimize their technology infrastructure. Noticed some interesting challenges at {company}."
            },
            'follow_up_email': {
                'subject': "Quick question about {company}'s tech infrastructure",
                'body': """Hi {name},

I recently analyzed {company}'s technology stack and noticed a few optimization opportunities that could save you significant costs while improving performance.

I've helped similar companies in {industry} reduce infrastructure costs by 30-40% while improving security and scalability.

Would you be interested in a brief 15-minute call to discuss:
- {pain_point_1}
- {pain_point_2}
- {pain_point_3}

Best regards,
{consultant_name}"""
            }
        }

    async def find_prospects(self, industry: str, location: str, min_employees: int = 50) -> List[Prospect]:
        """
        Find potential prospects based on criteria
        """
        print(f"🔍 Searching for {industry} companies in {location} with {min_employees}+ employees...")

        # Simulate company discovery (would integrate with APIs like LinkedIn Sales Navigator, ZoomInfo, etc.)
        prospects = await self._discover_companies(industry, location, min_employees)

        # Analyze each prospect
        analyzed_prospects = []
        for company_data in prospects:
            prospect = await self._analyze_company(company_data)
            if prospect and prospect.contact_score > 0.6:  # Only high-quality prospects
                analyzed_prospects.append(prospect)

        print(f"✅ Found {len(analyzed_prospects)} qualified prospects")
        return analyzed_prospects

    async def _discover_companies(self, industry: str, location: str, min_employees: int) -> List[Dict]:
        """
        Discover companies matching criteria
        """
        # Mock data - in real implementation, would use APIs
        companies = [
            {
                'name': 'TechFlow Solutions',
                'industry': industry,
                'size': '100-500',
                'website': 'https://techflowsolutions.com',
                'location': location
            },
            {
                'name': 'Digital Dynamics Ltd',
                'industry': industry,
                'size': '50-200',
                'website': 'https://digitaldynamics.co.uk',
                'location': location
            },
            {
                'name': 'Innovation Partners',
                'industry': industry,
                'size': '200-1000',
                'website': 'https://innovationpartners.eu',
                'location': location
            }
        ]

        await asyncio.sleep(1)  # Simulate API delay
        return companies

    async def _analyze_company(self, company_data: Dict) -> Optional[Prospect]:
        """
        Analyze a company's tech stack and identify opportunities
        """
        try:
            # Analyze website technology
            tech_stack = await self._analyze_tech_stack(company_data['website'])

            # Identify decision makers
            decision_makers = await self._find_decision_makers(company_data['name'])

            # Assess pain points
            pain_points = self._identify_pain_points(tech_stack, company_data['industry'])

            # Calculate contact score
            contact_score = self._calculate_contact_score(tech_stack, decision_makers, pain_points)

            return Prospect(
                company_name=company_data['name'],
                industry=company_data['industry'],
                size=company_data['size'],
                website=company_data['website'],
                tech_stack=tech_stack,
                decision_makers=decision_makers,
                pain_points=pain_points,
                contact_score=contact_score
            )

        except Exception as e:
            print(f"❌ Error analyzing {company_data['name']}: {str(e)}")
            return None

    async def _analyze_tech_stack(self, website: str) -> List[str]:
        """
        Analyze website to determine technology stack
        """
        try:
            # Mock tech stack analysis
            tech_stacks = {
                'https://techflowsolutions.com': ['WordPress', 'MySQL', 'AWS', 'Cloudflare'],
                'https://digitaldynamics.co.uk': ['Shopify', 'React', 'Node.js', 'Stripe'],
                'https://innovationpartners.eu': ['Drupal', 'PostgreSQL', 'Docker', 'Azure']
            }

            await asyncio.sleep(0.5)  # Simulate analysis time
            return tech_stacks.get(website, ['Unknown CMS', 'Standard hosting'])

        except Exception:
            return ['Analysis failed']

    async def _find_decision_makers(self, company_name: str) -> List[Dict]:
        """
        Find key decision makers at target company
        """
        # Mock decision maker data
        decision_makers = [
            {
                'name': 'Sarah Johnson',
                'title': 'CTO',
                'linkedin': f'linkedin.com/in/sarah-johnson-{company_name.lower().replace(" ", "")}',
                'email_pattern': 'sarah.johnson@{domain}',
                'authority_level': 'high'
            },
            {
                'name': 'Michael Chen',
                'title': 'IT Director',
                'linkedin': f'linkedin.com/in/michael-chen-{company_name.lower().replace(" ", "")}',
                'email_pattern': 'm.chen@{domain}',
                'authority_level': 'medium'
            }
        ]

        await asyncio.sleep(0.3)
        return decision_makers

    def _identify_pain_points(self, tech_stack: List[str], industry: str) -> List[str]:
        """
        Identify potential pain points based on tech stack and industry
        """
        pain_points = []

        # Technology-based pain points
        if 'WordPress' in tech_stack:
            pain_points.append('WordPress security vulnerabilities need regular monitoring')
        if 'AWS' not in tech_stack and 'Azure' not in tech_stack:
            pain_points.append('Missing cloud infrastructure for scalability')

        # Industry-specific pain points
        industry_pain_points = {
            'fintech': [
                'PCI DSS compliance requirements',
                'Real-time fraud detection needs',
                'API security for payment processing'
            ],
            'healthtech': [
                'HIPAA compliance gaps',
                'Patient data encryption requirements',
                'Interoperability challenges'
            ],
            'ecommerce': [
                'Website performance during traffic spikes',
                'Payment gateway optimization',
                'Inventory management integration'
            ]
        }

        pain_points.extend(industry_pain_points.get(industry, []))
        return pain_points[:3]  # Top 3 pain points

    def _calculate_contact_score(self, tech_stack: List[str], decision_makers: List[Dict], pain_points: List[str]) -> float:
        """
        Calculate how promising this prospect is (0-1 score)
        """
        score = 0.0

        # Tech stack indicators
        if any(tech in tech_stack for tech in ['WordPress', 'Drupal', 'Joomla']):
            score += 0.3  # CMS indicates potential for optimization

        if not any(cloud in tech_stack for cloud in ['AWS', 'Azure', 'GCP']):
            score += 0.2  # No cloud = migration opportunity

        # Decision maker accessibility
        if decision_makers:
            score += 0.3
            if any(dm['authority_level'] == 'high' for dm in decision_makers):
                score += 0.2

        # Pain points = opportunities
        score += len(pain_points) * 0.1

        return min(score, 1.0)

    async def generate_outreach_messages(self, prospect: Prospect) -> Dict[str, str]:
        """
        Generate personalized outreach messages for a prospect
        """
        decision_maker = prospect.decision_makers[0] if prospect.decision_makers else {'name': 'there'}

        # Choose template based on industry
        industry_key = prospect.industry if prospect.industry in self.outreach_templates['linkedin_connection'] else 'default'

        linkedin_message = self.outreach_templates['linkedin_connection'][industry_key].format(
            name=decision_maker.get('name', 'there'),
            company=prospect.company_name
        )

        email_message = self.outreach_templates['follow_up_email']['body'].format(
            name=decision_maker.get('name', 'there'),
            company=prospect.company_name,
            industry=prospect.industry,
            pain_point_1=prospect.pain_points[0] if len(prospect.pain_points) > 0 else "Infrastructure optimization",
            pain_point_2=prospect.pain_points[1] if len(prospect.pain_points) > 1 else "Security enhancements",
            pain_point_3=prospect.pain_points[2] if len(prospect.pain_points) > 2 else "Cost reduction strategies",
            consultant_name="Your Name"
        )

        return {
            'linkedin_connection': linkedin_message,
            'follow_up_email': email_message,
            'email_subject': self.outreach_templates['follow_up_email']['subject'].format(
                company=prospect.company_name
            )
        }

    def track_outreach_campaign(self, prospect: Prospect, message_type: str) -> Dict:
        """
        Track outreach campaign performance
        """
        campaign_data = {
            'prospect_id': f"{prospect.company_name.lower().replace(' ', '_')}",
            'message_type': message_type,
            'sent_date': datetime.now(),
            'industry': prospect.industry,
            'contact_score': prospect.contact_score,
            'status': 'sent'
        }

        # In real implementation, would store in database
        print(f"📧 Tracked outreach: {message_type} to {prospect.company_name}")
        return campaign_data

    def generate_campaign_report(self) -> Dict:
        """
        Generate campaign performance report
        """
        # Mock campaign data
        report = {
            'period': '30 days',
            'total_prospects_identified': 85,
            'qualified_prospects': 24,
            'outreach_sent': 18,
            'responses_received': 6,
            'meetings_scheduled': 3,
            'proposals_requested': 2,
            'conversion_metrics': {
                'response_rate': '33.3%',
                'meeting_rate': '16.7%',
                'proposal_rate': '11.1%'
            },
            'top_performing_industries': ['fintech', 'healthtech'],
            'recommended_actions': [
                'Increase focus on fintech sector',
                'Improve healthcare messaging',
                'Follow up on pending responses'
            ]
        }

        return report

# Example usage and testing
async def main():
    """
    Example usage of the Lead Generation Agent
    """
    agent = LeadGenerationAgent()

    # Find prospects in fintech
    prospects = await agent.find_prospects('fintech', 'London', 50)

    print(f"\n📊 Found {len(prospects)} prospects:")
    for prospect in prospects[:3]:  # Show first 3
        print(f"\n🏢 {prospect.company_name}")
        print(f"   Industry: {prospect.industry}")
        print(f"   Tech Stack: {', '.join(prospect.tech_stack)}")
        print(f"   Contact Score: {prospect.contact_score:.2f}")
        print(f"   Pain Points: {len(prospect.pain_points)} identified")

        # Generate outreach messages
        messages = await agent.generate_outreach_messages(prospect)
        print(f"   LinkedIn Message: {messages['linkedin_connection'][:100]}...")

    # Generate campaign report
    report = agent.generate_campaign_report()
    print(f"\n📈 Campaign Report:")
    print(f"   Response Rate: {report['conversion_metrics']['response_rate']}")
    print(f"   Meeting Rate: {report['conversion_metrics']['meeting_rate']}")

if __name__ == "__main__":
    asyncio.run(main())