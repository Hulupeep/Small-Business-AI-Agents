# 🚀 Garage AI Toolkit Setup Guide

*Complete implementation guide for O'Connor's Auto Repair and similar garages*

## Pre-Implementation Checklist

### **Business Requirements Assessment**
- [ ] Current monthly vehicle volume: _____ vehicles
- [ ] Number of mechanics: _____
- [ ] Current phone system: _____ (VoIP/Landline)
- [ ] Existing garage management software: _____ (Mitchell1/DealerSocket/None)
- [ ] Internet speed: _____ Mbps (minimum 25 Mbps recommended)
- [ ] Mobile devices available: _____ tablets/smartphones

### **Customer Data Inventory**
- [ ] Customer database format: _____ (Excel/Access/CRM)
- [ ] Approximate customer count: _____
- [ ] Vehicle history available: _____ (Yes/No)
- [ ] Customer contact preferences known: _____ (Yes/No)

## Phase 1: Foundation Setup (Week 1-2)

### **Day 1-3: System Infrastructure**

#### **1. Server Setup & API Keys**
```bash
# Set up cloud infrastructure
# Option A: AWS Setup
aws configure
aws s3 mb s3://oconnors-auto-ai-data
aws rds create-db-instance --db-instance-identifier garage-ai-db

# Option B: Google Cloud Setup
gcloud config set project oconnors-auto-repair
gcloud sql instances create garage-ai-db --tier=db-f1-micro

# Option C: Local Server Setup (Budget Option)
docker run -d --name garage-ai-db postgres:13
docker run -d --name garage-ai-redis redis:alpine
```

#### **2. Required API Integrations**
```yaml
# config/api-keys.yml
communication:
  twilio:
    account_sid: "YOUR_TWILIO_SID"
    auth_token: "YOUR_TWILIO_TOKEN"
    phone_number: "+353123456789"

  sendgrid:
    api_key: "YOUR_SENDGRID_KEY"
    from_email: "service@oconnorsauto.ie"

payments:
  stripe:
    public_key: "pk_live_..."
    secret_key: "sk_live_..."
    webhook_secret: "whsec_..."

ai_services:
  openai:
    api_key: "sk-..."
    model: "gpt-4"

  anthropic:  # Alternative
    api_key: "sk-ant-..."
    model: "claude-3-sonnet"
```

#### **3. Phone System Integration**
```javascript
// For VoIP systems (3CX, FreePBX, etc.)
const voipIntegration = {
  provider: "3CX",
  api_endpoint: "https://your-3cx.com/api",
  webhook_url: "https://your-ai-system.com/webhooks/incoming-call",
  auto_answer_enabled: true,
  call_recording: true
};

// For traditional landlines with VoIP adapter
const landlineIntegration = {
  adapter: "Grandstream HT801",
  sip_server: "your-voip-provider.com",
  forward_to_ai: true,
  business_hours_only: false
};
```

### **Day 4-7: Data Migration**

#### **Customer Database Import**
```python
# scripts/import_customers.py
import pandas as pd
from sqlalchemy import create_engine

def import_customer_data(excel_file_path):
    """Import existing customer data from Excel/CSV"""

    # Read existing data
    df = pd.read_excel(excel_file_path)

    # Standardize column names
    column_mapping = {
        'Name': 'full_name',
        'Phone': 'phone_number',
        'Email': 'email_address',
        'Address': 'address',
        'Car Make': 'vehicle_make',
        'Car Model': 'vehicle_model',
        'Year': 'vehicle_year',
        'Last Service': 'last_service_date'
    }

    df = df.rename(columns=column_mapping)

    # Clean and validate data
    df['phone_number'] = df['phone_number'].apply(clean_phone_number)
    df['email_address'] = df['email_address'].apply(validate_email)
    df['last_service_date'] = pd.to_datetime(df['last_service_date'])

    # Import to database
    engine = create_engine('postgresql://user:pass@localhost/garage_ai')
    df.to_sql('customers', engine, if_exists='append', index=False)

    return len(df)

# Example usage
customers_imported = import_customer_data('data/existing_customers.xlsx')
print(f"Successfully imported {customers_imported} customers")
```

