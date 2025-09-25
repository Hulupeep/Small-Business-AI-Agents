"""
Real Estate AI Toolkit - Realistic Usage Examples
Demonstrates practical use cases and expected results for small real estate businesses.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List

# Import toolkit components
try:
    from agents.lead_qualifier import SimpleLeadQualifier, LeadProfile, LeadSource, TimelineUrgency
    from agents.cma_intelligence import SimpleCMAAgent, SimplePropertyData, PropertyType, PropertyStatus
    from compliance.fair_housing import BasicFairHousingChecker
except ImportError:
    print("Import Error: Make sure you're running from the real-estate-suite directory")
    print("Run: cd toolkits/real-estate-suite && python examples/usage-example.py")
    exit(1)

class RealEstateToolkitDemo:
    """Practical demonstration of the Real Estate AI Toolkit."""

    def __init__(self):
        # Initialize components (will work with or without API keys)
        self.lead_qualifier = SimpleLeadQualifier()
        self.cma_agent = SimpleCMAAgent()
        self.compliance_checker = BasicFairHousingChecker()

    async def demo_lead_qualification(self):
        """Demonstrate practical lead qualification scenarios."""

        print("🔍 LEAD QUALIFICATION DEMONSTRATION")
        print("=" * 60)
        print("This shows how the AI helps prioritize and score leads systematically.\n")

        # Realistic lead scenarios
        leads = [
            # High-quality lead
            LeadProfile(
                first_name="Jennifer",
                last_name="Chen",
                email="j.chen@email.com",
                phone="(512) 555-0123",
                source=LeadSource.REFERRAL,
                initial_inquiry="Hi, my friend Sarah recommended you. We're pre-approved for $450k and need to buy within 30 days due to job relocation. Looking for 3BR in Cedar Park or Round Rock area.",
                budget_min=400000,
                budget_max=450000,
                property_type="single_family",
                bedrooms_min=3,
                bathrooms_min=2,
                preferred_areas=["Cedar Park", "Round Rock"],
                timeline=TimelineUrgency.IMMEDIATE,
                motivation_level=9,
                pre_approved=True,
                current_situation="Job relocation, pre-approved, urgent timeline"
            ),

            # Average lead
            LeadProfile(
                first_name="Michael",
                last_name="Rodriguez",
                email="mrodriguez@gmail.com",
                phone="(512) 555-0456",
                source=LeadSource.WEBSITE,
                initial_inquiry="Looking to buy my first home. Budget around $300k. Want something in good condition.",
                budget_min=275000,
                budget_max=325000,
                property_type="single_family",
                bedrooms_min=2,
                bathrooms_min=2,
                preferred_areas=["Austin", "East Austin"],
                timeline=TimelineUrgency.SHORT_TERM,
                motivation_level=6,
                pre_approved=False,
                current_situation="First-time buyer, researching process"
            ),

            # Lower priority lead
            LeadProfile(
                first_name="Lisa",
                last_name="Johnson",
                email="lisa.j@email.com",
                source=LeadSource.ZILLOW,
                initial_inquiry="Just browsing properties online. Might be interested in buying next year.",
                timeline=TimelineUrgency.LONG_TERM,
                motivation_level=3,
                pre_approved=False,
                current_situation="Early research phase"
            )
        ]

        for i, lead in enumerate(leads, 1):
            print(f"LEAD {i}: {lead.first_name} {lead.last_name}")
            print("-" * 40)

            try:
                # Qualify the lead
                result = await self.lead_qualifier.qualify_lead(lead)

                print(f"📊 Score: {result['lead_score']}/100")
                print(f"🎯 Priority: {result['priority'].upper()}")
                print(f"📞 Contact Info: {lead.email}" + (f", {lead.phone}" if lead.phone else ""))
                print(f"💰 Budget: {f'${lead.budget_min:,} - ${lead.budget_max:,}' if lead.budget_min else 'Not specified'}")
                print(f"⏰ Timeline: {lead.timeline.value.replace('_', ' ').title()}")

                print(f"\n📋 Next Steps:")
                for j, step in enumerate(result['next_steps'][:3], 1):
                    print(f"  {j}. {step}")

                print(f"\n🔄 Follow-up: {result['recommended_followup']}")

                # Show AI analysis if available
                if "AI analysis unavailable" not in result['ai_analysis']:
                    print(f"\n🤖 AI Insights:")
                    analysis_preview = result['ai_analysis'][:150] + "..." if len(result['ai_analysis']) > 150 else result['ai_analysis']
                    print(f"   {analysis_preview}")

                print(f"\n💡 Business Value:")
                summary = result['qualification_summary']
                print(f"   Conversion likelihood: {summary['conversion_likelihood']}")
                print(f"   Expected timeline: {summary['estimated_timeline']}")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

            print("\n" + "=" * 60)

    async def demo_cma_analysis(self):
        """Demonstrate CMA generation for different property types."""

        print("🏠 CMA ANALYSIS DEMONSTRATION")
        print("=" * 60)
        print("This shows how the toolkit generates market analysis and pricing recommendations.\n")

        # Sample properties for CMA
        properties = [
            # Starter home
            SimplePropertyData(
                address="123 Oak Street",
                city="Austin",
                state="TX",
                zip_code="78745",
                property_type=PropertyType.SINGLE_FAMILY,
                bedrooms=3,
                bathrooms=2,
                square_footage=1650,
                lot_size=0.25,
                year_built=2010,
                garage_spaces=2,
                list_price=425000,
                features=["updated_kitchen", "hardwood_floors"]
            ),

            # Move-up home
            SimplePropertyData(
                address="456 Maple Drive",
                city="Cedar Park",
                state="TX",
                zip_code="78613",
                property_type=PropertyType.SINGLE_FAMILY,
                bedrooms=4,
                bathrooms=3,
                square_footage=2800,
                lot_size=0.5,
                year_built=2018,
                garage_spaces=3,
                list_price=675000,
                features=["granite_counters", "master_suite", "covered_patio"]
            )
        ]

        for i, property_data in enumerate(properties, 1):
            print(f"PROPERTY {i}: {property_data.address}")
            print("-" * 40)

            try:
                # Generate CMA
                cma_result = await self.cma_agent.generate_cma(property_data, months_back=6)

                print(f"🏡 Details: {property_data.bedrooms}BR/{property_data.bathrooms}BA")
                print(f"📐 Size: {property_data.square_footage:,} sq ft")
                print(f"💰 Listed at: ${property_data.list_price:,}")

                print(f"\n📊 CMA RESULTS:")
                print(f"   Estimated Value: ${cma_result.estimated_value:,}")
                print(f"   Value Range: ${cma_result.value_range_low:,} - ${cma_result.value_range_high:,}")
                print(f"   Comparable Sales: {cma_result.comparable_count}")
                print(f"   Avg Price/SqFt: ${cma_result.price_per_sqft_avg:.0f}")
                print(f"   Market Conditions: {cma_result.market_conditions}")
                print(f"   Confidence: {cma_result.confidence_level}")

                # Show pricing recommendations
                pricing = cma_result.pricing_recommendations
                recommended_strategy = pricing['recommended']
                rec_price = pricing['strategies'][recommended_strategy]['price']
                rec_timeline = pricing['strategies'][recommended_strategy]['timeline']

                print(f"\n💡 PRICING RECOMMENDATION:")
                print(f"   Strategy: {recommended_strategy.title()}")
                print(f"   Recommended Price: ${rec_price:,}")
                print(f"   Expected Timeline: {rec_timeline}")
                print(f"   Reasoning: {pricing['reasoning']}")

                # Show first few next steps
                print(f"\n📋 Next Steps:")
                for j, step in enumerate(cma_result.next_steps[:4], 1):
                    print(f"   {j}. {step}")

                # Show AI analysis preview if available
                if len(cma_result.market_analysis) > 50:
                    analysis_preview = cma_result.market_analysis[:200] + "..." if len(cma_result.market_analysis) > 200 else cma_result.market_analysis
                    print(f"\n🤖 Market Analysis Preview:")
                    print(f"   {analysis_preview}")

                print(f"\n💼 Business Impact:")
                if property_data.list_price != cma_result.estimated_value:
                    price_diff = cma_result.estimated_value - property_data.list_price
                    if price_diff > 0:
                        print(f"   Property may be underpriced by ${price_diff:,}")
                    else:
                        print(f"   Property may be overpriced by ${abs(price_diff):,}")
                else:
                    print(f"   Listed price aligns with market analysis")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

            print("\n" + "=" * 60)

    def demo_compliance_checking(self):
        """Demonstrate Fair Housing compliance checking."""

        print("⚖️ FAIR HOUSING COMPLIANCE DEMONSTRATION")
        print("=" * 60)
        print("This shows how the toolkit helps ensure marketing content is compliant.\n")

        # Sample marketing texts with various issues
        test_cases = [
            {
                "name": "Problematic Listing",
                "text": "Beautiful family home with great schools nearby! Perfect for young professionals with children. Quiet, mature community.",
                "context": "Common violations found in real listings"
            },
            {
                "name": "Better but Still Issues",
                "text": "Luxury condo near church and synagogue. Great for executives and professionals. Adults preferred.",
                "context": "Religious references and preference language"
            },
            {
                "name": "Compliant Example",
                "text": "Spacious 3-bedroom home in established neighborhood. Updated kitchen, hardwood floors. Close to parks, shopping, and transportation. Move-in ready condition.",
                "context": "Properly written compliant description"
            },
            {
                "name": "Rental with Issues",
                "text": "No Section 8, no vouchers accepted. English-speaking tenants only. Background check required.",
                "context": "High-severity violations in rental ads"
            }
        ]

        for i, case in enumerate(test_cases, 1):
            print(f"CASE {i}: {case['name']}")
            print("-" * 40)
            print(f"Context: {case['context']}")
            print(f"Original Text: \"{case['text']}\"")

            try:
                # Check compliance
                result = self.compliance_checker.check_compliance(case['text'])

                if result.is_compliant:
                    print("✅ COMPLIANT")
                    print("   No Fair Housing issues detected")
                else:
                    print(f"❌ COMPLIANCE ISSUES FOUND ({len(result.issues)})")

                    # Show issues by severity
                    high_severity = [issue for issue in result.issues if issue.severity == "high"]
                    medium_severity = [issue for issue in result.issues if issue.severity == "medium"]
                    low_severity = [issue for issue in result.issues if issue.severity == "low"]

                    if high_severity:
                        print("   🚨 HIGH SEVERITY:")
                        for issue in high_severity:
                            print(f"      • '{issue.original_phrase}': {issue.explanation}")

                    if medium_severity:
                        print("   ⚠️  MEDIUM SEVERITY:")
                        for issue in medium_severity:
                            print(f"      • '{issue.original_phrase}': {issue.explanation}")

                    if low_severity:
                        print("   ℹ️  LOW SEVERITY:")
                        for issue in low_severity:
                            print(f"      • '{issue.original_phrase}': {issue.explanation}")

                    print(f"\n📝 Corrected Version:")
                    print(f"   \"{result.corrected_text}\"")

                # Show suggestions
                if len(result.suggestions) > 1:  # More than just the "compliant" message
                    print(f"\n💡 Recommendations:")
                    for suggestion in result.suggestions[:3]:  # Show first 3
                        print(f"   • {suggestion}")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

            print("\n" + "=" * 60)

    def demo_safe_description_generator(self):
        """Demonstrate automatic generation of compliant descriptions."""

        print("📝 SAFE DESCRIPTION GENERATOR DEMONSTRATION")
        print("=" * 60)
        print("This shows how to automatically generate Fair Housing compliant descriptions.\n")

        # Sample properties for description generation
        properties = [
            {
                'address': '789 Pine Street',
                'bedrooms': 4,
                'bathrooms': 3,
                'square_footage': 2400,
                'features': ['updated kitchen', 'hardwood floors', 'family room', 'master suite'],
                'city': 'Round Rock'
            },
            {
                'address': '321 Elm Avenue',
                'bedrooms': 2,
                'bathrooms': 1,
                'square_footage': 1200,
                'features': ['granite counters', 'stainless appliances', 'covered patio'],
                'city': 'Austin'
            }
        ]

        for i, prop in enumerate(properties, 1):
            print(f"PROPERTY {i}: {prop['address']}")
            print("-" * 40)

            try:
                # Generate safe description
                description = self.compliance_checker.generate_safe_description(prop)

                print(f"📋 Property Details:")
                print(f"   {prop['bedrooms']}BR/{prop['bathrooms']}BA - {prop['square_footage']:,} sq ft")
                print(f"   Features: {', '.join(prop['features'])}")
                print(f"   Location: {prop['city']}")

                print(f"\n📝 Generated Compliant Description:")
                print(f'   "{description}"')

                # Verify the generated description is compliant
                compliance_check = self.compliance_checker.check_compliance(description)
                if compliance_check.is_compliant:
                    print("✅ Generated description passes compliance check")
                else:
                    print(f"⚠️  Generated description has {len(compliance_check.issues)} potential issues")

            except Exception as e:
                print(f"❌ Error: {str(e)}")

            print("\n" + "=" * 60)

    def show_roi_calculation(self):
        """Show realistic ROI calculation for a small real estate business."""

        print("💰 REALISTIC ROI CALCULATION")
        print("=" * 60)
        print("Business impact for a small real estate team (3-5 agents).\n")

        # Baseline metrics for a small team
        baseline = {
            'agents': 4,
            'monthly_leads': 200,
            'current_conversion_rate': 0.08,  # 8%
            'avg_commission': 8000,
            'time_per_lead_qualification': 15,  # minutes
            'time_per_cma': 45,  # minutes
            'cmas_per_month': 20,
            'compliance_review_time': 30,  # minutes per listing
            'listings_per_month': 15
        }

        # With toolkit
        with_toolkit = {
            'lead_qualification_time': 3,  # minutes (AI-assisted)
            'improved_conversion_rate': 0.10,  # 10% (better prioritization)
            'cma_time': 10,  # minutes (automated comparable search)
            'compliance_check_time': 5  # minutes (automated checking)
        }

        print("📊 BASELINE (Current State):")
        print(f"   Team Size: {baseline['agents']} agents")
        print(f"   Monthly Leads: {baseline['monthly_leads']}")
        print(f"   Conversion Rate: {baseline['current_conversion_rate']:.1%}")
        print(f"   Monthly Conversions: {int(baseline['monthly_leads'] * baseline['current_conversion_rate'])}")
        print(f"   Monthly Commission: ${int(baseline['monthly_leads'] * baseline['current_conversion_rate'] * baseline['avg_commission']):,}")

        print(f"\n⏱️  Time Spent on Tasks (Monthly):")
        lead_qual_hours = (baseline['monthly_leads'] * baseline['time_per_lead_qualification']) / 60
        cma_hours = (baseline['cmas_per_month'] * baseline['time_per_cma']) / 60
        compliance_hours = (baseline['listings_per_month'] * baseline['compliance_review_time']) / 60
        total_hours = lead_qual_hours + cma_hours + compliance_hours

        print(f"   Lead Qualification: {lead_qual_hours:.1f} hours")
        print(f"   CMA Preparation: {cma_hours:.1f} hours")
        print(f"   Compliance Review: {compliance_hours:.1f} hours")
        print(f"   Total: {total_hours:.1f} hours")

        print(f"\n🚀 WITH TOOLKIT:")
        new_conversions = int(baseline['monthly_leads'] * with_toolkit['improved_conversion_rate'])
        conversion_improvement = new_conversions - int(baseline['monthly_leads'] * baseline['current_conversion_rate'])

        new_lead_qual_hours = (baseline['monthly_leads'] * with_toolkit['lead_qualification_time']) / 60
        new_cma_hours = (baseline['cmas_per_month'] * with_toolkit['cma_time']) / 60
        new_compliance_hours = (baseline['listings_per_month'] * with_toolkit['compliance_check_time']) / 60
        new_total_hours = new_lead_qual_hours + new_cma_hours + new_compliance_hours

        print(f"   Improved Conversion Rate: {with_toolkit['improved_conversion_rate']:.1%}")
        print(f"   Monthly Conversions: {new_conversions} (+{conversion_improvement})")
        print(f"   Additional Monthly Revenue: ${conversion_improvement * baseline['avg_commission']:,}")

        print(f"\n⏱️  New Time Investment:")
        print(f"   Lead Qualification: {new_lead_qual_hours:.1f} hours (-{lead_qual_hours - new_lead_qual_hours:.1f})")
        print(f"   CMA Preparation: {new_cma_hours:.1f} hours (-{cma_hours - new_cma_hours:.1f})")
        print(f"   Compliance Review: {new_compliance_hours:.1f} hours (-{compliance_hours - new_compliance_hours:.1f})")
        print(f"   Total: {new_total_hours:.1f} hours (-{total_hours - new_total_hours:.1f} hours saved)")

        print(f"\n💰 MONTHLY ROI CALCULATION:")
        additional_revenue = conversion_improvement * baseline['avg_commission']
        time_savings_hours = total_hours - new_total_hours
        time_savings_value = time_savings_hours * 50  # $50/hour value
        total_monthly_benefit = additional_revenue + time_savings_value

        monthly_cost = 250  # Realistic monthly cost (API usage + tool cost)

        print(f"   Additional Revenue: ${additional_revenue:,}")
        print(f"   Time Savings Value: ${time_savings_value:,.0f} ({time_savings_hours:.1f} hours × $50)")
        print(f"   Total Monthly Benefit: ${total_monthly_benefit:,.0f}")
        print(f"   Monthly Investment: ${monthly_cost}")
        print(f"   Net Monthly Benefit: ${total_monthly_benefit - monthly_cost:,.0f}")
        print(f"   ROI: {((total_monthly_benefit - monthly_cost) / monthly_cost * 100):.0f}%")
        print(f"   Payback Period: {monthly_cost / (total_monthly_benefit - monthly_cost):.1f} months")

        print(f"\n📈 ANNUAL IMPACT:")
        annual_benefit = (total_monthly_benefit - monthly_cost) * 12
        print(f"   Annual Net Benefit: ${annual_benefit:,.0f}")
        print(f"   3-Year Value: ${annual_benefit * 3:,.0f}")

    async def run_complete_demo(self):
        """Run the complete toolkit demonstration."""

        print("🏡" * 30)
        print("REAL ESTATE AI TOOLKIT - REALISTIC DEMONSTRATION")
        print("🏡" * 30)
        print("\nThis demo shows what the toolkit actually does - practical AI tools")
        print("to help small real estate businesses work more efficiently.\n")
        print("Note: Some features require OpenAI API key for full functionality.")
        print("Set OPENAI_API_KEY environment variable or pass to constructors.")
        print("\n" + "=" * 90)

        # Run demonstrations
        await self.demo_lead_qualification()
        await self.demo_cma_analysis()
        self.demo_compliance_checking()
        self.demo_safe_description_generator()
        self.show_roi_calculation()

        print("\n" + "=" * 90)
        print("DEMONSTRATION COMPLETE")
        print("=" * 90)
        print("\n✅ What This Toolkit Provides:")
        print("   • Systematic lead scoring and prioritization")
        print("   • Automated property valuation with comparable sales analysis")
        print("   • Fair Housing compliance checking for marketing materials")
        print("   • Time savings through AI-assisted routine tasks")
        print("\n❗ What It Doesn't Do:")
        print("   • Replace agent expertise and relationships")
        print("   • Guarantee lead conversion improvements")
        print("   • Provide perfect legal compliance (review still needed)")
        print("   • Work without proper data sources (MLS access helpful)")
        print("\n📞 Getting Started:")
        print("   1. Install requirements: pip install -r requirements.txt")
        print("   2. Set up OpenAI API key for AI features")
        print("   3. Configure database for data storage (optional)")
        print("   4. Start with lead qualification on incoming inquiries")
        print("   5. Use CMA tools for property valuations")
        print("   6. Check compliance before publishing marketing materials")
        print("\n💡 Expected Timeline: 2-4 weeks for full setup and training")
        print("💰 Expected ROI: 200-400% within 6 months for active teams")

if __name__ == "__main__":
    print("Starting Real Estate AI Toolkit Demonstration...")
    print("=" * 60)

    demo = RealEstateToolkitDemo()

    # Run the demonstration
    asyncio.run(demo.run_complete_demo())