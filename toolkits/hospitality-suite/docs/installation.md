# 🚀 Installation Guide

**Complete setup guide for the Hospitality AI Suite**

## Prerequisites

Before installing the Hospitality AI Suite, ensure you have:

### System Requirements
- **Node.js 18+** or **Python 3.8+**
- **4GB RAM minimum** (8GB recommended for multiple agents)
- **10GB free disk space**
- **Stable internet connection**
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Technical Requirements
- Basic computer literacy
- Access to your booking platform accounts
- Email account for notifications
- Mobile phone for SMS alerts (optional)

### Account Access Needed
- **Booking platform logins** (Booking.com, Airbnb, etc.)
- **Email account** for guest communications
- **WhatsApp Business** account (recommended)
- **Payment processor** access (Stripe, PayPal, etc.)

## Quick Start (5 minutes)

### Option 1: Automated Installation
```bash
# Download and run the automated installer
curl -fsSL https://install.floutlabs.com/hospitality | bash

# Follow the interactive setup
cd hospitality-suite
npm run setup
```

### Option 2: Manual Installation
```bash
# Clone the repository
git clone https://github.com/floutlabs/hospitality-ai-suite.git
cd hospitality-ai-suite

# Install dependencies
npm install

# Copy configuration template
cp config/example.env config/.env

# Run the setup wizard
npm run setup:wizard
```

## Detailed Installation Steps

### Step 1: Download the Toolkit

#### Option A: Git Clone (Recommended)
```bash
git clone https://github.com/floutlabs/hospitality-ai-suite.git
cd hospitality-ai-suite
```

