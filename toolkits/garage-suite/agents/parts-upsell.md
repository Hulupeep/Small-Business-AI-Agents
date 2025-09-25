# 🔧 Parts & Upsell Manager Agent

*The AI that optimizes inventory, maximizes revenue, and builds customer loyalty*

## Overview

The Parts & Upsell Manager Agent handles inventory optimization, intelligent upselling, and revenue maximization while maintaining customer trust. It identifies cross-sell opportunities, manages parts procurement, and implements loyalty programs that benefit both customers and the garage.

## Core Capabilities

### 1. **Intelligent Inventory Management**
```python
class IntelligentInventoryManager:
    def __init__(self):
        self.usage_analyzer = UsageAnalyzer()
        self.demand_predictor = DemandPredictor()
        self.supplier_manager = SupplierManager()
        self.cost_optimizer = CostOptimizer()

    async def optimize_inventory_levels(self):
        """Continuously optimize inventory based on usage patterns"""

        # Analyze historical usage
        usage_patterns = await self.usage_analyzer.analyze_parts_usage(
            time_period="6_months",
            seasonal_adjustment=True
        )

        # Predict future demand
        demand_forecast = await self.demand_predictor.forecast_demand(
            historical_data=usage_patterns,
            seasonal_factors=self.get_seasonal_factors(),
            local_market_trends=self.get_market_trends()
        )

        # Calculate optimal stock levels
        optimal_levels = {}
        for part_id, forecast in demand_forecast.items():
            part_info = await self.get_part_info(part_id)

            optimal_level = self.calculate_optimal_stock_level(
                demand_forecast=forecast,
                lead_time=part_info.supplier_lead_time,
                holding_cost=part_info.holding_cost,
                stockout_cost=part_info.stockout_cost
            )

            optimal_levels[part_id] = optimal_level

        # Generate reorder recommendations
        reorder_recommendations = await self.generate_reorder_list(optimal_levels)

        return reorder_recommendations

    def calculate_optimal_stock_level(self, demand_forecast, lead_time, holding_cost, stockout_cost):
        """Calculate optimal stock level using economic order quantity model"""

        annual_demand = demand_forecast.annual_units
        order_cost = 25  # Fixed cost per order
        holding_cost_per_unit = holding_cost.annual_percentage * demand_forecast.unit_cost

        # Economic Order Quantity
        eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost_per_unit)

        # Safety stock for demand variability
        safety_stock = demand_forecast.standard_deviation * math.sqrt(lead_time)

        # Reorder point
        reorder_point = (demand_forecast.daily_average * lead_time) + safety_stock

        return {
            "optimal_order_quantity": eoq,
            "reorder_point": reorder_point,
            "safety_stock": safety_stock,
            "max_stock_level": reorder_point + eoq
        }

INVENTORY_CATEGORIES = {
    "fast_moving": {
        "oil_filters": {"reorder_threshold": 10, "max_stock": 50},
        "oil_5w30": {"reorder_threshold": 20, "max_stock": 100},
        "brake_pads_common": {"reorder_threshold": 8, "max_stock": 40},
        "spark_plugs": {"reorder_threshold": 20, "max_stock": 80}
    },
    "medium_moving": {
        "air_filters": {"reorder_threshold": 15, "max_stock": 60},
        "belts_common": {"reorder_threshold": 5, "max_stock": 25},
        "batteries": {"reorder_threshold": 3, "max_stock": 15}
    },
    "slow_moving": {
        "timing_belts": {"reorder_threshold": 2, "max_stock": 8},
        "water_pumps": {"reorder_threshold": 2, "max_stock": 10},
        "alternators": {"reorder_threshold": 1, "max_stock": 5}
    }
}
```

