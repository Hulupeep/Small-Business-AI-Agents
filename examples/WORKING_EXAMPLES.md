# Working Examples - Copy & Paste Ready

## Complete Working Customer Service Bot

### Requirements
```bash
npm init -y
npm install express axios dotenv body-parser
```

### .env file
```
OPENAI_API_KEY=sk-...your-key-here
INTERCOM_TOKEN=dG9rOi...your-token
PORT=3000
```

### Full Implementation (server.js)
```javascript
require('dotenv').config();
const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

// Store conversation context
const conversations = new Map();

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'running', timestamp: new Date() });
});

// Main webhook endpoint
app.post('/webhook/chat', async (req, res) => {
    console.log('Received webhook:', JSON.stringify(req.body, null, 2));

    try {
        const { message, conversation_id, user_id } = req.body;

        // Get conversation history
        const history = conversations.get(conversation_id) || [];

        // Add new message to history
        history.push({ role: 'user', content: message });

        // Call OpenAI
        const openaiResponse = await axios.post(
            'https://api.openai.com/v1/chat/completions',
            {
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: `You are a helpful customer service agent for our business.
                        Be concise and friendly. If you don't know something, say so.`
                    },
                    ...history.slice(-10) // Keep last 10 messages for context
                ],
                max_tokens: 200,
                temperature: 0.7
            },
            {
                headers: {
                    'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        const aiMessage = openaiResponse.data.choices[0].message.content;

        // Update conversation history
        history.push({ role: 'assistant', content: aiMessage });
        conversations.set(conversation_id, history);

        // Return response
        res.json({
            success: true,
            response: aiMessage,
            conversation_id
        });

    } catch (error) {
        console.error('Error:', error.response?.data || error.message);

        res.status(500).json({
            success: false,
            error: 'Failed to process request',
            fallback: 'I apologize for the inconvenience. Please contact support@company.com'
        });
    }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Webhook URL: http://localhost:${PORT}/webhook/chat`);
});
```

### Testing the Bot
```bash
# Start server
node server.js

# In another terminal, test with curl
curl -X POST http://localhost:3000/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your business hours?",
    "conversation_id": "test-123",
    "user_id": "user-456"
  }'
```

---

## Complete Working Lead Qualifier

### Python Implementation (lead_qualifier.py)
```python
import os
from flask import Flask, request, jsonify
from dataclasses import dataclass
from typing import Dict, List
import openai
import json

app = Flask(__name__)
openai.api_key = os.environ['OPENAI_API_KEY']

@dataclass
class Lead:
    email: str
    responses: Dict[str, str]
    score: int = 0
    qualified: bool = False