#### Option B: Direct Download
1. Visit [https://github.com/floutlabs/hospitality-ai-suite](https://github.com/floutlabs/hospitality-ai-suite)
2. Click "Code" → "Download ZIP"
3. Extract to your desired location
4. Open terminal/command prompt in the extracted folder

### Step 2: Install Dependencies

#### For Node.js Installation
```bash
# Install Node.js dependencies
npm install

# Verify installation
npm run verify
```

#### For Python Installation
```bash
# Create virtual environment
python -m venv hospitality-env

# Activate virtual environment
source hospitality-env/bin/activate  # On Windows: hospitality-env\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

### Step 3: Configuration Setup

#### 1. Copy Configuration Template
```bash
cp config/example.env config/.env
```

#### 2. Edit Configuration File
Open `config/.env` in your preferred text editor and fill in your details:

```env
# Property Information
PROPERTY_NAME="Fitzgerald's Guesthouse"
PROPERTY_ADDRESS="Main Street, Westport, Co. Mayo"
PROPERTY_ROOMS=8
PROPERTY_EMAIL=info@fitzgeraldsguesthouse.ie
PROPERTY_PHONE=+353871234567

# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Booking Platform APIs
BOOKING_COM_API_KEY=your_booking_com_api_key
BOOKING_COM_PROPERTY_ID=your_property_id
AIRBNB_API_KEY=your_airbnb_api_key
AIRBNB_LISTING_ID=your_listing_id

# Communication Channels
WHATSAPP_API_KEY=your_whatsapp_business_api_key
WHATSAPP_PHONE_NUMBER=+353871234567
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Payment Processing
STRIPE_API_KEY=your_stripe_api_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# Smart Lock Integration (Optional)
SMART_LOCK_PROVIDER=august  # august, yale, schlage, manual
SMART_LOCK_API_KEY=your_smart_lock_api_key

# Weather API
WEATHER_API_KEY=your_openweather_api_key
WEATHER_LOCATION=Westport,IE

# Database (SQLite by default, PostgreSQL for production)
DATABASE_URL=sqlite:./data/hospitality.db
# DATABASE_URL=postgresql://user:password@localhost:5432/hospitality

# Monitoring & Alerts
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

#### 3. Run Configuration Wizard
```bash
npm run setup:wizard
```

The wizard will guide you through:
- Property setup
- Platform connections
- Communication preferences
- Smart lock configuration
- Payment setup
- Testing connections

### Step 4: Database Setup

#### SQLite (Default - No setup needed)
```bash
# Initialize database
npm run db:init

# Run migrations
npm run db:migrate
```

#### PostgreSQL (Production recommended)
```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Create database
createdb hospitality_suite

# Update DATABASE_URL in .env file
# Run migrations
npm run db:migrate
```

### Step 5: Agent Configuration

#### Configure Individual Agents
Each agent has its own configuration file in the `agents/` directory:

```bash
# Booking Manager
cp agents/booking-manager/config/example.yml agents/booking-manager/config/settings.yml

# Guest Concierge
cp agents/guest-concierge/config/example.yml agents/guest-concierge/config/settings.yml

# Check-in Automation
cp agents/checkin-automation/config/example.yml agents/checkin-automation/config/settings.yml

# Local Guide
cp agents/local-guide/config/example.yml agents/local-guide/config/settings.yml

# Review Manager
cp agents/review-manager/config/example.yml agents/review-manager/config/settings.yml
```

#### Edit agent configurations as needed:
```yaml
# Example: agents/booking-manager/config/settings.yml
property:
  name: "Fitzgerald's Guesthouse"
  rooms: 8
  base_rate: 85

pricing:
  dynamic_pricing: true
  minimum_rate: 65
  maximum_rate: 150

channels:
  booking_com:
    enabled: true
    auto_respond: true
  airbnb:
    enabled: true
    auto_respond: true
```

## Platform Integrations

### Booking.com Setup
1. Log into Booking.com Partner Hub
2. Go to API Integration section
3. Generate API credentials
4. Add credentials to `.env` file
5. Test connection: `npm run test:booking-com`

### Airbnb Setup
1. Visit Airbnb Partner Portal
2. Create new integration
3. Get API keys and listing ID
4. Add to configuration
5. Test: `npm run test:airbnb`

### WhatsApp Business Setup
1. Create WhatsApp Business account
2. Apply for WhatsApp Business API
3. Get API credentials from provider (Twilio, etc.)
4. Configure webhook URL
5. Test: `npm run test:whatsapp`

### Smart Lock Integration
```bash
# August Smart Lock
npm run setup:august

# Yale Connect
npm run setup:yale

# Schlage Encode
npm run setup:schlage

# Manual lock box (no API needed)
npm run setup:manual-locks
```

### Payment Processing Setup
```bash
# Stripe setup
npm run setup:stripe

# PayPal setup (alternative)
npm run setup:paypal
```

## First Launch

### Start All Agents
```bash
# Start all agents
npm run start:all

# Or start individually
npm run start:booking-manager
npm run start:guest-concierge
npm run start:checkin-automation
npm run start:local-guide
npm run start:review-manager
```

### Access the Dashboard
1. Open browser to `http://localhost:3000`
2. Login with admin credentials (set during setup)
3. Verify all agents are running
4. Review configuration status

### Initial Testing

#### Test Booking Flow
```bash
# Send test booking inquiry
npm run test:booking-inquiry

# Check availability
npm run test:availability

# Test pricing engine
npm run test:pricing
```

#### Test Guest Communications
```bash
# Test WhatsApp
npm run test:whatsapp-message

# Test email
npm run test:email-send

# Test SMS
npm run test:sms-send
```

#### Test Check-in Process
```bash
# Test document upload
npm run test:document-upload

# Test smart lock integration
npm run test:smart-locks

# Test checkout flow
npm run test:checkout
```

## Production Deployment

### Option 1: VPS Deployment
```bash
# Install on Ubuntu/Debian VPS
curl -fsSL https://deploy.floutlabs.com/vps | bash

# Configure domain and SSL
npm run setup:domain
npm run setup:ssl
```

### Option 2: Cloud Deployment
```bash
# Deploy to AWS
npm run deploy:aws

# Deploy to Google Cloud
npm run deploy:gcp

# Deploy to DigitalOcean
npm run deploy:digitalocean
```

### Option 3: Docker Deployment
```bash
# Build Docker images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

## Monitoring & Maintenance

### Health Checks
```bash
# Check system health
npm run health-check

# Check individual agents
npm run health-check:booking-manager
npm run health-check:guest-concierge
```

### Log Monitoring
```bash
# View real-time logs
npm run logs:tail

# View agent-specific logs
npm run logs:booking-manager
npm run logs:guest-concierge
```

### Backup Setup
```bash
# Setup automated backups
npm run setup:backups

# Manual backup
npm run backup:create

# Restore from backup
npm run backup:restore backup-filename.tar.gz
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 3000
lsof -i :3000

# Kill process
kill -9 [PID]

# Or change port in config
export PORT=3001
npm start
```

#### 2. Database Connection Issues
```bash
# Reset database
npm run db:reset

# Check connection
npm run db:test

# View database logs
npm run db:logs
```

#### 3. API Key Issues
```bash
# Test API connections
npm run test:apis

# Verify API keys
npm run verify:api-keys

# Reset API configuration
npm run setup:apis
```

#### 4. WhatsApp Webhook Issues
```bash
# Test webhook
npm run test:webhook

# Regenerate webhook
npm run setup:webhook

# Check webhook logs
npm run logs:webhook
```

### Getting Help

#### Self-Diagnosis
```bash
# Run full system diagnostic
npm run diagnose

# Generate support report
npm run support:report
```

#### Support Channels
- 📧 **Email**: support@floutlabs.com
- 📱 **WhatsApp**: +353 1 234 5678
- 💬 **Discord**: [Hospitality AI Community](https://discord.gg/hospitality-ai)
- 📖 **Documentation**: [docs.floutlabs.com](https://docs.floutlabs.com)

#### Emergency Support
For urgent issues affecting guest operations:
- 🚨 **Emergency Hotline**: +353 1 234 5678
- 📧 **Priority Email**: emergency@floutlabs.com
- Available 24/7 for critical issues

## Next Steps

After successful installation:

1. **Complete the Setup Wizard**: `npm run setup:wizard`
2. **Test All Integrations**: `npm run test:all`
3. **Review Configuration**: Check each agent's settings
4. **Train Your Team**: Use the provided training materials
5. **Monitor Performance**: Set up daily health checks
6. **Schedule Backups**: Configure automated backups
7. **Plan Gradual Rollout**: Start with one agent at a time

## Security Considerations

### Data Protection
- All guest data is encrypted at rest
- API keys stored securely with encryption
- Regular security updates applied automatically
- GDPR compliance built-in

### Access Control
- Multi-factor authentication supported
- Role-based access control
- Audit logging for all actions
- Secure webhook endpoints

### Network Security
- HTTPS enforced for all communications
- API rate limiting implemented
- Intrusion detection monitoring
- Regular security scans

---

**🎉 Congratulations! Your Hospitality AI Suite is now ready to transform your guest experience and boost your revenue.**

Next: [Configuration Guide](configuration.md) | [Integration Guide](integrations.md)