### 2. **Smart Upselling Engine**
```python
class SmartUpsellingEngine:
    def __init__(self):
        self.service_correlator = ServiceCorrelator()
        self.customer_analyzer = CustomerAnalyzer()
        self.timing_optimizer = TimingOptimizer()

    async def generate_upsell_opportunities(self, current_service, vehicle, customer):
        """Generate relevant upsell opportunities during service"""

        opportunities = []

        # Check maintenance schedule correlations
        schedule_based = await self.find_schedule_based_opportunities(
            current_service=current_service,
            vehicle=vehicle,
            customer_history=customer.service_history
        )

        # Check parts condition correlations
        condition_based = await self.find_condition_based_opportunities(
            current_service=current_service,
            vehicle=vehicle
        )

        # Check seasonal opportunities
        seasonal_based = await self.find_seasonal_opportunities(
            vehicle=vehicle,
            location=customer.location,
            current_month=datetime.now().month
        )

        all_opportunities = schedule_based + condition_based + seasonal_based

        # Filter and prioritize opportunities
        filtered_opportunities = await self.filter_and_prioritize_opportunities(
            opportunities=all_opportunities,
            customer_profile=customer,
            current_service_value=current_service.total_cost
        )

        return filtered_opportunities

    async def find_schedule_based_opportunities(self, current_service, vehicle, customer_history):
        """Find opportunities based on maintenance schedule"""

        opportunities = []

        # Check what's due soon
        upcoming_services = await self.get_upcoming_services(vehicle, customer_history)

        for service in upcoming_services:
            if service.due_within_months <= 2:  # Due within 2 months
                # Calculate savings if done together
                standalone_cost = service.standalone_cost
                combined_cost = service.get_combined_cost(current_service)
                savings = standalone_cost - combined_cost

                if savings >= 20:  # Minimum €20 savings
                    opportunities.append({
                        "type": "schedule_based",
                        "service": service.name,
                        "reason": f"Due in {service.due_within_months} months",
                        "savings": savings,
                        "urgency": "medium" if service.due_within_months <= 1 else "low",
                        "customer_benefit": f"Save €{savings} by combining services",
                        "additional_cost": combined_cost - current_service.total_cost
                    })

        return opportunities

UPSELL_RULES = {
    "oil_change": {
        "natural_additions": [
            {
                "service": "air_filter_replacement",
                "condition": "filter_dirty_percentage > 60",
                "savings": 15,
                "pitch": "Your air filter is 60% dirty - replace now and save €15 vs separate visit"
            },
            {
                "service": "cabin_filter_replacement",
                "condition": "months_since_replacement > 12",
                "savings": 20,
                "pitch": "Cabin filter due - better air quality and save €20 doing it together"
            }
        ]
    },
    "brake_service": {
        "natural_additions": [
            {
                "service": "brake_fluid_flush",
                "condition": "fluid_age_months > 24",
                "savings": 25,
                "pitch": "Brake fluid is 2+ years old - flush now while brakes are apart (save €25)"
            },
            {
                "service": "tire_rotation",
                "condition": "mileage_since_rotation > 10000",
                "savings": 10,
                "pitch": "Wheels already off - rotate tires for even wear (save €10)"
            }
        ]
    }
}
```

