"""
Configuration management for automation agents.

Handles:
- Environment-specific settings
- Database configuration
- API credentials and integrations
- Notification settings
- Business rules and thresholds
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str = "sqlite:///automation_agents.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30

@dataclass
class NotificationConfig:
    """Notification system configuration"""
    email_enabled: bool = True
    slack_enabled: bool = False
    sms_enabled: bool = False
    webhook_enabled: bool = False

    # Email settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    default_email_recipients: list = None

    # Slack settings
    slack_webhook_url: str = ""
    slack_channel: str = "#automation"

    # SMS settings (Twilio)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    default_sms_recipients: list = None

    # Webhook settings
    webhook_urls: list = None

    def __post_init__(self):
        if self.default_email_recipients is None:
            self.default_email_recipients = []
        if self.default_sms_recipients is None:
            self.default_sms_recipients = []
        if self.webhook_urls is None:
            self.webhook_urls = []

@dataclass
class InventoryConfig:
    """Inventory tracker specific configuration"""
    # Monitoring settings
    monitoring_interval_minutes: int = 60
    auto_generate_pos: bool = True
    critical_stock_multiplier: float = 0.5  # Stock level below reorder_point * this = critical

    # Forecasting settings
    min_data_points_forecasting: int = 10
    default_forecast_days: int = 30
    confidence_level: float = 0.95
    seasonality_detection_threshold: float = 0.2

    # Business thresholds
    stockout_cost_estimate: float = 500.0  # Average cost per stockout event
    holding_cost_annual_percentage: float = 0.20  # 20% annual holding cost
    automation_hourly_rate: float = 50.0  # Cost savings per hour of automation

    # Alert thresholds
    high_urgency_days_threshold: int = 7
    critical_urgency_days_threshold: int = 3
    excess_inventory_threshold: float = 1.2  # 20% over optimal level

@dataclass
class MeetingSchedulerConfig:
    """Meeting scheduler specific configuration"""
    # Processing settings
    default_meeting_duration_minutes: int = 60
    default_timezone: str = "UTC"
    business_hours_start: int = 9  # 9 AM
    business_hours_end: int = 17  # 5 PM

    # Conflict resolution
    max_alternative_suggestions: int = 5
    flexibility_hours: int = 2
    prefer_business_hours: bool = True

    # NLP settings
    intent_confidence_threshold: float = 0.6
    entity_confidence_threshold: float = 0.7

    # Calendar integration
    google_calendar_enabled: bool = False
    outlook_calendar_enabled: bool = False
    calendly_enabled: bool = False

    # Business metrics
    scheduling_time_saved_per_meeting: float = 0.25  # Hours saved per automated scheduling
    coordinator_hourly_rate: float = 75.0

@dataclass
class CalendarCredentials:
    """Calendar integration credentials"""
    # Google Calendar
    google_client_id: str = ""
    google_client_secret: str = ""
    google_refresh_token: str = ""
    google_access_token: str = ""

    # Outlook/Microsoft Graph
    outlook_client_id: str = ""
    outlook_client_secret: str = ""
    outlook_tenant_id: str = ""
    outlook_access_token: str = ""

    # Calendly
    calendly_api_token: str = ""
    calendly_user_uri: str = ""

@dataclass
class SecurityConfig:
    """Security and encryption settings"""
    secret_key: str = "your-secret-key-here"
    encryption_algorithm: str = "AES-256-GCM"
    token_expiry_hours: int = 24
    max_login_attempts: int = 3
    session_timeout_minutes: int = 30

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/automation_agents.log"
    max_file_size_mb: int = 10
    backup_count: int = 5
    console_logging: bool = True

class ConfigManager:
    """
    Configuration manager for automation agents.
    Handles loading, validation, and environment-specific overrides.
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/config.json"
        self.environment = os.getenv("ENVIRONMENT", "development")

        # Initialize default configurations
        self.database = DatabaseConfig()
        self.notifications = NotificationConfig()
        self.inventory = InventoryConfig()
        self.meeting_scheduler = MeetingSchedulerConfig()
        self.calendar_credentials = CalendarCredentials()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()

        # Load configuration
        self.load_config()
        self.apply_environment_overrides()
        self.validate_config()

    def load_config(self):
        """Load configuration from file"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)

                # Update configurations with loaded data
                self._update_config_from_dict(config_data)

                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.warning(f"Configuration file {self.config_file} not found, using defaults")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")

    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration objects from dictionary"""

        if 'database' in config_data:
            self._update_dataclass(self.database, config_data['database'])

        if 'notifications' in config_data:
            self._update_dataclass(self.notifications, config_data['notifications'])

        if 'inventory' in config_data:
            self._update_dataclass(self.inventory, config_data['inventory'])

        if 'meeting_scheduler' in config_data:
            self._update_dataclass(self.meeting_scheduler, config_data['meeting_scheduler'])

        if 'calendar_credentials' in config_data:
            self._update_dataclass(self.calendar_credentials, config_data['calendar_credentials'])

        if 'security' in config_data:
            self._update_dataclass(self.security, config_data['security'])

        if 'logging' in config_data:
            self._update_dataclass(self.logging, config_data['logging'])

    def _update_dataclass(self, instance, data: Dict[str, Any]):
        """Update dataclass instance with dictionary data"""
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

    def apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""

        # Database overrides
        if db_url := os.getenv("DATABASE_URL"):
            self.database.url = db_url

        # Notification overrides
        if smtp_host := os.getenv("SMTP_HOST"):
            self.notifications.smtp_host = smtp_host
        if smtp_username := os.getenv("SMTP_USERNAME"):
            self.notifications.smtp_username = smtp_username
        if smtp_password := os.getenv("SMTP_PASSWORD"):
            self.notifications.smtp_password = smtp_password
        if from_email := os.getenv("FROM_EMAIL"):
            self.notifications.from_email = from_email

        # Slack overrides
        if slack_webhook := os.getenv("SLACK_WEBHOOK_URL"):
            self.notifications.slack_webhook_url = slack_webhook
            self.notifications.slack_enabled = True

        # Twilio overrides
        if twilio_sid := os.getenv("TWILIO_ACCOUNT_SID"):
            self.notifications.twilio_account_sid = twilio_sid
        if twilio_token := os.getenv("TWILIO_AUTH_TOKEN"):
            self.notifications.twilio_auth_token = twilio_token
        if twilio_from := os.getenv("TWILIO_FROM_NUMBER"):
            self.notifications.twilio_from_number = twilio_from
            self.notifications.sms_enabled = True

        # Calendar credentials overrides
        if google_client_id := os.getenv("GOOGLE_CLIENT_ID"):
            self.calendar_credentials.google_client_id = google_client_id
        if google_client_secret := os.getenv("GOOGLE_CLIENT_SECRET"):
            self.calendar_credentials.google_client_secret = google_client_secret
        if google_refresh_token := os.getenv("GOOGLE_REFRESH_TOKEN"):
            self.calendar_credentials.google_refresh_token = google_refresh_token

        if outlook_client_id := os.getenv("OUTLOOK_CLIENT_ID"):
            self.calendar_credentials.outlook_client_id = outlook_client_id
        if outlook_client_secret := os.getenv("OUTLOOK_CLIENT_SECRET"):
            self.calendar_credentials.outlook_client_secret = outlook_client_secret
        if outlook_tenant_id := os.getenv("OUTLOOK_TENANT_ID"):
            self.calendar_credentials.outlook_tenant_id = outlook_tenant_id

        if calendly_token := os.getenv("CALENDLY_API_TOKEN"):
            self.calendar_credentials.calendly_api_token = calendly_token

        # Security overrides
        if secret_key := os.getenv("SECRET_KEY"):
            self.security.secret_key = secret_key

        # Environment-specific adjustments
        if self.environment == "production":
            self.database.echo = False
            self.logging.level = "WARNING"
            self.logging.console_logging = False
        elif self.environment == "development":
            self.database.echo = True
            self.logging.level = "DEBUG"
            self.logging.console_logging = True

    def validate_config(self):
        """Validate configuration settings"""
        errors = []

        # Validate database configuration
        if not self.database.url:
            errors.append("Database URL is required")

        # Validate notification configuration
        if self.notifications.email_enabled:
            if not self.notifications.smtp_host:
                errors.append("SMTP host is required when email is enabled")
            if not self.notifications.smtp_username:
                errors.append("SMTP username is required when email is enabled")
            if not self.notifications.from_email:
                errors.append("From email is required when email is enabled")

        if self.notifications.slack_enabled and not self.notifications.slack_webhook_url:
            errors.append("Slack webhook URL is required when Slack is enabled")

        if self.notifications.sms_enabled:
            if not self.notifications.twilio_account_sid:
                errors.append("Twilio Account SID is required when SMS is enabled")
            if not self.notifications.twilio_auth_token:
                errors.append("Twilio Auth Token is required when SMS is enabled")

        # Validate business thresholds
        if self.inventory.stockout_cost_estimate <= 0:
            errors.append("Stockout cost estimate must be positive")
        if not (0 < self.inventory.holding_cost_annual_percentage <= 1):
            errors.append("Holding cost percentage must be between 0 and 1")

        if self.meeting_scheduler.business_hours_start >= self.meeting_scheduler.business_hours_end:
            errors.append("Business hours start must be before business hours end")

        # Validate security settings
        if len(self.security.secret_key) < 32:
            errors.append("Secret key should be at least 32 characters long")

        if errors:
            error_message = "Configuration validation errors:\n" + "\n".join(f"- {error}" for error in errors)
            raise ValueError(error_message)

        logger.info("Configuration validation successful")

    def get_inventory_config(self) -> Dict[str, Any]:
        """Get inventory tracker configuration as dictionary"""
        return {
            'database_url': self.database.url,
            'notifications': asdict(self.notifications),
            'inventory_settings': asdict(self.inventory)
        }

    def get_meeting_scheduler_config(self) -> Dict[str, Any]:
        """Get meeting scheduler configuration as dictionary"""
        return {
            'database_url': self.database.url,
            'notifications': asdict(self.notifications),
            'meeting_settings': asdict(self.meeting_scheduler),
            'google_credentials': {
                'client_id': self.calendar_credentials.google_client_id,
                'client_secret': self.calendar_credentials.google_client_secret,
                'refresh_token': self.calendar_credentials.google_refresh_token,
                'access_token': self.calendar_credentials.google_access_token
            } if self.calendar_credentials.google_client_id else None,
            'outlook_credentials': {
                'client_id': self.calendar_credentials.outlook_client_id,
                'client_secret': self.calendar_credentials.outlook_client_secret,
                'tenant_id': self.calendar_credentials.outlook_tenant_id,
                'access_token': self.calendar_credentials.outlook_access_token
            } if self.calendar_credentials.outlook_client_id else None,
            'calendly_credentials': {
                'api_token': self.calendar_credentials.calendly_api_token,
                'user_uri': self.calendar_credentials.calendly_user_uri
            } if self.calendar_credentials.calendly_api_token else None
        }

    def save_config(self, file_path: Optional[str] = None):
        """Save current configuration to file"""
        try:
            config_data = {
                'database': asdict(self.database),
                'notifications': asdict(self.notifications),
                'inventory': asdict(self.inventory),
                'meeting_scheduler': asdict(self.meeting_scheduler),
                'calendar_credentials': asdict(self.calendar_credentials),
                'security': asdict(self.security),
                'logging': asdict(self.logging)
            }

            save_path = file_path or self.config_file
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'w') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Configuration saved to {save_path}")

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def setup_logging(self):
        """Setup logging based on configuration"""
        log_level = getattr(logging, self.logging.level.upper())

        # Create formatter
        formatter = logging.Formatter(self.logging.format)

        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear existing handlers
        root_logger.handlers = []

        # Console handler
        if self.logging.console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # File handler
        if self.logging.file_path:
            try:
                from logging.handlers import RotatingFileHandler

                os.makedirs(os.path.dirname(self.logging.file_path), exist_ok=True)

                file_handler = RotatingFileHandler(
                    self.logging.file_path,
                    maxBytes=self.logging.max_file_size_mb * 1024 * 1024,
                    backupCount=self.logging.backup_count
                )
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

            except Exception as e:
                logger.error(f"Failed to setup file logging: {e}")


# Global configuration instance
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get global configuration instance"""
    return config

def setup_config(config_file: Optional[str] = None, environment: Optional[str] = None):
    """Setup global configuration"""
    global config

    if environment:
        os.environ["ENVIRONMENT"] = environment

    config = ConfigManager(config_file)
    config.setup_logging()

    return config