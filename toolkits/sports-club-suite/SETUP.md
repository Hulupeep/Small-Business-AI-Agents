# Sports Club Management Setup Guide

## Quick Start (5 minutes)

1. **Clone/Download the code**
   ```bash
   git clone [repository-url]
   cd sports-club-suite
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Run the demo**
   ```bash
   cd examples
   python realistic_demo.py
   ```

## Production Setup (2-3 weeks)

### 1. Server Setup

**Minimum Requirements:**
- Linux VPS (Ubuntu 20.04+ recommended)
- 2GB RAM, 20GB storage
- Python 3.8+
- SSL certificate

**Recommended Providers:**
- DigitalOcean: €25-50/month
- Linode: €25-40/month
- AWS: €30-60/month

### 2. Service Accounts Required

**Stripe (Payment Processing):**
1. Create account at stripe.com
2. Get API keys from dashboard
3. Cost: 1.4% + €0.25 per transaction

**Twilio (SMS):**
1. Create account at twilio.com
2. Get Account SID, Auth Token, Phone Number
3. Cost: ~€0.04 per SMS

**SendGrid (Email):**
1. Create account at sendgrid.com
2. Get API key
3. Cost: Free for first 100 emails/day

### 3. Environment Setup

Create `.env` file with your credentials:
```bash
# Database
DATABASE_PATH=/path/to/club_database.db

# Stripe Payment Processing
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Twilio SMS
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+353...

# SendGrid Email
SENDGRID_API_KEY=SG...
CLUB_EMAIL=noreply@yourclub.com
```

### 4. Database Initialization

```bash
cd src
python database.py
```

This creates the SQLite database with all required tables.

### 5. Initial Data Import

**From Spreadsheet:**
```bash
# Export your existing member data as CSV
# Run import script (would need to be created)
python import_members.py members.csv
```

**Manual Entry:**
Use the member registration system to add members one by one.

### 6. Testing

```bash
# Test member registration
python member_registration_manager.py

# Test payment processing (requires Stripe keys)
python payment_processor.py

# Test communications (requires Twilio/SendGrid keys)
python communication_manager.py
```

## Security Checklist

- [ ] SSL certificate installed
- [ ] Database backups configured (daily)
- [ ] Environment variables secured (not in code)
- [ ] Regular software updates scheduled
- [ ] Access logs monitored
- [ ] Stripe webhook security configured

## Maintenance Tasks

**Weekly:**
- Check backup files
- Review error logs
- Update member records

**Monthly:**
- Software updates
- Performance review
- Cost analysis

**Quarterly:**
- Full system backup test
- Security review
- User training refresh

## Common Issues

**Database locked:**
- Ensure only one process accesses database
- Check file permissions

**SMS not sending:**
- Verify Twilio credentials
- Check phone number format
- Confirm account balance

**Email bounces:**
- Validate email addresses
- Check SendGrid reputation
- Review spam settings

**Payment failures:**
- Test Stripe webhooks
- Check API key permissions
- Verify SSL certificate

## Support

**Self-Help:**
1. Check error logs first
2. Review configuration
3. Test individual components

**Paid Support:**
- Email: agents@hubduck.com
- Response: 48 hours
- Cost: €75/hour for customizations

## Data Migration

**From Existing System:**
1. Export data to CSV
2. Map fields to our database structure
3. Run import scripts
4. Validate data integrity
5. Test functionality

**Backup Strategy:**
- Daily automated backups
- Weekly off-site backup
- Monthly backup restoration test
- Emergency recovery plan documented

---

**Remember:** This is working software, not magic. Plan for setup time and learning curve.