### 3. **Customer Loyalty Program Engine**
```python
class LoyaltyProgramEngine:
    def __init__(self):
        self.points_calculator = PointsCalculator()
        self.rewards_manager = RewardsManager()
        self.tier_manager = TierManager()

    async def calculate_loyalty_benefits(self, customer, current_service):
        """Calculate loyalty points and available rewards"""

        # Calculate points for current service
        base_points = self.points_calculator.calculate_base_points(current_service.total_cost)
        bonus_points = self.points_calculator.calculate_bonus_points(
            customer=customer,
            service_type=current_service.type,
            special_promotions=self.get_active_promotions()
        )

        total_points = base_points + bonus_points

        # Check tier progression
        new_tier = self.tier_manager.calculate_tier_after_service(
            current_tier=customer.loyalty_tier,
            current_points=customer.loyalty_points,
            points_to_add=total_points,
            annual_spending=customer.annual_spending + current_service.total_cost
        )

        # Check available rewards
        available_rewards = self.rewards_manager.get_available_rewards(
            customer_points=customer.loyalty_points + total_points,
            customer_tier=new_tier
        )

        return {
            "points_earned": total_points,
            "points_breakdown": {
                "base_points": base_points,
                "bonus_points": bonus_points,
                "bonus_reasons": self.points_calculator.bonus_reasons
            },
            "new_total_points": customer.loyalty_points + total_points,
            "tier_progression": {
                "current_tier": customer.loyalty_tier,
                "new_tier": new_tier,
                "tier_upgraded": new_tier != customer.loyalty_tier
            },
            "available_rewards": available_rewards,
            "next_reward_progress": self.calculate_next_reward_progress(customer.loyalty_points + total_points)
        }

LOYALTY_PROGRAM = {
    "points_earning": {
        "base_rate": 1,  # 1 point per euro spent
        "oil_change_bonus": 0.5,  # 1.5 points per euro for oil changes
        "major_repair_bonus": 0.25,  # 1.25 points per euro for repairs >€500
        "referral_bonus": 100,  # 100 points for successful referral
        "review_bonus": 25   # 25 points for online review
    },
    "tiers": {
        "bronze": {
            "requirements": {"annual_spending": 0, "points": 0},
            "benefits": ["birthday_discount_10%", "priority_booking"]
        },
        "silver": {
            "requirements": {"annual_spending": 500, "points": 750},
            "benefits": ["loyalty_discount_5%", "free_car_wash", "extended_warranty"]
        },
        "gold": {
            "requirements": {"annual_spending": 1200, "points": 1800},
            "benefits": ["loyalty_discount_10%", "free_courtesy_car", "premium_service"]
        },
        "platinum": {
            "requirements": {"annual_spending": 2500, "points": 3500},
            "benefits": ["loyalty_discount_15%", "concierge_service", "exclusive_events"]
        }
    },
    "rewards_catalog": {
        "free_oil_change": {"cost": 200, "value": 65},
        "20_euro_credit": {"cost": 150, "value": 20},
        "free_car_wash": {"cost": 100, "value": 25},
        "premium_detail": {"cost": 500, "value": 150},
        "tire_rotation": {"cost": 80, "value": 35}
    }
}
```

## Implementation Code

### Main Parts & Upsell Manager
```python
class PartsUpsellAgent:
    def __init__(self):
        self.inventory_manager = IntelligentInventoryManager()
        self.upsell_engine = SmartUpsellingEngine()
        self.loyalty_engine = LoyaltyProgramEngine()
        self.pricing_optimizer = PricingOptimizer()

    async def process_service_opportunity(self, work_order):
        """Process a service for upsell opportunities and inventory impact"""

        # Check parts availability
        parts_status = await self.check_parts_availability(work_order.required_parts)

        # Generate upsell opportunities
        upsell_opportunities = await self.upsell_engine.generate_upsell_opportunities(
            current_service=work_order.planned_service,
            vehicle=work_order.vehicle,
            customer=work_order.customer
        )

        # Calculate loyalty benefits
        loyalty_benefits = await self.loyalty_engine.calculate_loyalty_benefits(
            customer=work_order.customer,
            current_service=work_order.planned_service
        )

        # Create comprehensive recommendation
        recommendation = ServiceRecommendation(
            work_order=work_order,
            parts_availability=parts_status,
            upsell_opportunities=upsell_opportunities,
            loyalty_benefits=loyalty_benefits,
            total_value_proposition=self.calculate_total_value(
                base_service=work_order.planned_service,
                upsells=upsell_opportunities,
                loyalty_benefits=loyalty_benefits
            )
        )

        return recommendation

    async def handle_parts_shortage(self, part_id, required_quantity):
        """Handle parts shortage situations"""

        part_info = await self.inventory_manager.get_part_info(part_id)

        # Check alternative sources
        alternative_sources = await self.find_alternative_sources(
            part_id=part_id,
            required_quantity=required_quantity,
            max_delivery_time="same_day"
        )

        if alternative_sources:
            # Found alternatives
            best_option = self.select_best_alternative(
                alternatives=alternative_sources,
                criteria=["delivery_time", "cost", "quality"]
            )

            return {
                "status": "alternative_found",
                "solution": best_option,
                "additional_cost": best_option.price_difference,
                "delay": best_option.delivery_time
            }

        else:
            # No immediate alternatives - check substitutes
            substitutes = await self.find_substitute_parts(
                original_part=part_info,
                compatibility_requirements=part_info.compatibility
            )

            if substitutes:
                return {
                    "status": "substitute_available",
                    "options": substitutes,
                    "customer_approval_required": True
                }

            else:
                # Must order and wait
                rush_order = await self.place_rush_order(
                    part_id=part_id,
                    quantity=required_quantity
                )

                return {
                    "status": "rush_order_placed",
                    "delivery_estimate": rush_order.estimated_delivery,
                    "additional_cost": rush_order.rush_fee,
                    "customer_notification_required": True
                }
```

