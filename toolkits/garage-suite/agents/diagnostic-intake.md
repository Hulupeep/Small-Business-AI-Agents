# 🔍 Diagnostic Intake & Triage Agent

*The AI that answers every call and pre-diagnoses every problem*

## Overview

The Diagnostic Intake Agent serves as your 24/7 phone answering and initial diagnostic system. It handles incoming calls, texts, and digital inquiries, performs preliminary symptom analysis, and schedules appropriate appointments based on urgency and complexity.

## Core Capabilities

### 1. **Symptom Analysis Engine**
```python
# Example symptom mapping
SYMPTOM_DATABASE = {
    "grinding_noise_braking": {
        "likely_causes": ["brake_pad_wear", "rotor_damage"],
        "urgency": "high",
        "safety_risk": "significant",
        "typical_cost_range": (250, 450),
        "diagnostic_questions": [
            "How long have you noticed this noise?",
            "Does it happen every time you brake?",
            "Any vibration in the steering wheel?"
        ]
    },
    "engine_rough_idle": {
        "likely_causes": ["spark_plugs", "air_filter", "fuel_injectors"],
        "urgency": "medium",
        "safety_risk": "minimal",
        "typical_cost_range": (150, 400),
        "diagnostic_questions": [
            "When did the rough idling start?",
            "Does it happen when cold or warm?",
            "Any dashboard warning lights?"
        ]
    }
}
```

### 2. **Photo/Video Assessment**
- Accepts customer uploads via text or email
- AI vision analysis for visible issues
- Damage severity assessment
- Parts identification and preliminary quotes

### 3. **Urgency Scoring System**
```python
URGENCY_MATRIX = {
    "critical": {
        "symptoms": ["no_brakes", "engine_fire", "steering_failure"],
        "action": "immediate_tow_recommend",
        "appointment": "emergency_slot"
    },
    "high": {
        "symptoms": ["brake_noise", "overheating", "transmission_slip"],
        "action": "schedule_within_24hrs",
        "appointment": "priority_slot"
    },
    "medium": {
        "symptoms": ["rough_idle", "check_engine", "minor_leak"],
        "action": "schedule_within_week",
        "appointment": "standard_slot"
    },
    "low": {
        "symptoms": ["oil_change_due", "tire_wear", "cosmetic_damage"],
        "action": "schedule_convenient",
        "appointment": "flexible_slot"
    }
}
```

## Implementation Code

### Main Intake Handler
```python
class DiagnosticIntakeAgent:
    def __init__(self):
        self.symptom_analyzer = SymptomAnalyzer()
        self.scheduler = AppointmentScheduler()
        self.communicator = CustomerCommunicator()

    async def handle_incoming_inquiry(self, inquiry):
        """Process customer inquiry and provide response"""

        # Parse inquiry type
        inquiry_type = self.classify_inquiry(inquiry)

        if inquiry_type == "symptom_description":
            return await self.process_symptom_inquiry(inquiry)
        elif inquiry_type == "photo_upload":
            return await self.process_visual_inquiry(inquiry)
        elif inquiry_type == "emergency":
            return await self.handle_emergency(inquiry)
        else:
            return await self.general_inquiry_response(inquiry)

    async def process_symptom_inquiry(self, inquiry):
        """Analyze symptoms and provide preliminary diagnosis"""

        # Extract symptoms using NLP
        symptoms = self.symptom_analyzer.extract_symptoms(inquiry.text)

        # Match against known issues
        potential_diagnoses = self.symptom_analyzer.match_symptoms(symptoms)

        # Generate response
        response = self.generate_diagnostic_response(
            symptoms=symptoms,
            diagnoses=potential_diagnoses,
            vehicle_info=inquiry.vehicle_info
        )

        # Schedule appropriate appointment
        appointment = await self.scheduler.suggest_appointment(
            urgency=response.urgency,
            estimated_duration=response.estimated_repair_time
        )

        return {
            "response": response,
            "appointment_suggestion": appointment,
            "follow_up_questions": response.clarifying_questions
        }
```

