"""
Configuration settings for business agents
"""

import os
from typing import Dict, Any
from pathlib import Path

# Base configuration
BASE_CONFIG = {
    "database_path": "data/",
    "log_level": "INFO",
    "log_file_prefix": "logs/",
    "enable_analytics": True,
    "enable_crm_sync": True,
    "enable_notifications": True
}

# Customer Service Chatbot Configuration
CUSTOMER_SERVICE_CONFIG = {
    "database_file": "customer_service.db",
    "knowledge_base_refresh_interval": 3600,  # seconds
    "max_conversation_length": 100,  # messages
    "escalation_threshold": 3,  # failed attempts before escalation
    "satisfaction_survey_trigger": True,
    "auto_close_resolved_after": 24,  # hours
    "supported_channels": ["web", "email", "sms", "whatsapp", "slack"],
    "business_hours": {
        "timezone": "EST",
        "weekdays": {"start": "09:00", "end": "18:00"},
        "weekends": {"enabled": False}
    },
    "escalation_keywords": [
        "cancel subscription", "refund", "billing error", "technical issue",
        "speak to manager", "complaint", "legal", "urgent", "emergency",
        "lawsuit", "attorney", "fraud", "scam", "terrible", "worst"
    ],
    "response_templates": {
        "greeting": "👋 Hello! I'm your AI customer service assistant. I'm here 24/7 to help you!",
        "escalation": "🚀 I've connected you with our human support team for personalized assistance.",
        "satisfaction": "How would you rate your experience? (1-5 stars)",
        "closing": "Thank you for contacting us! Have a great day! 😊"
    }
}

# Lead Qualifier Configuration
LEAD_QUALIFIER_CONFIG = {
    "database_file": "lead_qualifier.db",
    "qualification_thresholds": {
        "qualified": 75,
        "nurturing": 50,
        "unqualified": 50
    },
    "bant_weights": {
        "budget": 0.25,
        "authority": 0.30,
        "need": 0.30,
        "timeline": 0.15
    },
    "scoring_criteria": {
        "company_sizes": {
            "startup": 30,
            "small": 50,
            "medium": 70,
            "large": 85,
            "enterprise": 95
        },
        "authority_titles": {
            "executive": ["ceo", "cto", "cfo", "coo", "founder", "co-founder", "president"],
            "vp_director": ["vp", "vice president", "director", "head of"],
            "manager": ["manager", "lead", "principal", "senior"],
            "individual": ["analyst", "specialist", "coordinator", "associate"]
        },
        "high_budget_industries": [
            "fintech", "software", "saas", "technology", "consulting",
            "healthcare", "finance", "enterprise", "ai", "machine learning"
        ],
        "target_industries": [
            "technology", "software", "saas", "e-commerce", "fintech",
            "marketing", "consulting", "healthcare", "education"
        ]
    },
    "auto_nurturing": {
        "enabled": True,
        "nurturing_sequence": [
            {"delay_days": 1, "template": "welcome_nurture"},
            {"delay_days": 3, "template": "value_proposition"},
            {"delay_days": 7, "template": "case_study"},
            {"delay_days": 14, "template": "demo_offer"}
        ]
    },
    "sales_alerts": {
        "qualified_lead_alert": True,
        "high_score_threshold": 85,
        "urgent_response_time": 300,  # 5 minutes in seconds
        "alert_channels": ["email", "slack", "webhook"]
    }
}

# CRM Integration Configuration
CRM_CONFIG = {
    "supabase": {
        "url": os.getenv("SUPABASE_URL", ""),
        "key": os.getenv("SUPABASE_KEY", ""),
        "table": "leads",
        "enabled": bool(os.getenv("SUPABASE_URL"))
    },
    "airtable": {
        "api_key": os.getenv("AIRTABLE_API_KEY", ""),
        "base_id": os.getenv("AIRTABLE_BASE_ID", ""),
        "table": "Leads",
        "enabled": bool(os.getenv("AIRTABLE_API_KEY"))
    },
    "hubspot": {
        "api_key": os.getenv("HUBSPOT_API_KEY", ""),
        "enabled": bool(os.getenv("HUBSPOT_API_KEY"))
    },
    "sync_frequency": 300,  # seconds
    "batch_sync_size": 50,
    "retry_attempts": 3,
    "retry_delay": 60  # seconds
}