## Sample Upselling Scenarios

### **Scenario 1: Oil Change with Smart Upsells**
```
Customer brings 2019 Honda Civic for oil change.

SYSTEM ANALYSIS:
✓ Air filter: 75% dirty (due for replacement)
✓ Cabin filter: 14 months old (recommend replacement)
✓ Tire rotation: 12,000km since last rotation
✓ Battery: 3.5 years old (test recommended)

UPSELL PRESENTATION:
"Hi Sarah! While we're changing your oil, I noticed a couple of things:

🔧 RECOMMENDED ADDITIONS:
• Air filter (75% dirty): +€25 (save €15 vs separate visit)
• Cabin filter (pollen season): +€20 (save €10 vs separate visit)
• Tire rotation (extend tire life): +€15 (save €10 - wheels already off)

💰 PACKAGE DEAL:
Oil change + all three services: €95 (save €35 total!)

⚡ LOYALTY BENEFITS:
Current service: 95 points
Tier: Silver (5% discount automatically applied)
Next reward: Free car wash (need 15 more points)

Total time: 45 minutes instead of 3 separate visits
Would you like to do everything today?"

CUSTOMER DECISION POINTS:
□ Oil change only: €45
□ Oil + air filter: €65 (save €15)
□ Complete package: €95 (save €35)
```

### **Scenario 2: Brake Service with Strategic Upsells**
```
Customer approved brake pad replacement for €285.

SYSTEM ANALYSIS:
✓ Brake fluid: 30 months old (due for flush)
✓ Rotors: Minor scoring (resurface recommended)
✓ Tires: Uneven wear pattern (alignment check due)

UPSELL PRESENTATION:
"John, while we're working on your brakes, we found:

🔧 BRAKE SYSTEM OPTIMIZATION:
• Brake fluid flush (2.5 years old): +€45
  Benefits: Better pedal feel, prevent corrosion
  Saves: €25 (brake lines already open)

• Rotor resurfacing (minor scoring): +€65
  Benefits: Smoother braking, longer pad life
  Saves: €35 (rotors already removed)

⚠️ RELATED ISSUE DETECTED:
• Front alignment check (uneven tire wear): +€85
  Risk: New brake work won't help if alignment is off
  Saves: Prevents premature tire replacement (€400+)

🎯 COMPLETE BRAKE RESTORATION:
All services: €480 (save €60)
Instead of: €540 done separately

💡 FINANCING AVAILABLE:
□ Pay full amount today
□ 50% now, 50% in 30 days
□ Add to monthly service plan: €45/month

Would you like the complete brake restoration?"
```

### **Scenario 3: Family Fleet Management**
```
Smith family has 3 vehicles all due for winter preparation.

SYSTEM ANALYSIS:
Vehicle 1 (2018 Toyota Camry): Winter tires, battery test
Vehicle 2 (2020 Ford Explorer): All-season check, antifreeze
Vehicle 3 (2016 Honda Civic): Winter tires, heating system

FAMILY PACKAGE PRESENTATION:
"Hi Mike! Perfect timing - all three vehicles need winter prep:

🚗 SMITH FAMILY WINTER PACKAGE:

Toyota Camry:
• Winter tire changeover: €85
• Battery load test: €25

Ford Explorer:
• All-season tire inspection: €35
• Antifreeze level check: €25

Honda Civic:
• Winter tire changeover: €85
• Heating system check: €45

INDIVIDUAL PRICING: €300 total

🎉 FAMILY DISCOUNT: €225 (save €75!)

⏰ CONVENIENCE OPTION:
Saturday appointment: All 3 cars, 3 hours
You wait in comfort - coffee, WiFi, kids' area

💳 LOYALTY SUPER BONUS:
Family package = 400 loyalty points
Sarah reaches Gold tier = 10% discount on future services

🗓️ AVAILABLE DATES:
• Saturday, Oct 12th - 9:00 AM (recommended)
• Saturday, Oct 19th - 8:00 AM
• Weekday option available with 20% additional discount

Ready to book the family winter package?"
```

