# Accounting Practice AI Toolkit - Setup Instructions

## Quick Start Guide for Eileen Murphy's Practice

### System Requirements
- **Python 3.9+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Redis 6+**
- **Ubuntu 20.04+ / Windows 10+ / macOS 12+**

### 1. Environment Setup

```bash
# Clone the toolkit
git clone https://github.com/accounting-ai-toolkit.git
cd accounting-ai-toolkit

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Install additional dependencies for Irish accounting
pip install irish-revenue-api pytesseract opencv-python
```

### 2. Database Configuration

```sql
-- PostgreSQL setup
CREATE DATABASE accounting_practice;
CREATE USER eileen_murphy WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE accounting_practice TO eileen_murphy;

-- Create essential tables
\c accounting_practice;

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    tax_number VARCHAR(20),
    vat_number VARCHAR(15),
    year_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    document_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(500),
    extracted_data JSONB,
    confidence_score DECIMAL(5,2),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tax_returns (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    return_type VARCHAR(50) NOT NULL,
    tax_year INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    due_date DATE,
    submitted_at TIMESTAMP,
    ros_reference VARCHAR(100)
);
```

### 3. Irish Revenue Integration

```bash
# Register for ROS digital certificate
# Visit: https://ros.ie/online-services/

# Configure ROS connection
export ROS_CERTIFICATE_PATH="/path/to/certificate.p12"
export ROS_CERTIFICATE_PASSWORD="certificate_password"
export ROS_TAX_ADVISER_NUMBER="your_adviser_number"

# Test ROS connection
python scripts/test_ros_connection.py
```

### 4. AI Agent Configuration

```python
# config/agents_config.py
AGENT_SETTINGS = {
    'revenue_compliance_manager': {
        'enabled': True,
        'ros_integration': True,
        'auto_filing': False,  # Set to True after testing
        'deadline_alerts': True,
        'email_notifications': True
    },
    'document_processor': {
        'enabled': True,
        'ocr_engine': 'tesseract',
        'confidence_threshold': 0.75,
        'auto_categorization': True,
        'vat_validation': True
    },
    'practice_management_hub': {
        'enabled': True,
        'time_tracking': True,
        'automated_workflows': True,
        'staff_assignments': True
    }
}

# Email configuration for notifications
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': 'eileen@murphyaccounting.ie',
    'password': 'app_specific_password',
    'from_email': 'eileen@murphyaccounting.ie'
}
```

### 5. Staff Training Program

#### Week 1: AI Fundamentals
```bash
# Run interactive training modules
python training/week1_fundamentals.py

# Topics covered:
# - How AI agents work
# - Benefits for accounting practice
# - Data security and GDPR compliance
# - Basic troubleshooting
```

#### Week 2: Revenue Compliance Manager
```bash
# Hands-on training with test data
python training/week2_revenue_compliance.py

# Practice activities:
# - Form 11 preparation
# - VAT return calculation
# - Corporation tax filing
# - Deadline management
```

#### Week 3: Document Processing
```bash
# Document processing workshop
python training/week3_document_processing.py

# Skills development:
# - Receipt scanning and validation
# - Bank statement reconciliation
# - Invoice processing
# - Error correction workflows
```

#### Week 4: Client Communications
```bash
# Client portal training
python training/week4_client_communications.py

# Communication skills:
# - Automated client updates
# - Query handling
# - Document requests
# - Progress reporting
```

### 6. Production Deployment

```bash
# Production environment setup
export ENVIRONMENT=production
export DEBUG=False
export DATABASE_URL="postgresql://user:pass@localhost/accounting_practice"
export REDIS_URL="redis://localhost:6379/0"

# Security configuration
export SECRET_KEY="your_secure_secret_key"
export JWT_SECRET="your_jwt_secret"
export ENCRYPTION_KEY="your_encryption_key"

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Verify all services are running
docker-compose ps
```

### 7. Monitoring and Maintenance

