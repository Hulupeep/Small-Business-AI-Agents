"""
Setup and Installation Script for Micro-Influencer AI Toolkit
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List
import argparse

class InfluencerSuiteSetup:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_path = self.base_path / "config"
        self.config_path.mkdir(exist_ok=True)

        # Default configuration
        self.default_config = {
            "profile": "micro-influencer",
            "target_revenue": 25000,
            "current_revenue": 8000,
            "platforms": ["linkedin", "substack", "twitter"],
            "niche": "AI/productivity",
            "audience_size": {
                "linkedin": 15000,
                "substack": 3000,
                "twitter": 5000
            },
            "goals": {
                "monthly_growth_rate": 0.15,
                "conversion_rate_target": 0.08,
                "content_frequency": "daily"
            }
        }

    def run_setup(self, profile: str = "micro-influencer"):
        """Run complete setup process"""

        print("🚀 Micro-Influencer AI Toolkit Setup")
        print("=" * 50)

        try:
            # Step 1: Check dependencies
            print("\n1. Checking dependencies...")
            self.check_dependencies()

            # Step 2: Install Python packages
            print("\n2. Installing Python packages...")
            self.install_python_packages()

            # Step 3: Setup configuration
            print("\n3. Setting up configuration...")
            self.setup_configuration(profile)

            # Step 4: Initialize databases
            print("\n4. Initializing databases...")
            self.initialize_databases()

            # Step 5: Setup API integrations
            print("\n5. Setting up API integrations...")
            self.setup_api_integrations()

            # Step 6: Create sample workflows
            print("\n6. Creating sample workflows...")
            self.create_sample_workflows()

            # Step 7: Verify installation
            print("\n7. Verifying installation...")
            self.verify_installation()

            print("\n✅ Setup completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Configure your API keys in config/api_keys.json")
            print("2. Run: python -m influencer_suite.main --help")
            print("3. Start with: python -m influencer_suite.main run daily_content_automation")

        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            sys.exit(1)

    def check_dependencies(self):
        """Check system dependencies"""

        dependencies = {
            "python": "python --version",
            "pip": "pip --version",
            "git": "git --version"
        }

        for dep, cmd in dependencies.items():
            try:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {dep}: {result.stdout.strip()}")
                else:
                    raise Exception(f"{dep} not found")
            except Exception as e:
                print(f"  ❌ {dep}: {e}")
                raise

    def install_python_packages(self):
        """Install required Python packages"""

        requirements = [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "requests>=2.31.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "sqlite3",  # Built into Python
            "schedule>=1.2.0",
            "plotly>=5.15.0",
            "jinja2>=3.1.0",
            "python-dotenv>=1.0.0",
            "stripe>=5.5.0",
            "selenium>=4.10.0",
            "beautifulsoup4>=4.12.0",
            "dataclasses-json>=0.5.0",
            "asyncio",  # Built into Python 3.7+
            "concurrent.futures",  # Built into Python 3.2+
            "logging",  # Built into Python
            "datetime",  # Built into Python
            "json",  # Built into Python
            "typing",  # Built into Python 3.5+
            "enum",  # Built into Python 3.4+
            "pathlib",  # Built into Python 3.4+
            "argparse",  # Built into Python
        ]

        # Filter out built-in modules
        external_packages = [
            pkg for pkg in requirements
            if not self._is_builtin_module(pkg.split(">=")[0])
        ]

        for package in external_packages:
            try:
                print(f"  Installing {package}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"  ✅ {package} installed")
                else:
                    print(f"  ⚠️  {package} installation warning: {result.stderr}")

            except Exception as e:
                print(f"  ❌ Failed to install {package}: {e}")

    def _is_builtin_module(self, module_name: str) -> bool:
        """Check if module is built into Python"""
        builtin_modules = {
            "sqlite3", "asyncio", "concurrent.futures", "logging",
            "datetime", "json", "typing", "enum", "pathlib", "argparse"
        }
        return module_name in builtin_modules

    def setup_configuration(self, profile: str):
        """Setup configuration files"""

        # Create profile-specific config
        profile_config = self.default_config.copy()
        profile_config["profile"] = profile

        if profile == "micro-influencer":
            profile_config.update({
                "target_revenue": 25000,
                "current_revenue": 8000,
                "audience_size": {"linkedin": 15000, "substack": 3000},
                "goals": {
                    "monthly_growth_rate": 0.15,
                    "content_frequency": "daily",
                    "outreach_daily_limit": 50
                }
            })
        elif profile == "creator":
            profile_config.update({
                "target_revenue": 50000,
                "current_revenue": 15000,
                "audience_size": {"linkedin": 50000, "youtube": 10000, "substack": 8000},
                "goals": {
                    "monthly_growth_rate": 0.20,
                    "content_frequency": "multiple_daily",
                    "outreach_daily_limit": 100
                }
            })

        # Save main config
        config_file = self.config_path / "config.json"
        with open(config_file, "w") as f:
            json.dump(profile_config, f, indent=2)

        print(f"  ✅ Configuration saved to {config_file}")

        # Create API keys template
        api_keys_template = {
            "openai_api_key": "your-openai-api-key-here",
            "anthropic_api_key": "your-anthropic-api-key-here",
            "linkedin_access_token": "your-linkedin-access-token-here",
            "substack_api_key": "your-substack-api-key-here",
            "convertkit_api_key": "your-convertkit-api-key-here",
            "convertkit_api_secret": "your-convertkit-api-secret-here",
            "stripe_api_key": "your-stripe-api-key-here",
            "calendly_api_token": "your-calendly-api-token-here",
            "gumroad_access_token": "your-gumroad-access-token-here",
            "teachable_api_key": "your-teachable-api-key-here",
            "twitter_bearer_token": "your-twitter-bearer-token-here",
            "zapier_webhook_url": "your-zapier-webhook-url-here"
        }

        api_keys_file = self.config_path / "api_keys.json"
        if not api_keys_file.exists():
            with open(api_keys_file, "w") as f:
                json.dump(api_keys_template, f, indent=2)
            print(f"  ✅ API keys template created at {api_keys_file}")
            print("  ⚠️  Please update api_keys.json with your actual API keys")

    def initialize_databases(self):
        """Initialize SQLite databases for each agent"""

        import sqlite3
        from datetime import datetime

        databases = [
            "audience_growth.db",
            "lead_pipeline.db",
            "product_factory.db",
            "revenue_analytics.db"
        ]

        db_path = self.base_path / "databases"
        db_path.mkdir(exist_ok=True)

        for db_name in databases:
            db_file = db_path / db_name

            # Create database with basic structure
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Create a basic tracking table for each database
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS setup_info (
                    id INTEGER PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version TEXT,
                    profile TEXT
                )
            ''')

            cursor.execute('''
                INSERT INTO setup_info (version, profile) VALUES (?, ?)
            ''', ("1.0.0", self.default_config["profile"]))

            conn.commit()
            conn.close()

            print(f"  ✅ Database initialized: {db_name}")

    def setup_api_integrations(self):
        """Setup API integration configurations"""

        integrations_config = {
            "linkedin": {
                "enabled": True,
                "daily_connection_limit": 50,
                "message_templates": {
                    "initial": "Hi {name}, I enjoyed your recent post about {topic}. Would love to connect!",
                    "follow_up": "Thanks for connecting! I share similar content about AI and productivity."
                },
                "automation_schedule": "09:00"
            },
            "substack": {
                "enabled": True,
                "publication_schedule": "thursday_10am",
                "subscriber_goals": {
                    "monthly_growth": 300,
                    "target_open_rate": 0.45
                }
            },
            "convertkit": {
                "enabled": True,
                "sequences": {
                    "welcome": "activated",
                    "tripwire_nurture": "activated",
                    "webinar": "activated"
                }
            },
            "stripe": {
                "enabled": True,
                "products": {
                    "tripwire": {"name": "AI Starter Guide", "price": 27},
                    "core": {"name": "Productivity Mastery", "price": 297},
                    "premium": {"name": "1:1 Coaching", "price": 2997}
                }
            }
        }

        integrations_file = self.config_path / "integrations.json"
        with open(integrations_file, "w") as f:
            json.dump(integrations_config, f, indent=2)

        print(f"  ✅ Integration config saved to {integrations_file}")

    def create_sample_workflows(self):
        """Create sample workflow definitions"""

        workflows_dir = self.base_path / "workflows" / "samples"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Quick start workflow
        quick_start_workflow = {
            "id": "quick_start_automation",
            "name": "Quick Start - Daily Automation",
            "description": "Essential daily tasks for micro-influencer growth",
            "trigger_type": "time_based",
            "trigger_config": {"schedule": "daily", "time": "09:00"},
            "steps": [
                {
                    "id": "morning_content_creation",
                    "name": "Create Morning Content",
                    "agent": "content_engine",
                    "action": "generate_daily_post",
                    "parameters": {"platform": "linkedin", "niche": "AI productivity"},
                    "dependencies": []
                },
                {
                    "id": "audience_engagement",
                    "name": "Engage with Audience",
                    "agent": "audience_automator",
                    "action": "daily_engagement_routine",
                    "parameters": {"engagement_limit": 20},
                    "dependencies": ["morning_content_creation"]
                },
                {
                    "id": "lead_follow_up",
                    "name": "Follow Up with Leads",
                    "agent": "lead_pipeline",
                    "action": "daily_lead_nurture",
                    "parameters": {"max_contacts": 10},
                    "dependencies": ["audience_engagement"]
                }
            ]
        }

        # Growth accelerator workflow
        growth_workflow = {
            "id": "growth_accelerator",
            "name": "Weekly Growth Accelerator",
            "description": "Intensive growth activities for rapid audience expansion",
            "trigger_type": "time_based",
            "trigger_config": {"schedule": "weekly", "day": "monday", "time": "08:00"},
            "steps": [
                {
                    "id": "competitor_analysis",
                    "name": "Analyze Competitor Content",
                    "agent": "content_engine",
                    "action": "analyze_trending_content",
                    "parameters": {"competitors": ["ai_productivity_leaders"]},
                    "dependencies": []
                },
                {
                    "id": "content_calendar_planning",
                    "name": "Plan Weekly Content Calendar",
                    "agent": "content_engine",
                    "action": "create_weekly_calendar",
                    "parameters": {"platforms": ["linkedin", "twitter", "substack"]},
                    "dependencies": ["competitor_analysis"]
                },
                {
                    "id": "prospect_research",
                    "name": "Research New Prospects",
                    "agent": "audience_automator",
                    "action": "find_weekly_prospects",
                    "parameters": {"target_count": 200},
                    "dependencies": ["content_calendar_planning"]
                }
            ]
        }

        # Save sample workflows
        sample_workflows = [quick_start_workflow, growth_workflow]

        for workflow in sample_workflows:
            workflow_file = workflows_dir / f"{workflow['id']}.json"
            with open(workflow_file, "w") as f:
                json.dump(workflow, f, indent=2)
            print(f"  ✅ Sample workflow created: {workflow['name']}")

    def verify_installation(self):
        """Verify that installation was successful"""

        verification_checks = [
            ("Config files", self._check_config_files),
            ("Database files", self._check_database_files),
            ("Python modules", self._check_python_modules),
            ("Directory structure", self._check_directory_structure)
        ]

        all_passed = True

        for check_name, check_func in verification_checks:
            try:
                check_func()
                print(f"  ✅ {check_name}: OK")
            except Exception as e:
                print(f"  ❌ {check_name}: {e}")
                all_passed = False

        if not all_passed:
            raise Exception("Installation verification failed")

    def _check_config_files(self):
        """Check that config files exist"""
        required_files = ["config.json", "api_keys.json", "integrations.json"]
        for file in required_files:
            if not (self.config_path / file).exists():
                raise Exception(f"Missing config file: {file}")

    def _check_database_files(self):
        """Check that database files were created"""
        db_path = self.base_path / "databases"
        if not db_path.exists():
            raise Exception("Database directory not found")

        required_dbs = ["audience_growth.db", "lead_pipeline.db", "product_factory.db", "revenue_analytics.db"]
        for db in required_dbs:
            if not (db_path / db).exists():
                raise Exception(f"Missing database: {db}")

    def _check_python_modules(self):
        """Check that key Python modules can be imported"""
        key_modules = ["openai", "requests", "pandas", "sqlite3"]
        for module in key_modules:
            try:
                __import__(module)
            except ImportError:
                raise Exception(f"Cannot import module: {module}")

    def _check_directory_structure(self):
        """Check that directory structure is correct"""
        required_dirs = ["agents", "integrations", "workflows", "config"]
        for dir_name in required_dirs:
            if not (self.base_path / dir_name).exists():
                raise Exception(f"Missing directory: {dir_name}")

    def create_launcher_script(self):
        """Create a launcher script for easy access"""

        launcher_content = f'''#!/usr/bin/env python3
"""
Micro-Influencer AI Toolkit Launcher
Quick access to all toolkit functions
"""

import sys
import os
sys.path.insert(0, "{self.base_path}")

from influencer_suite.main import main

if __name__ == "__main__":
    main()
'''

        launcher_file = self.base_path / "launch.py"
        with open(launcher_file, "w") as f:
            f.write(launcher_content)

        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(launcher_file, 0o755)

        print(f"  ✅ Launcher script created: {launcher_file}")

    def generate_quick_start_guide(self):
        """Generate a quick start guide"""

        guide_content = """# Micro-Influencer AI Toolkit - Quick Start Guide

