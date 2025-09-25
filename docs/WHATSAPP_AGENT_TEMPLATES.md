# WhatsApp Business AI Agent Templates

Complete guide with ready-to-use templates for WhatsApp Business integration.

## 🚀 Quick Setup Guide

### Step 1: WhatsApp Business API Setup (15 minutes)

```bash
# Option 1: Meta WhatsApp Business API (Official)
# 1. Go to developers.facebook.com
# 2. Create Business App
# 3. Add WhatsApp Product
# 4. Get Phone Number ID and Access Token

# Option 2: Third-party providers (Easier)
# - Twilio: $0.005 per message
# - MessageBird: €0.0045 per message
# - Vonage: $0.0057 per message
```

### Step 2: Webhook Setup

```javascript
// webhook.js - Express.js webhook handler
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

// WhatsApp webhook verification
app.get('/webhook', (req, res) => {
  const VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN;
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode && token === VERIFY_TOKEN) {
    res.status(200).send(challenge);
  } else {
    res.sendStatus(403);
  }
});

// Handle incoming messages
app.post('/webhook', async (req, res) => {
  const body = req.body;

  if (body.object === 'whatsapp_business_account') {
    body.entry?.forEach(entry => {
      entry.changes?.forEach(change => {
        if (change.field === 'messages') {
          const message = change.value.messages?.[0];
          if (message) {
            handleMessage(message, change.value);
          }
        }
      });
    });
    res.status(200).send('EVENT_RECEIVED');
  } else {
    res.sendStatus(404);
  }
});

async function handleMessage(message, metadata) {
  const from = message.from;
  const text = message.text?.body;
  const phoneNumberId = metadata.metadata.phone_number_id;

  // Route to appropriate bot template
  const response = await generateResponse(text, from);
  await sendMessage(phoneNumberId, from, response);
}

async function sendMessage(phoneNumberId, to, text) {
  const accessToken = process.env.WHATSAPP_ACCESS_TOKEN;

  await axios.post(`https://graph.facebook.com/v17.0/${phoneNumberId}/messages`, {
    messaging_product: 'whatsapp',
    to: to,
    text: { body: text }
  }, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
}

app.listen(process.env.PORT || 3000);
```

## 📋 5 Ready-to-Use Bot Templates

### 1. Restaurant Booking Bot

```javascript
// restaurant-bot.js
class RestaurantBot {
  constructor() {
    this.conversations = new Map();
  }

  async handleMessage(phone, message) {
    const state = this.conversations.get(phone) || { step: 'welcome' };

    switch (state.step) {
      case 'welcome':
        this.conversations.set(phone, { step: 'menu' });
        return `🍕 Welcome to Mario's Pizza!

Choose an option:
1️⃣ View Menu
2️⃣ Make Reservation
3️⃣ Order Delivery
4️⃣ Contact Info

Reply with a number (1-4)`;

      case 'menu':
        if (message === '1') {
          return `📋 **MENU**

🍕 **PIZZAS**
- Margherita: €12
- Pepperoni: €14
- Quattro Stagioni: €16

🥗 **SALADS**
- Caesar: €8
- Greek: €9

Reply *ORDER* to place order or *BACK* for main menu`;
        }

        if (message === '2') {
          this.conversations.set(phone, { step: 'booking_date' });
          return `📅 **RESERVATION**

What date would you like?
Please use format: DD/MM/YYYY

Example: 25/12/2024`;
        }

        if (message === '3') {
          this.conversations.set(phone, { step: 'delivery_address' });
          return `🚚 **DELIVERY**

Please provide your full address:

Example: Via Roma 123, Milano 20121`;
        }

        return "Please reply with 1, 2, 3, or 4";

      case 'booking_date':
        if (this.isValidDate(message)) {
          state.date = message;
          state.step = 'booking_time';
          this.conversations.set(phone, state);
          return `⏰ **TIME SELECTION**

Available times for ${message}:
- 19:00
- 19:30
- 20:00
- 20:30
- 21:00

Which time works for you?`;
        }
        return "Please use date format DD/MM/YYYY";

      case 'booking_time':
        state.time = message;
        state.step = 'booking_guests';
        this.conversations.set(phone, state);
        return `👥 **PARTY SIZE**

How many guests will be dining?`;

      case 'booking_guests':
        const guests = parseInt(message);
        if (guests > 0 && guests <= 10) {
          this.conversations.delete(phone); // Reset conversation

          // Here you would save to your booking system
          await this.saveBooking(phone, state.date, state.time, guests);

          return `✅ **BOOKING CONFIRMED**

📅 Date: ${state.date}
⏰ Time: ${state.time}
👥 Guests: ${guests}
📱 Phone: ${phone}

We'll send a reminder 1 day before.
Thank you for choosing Mario's Pizza! 🍕`;
        }
        return "Please enter number of guests (1-10)";
    }
  }

