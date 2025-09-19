
# Marketing Automation Agents Initialization
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.social_media_manager import SocialMediaManager
from src.agents.email_campaign_writer import EmailCampaignWriter
from src.analytics.roi_tracker import ROITracker

def initialize_agents(config):
    """Initialize all marketing automation agents"""
    agents = {}

    # Initialize Social Media Manager
    sm_config = config.get('social_media_manager', {})
    sm_config['openai_api_key'] = os.getenv('OPENAI_API_KEY')
    agents['social_media_manager'] = SocialMediaManager(sm_config)

    # Initialize Email Campaign Writer
    ec_config = config.get('email_campaign_writer', {})
    ec_config['openai_api_key'] = os.getenv('OPENAI_API_KEY')
    agents['email_campaign_writer'] = EmailCampaignWriter(ec_config)

    # Initialize ROI Tracker
    roi_config = config.get('roi_tracking', {})
    agents['roi_tracker'] = ROITracker(roi_config)

    return agents

if __name__ == "__main__":
    import yaml
    with open('config/agent_config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    agents = initialize_agents(config)
    print("Marketing automation agents initialized successfully!")
