# Messaging Integration Guide 💬

*Connect WhatsApp Business, SMS, Telegram, and more to your LangChain system*

## What You'll Need
- Business phone number
- 30-60 minutes setup time per platform
- Credit card for SMS services (small costs)
- Smartphone for verification

---

## WhatsApp Business API Integration

### Step 1: Set Up WhatsApp Business Account
1. **Download WhatsApp Business** app on your phone
2. **Register with your business phone number**
3. **Complete business profile:**
   - Business name
   - Category
   - Description
   - Website
   - Hours of operation

### Step 2: Apply for WhatsApp Business API
1. **Go to** https://business.whatsapp.com
2. **Click "Get Started"**
3. **Select "WhatsApp Business API"**
4. **Choose a Business Solution Provider** (BSP):
   - **Twilio** (easiest for beginners)
   - **360dialog**
   - **MessageBird**
   - **Vonage**

### Step 3: Twilio WhatsApp Setup (Recommended)
1. **Create Twilio account** at https://www.twilio.com
2. **Go to Console → Messaging → Try it out → Send a WhatsApp message**
3. **Follow the setup wizard:**
   - Verify your phone number
   - Join Twilio's WhatsApp sandbox
   - Send test message

### Step 4: Get Your WhatsApp Credentials
1. **In Twilio Console**, go to **Settings → General**
2. **Copy these values:**
   - **Account SID** (starts with AC...)
   - **Auth Token** (click to reveal)
3. **Go to Phone Numbers → Manage → WhatsApp senders**
4. **Copy your WhatsApp number** (format: +14155238886)

### Step 5: WhatsApp Integration Code
```javascript
// WhatsApp messaging with Twilio
const twilio = require('twilio');

const client = twilio(
    'YOUR_ACCOUNT_SID',
    'YOUR_AUTH_TOKEN'
);

async function sendWhatsAppMessage(to, message) {
    try {
        const response = await client.messages.create({
            body: message,
            from: 'whatsapp:+14155238886', // Your Twilio WhatsApp number
            to: `whatsapp:${to}`           // Recipient's WhatsApp number
        });

        console.log('Message sent:', response.sid);
        return response;
    } catch (error) {
        console.error('Error sending WhatsApp message:', error);
        throw error;
    }
}

// Example usage
sendWhatsAppMessage('+1234567890', 'Hello from LangChain! 🤖');
```

### Step 6: Handle Incoming WhatsApp Messages
```javascript
// Express.js webhook for receiving WhatsApp messages
const express = require('express');
const app = express();

app.use(express.urlencoded({ extended: false }));

app.post('/whatsapp-webhook', (req, res) => {
    const incomingMessage = req.body.Body;
    const senderNumber = req.body.From; // Format: whatsapp:+1234567890

    console.log(`Received: "${incomingMessage}" from ${senderNumber}`);

    // Process message with LangChain
    const response = processWithLangChain(incomingMessage);

    // Send response back
    sendWhatsAppMessage(
        senderNumber.replace('whatsapp:', ''),
        response
    );

    res.sendStatus(200);
});

app.listen(3000, () => {
    console.log('WhatsApp webhook listening on port 3000');
});
```

### WhatsApp Troubleshooting
**"Phone number not verified"**
- **Solution**: Complete WhatsApp Business verification process

**"Template message required"**
- **Solution**: Use approved message templates for promotional content

**"Rate limit exceeded"**
- **Solution**: WhatsApp has strict limits, space out messages

---

## SMS Integration with Twilio

### Step 1: Get Twilio Phone Number
1. **In Twilio Console**, go to **Phone Numbers → Manage → Buy a number**
2. **Select your country**
3. **Choose "SMS" capability**
4. **Click "Search"**
5. **Buy a number** you like (usually $1/month)

### Step 2: SMS Integration Code
```javascript
// Send SMS with Twilio
async function sendSMS(to, message) {
    try {
        const response = await client.messages.create({
            body: message,
            from: '+1234567890', // Your Twilio phone number
            to: to                // Recipient's phone number
        });

        console.log('SMS sent:', response.sid);
        return response;
    } catch (error) {
        console.error('Error sending SMS:', error);
        throw error;
    }
}

// Example usage
sendSMS('+1987654321', 'Your verification code is: 123456');
```