## 🚀 Getting Started

### 1. Configure API Keys
Edit `config/api_keys.json` with your actual API keys:
- OpenAI API key (required for AI content generation)
- LinkedIn access token (for LinkedIn automation)
- ConvertKit API credentials (for email marketing)
- Stripe API key (for payment processing)

### 2. Basic Commands

```bash
# Run daily content automation
python launch.py run daily_content_automation

# Check workflow status
python launch.py status

# Generate revenue report
python launch.py report monthly

# Start audience growth campaign
python launch.py run weekly_audience_growth
```

### 3. First Week Action Plan

#### Day 1-2: Setup
- [ ] Configure all API keys
- [ ] Test basic content generation
- [ ] Verify LinkedIn integration

#### Day 3-4: Content
- [ ] Run content multiplication engine
- [ ] Schedule first week of posts
- [ ] Create lead magnets

#### Day 5-7: Growth
- [ ] Start audience growth automation
- [ ] Launch email sequences
- [ ] Begin revenue tracking

### 4. Expected Results (First Month)

- **Content**: 50+ pieces across platforms
- **Audience Growth**: 200+ new LinkedIn connections
- **Email Subscribers**: 100+ new subscribers
- **Revenue**: 15-20% increase from baseline

### 5. Troubleshooting

**Common Issues:**
- API rate limits: Adjust timing in config
- Content quality: Refine prompts in templates
- Low engagement: A/B test different content styles

