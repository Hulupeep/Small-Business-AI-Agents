"""
Automation Sequences and Workflows
Complete automation orchestration for micro-influencer growth
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import schedule
import time
from concurrent.futures import ThreadPoolExecutor
import logging

# Import our agents
from ..agents.content_multiplication_engine import ContentMultiplicationEngine
from ..agents.audience_growth_automator import AudienceGrowthAutomator
from ..agents.lead_conversion_pipeline import LeadConversionPipeline
from ..agents.digital_product_factory import DigitalProductFactory
from ..agents.revenue_analytics_dashboard import RevenueAnalyticsDashboard
from ..integrations.platform_apis import PlatformIntegrationManager

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class TriggerType(Enum):
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    METRIC_BASED = "metric_based"
    MANUAL = "manual"

@dataclass
class WorkflowStep:
    id: str
    name: str
    agent: str
    action: str
    parameters: Dict
    dependencies: List[str]
    timeout_minutes: int = 30
    retry_count: int = 3
    error_handling: str = "continue"  # continue, stop, retry

@dataclass
class Workflow:
    id: str
    name: str
    description: str
    trigger_type: TriggerType
    trigger_config: Dict
    steps: List[WorkflowStep]
    status: WorkflowStatus
    created_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0

class AutomationOrchestrator:
    def __init__(self, config: Dict):
        self.config = config
        self.workflows: Dict[str, Workflow] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}

        # Initialize agents
        self.content_engine = ContentMultiplicationEngine(config)
        self.audience_automator = AudienceGrowthAutomator(config)
        self.lead_pipeline = LeadConversionPipeline(config)
        self.product_factory = DigitalProductFactory(config)
        self.analytics_dashboard = RevenueAnalyticsDashboard(config)
        self.platform_manager = PlatformIntegrationManager(config)

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Register built-in workflows
        self._register_built_in_workflows()

        # Start scheduler
        self.scheduler_running = False

    def _register_built_in_workflows(self):
        """Register pre-built automation workflows"""

        # Daily content creation and distribution workflow
        daily_content_workflow = Workflow(
            id="daily_content_automation",
            name="Daily Content Creation & Distribution",
            description="Automatically create and distribute content across all platforms",
            trigger_type=TriggerType.TIME_BASED,
            trigger_config={"schedule": "daily", "time": "09:00"},
            steps=[
                WorkflowStep(
                    id="generate_content_ideas",
                    name="Generate Content Ideas",
                    agent="content_engine",
                    action="generate_content_ideas",
                    parameters={"count": 3, "niche": "AI productivity"},
                    dependencies=[]
                ),
                WorkflowStep(
                    id="create_multi_platform_content",
                    name="Create Multi-Platform Content",
                    agent="content_engine",
                    action="multiply_content",
                    parameters={"platforms": ["linkedin", "twitter", "substack"]},
                    dependencies=["generate_content_ideas"]
                ),
                WorkflowStep(
                    id="schedule_content_distribution",
                    name="Schedule Content Distribution",
                    agent="platform_manager",
                    action="cross_platform_post",
                    parameters={"optimal_timing": True},
                    dependencies=["create_multi_platform_content"]
                ),
                WorkflowStep(
                    id="track_content_performance",
                    name="Track Content Performance",
                    agent="analytics_dashboard",
                    action="track_content_metrics",
                    parameters={"attribution": True},
                    dependencies=["schedule_content_distribution"]
                )
            ],
            status=WorkflowStatus.PENDING,
            created_at=datetime.now()
        )

        # Weekly audience growth workflow
        weekly_growth_workflow = Workflow(
            id="weekly_audience_growth",
            name="Weekly Audience Growth Campaign",
            description="Execute comprehensive audience growth strategy",
            trigger_type=TriggerType.TIME_BASED,
            trigger_config={"schedule": "weekly", "day": "monday", "time": "10:00"},
            steps=[
                WorkflowStep(
                    id="find_new_prospects",
                    name="Find New Prospects",
                    agent="audience_automator",
                    action="find_prospects",
                    parameters={"criteria": {"keywords": "AI productivity", "titles": ["Director", "VP", "Manager"]}},
                    dependencies=[]
                ),
                WorkflowStep(
                    id="execute_outreach_campaign",
                    name="Execute Outreach Campaign",
                    agent="audience_automator",
                    action="execute_daily_outreach",
                    parameters={"personalization_level": "high"},
                    dependencies=["find_new_prospects"]
                ),
                WorkflowStep(
                    id="analyze_growth_metrics",
                    name="Analyze Growth Metrics",
                    agent="audience_automator",
                    action="track_growth_metrics",
                    parameters={},
                    dependencies=["execute_outreach_campaign"]
                ),
                WorkflowStep(
                    id="optimize_growth_strategy",
                    name="Optimize Growth Strategy",
                    agent="audience_automator",
                    action="analyze_outreach_performance",
                    parameters={},
                    dependencies=["analyze_growth_metrics"]
                )
            ],
            status=WorkflowStatus.PENDING,
            created_at=datetime.now()
        )

        # Lead nurture and conversion workflow
        lead_nurture_workflow = Workflow(
            id="lead_nurture_automation",
            name="Automated Lead Nurturing",
            description="Nurture leads through the conversion pipeline",
            trigger_type=TriggerType.EVENT_BASED,
            trigger_config={"event": "new_lead_captured"},
            steps=[
                WorkflowStep(
                    id="score_new_lead",
                    name="Score New Lead",
                    agent="lead_pipeline",
                    action="score_lead_interaction",
                    parameters={"interaction_type": "lead_capture"},
                    dependencies=[]
                ),
                WorkflowStep(
                    id="trigger_welcome_sequence",
                    name="Trigger Welcome Sequence",
                    agent="lead_pipeline",
                    action="_trigger_email_sequence",
                    parameters={"sequence": "welcome_series"},
                    dependencies=["score_new_lead"]
                ),
                WorkflowStep(
                    id="add_to_nurture_campaign",
                    name="Add to Nurture Campaign",
                    agent="platform_manager",
                    action="automate_lead_nurture",
                    parameters={"stage": "awareness"},
                    dependencies=["trigger_welcome_sequence"]
                )
            ],
            status=WorkflowStatus.PENDING,
            created_at=datetime.now()
        )

        # Revenue optimization workflow
        revenue_optimization_workflow = Workflow(
            id="revenue_optimization",
            name="Revenue Optimization Analysis",
            description="Analyze revenue data and optimize strategies",
            trigger_type=TriggerType.TIME_BASED,
            trigger_config={"schedule": "weekly", "day": "friday", "time": "17:00"},
            steps=[
                WorkflowStep(
                    id="generate_revenue_report",
                    name="Generate Revenue Report",
                    agent="analytics_dashboard",
                    action="generate_revenue_report",
                    parameters={"report_type": "weekly"},
                    dependencies=[]
                ),
                WorkflowStep(
                    id="analyze_conversion_funnel",
                    name="Analyze Conversion Funnel",
                    agent="analytics_dashboard",
                    action="analyze_conversion_funnel",
                    parameters={"timeframe_days": 7},
                    dependencies=["generate_revenue_report"]
                ),
                WorkflowStep(
                    id="generate_optimization_recommendations",
                    name="Generate Optimization Recommendations",
                    agent="analytics_dashboard",
                    action="_generate_optimization_recommendations",
                    parameters={},
                    dependencies=["analyze_conversion_funnel"]
                ),
                WorkflowStep(
                    id="implement_quick_wins",
                    name="Implement Quick Wins",
                    agent="platform_manager",
                    action="implement_optimizations",
                    parameters={"priority": "high"},
                    dependencies=["generate_optimization_recommendations"]
                )
            ],
            status=WorkflowStatus.PENDING,
            created_at=datetime.now()
        )

        # Product launch workflow
        product_launch_workflow = Workflow(
            id="product_launch_sequence",
            name="Complete Product Launch Sequence",
            description="Orchestrate full product launch from creation to sales",
            trigger_type=TriggerType.MANUAL,
            trigger_config={},
            steps=[
                WorkflowStep(
                    id="generate_course_outline",
                    name="Generate Course Outline",
                    agent="product_factory",
                    action="generate_course_outline",
                    parameters={"topic": "AI Automation", "target_audience": "entrepreneurs"},
                    dependencies=[]
                ),
                WorkflowStep(
                    id="create_course_content",
                    name="Create Course Content",
                    agent="product_factory",
                    action="create_course_content",
                    parameters={},
                    dependencies=["generate_course_outline"]
                ),
                WorkflowStep(
                    id="create_launch_content",
                    name="Create Launch Content",
                    agent="content_engine",
                    action="create_launch_campaign",
                    parameters={"campaign_type": "product_launch"},
                    dependencies=["create_course_content"]
                ),
                WorkflowStep(
                    id="setup_sales_funnel",
                    name="Setup Sales Funnel",
                    agent="lead_pipeline",
                    action="create_product_funnel",
                    parameters={"product_type": "course"},
                    dependencies=["create_launch_content"]
                ),
                WorkflowStep(
                    id="execute_launch_campaign",
                    name="Execute Launch Campaign",
                    agent="platform_manager",
                    action="execute_launch_sequence",
                    parameters={"duration_days": 7},
                    dependencies=["setup_sales_funnel"]
                ),
                WorkflowStep(
                    id="track_launch_metrics",
                    name="Track Launch Metrics",
                    agent="analytics_dashboard",
                    action="track_launch_performance",
                    parameters={},
                    dependencies=["execute_launch_campaign"]
                )
            ],
            status=WorkflowStatus.PENDING,
            created_at=datetime.now()
        )

        # Register all workflows
        self.workflows.update({
            "daily_content_automation": daily_content_workflow,
            "weekly_audience_growth": weekly_growth_workflow,
            "lead_nurture_automation": lead_nurture_workflow,
            "revenue_optimization": revenue_optimization_workflow,
            "product_launch_sequence": product_launch_workflow
        })

    async def execute_workflow(self, workflow_id: str, context: Dict = None) -> Dict:
        """Execute a workflow asynchronously"""

        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} not found"}

        workflow = self.workflows[workflow_id]

        if workflow.status == WorkflowStatus.RUNNING:
            return {"error": f"Workflow {workflow_id} is already running"}

        # Update workflow status
        workflow.status = WorkflowStatus.RUNNING
        workflow.last_run = datetime.now()
        workflow.execution_count += 1

        self.logger.info(f"Starting workflow: {workflow.name}")

        execution_context = context or {}
        step_results = {}
        failed_steps = []

        try:
            # Execute steps based on dependencies
            completed_steps = set()

            while len(completed_steps) < len(workflow.steps):
                # Find steps ready to execute
                ready_steps = [
                    step for step in workflow.steps
                    if step.id not in completed_steps and
                    all(dep in completed_steps for dep in step.dependencies)
                ]

                if not ready_steps:
                    # Check if we're stuck due to failed dependencies
                    remaining_steps = [s for s in workflow.steps if s.id not in completed_steps]
                    if remaining_steps:
                        self.logger.error(f"Workflow stuck - remaining steps have unmet dependencies")
                        workflow.status = WorkflowStatus.FAILED
                        break
                    else:
                        break

                # Execute ready steps
                tasks = []
                for step in ready_steps:
                    task = self._execute_step(step, execution_context, step_results)
                    tasks.append((step, task))

                # Wait for completion
                for step, task in tasks:
                    try:
                        result = await task
                        step_results[step.id] = result
                        completed_steps.add(step.id)

                        if result.get("success", False):
                            self.logger.info(f"Step completed: {step.name}")
                        else:
                            self.logger.error(f"Step failed: {step.name} - {result.get('error', 'Unknown error')}")
                            failed_steps.append(step.id)

                            if step.error_handling == "stop":
                                workflow.status = WorkflowStatus.FAILED
                                break

                    except Exception as e:
                        self.logger.error(f"Step {step.name} failed with exception: {e}")
                        failed_steps.append(step.id)
                        step_results[step.id] = {"success": False, "error": str(e)}

                        if step.error_handling == "stop":
                            workflow.status = WorkflowStatus.FAILED
                            break

            # Update final status
            if workflow.status != WorkflowStatus.FAILED:
                if failed_steps:
                    workflow.status = WorkflowStatus.COMPLETED  # Partial success
                else:
                    workflow.status = WorkflowStatus.COMPLETED
                    workflow.success_count += 1

            self.logger.info(f"Workflow completed: {workflow.name} - Status: {workflow.status.value}")

            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "step_results": step_results,
                "failed_steps": failed_steps,
                "execution_time": (datetime.now() - workflow.last_run).total_seconds()
            }

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            self.logger.error(f"Workflow {workflow.name} failed: {e}")
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e)
            }

    async def _execute_step(self, step: WorkflowStep, context: Dict, previous_results: Dict) -> Dict:
        """Execute a single workflow step"""

        try:
            # Get the appropriate agent
            agent = self._get_agent(step.agent)
            if not agent:
                return {"success": False, "error": f"Agent {step.agent} not found"}

            # Prepare parameters with context and previous results
            parameters = step.parameters.copy()
            parameters.update(context)

            # Add results from dependent steps
            for dep_id in step.dependencies:
                if dep_id in previous_results:
                    parameters[f"{dep_id}_result"] = previous_results[dep_id]

            # Execute the action
            if hasattr(agent, step.action):
                action_method = getattr(agent, step.action)

                # Execute with timeout
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: action_method(**parameters)
                    ),
                    timeout=step.timeout_minutes * 60
                )

                return {"success": True, "result": result}
            else:
                return {"success": False, "error": f"Action {step.action} not found on agent {step.agent}"}

        except asyncio.TimeoutError:
            return {"success": False, "error": f"Step timed out after {step.timeout_minutes} minutes"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_agent(self, agent_name: str):
        """Get agent instance by name"""
        agents = {
            "content_engine": self.content_engine,
            "audience_automator": self.audience_automator,
            "lead_pipeline": self.lead_pipeline,
            "product_factory": self.product_factory,
            "analytics_dashboard": self.analytics_dashboard,
            "platform_manager": self.platform_manager
        }
        return agents.get(agent_name)

    def schedule_workflow(self, workflow_id: str, schedule_config: Dict) -> Dict:
        """Schedule a workflow for automatic execution"""

        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} not found"}

        workflow = self.workflows[workflow_id]

        # Parse schedule configuration
        if schedule_config.get("schedule") == "daily":
            time_str = schedule_config.get("time", "09:00")
            schedule.every().day.at(time_str).do(self._run_scheduled_workflow, workflow_id)

        elif schedule_config.get("schedule") == "weekly":
            day = schedule_config.get("day", "monday")
            time_str = schedule_config.get("time", "09:00")
            getattr(schedule.every(), day).at(time_str).do(self._run_scheduled_workflow, workflow_id)

        elif schedule_config.get("schedule") == "monthly":
            # Monthly scheduling (simplified - runs on 1st of month)
            schedule.every().day.at("09:00").do(self._check_monthly_schedule, workflow_id)

        # Update workflow config
        workflow.trigger_config = schedule_config
        workflow.next_run = self._calculate_next_run(schedule_config)

        return {
            "scheduled": True,
            "workflow_id": workflow_id,
            "next_run": workflow.next_run.isoformat() if workflow.next_run else None
        }

    def _run_scheduled_workflow(self, workflow_id: str):
        """Run a scheduled workflow"""
        asyncio.create_task(self.execute_workflow(workflow_id))

    def _check_monthly_schedule(self, workflow_id: str):
        """Check if monthly workflow should run"""
        if datetime.now().day == 1:
            self._run_scheduled_workflow(workflow_id)

    def _calculate_next_run(self, schedule_config: Dict) -> Optional[datetime]:
        """Calculate next run time based on schedule config"""
        # Simplified calculation
        if schedule_config.get("schedule") == "daily":
            return datetime.now() + timedelta(days=1)
        elif schedule_config.get("schedule") == "weekly":
            return datetime.now() + timedelta(weeks=1)
        elif schedule_config.get("schedule") == "monthly":
            return datetime.now() + timedelta(days=30)
        return None

    def start_scheduler(self):
        """Start the workflow scheduler"""
        self.scheduler_running = True

        def run_scheduler():
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        import threading
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

        self.logger.info("Workflow scheduler started")

    def stop_scheduler(self):
        """Stop the workflow scheduler"""
        self.scheduler_running = False
        self.logger.info("Workflow scheduler stopped")

    def create_custom_workflow(self, workflow_definition: Dict) -> Dict:
        """Create a custom workflow from definition"""

        try:
            # Validate workflow definition
            required_fields = ["id", "name", "description", "steps"]
            for field in required_fields:
                if field not in workflow_definition:
                    return {"error": f"Missing required field: {field}"}

            # Create workflow steps
            steps = []
            for step_def in workflow_definition["steps"]:
                step = WorkflowStep(
                    id=step_def["id"],
                    name=step_def["name"],
                    agent=step_def["agent"],
                    action=step_def["action"],
                    parameters=step_def.get("parameters", {}),
                    dependencies=step_def.get("dependencies", []),
                    timeout_minutes=step_def.get("timeout_minutes", 30),
                    retry_count=step_def.get("retry_count", 3),
                    error_handling=step_def.get("error_handling", "continue")
                )
                steps.append(step)

            # Create workflow
            workflow = Workflow(
                id=workflow_definition["id"],
                name=workflow_definition["name"],
                description=workflow_definition["description"],
                trigger_type=TriggerType(workflow_definition.get("trigger_type", "manual")),
                trigger_config=workflow_definition.get("trigger_config", {}),
                steps=steps,
                status=WorkflowStatus.PENDING,
                created_at=datetime.now()
            )

            # Register workflow
            self.workflows[workflow.id] = workflow

            return {
                "created": True,
                "workflow_id": workflow.id,
                "workflow": asdict(workflow)
            }

        except Exception as e:
            return {"error": f"Failed to create workflow: {e}"}

    def get_workflow_status(self, workflow_id: str = None) -> Dict:
        """Get status of workflows"""

        if workflow_id:
            if workflow_id not in self.workflows:
                return {"error": f"Workflow {workflow_id} not found"}

            workflow = self.workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "last_run": workflow.last_run.isoformat() if workflow.last_run else None,
                "next_run": workflow.next_run.isoformat() if workflow.next_run else None,
                "execution_count": workflow.execution_count,
                "success_count": workflow.success_count,
                "success_rate": (workflow.success_count / workflow.execution_count * 100) if workflow.execution_count > 0 else 0
            }
        else:
            # Return status of all workflows
            return {
                "workflows": [
                    {
                        "id": wf.id,
                        "name": wf.name,
                        "status": wf.status.value,
                        "last_run": wf.last_run.isoformat() if wf.last_run else None,
                        "next_run": wf.next_run.isoformat() if wf.next_run else None,
                        "execution_count": wf.execution_count,
                        "success_rate": (wf.success_count / wf.execution_count * 100) if wf.execution_count > 0 else 0
                    }
                    for wf in self.workflows.values()
                ]
            }

    def trigger_event_workflow(self, event_type: str, event_data: Dict) -> List[Dict]:
        """Trigger workflows based on events"""

        triggered_workflows = []

        for workflow in self.workflows.values():
            if (workflow.trigger_type == TriggerType.EVENT_BASED and
                workflow.trigger_config.get("event") == event_type):

                # Execute workflow with event data as context
                task = asyncio.create_task(self.execute_workflow(workflow.id, event_data))
                triggered_workflows.append({
                    "workflow_id": workflow.id,
                    "workflow_name": workflow.name,
                    "triggered": True
                })

        return triggered_workflows

    def pause_workflow(self, workflow_id: str) -> Dict:
        """Pause a workflow"""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} not found"}

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.PAUSED

        return {"paused": True, "workflow_id": workflow_id}

    def resume_workflow(self, workflow_id: str) -> Dict:
        """Resume a paused workflow"""
        if workflow_id not in self.workflows:
            return {"error": f"Workflow {workflow_id} not found"}

        workflow = self.workflows[workflow_id]
        if workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.PENDING
            return {"resumed": True, "workflow_id": workflow_id}
        else:
            return {"error": f"Workflow {workflow_id} is not paused"}

    def get_workflow_analytics(self) -> Dict:
        """Get analytics for all workflows"""

        total_workflows = len(self.workflows)
        total_executions = sum(wf.execution_count for wf in self.workflows.values())
        total_successes = sum(wf.success_count for wf in self.workflows.values())
        overall_success_rate = (total_successes / total_executions * 100) if total_executions > 0 else 0

        # Workflow performance
        workflow_performance = []
        for workflow in self.workflows.values():
            if workflow.execution_count > 0:
                workflow_performance.append({
                    "id": workflow.id,
                    "name": workflow.name,
                    "execution_count": workflow.execution_count,
                    "success_rate": (workflow.success_count / workflow.execution_count * 100),
                    "avg_execution_time": "N/A"  # Would need to track execution times
                })

        # Sort by success rate
        workflow_performance.sort(key=lambda x: x["success_rate"], reverse=True)

        return {
            "total_workflows": total_workflows,
            "total_executions": total_executions,
            "overall_success_rate": round(overall_success_rate, 2),
            "top_performing_workflows": workflow_performance[:5],
            "workflow_status_distribution": {
                status.value: sum(1 for wf in self.workflows.values() if wf.status == status)
                for status in WorkflowStatus
            }
        }


# Example usage and workflow definitions
if __name__ == "__main__":
    config = {
        'openai_api_key': 'your-openai-key',
        'linkedin_access_token': 'your-linkedin-token',
        'convertkit_api_key': 'your-convertkit-key',
        'stripe_api_key': 'your-stripe-key',
        'database_path': 'automation.db'
    }

    # Initialize orchestrator
    orchestrator = AutomationOrchestrator(config)

    # Start scheduler
    orchestrator.start_scheduler()

    # Example: Trigger a workflow manually
    async def run_example():
        result = await orchestrator.execute_workflow("daily_content_automation")
        print("Workflow result:", json.dumps(result, indent=2, default=str))

    # Example: Create custom workflow
    custom_workflow = {
        "id": "newsletter_automation",
        "name": "Weekly Newsletter Automation",
        "description": "Automatically create and send weekly newsletter",
        "trigger_type": "time_based",
        "trigger_config": {"schedule": "weekly", "day": "thursday", "time": "10:00"},
        "steps": [
            {
                "id": "gather_content",
                "name": "Gather Weekly Content",
                "agent": "content_engine",
                "action": "gather_weekly_highlights",
                "parameters": {"sources": ["linkedin_posts", "blog_articles"]},
                "dependencies": []
            },
            {
                "id": "create_newsletter",
                "name": "Create Newsletter",
                "agent": "content_engine",
                "action": "create_newsletter_content",
                "parameters": {"template": "weekly_roundup"},
                "dependencies": ["gather_content"]
            },
            {
                "id": "send_newsletter",
                "name": "Send Newsletter",
                "agent": "platform_manager",
                "action": "send_newsletter",
                "parameters": {"platform": "substack"},
                "dependencies": ["create_newsletter"]
            }
        ]
    }

    creation_result = orchestrator.create_custom_workflow(custom_workflow)
    print("Custom workflow created:", creation_result)

    # Get workflow status
    status = orchestrator.get_workflow_status()
    print("Workflow status:", json.dumps(status, indent=2, default=str))

    # Run the async example
    # asyncio.run(run_example())