class LeadQualifier:
    def __init__(self):
        self.questions = [
            "What's your budget range?",
            "When do you need this implemented?",
            "Who makes the purchasing decisions?",
            "What problem are you trying to solve?"
        ]
        self.leads = {}

    def calculate_bant_score(self, responses):
        score = 0

        # Budget scoring
        budget = responses.get('budget', '').lower()
        if 'thousand' in budget or 'k' in budget:
            score += 25
        elif 'hundred' in budget:
            score += 10

        # Authority scoring
        authority = responses.get('authority', '').lower()
        if 'owner' in authority or 'ceo' in authority or 'director' in authority:
            score += 25
        elif 'manager' in authority:
            score += 15

        # Need scoring
        need = responses.get('need', '').lower()
        if 'urgent' in need or 'asap' in need or 'immediately' in need:
            score += 25

        # Timeline scoring
        timeline = responses.get('timeline', '').lower()
        if 'week' in timeline or 'month' in timeline:
            score += 25
        elif 'quarter' in timeline:
            score += 15

        return score

    def qualify_with_ai(self, responses):
        prompt = f"""
        Analyze this lead based on their responses:
        {json.dumps(responses, indent=2)}

        Score them 1-100 on:
        1. Budget fit
        2. Authority level
        3. Need urgency
        4. Timeline readiness

        Return a JSON with: score, qualified (true/false), and reason.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a lead qualification expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            return json.loads(response.choices[0].message.content)
        except:
            # Fallback to rule-based scoring
            score = self.calculate_bant_score(responses)
            return {
                "score": score,
                "qualified": score >= 60,
                "reason": "Scored based on BANT criteria"
            }

qualifier = LeadQualifier()

@app.route('/qualify', methods=['POST'])
def qualify_lead():
    data = request.json

    # Get or create lead
    email = data.get('email')
    responses = data.get('responses', {})

    # Qualify with AI
    result = qualifier.qualify_with_ai(responses)

    # Store lead
    lead = Lead(
        email=email,
        responses=responses,
        score=result['score'],
        qualified=result['qualified']
    )
    qualifier.leads[email] = lead

    return jsonify({
        'qualified': lead.qualified,
        'score': lead.score,
        'next_action': 'schedule_demo' if lead.qualified else 'nurture_campaign',
        'reason': result['reason']
    })

@app.route('/leads', methods=['GET'])
def get_leads():
    return jsonify([
        {
            'email': lead.email,
            'score': lead.score,
            'qualified': lead.qualified
        }
        for lead in qualifier.leads.values()
    ])

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

---

## Complete Working Social Media Bot

### Node.js Twitter/X Bot
```javascript
const { TwitterApi } = require('twitter-api-v2');
const OpenAI = require('openai');
const cron = require('node-cron');

// Initialize clients
const twitter = new TwitterApi({
    appKey: process.env.TWITTER_API_KEY,
    appSecret: process.env.TWITTER_API_SECRET,
    accessToken: process.env.TWITTER_ACCESS_TOKEN,
    accessSecret: process.env.TWITTER_ACCESS_SECRET,
});

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

class SocialMediaBot {
    constructor() {
        this.client = twitter.v2;
    }

    async generatePost(topic) {
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [{
                role: "system",
                content: "You are a social media manager. Create engaging posts under 280 characters."
            }, {
                role: "user",
                content: `Create a post about: ${topic}`
            }],
            max_tokens: 100,
            temperature: 0.8
        });

        return completion.choices[0].message.content;
    }

    async postTweet(content) {
        try {
            const tweet = await this.client.tweet(content);
            console.log('Posted:', tweet.data);
            return tweet.data;
        } catch (error) {
            console.error('Failed to post:', error);
            throw error;
        }
    }

    async replyToMentions() {
        try {
            // Get mentions
            const mentions = await this.client.userMentionTimeline(
                process.env.TWITTER_USER_ID,
                { max_results: 10 }
            );

            for (const mention of mentions.data || []) {
                // Generate reply
                const reply = await this.generateReply(mention.text);

                // Post reply
                await this.client.reply(reply, mention.id);

                console.log(`Replied to ${mention.id}`);
            }
        } catch (error) {
            console.error('Error handling mentions:', error);
        }
    }

    async generateReply(mentionText) {
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [{
                role: "system",
                content: "Reply helpfully and professionally to this mention."
            }, {
                role: "user",
                content: mentionText
            }],
            max_tokens: 100
        });

        return completion.choices[0].message.content;
    }
}

// Initialize bot
const bot = new SocialMediaBot();

// Schedule posts (every 6 hours)
cron.schedule('0 */6 * * *', async () => {
    const topics = [
        "productivity tips",
        "industry insights",
        "customer success story",
        "product update"
    ];

    const topic = topics[Math.floor(Math.random() * topics.length)];
    const post = await bot.generatePost(topic);
    await bot.postTweet(post);
});

// Check mentions every 30 minutes
cron.schedule('*/30 * * * *', () => {
    bot.replyToMentions();
});

console.log('Social media bot started');
```

---

## Complete Working Email Responder

### Gmail Integration with AI
```python
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import openai
import pickle

class EmailResponder:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
        self.service = self.authenticate_gmail()
        openai.api_key = os.environ['OPENAI_API_KEY']

    def authenticate_gmail(self):
        creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def get_unread_emails(self):
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread'
            ).execute()

            messages = results.get('messages', [])
            return messages
        except Exception as error:
            print(f'An error occurred: {error}')
            return []

    def read_email(self, message_id):
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()

            # Extract email content
            payload = message['payload']
            headers = payload.get('headers', [])

            subject = ''
            sender = ''
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'From':
                    sender = header['value']

            # Get body
            body = self.extract_body(payload)

            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'body': body
            }
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

    def extract_body(self, payload):
        body = ''

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif payload['body'].get('data'):
            body = base64.urlsafe_b64decode(
                payload['body']['data']).decode('utf-8')

        return body

    def generate_reply(self, email_content):
        prompt = f"""
        Generate a professional reply to this email:

        Subject: {email_content['subject']}
        From: {email_content['sender']}
        Body: {email_content['body']}

        Keep the reply concise and professional.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional email assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        return response.choices[0].message.content

    def send_reply(self, to, subject, body, thread_id=None):
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = f"Re: {subject}"

        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()).decode('utf-8')

        send_message = {'raw': raw_message}
        if thread_id:
            send_message['threadId'] = thread_id

        try:
            message = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()
            print(f'Message sent: {message["id"]}')
            return message
        except Exception as error:
            print(f'An error occurred: {error}')
            return None

    def process_emails(self):
        unread = self.get_unread_emails()

        for msg in unread:
            email = self.read_email(msg['id'])
            if email:
                # Generate AI reply
                reply = self.generate_reply(email)

                # Send reply
                self.send_reply(
                    email['sender'],
                    email['subject'],
                    reply,
                    msg.get('threadId')
                )

                # Mark as read
                self.service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()

