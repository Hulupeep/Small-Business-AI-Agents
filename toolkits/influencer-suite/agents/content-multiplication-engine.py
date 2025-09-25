"""
Content Multiplication Engine - AI Agent
Transform 1 idea into 15+ pieces of content across platforms
"""

import openai
import anthropic
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from jinja2 import Template

@dataclass
class ContentPiece:
    platform: str
    format: str
    content: str
    hooks: List[str]
    hashtags: List[str]
    engagement_prediction: float
    optimal_time: str

class ContentMultiplicationEngine:
    def __init__(self, config: Dict):
        self.openai_client = openai.OpenAI(api_key=config['openai_api_key'])
        self.anthropic_client = anthropic.Anthropic(api_key=config['anthropic_api_key'])
        self.linkedin_api = config.get('linkedin_api_key')
        self.substack_api = config.get('substack_api_key')

        # Content templates for different platforms
        self.templates = {
            'linkedin_post': Template("""
{{ hook }}

{{ main_content }}

{{ cta }}

{{ hashtags }}
            """),
            'twitter_thread': Template("""
🧵 {{ thread_title }}

1/{{ total_threads }} {{ hook }}

{{ thread_content }}

{{ final_cta }}
            """),
            'newsletter': Template("""
Subject: {{ subject_line }}

Hey {{ subscriber_name }},

{{ intro_hook }}

{{ main_content }}

{{ value_section }}

{{ cta_section }}

Best,
{{ sender_name }}
            """),
            'video_script': Template("""
HOOK (0-3s): {{ video_hook }}

SETUP (3-10s): {{ problem_setup }}

CONTENT (10-45s): {{ main_teaching }}

CTA (45-60s): {{ call_to_action }}

RETENTION: {{ retention_hooks }}
            """)
        }

    def multiply_content(self, seed_idea: str, target_platforms: List[str]) -> Dict[str, ContentPiece]:
        """Transform one idea into multiple content pieces"""

        # Analyze seed idea
        analysis = self._analyze_idea(seed_idea)

        # Generate content for each platform
        content_pieces = {}

        for platform in target_platforms:
            if platform == 'linkedin':
                content_pieces['linkedin'] = self._create_linkedin_post(seed_idea, analysis)
            elif platform == 'twitter':
                content_pieces['twitter'] = self._create_twitter_thread(seed_idea, analysis)
            elif platform == 'substack':
                content_pieces['substack'] = self._create_newsletter(seed_idea, analysis)
            elif platform == 'youtube':
                content_pieces['youtube'] = self._create_video_script(seed_idea, analysis)
            elif platform == 'blog':
                content_pieces['blog'] = self._create_blog_post(seed_idea, analysis)

        return content_pieces

    def _analyze_idea(self, idea: str) -> Dict:
        """Analyze the core idea for content multiplication"""
        prompt = f"""
        Analyze this content idea for maximum engagement across platforms:

        Idea: {idea}

        Return JSON with:
        1. Core message
        2. Key pain points it addresses
        3. Target audience segments
        4. Emotional triggers
        5. Best content angles
        6. Optimal platforms
        7. Trending hashtags
        8. Engagement prediction
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return json.loads(response.choices[0].message.content)

    def _create_linkedin_post(self, idea: str, analysis: Dict) -> ContentPiece:
        """Generate LinkedIn post with viral hooks"""

        # Generate multiple hook options
        hooks = self._generate_hooks(idea, 'linkedin', analysis)

        # Select best hook based on AI scoring
        best_hook = self._score_and_select_hook(hooks, 'linkedin')

        # Generate main content
        content_prompt = f"""
        Create a LinkedIn post for AI/productivity micro-influencers:

        Hook: {best_hook}
        Core idea: {idea}
        Target: {analysis.get('target_audience', 'professionals wanting AI productivity')}

        Structure:
        1. Hook (attention-grabbing first line)
        2. Story/context (2-3 lines)
        3. Key insights (3-5 bullet points or numbered list)
        4. Call to action (engagement-focused)

        Make it conversational, valuable, and shareable.
        Length: 150-200 words optimal for LinkedIn algorithm.
        """

        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": content_prompt}]
        )

        content = response.content[0].text

        # Generate relevant hashtags
        hashtags = self._generate_hashtags(idea, 'linkedin')

        # Predict engagement
        engagement_score = self._predict_engagement(content, 'linkedin', analysis)

        return ContentPiece(
            platform='linkedin',
            format='post',
            content=content,
            hooks=hooks,
            hashtags=hashtags,
            engagement_prediction=engagement_score,
            optimal_time=self._get_optimal_posting_time('linkedin')
        )

    def _create_twitter_thread(self, idea: str, analysis: Dict) -> ContentPiece:
        """Generate Twitter thread from core idea"""

        thread_prompt = f"""
        Create a Twitter thread about: {idea}

        Thread structure:
        1. Hook tweet (must be quotable/shareable)
        2. Problem setup (why this matters)
        3. Solution breakdown (3-5 tweets with actionable steps)
        4. Real example/case study
        5. Call to action (retweet, follow, comment)

        Each tweet max 280 characters.
        Use thread numbers (1/7, 2/7, etc.)
        Include retention hooks to keep reading.
        Target: AI/productivity professionals
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": thread_prompt}],
            temperature=0.8
        )

        thread_content = response.choices[0].message.content
        hashtags = self._generate_hashtags(idea, 'twitter')
        engagement_score = self._predict_engagement(thread_content, 'twitter', analysis)

        return ContentPiece(
            platform='twitter',
            format='thread',
            content=thread_content,
            hooks=[],
            hashtags=hashtags,
            engagement_prediction=engagement_score,
            optimal_time=self._get_optimal_posting_time('twitter')
        )

    def _create_newsletter(self, idea: str, analysis: Dict) -> ContentPiece:
        """Generate Substack newsletter content"""

        newsletter_prompt = f"""
        Create a newsletter about: {idea}

        Target: AI/productivity enthusiasts (3K subscribers)
        Goal: High open rates, click-throughs, and forwards

        Structure:
        1. Subject line (curiosity + value)
        2. Personal intro (2-3 sentences)
        3. Main content (problem → solution → implementation)
        4. Resource section (3 tools/links)
        5. Community question (engagement)
        6. P.S. with subtle course/coaching mention

        Tone: Conversational, expert but approachable
        Length: 800-1200 words
        Include 2-3 specific examples or case studies
        """

        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": newsletter_prompt}]
        )

        newsletter_content = response.content[0].text
        engagement_score = self._predict_engagement(newsletter_content, 'newsletter', analysis)

        return ContentPiece(
            platform='substack',
            format='newsletter',
            content=newsletter_content,
            hooks=[],
            hashtags=[],
            engagement_prediction=engagement_score,
            optimal_time=self._get_optimal_posting_time('newsletter')
        )

    def _create_video_script(self, idea: str, analysis: Dict) -> ContentPiece:
        """Generate YouTube/TikTok video script"""

        script_prompt = f"""
        Create a 60-second video script about: {idea}

        Platform: YouTube Shorts/TikTok
        Target: AI productivity enthusiasts
        Goal: High retention, saves, shares

        Script format:
        HOOK (0-3s): Pattern interrupt + benefit
        SETUP (3-10s): Problem/situation
        CONTENT (10-50s): Solution steps (3 max)
        CTA (50-60s): Like, save, follow

        Include:
        - Visual cues for editing
        - Text overlay suggestions
        - Retention hooks every 10-15 seconds
        - Specific tool mentions

        Make it fast-paced and actionable.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": script_prompt}],
            temperature=0.9
        )

        script_content = response.choices[0].message.content
        hashtags = self._generate_hashtags(idea, 'video')
        engagement_score = self._predict_engagement(script_content, 'video', analysis)

        return ContentPiece(
            platform='youtube',
            format='video_script',
            content=script_content,
            hooks=[],
            hashtags=hashtags,
            engagement_prediction=engagement_score,
            optimal_time=self._get_optimal_posting_time('video')
        )

    def _create_blog_post(self, idea: str, analysis: Dict) -> ContentPiece:
        """Generate SEO-optimized blog post"""

        blog_prompt = f"""
        Create an SEO blog post about: {idea}

        Target: 2,000+ words, SEO optimized
        Keywords: AI productivity, automation tools, efficiency
        Goal: Organic traffic + newsletter signups

        Structure:
        1. SEO title with primary keyword
        2. Meta description (155 chars)
        3. Introduction with hook
        4. H2 sections (5-7 main points)
        5. Practical examples
        6. Tool recommendations
        7. Implementation guide
        8. FAQ section
        9. Conclusion with CTA

        Include:
        - Internal linking opportunities
        - Featured snippet optimization
        - Tool comparisons
        - Screenshots/visual descriptions
        """

        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=3000,
            messages=[{"role": "user", "content": blog_prompt}]
        )

        blog_content = response.content[0].text
        engagement_score = self._predict_engagement(blog_content, 'blog', analysis)

        return ContentPiece(
            platform='blog',
            format='article',
            content=blog_content,
            hooks=[],
            hashtags=[],
            engagement_prediction=engagement_score,
            optimal_time=self._get_optimal_posting_time('blog')
        )

    def _generate_hooks(self, idea: str, platform: str, analysis: Dict) -> List[str]:
        """Generate multiple hook options for A/B testing"""

        hook_prompt = f"""
        Generate 5 different hooks for {platform} about: {idea}

        Hook types to include:
        1. Number/statistic hook
        2. Question hook
        3. Controversial/contrarian hook
        4. Story/personal hook
        5. Problem/pain hook

        Target audience: {analysis.get('target_audience', 'AI/productivity professionals')}
        Each hook should be 1-2 sentences max.
        Make them scroll-stopping and curiosity-driven.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": hook_prompt}],
            temperature=0.9
        )

        hooks_text = response.choices[0].message.content
        return [hook.strip() for hook in hooks_text.split('\n') if hook.strip()]

    def _score_and_select_hook(self, hooks: List[str], platform: str) -> str:
        """Score hooks and select the best one"""

        scoring_prompt = f"""
        Score these {platform} hooks from 1-10 based on:
        - Attention-grabbing power
        - Curiosity factor
        - Platform fit
        - Engagement potential

        Hooks:
        {json.dumps(hooks, indent=2)}

        Return JSON with hook scores and explanation.
        """

        response = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": scoring_prompt}]
        )

        try:
            scores = json.loads(response.content[0].text)
            # Return highest scoring hook
            best_hook = max(hooks, key=lambda h: scores.get(h, 0))
            return best_hook
        except:
            # Fallback to first hook if scoring fails
            return hooks[0] if hooks else ""

    def _generate_hashtags(self, idea: str, platform: str) -> List[str]:
        """Generate relevant hashtags for platform"""

        hashtag_prompt = f"""
        Generate optimal hashtags for {platform} about: {idea}

        Requirements:
        - Mix of popular and niche hashtags
        - AI/productivity focused
        - Platform-specific best practices
        - Include trending hashtags

        Return 10-15 hashtags as JSON array.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": hashtag_prompt}],
            temperature=0.7
        )

        try:
            hashtags = json.loads(response.choices[0].message.content)
            return hashtags if isinstance(hashtags, list) else []
        except:
            # Fallback hashtags
            return ['#AI', '#Productivity', '#Automation', '#Tech', '#Innovation']

    def _predict_engagement(self, content: str, platform: str, analysis: Dict) -> float:
        """Predict engagement score based on content analysis"""

        # Simple engagement prediction based on content characteristics
        score = 0.5  # Base score

        # Length optimization
        if platform == 'linkedin':
            optimal_length = len(content.split()) in range(100, 250)
            score += 0.1 if optimal_length else -0.1
        elif platform == 'twitter':
            score += 0.1 if len(content) < 2000 else -0.1  # Thread length

        # Keyword presence
        ai_keywords = ['AI', 'automation', 'productivity', 'efficiency']
        keyword_count = sum(1 for keyword in ai_keywords if keyword.lower() in content.lower())
        score += keyword_count * 0.05

        # Question marks (engagement boost)
        score += content.count('?') * 0.02

        # Emotional triggers
        emotion_words = ['amazing', 'incredible', 'shocking', 'revealed', 'secret']
        emotion_count = sum(1 for word in emotion_words if word.lower() in content.lower())
        score += emotion_count * 0.03

        # Cap at 1.0
        return min(score, 1.0)

    def _get_optimal_posting_time(self, platform: str) -> str:
        """Get optimal posting time for platform"""

        optimal_times = {
            'linkedin': '9:00 AM',  # Tuesday-Thursday
            'twitter': '12:00 PM',  # Monday-Friday
            'substack': '9:00 AM',  # Thursday
            'video': '6:00 PM',     # Wednesday-Friday
            'blog': '10:00 AM'      # Tuesday-Thursday
        }

        return optimal_times.get(platform, '12:00 PM')

    def schedule_content(self, content_pieces: Dict[str, ContentPiece], start_date: datetime) -> Dict:
        """Create a content calendar for all pieces"""

        calendar = {}
        current_date = start_date

        for platform, content in content_pieces.items():
            # Spread content across optimal days
            platform_schedule = {
                'content': content.content,
                'scheduled_time': current_date.strftime('%Y-%m-%d %H:%M'),
                'platform': platform,
                'engagement_prediction': content.engagement_prediction,
                'hashtags': content.hashtags
            }

            calendar[platform] = platform_schedule
            current_date += timedelta(days=1)  # Space out content

        return calendar

    def analyze_performance(self, content_id: str, platform: str) -> Dict:
        """Analyze actual vs predicted performance"""

        # This would integrate with platform APIs to get real metrics
        # For now, return mock analysis

        return {
            'predicted_engagement': 0.75,
            'actual_engagement': 0.82,
            'variance': 0.07,
            'top_performing_elements': [
                'Strong hook',
                'Relevant hashtags',
                'Optimal timing'
            ],
            'improvement_suggestions': [
                'Add more visual elements',
                'Include specific numbers',
                'Test different CTAs'
            ]
        }


# Example usage
if __name__ == "__main__":
    config = {
        'openai_api_key': 'your-openai-key',
        'anthropic_api_key': 'your-anthropic-key',
        'linkedin_api_key': 'your-linkedin-key',
        'substack_api_key': 'your-substack-key'
    }

    engine = ContentMultiplicationEngine(config)

    # Test content multiplication
    seed_idea = "How I automated my entire content creation workflow using 5 AI tools and now create 50+ pieces of content per week in just 2 hours"

    target_platforms = ['linkedin', 'twitter', 'substack', 'youtube']

    content_pieces = engine.multiply_content(seed_idea, target_platforms)

    # Schedule content
    from datetime import datetime
    schedule = engine.schedule_content(content_pieces, datetime.now())

    print("Content Calendar Generated:")
    print(json.dumps(schedule, indent=2, default=str))