## Advanced Features

### **Dynamic Pricing Optimization**
```python
class DynamicPricingOptimizer:
    def __init__(self):
        self.market_analyzer = MarketAnalyzer()
        self.demand_tracker = DemandTracker()
        self.competitor_monitor = CompetitorMonitor()

    async def optimize_service_pricing(self, service_type, customer_profile, timing):
        """Optimize pricing based on multiple factors"""

        base_price = self.get_base_price(service_type)

        # Market demand adjustment
        demand_level = await self.demand_tracker.get_current_demand(service_type)
        demand_multiplier = self.calculate_demand_multiplier(demand_level)

        # Customer loyalty adjustment
        loyalty_discount = self.calculate_loyalty_discount(customer_profile)

        # Timing adjustment (off-peak discounts)
        timing_adjustment = self.calculate_timing_adjustment(timing)

        # Competitor price check
        competitive_position = await self.competitor_monitor.check_competitive_position(
            service_type,
            base_price
        )

        final_price = base_price * demand_multiplier * (1 - loyalty_discount) * timing_adjustment

        return {
            "base_price": base_price,
            "final_price": final_price,
            "adjustments": {
                "demand": demand_multiplier,
                "loyalty": loyalty_discount,
                "timing": timing_adjustment,
                "competitive_position": competitive_position
            }
        }
```

### **Predictive Maintenance Recommendations**
```python
class PredictiveMaintenanceEngine:
    def __init__(self):
        self.failure_predictor = FailurePredictor()
        self.cost_benefit_analyzer = CostBenefitAnalyzer()

    async def predict_future_needs(self, vehicle, service_history):
        """Predict future maintenance needs and optimal timing"""

        predictions = []

        # Analyze wear patterns
        wear_analysis = await self.failure_predictor.analyze_component_wear(
            vehicle=vehicle,
            service_history=service_history,
            current_mileage=vehicle.odometer_reading
        )

        for component, wear_data in wear_analysis.items():
            if wear_data.failure_probability > 0.3:  # >30% chance of failure
                optimal_timing = self.calculate_optimal_replacement_timing(
                    component=component,
                    wear_data=wear_data,
                    cost_data=self.get_component_costs(component)
                )

                predictions.append({
                    "component": component,
                    "failure_probability": wear_data.failure_probability,
                    "estimated_failure_date": wear_data.estimated_failure_date,
                    "optimal_replacement_date": optimal_timing.replacement_date,
                    "cost_if_proactive": optimal_timing.proactive_cost,
                    "cost_if_reactive": optimal_timing.reactive_cost,
                    "savings": optimal_timing.reactive_cost - optimal_timing.proactive_cost
                })

        return sorted(predictions, key=lambda x: x["savings"], reverse=True)
```

## Configuration Options

### **Inventory Management Settings**
```yaml
inventory_settings:
  reorder_automation: true
  safety_stock_percentage: 15
  lead_time_buffer_days: 2
  seasonal_adjustment: true

  fast_moving_threshold: 10  # units per month
  slow_moving_threshold: 2   # units per month

supplier_settings:
  primary_suppliers:
    - name: "Euro Car Parts"
      delivery_days: 1
      minimum_order: 100
      discount_tier: "gold"

    - name: "GSF"
      delivery_days: 1
      minimum_order: 50
      discount_tier: "silver"

  backup_suppliers:
    - name: "Motorstore"
      delivery_days: 2
      emergency_service: true
```