#### **Service History Import**
```python
# scripts/import_service_history.py
def import_service_history(service_records_file):
    """Import historical service records"""

    df = pd.read_excel(service_records_file)

    # Standardize service data
    service_mapping = {
        'Customer Name': 'customer_name',
        'Vehicle': 'vehicle_info',
        'Service Date': 'service_date',
        'Services Performed': 'services',
        'Parts Used': 'parts',
        'Total Cost': 'total_cost',
        'Mileage': 'vehicle_mileage'
    }

    df = df.rename(columns=service_mapping)

    # Parse service details
    df['services_list'] = df['services'].apply(parse_services)
    df['parts_list'] = df['parts'].apply(parse_parts)

    # Import to database
    engine = create_engine('postgresql://user:pass@localhost/garage_ai')
    df.to_sql('service_history', engine, if_exists='append', index=False)

    return len(df)
```

## Phase 2: Agent Deployment (Week 2-3)

### **Agent 1: Diagnostic Intake (Priority 1)**

#### **Installation**
```bash
# Install diagnostic intake agent
git clone https://github.com/garage-ai/diagnostic-intake
cd diagnostic-intake

# Configure environment
cp config/config.template.yml config/config.yml
# Edit config.yml with your settings

# Install dependencies
pip install -r requirements.txt

# Test phone integration
python test_phone_integration.py

# Deploy
docker build -t diagnostic-intake .
docker run -d --name diagnostic-intake -p 8001:8000 diagnostic-intake
```

#### **Configuration Example**
```yaml
# config/diagnostic-intake.yml
business_info:
  name: "O'Connor's Auto Repair"
  phone: "+353123456789"
  address: "123 Main Street, Dublin"
  hours:
    monday: "08:00-18:00"
    tuesday: "08:00-18:00"
    wednesday: "08:00-18:00"
    thursday: "08:00-18:00"
    friday: "08:00-18:00"
    saturday: "09:00-16:00"
    sunday: "closed"

pricing:
  currency: "EUR"
  diagnostic_fee: 85
  hourly_rate: 65

  typical_services:
    oil_change: {min: 45, max: 85}
    brake_service: {min: 250, max: 450}
    timing_belt: {min: 400, max: 800}

communication:
  response_delay_seconds: 2
  max_call_duration_minutes: 15
  escalate_to_human_keywords: ["speak to mechanic", "talk to Mike", "emergency"]
```

### **Agent 2: Service Reminder (Priority 2)**

#### **Installation & Setup**
```bash
# Install service reminder agent
git clone https://github.com/garage-ai/service-reminder
cd service-reminder

# Configure service intervals
cp config/service-intervals.template.yml config/service-intervals.yml
```

#### **Service Intervals Configuration**
```yaml
# config/service-intervals.yml
service_intervals:
  oil_change:
    synthetic:
      kilometers: 10000
      months: 6
    conventional:
      kilometers: 5000
      months: 4
    diesel:
      kilometers: 7500
      months: 6

  brake_inspection:
    kilometers: 20000
    months: 12

  timing_belt:
    kilometers: 100000
    years: 7

  mot_test:
    months: 24
    reminder_schedule: [60, 30, 14, 7]  # days before expiry

reminder_campaigns:
  oil_change_due:
    template: "oil_change_reminder"
    send_at: [30, 14, 7]  # days before due
    channels: ["sms", "email"]

  winter_preparation:
    trigger_date: "2024-10-01"
    template: "winter_prep_campaign"
    target_services: ["tire_changeover", "battery_test", "antifreeze_check"]
```

### **Agent 3: Quote & Approval (Priority 3)**

#### **Quote Template Setup**
```html
<!-- templates/quote-email.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Repair Quote - O'Connor's Auto Repair</title>
    <style>
        .quote-header { background: #2c5aa0; color: white; padding: 20px; }
        .parts-section { margin: 20px 0; }
        .cost-breakdown { border: 1px solid #ddd; padding: 15px; }
        .approval-buttons { text-align: center; margin: 30px 0; }
        .approve-btn { background: #28a745; color: white; padding: 15px 30px; text-decoration: none; }
        .decline-btn { background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="quote-header">
        <h2>Repair Quote Ready</h2>
        <p>{{customer_name}} - {{vehicle_year}} {{vehicle_make}} {{vehicle_model}}</p>
    </div>

    <div class="parts-section">
        <h3>Parts & Labor Breakdown</h3>
        {{parts_breakdown_html}}
    </div>

    <div class="cost-breakdown">
        <h3>Total Cost: €{{total_cost}}</h3>
        <p>Parts: €{{parts_total}}</p>
        <p>Labor: €{{labor_total}}</p>
        <p>VAT (23%): €{{vat_amount}}</p>
    </div>

    <div class="approval-buttons">
        <a href="{{approve_url}}" class="approve-btn">APPROVE REPAIR</a>
        <a href="{{decline_url}}" class="decline-btn">DECLINE</a>
        <a href="{{discuss_url}}">CALL TO DISCUSS</a>
    </div>
</body>
</html>
```

