#!/usr/bin/env node

/**
 * Booking & Availability Manager
 * 24/7 Reservation Assistant for B&B/Guesthouse
 */

const { ChatOpenAI } = require('@langchain/openai');
const { PromptTemplate } = require('@langchain/core/prompts');
const { ConversationChain } = require('langchain/chains');
const { BufferMemory } = require('langchain/memory');
const express = require('express');
const moment = require('moment');
const axios = require('axios');

class BookingManager {
  constructor(config) {
    this.config = config;
    this.llm = new ChatOpenAI({
      modelName: 'gpt-4',
      temperature: 0.7
    });

    this.memory = new BufferMemory();
    this.availabilityEngine = new AvailabilityEngine(config);
    this.pricingOptimizer = new PricingOptimizer(config);
    this.bookingProcessor = new BookingProcessor(config);

    this.setupPromptTemplate();
    this.setupConversationChain();
  }

  setupPromptTemplate() {
    this.promptTemplate = PromptTemplate.fromTemplate(`
You are the Booking Manager for ${this.config.property.name}, a charming ${this.config.property.rooms}-room B&B.

Your role:
- Respond to booking inquiries instantly and professionally
- Check availability and provide accurate pricing
- Process bookings with deposit collection
- Offer alternatives when fully booked
- Upsell premium rooms and packages

Current context:
- Property: ${this.config.property.name}
- Rooms available: {available_rooms}
- Today: {current_date}
- Pricing strategy: Dynamic based on demand

Guest inquiry: {input}
Previous conversation: {history}

Guidelines:
- Be warm, professional, and helpful
- Always confirm dates and guest count
- Explain deposit requirements clearly
- Offer alternatives if unavailable
- Include payment links for bookings
- Mention local attractions briefly

Response:
`);
  }

  setupConversationChain() {
    this.chain = new ConversationChain({
      llm: this.llm,
      prompt: this.promptTemplate,
      memory: this.memory
    });
  }

  async handleInquiry(inquiry, metadata = {}) {
    try {
      // Extract booking dates and details
      const bookingDetails = await this.extractBookingDetails(inquiry);

      // Check availability
      const availability = await this.availabilityEngine.checkAvailability(
        bookingDetails.checkIn,
        bookingDetails.checkOut,
        bookingDetails.rooms
      );

      // Get current context
      const context = {
        available_rooms: availability.roomsLeft,
        current_date: moment().format('YYYY-MM-DD'),
        input: inquiry,
        booking_details: bookingDetails,
        availability: availability
      };

      // Generate response
      const response = await this.chain.call(context);

      // Log interaction
      await this.logInquiry(inquiry, response.response, metadata);

      return {
        response: response.response,
        booking_details: bookingDetails,
        availability: availability,
        followUp: this.generateFollowUpActions(bookingDetails, availability)
      };

    } catch (error) {
      console.error('Error handling inquiry:', error);
      return {
        response: "I apologize, but I'm experiencing technical difficulties. Please try again in a moment or contact us directly at +353 1 234 5678.",
        error: true
      };
    }
  }

  async extractBookingDetails(inquiry) {
    const extractionPrompt = `
Extract booking details from this inquiry: "${inquiry}"

Return JSON with:
- checkIn: date (YYYY-MM-DD) or null
- checkOut: date (YYYY-MM-DD) or null
- guests: number or null
- rooms: number or 1
- flexible: boolean (if dates are flexible)
- purpose: string (business, leisure, celebration, etc.)

Example:
{"checkIn": "2024-03-15", "checkOut": "2024-03-17", "guests": 2, "rooms": 1, "flexible": false, "purpose": "leisure"}

Only return valid JSON:
`;

    try {
      const result = await this.llm.call([{ role: 'user', content: extractionPrompt }]);
      return JSON.parse(result.content);
    } catch (error) {
      console.error('Error extracting booking details:', error);
      return {
        checkIn: null,
        checkOut: null,
        guests: null,
        rooms: 1,
        flexible: false,
        purpose: 'leisure'
      };
    }
  }