### Step 3: Receive SMS Messages
```javascript
// Webhook for incoming SMS
app.post('/sms-webhook', (req, res) => {
    const incomingMessage = req.body.Body;
    const senderNumber = req.body.From;

    console.log(`SMS received: "${incomingMessage}" from ${senderNumber}`);

    // Auto-reply example
    const autoReply = generateAutoReply(incomingMessage);

    sendSMS(senderNumber, autoReply);

    res.sendStatus(200);
});

function generateAutoReply(message) {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('help')) {
        return 'How can we help you? Reply with:\n- HOURS for business hours\n- LOCATION for our address\n- STOP to unsubscribe';
    } else if (lowerMessage.includes('hours')) {
        return 'We are open Monday-Friday 9AM-6PM, Saturday 10AM-4PM. Closed Sundays.';
    } else if (lowerMessage.includes('location')) {
        return 'Visit us at 123 Main Street, Your City. Call (555) 123-4567 for directions.';
    } else {
        return 'Thanks for your message! We will respond within 24 hours. Reply HELP for immediate assistance.';
    }
}
```

### SMS Best Practices
```javascript
// SMS compliance and best practices
const smsConfig = {
    // Always include opt-out option
    optOutFooter: '\n\nReply STOP to unsubscribe',

    // Keep messages under 160 characters when possible
    maxLength: 160,

    // Respect time zones and business hours
    sendingHours: {
        start: 9,  // 9 AM
        end: 21    // 9 PM
    },

    // Rate limiting to avoid spam
    rateLimitPerHour: 10
};

function isValidSendingTime() {
    const hour = new Date().getHours();
    return hour >= smsConfig.sendingHours.start &&
           hour < smsConfig.sendingHours.end;
}
```

---

## Telegram Bot Integration

### Step 1: Create Telegram Bot
1. **Open Telegram** on your phone or computer
2. **Search for** "@BotFather"
3. **Start a chat** with BotFather
4. **Send** `/newbot`
5. **Choose a name** for your bot (e.g., "My LangChain Bot")
6. **Choose a username** (must end with "bot", e.g., "mylangchainbot")
7. **Copy the Bot Token** (looks like: 123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)

### Step 2: Telegram Bot Code
```javascript
// Telegram bot with node-telegram-bot-api
const TelegramBot = require('node-telegram-bot-api');

const bot = new TelegramBot('YOUR_BOT_TOKEN', { polling: true });

// Handle /start command
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, 'Welcome to LangChain Bot! 🤖\n\nType /help for available commands.');
});

// Handle /help command
bot.onText(/\/help/, (msg) => {
    const chatId = msg.chat.id;
    const helpText = `
Available commands:
/start - Start the bot
/help - Show this help message
/ask <question> - Ask me anything
/status - Check bot status
    `;
    bot.sendMessage(chatId, helpText);
});

// Handle /ask command
bot.onText(/\/ask (.+)/, (msg, match) => {
    const chatId = msg.chat.id;
    const question = match[1];

    // Process with LangChain
    const answer = processWithLangChain(question);

    bot.sendMessage(chatId, `🤖 ${answer}`);
});

// Handle all other messages
bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    const messageText = msg.text;

    // Ignore commands (they start with /)
    if (!messageText.startsWith('/')) {
        const response = processWithLangChain(messageText);
        bot.sendMessage(chatId, response);
    }
});

console.log('Telegram bot is running...');
```

### Step 3: Advanced Telegram Features
```javascript
// Send photo with caption
bot.sendPhoto(chatId, 'https://example.com/image.jpg', {
    caption: 'Here is the image you requested!'
});

// Send document
bot.sendDocument(chatId, 'https://example.com/report.pdf', {
    caption: 'Your report is ready!'
});

// Inline keyboard
const options = {
    reply_markup: {
        inline_keyboard: [
            [
                { text: 'Option 1', callback_data: 'option1' },
                { text: 'Option 2', callback_data: 'option2' }
            ]
        ]
    }
};

bot.sendMessage(chatId, 'Choose an option:', options);

// Handle button clicks
bot.on('callback_query', (callbackQuery) => {
    const chatId = callbackQuery.message.chat.id;
    const data = callbackQuery.data;

    if (data === 'option1') {
        bot.sendMessage(chatId, 'You selected Option 1!');
    } else if (data === 'option2') {
        bot.sendMessage(chatId, 'You selected Option 2!');
    }

    bot.answerCallbackQuery(callbackQuery.id);
});
```

### Telegram Troubleshooting
**"Bot doesn't respond"**
- **Solution**: Check if bot token is correct and bot is running

**"Polling error"**
- **Solution**: Only one instance can poll at a time, stop other instances

**"Message too long"**
- **Solution**: Telegram has 4096 character limit, split long messages

---

## Slack Integration

### Step 1: Create Slack App
1. **Go to** https://api.slack.com/apps
2. **Click "Create New App"**
3. **Choose "From scratch"**
4. **App Name**: "LangChain Bot"
5. **Select your workspace**
6. **Click "Create App"**

### Step 2: Configure Bot User
1. **Go to "OAuth & Permissions"**
2. **Scroll to "Scopes"**
3. **Add Bot Token Scopes:**
   - `chat:write`
   - `chat:write.public`
   - `app_mentions:read`
   - `channels:read`
