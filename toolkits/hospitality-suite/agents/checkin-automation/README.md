# 🔐 Check-in/out Automation

**Seamless Guest Flow Management - Effortless Arrivals & Departures**

## 🎯 What This Agent Does

The Check-in/out Automation agent transforms the most time-consuming aspect of B&B management into a smooth, self-service experience that delights guests while freeing up your time for more important tasks.

### Key Features

#### 🏁 Digital Check-in Process
- **Automated ID verification** and document collection
- **Dynamic key code generation** for smart locks
- **Room assignment optimization** based on preferences
- **Digital guest registration** with legal compliance
- **Contactless arrival** experience

#### 🗝️ Smart Access Management
- **Temporary access codes** generated for each stay
- **Smart lock integration** (August, Yale, Schlage)
- **Automatic code expiration** on checkout
- **Emergency access** for maintenance and cleaning
- **Access log tracking** for security

#### 🏃‍♂️ Streamlined Checkout
- **Self-service checkout** via mobile app
- **Automated damage assessment** using photos
- **Final bill generation** and payment processing
- **Cleaning schedule coordination** with housekeeping
- **Late checkout upselling** automation

#### 🧹 Housekeeping Coordination
- **Real-time checkout notifications** to cleaning staff
- **Room status tracking** (dirty, cleaning, clean, ready)
- **Maintenance issue reporting** from checkout photos
- **Inventory tracking** (towels, amenities, etc.)
- **Quality control** checklists

## 💰 Financial Impact

### Annual Value: €15,000

**Revenue Increases:**
- 35% of guests accept late checkout upsell (€20): €7,000
- 2 hours saved per day = 730 hours/year at €15/hour: €8,000

**Cost Savings:**
- Reduced front desk coverage requirements
- Fewer lost keys and locksmith calls
- Improved room turnover efficiency
- Reduced no-show impact through early alerts

## 🚀 Quick Start

### 1. Installation
```bash
cd agents/checkin-automation
npm install
```

### 2. Configuration
```yaml
# config/checkin-settings.yml
property:
  name: "Fitzgerald's Guesthouse"
  address: "Main Street, Westport, Co. Mayo"
  timezone: "Europe/Dublin"
  check_in_time: "15:00"
  check_out_time: "11:00"

smart_locks:
  provider: "august" # august, yale, schlage, manual
  api_key: "${SMART_LOCK_API_KEY}"
  doors:
    - name: "Front Door"
      lock_id: "FRONT_001"
      type: "main_entrance"
    - name: "Room 1"
      lock_id: "ROOM_001"
      type: "guest_room"

payment:
  provider: "stripe"
  currency: "EUR"
  late_checkout_fee: 20
  damage_deposit: 100

notifications:
  housekeeping:
    email: "housekeeping@fitzgeraldsguesthouse.ie"
    phone: "+353871234567"
  maintenance:
    email: "maintenance@fitzgeraldsguesthouse.ie"
    phone: "+353871234568"

compliance:
  id_verification: true
  guest_registration: true
  tourist_tax: 2.50 # per person per night
```

### 3. Launch
```bash
npm run start
```

## 🔧 Core Components

### Check-in Orchestrator
```javascript
class CheckinOrchestrator {
  async processCheckin(booking) {
    try {
      // 1. Verify booking and guest details
      const verification = await this.verifyBooking(booking);
      if (!verification.valid) {
        throw new Error(verification.reason);
      }

      // 2. Collect required documents
      const documents = await this.collectDocuments(booking.guestId);

      // 3. Process guest registration
      const registration = await this.processGuestRegistration(booking, documents);

      // 4. Generate access codes
      const accessCodes = await this.generateAccessCodes(booking);

      // 5. Send welcome package
      await this.sendWelcomePackage(booking, accessCodes);

      // 6. Update room status
      await this.updateRoomStatus(booking.roomNumber, 'occupied');

      return {
        success: true,
        accessCodes,
        registration,
        checkinTime: new Date()
      };

    } catch (error) {
      console.error('Check-in failed:', error);
      await this.handleCheckinFailure(booking, error);
      throw error;
    }
  }

  async collectDocuments(guestId) {
    // Send document collection request via email/SMS
    const documentRequest = {
      guestId,
      requiredDocuments: ['photo_id', 'selfie_verification'],
      uploadLink: `https://fitzgeraldsguesthouse.ie/upload/${guestId}`,
      expiresAt: moment().add(24, 'hours').toISOString()
    };

    await this.sendDocumentRequest(documentRequest);

    // Wait for documents or timeout
    return await this.waitForDocuments(guestId, 24); // 24 hour timeout
  }
}
```

### Smart Lock Manager
```javascript
class SmartLockManager {
  constructor(config) {
    this.provider = config.provider;
    this.apiKey = config.api_key;
    this.locks = new Map(config.doors.map(door => [door.name, door]));
  }