**Support:**
- Check logs in `logs/` directory
- Review workflow status with `python launch.py status`
- Adjust parameters in `config/config.json`

### 6. Advanced Features

After mastering basics, explore:
- Custom workflow creation
- Advanced analytics dashboards
- A/B testing automation
- Cross-platform attribution

---

**Ready to scale your influence? Start with the daily automation workflow!**
"""

        guide_file = self.base_path / "QUICK_START.md"
        with open(guide_file, "w") as f:
            f.write(guide_content)

        print(f"  ✅ Quick start guide created: {guide_file}")


def main():
    parser = argparse.ArgumentParser(description="Setup Micro-Influencer AI Toolkit")
    parser.add_argument(
        "--profile",
        choices=["micro-influencer", "creator", "enterprise"],
        default="micro-influencer",
        help="Installation profile"
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip installation verification"
    )

    args = parser.parse_args()

    setup = InfluencerSuiteSetup()

    try:
        setup.run_setup(args.profile)

        if not args.skip_verification:
            print("\n🔧 Creating additional setup files...")
            setup.create_launcher_script()
            setup.generate_quick_start_guide()

        print("\n🎉 Installation Complete!")
        print("\n📚 Next steps:")
        print("1. Read QUICK_START.md for usage instructions")
        print("2. Configure your API keys in config/api_keys.json")
        print("3. Run: python launch.py run daily_content_automation")

    except KeyboardInterrupt:
        print("\n\n⏸️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()