4. **Click "Install to Workspace"**
5. **Copy the "Bot User OAuth Token"** (starts with xoxb-)

### Step 3: Slack Bot Code
```javascript
// Slack bot with @slack/bolt
const { App } = require('@slack/bolt');

const app = new App({
    token: 'xoxb-your-bot-token',
    signingSecret: 'your-signing-secret'
});

// Listen for mentions
app.event('app_mention', async ({ event, client }) => {
    try {
        const response = processWithLangChain(event.text);

        await client.chat.postMessage({
            channel: event.channel,
            text: `<@${event.user}> ${response}`
        });
    } catch (error) {
        console.error('Error handling mention:', error);
    }
});

// Listen for direct messages
app.message('hello', async ({ message, say }) => {
    await say(`Hello <@${message.user}>! How can I help you today?`);
});

// Slash command
app.command('/ask', async ({ command, ack, say }) => {
    await ack();

    const answer = processWithLangChain(command.text);
    await say(answer);
});

(async () => {
    await app.start(process.env.PORT || 3000);
    console.log('⚡️ Slack bot is running!');
})();
```

---

## Discord Bot Integration

### Step 1: Create Discord Application
1. **Go to** https://discord.com/developers/applications
2. **Click "New Application"**
3. **Name**: "LangChain Bot"
4. **Go to "Bot" section**
5. **Click "Add Bot"**
6. **Copy the Bot Token**

### Step 2: Discord Bot Code
```javascript
// Discord bot with discord.js
const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
});

client.on('messageCreate', async (message) => {
    // Ignore bot messages
    if (message.author.bot) return;

    // Respond to mentions or DMs
    if (message.mentions.has(client.user) || message.channel.type === 'DM') {
        const response = processWithLangChain(message.content);
        message.reply(response);
    }

    // Respond to specific keywords
    if (message.content.toLowerCase().includes('langchain')) {
        message.react('🤖');
        message.reply('Did someone mention LangChain? How can I help?');
    }
});

client.login('YOUR_BOT_TOKEN');
```

---

## Multi-Platform Messaging Manager

### Universal Messaging Class
```javascript
class MessagingManager {
    constructor() {
        this.platforms = {
            whatsapp: null,
            sms: null,
            telegram: null,
            slack: null,
            discord: null
        };
    }

    async initialize() {
        // Initialize all platforms
        this.platforms.whatsapp = new WhatsAppClient(config.whatsapp);
        this.platforms.sms = new SMSClient(config.sms);
        this.platforms.telegram = new TelegramClient(config.telegram);
        this.platforms.slack = new SlackClient(config.slack);
        this.platforms.discord = new DiscordClient(config.discord);
    }

    async sendMessage(platform, recipient, message) {
        const client = this.platforms[platform];
        if (!client) {
            throw new Error(`Platform ${platform} not configured`);
        }

        try {
            return await client.sendMessage(recipient, message);
        } catch (error) {
            console.error(`Failed to send ${platform} message:`, error);
            throw error;
        }
    }

    async broadcastMessage(message, platforms = ['whatsapp', 'sms', 'telegram']) {
        const results = await Promise.allSettled(
            platforms.map(platform =>
                this.sendMessage(platform, 'broadcast', message)
            )
        );

        return results.map((result, index) => ({
            platform: platforms[index],
            success: result.status === 'fulfilled',
            error: result.reason || null
        }));
    }
}
```

### Auto-Response System
```javascript
class AutoResponseSystem {
    constructor(messagingManager) {
        this.messaging = messagingManager;
        this.responses = {
            greeting: ['hi', 'hello', 'hey'],
            help: ['help', 'support', 'assist'],
            hours: ['hours', 'open', 'closed'],
            location: ['location', 'address', 'where']
        };
    }

    processIncomingMessage(platform, sender, message) {
        const intent = this.detectIntent(message);
        const response = this.generateResponse(intent, platform);

        if (response) {
            this.messaging.sendMessage(platform, sender, response);
        }
    }

    detectIntent(message) {
        const lowerMessage = message.toLowerCase();

        for (const [intent, keywords] of Object.entries(this.responses)) {
            if (keywords.some(keyword => lowerMessage.includes(keyword))) {
                return intent;
            }
        }

        return 'general';
    }

    generateResponse(intent, platform) {
        const responses = {
            greeting: 'Hello! How can I help you today?',
            help: 'I can help with:\n• Business hours\n• Location\n• General questions\n• Product information',
            hours: 'We are open Monday-Friday 9AM-6PM, weekends 10AM-4PM.',
            location: '📍 123 Main Street, Your City\n📞 (555) 123-4567',
            general: 'Thanks for your message! A team member will respond soon.'
        };

        return responses[intent] || responses.general;
    }
}
```