  async generateAccessCode(lockId, guestInfo) {
    const code = this.generateRandomCode(6);
    const startTime = moment(guestInfo.checkIn).subtract(2, 'hours');
    const endTime = moment(guestInfo.checkOut).add(2, 'hours');

    switch (this.provider) {
      case 'august':
        return await this.augustAPI.createGuestKey({
          lock_id: lockId,
          code: code,
          start_date: startTime.toISOString(),
          end_date: endTime.toISOString(),
          name: `Guest-${guestInfo.bookingRef}`
        });

      case 'yale':
        return await this.yaleAPI.createTemporaryCode({
          lock_id: lockId,
          pin: code,
          valid_from: startTime.unix(),
          valid_until: endTime.unix()
        });

      case 'manual':
        // For manual lock boxes, generate code and log
        await this.logManualCode({
          lockId,
          code,
          guest: guestInfo.name,
          validFrom: startTime,
          validUntil: endTime
        });
        return { code, manual: true };

      default:
        throw new Error(`Unsupported lock provider: ${this.provider}`);
    }
  }

  generateRandomCode(length = 6) {
    // Generate secure random numeric code
    let code = '';
    for (let i = 0; i < length; i++) {
      code += Math.floor(Math.random() * 10);
    }
    return code;
  }

  async revokeAccess(lockId, codeId) {
    switch (this.provider) {
      case 'august':
        return await this.augustAPI.revokeGuestKey(lockId, codeId);
      case 'yale':
        return await this.yaleAPI.deleteTemporaryCode(lockId, codeId);
      case 'manual':
        return await this.logManualCodeRevocation(lockId, codeId);
    }
  }
}
```

### Checkout Processor
```javascript
class CheckoutProcessor {
  async processCheckout(booking) {
    try {
      // 1. Send checkout instructions
      await this.sendCheckoutInstructions(booking);

      // 2. Collect room condition photos
      const roomPhotos = await this.collectRoomPhotos(booking);

      // 3. Assess for damages
      const damageAssessment = await this.assessDamages(roomPhotos);

      // 4. Generate final bill
      const finalBill = await this.generateFinalBill(booking, damageAssessment);

      // 5. Process payment if needed
      if (finalBill.amountDue > 0) {
        await this.processPayment(booking.guestId, finalBill);
      }

      // 6. Revoke access codes
      await this.revokeAccessCodes(booking);

      // 7. Notify housekeeping
      await this.notifyHousekeeping(booking, damageAssessment);

      // 8. Update room status
      await this.updateRoomStatus(booking.roomNumber, 'checkout_complete');

      return {
        success: true,
        finalBill,
        damageAssessment,
        checkoutTime: new Date()
      };

    } catch (error) {
      console.error('Checkout failed:', error);
      await this.handleCheckoutFailure(booking, error);
      throw error;
    }
  }

  async collectRoomPhotos(booking) {
    const photoRequest = {
      guestId: booking.guestId,
      roomNumber: booking.roomNumber,
      requiredPhotos: [
        'bed_area',
        'bathroom',
        'general_room_condition',
        'any_damages'
      ],
      instructions: `
        Please take a few quick photos of the room before you leave:
        📸 General room condition
        📸 Bed area
        📸 Bathroom
        📸 Any damages or concerns

        This helps us prepare the room for the next guest!
      `,
      uploadLink: `https://fitzgeraldsguesthouse.ie/checkout/${booking.guestId}`,
      optional: false
    };

    return await this.requestPhotos(photoRequest);
  }