### Symptom Analysis Module
```python
class SymptomAnalyzer:
    def __init__(self):
        self.nlp_model = self.load_automotive_nlp_model()
        self.symptom_database = self.load_symptom_database()

    def extract_symptoms(self, customer_description):
        """Extract structured symptoms from customer description"""

        # Process text with automotive-specific NLP
        doc = self.nlp_model(customer_description)

        extracted_symptoms = {
            "sounds": self.extract_sounds(doc),
            "behaviors": self.extract_behaviors(doc),
            "conditions": self.extract_conditions(doc),
            "visual_indicators": self.extract_visual_indicators(doc)
        }

        return extracted_symptoms

    def match_symptoms(self, symptoms):
        """Match symptoms against known diagnostic patterns"""

        matches = []

        for condition_id, condition_data in self.symptom_database.items():
            confidence = self.calculate_match_confidence(
                symptoms,
                condition_data['symptoms']
            )

            if confidence > 0.6:
                matches.append({
                    "condition": condition_id,
                    "confidence": confidence,
                    "data": condition_data
                })

        # Sort by confidence
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
```

## Sample Conversation Flows

### **Flow 1: Brake Noise Inquiry**
```
Customer: "My car is making a grinding noise when I brake"

Agent: "I understand that's concerning. Grinding noises during braking often indicate brake pad wear, which is a safety issue. Can you tell me:
1. How long have you noticed this noise?
2. Does it happen every time you brake or only sometimes?
3. Any vibration in the steering wheel when braking?"

Customer: "Started about a week ago, happens every time, no vibration"

Agent: "Based on those symptoms, it sounds like your brake pads have worn down to the metal backing. This needs attention within the next few days for safety. For your 2018 Honda Civic, brake pad replacement typically runs €280-€350 including labor.

I can schedule you for Thursday at 2 PM for a full brake inspection and repair. We'll also check your rotors to make sure they haven't been damaged. Would that work for you?"
```

### **Flow 2: Photo Upload Assessment**
```
Customer: [Uploads photo of rusted exhaust pipe]

Agent: "Thanks for the photo! I can see significant rust on your exhaust pipe. Based on the corrosion level, you'll likely need exhaust repair or replacement soon.

This isn't immediately dangerous, but it will:
- Get progressively louder
- Fail your next MOT test
- Potentially affect fuel economy

For your vehicle, exhaust repair typically runs €180-€320 depending on which sections need replacement. Would you like me to schedule an inspection to give you an exact quote?"
```

### **Flow 3: Emergency Situation**
```
Customer: "My brakes went soft and I can barely stop!"

Agent: "This is a safety emergency. Please:
1. Drive VERY carefully to a safe location
2. DO NOT drive further than absolutely necessary
3. I'm arranging immediate assistance

Can you safely pull over now? I'm going to:
- Send our mobile diagnostic van to your location
- Arrange a tow truck if needed
- Clear an emergency slot for immediate repair

What's your exact location?"
```

## Integration Requirements

### **Phone System Integration**
```python
# Example integration with VoIP system
class PhoneSystemIntegration:
    def __init__(self, voip_provider):
        self.voip = voip_provider
        self.call_handler = CallHandler()

    async def handle_incoming_call(self, call_data):
        """Process incoming phone call"""

        # Answer call with AI agent
        response = await self.call_handler.process_call(
            caller_info=call_data.caller_id,
            call_audio=call_data.audio_stream
        )

        # Convert text response to speech
        audio_response = self.text_to_speech(response.text)

        # Send response back to caller
        await self.voip.send_audio(call_data.call_id, audio_response)
```

