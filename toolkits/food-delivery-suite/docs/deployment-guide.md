# 🚀 Food Delivery AI Toolkit - Deployment Guide

This guide walks you through deploying the Food Delivery AI Toolkit for your restaurant or takeaway.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 20GB free space
- **Network**: Stable internet connection

### Required Services
- **PostgreSQL**: 12+ (for data storage)
- **Redis**: 6+ (for caching and sessions)
- **NGINX**: 1.18+ (web server, optional)

## 🔧 Installation Steps

### Step 1: System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.8 python3-pip python3-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install NGINX (optional)
sudo apt install nginx -y
```

### Step 2: Database Setup

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE food_delivery_ai;
CREATE USER ai_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE food_delivery_ai TO ai_user;
\q
EOF

# Test connection
psql -h localhost -U ai_user -d food_delivery_ai -c "SELECT version();"
```

### Step 3: Application Setup

```bash
# Clone or copy the toolkit
mkdir -p /opt/food-delivery-ai
cd /opt/food-delivery-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r config/requirements.txt

# Create environment configuration
cp config/.env.example .env
nano .env  # Edit with your settings
```

### Step 4: Environment Configuration

Edit your `.env` file with your specific settings:

```bash
# Environment Settings
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=food_delivery_ai
DB_USER=ai_user
DB_PASSWORD=secure_password_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Delivery Platform APIs (get these from platform partners)
UBER_EATS_API_KEY=your_uber_eats_key
DELIVEROO_API_KEY=your_deliveroo_key
JUST_EAT_API_KEY=your_just_eat_key

# Notification Services
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+353xxxxxxxxx
SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=noreply@yourrestaurant.com

# Payment Processing
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Restaurant Details
RESTAURANT_NAME=Your Restaurant Name
RESTAURANT_ADDRESS=Your Full Address
RESTAURANT_LATITUDE=53.3498
RESTAURANT_LONGITUDE=-6.2603
```

### Step 5: Database Migration

```bash
# Initialize database schema
python -c "
from src.database import init_database
init_database()
print('Database initialized successfully!')
"
```

### Step 6: Service Configuration

Create systemd service file:

```bash
sudo nano /etc/systemd/system/food-delivery-ai.service
```

Add the following content:

```ini
[Unit]
Description=Food Delivery AI Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/food-delivery-ai
Environment=PATH=/opt/food-delivery-ai/venv/bin
ExecStart=/opt/food-delivery-ai/venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Step 7: NGINX Configuration (Optional)

Create NGINX configuration:

```bash
sudo nano /etc/nginx/sites-available/food-delivery-ai
```

Add configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/food-delivery-ai/static;
        expires 30d;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/food-delivery-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 8: Start Services

```bash
# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl start food-delivery-ai
sudo systemctl enable food-delivery-ai

# Check status
sudo systemctl status food-delivery-ai

# View logs
sudo journalctl -u food-delivery-ai -f
```

## 🔒 Security Configuration

### Firewall Setup

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow from localhost to any port 5432  # PostgreSQL
sudo ufw allow from localhost to any port 6379  # Redis
sudo ufw enable
```

### SSL Certificate (Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Database Security

```bash
# Secure PostgreSQL
sudo -u postgres psql << EOF
ALTER USER ai_user WITH PASSWORD 'very_secure_password_here';
\q
EOF

# Update pg_hba.conf for security
sudo nano /etc/postgresql/12/main/pg_hba.conf
# Change 'trust' to 'md5' for local connections
```

## 📊 Monitoring Setup

### Log Configuration

```bash
# Create log directory
sudo mkdir -p /var/log/food-delivery-ai
sudo chown www-data:www-data /var/log/food-delivery-ai

# Configure log rotation
sudo nano /etc/logrotate.d/food-delivery-ai
```

Add logrotate configuration:

```
/var/log/food-delivery-ai/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    postrotate
        systemctl reload food-delivery-ai
    endscript
}
```

### Health Monitoring

Create health check script:

```bash
nano /opt/food-delivery-ai/scripts/health-check.sh
```

```bash
#!/bin/bash
# Health check script

HEALTH_URL="http://localhost:8000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "Service is healthy"
    exit 0
else
    echo "Service is unhealthy (HTTP $RESPONSE)"
    exit 1
fi
```

Add to crontab:

```bash
sudo crontab -e
# Add: */5 * * * * /opt/food-delivery-ai/scripts/health-check.sh
```