  isValidDate(dateStr) {
    const regex = /^\d{2}\/\d{2}\/\d{4}$/;
    return regex.test(dateStr);
  }

  async saveBooking(phone, date, time, guests) {
    // Integration with your booking system
    console.log('New booking:', { phone, date, time, guests });
  }
}

module.exports = RestaurantBot;
```

### 2. Hair Salon Booking Bot

```javascript
// salon-bot.js
class SalonBot {
  constructor() {
    this.conversations = new Map();
    this.services = {
      '1': { name: 'Haircut', price: 25, duration: 45 },
      '2': { name: 'Hair Color', price: 65, duration: 120 },
      '3': { name: 'Highlights', price: 85, duration: 150 },
      '4': { name: 'Blowdry', price: 15, duration: 30 },
      '5': { name: 'Hair Treatment', price: 45, duration: 60 }
    };
  }

  async handleMessage(phone, message) {
    const state = this.conversations.get(phone) || { step: 'welcome' };

    switch (state.step) {
      case 'welcome':
        this.conversations.set(phone, { step: 'service_selection' });
        return `💇‍♀️ Welcome to Bella Hair Salon!

**OUR SERVICES:**
1️⃣ Haircut - €25 (45min)
2️⃣ Hair Color - €65 (2hrs)
3️⃣ Highlights - €85 (2.5hrs)
4️⃣ Blowdry - €15 (30min)
5️⃣ Hair Treatment - €45 (1hr)

Which service interests you? Reply with number (1-5)`;

      case 'service_selection':
        const service = this.services[message];
        if (service) {
          state.service = service;
          state.step = 'stylist_selection';
          this.conversations.set(phone, state);

          return `✨ Great choice! **${service.name}**

👩‍🎨 **CHOOSE YOUR STYLIST:**

1️⃣ Maria - Senior Stylist (5+ years)
2️⃣ Sofia - Junior Stylist (2+ years)
3️⃣ No preference

Who would you prefer?`;
        }
        return "Please choose a service number (1-5)";

      case 'stylist_selection':
        const stylists = { '1': 'Maria', '2': 'Sofia', '3': 'Any available' };
        const stylist = stylists[message];

        if (stylist) {
          state.stylist = stylist;
          state.step = 'date_selection';
          this.conversations.set(phone, state);

          return `📅 **AVAILABLE DATES**

This week:
🟢 Today - Available
🟢 Tomorrow - Available
🟡 Thursday - Limited slots
🟢 Friday - Available
🔴 Saturday - Fully booked

Reply with your preferred day or specific date (DD/MM)`;
        }
        return "Please choose 1, 2, or 3";

      case 'date_selection':
        // Simplified - in reality you'd check actual availability
        state.date = message;
        state.step = 'time_selection';
        this.conversations.set(phone, state);

        return `⏰ **AVAILABLE TIMES for ${message}**

🟢 09:00 - Available
🟢 11:00 - Available
🟡 14:00 - Available
🟢 16:00 - Available

Which time works for you?`;

      case 'time_selection':
        state.time = message;
        state.step = 'confirmation';
        this.conversations.set(phone, state);

        return `📋 **BOOKING SUMMARY**

💇‍♀️ Service: ${state.service.name}
💰 Price: €${state.service.price}
⏱️ Duration: ${state.service.duration} minutes
👩‍🎨 Stylist: ${state.stylist}
📅 Date: ${state.date}
⏰ Time: ${state.time}

Reply *CONFIRM* to book or *CHANGE* to modify`;

      case 'confirmation':
        if (message.toLowerCase() === 'confirm') {
          this.conversations.delete(phone);
          await this.saveBooking(phone, state);

          return `✅ **BOOKING CONFIRMED!**

Your appointment is set!

📱 You'll receive a reminder 24hrs before
🗓️ Need to reschedule? Reply *RESCHEDULE*
📍 Address: Via Fashion 45, Milano

Thank you for choosing Bella Hair Salon! 💕`;
        }
        return "Reply CONFIRM to complete booking";
    }
  }

  async saveBooking(phone, bookingData) {
    // Save to your booking system
    console.log('New salon booking:', phone, bookingData);
  }
}

module.exports = SalonBot;
```

### 3. Customer Support Bot

```javascript
// support-bot.js
class SupportBot {
  constructor() {
    this.conversations = new Map();
    this.tickets = new Map();
  }

