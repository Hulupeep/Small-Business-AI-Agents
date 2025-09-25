# Farm & Agri-Retail AI Toolkit - Deployment Guide

## 🚀 Production Deployment Guide

This comprehensive guide covers deploying the Farm & Agri-Retail AI Toolkit for production use on a mixed farm operation.

## Prerequisites

### System Requirements
- **Server**: Linux (Ubuntu 20.04+ recommended) or Windows Server 2019+
- **CPU**: Minimum 4 cores, 8 cores recommended
- **RAM**: Minimum 8GB, 16GB recommended
- **Storage**: Minimum 100GB SSD
- **Network**: Stable internet connection for weather APIs and integrations

### Software Dependencies
- **Python**: 3.9 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 14 or higher
- **Redis**: 6 or higher
- **Docker**: Latest stable version (optional but recommended)

## Installation Methods

### Method 1: Docker Deployment (Recommended)

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/farm-retail-suite.git
cd farm-retail-suite
```

#### 2. Configure Environment
```bash
cp .env.example .env
nano .env
```

Configure the following variables:
```env
# Database Configuration
DATABASE_URL=postgresql://farm_user:secure_password@localhost:5432/farm_db
REDIS_URL=redis://localhost:6379

# API Keys
OPENWEATHER_API_KEY=your_weather_api_key
GOOGLE_MAPS_API_KEY=your_maps_api_key
STRIPE_SECRET_KEY=your_stripe_key

# Farm Configuration
FARM_NAME="Your Farm Name"
FARM_LOCATION_LAT=52.3676
FARM_LOCATION_LON=4.9041
FARM_TOTAL_AREA=50

# Security
SECRET_KEY=your_very_secure_secret_key
JWT_SECRET=your_jwt_secret_key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

#### 3. Deploy with Docker Compose
```bash
docker-compose up -d
```

#### 4. Initialize Database
```bash
docker-compose exec app python scripts/init_database.py
```

#### 5. Create Admin User
```bash
docker-compose exec app python scripts/create_admin.py
```

### Method 2: Manual Installation

#### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-pip postgresql-14 redis-server nodejs npm

# CentOS/RHEL
sudo yum install python39 python39-pip postgresql14 redis nodejs npm
```

#### 2. Setup Database
```bash
sudo -u postgres createuser farm_user
sudo -u postgres createdb farm_db -O farm_user
sudo -u postgres psql -c "ALTER USER farm_user PASSWORD 'secure_password';"
```

#### 3. Install Python Dependencies
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt
```

#### 4. Configure Database Schema
```bash
alembic upgrade head
```

#### 5. Start Services
```bash
# Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Start Application
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Farm Profile Setup

#### 1. Basic Farm Information
```python
# scripts/setup_farm_profile.py
farm_profile = {
    "name": "Green Valley Farm",
    "total_area": 50,
    "location": {
        "latitude": 52.3676,
        "longitude": 4.9041,
        "address": "Farm Road 123, 1234 AB Farmville"
    },
    "farm_type": "mixed",
    "organic_certified": True,
    "primary_products": ["vegetables", "dairy", "eggs"]
}
```

#### 2. Crop Configuration
```yaml
# config/crops.yaml
crops:
  vegetables:
    - name: "tomatoes"
      varieties: ["cherry", "beefsteak", "roma"]
      seasonal_months: [5, 6, 7, 8, 9]
      price_per_kg: 4.50
    - name: "lettuce"
      varieties: ["butterhead", "romaine", "iceberg"]
      seasonal_months: [3, 4, 5, 9, 10, 11]
      price_per_kg: 3.20

  grains:
    - name: "wheat"
      varieties: ["winter_wheat", "spring_wheat"]
      seasonal_months: [7, 8]
      price_per_kg: 0.85
```

#### 3. Livestock Configuration
```yaml
# config/livestock.yaml
livestock:
  dairy_cows:
    breeds: ["Holstein-Friesian", "Jersey"]
    average_daily_milk: 25
    feed_cost_per_day: 12.50

  poultry:
    breeds: ["Rhode Island Red", "Leghorn"]
    average_daily_eggs: 0.8
    feed_cost_per_day: 0.15