### **Upselling Configuration**
```yaml
upselling_settings:
  max_upsells_per_service: 3
  minimum_savings_threshold: 20  # euros
  customer_approval_required_over: 100  # euros

  upsell_timing:
    present_during: "quote_stage"
    follow_up_after: "service_completion"
    educational_content: true

loyalty_program:
  points_per_euro: 1
  tier_review_frequency: "quarterly"
  reward_expiry_months: 12

  special_promotions:
    referral_bonus: 100
    review_bonus: 25
    birthday_multiplier: 2
```

## Performance Metrics

### **Inventory Efficiency**
- **Stock-out Rate**: Target <2% (critical parts <0.5%)
- **Inventory Turnover**: Target 8-12 times per year
- **Dead Stock Percentage**: Target <5% of total inventory value
- **Emergency Order Rate**: Target <10% of total orders

### **Upselling Performance**
- **Upsell Acceptance Rate**: Target >35% overall
- **Average Upsell Value**: Target €85 per successful upsell
- **Customer Satisfaction with Upsells**: Target >4.3/5
- **Repeat Customer Upsell Rate**: Target >45%

### **Revenue Impact**
- **Parts Revenue Growth**: Target 15% annual increase
- **Average Invoice Value**: Target 25% increase through upselling
- **Customer Lifetime Value**: Target 20% increase through loyalty program
- **Profit Margin Improvement**: Target 8% increase through optimization

### **Loyalty Program Metrics**
- **Program Participation Rate**: Target >70% of customers
- **Tier Progression Rate**: Target 25% advance tier annually
- **Reward Redemption Rate**: Target >60% of earned rewards used
- **Customer Retention (Loyalty Members)**: Target >92%

## Integration Requirements

### **Parts Supplier Integration**
```python
# Integration with parts suppliers' APIs
class SupplierIntegration:
    def __init__(self):
        self.euro_car_parts = EuroCarPartsAPI()
        self.gsf_api = GSFAPI()
        self.motor_store = MotorStoreAPI()

    async def check_parts_availability(self, parts_list):
        """Check availability across all suppliers"""

        availability_results = {}

        for part in parts_list:
            suppliers_checked = []

            # Check primary suppliers first
            for supplier in self.primary_suppliers:
                availability = await supplier.check_availability(
                    part_number=part.part_number,
                    quantity=part.required_quantity
                )

                suppliers_checked.append({
                    "supplier": supplier.name,
                    "available": availability.in_stock,
                    "quantity": availability.available_quantity,
                    "price": availability.unit_price,
                    "delivery_time": availability.delivery_time
                })

                if availability.in_stock and availability.available_quantity >= part.required_quantity:
                    break  # Found sufficient stock

            availability_results[part.part_number] = suppliers_checked

        return availability_results
```

### **Garage Management System Integration**
```python
# Integration with garage management for real-time updates
class GMSPartsIntegration:
    def __init__(self, gms_type):
        self.gms = self.initialize_gms_connector(gms_type)

    async def sync_parts_usage(self, work_order_id, parts_used):
        """Update parts inventory in garage management system"""

        for part in parts_used:
            await self.gms.inventory.update_stock(
                part_number=part.part_number,
                quantity_used=part.quantity_used,
                work_order_id=work_order_id,
                timestamp=datetime.now()
            )

    async def trigger_reorder_alert(self, part_number, current_stock, reorder_level):
        """Trigger reorder alert in garage management system"""

        await self.gms.alerts.create({
            "type": "reorder_alert",
            "part_number": part_number,
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "priority": "medium" if current_stock > 0 else "high"
        })
```

## Next Steps

1. **[Set Up Inventory Tracking](../config/inventory-setup.md)**
2. **[Configure Supplier Integrations](../config/supplier-apis.md)**
3. **[Implement Loyalty Program](../templates/loyalty-program.md)**
4. **[Test Upselling Workflows](../examples/upsell-testing.md)**

---

*This agent typically increases average invoice value by 25% and improves customer retention by 30% through intelligent upselling and loyalty rewards.*