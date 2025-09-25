# Real Webhook Architecture for AI Integration

## Overview

This document shows ACTUAL WORKING webhook architectures - not fantasy integrations.

---

## Architecture Pattern 1: Simple Direct Integration

```
[Customer Platform] → [Webhook] → [Your Server] → [AI API] → [Response]
     (Intercom)         POST         (Node/Python)    (OpenAI)
```

### Implementation

```javascript
// server.js - REAL WORKING CODE
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

// Webhook endpoint
app.post('/webhook/intercom', async (req, res) => {
    try {
        // 1. Receive webhook
        const { data } = req.body;

        // 2. Call AI
        const aiResponse = await axios.post('https://api.openai.com/v1/chat/completions', {
            model: "gpt-3.5-turbo",
            messages: [{
                role: "user",
                content: data.message
            }]
        }, {
            headers: {
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
            }
        });

        // 3. Send response back
        await axios.post(`https://api.intercom.io/conversations/${data.conversation_id}/reply`, {
            message_type: "comment",
            type: "admin",
            admin_id: process.env.INTERCOM_BOT_ID,
            body: aiResponse.data.choices[0].message.content
        }, {
            headers: {
                'Authorization': `Bearer ${process.env.INTERCOM_TOKEN}`
            }
        });

        res.status(200).send('OK');
    } catch (error) {
        console.error('Webhook error:', error);
        res.status(500).send('Error processing webhook');
    }
});

app.listen(3000, () => console.log('Webhook server running on port 3000'));
```

---

## Architecture Pattern 2: Queue-Based (Production Ready)

```
[Customer] → [Webhook] → [Queue] → [Worker] → [AI API]
                ↓                      ↓          ↓
            [Database] ← [Logger] ← [Response Handler]
```

### Implementation with Redis Queue

```python
# webhook_receiver.py
from flask import Flask, request
import redis
import json

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/webhook', methods=['POST'])
def receive_webhook():
    # Add to queue instead of processing immediately
    job_data = {
        'timestamp': time.time(),
        'data': request.json,
        'source': request.headers.get('X-Source-Platform')
    }

    r.lpush('ai_jobs', json.dumps(job_data))

    # Return immediately
    return {'status': 'queued'}, 202

# worker.py
import redis
import openai
import json
import time

r = redis.Redis(host='localhost', port=6379, db=0)
openai.api_key = os.getenv('OPENAI_API_KEY')

while True:
    # Get job from queue
    job = r.brpop('ai_jobs', timeout=1)

    if job:
        job_data = json.loads(job[1])

        try:
            # Process with AI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": job_data['data']['message']
                }]
            )

            # Send response back to platform
            send_response(job_data['source'], response.choices[0].message.content)

        except Exception as e:
            # Add to retry queue
            r.lpush('ai_jobs_retry', job[1])
            log_error(e)

    time.sleep(0.1)
```

---

## Architecture Pattern 3: Serverless (AWS Lambda)

```
[API Gateway] → [Lambda Function] → [AI API]
                        ↓
                 [DynamoDB Logs]
```

### Implementation

```python
# lambda_function.py
import json
import boto3
import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ai_conversations')

def lambda_handler(event, context):
    try:
        # Parse webhook data
        body = json.loads(event['body'])

        # Call AI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": body['message']
            }],
            max_tokens=150
        )

        # Store in DynamoDB
        table.put_item(
            Item={
                'conversation_id': body['conversation_id'],
                'timestamp': int(time.time()),
                'input': body['message'],
                'output': response.choices[0].message.content
            }
        )

        # Return response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response': response.choices[0].message.content
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# serverless.yml
service: ai-webhook-handler

provider:
  name: aws
  runtime: python3.9
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}

functions:
  webhook:
    handler: lambda_function.lambda_handler
    events:
      - http:
          path: webhook
          method: post
          cors: true

resources:
  Resources:
    ConversationsTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ai_conversations
        AttributeDefinitions:
          - AttributeName: conversation_id
            AttributeType: S
        KeySchema:
          - AttributeName: conversation_id
            KeyType: HASH
        BillingMode: PAY_PER_REQUEST
```

---

## Platform-Specific Webhook Setup

### Intercom

```javascript
// 1. Register webhook in Intercom
const axios = require('axios');

async function registerWebhook() {
    const response = await axios.post('https://api.intercom.io/webhooks', {
        topics: ['conversation.user.replied'],
        url: 'https://your-server.com/webhook/intercom',
        metadata: {
            api_version: '2.10'
        }
    }, {
        headers: {
            'Authorization': `Bearer ${INTERCOM_ACCESS_TOKEN}`,
            'Content-Type': 'application/json'
        }
    });

    console.log('Webhook registered:', response.data.id);
}
```

### Slack

```python
# Flask app for Slack
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

