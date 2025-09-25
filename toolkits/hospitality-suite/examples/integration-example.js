#!/usr/bin/env node

/**
 * Hospitality AI Suite Integration Example
 * Demonstrates how to integrate all 5 AI agents for a complete B&B automation system
 */

const { BookingManager } = require('../agents/booking-manager/booking-manager.js');
const { GuestConcierge } = require('../agents/guest-concierge/guest-concierge.js');
const { CheckinAutomation } = require('../agents/checkin-automation/checkin-automation.js');
const { LocalGuide } = require('../agents/local-guide/local-guide.js');
const { ReviewManager } = require('../agents/review-manager/review-manager.js');

/**
 * Complete Hospitality Management System
 * Orchestrates all AI agents for seamless B&B operations
 */
class HospitalityManagementSystem {
  constructor(config) {
    this.config = config;

    // Initialize all AI agents
    this.bookingManager = new BookingManager(config.booking);
    this.guestConcierge = new GuestConcierge(config.concierge);
    this.checkinAutomation = new CheckinAutomation(config.checkin);
    this.localGuide = new LocalGuide(config.guide);
    this.reviewManager = new ReviewManager(config.reviews);

    this.setupEventHandlers();
  }

  setupEventHandlers() {
    // Cross-agent communication and workflow coordination

    // Booking confirmed → Start guest experience flow
    this.bookingManager.on('booking_confirmed', async (booking) => {
      await this.handleNewBooking(booking);
    });

    // Guest checked in → Activate concierge and local guide
    this.checkinAutomation.on('checkin_completed', async (checkinData) => {
      await this.handleGuestCheckin(checkinData);
    });

    // Guest checked out → Trigger reviews and satisfaction survey
    this.checkinAutomation.on('checkout_completed', async (checkoutData) => {
      await this.handleGuestCheckout(checkoutData);
    });

    // Negative feedback → Immediate intervention
    this.reviewManager.on('negative_feedback', async (feedback) => {
      await this.handleNegativeFeedback(feedback);
    });
  }

  /**
   * Handle new booking - coordinate pre-arrival experience
   */
  async handleNewBooking(booking) {
    console.log(`🏨 New booking confirmed: ${booking.reference}`);

    try {
      // 1. Send welcome message via concierge
      await this.guestConcierge.sendWelcomeMessage(booking);

      // 2. Schedule pre-arrival check-in
      await this.checkinAutomation.schedulePreArrivalCheckin(booking);

      // 3. Prepare local recommendations based on guest profile
      const recommendations = await this.localGuide.preparePersonalizedRecommendations(booking);

      // 4. Store guest preferences for later use
      await this.guestConcierge.createGuestProfile(booking, recommendations);

      // 5. Set up review monitoring for this guest
      await this.reviewManager.addGuestToMonitoring(booking);

      console.log(`✅ Guest journey initiated for ${booking.guestName}`);

    } catch (error) {
      console.error('Error handling new booking:', error);
      await this.alertStaff('booking_error', { booking, error });
    }
  }

  /**
   * Handle guest check-in - activate during-stay services
   */
  async handleGuestCheckin(checkinData) {
    console.log(`🔑 Guest checked in: ${checkinData.guestName}`);

    try {
      // 1. Send arrival confirmation and room details
      await this.guestConcierge.sendArrivalConfirmation(checkinData);

      // 2. Activate local guide for immediate recommendations
      await this.localGuide.sendArrivalRecommendations(checkinData);

      // 3. Schedule satisfaction check-in (24 hours later)
      await this.scheduleTask('satisfaction_checkin', checkinData, 24 * 60 * 60 * 1000);

      // 4. Offer upsells based on length of stay
      if (checkinData.nights >= 2) {
        await this.localGuide.offerUpsells(checkinData);
      }

      console.log(`✅ Guest experience activated for ${checkinData.guestName}`);

    } catch (error) {
      console.error('Error handling check-in:', error);
    }
  }

  /**
   * Handle guest checkout - trigger post-stay engagement
   */
  async handleGuestCheckout(checkoutData) {
    console.log(`👋 Guest checked out: ${checkoutData.guestName}`);

    try {
      // 1. Send checkout confirmation
      await this.guestConcierge.sendCheckoutConfirmation(checkoutData);

      // 2. Send satisfaction survey
      await this.reviewManager.sendSatisfactionSurvey(checkoutData);

      // 3. Offer return booking incentive
      await this.bookingManager.offerReturnIncentive(checkoutData);

      // 4. Update guest profile with stay feedback
      await this.guestConcierge.updateGuestProfile(checkoutData);

      console.log(`✅ Post-stay engagement initiated for ${checkoutData.guestName}`);

    } catch (error) {
      console.error('Error handling checkout:', error);
    }
  }