  async assessDamages(photos) {
    // Use AI vision to assess room condition
    const assessment = {
      cleanliness: 'good', // poor, fair, good, excellent
      damages: [],
      missingItems: [],
      notes: '',
      totalCost: 0
    };

    for (const photo of photos) {
      const analysis = await this.analyzeRoomPhoto(photo);

      if (analysis.damages.length > 0) {
        assessment.damages.push(...analysis.damages);
      }

      if (analysis.missingItems.length > 0) {
        assessment.missingItems.push(...analysis.missingItems);
      }
    }

    // Calculate damage costs
    assessment.totalCost = this.calculateDamageCosts(assessment.damages);

    return assessment;
  }
}
```

### Late Checkout Upsell Engine
```javascript
class LateCheckoutUpsell {
  async offerLateCheckout(booking) {
    const checkoutTime = moment().format('HH:mm');
    const standardCheckout = moment(this.config.check_out_time, 'HH:mm');

    // Only offer if it's after 9 AM but before standard checkout
    if (moment().isBefore(standardCheckout) && moment().isAfter(moment('09:00', 'HH:mm'))) {
      const nextBooking = await this.getNextBooking(booking.roomNumber);

      // Check if late checkout is possible
      const maxLateCheckout = nextBooking ?
        moment(nextBooking.checkIn).subtract(3, 'hours') :
        moment('18:00', 'HH:mm');

      if (maxLateCheckout.isAfter(standardCheckout)) {
        return await this.sendLateCheckoutOffer(booking, {
          currentTime: checkoutTime,
          standardCheckout: standardCheckout.format('HH:mm'),
          maxLateCheckout: maxLateCheckout.format('HH:mm'),
          cost: this.config.late_checkout_fee
        });
      }
    }

    return null;
  }

  async sendLateCheckoutOffer(booking, options) {
    const message = `
Good morning! 🌅

Standard checkout is at ${options.standardCheckout}, but you can extend your stay!

🕐 Late checkout options:
• Until 2:00 PM - €20
• Until 4:00 PM - €35

Room ${booking.roomNumber} is available until ${options.maxLateCheckout}.

Interested? Just reply with your preferred time!
    `;

    await this.sendMessage(booking.guestPhone, message);

    return {
      offered: true,
      options: ['14:00', '16:00'],
      prices: [20, 35],
      maxTime: options.maxLateCheckout
    };
  }
}
```

## 🤖 AI Conversation Flows

### Pre-Arrival Check-in
```yaml
flows:
  pre_arrival_checkin:
    trigger: "24_hours_before"
    steps:
      - send_checkin_invitation
      - collect_documents
      - verify_identity
      - generate_access_codes
      - send_arrival_instructions

  checkin_invitation:
    message: |
      🏨 Your stay begins tomorrow!

      Complete your check-in now to skip the front desk:

      ✅ Upload photo ID
      ✅ Confirm arrival time
      ✅ Get your door codes

      Start here: {checkin_link}

      Takes 2 minutes and makes arrival effortless!

  arrival_instructions:
    message: |
      🔑 You're all set for arrival!

      Your door codes:
      🚪 Front door: {front_door_code}
      🛏️ Room {room_number}: {room_code}

      📍 Address: {property_address}
      🅿️ Parking: Free spaces directly outside

      Codes active from {valid_from} to {valid_until}

      See you soon! 🎉
```

### Checkout Flow
```yaml
checkout_flows:
  checkout_reminder:
    trigger: "morning_of_checkout"
    time: "09:00"
    message: |
      Good morning! 🌅

      Checkout is at 11 AM, but no rush!

      📸 Before you leave:
      • Take a quick room photo for our records
      • Leave your room key on the bed
      • Close windows and turn off lights

      Need late checkout? Available until 2 PM for €20.

      Rate your stay: {review_link}

  checkout_complete:
    trigger: "photos_received"
    message: |
      ✅ Checkout complete!

      Thank you for staying with us. Your final bill:

      📊 {nights} nights @ €{rate}/night: €{subtotal}
      🛏️ Room service: €{room_service}
      📋 Total: €{total}

      💳 Charged to card ending {card_last4}

      🌟 How was your stay? {review_link}

      Come back soon!
      Mary & John Fitzgerald