## Phase 3: Integration & Testing (Week 3-4)

### **Testing Protocols**

#### **1. Phone System Testing**
```python
# tests/test_phone_integration.py
import pytest
from diagnostic_intake import DiagnosticAgent

def test_incoming_call_handling():
    """Test that incoming calls are properly handled"""

    agent = DiagnosticAgent()

    # Simulate incoming call
    call_data = {
        "caller_id": "+353871234567",
        "call_time": "2024-10-15T10:30:00",
        "audio_stream": "simulated_audio_data"
    }

    response = agent.handle_incoming_call(call_data)

    assert response.status == "answered"
    assert "O'Connor's Auto Repair" in response.greeting
    assert response.next_action in ["collect_symptoms", "schedule_appointment"]

def test_symptom_analysis():
    """Test symptom analysis accuracy"""

    test_cases = [
        {
            "input": "My car makes a grinding noise when I brake",
            "expected_diagnosis": "brake_pad_wear",
            "expected_urgency": "high"
        },
        {
            "input": "Engine runs rough when idling",
            "expected_diagnosis": ["spark_plugs", "air_filter", "fuel_injectors"],
            "expected_urgency": "medium"
        }
    ]

    agent = DiagnosticAgent()

    for case in test_cases:
        result = agent.analyze_symptoms(case["input"])
        assert result.likely_diagnosis in case["expected_diagnosis"]
        assert result.urgency == case["expected_urgency"]
```

#### **2. Service Reminder Testing**
```python
# tests/test_service_reminders.py
def test_service_due_calculation():
    """Test that service due dates are calculated correctly"""

    from service_reminder import ServiceReminderAgent

    agent = ServiceReminderAgent()

    # Test vehicle with known service history
    vehicle = {
        "id": "test_vehicle_1",
        "make": "Honda",
        "model": "Civic",
        "year": 2019,
        "last_oil_change": "2024-08-15",
        "last_oil_change_mileage": 35000,
        "current_mileage": 42000
    }

    due_services = agent.calculate_due_services(vehicle)

    # Should identify oil change as due (7000km since last service)
    oil_change = next((s for s in due_services if s.type == "oil_change"), None)
    assert oil_change is not None
    assert oil_change.urgency == "due_now"
```

### **3. End-to-End Customer Journey Testing**
```python
# tests/test_customer_journey.py
def test_complete_customer_journey():
    """Test complete customer experience from call to completion"""

    # Stage 1: Customer calls with problem
    call_response = diagnostic_agent.handle_call(
        customer_input="My brakes are making noise"
    )

    assert "brake" in call_response.diagnosis.lower()
    assert call_response.appointment_scheduled

    # Stage 2: Vehicle arrives for service
    work_order = create_work_order(call_response.appointment)
    quote = quote_agent.generate_quote(work_order)

    assert quote.total_cost > 0
    assert len(quote.parts) > 0

    # Stage 3: Customer approves quote
    approval = quote_agent.process_approval(quote.id, approved=True)

    assert approval.status == "approved"
    assert approval.payment_processed

    # Stage 4: Work completed
    completion = communication_agent.send_completion_notice(work_order.id)

    assert completion.customer_notified
    assert completion.pickup_instructions_sent
```

## Phase 4: Staff Training (Week 4)

### **Training Materials**