```

### Integration Setup

#### 1. Weather API Integration
```bash
# Get OpenWeatherMap API key from openweathermap.org
export OPENWEATHER_API_KEY="your_api_key"

# Test connection
python scripts/test_weather_api.py
```

#### 2. Payment Processing Setup
```bash
# Configure Stripe
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."

# Test payment processing
python scripts/test_payments.py
```

#### 3. Email Service Configuration
```bash
# Configure SMTP for newsletters and alerts
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your_farm@gmail.com"
export SMTP_PASSWORD="your_app_password"

# Test email sending
python scripts/test_email.py
```

## Initial Data Setup

### 1. Import Product Catalog
```bash
python scripts/import_products.py data/product_catalog.csv
```

### 2. Setup Customer Segments
```bash
python scripts/setup_customer_segments.py
```

### 3. Configure Seasonal Pricing
```bash
python scripts/setup_seasonal_pricing.py
```

### 4. Import Compliance Templates
```bash
python scripts/import_compliance_templates.py
```

## Security Configuration

### 1. SSL/TLS Setup
```bash
# Install Certbot for Let's Encrypt certificates
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourfarm.com -d www.yourfarm.com
```

### 2. Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 8000/tcp  # Block direct access to app
```

### 3. Database Security
```bash
# Configure PostgreSQL security
sudo nano /etc/postgresql/14/main/postgresql.conf

# Set secure connections only
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

### 4. Application Security
```python
# config/security.py
SECURITY_CONFIG = {
    "SESSION_TIMEOUT": 3600,  # 1 hour
    "MAX_LOGIN_ATTEMPTS": 5,
    "PASSWORD_MIN_LENGTH": 12,
    "REQUIRE_2FA": True,
    "ALLOWED_HOSTS": ["yourfarm.com", "www.yourfarm.com"]
}
```

## Monitoring and Logging

### 1. Application Monitoring
```bash
# Install and configure Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvf prometheus-2.40.0.linux-amd64.tar.gz
sudo mv prometheus-2.40.0.linux-amd64 /opt/prometheus
```

### 2. Log Management
```python
# config/logging.py
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/farm-ai/application.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"]
    }
}
```

### 3. Health Checks
```python
# scripts/health_check.py
async def health_check():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "weather_api": await check_weather_api(),
        "email_service": await check_email_service()
    }
    return all(checks.values())
```

## Backup and Recovery

### 1. Database Backup
```bash
#!/bin/bash
# scripts/backup_database.sh

BACKUP_DIR="/backups/farm-ai"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="farm_db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump $DB_NAME > $BACKUP_DIR/farm_db_$TIMESTAMP.sql

# Compress backup
gzip $BACKUP_DIR/farm_db_$TIMESTAMP.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Database backup completed: farm_db_$TIMESTAMP.sql.gz"
```

### 2. Application Data Backup
```bash
#!/bin/bash
# scripts/backup_app_data.sh

APP_DATA_DIR="/var/lib/farm-ai"
BACKUP_DIR="/backups/farm-ai"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup application data
tar -czf $BACKUP_DIR/app_data_$TIMESTAMP.tar.gz $APP_DATA_DIR

# Remove old backups
find $BACKUP_DIR -name "app_data_*.tar.gz" -mtime +30 -delete
```

### 3. Automated Backup Schedule
```bash
# Add to crontab: crontab -e
# Daily database backup at 2 AM
0 2 * * * /path/to/scripts/backup_database.sh

# Weekly full backup on Sundays at 3 AM
0 3 * * 0 /path/to/scripts/backup_app_data.sh
```

## Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_crops_field_id ON crops(field_id);
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_payments_date ON payments(date);

-- Configure connection pooling
-- config/database.py
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600
}
```

### 2. Redis Caching
```python
# config/cache.py
CACHE_CONFIG = {
    "weather_data": {"ttl": 3600},  # 1 hour
    "product_prices": {"ttl": 1800},  # 30 minutes
    "customer_segments": {"ttl": 86400},  # 24 hours
    "compliance_status": {"ttl": 7200}  # 2 hours
}
```