### **SMS/Text Integration**
```python
# Example SMS handling
class SMSIntegration:
    def __init__(self, sms_provider):
        self.sms = sms_provider
        self.intake_agent = DiagnosticIntakeAgent()

    async def handle_incoming_sms(self, message):
        """Process incoming text message"""

        # Check if message contains photos
        if message.media_attachments:
            response = await self.intake_agent.process_visual_inquiry(message)
        else:
            response = await self.intake_agent.process_symptom_inquiry(message)

        # Send response back to customer
        await self.sms.send_message(
            to=message.sender,
            text=response.text,
            attachments=response.attachments
        )
```

## Configuration Options

### **Business Hours Handling**
```yaml
business_hours:
  monday:
    start: "08:00"
    end: "18:00"
  tuesday:
    start: "08:00"
    end: "18:00"
  # ... other days

after_hours_response: |
    Hi! You've reached O'Connor's Auto Repair after hours.
    I can still help with emergency diagnostics and scheduling.
    For non-emergency repairs, I'll have Mike call you first
    thing tomorrow morning.

emergency_keywords:
  - "emergency"
  - "can't drive"
  - "no brakes"
  - "engine fire"
  - "accident"
```

### **Pricing Configuration**
```yaml
pricing_ranges:
  brake_service:
    min: 250
    max: 450
    currency: "EUR"
    includes: ["pads", "inspection", "labor"]

  oil_change:
    min: 45
    max: 85
    currency: "EUR"
    includes: ["oil", "filter", "inspection"]

  diagnostic:
    standard: 85
    complex: 125
    currency: "EUR"
```

## Performance Metrics

### **Call Handling Metrics**
- **Answer Rate**: Target >95% (vs current ~70%)
- **Average Response Time**: <30 seconds
- **Call Resolution Rate**: >80% without human intervention
- **Customer Satisfaction**: >4.5/5 rating

### **Diagnostic Accuracy**
- **Preliminary Diagnosis Accuracy**: >75% match with final diagnosis
- **Urgency Classification Accuracy**: >90%
- **Cost Estimate Accuracy**: Within ±20% of final quote

### **Conversion Metrics**
- **Inquiry to Appointment Rate**: Target >60%
- **Emergency Response Time**: <5 minutes
- **Follow-up Contact Success**: >85%

## Customization Examples

### **Local Market Adaptation**
```python
# Ireland-specific customizations
IRELAND_CUSTOMIZATIONS = {
    "currency": "EUR",
    "test_requirements": {
        "mot_equivalent": "NCT",
        "frequency": "every_2_years_after_4_years"
    },
    "seasonal_reminders": {
        "winter_tires": "October-March",
        "battery_checks": "November-February"
    },
    "common_issues": {
        "road_salt_corrosion": "high_priority",
        "diesel_particulate_filter": "common_in_older_cars"
    }
}
```

### **Garage-Specific Tuning**
```python
# O'Connor's specific configuration
OCONNOR_CONFIG = {
    "specialties": ["transmission", "engine_rebuild", "classic_cars"],
    "courtesy_cars": 2,
    "mobile_service": True,
    "diagnostic_equipment": ["OBD2", "oscilloscope", "compression_tester"],
    "brand_expertise": ["Honda", "Toyota", "Ford", "Volkswagen"]
}
```

## Training Data Requirements

### **Sample Training Conversations**
```json
{
  "training_examples": [
    {
      "customer_input": "My car won't start this morning",
      "agent_response": "I can help diagnose that. When you turn the key, what happens? Do you hear any sound - clicking, cranking, or complete silence?",
      "follow_up_questions": [
        "Are your headlights working normally?",
        "When did you last drive the car?",
        "Any recent work done on the vehicle?"
      ]
    }
  ]
}
```

## Next Steps

1. **[Configure Phone Integration](../config/phone-setup.md)**
2. **[Import Vehicle Database](../config/vehicle-data.md)**
3. **[Set Up SMS/Email Handling](../config/communication-setup.md)**
4. **[Train Custom Responses](../config/training-setup.md)**

---

*This agent typically handles 200+ inquiries per month and captures 90% of calls that would otherwise be missed.*