  /**
   * Handle negative feedback - immediate service recovery
   */
  async handleNegativeFeedback(feedback) {
    console.log(`🚨 Negative feedback received: ${feedback.guestName}`);

    try {
      // 1. Immediate staff alert
      await this.alertStaff('negative_feedback', feedback);

      // 2. Personalized response from management
      await this.reviewManager.sendPersonalResponse(feedback);

      // 3. Offer service recovery if guest is still on property
      if (feedback.status === 'current_guest') {
        await this.guestConcierge.initiateServiceRecovery(feedback);
      }

      // 4. Schedule follow-up
      await this.scheduleTask('follow_up_negative_feedback', feedback, 48 * 60 * 60 * 1000);

      console.log(`✅ Service recovery initiated for ${feedback.guestName}`);

    } catch (error) {
      console.error('Error handling negative feedback:', error);
    }
  }

  /**
   * Daily operations coordinator
   */
  async runDailyOperations() {
    console.log('🌅 Running daily operations...');

    try {
      // Morning tasks
      await this.processMorningTasks();

      // Midday tasks
      setTimeout(() => this.processMiddayTasks(), 6 * 60 * 60 * 1000); // 6 hours

      // Evening tasks
      setTimeout(() => this.processEveningTasks(), 12 * 60 * 60 * 1000); // 12 hours

    } catch (error) {
      console.error('Error in daily operations:', error);
    }
  }

  async processMorningTasks() {
    console.log('🌅 Morning tasks started...');

    // Check today's arrivals
    const arrivals = await this.bookingManager.getTodayArrivals();

    for (const arrival of arrivals) {
      // Send arrival day messages
      await this.guestConcierge.sendArrivalDayMessage(arrival);

      // Prepare check-in instructions
      await this.checkinAutomation.prepareCheckinInstructions(arrival);
    }

    // Check weather and update recommendations
    const weather = await this.localGuide.updateWeatherBasedRecommendations();

    // Generate daily revenue report
    const report = await this.generateDailyReport();
    await this.sendReportToManagement(report);
  }

  async processMiddayTasks() {
    console.log('☀️ Midday tasks started...');

    // Check for early check-in requests
    await this.checkinAutomation.processEarlyCheckinRequests();

    // Send late checkout offers to departing guests
    await this.checkinAutomation.offerLateCheckout();

    // Follow up on unanswered guest inquiries
    await this.guestConcierge.followUpOnInquiries();
  }

  async processEveningTasks() {
    console.log('🌙 Evening tasks started...');

    // Send tomorrow's departure instructions
    const departures = await this.bookingManager.getTomorrowDepartures();

    for (const departure of departures) {
      await this.checkinAutomation.sendCheckoutInstructions(departure);
    }

    // Process review responses
    await this.reviewManager.processNewReviews();

    // Generate revenue analytics
    await this.localGuide.updateRevenueAnalytics();
  }

  /**
   * Real-time guest inquiry handler
   */
  async handleGuestInquiry(inquiry) {
    console.log(`💬 New guest inquiry: ${inquiry.channel}`);

    try {
      // Determine which agent should handle the inquiry
      const handler = this.routeInquiry(inquiry);

      let response;

      switch (handler) {
        case 'booking':
          response = await this.bookingManager.handleInquiry(inquiry.message, inquiry.metadata);
          break;

        case 'concierge':
          response = await this.guestConcierge.handleInquiry(inquiry.message, inquiry.guestContext);
          break;

        case 'checkin':
          response = await this.checkinAutomation.handleInquiry(inquiry.message, inquiry.guestContext);
          break;

        case 'guide':
          response = await this.localGuide.handleInquiry(inquiry.message, inquiry.guestContext);
          break;

        case 'reviews':
          response = await this.reviewManager.handleInquiry(inquiry.message, inquiry.guestContext);
          break;

        default:
          response = await this.guestConcierge.handleGeneralInquiry(inquiry.message);
      }

      // Send response via appropriate channel
      await this.sendResponse(inquiry.channel, response, inquiry.guestContact);

      // Log interaction for analytics
      await this.logInteraction(inquiry, response, handler);

      return response;

    } catch (error) {
      console.error('Error handling guest inquiry:', error);

      // Send fallback response
      await this.sendFallbackResponse(inquiry);
    }
  }

  /**
   * Route inquiries to appropriate agent based on content and context
   */
  routeInquiry(inquiry) {
    const message = inquiry.message.toLowerCase();
    const context = inquiry.guestContext;

    // Booking-related keywords
    if (message.includes('book') || message.includes('reserve') || message.includes('available')) {
      return 'booking';
    }

    // Check-in/out related
    if (message.includes('check') || message.includes('key') || message.includes('code') || message.includes('arrival')) {
      return 'checkin';
    }

    // Local recommendations
    if (message.includes('restaurant') || message.includes('tour') || message.includes('activity') || message.includes('recommend')) {
      return 'guide';
    }

    // Review/complaint related
    if (message.includes('complaint') || message.includes('problem') || message.includes('issue')) {
      return 'reviews';
    }

    // Default to concierge for general inquiries
    return 'concierge';
  }

