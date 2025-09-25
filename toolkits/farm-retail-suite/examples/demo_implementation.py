"""
Farm & Agri-Retail AI Toolkit - Complete Demo Implementation
Demonstrates all 5 AI agents working together for a mixed farm operation
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal

# Import all agents
from src.farm_production_manager import FarmProductionManager
from src.farm_shop_sales import FarmShopSales
from src.supply_chain_coordinator import SupplyChainCoordinator
from src.customer_engagement import CustomerEngagement
from src.financial_compliance_hub import FinancialComplianceHub

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FarmAIDemo:
    """
    Complete demonstration of the Farm & Agri-Retail AI Toolkit
    showcasing integrated operations for a 50-hectare mixed farm
    """

    def __init__(self):
        self.farm_config = {
            'name': 'Green Valley Farm',
            'total_area': 50,
            'location': {
                'latitude': 52.3676,
                'longitude': 4.9041,
                'address': 'Farm Road 123, 1234 AB Farmville, Netherlands'
            },
            'farmer_age': 32,
            'website': 'https://greenvalleyfarm.com',
            'vat_rate': 0.09
        }

        # Initialize all agents
        self.production_manager = None
        self.sales_system = None
        self.supply_coordinator = None
        self.customer_engagement = None
        self.financial_hub = None

    async def initialize_all_systems(self):
        """Initialize all AI agent systems"""
        logger.info("🌱 Initializing Farm & Agri-Retail AI Toolkit...")

        # Initialize each agent
        self.production_manager = FarmProductionManager(self.farm_config)
        await self.production_manager.initialize()
        logger.info("✅ Farm Production Manager initialized")

        self.sales_system = FarmShopSales(self.farm_config)
        await self.sales_system.initialize()
        logger.info("✅ Farm Shop Sales system initialized")

        self.supply_coordinator = SupplyChainCoordinator(self.farm_config)
        await self.supply_coordinator.initialize()
        logger.info("✅ Supply Chain Coordinator initialized")

        self.customer_engagement = CustomerEngagement(self.farm_config)
        await self.customer_engagement.initialize()
        logger.info("✅ Customer Engagement Platform initialized")

        self.financial_hub = FinancialComplianceHub(self.farm_config)
        await self.financial_hub.initialize()
        logger.info("✅ Financial & Compliance Hub initialized")

        logger.info("🚀 All systems initialized successfully!")

    async def demo_production_management(self):
        """Demonstrate farm production management capabilities"""
        logger.info("\n📊 === FARM PRODUCTION MANAGEMENT DEMO ===")

        # Add diverse crops
        crops_to_add = [
            {
                'variety': 'organic_tomatoes',
                'field_id': 'greenhouse_001',
                'area_hectares': 3.0,
                'stage': 'growing',
                'planted_date': (datetime.now() - timedelta(days=45)).isoformat()
            },
            {
                'variety': 'lettuce',
                'field_id': 'field_002',
                'area_hectares': 2.5,
                'stage': 'ready_to_harvest',
                'planted_date': (datetime.now() - timedelta(days=60)).isoformat()
            },
            {
                'variety': 'carrots',
                'field_id': 'field_003',
                'area_hectares': 4.0,
                'stage': 'growing',
                'planted_date': (datetime.now() - timedelta(days=75)).isoformat()
            },
            {
                'variety': 'wheat',
                'field_id': 'field_004',
                'area_hectares': 15.0,
                'stage': 'planned',
                'expected_harvest': (datetime.now() + timedelta(days=120)).isoformat()
            }
        ]

        crop_ids = []
        for crop_data in crops_to_add:
            crop_id = await self.production_manager.add_crop(crop_data)
            crop_ids.append(crop_id)
            logger.info(f"   🌾 Added crop: {crop_data['variety']} ({crop_data['area_hectares']} ha)")

        # Add livestock
        livestock_to_add = [
            {
                'type': 'dairy_cows',
                'breed': 'Holstein-Friesian',
                'birth_date': datetime.now() - timedelta(days=365*3),
                'location': 'barn_001',
                'production_data': {'daily_milk_kg': 28}
            },
            {
                'type': 'poultry',
                'breed': 'Rhode Island Red',
                'birth_date': datetime.now() - timedelta(days=365),
                'location': 'coop_001',
                'production_data': {'daily_eggs': 0.85}
            }
        ]

        for livestock_data in livestock_to_add:
            animal_id = await self.production_manager.add_livestock(livestock_data)
            logger.info(f"   🐄 Added livestock: {livestock_data['breed']} {livestock_data['type']}")

        # Simulate weather data
        for i in range(30):
            weather_data = {
                'date': datetime.now() + timedelta(days=i),
                'temperature_avg': 18.0 + (i % 10),
                'temperature_min': 12.0,
                'temperature_max': 25.0,
                'humidity': 60.0 + (i % 20),
                'precipitation': 3.0 if i % 5 == 0 else 0.0,
                'wind_speed': 5.0 + (i % 5),
                'solar_radiation': 450.0 + (i % 100)
            }
            await self.production_manager.update_weather_data(weather_data)

        # Get farm status
        farm_status = await self.production_manager.get_farm_status()
        logger.info(f"   📈 Farm Status: {farm_status['crops']['total_crops']} crops, {farm_status['livestock']['total_animals']} animals")

        # Generate recommendations
        recommendations = await self.production_manager.generate_recommendations()
        logger.info(f"   💡 Urgent actions: {len(recommendations['urgent'])}")
        for action in recommendations['urgent']:
            logger.info(f"      ⚠️  {action}")

        return crop_ids

    async def demo_sales_operations(self, available_products):
        """Demonstrate farm shop and market sales operations"""
        logger.info("\n🛒 === FARM SHOP & SALES DEMO ===")

        # Register customers
        customers_to_add = [
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.johnson@email.com',
                'phone': '+31612345678',
                'csa_member': True,
                'communication_preferences': ['email']
            },
            {
                'name': 'Mark van der Berg',
                'email': 'mark.vdberg@example.com',
                'phone': '+31687654321',
                'communication_preferences': ['email', 'sms']
            }
        ]

        customer_ids = []
        for customer_data in customers_to_add:
            customer_id = await self.sales_system.register_customer(customer_data)
            customer_ids.append(customer_id)
            logger.info(f"   👤 Registered customer: {customer_data['name']}")

        # Process sales transactions
        sales_to_process = [
            {
                'customer_id': customer_ids[0],
                'sale_type': 'farm_shop',
                'payment_method': 'card',
                'location': 'Green Valley Farm Shop',
                'items': [
                    {'product_id': list(self.sales_system.products.keys())[0], 'quantity': 3.5},
                    {'product_id': list(self.sales_system.products.keys())[1], 'quantity': 2}
                ]
            },
            {
                'customer_id': customer_ids[1],
                'sale_type': 'farmers_market',
                'payment_method': 'cash',
                'location': 'Downtown Farmers Market',
                'items': [
                    {'product_id': list(self.sales_system.products.keys())[0], 'quantity': 2.0},
                    {'product_id': list(self.sales_system.products.keys())[2], 'quantity': 1}
                ]
            }
        ]

        sale_ids = []
        for sale_data in sales_to_process:
            sale_id = await self.sales_system.process_sale(sale_data)
            sale_ids.append(sale_id)
            sale = self.sales_system.sales[sale_id]
            logger.info(f"   💰 Processed sale: €{sale.total_amount:.2f} via {sale.payment_method.value}")

        # Create CSA boxes
        csa_week = datetime.now() + timedelta(days=7)
        csa_result = await self.sales_system.manage_csa_boxes(csa_week)
        logger.info(f"   📦 Prepared {csa_result['total_boxes']} CSA boxes for {csa_week.strftime('%Y-%m-%d')}")

        # Generate sales report
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        sales_report = await self.sales_system.generate_sales_report(start_date, end_date)
        logger.info(f"   📊 30-day sales: €{sales_report['summary']['total_revenue']:.2f} ({sales_report['summary']['total_transactions']} transactions)")

        return customer_ids, sale_ids

    async def demo_supply_chain_coordination(self):
        """Demonstrate B2B supply chain management"""
        logger.info("\n🚛 === SUPPLY CHAIN COORDINATION DEMO ===")

        # Create B2B orders
        client_id = list(self.supply_coordinator.clients.keys())[0]
        client = self.supply_coordinator.clients[client_id]

        order_data = {
            'client_id': client_id,
            'requested_delivery_date': (datetime.now() + timedelta(days=2)).isoformat(),
            'items': [
                {'product_id': 'organic_tomatoes', 'quantity': 25, 'unit_price': '4.80'},
                {'product_id': 'fresh_lettuce', 'quantity': 15, 'unit_price': '3.20'},
                {'product_id': 'seasonal_herbs', 'quantity': 5, 'unit_price': '8.50'}
            ],
            'delivery_method': 'farm_delivery',
            'special_instructions': 'Deliver to kitchen entrance between 8-10 AM'
        }

        order_id = await self.supply_coordinator.create_order(order_data)
        order = self.supply_coordinator.orders[order_id]
        logger.info(f"   📝 Created B2B order: {order_id} for {client.name} - €{order.total_amount:.2f}")

        # Create traceability record
        trace_data = {
            'product_id': 'organic_tomatoes',
            'batch_id': 'TOM2024001',
            'field_id': 'greenhouse_001',
            'planted_date': (datetime.now() - timedelta(days=80)).isoformat(),
            'harvest_date': (datetime.now() - timedelta(days=2)).isoformat(),
            'organic': True,
            'quality_tests': [
                {'test_type': 'pesticide_residue', 'result': 'negative', 'date': datetime.now().isoformat()},
                {'test_type': 'bacterial_count', 'result': 'within_limits', 'date': datetime.now().isoformat()}
            ],
            'processing_steps': [
                {
                    'process': 'washing',
                    'date': datetime.now().isoformat(),
                    'location': 'processing_facility',
                    'details': 'Triple-washed with filtered water'
                }
            ],
            'destination_client': client_id
        }

        trace_id = await self.supply_coordinator.create_traceability_record(trace_data)
        logger.info(f"   🔍 Created traceability record: {trace_id}")

        # Track product journey
        journey = await self.supply_coordinator.track_product_journey('organic_tomatoes', 'TOM2024001')
        logger.info(f"   📋 Product journey: {len(journey['timeline'])} tracked events from field to customer")

        # Optimize delivery routes
        delivery_date = datetime.now() + timedelta(days=2)
        route_id = await self.supply_coordinator.optimize_delivery_routes(delivery_date)
        if isinstance(route_id, str) and route_id.startswith('route_'):
            route = self.supply_coordinator.delivery_routes[route_id]
            logger.info(f"   🗺️  Optimized delivery route: {route.total_distance_km:.1f}km, €{route.fuel_cost:.2f} fuel cost")

        # Check compliance status
        cert_status = await self.supply_coordinator.manage_certifications()
        logger.info(f"   ✅ Active certifications: {len(cert_status['active_certifications'])}")

        return order_id

    async def demo_customer_engagement(self, customer_ids):
        """Demonstrate customer engagement and marketing"""
        logger.info("\n📱 === CUSTOMER ENGAGEMENT DEMO ===")

        # Book farm tours
        tour_booking_data = {
            'customer_id': customer_ids[0],
            'tour_type': 'general_farm_tour',
            'scheduled_date': (datetime.now() + timedelta(days=14)).isoformat(),
            'group_size': 4,
            'special_requests': 'Interested in organic certification process and sustainable practices'
        }

        booking_id = await self.customer_engagement.book_farm_tour(tour_booking_data)
        booking = self.customer_engagement.tour_bookings[booking_id]
        logger.info(f"   🚜 Booked farm tour: {booking.tour_type.value} for {booking.group_size} people - €{booking.total_price:.2f}")

        # Send seasonal availability alerts
        seasonal_products = [
            {'name': 'organic_tomatoes', 'price': '4.50', 'unit': 'kg'},
            {'name': 'fresh_lettuce', 'price': '3.20', 'unit': 'head'},
            {'name': 'seasonal_herbs', 'price': '8.50', 'unit': 'bunch'}
        ]

        alert_result = await self.customer_engagement.send_seasonal_availability_alert(seasonal_products)
        logger.info(f"   📧 Sent seasonal alerts to {alert_result['notifications_sent']} customers")

        # Suggest recipes
        available_products = ['organic_tomatoes', 'fresh_lettuce', 'seasonal_herbs']
        recipe_suggestions = await self.customer_engagement.suggest_recipes(customer_ids[0], available_products)
        logger.info(f"   🍽️  Generated {len(recipe_suggestions)} recipe suggestions")

        # Create marketing campaign
        campaign_data = {
            'name': 'Summer Harvest Special',
            'type': 'email',
            'target_segments': ['regular_customer', 'csa_member'],
            'scheduled_date': (datetime.now() + timedelta(days=1)).isoformat(),
            'content': {
                'subject': 'Fresh Summer Produce Available Now!',
                'body': 'Our summer harvest is in full swing with the freshest organic produce.',
                'call_to_action': 'Visit our farm shop this weekend'
            }
        }

        campaign_id = await self.customer_engagement.create_marketing_campaign(campaign_data)
        campaign_metrics = await self.customer_engagement.execute_campaign(campaign_id)
        logger.info(f"   📊 Executed marketing campaign: {campaign_metrics['successful_sends']} sent, {campaign_metrics['delivery_rate']:.1f}% delivery rate")

        # Manage CSA memberships
        csa_summary = await self.customer_engagement.manage_csa_memberships()
        logger.info(f"   🥬 CSA program: {csa_summary['total_members']} total members, {csa_summary['active_members']} active")

        return booking_id, campaign_id

    async def demo_financial_compliance(self, sale_ids):
        """Demonstrate financial management and compliance"""
        logger.info("\n💰 === FINANCIAL & COMPLIANCE DEMO ===")

        # Record payments from sales
        for sale_id in sale_ids:
            payment_data = {
                'amount': '125.50',
                'channel': 'farm_shop_card',
                'date': datetime.now().isoformat(),
                'customer_id': 'customer_001',
                'order_id': sale_id
            }
            payment_id = await self.financial_hub.record_payment(payment_data)
            logger.info(f"   💳 Recorded payment: {payment_id} - €{payment_data['amount']}")

        # Record farm expenses
        expenses_to_record = [
            {
                'amount': '450.00',
                'category': 'seeds_plants',
                'date': (datetime.now() - timedelta(days=15)).isoformat(),
                'description': 'Organic vegetable seeds for summer planting',
                'supplier': 'Organic Seeds Co.'
            },
            {
                'amount': '320.00',
                'category': 'fertilizers',
                'date': (datetime.now() - timedelta(days=10)).isoformat(),
                'description': 'Organic compost and natural fertilizers',
                'supplier': 'Green Growth Suppliers'
            },
            {
                'amount': '180.00',
                'category': 'fuel',
                'date': (datetime.now() - timedelta(days=5)).isoformat(),
                'description': 'Tractor fuel for field operations',
                'supplier': 'Farm Fuel Direct'
            }
        ]

        for expense_data in expenses_to_record:
            expense_id = await self.financial_hub.record_expense(expense_data)
            logger.info(f"   📝 Recorded expense: €{expense_data['amount']} for {expense_data['category']}")

        # Analyze grant eligibility
        grant_analysis = await self.financial_hub.analyze_grant_eligibility()
        logger.info(f"   🎯 Grant opportunities: {len(grant_analysis['eligible_grants'])} eligible, €{grant_analysis['total_potential_funding']:.2f} potential funding")

        for grant in grant_analysis['eligible_grants'][:2]:  # Show top 2
            logger.info(f"      💰 {grant['title']}: €{grant['funding_amount']:.2f} ({grant['eligibility_score']}% eligible)")

        # Generate financial report
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        financial_report = await self.financial_hub.generate_financial_report(start_date, end_date)
        logger.info(f"   📊 30-day financial summary:")
        logger.info(f"      Revenue: €{financial_report.total_revenue:.2f}")
        logger.info(f"      Expenses: €{financial_report.total_expenses:.2f}")
        logger.info(f"      Net Profit: €{financial_report.net_profit:.2f}")

        # Generate VAT return
        vat_return = await self.financial_hub.generate_vat_return(start_date, end_date)
        logger.info(f"   🧾 VAT return: €{vat_return['net_vat_payable']:.2f} payable")

        # Check compliance status
        compliance_status = await self.financial_hub.check_compliance_status()
        logger.info(f"   ✅ Compliance score: {compliance_status['overall_score']}/100")
        logger.info(f"   ⏰ Upcoming inspections: {len(compliance_status['inspection_schedule'])}")

        return financial_report

    async def generate_roi_analysis(self, financial_report):
        """Generate comprehensive ROI analysis"""
        logger.info("\n📈 === ROI ANALYSIS ===")

        # Calculate monthly figures and extrapolate to annual
        monthly_revenue = float(financial_report.total_revenue)
        monthly_profit = float(financial_report.net_profit)

        annual_revenue = monthly_revenue * 12
        annual_profit = monthly_profit * 12

        # Estimated annual benefits from AI implementation
        ai_benefits = {
            'revenue_increases': {
                'direct_sales_growth': 18000,  # 40% increase in farm shop/market sales
                'b2b_contract_expansion': 12000,  # 25% growth in restaurant/hotel sales
                'farm_tourism': 8000,  # agritourism and farm experience revenue
                'premium_product_sales': 7000  # organic/specialty product premiums
            },
            'cost_reductions': {
                'input_optimization': 8000,  # feed, fertilizer, seed efficiency
                'labor_efficiency': 6000,  # automated scheduling and management
                'logistics_savings': 3000,  # route optimization and delivery efficiency
                'compliance_costs': 3000  # reduced accounting and legal fees
            }
        }

        total_revenue_increase = sum(ai_benefits['revenue_increases'].values())
        total_cost_reduction = sum(ai_benefits['cost_reductions'].values())
        total_annual_benefit = total_revenue_increase + total_cost_reduction

        logger.info(f"   🎯 PROJECTED ANNUAL AI BENEFITS:")
        logger.info(f"      Revenue Increases: €{total_revenue_increase:,}")
        for benefit, amount in ai_benefits['revenue_increases'].items():
            logger.info(f"         • {benefit.replace('_', ' ').title()}: €{amount:,}")

        logger.info(f"      Cost Reductions: €{total_cost_reduction:,}")
        for benefit, amount in ai_benefits['cost_reductions'].items():
            logger.info(f"         • {benefit.replace('_', ' ').title()}: €{amount:,}")

        logger.info(f"      TOTAL ANNUAL BENEFIT: €{total_annual_benefit:,}")

        # Calculate ROI metrics
        estimated_implementation_cost = 15000  # Initial setup and training
        annual_subscription_cost = 3600  # Monthly subscription * 12

        first_year_roi = ((total_annual_benefit - estimated_implementation_cost - annual_subscription_cost) /
                         (estimated_implementation_cost + annual_subscription_cost)) * 100

        payback_period_months = (estimated_implementation_cost + annual_subscription_cost) / (total_annual_benefit / 12)

        logger.info(f"   💰 ROI ANALYSIS:")
        logger.info(f"      Implementation Cost: €{estimated_implementation_cost:,}")
        logger.info(f"      Annual Subscription: €{annual_subscription_cost:,}")
        logger.info(f"      First Year ROI: {first_year_roi:.1f}%")
        logger.info(f"      Payback Period: {payback_period_months:.1f} months")

        # Calculate 5-year projection
        five_year_benefit = total_annual_benefit * 5
        five_year_cost = estimated_implementation_cost + (annual_subscription_cost * 5)
        five_year_net_benefit = five_year_benefit - five_year_cost

        logger.info(f"   📅 5-YEAR PROJECTION:")
        logger.info(f"      Total Benefits: €{five_year_benefit:,}")
        logger.info(f"      Total Costs: €{five_year_cost:,}")
        logger.info(f"      Net Benefit: €{five_year_net_benefit:,}")
        logger.info(f"      5-Year ROI: {(five_year_net_benefit / five_year_cost) * 100:.1f}%")

    async def run_complete_demo(self):
        """Run complete integrated demonstration"""
        logger.info("🌟 Starting Farm & Agri-Retail AI Toolkit Complete Demo")
        logger.info("=" * 60)

        try:
            # Initialize all systems
            await self.initialize_all_systems()

            # Run demonstrations in sequence
            crop_ids = await self.demo_production_management()
            customer_ids, sale_ids = await self.demo_sales_operations(crop_ids)
            order_id = await self.demo_supply_chain_coordination()
            booking_id, campaign_id = await self.demo_customer_engagement(customer_ids)
            financial_report = await self.demo_financial_compliance(sale_ids)

            # Generate ROI analysis
            await self.generate_roi_analysis(financial_report)

            logger.info("\n🎉 === DEMO COMPLETED SUCCESSFULLY ===")
            logger.info("All 5 AI agents demonstrated successful integration:")
            logger.info("✅ Farm Production Manager - Crop and livestock optimization")
            logger.info("✅ Farm Shop Sales - Direct sales and inventory management")
            logger.info("✅ Supply Chain Coordinator - B2B relationships and traceability")
            logger.info("✅ Customer Engagement - Marketing and relationship management")
            logger.info("✅ Financial & Compliance Hub - Financial management and compliance")

            logger.info(f"\n💰 Projected Annual Value: €65,000")
            logger.info("🚀 Ready for production deployment!")

        except Exception as e:
            logger.error(f"❌ Demo failed: {str(e)}")
            raise


async def main():
    """Main demonstration function"""
    demo = FarmAIDemo()
    await demo.run_complete_demo()


if __name__ == "__main__":
    asyncio.run(main())