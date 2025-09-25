# Local Pub AI Toolkit - Deployment Guide

## 🚀 Quick Start Deployment

### Prerequisites
- Python 3.8+
- Internet connection for cloud features
- Basic hardware (tablet/PC, mobile devices)
- Existing POS system (optional but recommended)

### Installation Steps

```bash
# 1. Clone or download the toolkit
git clone https://github.com/your-org/pub-ai-toolkit.git
cd pub-ai-toolkit

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your pub settings
cp config/pub_config.json.example config/pub_config.json
# Edit config/pub_config.json with your pub details

# 4. Run initial setup
python setup.py install

# 5. Start the system
python main.py
```

---

## 📋 Pre-Deployment Checklist

### Business Readiness
- [ ] Management buy-in and commitment
- [ ] Staff training schedule planned
- [ ] Budget approval (€25,000-30,000)
- [ ] Timeline agreed (8-week implementation)
- [ ] Success metrics defined

### Technical Requirements
- [ ] Stable internet connection (min 25 Mbps)
- [ ] Central tablet/PC for dashboard
- [ ] Staff mobile devices available
- [ ] POS system API documentation (if integrating)
- [ ] Current inventory data available

### Legal & Compliance
- [ ] Data protection compliance reviewed
- [ ] Staff privacy policies updated
- [ ] Customer data handling procedures
- [ ] Insurance coverage reviewed

---

## 🏗️ Phase-by-Phase Implementation

### Phase 1: Foundation (Week 1-2)
**Objective**: Establish core table and booking management

#### Technical Setup
```bash
# Initialize core agents
python agents/bar_table_manager.py --setup
python agents/staff_compliance_manager.py --setup

# Configure table layout
python config/setup_tables.py --layout your_pub_layout.json

# Test booking system
python tests/test_booking_system.py
```

#### Staff Training Topics
- New booking system interface
- Table status management
- Customer check-in process
- Basic troubleshooting

#### Success Metrics
- 95% booking accuracy
- 15% reduction in table turnover time
- Staff comfort with new system

### Phase 2: Stock & Inventory (Week 3-4)
**Objective**: Optimize stock management and reduce waste

#### Technical Setup
```bash
# Deploy stock controller
python agents/stock_cellar_controller.py --deploy

# Configure beer lines (if sensors available)
python config/setup_beer_lines.py

# Connect supplier APIs
python integrations/supplier_setup.py
```

#### Hardware Installation
- Temperature sensors for cellar
- Flow meters for beer lines (optional)
- Inventory tracking labels/QR codes

#### Staff Training Topics
- Stock level monitoring
- Wastage recording procedures
- Supplier order approvals
- Beer line quality checks

#### Success Metrics
- 20% reduction in wastage
- 95% stock accuracy
- Zero stock-outs

### Phase 3: Events & Marketing (Week 5-6)
**Objective**: Enhance customer experience and community engagement

#### Technical Setup
```bash
# Deploy entertainment hub
python agents/entertainment_events_hub.py --setup

# Configure social media accounts
python integrations/social_media_setup.py

# Set up community calendar integration
python integrations/community_calendar.py
```

#### Content Creation
- Social media account setup
- Event template creation
- Local partnership outreach
- Photography/content guidelines

#### Staff Training Topics
- Event booking procedures
- Social media content approval
- Community engagement protocols
- Customer feedback handling

#### Success Metrics
- 30% increase in midweek bookings
- 50% growth in social media engagement
- 3+ community partnerships established

### Phase 4: Full Integration (Week 7-8)
**Objective**: Complete system integration and optimization

#### Technical Setup
```bash
# Deploy marketing platform
python agents/local_marketing_platform.py --deploy

# Full system integration test
python tests/integration_test.py

# Performance optimization
python utils/optimize_system.py
```

#### Advanced Features
- Loyalty program launch
- Tourist information system
- Advanced analytics dashboard
- Performance monitoring

#### Staff Training Topics
- Loyalty program management
- Tourist service protocols
- Advanced system features
- Performance analytics review

#### Success Metrics
- All agents operational
- 85,000+ annual value target on track
- 90%+ staff satisfaction with system

---

## 🔧 Configuration Guide

### Basic Pub Configuration

Edit `config/pub_config.json`:

```json
{
  "pub_profile": {
    "name": "Your Pub Name",
    "location": "Your Location",
    "capacity": {
      "main_bar": 80,
      "function_room": 40,
      "beer_garden": 60
    }
  },
  "operating_hours": {
    "monday": {"open": "11:00", "close": "23:00"},
    "friday": {"open": "11:00", "close": "01:00"},
    "saturday": {"open": "11:00", "close": "01:00"}
  }
}
```

### Beer Line Configuration

```json
{
  "beer_lines": [
    {
      "line_id": "LINE1",
      "beer_name": "Guinness",
      "keg_size": 50.0,
      "optimal_temperature": 4.0,
      "optimal_pressure": 12.0
    }
  ]
}
```

### Staff Role Configuration

```json
{
  "staff_roles": {
    "manager": {
      "hourly_rate_range": [18.00, 25.00],
      "required_certifications": ["Personal Licence", "Food Safety Level 3"]
    },
    "bartender": {
      "hourly_rate_range": [12.50, 16.00],
      "required_certifications": ["Responsible Service of Alcohol"]
    }
  }
}
```