## 🚀 Production Deployment

### Performance Optimization

```bash
# Update settings for production
nano .env
```

Set production optimizations:

```bash
# Performance settings
WORKERS=4
MAX_CONNECTIONS=1000
KEEPALIVE_TIMEOUT=65

# Cache settings
REDIS_CACHE_TTL=3600
ENABLE_QUERY_CACHE=True

# AI optimizations
ENABLE_ML_FORECASTING=True
ENABLE_DYNAMIC_PRICING=True
BATCH_PROCESSING=True
```

### Backup Configuration

Create backup script:

```bash
nano /opt/food-delivery-ai/scripts/backup.sh
```

```bash
#!/bin/bash
# Database backup script

BACKUP_DIR="/opt/backups/food-delivery-ai"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U ai_user food_delivery_ai | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_backup_$DATE.sql.gz"
```

Schedule daily backups:

```bash
sudo crontab -e
# Add: 0 2 * * * /opt/food-delivery-ai/scripts/backup.sh
```

## 🔧 Integration Setup

### Delivery Platform Integration

1. **Uber Eats Integration**:
   ```bash
   # Register with Uber Eats Developer Portal
   # Get API credentials
   # Update .env with UBER_EATS_API_KEY
   ```

2. **Deliveroo Integration**:
   ```bash
   # Register with Deliveroo Partner API
   # Get API credentials
   # Update .env with DELIVEROO_API_KEY
   ```

3. **Just Eat Integration**:
   ```bash
   # Register with Just Eat Partner Portal
   # Get API credentials
   # Update .env with JUST_EAT_API_KEY
   ```

### Payment Integration

```bash
# Setup Stripe
# 1. Create Stripe account
# 2. Get API keys from dashboard
# 3. Update .env with keys
# 4. Configure webhooks for order updates
```

### SMS/Email Integration

```bash
# Setup Twilio for SMS
# 1. Create Twilio account
# 2. Get Account SID and Auth Token
# 3. Purchase phone number
# 4. Update .env with credentials

# Setup SendGrid for email
# 1. Create SendGrid account
# 2. Generate API key
# 3. Verify sender domain
# 4. Update .env with credentials
```

## 📱 Mobile App Setup (Optional)

### Frontend Deployment

```bash
# Build React Native app
cd mobile-app
npm install
npm run build

# Deploy to app stores
# Follow platform-specific deployment guides
```

### API Configuration

```bash
# Update mobile app API endpoints
nano mobile-app/src/config.js
```

```javascript
export const API_CONFIG = {
  baseURL: 'https://your-domain.com/api',
  timeout: 10000,
  retries: 3
};
```

## 🔍 Testing & Validation

### Deployment Testing

```bash
# Test all endpoints
python scripts/test_deployment.py

# Load testing
pip install locust
locust -f scripts/load_test.py --host=http://localhost:8000
```

### Integration Testing

```bash
# Test delivery platform connections
python scripts/test_integrations.py

# Test notification services
python scripts/test_notifications.py

# Test payment processing
python scripts/test_payments.py
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Daily**:
   - Check system logs
   - Monitor performance metrics
   - Verify backup completion

2. **Weekly**:
   - Update system packages
   - Review error logs
   - Check disk space

3. **Monthly**:
   - Security updates
   - Database optimization
   - Performance review

### Troubleshooting

**Common Issues**:

1. **Service won't start**:
   ```bash
   # Check logs
   sudo journalctl -u food-delivery-ai -n 50

   # Check configuration
   python -c "from config.settings import settings; print('Config OK')"
   ```

2. **Database connection issues**:
   ```bash
   # Test connection
   psql -h localhost -U ai_user -d food_delivery_ai -c "SELECT 1;"
   ```

3. **API integration failures**:
   ```bash
   # Check API credentials
   python scripts/test_api_connections.py
   ```

### Support Contacts

- **Technical Support**: support@fooddeliveryai.com
- **Emergency**: +353 1 234 5678
- **Documentation**: https://docs.fooddeliveryai.com

---

## 🎉 Deployment Complete!

Your Food Delivery AI system is now deployed and ready to revolutionize your restaurant operations!

### Next Steps:
1. 📊 Access your dashboard at: `https://your-domain.com`
2. 📱 Download the mobile app for real-time monitoring
3. 📚 Review the user manual for daily operations
4. 🎯 Schedule training session with your team

**Welcome to the future of food delivery management!** 🚀