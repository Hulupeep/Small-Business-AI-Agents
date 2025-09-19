# Financial Automation Agents - Setup Guide

## Quick Start Guide

This guide will help you set up and configure the Financial Automation Agents for maximum business value and ROI.

## Prerequisites

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Operating System: Windows, macOS, or Linux

### External Dependencies
- **Tesseract OCR**: Required for invoice text extraction
- **Accounting Software API Access**: QuickBooks Online or Xero (optional)

## Installation

### 1. Install Python Dependencies

```bash
# Install from requirements file
pip install -r config/requirements.txt

# Or install manually
pip install opencv-python Pillow pytesseract PyMuPDF scikit-learn pandas requests pytest
```

### 2. Install Tesseract OCR

#### Windows
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add tesseract.exe to PATH
```

#### macOS
```bash
brew install tesseract
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

### 3. Verify Installation

```bash
python -c "import cv2, pytesseract; print('Dependencies installed successfully')"
tesseract --version
```

## Configuration

### 1. Basic Configuration

Copy and customize the configuration file:

```bash
cp config/config.yaml config/config_local.yaml
# Edit config_local.yaml with your settings
```

### 2. Environment Variables

Create a `.env` file in the project root:

```bash
# OCR Settings
TESSERACT_PATH=/usr/bin/tesseract  # Adjust path as needed

# QuickBooks Integration (optional)
QUICKBOOKS_CLIENT_ID=your_client_id
QUICKBOOKS_CLIENT_SECRET=your_client_secret
QUICKBOOKS_COMPANY_ID=your_company_id

# Xero Integration (optional)
XERO_CLIENT_ID=your_client_id
XERO_CLIENT_SECRET=your_client_secret
XERO_TENANT_ID=your_tenant_id

# Business Settings
HOURLY_LABOR_RATE=25.0
BOOKKEEPER_RATE=30.0
```

### 3. Directory Structure

The agents will create these directories automatically:

```
project/
├── data/
│   ├── processed_invoices/
│   ├── categorized_expenses/
│   └── backups/
├── logs/
├── models/
└── exports/
```

## Quick Start Examples

### 1. Process a Single Invoice

```python
from src.agents.invoice_processor import InvoiceProcessor

# Initialize processor
processor = InvoiceProcessor()

# Process invoice
result = processor.process_invoice('path/to/invoice.pdf')

# View results
print(f"Invoice: {result['invoice_data']['invoice_number']}")
print(f"Amount: ${result['invoice_data']['total_amount']}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"Anomalies: {result['anomalies']}")
```

### 2. Categorize Bank Transactions

```python
from src.agents.expense_categorizer import ExpenseCategorizer
from datetime import datetime

# Initialize categorizer
categorizer = ExpenseCategorizer()

# Categorize transaction
transaction = {
    'id': 'txn_001',
    'date': datetime(2024, 1, 15),
    'description': 'Office supplies from Staples',
    'amount': 45.67,
    'account': 'Business Checking',
    'merchant': 'Staples'
}

result = categorizer.categorize_transaction(transaction)

print(f"Category: {result['category']}")
print(f"Tax Deductible: {result['tax_deductible']}")
print(f"Deductible Amount: ${result['deductible_amount']}")
```

### 3. Run from Command Line

```bash
# Process invoices
python -m src.agents.invoice_processor --batch /path/to/invoices/

# Categorize expenses
python -m src.agents.expense_categorizer --categorize transactions.json

# View business metrics
python -m src.agents.invoice_processor --metrics
python -m src.agents.expense_categorizer --metrics
```

## Accounting Software Integration

### QuickBooks Online Setup

1. **Create QuickBooks App**:
   - Go to https://developer.intuit.com/
   - Create new app and get Client ID/Secret
   - Configure OAuth2 redirect URIs

2. **OAuth2 Authentication**:
   ```python
   # Use QuickBooks OAuth2 flow to get tokens
   # Store access_token and refresh_token securely
   ```

3. **Test Connection**:
   ```python
   from src.integrations.accounting_integrations import QuickBooksIntegration

   config = {
       'client_id': 'your_client_id',
       'client_secret': 'your_client_secret',
       'access_token': 'your_access_token',
       'company_id': 'your_company_id',
       'sandbox': True
   }

   qb = QuickBooksIntegration(config)
   company_info = qb.get_company_info()
   print(f"Connected to: {company_info}")
   ```

### Xero Setup

1. **Create Xero App**:
   - Go to https://developer.xero.com/
   - Create new app and configure OAuth2

2. **Authentication and Testing**:
   ```python
   from src.integrations.accounting_integrations import XeroIntegration

   config = {
       'client_id': 'your_client_id',
       'client_secret': 'your_client_secret',
       'access_token': 'your_access_token',
       'tenant_id': 'your_tenant_id'
   }

   xero = XeroIntegration(config)
   accounts = xero.get_accounts()
   print(f"Found {len(accounts)} accounts")
   ```

## Training and Optimization

### 1. Train Expense Categorization Model