---

## 🔌 Integration Guide

### POS System Integration

Most Irish pubs use systems like:
- **Epos Now**: REST API available
- **Lightspeed**: Webhook support
- **Toast**: Real-time integration
- **Revel**: API documentation

#### Integration Steps:
1. Obtain API credentials from POS provider
2. Configure webhook endpoints
3. Test transaction synchronization
4. Validate inventory updates

```python
# Example POS integration
from integrations.pos_connector import POSConnector

pos = POSConnector(
    system_type="epos_now",
    api_key="your_api_key",
    webhook_url="https://your-pub.com/webhooks/pos"
)

# Test connection
if pos.test_connection():
    print("POS integration successful")
```

### Supplier API Connections

Common Irish suppliers with APIs:
- **Guinness Ireland**: Order management API
- **Heineken Ireland**: Inventory tracking
- **Musgrave**: Wholesale ordering system
- **BWG Foods**: Supply chain integration

#### Setup Process:
1. Contact supplier for API access
2. Obtain credentials and documentation
3. Configure automatic ordering thresholds
4. Test order placement and tracking

### Social Media Integration

Supported platforms:
- Facebook Business API
- Instagram Basic Display API
- Twitter API v2
- Google My Business API

#### Setup Steps:
1. Create developer accounts
2. Generate API tokens
3. Configure posting schedules
4. Set up monitoring webhooks

---

## 📊 Monitoring & Analytics

### System Health Dashboard

Access at `http://your-pub-system:8080/dashboard`

#### Key Metrics Monitored:
- **Agent Status**: All 5 agents operational status
- **Performance**: Response times, error rates
- **Business Metrics**: Daily revenue impact, customer satisfaction
- **System Resources**: Memory usage, API rate limits

### Daily Operations Report

Automated daily email containing:
- Booking success rate
- Stock levels and reorder alerts
- Event attendance predictions
- Staff schedule optimization
- Customer feedback summary

### Weekly Analytics

Comprehensive weekly report including:
- Financial impact analysis
- Customer behavior patterns
- Operational efficiency metrics
- Improvement recommendations

---

## 🛠️ Troubleshooting Guide

### Common Issues

#### Agent Not Starting
```bash
# Check logs
tail -f logs/pub_ai_system.log

# Restart specific agent
python agents/bar_table_manager.py --restart

# Full system restart
python main.py --restart-all
```

#### POS Integration Errors
```bash
# Test POS connection
python integrations/pos_test.py

# Refresh API tokens
python integrations/pos_connector.py --refresh-tokens

# Manual sync
python integrations/pos_sync.py --force
```

#### Beer Line Sensor Issues
```bash
# Check sensor connectivity
python hardware/sensor_check.py

# Recalibrate sensors
python hardware/sensor_calibration.py

# Switch to manual mode
python agents/stock_cellar_controller.py --manual-mode
```

### Emergency Procedures

#### System Failure
1. Switch to manual operations mode
2. Contact support immediately
3. Use backup procedures
4. Document any data loss

#### Data Recovery
```bash
# Restore from backup
python utils/restore_backup.py --date 2024-01-15

# Export current data
python utils/export_data.py --format json

# Import data
python utils/import_data.py --file backup_data.json
```

---

## 📞 Support & Maintenance

### Support Channels
- **24/7 Emergency**: +353 1 XXX-XXXX
- **Email Support**: support@pubai.ie
- **Online Portal**: https://support.pubai.ie
- **Documentation**: https://docs.pubai.ie

### Maintenance Schedule

#### Daily Automated Tasks
- System health checks
- Data backups
- Performance monitoring
- Security scans

#### Weekly Tasks
- Performance optimization
- Data analysis reports
- System updates check
- User feedback review

#### Monthly Tasks
- Full system backup
- Security audit
- Performance review
- Feature updates

### Service Level Agreement (SLA)

- **System Uptime**: 99.5% guaranteed
- **Response Time**: < 4 hours for critical issues
- **Resolution Time**: < 24 hours for critical issues
- **Data Backup**: Daily with 30-day retention

---

## 🔒 Security & Compliance

### Data Protection
- All customer data encrypted at rest and in transit
- GDPR compliance built-in
- Regular security audits
- Staff access controls

### Backup Strategy
- **Frequency**: Every 6 hours
- **Retention**: 30 days
- **Location**: Cloud and local backup
- **Testing**: Monthly restore tests

### Access Control
- Role-based permissions
- Multi-factor authentication
- Session timeouts
- Audit logging

---

## 📈 Scaling & Growth

### Performance Optimization

As your pub grows, the system scales automatically:
- **Low usage**: Single server deployment
- **Medium usage**: Load balancing
- **High usage**: Distributed architecture

### Feature Expansion

Additional modules available:
- **Advanced Analytics**: Detailed customer insights
- **Multi-location**: Chain management
- **Integration Hub**: Additional third-party services
- **Custom Development**: Bespoke features

### Success Measurement

Track your ROI with built-in metrics:
- Cost reduction tracking
- Revenue growth attribution
- Efficiency improvements
- Customer satisfaction scores

---

*For detailed technical documentation, visit our [Developer Portal](https://developers.pubai.ie)*

*Need implementation support? Schedule a consultation at [pubai.ie/contact](https://pubai.ie/contact)*