#### **Quick Reference Cards**
```yaml
# training/quick-reference.yml
ai_system_basics:
  how_to_override_ai: "Press * during call, then 0 for immediate transfer"
  how_to_check_messages: "Dashboard > Messages > Pending Responses"
  how_to_update_quotes: "Work Orders > Select Order > Modify Quote"

common_situations:
  customer_wants_human:
    action: "AI will automatically transfer after saying 'Let me get Mike for you'"
    when: "Customer says 'speak to mechanic', 'talk to Mike', or similar"

  ai_diagnosis_wrong:
    action: "Update diagnosis in system, AI will learn from correction"
    location: "Dashboard > Diagnostics > Correct Diagnosis"

  parts_not_in_stock:
    action: "AI will automatically check suppliers and suggest alternatives"
    override: "Manual override available in Parts > Inventory"

daily_tasks:
  morning_checklist:
    - "Check overnight messages/appointments"
    - "Review AI-generated quotes for approval"
    - "Confirm parts orders placed by AI"

  end_of_day:
    - "Update any incomplete work orders"
    - "Review AI performance metrics"
    - "Approve any pending customer communications"
```

#### **Staff Training Schedule**
```markdown
# Week 4 Training Schedule

## Day 1: System Overview (Monday)
- 9:00 AM: Introduction to AI agents
- 10:30 AM: Phone system integration demo
- 2:00 PM: Customer database tour
- 3:30 PM: Basic troubleshooting

## Day 2: Diagnostic Intake (Tuesday)
- 9:00 AM: How the diagnostic AI works
- 10:30 AM: When to override AI decisions
- 2:00 PM: Handling edge cases
- 3:30 PM: Practice scenarios

## Day 3: Service & Communication (Wednesday)
- 9:00 AM: Service reminder system
- 10:30 AM: Quote approval process
- 2:00 PM: Customer communication flow
- 3:30 PM: Handling complaints/issues

## Day 4: Upselling & Parts (Thursday)
- 9:00 AM: Understanding AI upsell suggestions
- 10:30 AM: Parts management integration
- 2:00 PM: Loyalty program basics
- 3:30 PM: Inventory alerts

## Day 5: Practice & Go-Live (Friday)
- 9:00 AM: Full system practice
- 10:30 AM: Final questions/concerns
- 2:00 PM: Go-live preparation
- 3:30 PM: System activation
```

## Phase 5: Go-Live & Monitoring (Week 5+)

### **Week 1 Monitoring Checklist**
```yaml
daily_monitoring:
  call_handling:
    - calls_answered_by_ai: target_percentage > 90%
    - average_call_duration: target_range [2-8] minutes
    - transfer_to_human_rate: target_percentage < 20%
    - customer_satisfaction: target_rating > 4.0

  appointments:
    - ai_scheduled_appointments: target_count > 5 per day
    - appointment_confirmation_rate: target_percentage > 85%
    - no_show_rate: target_percentage < 10%

  quotes:
    - quotes_generated: target_count > 3 per day
    - quote_approval_rate: target_percentage > 60%
    - quote_accuracy: target_percentage > 90%

weekly_monitoring:
  revenue_impact:
    - additional_appointments: track increase
    - average_invoice_value: track increase
    - upsell_success_rate: target_percentage > 30%

  customer_feedback:
    - communication_satisfaction: target_rating > 4.5
    - process_convenience: target_rating > 4.3
    - overall_experience: target_rating > 4.4
```

### **Performance Dashboard Setup**
```javascript
// dashboard/config.js
const dashboardMetrics = {
  realTimeMetrics: [
    'calls_in_queue',
    'ai_agent_status',
    'current_appointments',
    'pending_approvals'
  ],

  dailyMetrics: [
    'calls_handled',
    'appointments_scheduled',
    'quotes_sent',
    'revenue_generated'
  ],

  weeklyMetrics: [
    'customer_satisfaction',
    'appointment_conversion_rate',
    'average_invoice_value',
    'parts_turnover'
  ],

  alerts: [
    {
      metric: 'call_answer_rate',
      threshold: 85,  // percentage
      action: 'email_notification'
    },
    {
      metric: 'customer_complaint',
      threshold: 1,   // any complaint
      action: 'immediate_notification'
    }
  ]
};
```

## Troubleshooting Guide

### **Common Issues & Solutions**

