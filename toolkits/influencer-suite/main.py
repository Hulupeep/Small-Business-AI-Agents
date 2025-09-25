#!/usr/bin/env python3
"""
Influencer Content Management Suite - Main Entry Point
Simple tools for content planning and collaboration tracking
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add the toolkit to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import toolkit components
from agents.content_multiplication_engine import ContentMultiplicationEngine
from agents.audience_growth_automator import AudienceGrowthAutomator
from agents.lead_conversion_pipeline import LeadConversionPipeline
from agents.digital_product_factory import DigitalProductFactory
from agents.revenue_analytics_dashboard import RevenueAnalyticsDashboard
from integrations.platform_apis import PlatformIntegrationManager
from workflows.automation_sequences import AutomationOrchestrator

class InfluencerSuiteManager:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_path = self.base_path / "config"
        self.config = self._load_config()

        # Initialize basic components
        self._initialize_basic_tools()

    def _load_config(self) -> Dict:
        """Load configuration from files"""
        try:
            # Load main config
            config_file = self.config_path / "config.json"
            with open(config_file) as f:
                config = json.load(f)

            # Load API keys
            api_keys_file = self.config_path / "api_keys.json"
            if api_keys_file.exists():
                with open(api_keys_file) as f:
                    api_keys = json.load(f)
                config.update(api_keys)

            # Load integrations config
            integrations_file = self.config_path / "integrations.json"
            if integrations_file.exists():
                with open(integrations_file) as f:
                    integrations = json.load(f)
                config["integrations"] = integrations

            return config

        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            print("💡 Run 'python setup.py' to initialize configuration")
            sys.exit(1)

    def _initialize_basic_tools(self):
        """Initialize basic content management tools"""
        try:
            # Simple content planning tools (no complex AI)
            self.content_templates = self._load_content_templates()
            self.platform_best_practices = self._load_platform_guidelines()

            print("✅ Content management tools initialized")

        except Exception as e:
            print(f"❌ Error initializing tools: {e}")
            print("💡 Check your configuration files")
            sys.exit(1)

    def _load_content_templates(self) -> Dict:
        """Load basic content templates"""
        return {
            'instagram': ['photo_post', 'story', 'reel'],
            'linkedin': ['professional_post', 'article', 'poll'],
            'twitter': ['text_tweet', 'thread', 'quote_tweet']
        }

    def _load_platform_guidelines(self) -> Dict:
        """Load platform posting guidelines"""
        return {
            'instagram': {'best_times': ['9:00', '12:00', '17:00'], 'hashtag_limit': 30},
            'linkedin': {'best_times': ['8:00', '12:00', '16:00'], 'hashtag_limit': 5},
            'twitter': {'best_times': ['9:00', '15:00', '21:00'], 'hashtag_limit': 2}
        }

    def _suggest_format(self, platform: str, topic: str) -> str:
        """Suggest content format for platform"""
        formats = self.content_templates.get(platform, ['basic_post'])
        return formats[0]  # Simple default

    def _get_platform_times(self, platform: str) -> List[str]:
        """Get best posting times for platform"""
        return self.platform_best_practices.get(platform, {}).get('best_times', ['9:00'])

    def _suggest_hashtags(self, topic: str, platform: str) -> List[str]:
        """Suggest relevant hashtags"""
        # Simple hashtag suggestions based on topic keywords
        words = topic.lower().split()
        hashtags = [f"#{word}" for word in words[:3]]

        # Add platform-specific common hashtags
        common_hashtags = {
            'instagram': ['#content', '#creator'],
            'linkedin': ['#professional', '#business'],
            'twitter': ['#content', '#social']
        }

        hashtags.extend(common_hashtags.get(platform, []))
        return hashtags[:5]

    # Content Commands
    def plan_content(self, topic: str, platforms: List[str] = None):
        """Plan content topics for multiple platforms"""
        platforms = platforms or ["instagram", "linkedin", "twitter"]

        print(f"📝 Planning content for: {topic}")
        print(f"📱 Target platforms: {', '.join(platforms)}")

        try:
            # Simple content planning (no AI generation)
            content_plan = {
                platform: {
                    "topic": topic,
                    "suggested_format": self._suggest_format(platform, topic),
                    "best_posting_times": self._get_platform_times(platform),
                    "hashtag_suggestions": self._suggest_hashtags(topic, platform)
                }
                for platform in platforms
            }

            print("\n📋 Content Plan Created:")
            for platform, plan in content_plan.items():
                print(f"\n{platform.upper()}:")
                print(f"Format: {plan['suggested_format']}")
                print(f"Best times: {', '.join(plan['best_posting_times'])}")
                if plan['hashtag_suggestions']:
                    print(f"Hashtags: {', '.join(plan['hashtag_suggestions'][:5])}")

            return {"success": True, "content_plan": content_plan}

        except Exception as e:
            print(f"❌ Content planning failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_content_performance(self, days: int = 30):
        """Analyze content performance over specified days"""
        print(f"📊 Analyzing content performance (last {days} days)")

        try:
            # Get analytics from dashboard
            dashboard_data = self.analytics_dashboard.generate_revenue_dashboard(f"{days}_days")
            content_attribution = dashboard_data.get("content_attribution", {})

            print("\n🏆 Top Performing Content:")
            for content in content_attribution.get("top_performing_content", [])[:5]:
                print(f"  • {content.get('content_type', 'Unknown')} on {content.get('platform', 'Unknown')}")
                print(f"    Revenue: ${content.get('revenue', 0):.2f}")
                print(f"    CTR: {content.get('ctr', 0):.1%}")
                print(f"    Conversions: {content.get('conversions', 0)}")
                print()

            print("📈 Platform Performance:")
            for platform in content_attribution.get("platform_performance", []):
                print(f"  • {platform.get('platform', 'Unknown')}: ${platform.get('revenue', 0):.2f}")

            return {"success": True, "data": content_attribution}

        except Exception as e:
            print(f"❌ Content analysis failed: {e}")
            return {"success": False, "error": str(e)}

    # Audience Commands
    def track_engagement(self):
        """Track basic engagement metrics"""
        print("📊 Tracking engagement metrics (manual entry required)")

        try:
            # Basic metric tracking - requires manual input
            metrics = {
                'followers_current': self.config.get('current_followers', 0),
                'posts_this_month': self.config.get('monthly_posts', 0),
                'avg_engagement_rate': self.config.get('engagement_rate', 0.0),
                'top_performing_posts': self.config.get('top_posts', [])
            }

            print(f"\n📈 Current Metrics:")
            print(f"  • Followers: {metrics['followers_current']:,}")
            print(f"  • Posts this month: {metrics['posts_this_month']}")
            print(f"  • Average engagement rate: {metrics['avg_engagement_rate']:.1f}%")

            # Simple recommendations based on data
            recommendations = []
            if metrics['posts_this_month'] < 8:
                recommendations.append("Consider posting more consistently (aim for 8-12 posts/month)")
            if metrics['avg_engagement_rate'] < 2.0:
                recommendations.append("Focus on engaging with your audience more")

            if recommendations:
                print(f"\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"  • {rec}")

            return {"success": True, "metrics": metrics, "recommendations": recommendations}

        except Exception as e:
            print(f"❌ Engagement tracking failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_audience_growth(self):
        """Analyze audience growth performance"""
        print("📊 Analyzing audience growth performance")

        try:
            analysis = self.audience_automator.analyze_outreach_performance()

            print("\n🎯 Connection Performance:")
            conn_data = analysis["connection_requests"]
            print(f"  • Requests sent: {conn_data['sent']}")
            print(f"  • Accepted: {conn_data['accepted']}")
            print(f"  • Acceptance rate: {conn_data['acceptance_rate']:.1%}")

            print("\n💬 Message Performance:")
            msg_data = analysis["follow_up_messages"]
            print(f"  • Messages sent: {msg_data['sent']}")
            print(f"  • Responses received: {msg_data['responses']}")
            print(f"  • Response rate: {msg_data['response_rate']:.1%}")

            print("\n💡 Recommendations:")
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")

            return {"success": True, "analysis": analysis}

        except Exception as e:
            print(f"❌ Audience analysis failed: {e}")
            return {"success": False, "error": str(e)}

    # Lead & Revenue Commands
    def track_revenue(self, timeframe: str = "30_days"):
        """Generate revenue analytics report"""
        print(f"💰 Generating revenue report ({timeframe})")

        try:
            dashboard_data = self.analytics_dashboard.generate_revenue_dashboard(timeframe)
            summary = dashboard_data["summary_metrics"]

            print(f"\n💵 Revenue Summary:")
            print(f"  • Total Revenue: ${summary['total_revenue']:,.2f}")
            print(f"  • Growth Rate: {summary['growth_rate']:+.1f}%")
            print(f"  • Target Progress: {summary['target_progress']:.1f}%")
            print(f"  • Unique Customers: {summary['unique_customers']:,}")
            print(f"  • Average Order Value: ${summary['avg_order_value']:.2f}")

            print(f"\n🎯 Revenue by Stream:")
            for stream, amount in summary["revenue_by_stream"].items():
                target = self.analytics_dashboard.revenue_targets.get(stream, 0)
                progress = (amount / target * 100) if target > 0 else 0
                print(f"  • {stream.title()}: ${amount:,.2f} ({progress:.1f}% of target)")

            # Show forecasts
            forecasts = dashboard_data.get("forecasts", {})
            if forecasts:
                print(f"\n🔮 Revenue Forecast:")
                print(f"  • Next 30 days: ${forecasts.get('next_30_days', 0):,.2f}")
                print(f"  • Trend: {forecasts.get('trend_direction', 'stable').title()}")

            return {"success": True, "data": dashboard_data}

        except Exception as e:
            print(f"❌ Revenue tracking failed: {e}")
            return {"success": False, "error": str(e)}

    def optimize_funnel(self):
        """Analyze and optimize conversion funnel"""
        print("🔄 Analyzing conversion funnel")

        try:
            analysis = self.analytics_dashboard.analyze_conversion_funnel(30)

            print("\n📊 Funnel Performance:")
            for stage in analysis["funnel_stages"]:
                print(f"  • {stage['stage'].title()}: {stage['visitors']:,} visitors → {stage['conversions']:,} conversions ({stage['conversion_rate']:.1%})")

            if analysis.get("bottleneck_stage"):
                print(f"\n⚠️  Bottleneck detected at: {analysis['bottleneck_stage'].title()}")

            print("\n📉 Drop-off Analysis:")
            for drop_off in analysis["drop_off_analysis"]:
                print(f"  • {drop_off['from_stage']} → {drop_off['to_stage']}: {drop_off['drop_off_rate']:.1%} drop-off")

            # Generate recommendations
            recommendations = self.analytics_dashboard._generate_optimization_recommendations()
            print(f"\n💡 Optimization Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec.get('title', 'Optimize conversion rates')}")
                print(f"     Impact: {rec.get('expected_impact', 'Unknown')}")
                print(f"     Priority: {rec.get('priority', 'medium').title()}")

            return {"success": True, "analysis": analysis, "recommendations": recommendations}

        except Exception as e:
            print(f"❌ Funnel optimization failed: {e}")
            return {"success": False, "error": str(e)}

    # Product Commands
    def create_course(self, topic: str, audience: str, length: str = "8 hours"):
        """Create a complete course"""
        print(f"🎓 Creating course: {topic}")
        print(f"👥 Target audience: {audience}")

        try:
            # Generate course outline
            outline = self.product_factory.generate_course_outline(topic, audience, length)
            print(f"✅ Course outline generated: {outline.get('title', 'Unknown')}")
            print(f"📚 Modules: {len(outline.get('modules', []))}")

            # Create course content
            course_id = f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            content = self.product_factory.create_course_content(course_id, outline)

            print(f"✅ Course content generated")
            print(f"📝 Total lessons: {sum(len(module.get('lessons', [])) for module in content['modules'])}")
            print(f"📋 Assessments: {len(content['assessments'])}")
            print(f"📎 Resources: {len(content['resources'])}")

            return {"success": True, "course_id": course_id, "outline": outline, "content": content}

        except Exception as e:
            print(f"❌ Course creation failed: {e}")
            return {"success": False, "error": str(e)}

    def create_templates(self, category: str, count: int = 5):
        """Create template library for category"""
        print(f"📄 Creating {count} templates for category: {category}")

        try:
            templates = self.product_factory.create_template_library(category, count)

            print(f"✅ Templates created:")
            for template in templates:
                print(f"  • {template.name}")
                print(f"    Use cases: {len(template.use_cases)}")

            return {"success": True, "templates": templates}

        except Exception as e:
            print(f"❌ Template creation failed: {e}")
            return {"success": False, "error": str(e)}

    # Workflow Commands
    async def run_workflow(self, workflow_id: str):
        """Run a specific workflow"""
        print(f"⚙️  Running workflow: {workflow_id}")

        try:
            result = await self.orchestrator.execute_workflow(workflow_id)

            if result.get("status") == "completed":
                print(f"✅ Workflow completed successfully")
                print(f"⏱️  Execution time: {result.get('execution_time', 0):.1f} seconds")

                if result.get("failed_steps"):
                    print(f"⚠️  Some steps failed: {', '.join(result['failed_steps'])}")
            else:
                print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
            return {"success": False, "error": str(e)}

    def list_workflows(self):
        """List available workflows"""
        print("📋 Available Workflows:")

        status_data = self.orchestrator.get_workflow_status()

        for workflow in status_data["workflows"]:
            status_emoji = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
                "paused": "⏸️"
            }.get(workflow["status"], "❓")

            print(f"  {status_emoji} {workflow['id']}")
            print(f"    Status: {workflow['status']}")
            print(f"    Executions: {workflow['execution_count']}")
            print(f"    Success Rate: {workflow['success_rate']:.1f}%")
            if workflow['last_run']:
                print(f"    Last Run: {workflow['last_run'][:16]}")
            print()

        return status_data

    def schedule_workflow(self, workflow_id: str, schedule: str):
        """Schedule a workflow for automatic execution"""
        print(f"📅 Scheduling workflow: {workflow_id}")
        print(f"⏰ Schedule: {schedule}")

        try:
            # Parse schedule string (e.g., "daily_09:00", "weekly_monday_10:00")
            schedule_parts = schedule.split("_")

            if schedule_parts[0] == "daily":
                schedule_config = {
                    "schedule": "daily",
                    "time": schedule_parts[1] if len(schedule_parts) > 1 else "09:00"
                }
            elif schedule_parts[0] == "weekly":
                schedule_config = {
                    "schedule": "weekly",
                    "day": schedule_parts[1] if len(schedule_parts) > 1 else "monday",
                    "time": schedule_parts[2] if len(schedule_parts) > 2 else "09:00"
                }
            else:
                print(f"❌ Invalid schedule format: {schedule}")
                print("💡 Use format: daily_HH:MM or weekly_day_HH:MM")
                return {"success": False, "error": "Invalid schedule format"}

            result = self.orchestrator.schedule_workflow(workflow_id, schedule_config)

            if result.get("scheduled"):
                print(f"✅ Workflow scheduled successfully")
                print(f"⏰ Next run: {result.get('next_run', 'Unknown')}")
            else:
                print(f"❌ Scheduling failed: {result.get('error', 'Unknown error')}")

            return result

        except Exception as e:
            print(f"❌ Workflow scheduling failed: {e}")
            return {"success": False, "error": str(e)}

    # Utility Commands
    def status(self):
        """Show overall system status"""
        print("🔍 System Status Check")
        print("=" * 50)

        try:
            # Check configuration
            print("⚙️  Configuration: ✅ Loaded")

            # Check workflows
            workflow_status = self.orchestrator.get_workflow_status()
            active_workflows = len([w for w in workflow_status["workflows"] if w["status"] == "running"])
            print(f"📋 Workflows: {len(workflow_status['workflows'])} total, {active_workflows} running")

            # Check recent revenue
            try:
                revenue_data = self.analytics_dashboard.generate_revenue_dashboard("7_days")
                total_revenue = revenue_data["summary_metrics"]["total_revenue"]
                print(f"💰 Revenue (7 days): ${total_revenue:.2f}")
            except:
                print("💰 Revenue: ❌ Unable to fetch")

            # Check audience metrics
            try:
                metrics = self.audience_automator.track_growth_metrics()
                print(f"👥 Audience: {metrics.followers_current:,} followers ({metrics.growth_rate:+.1f}%)")
            except:
                print("👥 Audience: ❌ Unable to fetch")

            print("\n✅ System operational")
            return {"success": True}

        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return {"success": False, "error": str(e)}

    def quick_start(self):
        """Run quick start setup and first automation"""
        print("🚀 Quick Start - Setting up your first automation")
        print("=" * 50)

        try:
            # 1. Create sample content
            print("\n1️⃣  Creating sample content...")
            content_result = self.create_content(
                "5 AI tools that will transform your productivity in 2024",
                ["linkedin", "twitter"]
            )

            if not content_result["success"]:
                raise Exception("Content creation failed")

            # 2. Find some prospects
            print("\n2️⃣  Finding growth prospects...")
            audience_result = self.grow_audience("conservative")

            if not audience_result["success"]:
                raise Exception("Audience growth setup failed")

            # 3. Set up basic automation
            print("\n3️⃣  Setting up daily automation...")
            schedule_result = self.schedule_workflow("daily_content_automation", "daily_09:00")

            if not schedule_result["success"]:
                raise Exception("Workflow scheduling failed")

            # 4. Show initial metrics
            print("\n4️⃣  Current status:")
            self.status()

            print("\n🎉 Quick start completed successfully!")
            print("\n📋 What's next:")
            print("1. Configure more API keys for full functionality")
            print("2. Review and customize your workflows")
            print("3. Monitor your daily automation results")
            print("4. Scale up your outreach as you see success")

            return {"success": True}

        except Exception as e:
            print(f"❌ Quick start failed: {e}")
            print("💡 Try running individual commands to identify the issue")
            return {"success": False, "error": str(e)}


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Micro-Influencer AI Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py content create "AI productivity tips" --platforms linkedin twitter
  python main.py audience grow --strategy balanced
  python main.py revenue track --timeframe 30_days
  python main.py workflow run daily_content_automation
  python main.py workflow schedule daily_content_automation daily_09:00
  python main.py quick-start
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Content commands
    content_parser = subparsers.add_parser("content", help="Content creation and analysis")
    content_subparsers = content_parser.add_subparsers(dest="content_action")

    create_content_parser = content_subparsers.add_parser("create", help="Create multi-platform content")
    create_content_parser.add_argument("topic", help="Content topic or idea")
    create_content_parser.add_argument("--platforms", nargs="+", default=["linkedin", "twitter", "substack"], help="Target platforms")

    analyze_content_parser = content_subparsers.add_parser("analyze", help="Analyze content performance")
    analyze_content_parser.add_argument("--days", type=int, default=30, help="Analysis timeframe in days")

    # Audience commands
    audience_parser = subparsers.add_parser("audience", help="Audience growth and analysis")
    audience_subparsers = audience_parser.add_subparsers(dest="audience_action")

    grow_audience_parser = audience_subparsers.add_parser("grow", help="Execute audience growth campaign")
    grow_audience_parser.add_argument("--strategy", choices=["aggressive", "balanced", "conservative"], default="balanced", help="Growth strategy")

    audience_subparsers.add_parser("analyze", help="Analyze audience growth performance")

    # Revenue commands
    revenue_parser = subparsers.add_parser("revenue", help="Revenue tracking and optimization")
    revenue_subparsers = revenue_parser.add_subparsers(dest="revenue_action")

    track_revenue_parser = revenue_subparsers.add_parser("track", help="Generate revenue report")
    track_revenue_parser.add_argument("--timeframe", choices=["7_days", "30_days", "90_days"], default="30_days", help="Report timeframe")

    revenue_subparsers.add_parser("optimize", help="Analyze and optimize conversion funnel")

    # Product commands
    product_parser = subparsers.add_parser("product", help="Digital product creation")
    product_subparsers = product_parser.add_subparsers(dest="product_action")

    create_course_parser = product_subparsers.add_parser("course", help="Create a complete course")
    create_course_parser.add_argument("topic", help="Course topic")
    create_course_parser.add_argument("audience", help="Target audience")
    create_course_parser.add_argument("--length", default="8 hours", help="Course length")

    create_templates_parser = product_subparsers.add_parser("templates", help="Create template library")
    create_templates_parser.add_argument("category", help="Template category")
    create_templates_parser.add_argument("--count", type=int, default=5, help="Number of templates")

    # Workflow commands
    workflow_parser = subparsers.add_parser("workflow", help="Workflow management")
    workflow_subparsers = workflow_parser.add_subparsers(dest="workflow_action")

    run_workflow_parser = workflow_subparsers.add_parser("run", help="Run a workflow")
    run_workflow_parser.add_argument("workflow_id", help="Workflow ID to run")

    workflow_subparsers.add_parser("list", help="List available workflows")

    schedule_workflow_parser = workflow_subparsers.add_parser("schedule", help="Schedule a workflow")
    schedule_workflow_parser.add_argument("workflow_id", help="Workflow ID to schedule")
    schedule_workflow_parser.add_argument("schedule", help="Schedule (e.g., daily_09:00, weekly_monday_10:00)")

    # Utility commands
    subparsers.add_parser("status", help="Show system status")
    subparsers.add_parser("quick-start", help="Run quick start setup")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize the manager
    try:
        manager = InfluencerSuiteManager()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        sys.exit(1)

    # Execute commands
    try:
        if args.command == "content":
            if args.content_action == "create":
                manager.create_content(args.topic, args.platforms)
            elif args.content_action == "analyze":
                manager.analyze_content_performance(args.days)

        elif args.command == "audience":
            if args.audience_action == "grow":
                manager.grow_audience(args.strategy)
            elif args.audience_action == "analyze":
                manager.analyze_audience_growth()

        elif args.command == "revenue":
            if args.revenue_action == "track":
                manager.track_revenue(args.timeframe)
            elif args.revenue_action == "optimize":
                manager.optimize_funnel()

        elif args.command == "product":
            if args.product_action == "course":
                manager.create_course(args.topic, args.audience, args.length)
            elif args.product_action == "templates":
                manager.create_templates(args.category, args.count)

        elif args.command == "workflow":
            if args.workflow_action == "run":
                asyncio.run(manager.run_workflow(args.workflow_id))
            elif args.workflow_action == "list":
                manager.list_workflows()
            elif args.workflow_action == "schedule":
                manager.schedule_workflow(args.workflow_id, args.schedule)

        elif args.command == "status":
            manager.status()

        elif args.command == "quick-start":
            manager.quick_start()

    except KeyboardInterrupt:
        print("\n\n⏸️  Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Command failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()