  generateFollowUpActions(bookingDetails, availability) {
    const actions = [];

    if (bookingDetails.checkIn && availability.available) {
      actions.push({
        type: 'send_booking_link',
        data: {
          checkIn: bookingDetails.checkIn,
          checkOut: bookingDetails.checkOut,
          price: availability.price
        }
      });
    }

    if (!availability.available) {
      actions.push({
        type: 'offer_alternatives',
        data: {
          originalDates: [bookingDetails.checkIn, bookingDetails.checkOut],
          guestCount: bookingDetails.guests
        }
      });
    }

    if (bookingDetails.purpose === 'celebration') {
      actions.push({
        type: 'offer_celebration_package',
        data: {
          type: bookingDetails.purpose
        }
      });
    }

    return actions;
  }

  async logInquiry(inquiry, response, metadata) {
    const log = {
      timestamp: new Date(),
      inquiry,
      response,
      metadata,
      source: metadata.channel || 'unknown'
    };

    // Log to database or file
    console.log('Booking inquiry logged:', log);
  }
}

class AvailabilityEngine {
  constructor(config) {
    this.config = config;
    this.bookings = new Map(); // In production, use database
  }

  async checkAvailability(checkIn, checkOut, rooms = 1) {
    if (!checkIn || !checkOut) {
      return {
        available: false,
        roomsLeft: 0,
        price: 0,
        reason: 'Invalid dates'
      };
    }

    const startDate = moment(checkIn);
    const endDate = moment(checkOut);
    const nights = endDate.diff(startDate, 'days');

    if (nights <= 0) {
      return {
        available: false,
        roomsLeft: 0,
        price: 0,
        reason: 'Invalid date range'
      };
    }

    // Check each night for availability
    let minAvailable = this.config.property.rooms;

    for (let date = startDate.clone(); date.isBefore(endDate); date.add(1, 'day')) {
      const dateStr = date.format('YYYY-MM-DD');
      const bookingsForDate = this.getBookingsForDate(dateStr);
      const availableRooms = this.config.property.rooms - bookingsForDate.length;
      minAvailable = Math.min(minAvailable, availableRooms);
    }

    const available = minAvailable >= rooms;
    const price = await this.pricingOptimizer.calculatePrice(checkIn, checkOut, rooms);

    return {
      available,
      roomsLeft: minAvailable,
      price,
      nights,
      total: price * nights * rooms
    };
  }

  getBookingsForDate(date) {
    return this.bookings.get(date) || [];
  }

  async addBooking(booking) {
    const startDate = moment(booking.checkIn);
    const endDate = moment(booking.checkOut);

    for (let date = startDate.clone(); date.isBefore(endDate); date.add(1, 'day')) {
      const dateStr = date.format('YYYY-MM-DD');
      if (!this.bookings.has(dateStr)) {
        this.bookings.set(dateStr, []);
      }
      this.bookings.get(dateStr).push(booking);
    }
  }
}

class PricingOptimizer {
  constructor(config) {
    this.config = config;
    this.baseRate = config.pricing.base_rate;
  }

  async calculatePrice(checkIn, checkOut, rooms) {
    const date = moment(checkIn);
    let rate = this.baseRate;

    // Weekend premium (Friday/Saturday)
    if ([5, 6].includes(date.day())) {
      rate *= 1.2;
    }

    // Advance booking discount
    const daysUntilArrival = date.diff(moment(), 'days');
    if (daysUntilArrival > 30) {
      rate *= 0.95; // 5% early bird discount
    } else if (daysUntilArrival < 3) {
      rate *= 1.15; // 15% last-minute premium
    }

    // Seasonal adjustments
    const month = date.month();
    if ([5, 6, 7, 8].includes(month)) { // Summer premium
      rate *= 1.3;
    } else if ([11, 0, 1].includes(month)) { // Winter discount
      rate *= 0.8;
    }

    // Local events (mock data)
    const hasLocalEvent = await this.checkLocalEvents(checkIn);
    if (hasLocalEvent) {
      rate *= 1.4;
    }

    // Apply limits
    rate = Math.max(this.config.pricing.minimum_rate, rate);
    rate = Math.min(this.config.pricing.maximum_rate, rate);

    return Math.round(rate);
  }