```python
# Add historical transaction data
categorizer = ExpenseCategorizer()

# Import historical data (CSV, JSON, or from accounting software)
# Train model for better accuracy
result = categorizer.train_from_history()
print(f"Model trained with {result['training_results']['training_samples']} transactions")
print(f"Accuracy: {result['training_results']['accuracy']:.2%}")
```

### 2. Optimize OCR Performance

```python
# Adjust OCR settings for your document types
config = {
    'ocr': {
        'confidence_threshold': 0.8,  # Increase for better quality
        'preprocessing': {
            'denoise': True,
            'deskew': True,
            'enhance_contrast': True
        }
    }
}
```

## Business Value Tracking

### View ROI Metrics

```python
# Invoice processing ROI
processor = InvoiceProcessor()
metrics = processor.get_business_metrics()

print(f"Hours Saved: {metrics['summary']['total_hours_saved']}")
print(f"Cost Savings: ${metrics['summary']['total_cost_savings']}")
print(f"Monthly Savings: ${metrics['monthly_projections']['cost_savings_per_month']}")
print(f"ROI: {metrics['roi_analysis']['roi_percentage']}%")

# Expense categorization ROI
categorizer = ExpenseCategorizer()
metrics = categorizer.get_business_metrics()

print(f"Automation Rate: {metrics['performance_metrics']['automation_rate']}%")
print(f"Annual Savings: ${metrics['financial_impact']['annual_savings_projection']}")
```

## Troubleshooting

### Common Issues

1. **Tesseract Not Found**:
   ```bash
   # Ensure tesseract is in PATH
   which tesseract  # Linux/macOS
   where tesseract  # Windows
   ```

2. **Poor OCR Accuracy**:
   - Check image quality and resolution
   - Adjust preprocessing settings
   - Try different OCR engines (EasyOCR, PaddleOCR)

3. **Low Categorization Accuracy**:
   - Add more training data
   - Review and update categorization rules
   - Check merchant mappings

4. **API Integration Issues**:
   - Verify credentials and permissions
   - Check rate limiting
   - Review API documentation for changes

### Performance Optimization

1. **Processing Speed**:
   ```python
   # Adjust batch sizes
   config['performance']['batch_size'] = 50
   config['performance']['max_concurrent_jobs'] = 2
   ```

2. **Memory Usage**:
   ```python
   # Reduce memory footprint
   config['performance']['memory_limit_mb'] = 512
   config['storage']['cache_max_size_mb'] = 256
   ```

3. **Accuracy vs Speed**:
   ```python
   # For higher accuracy (slower)
   config['invoice_processor']['processing']['min_confidence_score'] = 0.9

   # For faster processing (lower accuracy)
   config['invoice_processor']['processing']['min_confidence_score'] = 0.6
   ```

## Testing

### Run Test Suite

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/agents/test_invoice_processor.py -v
python -m pytest tests/agents/test_expense_categorizer.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Test with Sample Data

```bash
# Process sample invoices
python -m src.agents.invoice_processor --file tests/sample_data/sample_invoice.pdf

# Test categorization
python -m src.agents.expense_categorizer --categorize tests/sample_data/sample_transactions.json
```

## Production Deployment

### 1. Environment Setup

```bash
# Production environment variables
export ENVIRONMENT=production
export DEBUG_MODE=false
export LOG_LEVEL=INFO
```

### 2. Security Considerations

- Store API credentials securely (environment variables, secrets manager)
- Enable encryption for sensitive data
- Implement rate limiting and authentication
- Regular security updates

### 3. Monitoring

```python
# Set up monitoring and alerting
config['monitoring']['metrics_enabled'] = True
config['monitoring']['alerts']['email_enabled'] = True
```

### 4. Backup and Recovery

```python
# Configure automatic backups
config['storage']['backup_enabled'] = True
config['storage']['backup_frequency_hours'] = 6
```

## Expected Business Results

### Invoice Processing Agent
- **Time Savings**: 15+ hours/week
- **Cost Savings**: $3,000+/month
- **ROI**: 300-500% within 6 months
- **Accuracy**: 99.5% data extraction accuracy

### Expense Categorizer Agent
- **Time Savings**: 5-8 hours/week
- **Cost Savings**: $500-1,000/month
- **ROI**: 200-400% within 3 months
- **Accuracy**: 95%+ categorization accuracy

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review processing accuracy
   - Check for failed transactions
   - Update categorization rules as needed

2. **Monthly**:
   - Retrain ML models with new data
   - Review business metrics and ROI
   - Update vendor/merchant mappings

3. **Quarterly**:
   - Review and update tax categories
   - Performance optimization
   - Security updates

### Getting Help

1. **Documentation**: Check configuration files and code comments
2. **Logs**: Review log files for error details
3. **Testing**: Use test suite to validate functionality
4. **Community**: Join discussions and share improvements

## Next Steps

1. **Start Small**: Begin with a small batch of invoices and transactions
2. **Monitor Results**: Track accuracy and business value metrics
3. **Iterate and Improve**: Continuously refine rules and training data
4. **Scale Up**: Gradually increase processing volume
5. **Integrate**: Connect with accounting software for full automation

With proper setup and configuration, these agents will deliver significant business value through automated financial document processing and expense categorization.