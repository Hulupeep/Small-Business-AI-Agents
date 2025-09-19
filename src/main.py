"""
Main application entry point for Automation Agents.

This module provides:
- Agent orchestration and coordination
- REST API endpoints for external integration
- Scheduled monitoring and automation tasks
- Business metrics dashboard
- Configuration management interface
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import schedule
import time
import threading

from config.config import setup_config, get_config
from src.agents.inventory_tracker import InventoryTrackerAgent
from src.agents.meeting_scheduler import MeetingSchedulerAgent
from src.database.models import DatabaseManager

# Setup logging and configuration
config = setup_config()
logger = logging.getLogger(__name__)

# Global agent instances
inventory_agent: Optional[InventoryTrackerAgent] = None
meeting_agent: Optional[MeetingSchedulerAgent] = None
scheduler_thread: Optional[threading.Thread] = None
shutdown_event = threading.Event()

# FastAPI models
class SchedulingRequest(BaseModel):
    """Request model for meeting scheduling"""
    request_text: str
    requester_email: str

class InventoryAlert(BaseModel):
    """Response model for inventory alerts"""
    product_id: int
    sku: str
    product_name: str
    location_name: str
    current_quantity: int
    reorder_point: int
    urgency_level: str
    recommended_order_qty: int

class BusinessMetrics(BaseModel):
    """Response model for business metrics"""
    inventory_metrics: Dict[str, Any]
    scheduling_metrics: Dict[str, Any]
    combined_savings: float
    roi_percentage: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    # Startup
    await startup()
    yield
    # Shutdown
    await shutdown()

# FastAPI app
app = FastAPI(
    title="Automation Agents",
    description="Operational automation agents for inventory tracking and meeting scheduling",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def startup():
    """Application startup tasks"""
    global inventory_agent, meeting_agent, scheduler_thread

    logger.info("Starting Automation Agents application")

    try:
        # Initialize database
        db_manager = DatabaseManager(config.database.url)
        db_manager.create_tables()
        logger.info("Database initialized")

        # Initialize agents
        inventory_config = config.get_inventory_config()
        meeting_config = config.get_meeting_scheduler_config()

        inventory_agent = InventoryTrackerAgent(inventory_config)
        meeting_agent = MeetingSchedulerAgent(meeting_config)

        logger.info("Automation agents initialized")

        # Setup scheduled tasks
        setup_scheduled_tasks()

        # Start scheduler thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

        logger.info("Scheduled tasks started")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

async def shutdown():
    """Application shutdown tasks"""
    global scheduler_thread

    logger.info("Shutting down Automation Agents application")

    # Signal scheduler to stop
    shutdown_event.set()

    # Wait for scheduler thread to finish
    if scheduler_thread and scheduler_thread.is_alive():
        scheduler_thread.join(timeout=5)

    logger.info("Application shutdown complete")

def setup_scheduled_tasks():
    """Setup automated monitoring and task schedules"""

    # Inventory monitoring every hour
    schedule.every(config.inventory.monitoring_interval_minutes).minutes.do(
        run_inventory_monitoring
    )

    # Daily business metrics calculation
    schedule.every().day.at("08:00").do(calculate_daily_metrics)

    # Weekly optimization analysis
    schedule.every().monday.at("09:00").do(run_weekly_optimization)

    # Monthly reporting
    schedule.every().month.do(generate_monthly_report)

    logger.info("Scheduled tasks configured")

def run_scheduler():
    """Run the scheduler in a separate thread"""
    while not shutdown_event.is_set():
        schedule.run_pending()
        time.sleep(60)  # Check every minute

def run_inventory_monitoring():
    """Scheduled inventory monitoring task"""
    try:
        if inventory_agent:
            logger.info("Running scheduled inventory monitoring")
            results = inventory_agent.run_monitoring_cycle()
            logger.info(f"Inventory monitoring completed: {results}")
    except Exception as e:
        logger.error(f"Scheduled inventory monitoring failed: {e}")

def calculate_daily_metrics():
    """Calculate daily business metrics"""
    try:
        logger.info("Calculating daily business metrics")

        if inventory_agent:
            inventory_impact = inventory_agent.calculate_business_impact()
            logger.info(f"Inventory impact: {inventory_impact}")

        if meeting_agent:
            scheduling_impact = meeting_agent.calculate_business_impact()
            logger.info(f"Scheduling impact: {scheduling_impact}")

    except Exception as e:
        logger.error(f"Daily metrics calculation failed: {e}")

def run_weekly_optimization():
    """Run weekly optimization analysis"""
    try:
        logger.info("Running weekly optimization analysis")

        if inventory_agent:
            optimization = inventory_agent.optimize_inventory_levels()
            logger.info(f"Inventory optimization: {optimization}")

        if meeting_agent:
            scheduling_optimization = meeting_agent.run_scheduling_optimization()
            logger.info(f"Scheduling optimization: {scheduling_optimization}")

    except Exception as e:
        logger.error(f"Weekly optimization failed: {e}")

def generate_monthly_report():
    """Generate monthly business impact report"""
    try:
        logger.info("Generating monthly business impact report")
        # This would generate comprehensive monthly reports
        # Implementation would include PDF generation, email distribution, etc.
    except Exception as e:
        logger.error(f"Monthly report generation failed: {e}")

# Dependency injection
def get_inventory_agent() -> InventoryTrackerAgent:
    """Get inventory agent dependency"""
    if inventory_agent is None:
        raise HTTPException(status_code=503, detail="Inventory agent not initialized")
    return inventory_agent

def get_meeting_agent() -> MeetingSchedulerAgent:
    """Get meeting agent dependency"""
    if meeting_agent is None:
        raise HTTPException(status_code=503, detail="Meeting agent not initialized")
    return meeting_agent

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Automation Agents",
        "version": "1.0.0",
        "status": "active",
        "agents": {
            "inventory_tracker": inventory_agent is not None,
            "meeting_scheduler": meeting_agent is not None
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents": {
            "inventory_tracker": inventory_agent is not None,
            "meeting_scheduler": meeting_agent is not None
        }
    }

# Inventory Tracker Endpoints

@app.get("/inventory/alerts", response_model=list[InventoryAlert])
async def get_inventory_alerts(agent: InventoryTrackerAgent = Depends(get_inventory_agent)):
    """Get current inventory alerts"""
    try:
        alerts = agent.monitor_inventory_levels()
        return [
            InventoryAlert(
                product_id=alert.product_id,
                sku=alert.sku,
                product_name=alert.product_name,
                location_name=alert.location_name,
                current_quantity=alert.current_quantity,
                reorder_point=alert.reorder_point,
                urgency_level=alert.urgency_level,
                recommended_order_qty=alert.recommended_order_qty
            )
            for alert in alerts
        ]
    except Exception as e:
        logger.error(f"Error getting inventory alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inventory/generate-pos")
async def generate_purchase_orders(
    background_tasks: BackgroundTasks,
    agent: InventoryTrackerAgent = Depends(get_inventory_agent)
):
    """Generate purchase orders for critical inventory items"""
    try:
        # Run in background to avoid blocking
        background_tasks.add_task(run_po_generation, agent)
        return {"message": "Purchase order generation started", "status": "processing"}
    except Exception as e:
        logger.error(f"Error starting PO generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_po_generation(agent: InventoryTrackerAgent):
    """Background task for PO generation"""
    try:
        alerts = agent.monitor_inventory_levels()
        po_ids = agent.generate_purchase_orders(alerts)
        logger.info(f"Generated {len(po_ids)} purchase orders")
    except Exception as e:
        logger.error(f"Background PO generation failed: {e}")

@app.get("/inventory/forecast/{product_id}")
async def get_demand_forecast(
    product_id: int,
    location_id: Optional[int] = None,
    days: int = 30,
    agent: InventoryTrackerAgent = Depends(get_inventory_agent)
):
    """Get demand forecast for specific product"""
    try:
        forecast = agent.forecast_demand(product_id, location_id, days)
        return {
            "product_id": forecast.product_id,
            "location_id": forecast.location_id,
            "forecast_days": forecast.forecast_period_days,
            "predicted_demand": forecast.predicted_demand,
            "confidence_interval": forecast.confidence_interval,
            "seasonality_factor": forecast.seasonality_factor,
            "trend_factor": forecast.trend_factor
        }
    except Exception as e:
        logger.error(f"Error getting demand forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inventory/optimization")
async def get_inventory_optimization(agent: InventoryTrackerAgent = Depends(get_inventory_agent)):
    """Get inventory optimization recommendations"""
    try:
        optimization = agent.optimize_inventory_levels()
        return optimization
    except Exception as e:
        logger.error(f"Error getting inventory optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inventory/metrics")
async def get_inventory_metrics(agent: InventoryTrackerAgent = Depends(get_inventory_agent)):
    """Get inventory business impact metrics"""
    try:
        metrics = agent.calculate_business_impact()
        return metrics
    except Exception as e:
        logger.error(f"Error getting inventory metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Meeting Scheduler Endpoints

@app.post("/meetings/schedule")
async def schedule_meeting(
    request: SchedulingRequest,
    agent: MeetingSchedulerAgent = Depends(get_meeting_agent)
):
    """Process natural language scheduling request"""
    try:
        result = agent.process_natural_language_request(
            request.request_text, request.requester_email
        )
        return result
    except Exception as e:
        logger.error(f"Error processing scheduling request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meetings/confirm/{request_id}")
async def confirm_meeting(
    request_id: int,
    time_index: int = 0,
    agent: MeetingSchedulerAgent = Depends(get_meeting_agent)
):
    """Confirm and schedule meeting from suggestions"""
    try:
        result = agent.schedule_meeting(request_id, time_index)
        return result
    except Exception as e:
        logger.error(f"Error confirming meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/conflicts/{meeting_id}")
async def resolve_conflicts(
    meeting_id: int,
    agent: MeetingSchedulerAgent = Depends(get_meeting_agent)
):
    """Resolve scheduling conflicts for existing meeting"""
    try:
        result = agent.resolve_scheduling_conflicts(meeting_id)
        return result
    except Exception as e:
        logger.error(f"Error resolving conflicts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meetings/find-time")
async def find_optimal_time(
    attendees: list[str],
    duration_minutes: int,
    start_date: str,
    end_date: str,
    timezone: str = "UTC",
    agent: MeetingSchedulerAgent = Depends(get_meeting_agent)
):
    """Find optimal meeting time for attendees"""
    try:
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        suggestions = agent.find_optimal_meeting_time(
            attendees, duration_minutes, (start_dt, end_dt), timezone
        )

        return [
            {
                "suggested_time": s.suggested_time.isoformat(),
                "end_time": s.end_time.isoformat(),
                "confidence_score": s.confidence_score,
                "all_attendees_available": s.all_attendees_available,
                "reasoning": s.reasoning
            }
            for s in suggestions
        ]
    except Exception as e:
        logger.error(f"Error finding optimal time: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/metrics")
async def get_meeting_metrics(agent: MeetingSchedulerAgent = Depends(get_meeting_agent)):
    """Get meeting scheduler business impact metrics"""
    try:
        metrics = agent.calculate_business_impact()
        return metrics
    except Exception as e:
        logger.error(f"Error getting meeting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/meetings/timezone-convert")
async def convert_timezone(
    time_str: str,
    from_timezone: str,
    to_timezone: str,
    agent: MeetingSchedulerAgent = Depends(get_meeting_agent)
):
    """Convert time between timezones"""
    try:
        result = agent.handle_timezone_conversion(time_str, from_timezone, to_timezone)
        return result
    except Exception as e:
        logger.error(f"Error converting timezone: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Combined Metrics and Reporting

@app.get("/metrics/business-impact", response_model=BusinessMetrics)
async def get_business_impact(
    inventory_agent: InventoryTrackerAgent = Depends(get_inventory_agent),
    meeting_agent: MeetingSchedulerAgent = Depends(get_meeting_agent)
):
    """Get combined business impact metrics"""
    try:
        inventory_metrics = inventory_agent.calculate_business_impact()
        scheduling_metrics = meeting_agent.calculate_business_impact()

        # Calculate combined metrics
        combined_monthly_savings = (
            inventory_metrics.get('monthly_cost_savings', 0) +
            scheduling_metrics.get('monthly_cost_savings', 0)
        )

        combined_annual_savings = combined_monthly_savings * 12
        implementation_cost = 75000  # Estimated total implementation cost
        combined_roi = (combined_annual_savings / implementation_cost) * 100

        return BusinessMetrics(
            inventory_metrics=inventory_metrics,
            scheduling_metrics=scheduling_metrics,
            combined_savings=combined_monthly_savings,
            roi_percentage=combined_roi
        )
    except Exception as e:
        logger.error(f"Error getting business impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/dashboard")
async def get_dashboard_metrics(
    inventory_agent: InventoryTrackerAgent = Depends(get_inventory_agent),
    meeting_agent: MeetingSchedulerAgent = Depends(get_meeting_agent)
):
    """Get comprehensive dashboard metrics"""
    try:
        # Get current alerts and status
        inventory_alerts = inventory_agent.monitor_inventory_levels()
        critical_alerts = [a for a in inventory_alerts if a.urgency_level == 'critical']

        # Get business metrics
        inventory_impact = inventory_agent.calculate_business_impact()
        scheduling_impact = meeting_agent.calculate_business_impact()

        dashboard_data = {
            "overview": {
                "total_alerts": len(inventory_alerts),
                "critical_alerts": len(critical_alerts),
                "monthly_savings": inventory_impact.get('monthly_cost_savings', 0) +
                                 scheduling_impact.get('monthly_cost_savings', 0),
                "automation_rate": 92.5,  # Percentage of tasks automated
                "last_updated": datetime.utcnow().isoformat()
            },
            "inventory": {
                "alerts_by_urgency": {
                    "critical": len([a for a in inventory_alerts if a.urgency_level == 'critical']),
                    "high": len([a for a in inventory_alerts if a.urgency_level == 'high']),
                    "medium": len([a for a in inventory_alerts if a.urgency_level == 'medium']),
                    "low": len([a for a in inventory_alerts if a.urgency_level == 'low'])
                },
                "monthly_metrics": inventory_impact,
                "optimization_opportunities": inventory_agent.optimize_inventory_levels()
            },
            "scheduling": {
                "monthly_metrics": scheduling_impact,
                "optimization_status": meeting_agent.run_scheduling_optimization()
            }
        }

        return dashboard_data

    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration Management

@app.get("/config")
async def get_configuration():
    """Get current configuration (sensitive data masked)"""
    try:
        # Return non-sensitive configuration data
        return {
            "inventory": {
                "monitoring_interval_minutes": config.inventory.monitoring_interval_minutes,
                "auto_generate_pos": config.inventory.auto_generate_pos,
                "default_forecast_days": config.inventory.default_forecast_days
            },
            "meeting_scheduler": {
                "default_meeting_duration_minutes": config.meeting_scheduler.default_meeting_duration_minutes,
                "business_hours_start": config.meeting_scheduler.business_hours_start,
                "business_hours_end": config.meeting_scheduler.business_hours_end,
                "max_alternative_suggestions": config.meeting_scheduler.max_alternative_suggestions
            },
            "notifications": {
                "email_enabled": config.notifications.email_enabled,
                "slack_enabled": config.notifications.slack_enabled,
                "sms_enabled": config.notifications.sms_enabled
            }
        }
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "InternalServerError"}
    )

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    shutdown_event.set()
    sys.exit(0)

if __name__ == "__main__":
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )