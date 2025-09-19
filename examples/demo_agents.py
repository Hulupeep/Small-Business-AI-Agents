"""
Demo script showcasing both business agents in action
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents.customer_service import CustomerServiceChatbot, demo_customer_service
from agents.lead_qualifier import LeadQualifierAgent, LeadSource, demo_lead_qualifier
from integrations.crm_integrations import setup_crm_integrations
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def comprehensive_demo():
    """
    Comprehensive demonstration of both agents working together
    """
    print("🚀 BUSINESS AGENTS COMPREHENSIVE DEMO")
    print("=" * 60)
    print()

    # Initialize agents
    print("🔧 Initializing agents...")
    customer_service = CustomerServiceChatbot()
    lead_qualifier = LeadQualifierAgent()

    # Scenario 1: Website visitor becomes lead then needs support
    print("\n📋 SCENARIO 1: Website Visitor Journey")
    print("-" * 40)

    # Step 1: Visitor fills out contact form (becomes lead)
    print("\n1️⃣ Visitor fills out contact form")
    lead_data = {
        "email": "sarah.johnson@techstartup.com",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "company": "TechStartup Inc",
        "job_title": "Chief Technology Officer",
        "phone": "+1-555-0199",
        "website": "techstartup.com",
        "company_size": "small",
        "industry": "technology"
    }

    lead_id = lead_qualifier.capture_lead(lead_data, LeadSource.WEBSITE_FORM)
    bant_score = lead_qualifier.qualify_lead(lead_id)

    print(f"✅ Lead captured and qualified:")
    print(f"   • BANT Score: {bant_score.overall_score:.1f}/100")
    print(f"   • Status: Qualified" if bant_score.overall_score >= 75 else f"   • Status: Nurturing")

    # Step 2: Lead starts chat for support
    print(f"\n2️⃣ {lead_data['first_name']} starts chat session")
    customer_id = f"customer_{lead_id}"
    conversation_id = customer_service.start_conversation(customer_id, "web")

    # Simulate conversation
    support_messages = [
        "Hi, I'm interested in your product but have some questions",
        "What's your pricing for a team of 20 developers?",
        "Do you offer API access?",
        "Can I get a demo scheduled?"
    ]

    for message in support_messages:
        print(f"👤 Sarah: {message}")
        response = customer_service.process_message(conversation_id, message)
        print(f"🤖 Agent: {response[:100]}...")
        print()

    # Scenario 2: Bulk lead processing
    print("\n📋 SCENARIO 2: Bulk Lead Processing")
    print("-" * 40)

    bulk_leads = [
        {
            "email": "john.doe@enterprise.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "Enterprise Corp",
            "job_title": "CEO",
            "company_size": "enterprise",
            "industry": "finance"
        },
        {
            "email": "jane.smith@startup.io",
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "Startup.io",
            "job_title": "Marketing Manager",
            "company_size": "startup",
            "industry": "saas"
        },
        {
            "email": "bob.wilson@midsize.com",
            "first_name": "Bob",
            "last_name": "Wilson",
            "company": "MidSize Solutions",
            "job_title": "VP of Operations",
            "company_size": "medium",
            "industry": "consulting"
        }
    ]

    print(f"📥 Processing {len(bulk_leads)} leads from email campaign...")

    lead_ids = lead_qualifier.bulk_import_leads(bulk_leads, LeadSource.EMAIL)

    for i, lead_id in enumerate(lead_ids):
        bant_score = lead_qualifier.qualify_lead(lead_id)
        lead = lead_qualifier._get_lead(lead_id)

        print(f"   {i+1}. {lead.first_name} {lead.last_name} ({lead.company})")
        print(f"      Score: {bant_score.overall_score:.1f}/100 | Status: {lead.status.value}")

    # Scenario 3: Customer support escalation
    print("\n📋 SCENARIO 3: Support Escalation")
    print("-" * 40)

    escalation_conversation = customer_service.start_conversation("customer_escalation", "email")

    escalation_messages = [
        "I've been trying to cancel my subscription for weeks",
        "This is completely unacceptable - I want a full refund",
        "I'm going to report this to my attorney if not resolved"
    ]

    for message in escalation_messages:
        print(f"😠 Angry Customer: {message}")
        response = customer_service.process_message(escalation_conversation, message)
        print(f"🤖 Agent: {response[:100]}...")
        print()

    # Analytics and ROI
    print("\n📊 ANALYTICS & ROI SUMMARY")
    print("-" * 40)

    # Customer service analytics
    cs_analytics = customer_service.get_analytics(30)
    print(f"\n🎧 Customer Service (30 days):")
    print(f"   • Total conversations: {cs_analytics.get('total_conversations', 0)}")
    print(f"   • Resolution rate: {cs_analytics.get('resolution_rate', 0)}%")
    print(f"   • Escalation rate: {cs_analytics.get('escalation_rate', 0)}%")
    print(f"   • Estimated savings: ${cs_analytics.get('estimated_savings', {}).get('cost_savings_usd', 0):,.2f}")

    # Lead qualifier analytics
    lq_analytics = lead_qualifier.get_analytics(30)
    print(f"\n🎯 Lead Qualifier (30 days):")
    print(f"   • Total leads: {lq_analytics.get('total_leads', 0)}")
    print(f"   • Qualification rate: {lq_analytics.get('qualification_rate', 0)}%")
    print(f"   • Time savings: {lq_analytics.get('time_savings', {}).get('hours_saved', 0)} hours")
    print(f"   • Cost savings: ${lq_analytics.get('time_savings', {}).get('cost_savings_usd', 0):,.2f}")

    # Combined ROI
    total_savings = (
        cs_analytics.get('estimated_savings', {}).get('cost_savings_usd', 0) +
        lq_analytics.get('time_savings', {}).get('cost_savings_usd', 0)
    )

    print(f"\n💰 TOTAL MONTHLY ROI: ${total_savings:,.2f}")
    print(f"   • Implementation cost: ~$500/month")
    print(f"   • Net savings: ${total_savings - 500:,.2f}/month")
    print(f"   • ROI: {((total_savings - 500) / 500 * 100):,.0f}%")

    print("\n✅ Demo completed successfully!")


def quick_demo():
    """Quick demo for testing"""
    print("⚡ QUICK DEMO")
    print("=" * 30)

    # Customer Service Quick Test
    print("\n🎧 Customer Service Agent:")
    demo_customer_service()

    print("\n" + "="*50 + "\n")

    # Lead Qualifier Quick Test
    print("🎯 Lead Qualifier Agent:")
    demo_lead_qualifier()


async def integration_demo():
    """Demonstrate CRM integrations"""
    print("\n🔗 CRM INTEGRATION DEMO")
    print("-" * 30)

    # Mock CRM configuration
    crm_config = {
        "supabase": {
            "url": "https://your-project.supabase.co",
            "key": "your-anon-key",
            "table": "leads"
        }
        # Add other CRM configs as needed
    }

    # This would work with real credentials
    print("📝 CRM integrations configured:")
    for crm_name, config in crm_config.items():
        print(f"   • {crm_name.title()}: {'✅ Configured' if config.get('key') else '❌ Missing credentials'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Business Agents Demo")
    parser.add_argument("--mode", choices=["quick", "full", "integration"],
                       default="quick", help="Demo mode to run")

    args = parser.parse_args()

    if args.mode == "quick":
        quick_demo()
    elif args.mode == "integration":
        asyncio.run(integration_demo())
    else:
        asyncio.run(comprehensive_demo())