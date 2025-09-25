"""
Configuration settings for Food Delivery AI Toolkit

This module contains all configuration settings for the food delivery
management system, including API keys, database settings, and business rules.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    name: str = "food_delivery_ai"
    user: str = "postgres"
    password: str = ""

@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None

@dataclass
class DeliveryPlatformConfig:
    uber_eats_api_key: Optional[str] = None
    deliveroo_api_key: Optional[str] = None
    just_eat_api_key: Optional[str] = None
    platform_commission_rates: Dict[str, float] = None

    def __post_init__(self):
        if self.platform_commission_rates is None:
            self.platform_commission_rates = {
                "uber_eats": 0.30,
                "deliveroo": 0.28,
                "just_eat": 0.14,
                "direct": 0.0
            }

@dataclass
class NotificationConfig:
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    sendgrid_api_key: Optional[str] = None
    sendgrid_from_email: Optional[str] = None

@dataclass
class PaymentConfig:
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    currency: str = "EUR"

@dataclass
class BusinessRules:
    # Order management
    default_prep_time: int = 20  # minutes
    max_order_modification_time: int = 5  # minutes after order placed
    auto_confirm_orders: bool = True

    # Delivery settings
    max_delivery_distance: float = 10.0  # kilometers
    delivery_fee_base: float = 3.50  # euros
    delivery_fee_per_km: float = 0.50  # euros per km

    # Inventory thresholds
    low_stock_threshold_percentage: float = 0.2  # 20% of max capacity
    auto_reorder_enabled: bool = True
    waste_alert_threshold: float = 100.0  # euros per day

    # Customer experience
    loyalty_points_per_euro: float = 1.0
    loyalty_point_value: float = 0.01  # 1 point = 1 cent
    feedback_request_delay: int = 30  # minutes after delivery

    # Financial
    target_profit_margin: float = 0.35  # 35%
    peak_hour_surge_multiplier: float = 1.2
    driver_commission_rate: float = 0.15  # 15% of delivery fee

class Settings:
    """Main settings class that loads configuration from environment variables"""

    def __init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.debug = os.getenv("DEBUG", "True").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")

        # Server settings
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))

        # Database configuration
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "food_delivery_ai"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )

        # Redis configuration
        self.redis = RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD")
        )

        # Delivery platform configuration
        self.delivery_platforms = DeliveryPlatformConfig(
            uber_eats_api_key=os.getenv("UBER_EATS_API_KEY"),
            deliveroo_api_key=os.getenv("DELIVEROO_API_KEY"),
            just_eat_api_key=os.getenv("JUST_EAT_API_KEY")
        )

        # Notification services
        self.notifications = NotificationConfig(
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
            twilio_phone_number=os.getenv("TWILIO_PHONE_NUMBER"),
            sendgrid_api_key=os.getenv("SENDGRID_API_KEY"),
            sendgrid_from_email=os.getenv("SENDGRID_FROM_EMAIL")
        )

        # Payment configuration
        self.payments = PaymentConfig(
            stripe_secret_key=os.getenv("STRIPE_SECRET_KEY"),
            stripe_publishable_key=os.getenv("STRIPE_PUBLISHABLE_KEY"),
            currency=os.getenv("CURRENCY", "EUR")
        )

        # Business rules
        self.business_rules = BusinessRules()

        # AI/ML settings
        self.enable_ml_forecasting = os.getenv("ENABLE_ML_FORECASTING", "True").lower() == "true"
        self.enable_dynamic_pricing = os.getenv("ENABLE_DYNAMIC_PRICING", "True").lower() == "true"
        self.enable_route_optimization = os.getenv("ENABLE_ROUTE_OPTIMIZATION", "True").lower() == "true"

        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "food_delivery_ai.log")

        # Monitoring and analytics
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.analytics_enabled = os.getenv("ANALYTICS_ENABLED", "True").lower() == "true"

    @property
    def database_url(self) -> str:
        """Get database URL for SQLAlchemy"""
        return (f"postgresql://{self.database.user}:{self.database.password}@"
                f"{self.database.host}:{self.database.port}/{self.database.name}")

    @property
    def redis_url(self) -> str:
        """Get Redis URL"""
        auth = f":{self.redis.password}@" if self.redis.password else ""
        return f"redis://{auth}{self.redis.host}:{self.redis.port}/{self.redis.db}"

# Global settings instance
settings = Settings()

# Environment-specific configurations
ENVIRONMENT_CONFIGS = {
    Environment.DEVELOPMENT: {
        "auto_reload": True,
        "workers": 1,
        "access_log": True,
        "use_colors": True
    },
    Environment.STAGING: {
        "auto_reload": False,
        "workers": 2,
        "access_log": True,
        "use_colors": False
    },
    Environment.PRODUCTION: {
        "auto_reload": False,
        "workers": 4,
        "access_log": False,
        "use_colors": False
    }
}

def get_environment_config() -> Dict:
    """Get configuration for current environment"""
    return ENVIRONMENT_CONFIGS.get(settings.environment, ENVIRONMENT_CONFIGS[Environment.DEVELOPMENT])

# Validation functions
def validate_required_settings():
    """Validate that all required settings are present"""
    errors = []

    if settings.environment == Environment.PRODUCTION:
        if not settings.secret_key or settings.secret_key == "your-secret-key-here":
            errors.append("SECRET_KEY must be set in production")

        if not settings.database.password:
            errors.append("DB_PASSWORD must be set in production")

        if not settings.notifications.twilio_account_sid:
            errors.append("TWILIO_ACCOUNT_SID recommended for SMS notifications")

        if not settings.notifications.sendgrid_api_key:
            errors.append("SENDGRID_API_KEY recommended for email notifications")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

def get_platform_credentials(platform: str) -> Optional[str]:
    """Get API credentials for delivery platform"""
    platform_keys = {
        "uber_eats": settings.delivery_platforms.uber_eats_api_key,
        "deliveroo": settings.delivery_platforms.deliveroo_api_key,
        "just_eat": settings.delivery_platforms.just_eat_api_key
    }

    return platform_keys.get(platform)

# Example .env file content
ENV_TEMPLATE = """
# Food Delivery AI Configuration

# Environment
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Server
HOST=0.0.0.0
PORT=8000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=food_delivery_ai
DB_USER=postgres
DB_PASSWORD=your-db-password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Delivery Platform APIs
UBER_EATS_API_KEY=your-uber-eats-key
DELIVEROO_API_KEY=your-deliveroo-key
JUST_EAT_API_KEY=your-just-eat-key

# Notifications
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+353XXXXXXXXX
SENDGRID_API_KEY=your-sendgrid-key
SENDGRID_FROM_EMAIL=noreply@yourrestaurant.com

# Payments
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
CURRENCY=EUR

# AI/ML Features
ENABLE_ML_FORECASTING=True
ENABLE_DYNAMIC_PRICING=True
ENABLE_ROUTE_OPTIMIZATION=True

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
ANALYTICS_ENABLED=True
LOG_LEVEL=INFO
"""