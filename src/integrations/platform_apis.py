"""
Platform API Integrations for Marketing Automation Agents
Connects to social media platforms and email services
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import aiohttp
from dataclasses import dataclass

@dataclass
class PlatformConfig:
    """Configuration for platform API integration"""
    platform: str
    api_key: str
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 100  # requests per hour

class PlatformAPIManager:
    """
    Manages API integrations for social media and email platforms

    Supported Platforms:
    - Twitter API v2
    - LinkedIn API
    - Instagram Graph API
    - Facebook Graph API
    - Mailchimp API
    - SendGrid API
    """

    def __init__(self, configs: List[PlatformConfig]):
        self.configs = {config.platform: config for config in configs}
        self.logger = self._setup_logging()
        self.session = None

        # Rate limiting tracking
        self.rate_limits = {}

        self.logger.info(f"Initialized API manager for {len(configs)} platforms")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for API manager"""
        logger = logging.getLogger('PlatformAPIManager')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    # Social Media Platform Methods

    async def post_to_twitter(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """
        Post content to Twitter using API v2

        Args:
            content: Tweet content
            media_urls: Optional media URLs to attach

        Returns:
            API response with post ID and metrics
        """
        try:
            config = self.configs.get('twitter')
            if not config:
                raise ValueError("Twitter configuration not found")

            headers = {
                'Authorization': f'Bearer {config.access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                'text': content
            }

            # Add media if provided
            if media_urls:
                # In production, you'd first upload media and get media IDs
                media_ids = await self._upload_twitter_media(media_urls)
                if media_ids:
                    payload['media'] = {'media_ids': media_ids}

            url = 'https://api.twitter.com/2/tweets'

            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    result = await response.json()
                    self.logger.info(f"Successfully posted to Twitter: {result['data']['id']}")
                    return {
                        'success': True,
                        'platform': 'twitter',
                        'post_id': result['data']['id'],
                        'url': f"https://twitter.com/user/status/{result['data']['id']}",
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"Twitter API error: {response.status} - {error_text}")
                    return {'success': False, 'error': error_text, 'status': response.status}

        except Exception as e:
            self.logger.error(f"Error posting to Twitter: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def post_to_linkedin(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """
        Post content to LinkedIn

        Args:
            content: Post content
            media_urls: Optional media URLs

        Returns:
            API response with post details
        """
        try:
            config = self.configs.get('linkedin')
            if not config:
                raise ValueError("LinkedIn configuration not found")

            headers = {
                'Authorization': f'Bearer {config.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            # Get user profile ID (in production, cache this)
            profile_url = 'https://api.linkedin.com/v2/me'
            async with self.session.get(profile_url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {'success': False, 'error': f"Profile fetch failed: {error_text}"}

                profile = await response.json()
                person_urn = f"urn:li:person:{profile['id']}"

            # Create post payload
            payload = {
                'author': person_urn,
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {
                            'text': content
                        },
                        'shareMediaCategory': 'NONE'
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }

            # Add media if provided
            if media_urls:
                payload['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'IMAGE'
                # In production, upload media first and get asset URNs

            url = 'https://api.linkedin.com/v2/ugcPosts'

            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    result = await response.json()
                    post_id = result['id']
                    self.logger.info(f"Successfully posted to LinkedIn: {post_id}")
                    return {
                        'success': True,
                        'platform': 'linkedin',
                        'post_id': post_id,
                        'url': f"https://linkedin.com/feed/update/{post_id}",
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"LinkedIn API error: {response.status} - {error_text}")
                    return {'success': False, 'error': error_text, 'status': response.status}

        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def post_to_instagram(self, content: str, media_url: str) -> Dict[str, Any]:
        """
        Post content to Instagram (requires media)

        Args:
            content: Post caption
            media_url: Image or video URL

        Returns:
            API response with post details
        """
        try:
            config = self.configs.get('instagram')
            if not config:
                raise ValueError("Instagram configuration not found")

            if not media_url:
                return {'success': False, 'error': 'Instagram posts require media'}

            headers = {
                'Authorization': f'Bearer {config.access_token}',
                'Content-Type': 'application/json'
            }

            # Step 1: Create media container
            container_payload = {
                'image_url': media_url,
                'caption': content,
                'access_token': config.access_token
            }

            # Get Instagram Business Account ID (should be cached in production)
            account_id = await self._get_instagram_account_id()
            if not account_id:
                return {'success': False, 'error': 'Could not get Instagram account ID'}

            container_url = f'https://graph.facebook.com/v18.0/{account_id}/media'

            async with self.session.post(container_url, json=container_payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {'success': False, 'error': f"Container creation failed: {error_text}"}

                container_result = await response.json()
                container_id = container_result['id']

            # Step 2: Publish the media
            publish_payload = {
                'creation_id': container_id,
                'access_token': config.access_token
            }

            publish_url = f'https://graph.facebook.com/v18.0/{account_id}/media_publish'

            async with self.session.post(publish_url, json=publish_payload) as response:
                if response.status == 200:
                    result = await response.json()
                    post_id = result['id']
                    self.logger.info(f"Successfully posted to Instagram: {post_id}")
                    return {
                        'success': True,
                        'platform': 'instagram',
                        'post_id': post_id,
                        'url': f"https://instagram.com/p/{post_id}",
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"Instagram publish error: {response.status} - {error_text}")
                    return {'success': False, 'error': error_text, 'status': response.status}

        except Exception as e:
            self.logger.error(f"Error posting to Instagram: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def post_to_facebook(self, content: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """
        Post content to Facebook Page

        Args:
            content: Post content
            media_urls: Optional media URLs

        Returns:
            API response with post details
        """
        try:
            config = self.configs.get('facebook')
            if not config:
                raise ValueError("Facebook configuration not found")

            # Get Page ID (should be cached in production)
            page_id = await self._get_facebook_page_id()
            if not page_id:
                return {'success': False, 'error': 'Could not get Facebook page ID'}

            payload = {
                'message': content,
                'access_token': config.access_token
            }

            # Add media if provided
            if media_urls and len(media_urls) == 1:
                payload['link'] = media_urls[0]
            elif media_urls and len(media_urls) > 1:
                # For multiple media, would need to create album
                pass

            url = f'https://graph.facebook.com/v18.0/{page_id}/feed'

            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    post_id = result['id']
                    self.logger.info(f"Successfully posted to Facebook: {post_id}")
                    return {
                        'success': True,
                        'platform': 'facebook',
                        'post_id': post_id,
                        'url': f"https://facebook.com/{post_id}",
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"Facebook API error: {response.status} - {error_text}")
                    return {'success': False, 'error': error_text, 'status': response.status}

        except Exception as e:
            self.logger.error(f"Error posting to Facebook: {str(e)}")
            return {'success': False, 'error': str(e)}

    # Email Platform Methods

    async def send_email_mailchimp(self,
                                 campaign_id: str,
                                 recipient_email: str,
                                 subject: str,
                                 content: str,
                                 personalization: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send email via Mailchimp API

        Args:
            campaign_id: Mailchimp campaign ID
            recipient_email: Recipient email address
            subject: Email subject line
            content: Email content (HTML)
            personalization: Personalization data

        Returns:
            Send result
        """
        try:
            config = self.configs.get('mailchimp')
            if not config:
                raise ValueError("Mailchimp configuration not found")

            # Extract datacenter from API key (format: key-dc)
            datacenter = config.api_key.split('-')[-1]

            headers = {
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            }

            # Apply personalization
            if personalization:
                for key, value in personalization.items():
                    content = content.replace(f'{{{key}}}', str(value))
                    subject = subject.replace(f'{{{key}}}', str(value))

            # Create campaign content
            content_payload = {
                'template': {
                    'id': 'campaign_template',
                    'sections': {
                        'main_content': content
                    }
                }
            }

            content_url = f'https://{datacenter}.api.mailchimp.com/3.0/campaigns/{campaign_id}/content'

            async with self.session.put(content_url, headers=headers, json=content_payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {'success': False, 'error': f"Content update failed: {error_text}"}

            # Send campaign
            send_url = f'https://{datacenter}.api.mailchimp.com/3.0/campaigns/{campaign_id}/actions/send'

            async with self.session.post(send_url, headers=headers) as response:
                if response.status == 204:  # Mailchimp returns 204 for successful send
                    self.logger.info(f"Successfully sent Mailchimp campaign: {campaign_id}")
                    return {
                        'success': True,
                        'platform': 'mailchimp',
                        'campaign_id': campaign_id,
                        'recipient': recipient_email
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"Mailchimp send error: {response.status} - {error_text}")
                    return {'success': False, 'error': error_text, 'status': response.status}

        except Exception as e:
            self.logger.error(f"Error sending via Mailchimp: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def send_email_sendgrid(self,
                                recipient_email: str,
                                sender_email: str,
                                subject: str,
                                content: str,
                                personalization: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send email via SendGrid API

        Args:
            recipient_email: Recipient email
            sender_email: Sender email
            subject: Email subject
            content: Email content (HTML)
            personalization: Personalization data

        Returns:
            Send result
        """
        try:
            config = self.configs.get('sendgrid')
            if not config:
                raise ValueError("SendGrid configuration not found")

            headers = {
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            }

            # Apply personalization
            if personalization:
                for key, value in personalization.items():
                    content = content.replace(f'{{{key}}}', str(value))
                    subject = subject.replace(f'{{{key}}}', str(value))

            payload = {
                'personalizations': [
                    {
                        'to': [{'email': recipient_email}],
                        'subject': subject
                    }
                ],
                'from': {'email': sender_email},
                'content': [
                    {
                        'type': 'text/html',
                        'value': content
                    }
                ],
                'tracking_settings': {
                    'click_tracking': {'enable': True},
                    'open_tracking': {'enable': True}
                }
            }

            url = 'https://api.sendgrid.com/v3/mail/send'

            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 202:  # SendGrid returns 202 for accepted
                    # Get message ID from response headers
                    message_id = response.headers.get('X-Message-Id', 'unknown')
                    self.logger.info(f"Successfully sent SendGrid email: {message_id}")
                    return {
                        'success': True,
                        'platform': 'sendgrid',
                        'message_id': message_id,
                        'recipient': recipient_email
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"SendGrid error: {response.status} - {error_text}")
                    return {'success': False, 'error': error_text, 'status': response.status}

        except Exception as e:
            self.logger.error(f"Error sending via SendGrid: {str(e)}")
            return {'success': False, 'error': str(e)}

    # Analytics and Engagement Methods

    async def get_post_analytics(self, platform: str, post_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific post

        Args:
            platform: Platform name
            post_id: Post ID

        Returns:
            Analytics data
        """
        try:
            if platform == 'twitter':
                return await self._get_twitter_analytics(post_id)
            elif platform == 'linkedin':
                return await self._get_linkedin_analytics(post_id)
            elif platform == 'instagram':
                return await self._get_instagram_analytics(post_id)
            elif platform == 'facebook':
                return await self._get_facebook_analytics(post_id)
            else:
                return {'success': False, 'error': f'Analytics not supported for {platform}'}

        except Exception as e:
            self.logger.error(f"Error getting {platform} analytics: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def get_email_analytics(self, platform: str, campaign_id: str) -> Dict[str, Any]:
        """
        Get email campaign analytics

        Args:
            platform: Email platform (mailchimp, sendgrid)
            campaign_id: Campaign ID

        Returns:
            Analytics data
        """
        try:
            if platform == 'mailchimp':
                return await self._get_mailchimp_analytics(campaign_id)
            elif platform == 'sendgrid':
                return await self._get_sendgrid_analytics(campaign_id)
            else:
                return {'success': False, 'error': f'Email analytics not supported for {platform}'}

        except Exception as e:
            self.logger.error(f"Error getting {platform} email analytics: {str(e)}")
            return {'success': False, 'error': str(e)}

    # Helper Methods

    async def _upload_twitter_media(self, media_urls: List[str]) -> List[str]:
        """Upload media to Twitter and return media IDs"""
        # Simplified - in production, download media and upload to Twitter
        return []

    async def _get_instagram_account_id(self) -> Optional[str]:
        """Get Instagram Business Account ID"""
        # In production, this would be cached or configured
        return "your_instagram_business_account_id"

    async def _get_facebook_page_id(self) -> Optional[str]:
        """Get Facebook Page ID"""
        # In production, this would be cached or configured
        return "your_facebook_page_id"

    async def _get_twitter_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Twitter post analytics"""
        try:
            config = self.configs.get('twitter')
            headers = {'Authorization': f'Bearer {config.access_token}'}

            url = f'https://api.twitter.com/2/tweets/{post_id}?tweet.fields=public_metrics'

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    metrics = result['data']['public_metrics']
                    return {
                        'success': True,
                        'platform': 'twitter',
                        'post_id': post_id,
                        'likes': metrics.get('like_count', 0),
                        'retweets': metrics.get('retweet_count', 0),
                        'replies': metrics.get('reply_count', 0),
                        'quotes': metrics.get('quote_count', 0),
                        'impressions': metrics.get('impression_count', 0)
                    }
                else:
                    error_text = await response.text()
                    return {'success': False, 'error': error_text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _get_linkedin_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get LinkedIn post analytics"""
        try:
            config = self.configs.get('linkedin')
            headers = {
                'Authorization': f'Bearer {config.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            url = f'https://api.linkedin.com/v2/socialActions/{post_id}'

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'platform': 'linkedin',
                        'post_id': post_id,
                        'likes': result.get('likesSummary', {}).get('totalLikes', 0),
                        'comments': result.get('commentsSummary', {}).get('totalComments', 0),
                        'shares': result.get('sharesSummary', {}).get('totalShares', 0)
                    }
                else:
                    error_text = await response.text()
                    return {'success': False, 'error': error_text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _get_instagram_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram post analytics"""
        try:
            config = self.configs.get('instagram')
            headers = {'Authorization': f'Bearer {config.access_token}'}

            url = f'https://graph.facebook.com/v18.0/{post_id}/insights?metric=impressions,reach,likes,comments,shares'

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    metrics = {item['name']: item['values'][0]['value'] for item in result['data']}
                    return {
                        'success': True,
                        'platform': 'instagram',
                        'post_id': post_id,
                        'impressions': metrics.get('impressions', 0),
                        'reach': metrics.get('reach', 0),
                        'likes': metrics.get('likes', 0),
                        'comments': metrics.get('comments', 0),
                        'shares': metrics.get('shares', 0)
                    }
                else:
                    error_text = await response.text()
                    return {'success': False, 'error': error_text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _get_facebook_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook post analytics"""
        try:
            config = self.configs.get('facebook')

            url = f'https://graph.facebook.com/v18.0/{post_id}/insights?metric=post_impressions,post_engaged_users,post_clicks&access_token={config.access_token}'

            async with self.session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    metrics = {item['name']: item['values'][0]['value'] for item in result['data']}
                    return {
                        'success': True,
                        'platform': 'facebook',
                        'post_id': post_id,
                        'impressions': metrics.get('post_impressions', 0),
                        'engaged_users': metrics.get('post_engaged_users', 0),
                        'clicks': metrics.get('post_clicks', 0)
                    }
                else:
                    error_text = await response.text()
                    return {'success': False, 'error': error_text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _get_mailchimp_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get Mailchimp campaign analytics"""
        try:
            config = self.configs.get('mailchimp')
            datacenter = config.api_key.split('-')[-1]

            headers = {'Authorization': f'Bearer {config.api_key}'}
            url = f'https://{datacenter}.api.mailchimp.com/3.0/campaigns/{campaign_id}'

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    stats = result.get('emails_sent', 0)
                    return {
                        'success': True,
                        'platform': 'mailchimp',
                        'campaign_id': campaign_id,
                        'emails_sent': stats,
                        'status': result.get('status', 'unknown')
                    }
                else:
                    error_text = await response.text()
                    return {'success': False, 'error': error_text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _get_sendgrid_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get SendGrid campaign analytics"""
        try:
            config = self.configs.get('sendgrid')
            headers = {'Authorization': f'Bearer {config.api_key}'}

            # SendGrid uses different endpoint structure
            url = f'https://api.sendgrid.com/v3/campaigns/{campaign_id}/stats'

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'platform': 'sendgrid',
                        'campaign_id': campaign_id,
                        'analytics': result
                    }
                else:
                    error_text = await response.text()
                    return {'success': False, 'error': error_text}

        except Exception as e:
            return {'success': False, 'error': str(e)}

# Example usage
async def example_usage():
    """Example of how to use the Platform API Manager"""

    # Configure platforms
    configs = [
        PlatformConfig(
            platform='twitter',
            api_key='your_api_key',
            access_token='your_access_token'
        ),
        PlatformConfig(
            platform='linkedin',
            api_key='your_api_key',
            access_token='your_access_token'
        ),
        PlatformConfig(
            platform='mailchimp',
            api_key='your_api_key-datacenter'
        ),
        PlatformConfig(
            platform='sendgrid',
            api_key='your_sendgrid_api_key'
        )
    ]

    # Use the API manager
    async with PlatformAPIManager(configs) as api_manager:

        # Post to social media
        twitter_result = await api_manager.post_to_twitter(
            "Exciting news! Our AI-powered marketing automation is live! 🚀 #MarketingAutomation #AI"
        )
        print(f"Twitter post result: {twitter_result}")

        linkedin_result = await api_manager.post_to_linkedin(
            "Thrilled to announce our new marketing automation platform that's helping businesses save 20+ hours per week!"
        )
        print(f"LinkedIn post result: {linkedin_result}")

        # Send email
        email_result = await api_manager.send_email_sendgrid(
            recipient_email="customer@example.com",
            sender_email="marketing@yourcompany.com",
            subject="Welcome to our platform!",
            content="<h1>Welcome!</h1><p>Thanks for joining us, {first_name}!</p>",
            personalization={'first_name': 'John'}
        )
        print(f"Email result: {email_result}")

        # Get analytics
        if twitter_result.get('success'):
            analytics = await api_manager.get_post_analytics('twitter', twitter_result['post_id'])
            print(f"Twitter analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(example_usage())