#### **1. Phone Integration Problems**
```yaml
issue: "Calls not being answered by AI"
solutions:
  - check_voip_connection: "Verify VoIP provider settings"
  - check_webhook_url: "Ensure webhook URL is accessible"
  - restart_service: "Restart diagnostic intake agent"
  - contact_support: "If issue persists > 30 minutes"

issue: "AI transferring too many calls to human"
solutions:
  - review_transfer_triggers: "Check transfer keyword list"
  - adjust_confidence_threshold: "Lower AI confidence requirement"
  - retrain_model: "Add more training examples"
```

#### **2. Service Reminder Issues**
```yaml
issue: "Reminders not being sent"
solutions:
  - check_customer_preferences: "Verify contact info and preferences"
  - check_sms_credits: "Ensure SMS service has sufficient credits"
  - review_service_intervals: "Verify service interval calculations"

issue: "Customers complaining about too many reminders"
solutions:
  - adjust_frequency: "Reduce reminder frequency in config"
  - improve_targeting: "Better filter for relevant reminders"
  - add_unsubscribe: "Ensure easy opt-out option"
```

## Success Metrics & ROI Tracking

### **30-Day Benchmark Targets**
```yaml
month_1_targets:
  operational:
    call_answer_rate: 95%
    appointment_booking_rate: 25%  # of calls
    quote_approval_rate: 65%
    customer_satisfaction: 4.2/5

  financial:
    additional_monthly_revenue: €8000
    cost_savings: €2500
    roi_percentage: 300%

month_3_targets:
  operational:
    call_answer_rate: 98%
    appointment_booking_rate: 35%
    quote_approval_rate: 75%
    customer_satisfaction: 4.5/5

  financial:
    additional_monthly_revenue: €15000
    cost_savings: €4000
    roi_percentage: 500%
```

### **ROI Calculation Worksheet**
```python
# roi_calculator.py
def calculate_monthly_roi():
    """Calculate monthly ROI for garage AI implementation"""

    # Revenue gains
    additional_appointments = 45  # per month
    average_appointment_value = 185  # euros
    additional_revenue = additional_appointments * average_appointment_value

    # Upselling gains
    upsell_rate = 0.35  # 35% of services
    average_upsell_value = 85  # euros
    total_services = 120  # per month
    upsell_revenue = total_services * upsell_rate * average_upsell_value

    # Cost savings
    reduced_admin_time = 40  # hours per month
    hourly_cost = 25  # euros per hour
    admin_savings = reduced_admin_time * hourly_cost

    # Total benefits
    total_monthly_benefit = additional_revenue + upsell_revenue + admin_savings

    # System costs
    ai_system_cost = 800  # euros per month
    setup_cost_amortized = 2000 / 12  # euros per month (12-month amortization)
    total_monthly_cost = ai_system_cost + setup_cost_amortized

    # ROI calculation
    roi_percentage = ((total_monthly_benefit - total_monthly_cost) / total_monthly_cost) * 100

    return {
        "additional_revenue": additional_revenue,
        "upsell_revenue": upsell_revenue,
        "cost_savings": admin_savings,
        "total_benefit": total_monthly_benefit,
        "total_cost": total_monthly_cost,
        "net_benefit": total_monthly_benefit - total_monthly_cost,
        "roi_percentage": roi_percentage
    }

# Example output:
# {
#   "additional_revenue": 8325,
#   "upsell_revenue": 3570,
#   "cost_savings": 1000,
#   "total_benefit": 12895,
#   "total_cost": 967,
#   "net_benefit": 11928,
#   "roi_percentage": 1234%
# }
```

## Support & Maintenance

### **Monthly Maintenance Tasks**
- [ ] Review AI performance metrics
- [ ] Update parts pricing database
- [ ] Analyze customer feedback
- [ ] Optimize service intervals
- [ ] Update seasonal campaigns
- [ ] Backup system data
- [ ] Review security logs

### **Support Contacts**
- **Technical Support**: tech-support@garage-ai.com
- **Implementation Specialist**: implementation@garage-ai.com
- **24/7 Emergency Line**: +353-800-GARAGE-AI
- **Documentation**: https://docs.garage-ai.com
- **Community Forum**: https://community.garage-ai.com

---

**Ready to transform your garage operations?** Follow this guide step-by-step, and you'll have a fully operational AI-powered garage system within 4 weeks.

**Questions?** Contact our implementation team at **implementation@garage-ai.com** for personalized assistance.