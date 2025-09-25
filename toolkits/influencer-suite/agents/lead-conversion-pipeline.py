"""
Lead Conversion Pipeline - AI Agent
Automated funnel from content consumption to course purchase
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import stripe
import requests
import openai
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import smtplib

class LeadStage(Enum):
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    PURCHASE = "purchase"
    RETENTION = "retention"
    ADVOCACY = "advocacy"

@dataclass
class Lead:
    email: str
    name: str
    source: str
    stage: LeadStage
    score: int
    created_at: datetime
    last_interaction: Optional[datetime] = None
    lifetime_value: float = 0.0
    products_purchased: List[str] = None
    preferences: Dict = None
    notes: str = ""

@dataclass
class Product:
    id: str
    name: str
    price: float
    type: str  # tripwire, core, premium
    conversion_rate: float
    profit_margin: float

@dataclass
class Campaign:
    id: str
    name: str
    type: str
    target_stage: LeadStage
    trigger_conditions: Dict
    sequence_emails: List[Dict]
    success_metrics: Dict

class LeadConversionPipeline:
    def __init__(self, config: Dict):
        self.config = config
        self.openai_client = openai.OpenAI(api_key=config['openai_api_key'])
        self.stripe_client = stripe
        stripe.api_key = config['stripe_api_key']

        self.db_path = config.get('database_path', 'lead_pipeline.db')
        self._init_database()

        # Product catalog
        self.products = {
            'tripwire': Product(
                id='ai-automation-starter',
                name='AI Automation Starter Guide',
                price=27.0,
                type='tripwire',
                conversion_rate=0.15,
                profit_margin=0.95
            ),
            'core': Product(
                id='productivity-mastery',
                name='Productivity Mastery Program',
                price=297.0,
                type='core',
                conversion_rate=0.25,
                profit_margin=0.85
            ),
            'premium': Product(
                id='ai-transformation-coaching',
                name='AI Transformation 1:1 Coaching',
                price=2997.0,
                type='premium',
                conversion_rate=0.60,
                profit_margin=0.90
            )
        }

        # Email sequences
        self.email_sequences = {
            'welcome_series': [
                {
                    'delay_hours': 0,
                    'subject': 'Welcome! Your AI productivity guide is here 🚀',
                    'template': 'welcome_immediate_value'
                },
                {
                    'delay_hours': 72,
                    'subject': 'The #1 mistake killing your productivity',
                    'template': 'problem_agitation'
                },
                {
                    'delay_hours': 168,
                    'subject': 'Case study: How Sarah saved 20 hours/week',
                    'template': 'social_proof_story'
                }
            ],
            'tripwire_nurture': [
                {
                    'delay_hours': 24,
                    'subject': 'Your next step: Productivity Mastery Program',
                    'template': 'tripwire_upsell'
                },
                {
                    'delay_hours': 168,
                    'subject': 'Limited time: 50% off Productivity Mastery',
                    'template': 'scarcity_offer'
                }
            ],
            'core_nurture': [
                {
                    'delay_hours': 720,  # 30 days
                    'subject': 'Ready for 1:1 transformation?',
                    'template': 'premium_invitation'
                }
            ],
            'webinar_sequence': [
                {
                    'delay_hours': 0,
                    'subject': 'Your seat is confirmed! What to expect...',
                    'template': 'webinar_confirmation'
                },
                {
                    'delay_hours': 24,
                    'subject': 'Tomorrow: The AI Productivity Masterclass',
                    'template': 'webinar_reminder'
                },
                {
                    'delay_hours': 48,
                    'subject': 'Replay + Special Offer (24 hours only)',
                    'template': 'webinar_replay_offer'
                }
            ]
        }

        # Lead scoring weights
        self.scoring_weights = {
            'email_opens': 5,
            'email_clicks': 10,
            'content_engagement': 15,
            'webinar_attendance': 25,
            'discovery_call_booked': 50,
            'purchase_intent_signals': 30,
            'website_visits': 8,
            'resource_downloads': 12
        }

    def _init_database(self):
        """Initialize database for lead tracking"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                source TEXT,
                stage TEXT,
                score INTEGER DEFAULT 0,
                created_at TIMESTAMP,
                last_interaction TIMESTAMP,
                lifetime_value REAL DEFAULT 0.0,
                products_purchased TEXT,
                preferences TEXT,
                notes TEXT
            )
        ''')

        # Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                interaction_type TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                value INTEGER,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')

        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT UNIQUE,
                name TEXT,
                type TEXT,
                status TEXT,
                created_at TIMESTAMP,
                metrics TEXT
            )
        ''')

        # Purchases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER,
                product_id TEXT,
                amount REAL,
                purchase_date TIMESTAMP,
                stripe_payment_id TEXT,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')

        conn.commit()
        conn.close()

    def capture_lead(self, email: str, name: str, source: str, lead_magnet: str = None) -> Lead:
        """Capture new lead and initiate nurture sequence"""

        # Create lead object
        lead = Lead(
            email=email,
            name=name,
            source=source,
            stage=LeadStage.AWARENESS,
            score=self._calculate_initial_score(source),
            created_at=datetime.now(),
            products_purchased=[],
            preferences={}
        )

        # Save to database
        self._save_lead(lead)

        # Trigger welcome sequence
        self._trigger_email_sequence(lead, 'welcome_series')

        # Score based on lead magnet
        if lead_magnet:
            self._update_lead_score(lead, 'resource_downloads', 1)

        return lead

    def _calculate_initial_score(self, source: str) -> int:
        """Calculate initial lead score based on source"""

        source_scores = {
            'linkedin_organic': 25,
            'linkedin_ad': 20,
            'webinar_registration': 40,
            'content_download': 30,
            'referral': 35,
            'direct_website': 15,
            'social_media': 10
        }

        return source_scores.get(source, 10)

    def score_lead_interaction(self, lead: Lead, interaction_type: str, interaction_data: Dict = None):
        """Score lead based on interaction and update pipeline stage"""

        # Calculate interaction value
        base_value = self.scoring_weights.get(interaction_type, 5)

        # Apply multipliers based on interaction data
        multiplier = 1.0
        if interaction_data:
            # Time spent on page
            if 'time_spent' in interaction_data:
                time_minutes = interaction_data['time_spent'] / 60
                if time_minutes > 5:
                    multiplier *= 1.5
                elif time_minutes > 2:
                    multiplier *= 1.2

            # Multiple interactions in session
            if 'session_interactions' in interaction_data:
                if interaction_data['session_interactions'] > 3:
                    multiplier *= 1.3

        final_value = int(base_value * multiplier)

        # Update lead score
        self._update_lead_score(lead, interaction_type, final_value)

        # Check for stage progression
        self._evaluate_stage_progression(lead)

        # Log interaction
        self._log_interaction(lead, interaction_type, interaction_data, final_value)

    def _evaluate_stage_progression(self, lead: Lead):
        """Evaluate if lead should progress to next stage"""

        current_score = self._get_current_score(lead)
        current_stage = lead.stage

        # Stage progression thresholds
        thresholds = {
            LeadStage.AWARENESS: 50,      # Interested in content
            LeadStage.INTEREST: 100,      # Engaged with multiple pieces
            LeadStage.CONSIDERATION: 200, # Downloaded resources, attended webinar
            LeadStage.INTENT: 350,        # Booked discovery call or high engagement
            LeadStage.PURCHASE: 500       # Ready to buy
        }

        # Check for progression
        for stage, threshold in thresholds.items():
            if current_score >= threshold and current_stage.value < stage.value:
                self._progress_lead_stage(lead, stage)

    def _progress_lead_stage(self, lead: Lead, new_stage: LeadStage):
        """Progress lead to new stage and trigger appropriate actions"""

        old_stage = lead.stage
        lead.stage = new_stage

        # Update in database
        self._update_lead_stage(lead, new_stage)

        # Trigger stage-specific actions
        if new_stage == LeadStage.INTEREST:
            self._trigger_interest_actions(lead)
        elif new_stage == LeadStage.CONSIDERATION:
            self._trigger_consideration_actions(lead)
        elif new_stage == LeadStage.INTENT:
            self._trigger_intent_actions(lead)
        elif new_stage == LeadStage.PURCHASE:
            self._trigger_purchase_actions(lead)

        print(f"Lead {lead.email} progressed from {old_stage.value} to {new_stage.value}")

    def _trigger_interest_actions(self, lead: Lead):
        """Actions for leads showing interest"""

        # Send targeted content based on interests
        self._send_personalized_content(lead)

        # Invite to webinar
        self._invite_to_webinar(lead)

    def _trigger_consideration_actions(self, lead: Lead):
        """Actions for leads in consideration stage"""

        # Offer tripwire product
        self._send_tripwire_offer(lead)

        # Send social proof content
        self._send_social_proof(lead)

    def _trigger_intent_actions(self, lead: Lead):
        """Actions for leads showing purchase intent"""

        # Offer discovery call
        self._offer_discovery_call(lead)

        # Send core program information
        self._send_core_program_info(lead)

    def _trigger_purchase_actions(self, lead: Lead):
        """Actions for purchase-ready leads"""

        # Send personalized offer
        self._send_personalized_offer(lead)

        # Flag for personal outreach
        self._flag_for_personal_outreach(lead)

    def create_webinar_funnel(self, webinar_topic: str, date: datetime) -> Dict:
        """Create automated webinar funnel"""

        funnel = {
            'registration_page': self._create_registration_page(webinar_topic),
            'email_sequence': self.email_sequences['webinar_sequence'],
            'thank_you_page': self._create_thank_you_page(),
            'replay_page': self._create_replay_page(),
            'offer_page': self._create_offer_page()
        }

        # Create campaign tracking
        campaign = Campaign(
            id=f"webinar_{datetime.now().strftime('%Y%m%d')}",
            name=f"Webinar: {webinar_topic}",
            type="webinar",
            target_stage=LeadStage.CONSIDERATION,
            trigger_conditions={'webinar_registration': True},
            sequence_emails=self.email_sequences['webinar_sequence'],
            success_metrics={'registration_goal': 500, 'attendance_goal': 200, 'conversion_goal': 20}
        )

        self._save_campaign(campaign)

        return funnel

    def _create_registration_page(self, topic: str) -> Dict:
        """Generate webinar registration page content"""

        prompt = f"""
        Create compelling webinar registration page copy for:
        Topic: {topic}
        Target: AI/productivity micro-influencers wanting to scale

        Include:
        1. Attention-grabbing headline
        2. 3-4 key benefits/takeaways
        3. Social proof elements
        4. Urgency/scarcity
        5. Clear registration CTA
        6. Speaker bio/credibility

        Format as JSON with sections.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        try:
            content = json.loads(response.choices[0].message.content)
        except:
            content = {
                "headline": f"Master {topic} in 60 Minutes",
                "benefits": ["Save 10+ hours per week", "Automate repetitive tasks", "Scale your influence"],
                "cta": "Reserve Your Free Seat Now"
            }

        return content

    def process_tripwire_purchase(self, lead: Lead, product_id: str, payment_data: Dict) -> Dict:
        """Process tripwire purchase and trigger upsell sequence"""

        product = self.products.get('tripwire')

        # Validate payment with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_data['payment_intent_id'])

        if payment_intent.status == 'succeeded':
            # Record purchase
            self._record_purchase(lead, product_id, product.price, payment_data['payment_intent_id'])

            # Update lead stage and score
            lead.stage = LeadStage.PURCHASE
            self._update_lead_score(lead, 'purchase', 100)

            # Deliver product
            self._deliver_digital_product(lead, product_id)

            # Trigger upsell sequence
            self._trigger_email_sequence(lead, 'tripwire_nurture')

            # Update lifetime value
            lead.lifetime_value += product.price
            self._update_lead_lifetime_value(lead, product.price)

            return {
                'success': True,
                'next_step': 'upsell_sequence_triggered',
                'delivery_status': 'completed'
            }

        return {'success': False, 'error': 'Payment validation failed'}

    def create_discovery_call_funnel(self) -> Dict:
        """Create automated discovery call booking funnel"""

        funnel = {
            'qualification_questions': [
                {
                    'question': 'What is your current monthly revenue?',
                    'type': 'multiple_choice',
                    'options': ['< $5K', '$5K-$15K', '$15K-$50K', '$50K+'],
                    'scoring': {'< $5K': 10, '$5K-$15K': 25, '$15K-$50K': 40, '$50K+': 50}
                },
                {
                    'question': 'What is your biggest growth challenge?',
                    'type': 'multiple_choice',
                    'options': ['Content creation', 'Lead generation', 'Conversion', 'Scaling systems'],
                    'scoring': {'Content creation': 20, 'Lead generation': 30, 'Conversion': 40, 'Scaling systems': 50}
                },
                {
                    'question': 'When are you looking to implement?',
                    'type': 'multiple_choice',
                    'options': ['Immediately', 'Next 30 days', 'Next 90 days', 'Just exploring'],
                    'scoring': {'Immediately': 50, 'Next 30 days': 40, 'Next 90 days': 20, 'Just exploring': 5}
                }
            ],
            'calendar_integration': 'calendly',
            'pre_call_sequence': [
                'Confirmation email with calendar details',
                'Prep worksheet for maximum value',
                'Case study examples relevant to their situation'
            ],
            'post_call_sequence': [
                'Thank you + next steps email',
                'Proposal delivery (if qualified)',
                'Follow-up sequence for objection handling'
            ]
        }

        return funnel

    def analyze_conversion_funnel(self, timeframe_days: int = 30) -> Dict:
        """Analyze conversion funnel performance"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get leads by stage in timeframe
        start_date = (datetime.now() - timedelta(days=timeframe_days)).isoformat()

        cursor.execute('''
            SELECT stage, COUNT(*) as count
            FROM leads
            WHERE created_at >= ?
            GROUP BY stage
        ''', (start_date,))

        stage_counts = dict(cursor.fetchall())

        # Get conversion rates
        cursor.execute('''
            SELECT
                COUNT(CASE WHEN stage = 'awareness' THEN 1 END) as awareness,
                COUNT(CASE WHEN stage = 'interest' THEN 1 END) as interest,
                COUNT(CASE WHEN stage = 'consideration' THEN 1 END) as consideration,
                COUNT(CASE WHEN stage = 'intent' THEN 1 END) as intent,
                COUNT(CASE WHEN stage = 'purchase' THEN 1 END) as purchase
            FROM leads
            WHERE created_at >= ?
        ''', (start_date,))

        conversion_data = cursor.fetchone()

        # Calculate conversion rates
        total_leads = conversion_data[0] if conversion_data[0] > 0 else 1

        funnel_analysis = {
            'total_leads': total_leads,
            'stage_distribution': stage_counts,
            'conversion_rates': {
                'awareness_to_interest': (conversion_data[1] / total_leads) * 100,
                'interest_to_consideration': (conversion_data[2] / conversion_data[1]) * 100 if conversion_data[1] > 0 else 0,
                'consideration_to_intent': (conversion_data[3] / conversion_data[2]) * 100 if conversion_data[2] > 0 else 0,
                'intent_to_purchase': (conversion_data[4] / conversion_data[3]) * 100 if conversion_data[3] > 0 else 0,
                'overall_conversion': (conversion_data[4] / total_leads) * 100
            },
            'bottlenecks': self._identify_bottlenecks(conversion_data),
            'recommendations': self._generate_funnel_recommendations(conversion_data)
        }

        conn.close()

        return funnel_analysis

    def _identify_bottlenecks(self, conversion_data: Tuple) -> List[str]:
        """Identify conversion bottlenecks"""

        bottlenecks = []

        # Calculate drop-off rates
        awareness, interest, consideration, intent, purchase = conversion_data

        if interest / awareness < 0.3:  # Less than 30% interest rate
            bottlenecks.append("Low awareness to interest conversion - improve content quality/targeting")

        if consideration / interest < 0.4:  # Less than 40% consideration rate
            bottlenecks.append("Low interest to consideration - need better lead magnets/nurture sequence")

        if intent / consideration < 0.25:  # Less than 25% intent rate
            bottlenecks.append("Low consideration to intent - improve social proof and urgency")

        if purchase / intent < 0.6:  # Less than 60% purchase rate
            bottlenecks.append("Low intent to purchase - optimize pricing/offer/objection handling")

        return bottlenecks

    def _generate_funnel_recommendations(self, conversion_data: Tuple) -> List[str]:
        """Generate optimization recommendations"""

        recommendations = [
            "A/B test email subject lines for 20% open rate improvement",
            "Add more social proof elements to landing pages",
            "Implement exit-intent popups with lead magnets",
            "Create urgency with limited-time offers",
            "Segment email list for better personalization",
            "Add video testimonials to key conversion pages",
            "Optimize mobile experience for better conversions",
            "Implement retargeting campaigns for warm leads"
        ]

        return recommendations

    def predict_lifetime_value(self, lead: Lead) -> float:
        """Predict customer lifetime value based on current data"""

        # Base prediction on lead score, source, and interactions
        base_value = 0

        # Score-based prediction
        if lead.score > 350:
            base_value = 500  # Likely premium customer
        elif lead.score > 200:
            base_value = 300  # Likely core program customer
        elif lead.score > 100:
            base_value = 100  # Likely tripwire customer
        else:
            base_value = 50   # Email subscriber value

        # Source quality multiplier
        source_multipliers = {
            'webinar_registration': 1.5,
            'referral': 1.8,
            'linkedin_organic': 1.2,
            'content_download': 1.1,
            'linkedin_ad': 1.0,
            'social_media': 0.8
        }

        multiplier = source_multipliers.get(lead.source, 1.0)
        predicted_ltv = base_value * multiplier

        return round(predicted_ltv, 2)

    def optimize_email_sequences(self, sequence_name: str) -> Dict:
        """Optimize email sequences using AI"""

        # Analyze current performance
        performance_data = self._get_sequence_performance(sequence_name)

        # Generate optimization suggestions
        optimization_prompt = f"""
        Optimize this email sequence based on performance data:

        Sequence: {sequence_name}
        Current metrics: {json.dumps(performance_data, indent=2)}

        Target audience: AI/productivity micro-influencers
        Goal: Increase conversions by 25%

        Provide specific improvements for:
        1. Subject lines (open rate optimization)
        2. Email content (engagement optimization)
        3. CTAs (click-through optimization)
        4. Timing (delivery optimization)
        5. Personalization (relevance optimization)

        Return JSON with detailed recommendations.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": optimization_prompt}],
            temperature=0.7
        )

        try:
            optimizations = json.loads(response.choices[0].message.content)
        except:
            optimizations = {
                "subject_lines": ["Add numbers and curiosity gaps"],
                "content": ["Include more social proof"],
                "ctas": ["Make CTAs more specific and action-oriented"],
                "timing": ["Test different send times"],
                "personalization": ["Use more dynamic content blocks"]
            }

        return optimizations

    # Database helper methods
    def _save_lead(self, lead: Lead):
        """Save lead to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO leads
            (email, name, source, stage, score, created_at, lifetime_value, products_purchased, preferences, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lead.email, lead.name, lead.source, lead.stage.value,
            lead.score, lead.created_at.isoformat(), lead.lifetime_value,
            json.dumps(lead.products_purchased or []),
            json.dumps(lead.preferences or {}), lead.notes
        ))

        conn.commit()
        conn.close()

    def _update_lead_score(self, lead: Lead, interaction_type: str, value: int):
        """Update lead score in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE leads
            SET score = score + ?, last_interaction = ?
            WHERE email = ?
        ''', (value, datetime.now().isoformat(), lead.email))

        conn.commit()
        conn.close()

        lead.score += value
        lead.last_interaction = datetime.now()

    def _log_interaction(self, lead: Lead, interaction_type: str, interaction_data: Dict, value: int):
        """Log lead interaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get lead ID
        cursor.execute('SELECT id FROM leads WHERE email = ?', (lead.email,))
        lead_id = cursor.fetchone()[0]

        cursor.execute('''
            INSERT INTO interactions
            (lead_id, interaction_type, content, timestamp, value)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            lead_id, interaction_type, json.dumps(interaction_data or {}),
            datetime.now().isoformat(), value
        ))

        conn.commit()
        conn.close()

    def _record_purchase(self, lead: Lead, product_id: str, amount: float, stripe_payment_id: str):
        """Record purchase in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get lead ID
        cursor.execute('SELECT id FROM leads WHERE email = ?', (lead.email,))
        lead_id = cursor.fetchone()[0]

        cursor.execute('''
            INSERT INTO purchases
            (lead_id, product_id, amount, purchase_date, stripe_payment_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (lead_id, product_id, amount, datetime.now().isoformat(), stripe_payment_id))

        conn.commit()
        conn.close()

    def _get_current_score(self, lead: Lead) -> int:
        """Get current lead score from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT score FROM leads WHERE email = ?', (lead.email,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else 0

    def _trigger_email_sequence(self, lead: Lead, sequence_name: str):
        """Trigger email sequence for lead"""
        # In real implementation, integrate with email service provider
        print(f"Triggering {sequence_name} sequence for {lead.email}")

    def _get_sequence_performance(self, sequence_name: str) -> Dict:
        """Get email sequence performance metrics"""
        # Mock performance data
        return {
            "open_rate": 0.45,
            "click_rate": 0.12,
            "conversion_rate": 0.08,
            "unsubscribe_rate": 0.02
        }

# Additional helper methods would be implemented here for:
# - Email delivery integration
# - Calendly integration
# - Stripe webhook handling
# - Analytics and reporting
# - A/B testing functionality


# Example usage
if __name__ == "__main__":
    config = {
        'openai_api_key': 'your-openai-key',
        'stripe_api_key': 'your-stripe-key',
        'database_path': 'lead_pipeline.db'
    }

    pipeline = LeadConversionPipeline(config)

    # Capture new lead
    lead = pipeline.capture_lead(
        email='alex@example.com',
        name='Alex Chen',
        source='linkedin_organic',
        lead_magnet='AI Tools Guide'
    )

    # Score interaction
    pipeline.score_lead_interaction(
        lead,
        'email_opens',
        {'time_spent': 300, 'session_interactions': 2}
    )

    # Analyze funnel
    analysis = pipeline.analyze_conversion_funnel(30)
    print("Funnel analysis:", json.dumps(analysis, indent=2))