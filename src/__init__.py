"""
LangChain Small Business Agents

A comprehensive suite of AI-powered agents designed to automate and enhance
various aspects of small business operations using LangChain framework.

Available Agents:
- Customer Service Agent: Handle customer inquiries and support tickets
- Sales Lead Qualifier: Qualify and score potential sales leads
- Content Creator: Generate marketing content and social media posts
- Financial Analyst: Analyze financial data and generate reports
- HR Assistant: Manage HR tasks and employee interactions
- Inventory Manager: Track and manage inventory levels
- Email Marketing: Create and manage email campaigns
- Social Media Manager: Manage social media presence and engagement
- Market Research: Conduct market analysis and competitor research
- Document Processor: Process and analyze business documents
"""

__version__ = "1.0.0"
__author__ = "LangChain Small Business Team"
__email__ = "support@langchain-business.com"

# Import core modules
from .agents import *
from .utils import *
from .tools import *

# Agent registry
AVAILABLE_AGENTS = {
    "customer_service": "Customer Service Agent",
    "sales_qualifier": "Sales Lead Qualifier",
    "content_creator": "Content Creator",
    "financial_analyst": "Financial Analyst",
    "hr_assistant": "HR Assistant",
    "inventory_manager": "Inventory Manager",
    "email_marketing": "Email Marketing Agent",
    "social_media": "Social Media Manager",
    "market_research": "Market Research Agent",
    "document_processor": "Document Processor"
}

def get_agent_list():
    """Return list of available agents."""
    return list(AVAILABLE_AGENTS.keys())

def get_agent_description(agent_name):
    """Get description for a specific agent."""
    return AVAILABLE_AGENTS.get(agent_name, "Agent not found")

# Package initialization
def initialize_package():
    """Initialize the package with necessary configurations."""
    import logging
    from .config.settings import setup_logging

    # Setup logging
    setup_logging()

    # Log package initialization
    logger = logging.getLogger(__name__)
    logger.info(f"LangChain Small Business Agents v{__version__} initialized")
    logger.info(f"Available agents: {', '.join(AVAILABLE_AGENTS.keys())}")

# Auto-initialize when package is imported
initialize_package()