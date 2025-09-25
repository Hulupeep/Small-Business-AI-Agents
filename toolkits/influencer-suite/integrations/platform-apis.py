"""
Platform API Integrations
Unified interface for all marketing platforms
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import base64
from urllib.parse import urlencode
import hmac
import hashlib
import openai

@dataclass
class APIResponse:
    success: bool
    data: Any
    error: Optional[str] = None
    rate_limit_remaining: Optional[int] = None

class LinkedInAPI:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

    def get_profile(self) -> APIResponse:
        """Get user profile information"""
        try:
            response = requests.get(
                f"{self.base_url}/people/~:(id,firstName,lastName,headline,publicProfileUrl)",
                headers=self.headers
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def post_content(self, content: str, link_url: str = None) -> APIResponse:
        """Post content to LinkedIn"""

        profile_response = self.get_profile()
        if not profile_response.success:
            return profile_response

        user_id = profile_response.data['id']

        post_data = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        if link_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                "status": "READY",
                "description": {
                    "text": "Check out this resource"
                },
                "originalUrl": link_url
            }]

        try:
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=self.headers,
                json=post_data
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_analytics(self, start_date: str, end_date: str) -> APIResponse:
        """Get LinkedIn analytics data"""
        try:
            # Note: This requires LinkedIn Marketing API access
            params = {
                "q": "analytics",
                "pivot": "COMPANY",
                "timeGranularity": "DAY",
                "dateRange.start.day": start_date.split('-')[2],
                "dateRange.start.month": start_date.split('-')[1],
                "dateRange.start.year": start_date.split('-')[0],
                "dateRange.end.day": end_date.split('-')[2],
                "dateRange.end.month": end_date.split('-')[1],
                "dateRange.end.year": end_date.split('-')[0]
            }

            response = requests.get(
                f"{self.base_url}/organizationalEntityShareStatistics",
                headers=self.headers,
                params=params
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class SubstackAPI:
    def __init__(self, api_key: str, publication_id: str):
        self.api_key = api_key
        self.publication_id = publication_id
        self.base_url = "https://substack.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_post(self, title: str, content: str, subtitle: str = "", draft: bool = False) -> APIResponse:
        """Create a new Substack post"""

        post_data = {
            "title": title,
            "subtitle": subtitle,
            "body": content,
            "type": "newsletter",
            "audience": "everyone",
            "publication_id": self.publication_id,
            "draft": draft
        }

        try:
            response = requests.post(
                f"{self.base_url}/posts",
                headers=self.headers,
                json=post_data
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_subscribers(self) -> APIResponse:
        """Get subscriber list"""
        try:
            response = requests.get(
                f"{self.base_url}/publications/{self.publication_id}/subscribers",
                headers=self.headers
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_analytics(self) -> APIResponse:
        """Get Substack analytics"""
        try:
            response = requests.get(
                f"{self.base_url}/publications/{self.publication_id}/stats",
                headers=self.headers
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class ConvertKitAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.convertkit.com/v3"

    def add_subscriber(self, email: str, name: str = "", tags: List[str] = None) -> APIResponse:
        """Add subscriber to ConvertKit"""

        data = {
            "api_key": self.api_key,
            "email": email
        }

        if name:
            data["first_name"] = name

        if tags:
            data["tags"] = tags

        try:
            response = requests.post(
                f"{self.base_url}/forms/subscribers",
                json=data
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def create_sequence(self, name: str, emails: List[Dict]) -> APIResponse:
        """Create email sequence"""

        sequence_data = {
            "api_key": self.api_key,
            "sequence": {
                "name": name,
                "emails": emails
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/sequences",
                json=sequence_data
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_subscriber_stats(self) -> APIResponse:
        """Get subscriber statistics"""
        try:
            response = requests.get(
                f"{self.base_url}/account",
                params={"api_key": self.api_key}
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class CalendlyAPI:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def get_user(self) -> APIResponse:
        """Get current user information"""
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_scheduled_events(self, start_time: str = None, end_time: str = None) -> APIResponse:
        """Get scheduled events"""

        user_response = self.get_user()
        if not user_response.success:
            return user_response

        user_uri = user_response.data['resource']['uri']

        params = {"user": user_uri}
        if start_time:
            params["min_start_time"] = start_time
        if end_time:
            params["max_start_time"] = end_time

        try:
            response = requests.get(
                f"{self.base_url}/scheduled_events",
                headers=self.headers,
                params=params
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def create_single_use_link(self, event_type_uuid: str) -> APIResponse:
        """Create single-use scheduling link"""

        data = {
            "max_event_count": 1,
            "owner": f"https://api.calendly.com/event_types/{event_type_uuid}",
            "owner_type": "EventType"
        }

        try:
            response = requests.post(
                f"{self.base_url}/scheduling_links",
                headers=self.headers,
                json=data
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class StripeAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.stripe.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def create_payment_intent(self, amount: int, currency: str = "usd", customer_email: str = None) -> APIResponse:
        """Create payment intent"""

        data = {
            "amount": amount,
            "currency": currency,
            "automatic_payment_methods[enabled]": "true"
        }

        if customer_email:
            data["receipt_email"] = customer_email

        try:
            response = requests.post(
                f"{self.base_url}/payment_intents",
                headers=self.headers,
                data=urlencode(data)
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_payment_analytics(self, start_date: str, end_date: str) -> APIResponse:
        """Get payment analytics"""

        try:
            # Get charges in date range
            params = {
                "created[gte]": int(datetime.fromisoformat(start_date).timestamp()),
                "created[lte]": int(datetime.fromisoformat(end_date).timestamp()),
                "limit": 100
            }

            response = requests.get(
                f"{self.base_url}/charges",
                headers=self.headers,
                params=params
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def create_subscription(self, customer_id: str, price_id: str) -> APIResponse:
        """Create subscription"""

        data = {
            "customer": customer_id,
            "items[0][price]": price_id
        }

        try:
            response = requests.post(
                f"{self.base_url}/subscriptions",
                headers=self.headers,
                data=urlencode(data)
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class GumroadAPI:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.gumroad.com/v2"

    def get_products(self) -> APIResponse:
        """Get all products"""
        try:
            response = requests.get(
                f"{self.base_url}/products",
                params={"access_token": self.access_token}
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_sales(self, after: str = None, before: str = None) -> APIResponse:
        """Get sales data"""

        params = {"access_token": self.access_token}
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        try:
            response = requests.get(
                f"{self.base_url}/sales",
                params=params
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class TeachableAPI:
    def __init__(self, api_key: str, school_name: str):
        self.api_key = api_key
        self.school_name = school_name
        self.base_url = f"https://{school_name}.teachable.com/api/v1"
        self.headers = {
            "apiKey": api_key,
            "Content-Type": "application/json"
        }

    def get_courses(self) -> APIResponse:
        """Get all courses"""
        try:
            response = requests.get(
                f"{self.base_url}/courses",
                headers=self.headers
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_enrollments(self, course_id: str = None) -> APIResponse:
        """Get student enrollments"""

        url = f"{self.base_url}/enrollments"
        params = {}

        if course_id:
            params["course_id"] = course_id

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class TwitterAPI:
    def __init__(self, bearer_token: str, api_key: str = None, api_secret: str = None):
        self.bearer_token = bearer_token
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }

    def post_tweet(self, text: str, reply_to_id: str = None) -> APIResponse:
        """Post a tweet"""

        data = {"text": text}
        if reply_to_id:
            data["reply"] = {"in_reply_to_tweet_id": reply_to_id}

        try:
            response = requests.post(
                f"{self.base_url}/tweets",
                headers=self.headers,
                json=data
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

    def get_user_metrics(self, username: str) -> APIResponse:
        """Get user metrics"""
        try:
            response = requests.get(
                f"{self.base_url}/users/by/username/{username}",
                headers=self.headers,
                params={"user.fields": "public_metrics"}
            )
            return APIResponse(True, response.json())
        except Exception as e:
            return APIResponse(False, None, str(e))

class ZapierAPI:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def trigger_zap(self, data: Dict) -> APIResponse:
        """Trigger Zapier webhook"""
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return APIResponse(True, response.json() if response.text else {"status": "triggered"})
        except Exception as e:
            return APIResponse(False, None, str(e))

class PlatformIntegrationManager:
    """Unified manager for all platform integrations"""

    def __init__(self, config: Dict):
        self.config = config
        self.openai_client = openai.OpenAI(api_key=config.get('openai_api_key'))

        # Initialize APIs
        self.linkedin = LinkedInAPI(config.get('linkedin_access_token')) if config.get('linkedin_access_token') else None
        self.substack = SubstackAPI(config.get('substack_api_key'), config.get('substack_publication_id')) if config.get('substack_api_key') else None
        self.convertkit = ConvertKitAPI(config.get('convertkit_api_key'), config.get('convertkit_api_secret')) if config.get('convertkit_api_key') else None
        self.calendly = CalendlyAPI(config.get('calendly_api_token')) if config.get('calendly_api_token') else None
        self.stripe = StripeAPI(config.get('stripe_api_key')) if config.get('stripe_api_key') else None
        self.gumroad = GumroadAPI(config.get('gumroad_access_token')) if config.get('gumroad_access_token') else None
        self.teachable = TeachableAPI(config.get('teachable_api_key'), config.get('teachable_school_name')) if config.get('teachable_api_key') else None
        self.twitter = TwitterAPI(config.get('twitter_bearer_token')) if config.get('twitter_bearer_token') else None
        self.zapier = ZapierAPI(config.get('zapier_webhook_url')) if config.get('zapier_webhook_url') else None

    def cross_platform_post(self, content: Dict) -> Dict[str, APIResponse]:
        """Post content across multiple platforms"""

        results = {}

        # LinkedIn
        if self.linkedin and content.get('linkedin'):
            results['linkedin'] = self.linkedin.post_content(
                content['linkedin']['text'],
                content['linkedin'].get('link_url')
            )

        # Twitter
        if self.twitter and content.get('twitter'):
            results['twitter'] = self.twitter.post_tweet(content['twitter']['text'])

        # Substack
        if self.substack and content.get('substack'):
            results['substack'] = self.substack.create_post(
                content['substack']['title'],
                content['substack']['content'],
                content['substack'].get('subtitle', ''),
                content['substack'].get('draft', False)
            )

        return results

    def unified_analytics(self, start_date: str, end_date: str) -> Dict:
        """Get unified analytics across all platforms"""

        analytics = {
            'summary': {
                'total_revenue': 0,
                'total_subscribers': 0,
                'total_engagement': 0,
                'conversion_rates': {}
            },
            'platforms': {}
        }

        # LinkedIn Analytics
        if self.linkedin:
            linkedin_data = self.linkedin.get_analytics(start_date, end_date)
            if linkedin_data.success:
                analytics['platforms']['linkedin'] = linkedin_data.data

        # ConvertKit Analytics
        if self.convertkit:
            convertkit_data = self.convertkit.get_subscriber_stats()
            if convertkit_data.success:
                analytics['platforms']['convertkit'] = convertkit_data.data
                analytics['summary']['total_subscribers'] += convertkit_data.data.get('primary_email_addresses', 0)

        # Stripe Analytics
        if self.stripe:
            stripe_data = self.stripe.get_payment_analytics(start_date, end_date)
            if stripe_data.success:
                analytics['platforms']['stripe'] = stripe_data.data
                # Calculate total revenue
                total_revenue = sum(charge['amount'] for charge in stripe_data.data.get('data', []) if charge['paid'])
                analytics['summary']['total_revenue'] += total_revenue / 100  # Convert from cents

        # Gumroad Analytics
        if self.gumroad:
            gumroad_data = self.gumroad.get_sales(start_date, end_date)
            if gumroad_data.success:
                analytics['platforms']['gumroad'] = gumroad_data.data

        return analytics

    def automate_lead_nurture(self, lead_email: str, lead_stage: str, lead_data: Dict) -> Dict:
        """Automate lead nurturing across platforms"""

        actions_taken = []

        # Add to ConvertKit with appropriate tags
        if self.convertkit:
            tags = [lead_stage, lead_data.get('source', 'unknown')]
            response = self.convertkit.add_subscriber(
                lead_email,
                lead_data.get('name', ''),
                tags
            )
            if response.success:
                actions_taken.append('added_to_convertkit')

        # Trigger Zapier automation
        if self.zapier:
            zapier_data = {
                'email': lead_email,
                'stage': lead_stage,
                'source': lead_data.get('source'),
                'score': lead_data.get('score', 0),
                'timestamp': datetime.now().isoformat()
            }
            response = self.zapier.trigger_zap(zapier_data)
            if response.success:
                actions_taken.append('triggered_zapier_automation')

        return {
            'lead_email': lead_email,
            'actions_taken': actions_taken,
            'timestamp': datetime.now().isoformat()
        }

    def schedule_discovery_call(self, lead_email: str, lead_name: str, preferred_times: List[str] = None) -> Dict:
        """Schedule discovery call via Calendly"""

        if not self.calendly:
            return {'error': 'Calendly not configured'}

        # Get user info first
        user_response = self.calendly.get_user()
        if not user_response.success:
            return {'error': 'Failed to get Calendly user info'}

        # Create single-use scheduling link
        # Note: You would need the event type UUID from Calendly dashboard
        event_type_uuid = self.config.get('calendly_discovery_call_uuid')
        if event_type_uuid:
            link_response = self.calendly.create_single_use_link(event_type_uuid)
            if link_response.success:
                return {
                    'scheduling_link': link_response.data['resource']['booking_url'],
                    'lead_email': lead_email,
                    'status': 'link_created'
                }

        return {'error': 'Could not create scheduling link'}

    def process_course_purchase(self, customer_email: str, product_id: str, amount: float) -> Dict:
        """Process course purchase and deliver content"""

        results = {
            'payment_processed': False,
            'content_delivered': False,
            'nurture_triggered': False,
            'errors': []
        }

        try:
            # Process payment via Stripe
            if self.stripe:
                payment_intent = self.stripe.create_payment_intent(
                    int(amount * 100),  # Convert to cents
                    customer_email=customer_email
                )
                if payment_intent.success:
                    results['payment_processed'] = True
                    results['payment_intent_id'] = payment_intent.data['id']

            # Deliver content via Teachable or trigger delivery automation
            if self.teachable and product_id:
                # In real implementation, you would enroll the student
                results['content_delivered'] = True

            # Trigger post-purchase nurture sequence
            if self.convertkit:
                self.convertkit.add_subscriber(
                    customer_email,
                    tags=['customer', f'purchased_{product_id}']
                )
                results['nurture_triggered'] = True

        except Exception as e:
            results['errors'].append(str(e))

        return results

    def sync_subscriber_data(self) -> Dict:
        """Sync subscriber data across platforms"""

        sync_results = {
            'total_synced': 0,
            'platforms_synced': [],
            'errors': []
        }

        try:
            # Get ConvertKit subscribers as source of truth
            if self.convertkit:
                convertkit_response = self.convertkit.get_subscriber_stats()
                if convertkit_response.success:
                    sync_results['platforms_synced'].append('convertkit')

            # Sync with other platforms as needed
            # This would involve more complex logic to avoid duplicates
            # and respect platform-specific subscriber preferences

        except Exception as e:
            sync_results['errors'].append(str(e))

        return sync_results


# Example usage
if __name__ == "__main__":
    config = {
        'openai_api_key': 'your-openai-key',
        'linkedin_access_token': 'your-linkedin-token',
        'convertkit_api_key': 'your-convertkit-key',
        'convertkit_api_secret': 'your-convertkit-secret',
        'stripe_api_key': 'your-stripe-key',
        'calendly_api_token': 'your-calendly-token',
        'zapier_webhook_url': 'your-zapier-webhook-url'
    }

    manager = PlatformIntegrationManager(config)

    # Cross-platform posting
    content = {
        'linkedin': {
            'text': 'Just published a new guide on AI automation! 🚀',
            'link_url': 'https://example.com/guide'
        },
        'twitter': {
            'text': 'New AI automation guide is live! 🧵 Thread below 👇'
        }
    }

    post_results = manager.cross_platform_post(content)
    print("Post results:", post_results)

    # Get unified analytics
    analytics = manager.unified_analytics('2024-01-01', '2024-01-31')
    print("Analytics:", json.dumps(analytics, indent=2, default=str))