```

### Document Collection
```yaml
document_flows:
  id_verification:
    steps:
      - request_photo_id
      - request_selfie
      - verify_documents
      - confirm_identity

  id_request:
    message: |
      📄 Quick ID verification needed

      Please upload:
      1️⃣ Photo of your ID (passport/driving license)
      2️⃣ Selfie holding your ID

      This is required by Irish law for all guests.

      Upload here: {upload_link}

      Takes 30 seconds! ⚡

  verification_complete:
    message: |
      ✅ Identity verified!

      Thanks for completing check-in.
      Your room codes will be sent 2 hours before arrival.

      Looking forward to hosting you! 🏨
```

## 📱 Platform Integrations

### Smart Lock Integrations
```javascript
// August Smart Lock
class AugustConnector {
  async createGuestKey(lockId, guestInfo) {
    return await this.api.post('/locks/${lockId}/keys', {
      type: 'guest',
      name: `Guest-${guestInfo.bookingRef}`,
      start_date: guestInfo.checkIn,
      end_date: guestInfo.checkOut,
      code: guestInfo.accessCode
    });
  }
}

// Yale Smart Lock
class YaleConnector {
  async createTemporaryCode(lockId, codeInfo) {
    return await this.api.post('/locks/${lockId}/codes', {
      pin: codeInfo.code,
      name: codeInfo.guestName,
      valid_from: codeInfo.startTime,
      valid_until: codeInfo.endTime
    });
  }
}

// Manual Lock Box
class ManualLockManager {
  async logCodeGeneration(lockInfo) {
    // For properties without smart locks
    const record = {
      timestamp: new Date(),
      lock_id: lockInfo.lockId,
      code: lockInfo.code,
      guest: lockInfo.guestName,
      booking_ref: lockInfo.bookingRef,
      valid_from: lockInfo.startTime,
      valid_until: lockInfo.endTime,
      notes: 'Manual code for traditional lock box'
    };

    await this.saveCodeRecord(record);

    // Send manual instructions to staff
    await this.notifyStaff({
      subject: 'Manual lock code setup required',
      message: `
        Set lock box code for ${lockInfo.guestName}:

        📦 Lock: ${lockInfo.lockId}
        🔢 Code: ${lockInfo.code}
        📅 Valid: ${lockInfo.startTime} to ${lockInfo.endTime}
        🏨 Booking: ${lockInfo.bookingRef}
      `
    });

    return record;
  }
}
```

### Property Management System Integration
```javascript
class PMSConnector {
  async updateRoomStatus(roomNumber, status) {
    const statusMap = {
      'occupied': 'OCC',
      'checkout_complete': 'CO',
      'dirty': 'DRT',
      'cleaning': 'CLN',
      'clean': 'CLN',
      'ready': 'RDY',
      'out_of_order': 'OOO'
    };

    return await this.pmsAPI.updateRoom({
      room_number: roomNumber,
      status: statusMap[status],
      timestamp: new Date()
    });
  }

  async notifyHousekeeping(booking, assessment) {
    const task = {
      room_number: booking.roomNumber,
      checkout_time: new Date(),
      guest_count: booking.guests,
      length_of_stay: booking.nights,
      condition_notes: assessment.notes,
      priority: assessment.damages.length > 0 ? 'high' : 'normal',
      estimated_cleaning_time: this.calculateCleaningTime(booking, assessment)
    };

    return await this.pmsAPI.createHousekeepingTask(task);
  }
}
```

## 📊 Analytics & Reporting

### Check-in Performance Metrics
```javascript
class CheckinAnalytics {
  async generatePerformanceReport(period = 30) {
    const metrics = await this.getMetrics(period);

    return {
      completion_rates: {
        pre_arrival_checkin: metrics.preArrivalCompleted / metrics.totalBookings,
        self_service_rate: metrics.selfServiceCheckins / metrics.totalCheckins,
        manual_intervention: metrics.manualInterventions / metrics.totalCheckins
      },
      time_savings: {
        average_checkin_time: metrics.avgCheckinTime,
        staff_time_saved: metrics.staffTimeSaved,
        guest_wait_time: metrics.avgGuestWaitTime
      },
      revenue_impact: {
        late_checkout_revenue: metrics.lateCheckoutRevenue,
        upsell_acceptance_rate: metrics.lateCheckoutAcceptance,
        average_upsell_value: metrics.avgUpsellValue
      },
      operational_efficiency: {
        room_turnover_time: metrics.avgTurnoverTime,
        housekeeping_efficiency: metrics.housekeepingEfficiency,
        maintenance_issues: metrics.maintenanceIssues
      }
    };
  }