  async handleMessage(phone, message) {
    const state = this.conversations.get(phone) || { step: 'welcome' };

    switch (state.step) {
      case 'welcome':
        this.conversations.set(phone, { step: 'issue_type' });
        return `🎧 **Customer Support**

How can we help you today?

1️⃣ Technical Issue
2️⃣ Billing Question
3️⃣ Product Information
4️⃣ Return/Refund
5️⃣ Track My Order
6️⃣ Speak to Human Agent

Please reply with a number (1-6)`;

      case 'issue_type':
        const issueTypes = {
          '1': 'Technical Issue',
          '2': 'Billing Question',
          '3': 'Product Information',
          '4': 'Return/Refund',
          '5': 'Order Tracking',
          '6': 'Human Agent'
        };

        const issueType = issueTypes[message];
        if (!issueType) {
          return "Please choose a number between 1-6";
        }

        if (message === '5') {
          state.step = 'order_tracking';
          this.conversations.set(phone, state);
          return `📦 **ORDER TRACKING**

Please provide your order number:

Format: #12345 or ORD12345`;
        }

        if (message === '6') {
          const ticketId = this.createTicket(phone, 'Human Agent Request');
          this.conversations.delete(phone);
          return `👨‍💼 **AGENT REQUESTED**

Ticket #${ticketId} created
⏱️ Estimated wait time: 15-20 minutes
📱 An agent will contact you shortly

In the meantime, you can describe your issue in detail.`;
        }

        state.issueType = issueType;
        state.step = 'issue_description';
        this.conversations.set(phone, state);

        return `📝 **${issueType.toUpperCase()}**

Please describe your issue in detail:

The more information you provide, the better we can help you!`;

      case 'order_tracking':
        const orderNum = message.replace(/[#\s]/g, '');
        // In reality, check your order system
        const orderStatus = await this.checkOrderStatus(orderNum);

        this.conversations.delete(phone);
        return `📦 **ORDER STATUS: ${orderNum}**

${orderStatus}

Need more help? Reply *SUPPORT* anytime!`;

      case 'issue_description':
        const ticketId = this.createTicket(phone, state.issueType, message);
        this.conversations.delete(phone);

        // Auto-response for common issues
        let autoResponse = this.getAutoResponse(state.issueType, message);

        return `🎫 **TICKET #${ticketId} CREATED**

${autoResponse}

If this doesn't solve your issue:
⏱️ Our team will respond within 2-4 hours
📧 Updates will be sent via WhatsApp
📞 For urgent issues, call: +39 02 1234 5678`;
    }
  }

  createTicket(phone, type, description = '') {
    const ticketId = Math.random().toString(36).substr(2, 9).toUpperCase();
    this.tickets.set(ticketId, {
      phone,
      type,
      description,
      status: 'open',
      created: new Date()
    });
    return ticketId;
  }

  async checkOrderStatus(orderNum) {
    // Mock order tracking - replace with real API
    const statuses = [
      '✅ **DELIVERED** - Delivered yesterday at 14:30',
      '🚛 **IN TRANSIT** - Expected delivery: Tomorrow by 18:00',
      '📦 **PREPARING** - Being packed at warehouse',
      '❌ **ORDER NOT FOUND** - Please check order number'
    ];
    return statuses[Math.floor(Math.random() * statuses.length)];
  }

  getAutoResponse(issueType, description) {
    const responses = {
      'Technical Issue': `🔧 **QUICK FIXES TO TRY:**

1. Restart your device
2. Check internet connection
3. Update the app to latest version
4. Clear app cache

Try these steps first!`,

      'Billing Question': `💳 **BILLING INFO:**

📧 Invoices sent to your email
💰 Refunds take 3-5 business days
🔄 Auto-renewal can be disabled in settings
📞 For urgent billing: +39 02 1234 5678`,

      'Product Information': `📋 **PRODUCT HELP:**

🔍 Full specifications on our website
📱 User manuals in the app
🎥 Tutorial videos available
💬 Product reviews from other customers`,

      'Return/Refund': `↩️ **RETURN PROCESS:**

✅ 30-day return policy
📦 Keep original packaging
🏷️ Return label will be emailed
💰 Refund within 7 business days after return`
    };

    return responses[issueType] || 'Our team will review your request shortly.';
  }
}

module.exports = SupportBot;
```

### 4. Lead Generation Bot

```javascript
// lead-bot.js
class LeadBot {
  constructor() {
    this.conversations = new Map();
    this.leads = new Map();
  }

  async handleMessage(phone, message) {
    const state = this.conversations.get(phone) || { step: 'welcome' };

    switch (state.step) {
      case 'welcome':
        this.conversations.set(phone, { step: 'interest' });
        return `🚀 **Welcome to TechSolutions!**

We help businesses grow with AI & automation.

What interests you most?

1️⃣ AI Chatbots
2️⃣ Process Automation
3️⃣ Data Analytics
4️⃣ Custom Software
5️⃣ Free Consultation

Reply with a number (1-5)`;

      case 'interest':
        const interests = {
          '1': 'AI Chatbots',
          '2': 'Process Automation',
          '3': 'Data Analytics',
          '4': 'Custom Software',
          '5': 'Free Consultation'
        };

        const interest = interests[message];
        if (!interest) {
          return "Please choose 1, 2, 3, 4, or 5";
        }

        state.interest = interest;

        if (message === '5') {
          state.step = 'consultation_type';
          this.conversations.set(phone, state);
          return `📞 **FREE CONSULTATION**

Choose consultation type:

1️⃣ 15-min Phone Call
2️⃣ 30-min Video Meeting
3️⃣ In-Person Meeting (Milano area)
4️⃣ WhatsApp Chat Session

What works best for you?`;
        }

        state.step = 'company_info';
        this.conversations.set(phone, state);
        return `💼 **${interest.toUpperCase()}**

Great choice! We've helped 200+ companies with ${interest.toLowerCase()}.

What's your company name?`;

      case 'consultation_type':
        const consultationTypes = {
          '1': '15-min Phone Call',
          '2': '30-min Video Meeting',
          '3': 'In-Person Meeting',
          '4': 'WhatsApp Chat Session'
        };

        state.consultationType = consultationTypes[message];
        state.step = 'company_info';
        this.conversations.set(phone, state);

        return `📋 **CONSULTATION DETAILS**

Type: ${state.consultationType}

To schedule your FREE consultation, I need some quick info:

What's your company name?`;

      case 'company_info':
        state.company = message;
        state.step = 'role_info';
        this.conversations.set(phone, state);

        return `👋 Nice to meet you, ${message}!

What's your role there?

Examples:
- CEO/Founder
- IT Manager
- Operations Manager
- Marketing Director
- Other`;

      case 'role_info':
        state.role = message;
        state.step = 'company_size';
        this.conversations.set(phone, state);

        return `🏢 **COMPANY SIZE**

How many employees does ${state.company} have?

1️⃣ 1-10 (Small business)
2️⃣ 11-50 (Medium business)
3️⃣ 51-200 (Large business)
4️⃣ 200+ (Enterprise)

Reply with number (1-4)`;

      case 'company_size':
        const sizes = {
          '1': '1-10 employees',
          '2': '11-50 employees',
          '3': '51-200 employees',
          '4': '200+ employees'
        };

        state.companySize = sizes[message];
        if (!state.companySize) {
          return "Please choose 1, 2, 3, or 4";
        }

        state.step = 'current_challenges';
        this.conversations.set(phone, state);

        return `🎯 **CURRENT CHALLENGES**

What's the biggest challenge ${state.company} faces right now?

Common challenges:
• Too much manual work
• Poor customer response times
• Data scattered everywhere
• Repetitive tasks taking forever
• Need better insights from data

Describe in your own words:`;

      case 'current_challenges':
        state.challenges = message;
        state.step = 'timeline';
        this.conversations.set(phone, state);

        return `⏰ **PROJECT TIMELINE**

When would you like to start addressing this?

1️⃣ ASAP (This month)
2️⃣ Within 2-3 months
3️⃣ Within 6 months
4️⃣ Just exploring options

Reply with number (1-4)`;

      case 'timeline':
        const timelines = {
          '1': 'ASAP (This month)',
          '2': 'Within 2-3 months',
          '3': 'Within 6 months',
          '4': 'Just exploring'
        };

        state.timeline = timelines[message];
        state.step = 'budget';
        this.conversations.set(phone, state);

        return `💰 **BUDGET RANGE** (Optional)

What budget range are you considering?

1️⃣ Under €5,000
2️⃣ €5,000 - €15,000
3️⃣ €15,000 - €50,000
4️⃣ €50,000+
5️⃣ Not sure yet

Reply with number or *SKIP*`;

      case 'budget':
        const budgets = {
          '1': 'Under €5,000',
          '2': '€5,000 - €15,000',
          '3': '€15,000 - €50,000',
          '4': '€50,000+',
          '5': 'Not determined'
        };

        if (message.toLowerCase() === 'skip') {
          state.budget = 'Not specified';
        } else {
          state.budget = budgets[message] || 'Not specified';
        }

        // Save lead and send summary
        const leadId = await this.saveLead(phone, state);
        this.conversations.delete(phone);

        return `✅ **THANK YOU ${state.company.toUpperCase()}!**

📋 **YOUR INFO:**
🏢 Company: ${state.company}
👤 Role: ${state.role}
📊 Size: ${state.companySize}
🎯 Interest: ${state.interest}
⏰ Timeline: ${state.timeline}
💰 Budget: ${state.budget}

🎯 **NEXT STEPS:**
📞 Our specialist will call within 24 hours
📧 Custom proposal sent within 48 hours
🎁 FREE audit of your current processes

Questions? Reply anytime!

Lead ID: #${leadId}`;
    }
  }

  async saveLead(phone, leadData) {
    const leadId = Math.random().toString(36).substr(2, 9).toUpperCase();

    this.leads.set(leadId, {
      phone,
      ...leadData,
      created: new Date(),
      status: 'new'
    });

    // In reality, save to CRM or send notification
    console.log('New lead generated:', leadId, leadData);

    return leadId;
  }
}

module.exports = LeadBot;
```

### 5. Information/FAQ Bot

```javascript
// info-bot.js
class InfoBot {
  constructor() {
    this.faq = {
      hours: `🕐 **OPENING HOURS**

Monday-Friday: 9:00-18:00
Saturday: 9:00-17:00
Sunday: 11:00-16:00

📍 Holiday hours may vary`,

      location: `📍 **OUR LOCATION**

Via Milano 123
20121 Milano, Italy

🚗 Parking available
🚇 Metro: Duomo (2 min walk)
🚌 Bus: Lines 54, 61, 94`,

      contact: `📞 **CONTACT INFO**

📱 WhatsApp: This number!
☎️ Phone: +39 02 1234 5678
📧 Email: info@company.com
🌐 Website: www.company.com

💬 WhatsApp is fastest for quick questions!`,

      prices: `💰 **PRICING**

⭐ **BASIC PACKAGE**
€29/month
- Feature A
- Feature B
- Email support

🚀 **PRO PACKAGE**
€59/month
- Everything in Basic
- Feature C
- Feature D
- Priority support

💎 **ENTERPRISE**
Custom pricing
- All features
- Dedicated support
- Custom integrations

💬 Reply *QUOTE* for personalized pricing`,

      services: `🛠️ **OUR SERVICES**

✅ Service 1 - Brief description
✅ Service 2 - Brief description
✅ Service 3 - Brief description
✅ Service 4 - Brief description

📋 **PROCESS:**
1. Free consultation
2. Custom proposal
3. Implementation
4. Training & support

💬 Reply *CONSULT* to start`
    };

    this.keywords = {
      // Hours-related keywords
      'hours': 'hours', 'open': 'hours', 'closed': 'hours',
      'time': 'hours', 'when': 'hours', 'schedule': 'hours',

      // Location-related
      'where': 'location', 'address': 'location', 'location': 'location',
      'directions': 'location', 'parking': 'location', 'metro': 'location',

      // Contact-related
      'contact': 'contact', 'phone': 'contact', 'email': 'contact',
      'call': 'contact', 'reach': 'contact', 'talk': 'contact',

      // Price-related
      'price': 'prices', 'cost': 'prices', 'pricing': 'prices',
      'how much': 'prices', 'fees': 'prices', 'quote': 'prices',

      // Service-related
      'services': 'services', 'what do you': 'services', 'offer': 'services',
      'help': 'services', 'do': 'services'
    };
  }

  async handleMessage(phone, message) {
    const lowerMessage = message.toLowerCase();

    // Check for specific commands
    if (lowerMessage.includes('menu') || lowerMessage === 'help' || lowerMessage === 'start') {
      return this.getMainMenu();
    }

    // Check for FAQ keywords
    const faqKey = this.findFAQMatch(lowerMessage);
    if (faqKey) {
      return this.faq[faqKey] + '\n\n💬 More questions? Reply *MENU* for options';
    }

    // Smart contextual responses
    if (lowerMessage.includes('book') || lowerMessage.includes('appointment')) {
      return `📅 **BOOKING**

To book an appointment:
1️⃣ Call us: +39 02 1234 5678
2️⃣ WhatsApp: Reply *BOOK*
3️⃣ Online: www.company.com/book
4️⃣ Walk-in (subject to availability)

Prefer WhatsApp booking? Reply *BOOK*`;
    }

    if (lowerMessage.includes('emergency') || lowerMessage.includes('urgent')) {
      return `🚨 **URGENT/EMERGENCY**

For urgent matters:
📞 Call immediately: +39 02 1234 5678
⏰ Available 24/7 for emergencies

For non-urgent questions, continue chatting here!`;
    }

    // Default response with suggestions
    return `🤖 I'm here to help!

Popular questions:
💬 *HOURS* - Opening hours
💬 *LOCATION* - Address & directions
💬 *PRICES* - Service pricing
💬 *SERVICES* - What we offer
💬 *CONTACT* - Contact information
💬 *MENU* - See all options

Or just type your question naturally!`;
  }

  findFAQMatch(message) {
    // Direct keyword matches
    for (const [keyword, faqKey] of Object.entries(this.keywords)) {
      if (message.includes(keyword)) {
        return faqKey;
      }
    }

    // Fuzzy matching for common variations
    if (message.match(/what.*(time|hour)/)) return 'hours';
    if (message.match(/where.*(you|located)/)) return 'location';
    if (message.match(/how.*(much|cost)/)) return 'prices';

    return null;
  }

  getMainMenu() {
    return `📋 **MAIN MENU**

Quick info:
1️⃣ Opening Hours
2️⃣ Location & Directions
3️⃣ Contact Information
4️⃣ Services & What We Do
5️⃣ Pricing Information
6️⃣ Book Appointment
7️⃣ Talk to Human

💬 Reply with number (1-7) or ask any question!

Examples:
• "What time do you open?"
• "Where are you located?"
• "How much does it cost?"
• "What services do you offer?"`;
  }
}

module.exports = InfoBot;
```

## 🔗 Integration Code

### Main Bot Router

```javascript
// bot-router.js - Routes messages to appropriate bots
const RestaurantBot = require('./restaurant-bot');
const SalonBot = require('./salon-bot');
const SupportBot = require('./support-bot');
const LeadBot = require('./lead-bot');
const InfoBot = require('./info-bot');

class BotRouter {
  constructor() {
    // Initialize bots based on your business type
    this.bots = {
      restaurant: new RestaurantBot(),
      salon: new SalonBot(),
      support: new SupportBot(),
      lead: new LeadBot(),
      info: new InfoBot()
    };

    // Default bot (change based on your primary business)
    this.defaultBot = 'info';

    // User preferences (persist in database)
    this.userPreferences = new Map();
  }

  async handleMessage(phone, message, context = {}) {
    // Detect intent or use user preference
    const botType = this.detectBotType(message, phone) || this.defaultBot;
    const bot = this.bots[botType];

    if (!bot) {
      return "Sorry, I didn't understand. Reply *HELP* for options.";
    }

    try {
      const response = await bot.handleMessage(phone, message, context);
      return response;
    } catch (error) {
      console.error('Bot error:', error);
      return "Sorry, something went wrong. Please try again or contact support.";
    }
  }

  detectBotType(message, phone) {
    const lowerMessage = message.toLowerCase();

    // Keyword-based detection
    if (lowerMessage.match(/(book|reservation|table|menu|food|pizza|restaurant)/)) {
      return 'restaurant';
    }

    if (lowerMessage.match(/(haircut|salon|stylist|color|highlights|appointment)/)) {
      return 'salon';
    }

    if (lowerMessage.match(/(support|help|problem|issue|broken|bug|ticket)/)) {
      return 'support';
    }

    if (lowerMessage.match(/(quote|consultation|business|company|service|price)/)) {
      return 'lead';
    }

    // Check user preference
    return this.userPreferences.get(phone);
  }

  setUserPreference(phone, botType) {
    this.userPreferences.set(phone, botType);
  }
}

module.exports = BotRouter;
```

### Database Integration

```javascript
// database.js - Simple database integration
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

class Database {
  constructor() {
    this.db = new sqlite3.Database(path.join(__dirname, 'whatsapp_bot.db'));
    this.init();
  }

  init() {
    // Create tables
    this.db.serialize(() => {
      // Conversations table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS conversations (
          phone TEXT,
          step TEXT,
          data TEXT,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Bookings table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS bookings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          phone TEXT,
          type TEXT,
          service TEXT,
          date TEXT,
          time TEXT,
          details TEXT,
          status TEXT DEFAULT 'confirmed',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Leads table
      this.db.run(`
        CREATE TABLE IF NOT EXISTS leads (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          phone TEXT,
          company TEXT,
          contact_person TEXT,
          interest TEXT,
          status TEXT DEFAULT 'new',
          data TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);

      // Support tickets
      this.db.run(`
        CREATE TABLE IF NOT EXISTS tickets (
          id TEXT PRIMARY KEY,
          phone TEXT,
          type TEXT,
          description TEXT,
          status TEXT DEFAULT 'open',
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `);
    });
  }

  // Conversation state management
  saveConversationState(phone, step, data) {
    return new Promise((resolve, reject) => {
      this.db.run(`
        INSERT OR REPLACE INTO conversations (phone, step, data, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
      `, [phone, step, JSON.stringify(data)], function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      });
    });
  }

  getConversationState(phone) {
    return new Promise((resolve, reject) => {
      this.db.get(`
        SELECT * FROM conversations WHERE phone = ?
        ORDER BY updated_at DESC LIMIT 1
      `, [phone], (err, row) => {
        if (err) reject(err);
        else resolve(row ? { step: row.step, data: JSON.parse(row.data) } : null);
      });
    });
  }

  // Booking management
  saveBooking(bookingData) {
    return new Promise((resolve, reject) => {
      this.db.run(`
        INSERT INTO bookings (phone, type, service, date, time, details)
        VALUES (?, ?, ?, ?, ?, ?)
      `, [
        bookingData.phone,
        bookingData.type,
        bookingData.service,
        bookingData.date,
        bookingData.time,
        JSON.stringify(bookingData.details)
      ], function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      });
    });
  }

  // Lead management
  saveLead(leadData) {
    return new Promise((resolve, reject) => {
      this.db.run(`
        INSERT INTO leads (phone, company, contact_person, interest, data)
        VALUES (?, ?, ?, ?, ?)
      `, [
        leadData.phone,
        leadData.company,
        leadData.contact_person,
        leadData.interest,
        JSON.stringify(leadData)
      ], function(err) {
        if (err) reject(err);
        else resolve(this.lastID);
      });
    });
  }
}

module.exports = Database;
```

## ⚡ Zapier Integration Blueprints

### 1. New Lead to CRM

```javascript
// Zapier Webhook - New Lead Created
// Trigger: Webhook POST /zapier/new-lead

{
  "phone": "+391234567890",
  "company": "Acme Corp",
  "contact_person": "John Smith",
  "role": "CEO",
  "interest": "AI Chatbots",
  "company_size": "11-50 employees",
  "timeline": "Within 2-3 months",
  "budget": "€15,000 - €50,000",
  "challenges": "Too much manual customer support",
  "created_at": "2024-01-15T10:30:00Z"
}

// Zapier Actions:
// 1. Create contact in HubSpot/Salesforce
// 2. Send internal Slack notification
// 3. Add to Google Sheets
// 4. Schedule follow-up email
// 5. Create calendar reminder
```

### 2. Booking Confirmation to Calendar

```javascript
// Zapier Webhook - New Booking
// Trigger: Webhook POST /zapier/new-booking

{
  "phone": "+391234567890",
  "customer_name": "Maria Rossi",
  "service": "Haircut",
  "stylist": "Sofia",
  "date": "2024-01-20",
  "time": "14:00",
  "duration": 45,
  "price": 25,
  "booking_type": "salon"
}

// Zapier Actions:
// 1. Create Google Calendar event
// 2. Send confirmation email
// 3. Add to staff schedule
// 4. Set up SMS reminder
// 5. Update availability system
```

### 3. Support Ticket to Helpdesk

```javascript
// Zapier Webhook - New Support Ticket
// Trigger: Webhook POST /zapier/new-ticket

{
  "ticket_id": "TKT123456",
  "phone": "+391234567890",
  "customer_name": "Giovanni Bianchi",
  "issue_type": "Technical Issue",
  "description": "App crashes when uploading photos",
  "priority": "medium",
  "created_at": "2024-01-15T15:45:00Z"
}

// Zapier Actions:
// 1. Create ticket in Zendesk/Freshdesk
// 2. Assign to appropriate team member
// 3. Send internal notification
// 4. Add to project management tool
// 5. Set up automated follow-up
```

## 💰 Cost Breakdown

### Free Tier (€0/month)
```
✅ Meta WhatsApp Business API
✅ 1,000 conversations/month free
✅ Basic templates included
✅ Webhook integration

Limitations:
- Basic phone number verification required
- Limited to approved business accounts
```

### Small Business (€15-25/month)
```
📱 WhatsApp Business API: €0.005-0.01/message
🖥️  Hosting (VPS): €10-15/month
💾 Database: €0 (SQLite) or €5 (PostgreSQL)
⚡ Additional services: €5-10/month

💬 ~3,000 messages/month capacity
👥 Perfect for local businesses
```

### Medium Business (€35-50/month)
```
📱 WhatsApp API: €0.005/message
🖥️  Cloud hosting: €20-30/month
💾 Database: €10-15/month
🔄 Zapier Pro: €15-20/month
📊 Analytics: €5-10/month

💬 ~8,000 messages/month capacity
🚀 Advanced automation included
```

### Enterprise (€100+/month)
```
📱 WhatsApp Business Solution: €50+/month
🖥️  Dedicated infrastructure: €50+/month
💾 Enterprise database: €25+/month
🔧 Custom integrations: €100+/month
👨‍💼 Priority support: €50+/month

💬 Unlimited messages
🎯 Full customization
🔐 Advanced security
```

## 🚀 Deployment Guide

### 1. Local Development Setup

```bash
# Clone or create project directory
mkdir whatsapp-bot
cd whatsapp-bot

# Initialize project
npm init -y

# Install dependencies
npm install express axios sqlite3 dotenv

# Create environment file
touch .env
```

### 2. Environment Variables

```bash
# .env file
WHATSAPP_ACCESS_TOKEN=your_meta_access_token
WHATSAPP_VERIFY_TOKEN=your_verify_token_here
WEBHOOK_VERIFY_TOKEN=your_webhook_token
PORT=3000

# Optional integrations
ZAPIER_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/...
DATABASE_URL=sqlite:./whatsapp_bot.db
```

### 3. Production Deployment (Heroku)

```bash
# Install Heroku CLI
npm install -g heroku

# Create Heroku app
heroku create your-whatsapp-bot

# Set environment variables
heroku config:set WHATSAPP_ACCESS_TOKEN=your_token
heroku config:set WHATSAPP_VERIFY_TOKEN=your_verify_token
heroku config:set PORT=443

# Deploy
git add .
git commit -m "WhatsApp bot deployment"
git push heroku main

# Your webhook URL will be:
# https://your-whatsapp-bot.herokuapp.com/webhook
```

### 4. Alternative Deployment (Railway)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables in Railway dashboard
```

## 📊 Performance Optimization

### Message Response Time Tips

```javascript
// 1. Use async/await properly
async function handleMessage(phone, message) {
  // ✅ Good - parallel operations
  const [userState, businessHours] = await Promise.all([
    getUserState(phone),
    checkBusinessHours()
  ]);

  // ❌ Bad - sequential operations
  const userState = await getUserState(phone);
  const businessHours = await checkBusinessHours();
}

// 2. Cache frequently accessed data
const cache = new Map();

async function getCachedData(key) {
  if (cache.has(key)) {
    return cache.get(key);
  }

  const data = await fetchData(key);
  cache.set(key, data);
  return data;
}

// 3. Implement message queues for high volume
const Queue = require('bull');
const messageQueue = new Queue('message processing');

messageQueue.process(async (job) => {
  const { phone, message } = job.data;
  return await processMessage(phone, message);
});
```

### Database Optimization

```javascript
// Use connection pooling
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10, // max connections
  idleTimeoutMillis: 30000
});

// Index important fields
CREATE INDEX idx_conversations_phone ON conversations(phone);
CREATE INDEX idx_bookings_date ON bookings(date, time);
CREATE INDEX idx_leads_created ON leads(created_at);
```

## 🔧 Advanced Features

### Smart Message Recognition

```javascript
// AI-powered intent recognition using OpenAI
const OpenAI = require('openai');
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function detectIntent(message) {
  const completion = await openai.chat.completions.create({
    model: "gpt-3.5-turbo",
    messages: [{
      role: "system",
      content: "Classify this message intent as: booking, support, info, lead, or general. Reply with just the category."
    }, {
      role: "user",
      content: message
    }],
    max_tokens: 10
  });

  return completion.choices[0].message.content.toLowerCase().trim();
}
```

### Multi-language Support

```javascript
// Language detection and response
const languages = {
  'it': {
    welcome: 'Benvenuto! Come posso aiutarti?',
    booking: 'Prenotazione',
    support: 'Supporto clienti'
  },
  'en': {
    welcome: 'Welcome! How can I help you?',
    booking: 'Booking',
    support: 'Customer support'
  },
  'de': {
    welcome: 'Willkommen! Wie kann ich helfen?',
    booking: 'Buchung',
    support: 'Kundensupport'
  }
};

function detectLanguage(message) {
  // Simple keyword-based detection
  if (/ciao|grazie|prego|aiuto/i.test(message)) return 'it';
  if (/hallo|danke|bitte|hilfe/i.test(message)) return 'de';
  return 'en'; // default
}
```

This comprehensive guide provides everything needed to implement WhatsApp Business integration with practical, working templates that can be customized for any business type.