---

## Message Templates & Personalization

### Template System
```javascript
class MessageTemplates {
    constructor() {
        this.templates = {
            welcome: 'Welcome {{name}}! Thanks for joining {{business_name}}. 🎉',
            reminder: 'Hi {{name}}, this is a reminder about {{event}} on {{date}}.',
            promotion: '🎉 Special offer for {{name}}! Get {{discount}}% off {{product}}. Code: {{code}}',
            support: 'Hi {{name}}, we received your message about {{topic}}. We will respond within {{response_time}}.'
        };
    }

    render(templateName, variables) {
        let template = this.templates[templateName];
        if (!template) {
            throw new Error(`Template ${templateName} not found`);
        }

        // Replace variables
        for (const [key, value] of Object.entries(variables)) {
            template = template.replace(new RegExp(`{{${key}}}`, 'g'), value);
        }

        return template;
    }

    sendTemplatedMessage(platform, recipient, templateName, variables) {
        const message = this.render(templateName, variables);
        return this.messaging.sendMessage(platform, recipient, message);
    }
}

// Usage example
const templates = new MessageTemplates();
templates.sendTemplatedMessage('whatsapp', '+1234567890', 'welcome', {
    name: 'John',
    business_name: 'LangChain Solutions'
});
```

---

## Analytics & Monitoring

### Message Analytics
```javascript
class MessageAnalytics {
    constructor() {
        this.metrics = {
            sent: 0,
            delivered: 0,
            failed: 0,
            responses: 0
        };
    }

    trackMessage(platform, status, messageType = 'outbound') {
        const timestamp = new Date().toISOString();

        // Update counters
        this.metrics[status]++;

        // Log to database or analytics service
        this.logEvent({
            platform,
            status,
            messageType,
            timestamp
        });
    }

    generateReport(period = '24h') {
        const deliveryRate = (this.metrics.delivered / this.metrics.sent * 100).toFixed(2);
        const responseRate = (this.metrics.responses / this.metrics.sent * 100).toFixed(2);

        return {
            period,
            totalSent: this.metrics.sent,
            deliveryRate: `${deliveryRate}%`,
            responseRate: `${responseRate}%`,
            failedMessages: this.metrics.failed
        };
    }

    logEvent(event) {
        // Store in database or send to analytics service
        console.log('Analytics event:', event);
    }
}
```

---

## Common Problems & Solutions

### Message Delivery Issues
**Problem**: Messages not being delivered
**Solutions:**
- Check phone number format (include country code)
- Verify recipient has opted in to receive messages
- Check platform-specific delivery reports
- Ensure your account is in good standing

### Rate Limiting
**Problem**: "Too many requests" errors
**Solutions:**
- Implement proper rate limiting in your code
- Space out messages appropriately
- Use message queues for high volume
- Monitor your usage against platform limits

### Webhook Issues
**Problem**: Not receiving incoming messages
**Solutions:**
- Verify webhook URL is publicly accessible
- Check HTTPS certificate is valid
- Test webhook endpoint manually
- Review webhook logs for errors

### Character Encoding
**Problem**: Emojis or special characters display incorrectly
**Solutions:**
- Use UTF-8 encoding consistently
- Test with various character sets
- Check platform-specific character limits
- Use platform-appropriate emoji sets

---

## Compliance & Best Practices

### Legal Requirements
- **Obtain consent** before sending marketing messages
- **Provide opt-out mechanism** in every promotional message
- **Respect do-not-contact lists**
- **Follow TCPA, CAN-SPAM, and GDPR** regulations

### Technical Best Practices
```javascript
const complianceConfig = {
    // Required opt-out phrases
    optOutKeywords: ['stop', 'unsubscribe', 'quit', 'cancel'],

    // Message frequency limits
    maxMessagesPerDay: 5,
    maxMessagesPerHour: 2,

    // Required message elements
    businessIdentification: 'YourBusiness',
    optOutInstructions: 'Reply STOP to unsubscribe',

    // Sending time restrictions
    allowedHours: {
        start: 8,  // 8 AM
        end: 21,   // 9 PM
        timezone: 'America/New_York'
    }
};
```

---

## Getting Help

### Platform-Specific Support:
- **Twilio**: https://support.twilio.com
- **Telegram**: https://core.telegram.org/bots/faq
- **Slack**: https://api.slack.com/support
- **Discord**: https://discord.com/developers/docs

### Before Contacting Support:
1. **Test with simple messages** first
2. **Check API credentials** are correct
3. **Verify webhook endpoints** are working
4. **Review platform documentation** for changes

---

*Want to connect your CRM next? Check out our CRM_CONNECTIONS.md guide!*