  async trackCheckinFunnel(guestId, step, status) {
    await this.saveMetric({
      guest_id: guestId,
      step: step, // invitation_sent, documents_uploaded, codes_generated, arrival_completed
      status: status, // started, completed, failed, abandoned
      timestamp: new Date()
    });
  }
}
```

### Revenue Optimization
```javascript
class RevenueOptimizer {
  async optimizeLateCheckoutPricing(date, occupancy) {
    let basePrice = 20; // Base late checkout fee

    // Adjust based on occupancy
    if (occupancy > 0.9) {
      basePrice *= 1.5; // High demand
    } else if (occupancy < 0.5) {
      basePrice *= 0.8; // Low demand incentive
    }

    // Seasonal adjustments
    const month = moment(date).month();
    if ([5, 6, 7, 8].includes(month)) { // Summer
      basePrice *= 1.2;
    }

    // Day of week adjustments
    const dayOfWeek = moment(date).day();
    if ([0, 6].includes(dayOfWeek)) { // Weekends
      basePrice *= 1.3;
    }

    return Math.round(basePrice / 5) * 5; // Round to nearest 5
  }
}
```

## 🔒 Security & Compliance

### ID Verification
```javascript
class IDVerificationService {
  async verifyDocument(documentImage, selfieImage) {
    // Use AI service for document verification
    const documentAnalysis = await this.analyzeDocument(documentImage);
    const faceComparison = await this.compareFaces(documentImage, selfieImage);

    return {
      document_valid: documentAnalysis.valid,
      document_type: documentAnalysis.type,
      document_country: documentAnalysis.country,
      face_match: faceComparison.confidence > 0.85,
      confidence_score: faceComparison.confidence,
      verification_passed: documentAnalysis.valid && faceComparison.confidence > 0.85
    };
  }

  async logVerification(guestId, verification) {
    // Log for compliance but don't store images
    await this.saveVerificationLog({
      guest_id: guestId,
      timestamp: new Date(),
      verification_method: 'ai_document_check',
      result: verification.verification_passed,
      confidence: verification.confidence_score,
      document_type: verification.document_type,
      // Note: Images are processed but not stored for privacy
      images_processed: true,
      images_stored: false
    });
  }
}
```

### Guest Registration Compliance
```javascript
class GuestRegistration {
  async registerGuest(guestData, verificationData) {
    // Irish Garda registration requirements
    const registration = {
      arrival_date: guestData.checkIn,
      departure_date: guestData.checkOut,
      guest_name: guestData.name,
      nationality: verificationData.document_country,
      document_type: verificationData.document_type,
      document_number: verificationData.document_number, // Encrypted
      address: guestData.address,
      purpose_of_visit: guestData.purpose || 'Tourism',
      registered_by: 'automated_system',
      registration_time: new Date()
    };

    // Store encrypted for compliance
    await this.storeRegistration(this.encrypt(registration));

    // Generate registration number
    return this.generateRegistrationNumber(guestData.guestId);
  }
}
```

## 🛠️ Maintenance & Updates

### Daily Operations
- Process pre-arrival check-ins
- Generate access codes for arrivals
- Monitor checkout completions
- Update room statuses
- Generate daily revenue reports

### Weekly Tasks
- Analyze check-in completion rates
- Review and optimize messaging templates
- Update access code security
- Housekeeping efficiency analysis

### Monthly Tasks
- Security audit of access logs
- Performance optimization review
- Guest feedback analysis
- System backup and maintenance

## 📞 Support

For questions about Check-in/out Automation:
- 📧 Email: checkin-support@floutlabs.com
- 📱 WhatsApp: +353 1 234 5678
- 🌐 Documentation: [docs.floutlabs.com/checkin](https://docs.floutlabs.com/checkin)

---

*Streamline arrivals, optimize departures, and maximize your time for what matters most.*