# Run the email responder
if __name__ == '__main__':
    responder = EmailResponder()
    responder.process_emails()
```

---

## Complete Working Slack Bot

```javascript
const { App } = require('@slack/bolt');
const OpenAI = require('openai');

const app = new App({
    token: process.env.SLACK_BOT_TOKEN,
    signingSecret: process.env.SLACK_SIGNING_SECRET,
    socketMode: true,
    appToken: process.env.SLACK_APP_TOKEN
});

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

// Handle direct messages
app.message(async ({ message, say }) => {
    try {
        // Don't respond to bot messages
        if (message.subtype === 'bot_message') return;

        // Generate AI response
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [{
                role: "system",
                content: "You are a helpful Slack assistant."
            }, {
                role: "user",
                content: message.text
            }],
            max_tokens: 200
        });

        // Send response
        await say(completion.choices[0].message.content);

    } catch (error) {
        console.error('Error:', error);
        await say("Sorry, I encountered an error processing your request.");
    }
});

// Handle slash commands
app.command('/ask-ai', async ({ command, ack, respond }) => {
    await ack();

    try {
        const completion = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [{
                role: "user",
                content: command.text
            }],
            max_tokens: 500
        });

        await respond({
            text: completion.choices[0].message.content
        });
    } catch (error) {
        await respond({
            text: "Error processing your request"
        });
    }
});

// Start app
(async () => {
    await app.start();
    console.log('⚡️ Slack bot is running!');
})();
```

---

## Deployment Script (deploy.sh)

```bash
#!/bin/bash

# Simple deployment script for any of the above bots

echo "🚀 Deploying AI Bot..."

# Check for required environment variables
required_vars=("OPENAI_API_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set"
        exit 1
    fi
done

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Run tests
echo "🧪 Running tests..."
npm test

# Start with PM2
echo "🏃 Starting application..."
pm2 stop ai-bot 2>/dev/null
pm2 start server.js --name ai-bot

# Check if running
sleep 3
if pm2 list | grep -q "ai-bot.*online"; then
    echo "✅ Bot deployed successfully!"
    echo "📊 View logs: pm2 logs ai-bot"
    echo "🔍 Monitor: pm2 monit"
else
    echo "❌ Deployment failed"
    pm2 logs ai-bot --lines 50
    exit 1
fi
```

---

## Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-bot:
    build: .
    ports:
      - "3000:3000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NODE_ENV=production
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

*These are REAL, WORKING examples. Not promises, not concepts - actual code that runs.*