# Notification Configuration
NOTIFICATION_CONFIG = {
    "email": {
        "smtp_server": os.getenv("SMTP_SERVER", ""),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("EMAIL_USERNAME", ""),
        "password": os.getenv("EMAIL_PASSWORD", ""),
        "from_address": os.getenv("FROM_EMAIL", ""),
        "enabled": bool(os.getenv("SMTP_SERVER"))
    },
    "slack": {
        "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
        "channel": os.getenv("SLACK_CHANNEL", "#sales"),
        "enabled": bool(os.getenv("SLACK_WEBHOOK_URL"))
    },
    "webhook": {
        "url": os.getenv("WEBHOOK_URL", ""),
        "secret": os.getenv("WEBHOOK_SECRET", ""),
        "enabled": bool(os.getenv("WEBHOOK_URL"))
    }
}

# Analytics Configuration
ANALYTICS_CONFIG = {
    "retention_days": 90,
    "report_frequency": "daily",
    "metrics_to_track": [
        "total_conversations",
        "resolution_rate",
        "escalation_rate",
        "response_time",
        "customer_satisfaction",
        "leads_captured",
        "qualification_rate",
        "conversion_rate",
        "time_savings",
        "cost_savings"
    ],
    "dashboard_refresh": 300,  # seconds
    "export_formats": ["json", "csv", "pdf"]
}

# Security Configuration
SECURITY_CONFIG = {
    "rate_limiting": {
        "enabled": True,
        "requests_per_minute": 60,
        "burst_limit": 10
    },
    "data_encryption": {
        "enabled": True,
        "encryption_key": os.getenv("ENCRYPTION_KEY", ""),
        "algorithm": "AES-256-GCM"
    },
    "audit_logging": {
        "enabled": True,
        "log_file": "audit.log",
        "retention_days": 365
    },
    "api_security": {
        "require_https": True,
        "api_key_required": True,
        "cors_enabled": True,
        "allowed_origins": ["*"]  # Configure for production
    }
}


def get_config() -> Dict[str, Any]:
    """Get complete configuration"""
    return {
        "base": BASE_CONFIG,
        "customer_service": CUSTOMER_SERVICE_CONFIG,
        "lead_qualifier": LEAD_QUALIFIER_CONFIG,
        "crm": CRM_CONFIG,
        "notifications": NOTIFICATION_CONFIG,
        "analytics": ANALYTICS_CONFIG,
        "security": SECURITY_CONFIG
    }


def validate_config() -> Dict[str, Any]:
    """Validate configuration and return any issues"""
    issues = {}

    # Check CRM configurations
    crm_issues = []
    if not any([
        CRM_CONFIG["supabase"]["enabled"],
        CRM_CONFIG["airtable"]["enabled"],
        CRM_CONFIG["hubspot"]["enabled"]
    ]):
        crm_issues.append("No CRM integrations configured")

    if crm_issues:
        issues["crm"] = crm_issues

    # Check notification configurations
    notification_issues = []
    if not any([
        NOTIFICATION_CONFIG["email"]["enabled"],
        NOTIFICATION_CONFIG["slack"]["enabled"],
        NOTIFICATION_CONFIG["webhook"]["enabled"]
    ]):
        notification_issues.append("No notification channels configured")

    if notification_issues:
        issues["notifications"] = notification_issues

    return issues


def create_directories():
    """Create necessary directories"""
    directories = [
        BASE_CONFIG["database_path"],
        BASE_CONFIG["log_file_prefix"],
        "data/exports",
        "data/backups",
        "config/templates"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # Validate configuration
    config = get_config()
    issues = validate_config()

    if issues:
        print("Configuration Issues Found:")
        for category, problems in issues.items():
            print(f"  {category.upper()}:")
            for problem in problems:
                print(f"    - {problem}")
    else:
        print("Configuration validation passed!")

    # Create directories
    create_directories()
    print("Directories created successfully!")