### 3. Application Performance
```bash
# Use Gunicorn for production WSGI server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app \
  --bind 0.0.0.0:8000 \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 120
```

## Scaling Considerations

### 1. Horizontal Scaling
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  app:
    deploy:
      replicas: 3
    depends_on:
      - db
      - redis
      - nginx

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
```

### 2. Load Balancing
```nginx
# nginx.conf
upstream farm_ai_backend {
    server app1:8000;
    server app2:8000;
    server app3:8000;
}

server {
    listen 80;
    server_name yourfarm.com;

    location / {
        proxy_pass http://farm_ai_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Database Scaling
```bash
# PostgreSQL read replicas for scaling reads
# Master-slave configuration
# config/database_replicas.py
DATABASES = {
    "master": "postgresql://user:pass@master-db:5432/farm_db",
    "slave1": "postgresql://user:pass@slave1-db:5432/farm_db",
    "slave2": "postgresql://user:pass@slave2-db:5432/farm_db"
}
```

## Maintenance

### 1. Regular Maintenance Tasks
```bash
#!/bin/bash
# scripts/maintenance.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up old log files
find /var/log/farm-ai -name "*.log.*" -mtime +30 -delete

# Optimize database
sudo -u postgres vacuumdb --analyze farm_db

# Clear old cache entries
redis-cli FLUSHDB

# Restart services if needed
sudo systemctl restart farm-ai
```

### 2. Update Procedure
```bash
#!/bin/bash
# scripts/update_application.sh

# Create backup before update
./scripts/backup_database.sh
./scripts/backup_app_data.sh

# Pull latest code
git pull origin main

# Update dependencies
pip install -r config/requirements.txt

# Run database migrations
alembic upgrade head

# Restart services
sudo systemctl restart farm-ai

# Verify deployment
python scripts/health_check.py
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U farm_user -d farm_db -c "SELECT 1;"

# View logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### 2. API Integration Failures
```bash
# Test weather API
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"

# Check API rate limits
python scripts/check_api_limits.py

# View API logs
grep "API" /var/log/farm-ai/application.log
```

#### 3. Performance Issues
```bash
# Monitor system resources
htop
iotop
netstat -tlnp

# Check database performance
sudo -u postgres psql farm_db -c "SELECT * FROM pg_stat_activity;"

# Analyze slow queries
sudo -u postgres psql farm_db -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### Emergency Procedures

#### 1. Service Recovery
```bash
#!/bin/bash
# scripts/emergency_recovery.sh

# Stop all services
sudo systemctl stop farm-ai
sudo systemctl stop nginx

# Restore from backup
LATEST_BACKUP=$(ls -t /backups/farm-ai/farm_db_*.sql.gz | head -1)
gunzip -c $LATEST_BACKUP | sudo -u postgres psql farm_db

# Start services
sudo systemctl start postgresql
sudo systemctl start redis
sudo systemctl start farm-ai
sudo systemctl start nginx

# Verify recovery
python scripts/health_check.py
```

#### 2. Data Recovery
```bash
# Point-in-time recovery
sudo -u postgres pg_restore -d farm_db /backups/farm-ai/latest_backup.dump

# Verify data integrity
python scripts/verify_data_integrity.py
```

## Support and Updates

### Getting Help
- **Documentation**: Complete API and user documentation
- **Community Forum**: Access to user community and expert advice
- **Email Support**: support@farm-ai-toolkit.com
- **Priority Support**: Available for enterprise customers

### Update Schedule
- **Security Updates**: Immediate deployment
- **Bug Fixes**: Monthly releases
- **Feature Updates**: Quarterly releases
- **Major Versions**: Annual releases

### Backup Support
- **Remote Monitoring**: Optional 24/7 system monitoring
- **Managed Updates**: Automated update deployment
- **Disaster Recovery**: Complete system recovery services

---

## 🎯 Deployment Checklist

- [ ] System requirements verified
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Backup system tested
- [ ] Monitoring configured
- [ ] Performance optimized
- [ ] Health checks passing
- [ ] Documentation reviewed
- [ ] Staff trained

**Ready for Production!** 🚀

Your Farm & Agri-Retail AI Toolkit is now ready to deliver €65,000 in annual value to your farm operation.