```bash
# Set up monitoring
pip install prometheus-client grafana-api

# Configure system monitoring
python scripts/setup_monitoring.py

# Schedule regular maintenance
crontab -e
# Add these lines:
# 0 2 * * * /path/to/daily_backup.sh
# 0 3 * * 0 /path/to/weekly_maintenance.sh
# 0 1 1 * * /path/to/monthly_reports.sh
```

### 8. Integration Testing

```bash
# Run comprehensive test suite
python -m pytest tests/ -v

# Test Irish Revenue integration
python tests/test_revenue_integration.py

# Test document processing accuracy
python tests/test_document_processing.py

# Load testing for peak season
python tests/load_test_peak_season.py
```

### 9. Data Migration from Current System

```python
# scripts/migrate_existing_data.py
import pandas as pd
from agents.revenue_compliance_manager import RevenueComplianceManager

def migrate_client_data():
    # Read existing client data
    clients_df = pd.read_csv('existing_data/clients.csv')

    # Transform to new format
    for _, client in clients_df.iterrows():
        # Create client record
        # Migrate historical data
        # Validate data integrity
        pass

# Run migration
python scripts/migrate_existing_data.py
```

### 10. Peak Season Preparation (October-November)

```bash
# Scale up infrastructure
docker-compose -f docker-compose.peak.yml up -d

# Pre-load client data
python scripts/preload_peak_season_data.py

# Configure automated workflows
python scripts/setup_peak_season_workflows.py

# Test capacity under load
python scripts/peak_season_load_test.py
```

## Security Checklist

### GDPR Compliance
- [ ] Data encryption at rest and in transit
- [ ] Client consent management
- [ ] Data retention policies
- [ ] Right to be forgotten implementation
- [ ] Data breach notification procedures

### Irish Revenue Security
- [ ] Digital certificate validation
- [ ] Secure API connections
- [ ] Audit trail maintenance
- [ ] Access control implementation
- [ ] Regular security updates

### Practice Security
- [ ] Staff access controls
- [ ] Multi-factor authentication
- [ ] Regular password updates
- [ ] Secure document storage
- [ ] Backup and recovery testing

## Troubleshooting Common Issues

### ROS Connection Problems
```bash
# Check certificate validity
openssl pkcs12 -in certificate.p12 -noout -info

# Test network connectivity
curl -I https://ros.ie

# Verify tax number format
python scripts/validate_tax_number.py
```

### Document Processing Issues
```bash
# Check OCR installation
tesseract --version

# Test image preprocessing
python scripts/test_image_processing.py

# Validate document formats
python scripts/check_document_formats.py
```

### Performance Optimization
```bash
# Monitor system resources
python scripts/monitor_resources.py

# Optimize database queries
python scripts/optimize_database.py

# Cache frequently accessed data
python scripts/setup_caching.py
```

## Support Contacts

- **Technical Support**: tech-support@accounting-ai-toolkit.com
- **Irish Revenue Queries**: revenue-support@accounting-ai-toolkit.com
- **Training Support**: training@accounting-ai-toolkit.com
- **Emergency Support**: +353-1-234-5678 (24/7)

## Success Metrics Tracking

```python
# scripts/track_success_metrics.py
def track_monthly_metrics():
    metrics = {
        'time_saved_hours': calculate_time_savings(),
        'cost_reduction_euro': calculate_cost_reduction(),
        'accuracy_improvement': calculate_accuracy_improvement(),
        'client_satisfaction': get_client_satisfaction_scores(),
        'deadline_compliance': calculate_deadline_compliance()
    }

    # Generate monthly report
    generate_monthly_report(metrics)

# Schedule monthly reporting
# 0 9 1 * * python scripts/track_success_metrics.py
```

---

**Next Steps:**
1. Complete system setup following this guide
2. Schedule staff training sessions
3. Begin with pilot group of 50 clients
4. Gradually expand to full 300-client base
5. Monitor and optimize performance

**Expected Timeline:** 6 weeks to full deployment
**Support Period:** 12 months included
**Training Period:** 4 weeks comprehensive training