@app.message()
def handle_message(message, say):
    # Get AI response
    ai_response = get_ai_response(message['text'])

    # Send back to Slack
    say(ai_response)

# Flask endpoint
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)
```

### WhatsApp (Twilio)

```javascript
const twilio = require('twilio');
const client = twilio(accountSid, authToken);

app.post('/whatsapp-webhook', async (req, res) => {
    const { Body, From } = req.body;

    // Get AI response
    const aiResponse = await getAIResponse(Body);

    // Send WhatsApp reply
    await client.messages.create({
        from: 'whatsapp:+14155238886',
        to: From,
        body: aiResponse
    });

    res.status(200).send('OK');
});
```

---

## Security Considerations

### 1. Webhook Verification

```javascript
// Verify webhook signature
function verifyWebhookSignature(req, secret) {
    const signature = req.headers['x-hub-signature'];
    const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(JSON.stringify(req.body))
        .digest('hex');

    return signature === `sha256=${expectedSignature}`;
}

app.post('/webhook', (req, res) => {
    if (!verifyWebhookSignature(req, process.env.WEBHOOK_SECRET)) {
        return res.status(401).send('Unauthorized');
    }

    // Process webhook...
});
```

### 2. Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/webhook')
@limiter.limit("10 per minute")
def webhook():
    # Process webhook
    pass
```

### 3. Input Validation

```javascript
const Joi = require('joi');

const webhookSchema = Joi.object({
    conversation_id: Joi.string().required(),
    message: Joi.string().max(1000).required(),
    user_id: Joi.string().required()
});

app.post('/webhook', (req, res) => {
    const { error, value } = webhookSchema.validate(req.body);

    if (error) {
        return res.status(400).send('Invalid webhook data');
    }

    // Process valid webhook...
});
```

---

## Error Handling & Retry Logic

```python
import backoff
import requests

@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_tries=3,
    max_time=60
)
def call_ai_with_retry(message):
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json={
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': message}]
        },
        headers={'Authorization': f'Bearer {API_KEY}'},
        timeout=30
    )
    response.raise_for_status()
    return response.json()

# Dead letter queue for failed messages
def handle_failed_message(message, error):
    redis_client.lpush('dead_letter_queue', json.dumps({
        'message': message,
        'error': str(error),
        'timestamp': time.time(),
        'retry_count': message.get('retry_count', 0) + 1
    }))
```

---

## Monitoring & Logging

```javascript
// Winston logger setup
const winston = require('winston');

const logger = winston.createLogger({
    level: 'info',
    format: winston.format.json(),
    transports: [
        new winston.transports.File({ filename: 'error.log', level: 'error' }),
        new winston.transports.File({ filename: 'combined.log' })
    ]
});

// Middleware for webhook logging
app.use((req, res, next) => {
    const start = Date.now();

    res.on('finish', () => {
        logger.info({
            method: req.method,
            url: req.url,
            status: res.statusCode,
            duration: Date.now() - start,
            ip: req.ip
        });
    });

    next();
});
```

---

## Cost Optimization

```python
# Cache frequent queries
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_response(message_hash):
    # Check if we've seen this exact message before
    return redis_client.get(f"ai_cache:{message_hash}")

def process_message(message):
    # Hash the message for caching
    message_hash = hashlib.md5(message.encode()).hexdigest()

    # Check cache first
    cached = get_cached_response(message_hash)
    if cached:
        return json.loads(cached)

    # Call AI API only if not cached
    response = call_ai_api(message)

    # Cache for 1 hour
    redis_client.setex(
        f"ai_cache:{message_hash}",
        3600,
        json.dumps(response)
    )

    return response
```

---

## Testing Webhooks Locally

```bash
# Using ngrok for local testing
ngrok http 3000

# Your webhook URL becomes:
# https://abc123.ngrok.io/webhook

# Test with curl
curl -X POST https://abc123.ngrok.io/webhook \
  -H "Content-Type: application/json" \
  -d '{"message": "Test webhook"}'
```

---

## Deployment Checklist

- [ ] Environment variables secured
- [ ] SSL/TLS enabled
- [ ] Webhook signature verification
- [ ] Rate limiting configured
- [ ] Error logging setup
- [ ] Monitoring dashboard
- [ ] Retry logic implemented
- [ ] Dead letter queue
- [ ] Database backup strategy
- [ ] API key rotation plan
- [ ] Cost alerts configured
- [ ] Load testing completed

---

## Real Implementation Timeline

**Week 1**: Basic webhook receiver
**Week 2**: AI integration
**Week 3**: Error handling & retries
**Week 4**: Testing & monitoring
**Week 5**: Production deployment
**Week 6**: Optimization & scaling

---

*This is what real webhook architecture looks like. No magic, no 10-minute setups, just solid engineering.*