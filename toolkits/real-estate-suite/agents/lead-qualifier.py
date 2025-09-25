"""
Lead Qualifier Agent
Practical lead qualification using OpenAI to score leads and suggest follow-up actions.
For small real estate businesses looking to prioritize leads more systematically.
"""

import asyncio
import json
import logging
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

import openai
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadSource(Enum):
    WEBSITE = "website"
    ZILLOW = "zillow"
    REALTOR_COM = "realtor_com"
    FACEBOOK = "facebook"
    REFERRAL = "referral"
    SIGN_CALL = "sign_call"
    OPEN_HOUSE = "open_house"
    OTHER = "other"

class LeadPriority(Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"

class TimelineUrgency(Enum):
    IMMEDIATE = "immediate"  # 0-30 days
    SHORT_TERM = "short_term"  # 1-3 months
    MEDIUM_TERM = "medium_term"  # 3-6 months
    LONG_TERM = "long_term"  # 6+ months

@dataclass
class LeadProfile:
    """Simple lead profile for qualification."""

    # Basic Information
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

    # Lead Details
    source: LeadSource = LeadSource.OTHER
    initial_inquiry: str = ""
    preferred_contact_method: str = "email"

    # Property Preferences
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    property_type: str = "single_family"
    bedrooms_min: int = 1
    bathrooms_min: float = 1.0
    preferred_areas: List[str] = None

    # Timeline & Motivation
    timeline: TimelineUrgency = TimelineUrgency.MEDIUM_TERM
    motivation_level: int = 5  # 1-10 scale
    pre_approved: bool = False
    current_situation: str = ""

    # Qualification Results
    lead_score: int = 0  # 1-100
    priority: LeadPriority = LeadPriority.WARM
    qualification_date: datetime = None

    def __post_init__(self):
        if self.preferred_areas is None:
            self.preferred_areas = []
        if self.qualification_date is None:
            self.qualification_date = datetime.now()

class SimpleLeadQualifier:
    """Simple but effective lead qualification using OpenAI GPT-4."""

    def __init__(self, openai_api_key: str = None, database_url: str = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
        self.db_engine = None
        if database_url or os.getenv('DATABASE_URL'):
            self.db_engine = create_engine(database_url or os.getenv('DATABASE_URL'))
            self.setup_database()

    def setup_database(self):
        """Initialize simple database table for leads."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            email VARCHAR(255) UNIQUE,
            phone VARCHAR(20),
            source VARCHAR(50),
            initial_inquiry TEXT,
            budget_min INTEGER,
            budget_max INTEGER,
            property_type VARCHAR(50),
            bedrooms_min INTEGER,
            bathrooms_min DECIMAL(3,1),
            preferred_areas TEXT,
            timeline VARCHAR(20),
            motivation_level INTEGER,
            pre_approved BOOLEAN,
            current_situation VARCHAR(100),
            lead_score INTEGER,
            priority VARCHAR(10),
            ai_analysis TEXT,
            qualification_date TIMESTAMP DEFAULT NOW(),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """

        with self.db_engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()

    async def qualify_lead(self, lead_profile: LeadProfile) -> Dict:
        """
        Qualify a lead using AI analysis and rule-based scoring.

        Args:
            lead_profile: LeadProfile object with lead information

        Returns:
            Dict containing qualification results and next steps
        """
        try:
            # Validate email if provided
            if lead_profile.email and not self._is_valid_email(lead_profile.email):
                raise ValueError("Invalid email address")

            # Generate AI analysis
            ai_analysis = await self._get_ai_analysis(lead_profile)

            # Calculate basic lead score
            lead_score = self._calculate_lead_score(lead_profile)

            # Determine priority
            priority = self._determine_priority(lead_score, lead_profile)

            # Update lead profile
            lead_profile.lead_score = lead_score
            lead_profile.priority = priority

            # Save to database if available
            lead_id = None
            if self.db_engine:
                lead_id = self._save_lead(lead_profile, ai_analysis)

            # Generate next steps
            next_steps = self._generate_next_steps(lead_profile)

            return {
                "lead_id": lead_id,
                "lead_score": lead_score,
                "priority": priority.value,
                "ai_analysis": ai_analysis,
                "next_steps": next_steps,
                "recommended_followup": self._get_followup_timeline(lead_profile),
                "qualification_summary": self._get_summary(lead_profile)
            }

        except Exception as e:
            logger.error(f"Error qualifying lead: {str(e)}")
            raise

    async def _get_ai_analysis(self, lead: LeadProfile) -> str:
        """Get AI analysis of the lead."""

        budget_info = f"${lead.budget_min:,} - ${lead.budget_max:,}" if lead.budget_min and lead.budget_max else "Not specified"
        areas_info = ", ".join(lead.preferred_areas) if lead.preferred_areas else "No specific areas"

        prompt = f"""
        Analyze this real estate lead and provide a practical assessment:

        LEAD INFO:
        Name: {lead.first_name} {lead.last_name}
        Email: {lead.email}
        Phone: {lead.phone or 'Not provided'}
        Source: {lead.source.value}
        Inquiry: "{lead.initial_inquiry}"

        PREFERENCES:
        Budget: {budget_info}
        Type: {lead.property_type}, {lead.bedrooms_min}+ BR, {lead.bathrooms_min}+ BA
        Areas: {areas_info}
        Timeline: {lead.timeline.value}
        Pre-approved: {'Yes' if lead.pre_approved else 'No'}
        Motivation (1-10): {lead.motivation_level}

        Provide analysis in this format:

        ASSESSMENT:
        - Readiness: [1-10 score with brief reason]
        - Timeline: [realistic assessment]
        - Budget: [realistic/optimistic/unclear]
        - Strengths: [2-3 key positives]
        - Concerns: [any red flags]

        NEXT STEPS:
        1. [Most important action]
        2. [Secondary action]
        3. [Follow-up plan]

        Keep it concise and actionable.
        """

        try:
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a practical real estate assistant. Provide concise, actionable lead analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return "AI analysis unavailable - using rule-based scoring only"

    def _calculate_lead_score(self, lead: LeadProfile) -> int:
        """Calculate lead score using simple rule-based system."""
        score = 0

        # Source quality (0-25 points)
        source_scores = {
            LeadSource.REFERRAL: 25,
            LeadSource.SIGN_CALL: 20,
            LeadSource.OPEN_HOUSE: 18,
            LeadSource.WEBSITE: 15,
            LeadSource.REALTOR_COM: 12,
            LeadSource.ZILLOW: 10,
            LeadSource.FACEBOOK: 8,
            LeadSource.OTHER: 5
        }
        score += source_scores.get(lead.source, 5)

        # Contact completeness (0-15 points)
        if lead.email:
            score += 8
        if lead.phone:
            score += 7

        # Budget clarity (0-20 points)
        if lead.budget_min and lead.budget_max:
            score += 20
        elif lead.budget_min or lead.budget_max:
            score += 10

        # Timeline urgency (0-15 points)
        timeline_scores = {
            TimelineUrgency.IMMEDIATE: 15,
            TimelineUrgency.SHORT_TERM: 12,
            TimelineUrgency.MEDIUM_TERM: 8,
            TimelineUrgency.LONG_TERM: 4
        }
        score += timeline_scores.get(lead.timeline, 4)

        # Pre-approval status (0-10 points)
        if lead.pre_approved:
            score += 10

        # Motivation level (0-10 points)
        score += lead.motivation_level

        # Specificity bonus (0-5 points)
        if lead.preferred_areas:
            score += 2
        if lead.current_situation:
            score += 2
        if len(lead.initial_inquiry) > 50:
            score += 1

        return min(score, 100)

    def _determine_priority(self, score: int, lead: LeadProfile) -> LeadPriority:
        """Determine lead priority based on score and key factors."""

        # Hot lead conditions
        if (score >= 75 or
            lead.timeline == TimelineUrgency.IMMEDIATE or
            (lead.pre_approved and score >= 60)):
            return LeadPriority.HOT

        # Warm lead conditions
        elif (score >= 50 or
              lead.timeline == TimelineUrgency.SHORT_TERM or
              lead.source in [LeadSource.REFERRAL, LeadSource.SIGN_CALL]):
            return LeadPriority.WARM

        # Cold lead (default)
        else:
            return LeadPriority.COLD

    def _generate_next_steps(self, lead: LeadProfile) -> List[str]:
        """Generate practical next steps based on lead priority."""

        steps = []

        if lead.priority == LeadPriority.HOT:
            steps = [
                "Call within 5-10 minutes",
                "Verify pre-approval status if not confirmed",
                "Schedule property viewing ASAP",
                "Send personalized property matches"
            ]
        elif lead.priority == LeadPriority.WARM:
            steps = [
                "Call within 1-2 hours",
                "Send welcome email with market info",
                "Schedule consultation call",
                "Add to weekly follow-up sequence"
            ]
        else:  # COLD
            steps = [
                "Send informative email response within 4 hours",
                "Add to monthly nurture campaign",
                "Provide market report for their area",
                "Schedule follow-up in 2 weeks"
            ]

        return steps

    def _get_followup_timeline(self, lead: LeadProfile) -> str:
        """Get recommended follow-up timeline."""

        if lead.priority == LeadPriority.HOT:
            return "Every 2-3 days until contact made"
        elif lead.priority == LeadPriority.WARM:
            return "Weekly for first month, then bi-weekly"
        else:
            return "Monthly touchpoints"

    def _get_summary(self, lead: LeadProfile) -> Dict:
        """Generate qualification summary."""

        return {
            "overall_rating": f"{lead.priority.value.upper()} priority ({lead.lead_score}/100)",
            "key_factors": self._identify_key_factors(lead),
            "estimated_timeline": self._estimate_timeline(lead),
            "conversion_likelihood": self._estimate_conversion_likelihood(lead.lead_score)
        }

    def _identify_key_factors(self, lead: LeadProfile) -> List[str]:
        """Identify key positive and negative factors."""
        factors = []

        # Positive factors
        if lead.pre_approved:
            factors.append("Pre-approved financing")
        if lead.source in [LeadSource.REFERRAL, LeadSource.SIGN_CALL]:
            factors.append("High-quality lead source")
        if lead.timeline in [TimelineUrgency.IMMEDIATE, TimelineUrgency.SHORT_TERM]:
            factors.append("Urgent timeline")
        if lead.motivation_level >= 7:
            factors.append("High motivation level")

        # Concerns
        if not lead.budget_min and not lead.budget_max:
            factors.append("Budget not specified")
        if not lead.phone:
            factors.append("No phone contact")
        if lead.motivation_level <= 4:
            factors.append("Low stated motivation")

        return factors

    def _estimate_timeline(self, lead: LeadProfile) -> str:
        """Estimate realistic conversion timeline."""

        if lead.priority == LeadPriority.HOT:
            return "2-6 weeks"
        elif lead.priority == LeadPriority.WARM:
            return "1-3 months"
        else:
            return "3-12 months"

    def _estimate_conversion_likelihood(self, score: int) -> str:
        """Estimate conversion likelihood."""

        if score >= 80:
            return "High (60-80%)"
        elif score >= 60:
            return "Medium (30-60%)"
        elif score >= 40:
            return "Low-Medium (15-30%)"
        else:
            return "Low (5-15%)"

    def _save_lead(self, lead: LeadProfile, ai_analysis: str) -> int:
        """Save lead to database."""

        insert_sql = """
        INSERT INTO leads (
            first_name, last_name, email, phone, source, initial_inquiry,
            budget_min, budget_max, property_type, bedrooms_min, bathrooms_min,
            preferred_areas, timeline, motivation_level, pre_approved,
            current_situation, lead_score, priority, ai_analysis
        ) VALUES (
            %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(source)s, %(initial_inquiry)s,
            %(budget_min)s, %(budget_max)s, %(property_type)s, %(bedrooms_min)s, %(bathrooms_min)s,
            %(preferred_areas)s, %(timeline)s, %(motivation_level)s, %(pre_approved)s,
            %(current_situation)s, %(lead_score)s, %(priority)s, %(ai_analysis)s
        ) RETURNING id
        """

        with self.db_engine.connect() as conn:
            result = conn.execute(text(insert_sql), {
                "first_name": lead.first_name,
                "last_name": lead.last_name,
                "email": lead.email,
                "phone": lead.phone,
                "source": lead.source.value,
                "initial_inquiry": lead.initial_inquiry,
                "budget_min": lead.budget_min,
                "budget_max": lead.budget_max,
                "property_type": lead.property_type,
                "bedrooms_min": lead.bedrooms_min,
                "bathrooms_min": lead.bathrooms_min,
                "preferred_areas": ", ".join(lead.preferred_areas) if lead.preferred_areas else None,
                "timeline": lead.timeline.value,
                "motivation_level": lead.motivation_level,
                "pre_approved": lead.pre_approved,
                "current_situation": lead.current_situation,
                "lead_score": lead.lead_score,
                "priority": lead.priority.value,
                "ai_analysis": ai_analysis
            })
            conn.commit()
            return result.fetchone()[0]

    def _is_valid_email(self, email: str) -> bool:
        """Simple email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

# Example usage
async def main():
    """Example of using the lead qualifier."""

    # Initialize qualifier
    qualifier = SimpleLeadQualifier()

    # Sample lead
    sample_lead = LeadProfile(
        first_name="Sarah",
        last_name="Johnson",
        email="sarah.johnson@email.com",
        phone="(555) 123-4567",
        source=LeadSource.WEBSITE,
        initial_inquiry="Looking for a 3-bedroom home under $500k in downtown area",
        budget_min=400000,
        budget_max=500000,
        property_type="single_family",
        bedrooms_min=3,
        bathrooms_min=2,
        preferred_areas=["Downtown", "Midtown"],
        timeline=TimelineUrgency.SHORT_TERM,
        motivation_level=7,
        pre_approved=False,
        current_situation="Renting, lease expires in 3 months"
    )

    # Qualify the lead
    try:
        result = await qualifier.qualify_lead(sample_lead)

        print("LEAD QUALIFICATION RESULT:")
        print(f"Score: {result['lead_score']}/100")
        print(f"Priority: {result['priority']}")
        print(f"AI Analysis:\n{result['ai_analysis']}")
        print("\nNext Steps:")
        for i, step in enumerate(result['next_steps'], 1):
            print(f"{i}. {step}")
        print(f"\nFollow-up Timeline: {result['recommended_followup']}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())