  async checkLocalEvents(date) {
    // Mock event checker - in production, integrate with local event APIs
    const eventDates = [
      '2024-03-17', // St. Patrick's Day
      '2024-07-15', // Local festival
      '2024-08-01', // Summer festival
      '2024-12-31'  // New Year's Eve
    ];

    return eventDates.includes(moment(date).format('YYYY-MM-DD'));
  }
}

class BookingProcessor {
  constructor(config) {
    this.config = config;
  }

  async processBooking(bookingData) {
    try {
      // Generate booking reference
      const reference = this.generateReference();

      // Calculate pricing
      const total = bookingData.price * bookingData.nights * bookingData.rooms;
      const deposit = Math.round(total * 0.25);

      // Create booking record
      const booking = {
        reference,
        ...bookingData,
        total,
        deposit,
        status: 'pending_deposit',
        created: new Date()
      };

      // Generate payment link
      const paymentLink = await this.generatePaymentLink(deposit, reference);

      // Send confirmation email
      await this.sendBookingConfirmation(booking, paymentLink);

      return {
        success: true,
        reference,
        paymentLink,
        booking
      };

    } catch (error) {
      console.error('Error processing booking:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  generateReference() {
    const prefix = this.config.property.name.substring(0, 3).toUpperCase();
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.random().toString(36).substring(2, 5).toUpperCase();

    return `${prefix}${timestamp}${random}`;
  }

  async generatePaymentLink(amount, reference) {
    // Mock payment link generation
    // In production, integrate with Stripe, PayPal, or local payment processor
    return `https://pay.fitzgeraldsguesthouse.ie/book/${reference}?amount=${amount}`;
  }

  async sendBookingConfirmation(booking, paymentLink) {
    // Mock email sending
    // In production, integrate with email service
    console.log(`Booking confirmation sent for ${booking.reference}`);
    console.log(`Payment link: ${paymentLink}`);
  }
}

// Express server for webhook endpoints
const app = express();
app.use(express.json());

// Initialize booking manager
const config = {
  property: {
    name: "Fitzgerald's Guesthouse",
    rooms: 8,
    check_in: "15:00",
    check_out: "11:00"
  },
  pricing: {
    base_rate: 85,
    minimum_rate: 65,
    maximum_rate: 150,
    dynamic_pricing: true
  }
};

const bookingManager = new BookingManager(config);

// Webhook endpoints
app.post('/booking-inquiry', async (req, res) => {
  try {
    const { message, metadata } = req.body;
    const result = await bookingManager.handleInquiry(message, metadata);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/process-booking', async (req, res) => {
  try {
    const result = await bookingManager.bookingProcessor.processBooking(req.body);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/availability', async (req, res) => {
  try {
    const { checkIn, checkOut, rooms = 1 } = req.query;
    const availability = await bookingManager.availabilityEngine.checkAvailability(
      checkIn,
      checkOut,
      parseInt(rooms)
    );
    res.json(availability);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'booking-manager',
    timestamp: new Date().toISOString()
  });
});

// Start server if run directly
if (require.main === module) {
  const PORT = process.env.PORT || 3001;
  app.listen(PORT, () => {
    console.log(`🏨 Booking Manager running on port ${PORT}`);
    console.log(`📅 Managing ${config.property.rooms} rooms at ${config.property.name}`);
  });
}

module.exports = { BookingManager, AvailabilityEngine, PricingOptimizer, BookingProcessor };