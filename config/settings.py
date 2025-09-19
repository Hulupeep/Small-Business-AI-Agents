"""
Configuration settings for LangChain Small Business Agents

This module contains all configuration settings, environment variables,
and setup functions for the 10 business agents.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR]:
    directory.mkdir(exist_ok=True)

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    name: str = os.getenv("DB_NAME", "langchain_business")
    username: str = os.getenv("DB_USERNAME", "postgres")
    password: str = os.getenv("DB_PASSWORD", "")
    url: str = f"postgresql://{username}:{password}@{host}:{port}/{name}"

@dataclass
class APIKeys:
    """API keys for external services."""
    # Core LLM APIs
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # Social Media APIs
    twitter_api_key: str = os.getenv("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    twitter_access_secret: str = os.getenv("TWITTER_ACCESS_SECRET", "")

    facebook_access_token: str = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    linkedin_access_token: str = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

    # Email Services
    sendgrid_api_key: str = os.getenv("SENDGRID_API_KEY", "")
    mailchimp_api_key: str = os.getenv("MAILCHIMP_API_KEY", "")

    # Financial APIs
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    quandl_api_key: str = os.getenv("QUANDL_API_KEY", "")

    # Document Processing
    azure_form_recognizer_key: str = os.getenv("AZURE_FORM_RECOGNIZER_KEY", "")
    azure_form_recognizer_endpoint: str = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT", "")

    # Search and Research
    serp_api_key: str = os.getenv("SERP_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")

    # Customer Service
    zendesk_subdomain: str = os.getenv("ZENDESK_SUBDOMAIN", "")
    zendesk_email: str = os.getenv("ZENDESK_EMAIL", "")
    zendesk_token: str = os.getenv("ZENDESK_TOKEN", "")

@dataclass
class AgentConfig:
    """Individual agent configuration."""
    name: str
    description: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    enabled: bool = True
    tools: list = None
    memory_type: str = "buffer"
    memory_size: int = 10

class Settings:
    """Main settings class for the application."""

    def __init__(self):
        self.database = DatabaseConfig()
        self.api_keys = APIKeys()
        self.agents = self._setup_agent_configs()

        # General settings
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.max_concurrent_agents = int(os.getenv("MAX_CONCURRENT_AGENTS", "5"))

        # LangChain settings
        self.langchain_tracing = os.getenv("LANGCHAIN_TRACING", "false").lower() == "true"
        self.langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT", "")
        self.langchain_api_key = os.getenv("LANGCHAIN_API_KEY", "")

        # Cache settings
        self.cache_type = os.getenv("CACHE_TYPE", "memory")  # memory, redis, file
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

        # Security settings
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.jwt_expiration = int(os.getenv("JWT_EXPIRATION", "3600"))

    def _setup_agent_configs(self) -> Dict[str, AgentConfig]:
        """Setup configuration for all 10 agents."""
        return {
            "customer_service": AgentConfig(
                name="Customer Service Agent",
                description="Handle customer inquiries and support tickets",
                model=os.getenv("CUSTOMER_SERVICE_MODEL", "gpt-3.5-turbo"),
                temperature=0.3,
                tools=["zendesk", "email", "knowledge_base"],
                memory_type="conversation_buffer",
                memory_size=20
            ),

            "sales_qualifier": AgentConfig(
                name="Sales Lead Qualifier",
                description="Qualify and score potential sales leads",
                model=os.getenv("SALES_QUALIFIER_MODEL", "gpt-4"),
                temperature=0.5,
                tools=["crm", "lead_scoring", "email"],
                memory_type="summary",
                memory_size=15
            ),

            "content_creator": AgentConfig(
                name="Content Creator",
                description="Generate marketing content and social media posts",
                model=os.getenv("CONTENT_CREATOR_MODEL", "gpt-4"),
                temperature=0.8,
                tools=["image_generation", "social_media", "seo_tools"],
                memory_type="buffer",
                memory_size=10
            ),

            "financial_analyst": AgentConfig(
                name="Financial Analyst",
                description="Analyze financial data and generate reports",
                model=os.getenv("FINANCIAL_ANALYST_MODEL", "gpt-4"),
                temperature=0.2,
                tools=["financial_apis", "excel", "reporting"],
                memory_type="summary",
                memory_size=25
            ),

            "hr_assistant": AgentConfig(
                name="HR Assistant",
                description="Manage HR tasks and employee interactions",
                model=os.getenv("HR_ASSISTANT_MODEL", "gpt-3.5-turbo"),
                temperature=0.4,
                tools=["hr_system", "email", "calendar"],
                memory_type="conversation_buffer",
                memory_size=15
            ),

            "inventory_manager": AgentConfig(
                name="Inventory Manager",
                description="Track and manage inventory levels",
                model=os.getenv("INVENTORY_MANAGER_MODEL", "gpt-3.5-turbo"),
                temperature=0.3,
                tools=["inventory_system", "suppliers", "forecasting"],
                memory_type="buffer",
                memory_size=20
            ),

            "email_marketing": AgentConfig(
                name="Email Marketing Agent",
                description="Create and manage email campaigns",
                model=os.getenv("EMAIL_MARKETING_MODEL", "gpt-4"),
                temperature=0.7,
                tools=["email_platform", "analytics", "segmentation"],
                memory_type="summary",
                memory_size=12
            ),

            "social_media": AgentConfig(
                name="Social Media Manager",
                description="Manage social media presence and engagement",
                model=os.getenv("SOCIAL_MEDIA_MODEL", "gpt-4"),
                temperature=0.8,
                tools=["twitter", "facebook", "linkedin", "analytics"],
                memory_type="buffer",
                memory_size=15
            ),

            "market_research": AgentConfig(
                name="Market Research Agent",
                description="Conduct market analysis and competitor research",
                model=os.getenv("MARKET_RESEARCH_MODEL", "gpt-4"),
                temperature=0.6,
                tools=["search_api", "news_api", "analytics"],
                memory_type="summary",
                memory_size=30
            ),

            "document_processor": AgentConfig(
                name="Document Processor",
                description="Process and analyze business documents",
                model=os.getenv("DOCUMENT_PROCESSOR_MODEL", "gpt-4"),
                temperature=0.3,
                tools=["ocr", "document_ai", "file_storage"],
                memory_type="buffer",
                memory_size=10
            )
        }

    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent."""
        return self.agents.get(agent_name)

    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []

        # Check required API keys
        if not self.api_keys.openai_api_key and not self.api_keys.anthropic_api_key:
            issues.append("No LLM API key configured (OpenAI or Anthropic required)")

        # Check database connection
        if not self.database.password and self.database.host != "localhost":
            issues.append("Database password not configured for remote host")

        # Check agent configurations
        disabled_agents = [name for name, config in self.agents.items() if not config.enabled]

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "disabled_agents": disabled_agents,
            "total_agents": len(self.agents),
            "enabled_agents": len(self.agents) - len(disabled_agents)
        }

def setup_logging():
    """Setup logging configuration."""
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOGS_DIR / "agents.log"),
            logging.StreamHandler()
        ]
    )

    # Create agent-specific loggers
    agent_names = [
        "customer_service", "sales_qualifier", "content_creator",
        "financial_analyst", "hr_assistant", "inventory_manager",
        "email_marketing", "social_media", "market_research", "document_processor"
    ]

    for agent_name in agent_names:
        logger = logging.getLogger(f"agents.{agent_name}")
        handler = logging.FileHandler(LOGS_DIR / f"{agent_name}.log")
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(handler)

# Global settings instance
settings = Settings()

# Export commonly used configurations
__all__ = ["settings", "Settings", "AgentConfig", "DatabaseConfig", "APIKeys", "setup_logging"]