  /**
   * Analytics and reporting
   */
  async generateDailyReport() {
    console.log('📊 Generating daily report...');

    const [
      bookingMetrics,
      guestMetrics,
      revenueMetrics,
      satisfactionMetrics
    ] = await Promise.all([
      this.bookingManager.getDailyMetrics(),
      this.guestConcierge.getDailyMetrics(),
      this.localGuide.getDailyRevenue(),
      this.reviewManager.getDailySatisfaction()
    ]);

    return {
      date: new Date().toISOString().split('T')[0],
      occupancy: bookingMetrics.occupancy,
      revenue: bookingMetrics.revenue + revenueMetrics.commissions,
      guestSatisfaction: satisfactionMetrics.averageScore,
      inquiriesHandled: guestMetrics.inquiriesHandled,
      upsellRevenue: revenueMetrics.upsells,
      checkinsCompleted: bookingMetrics.checkins,
      reviewsReceived: satisfactionMetrics.reviewsReceived,
      issues: satisfactionMetrics.issuesIdentified
    };
  }

  /**
   * Staff alert system
   */
  async alertStaff(type, data) {
    const alert = {
      type,
      timestamp: new Date(),
      data,
      urgency: this.calculateUrgency(type, data)
    };

    // Send via configured channels (email, SMS, Slack, etc.)
    await this.sendAlert(alert);
  }

  calculateUrgency(type, data) {
    const urgencyMap = {
      'negative_feedback': 'high',
      'booking_error': 'medium',
      'system_error': 'high',
      'guest_complaint': 'high',
      'payment_failed': 'medium',
      'maintenance_required': 'low'
    };

    return urgencyMap[type] || 'low';
  }

  /**
   * Revenue optimization engine
   */
  async optimizeRevenue() {
    console.log('💰 Running revenue optimization...');

    // Get current occupancy and demand
    const occupancy = await this.bookingManager.getCurrentOccupancy();
    const demand = await this.bookingManager.getDemandForecast();

    // Optimize pricing
    if (occupancy < 0.6 && demand.trend === 'declining') {
      await this.bookingManager.adjustPricing('decrease', 0.1);
    } else if (occupancy > 0.9 && demand.trend === 'increasing') {
      await this.bookingManager.adjustPricing('increase', 0.15);
    }

    // Optimize upsell strategies
    await this.localGuide.optimizeUpsellStrategies(occupancy, demand);

    // Optimize late checkout pricing
    await this.checkinAutomation.optimizeLateCheckoutPricing(occupancy);
  }

  /**
   * System health monitoring
   */
  async monitorSystemHealth() {
    const health = {
      timestamp: new Date(),
      agents: {
        booking: await this.bookingManager.healthCheck(),
        concierge: await this.guestConcierge.healthCheck(),
        checkin: await this.checkinAutomation.healthCheck(),
        guide: await this.localGuide.healthCheck(),
        reviews: await this.reviewManager.healthCheck()
      },
      integrations: await this.checkIntegrationHealth(),
      performance: await this.getPerformanceMetrics()
    };

    // Alert if any issues detected
    const issues = this.identifyHealthIssues(health);
    if (issues.length > 0) {
      await this.alertStaff('system_health', { issues, health });
    }

    return health;
  }

  /**
   * Start the complete system
   */
  async start() {
    console.log('🚀 Starting Hospitality Management System...');

    try {
      // Initialize all agents
      await Promise.all([
        this.bookingManager.start(),
        this.guestConcierge.start(),
        this.checkinAutomation.start(),
        this.localGuide.start(),
        this.reviewManager.start()
      ]);

      // Start daily operations
      this.runDailyOperations();

      // Start health monitoring
      setInterval(() => this.monitorSystemHealth(), 15 * 60 * 1000); // Every 15 minutes

      // Start revenue optimization
      setInterval(() => this.optimizeRevenue(), 60 * 60 * 1000); // Every hour

      console.log('✅ Hospitality Management System is running!');
      console.log('📊 Dashboard: http://localhost:3000');
      console.log('📱 WhatsApp: Ready for guest messages');
      console.log('📧 Email: Monitoring for inquiries');

    } catch (error) {
      console.error('Failed to start system:', error);
      process.exit(1);
    }
  }
}

// Example configuration
const config = {
  booking: {
    property: {
      name: "Fitzgerald's Guesthouse",
      rooms: 8,
      location: "Westport, Co. Mayo"
    },
    pricing: {
      base_rate: 85,
      dynamic_pricing: true
    }
  },
  concierge: {
    whatsapp: {
      enabled: true,
      number: "+353871234567"
    },
    email: {
      enabled: true,
      from: "concierge@fitzgeraldsguesthouse.ie"
    }
  },
  checkin: {
    smart_locks: {
      provider: "august",
      enabled: true
    },
    checkout: {
      late_fee: 20
    }
  },
  guide: {
    partnerships: {
      commission_target: 0.10
    },
    weather: {
      location: "Westport,IE"
    }
  },
  reviews: {
    platforms: ['booking_com', 'airbnb', 'google', 'tripadvisor'],
    response_time_target: 4
  }
};

// Start the system if run directly
if (require.main === module) {
  const system = new HospitalityManagementSystem(config);

  system.start().catch(error => {
    console.error('System startup failed:', error);
    process.exit(1);
  });

  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('🛑 Shutting down gracefully...');
    await system.shutdown();
    process.exit(0);
  });
}

module.exports = { HospitalityManagementSystem };