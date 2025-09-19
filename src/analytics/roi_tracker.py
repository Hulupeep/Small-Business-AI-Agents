"""
ROI Tracker - Comprehensive analytics and ROI tracking for marketing automation
Tracks time savings, revenue improvements, and overall marketing ROI
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json
import statistics
from enum import Enum

class MetricType(Enum):
    TIME_SAVED = "time_saved"
    REVENUE_GENERATED = "revenue_generated"
    ENGAGEMENT_IMPROVEMENT = "engagement_improvement"
    COST_REDUCTION = "cost_reduction"
    CONVERSION_IMPROVEMENT = "conversion_improvement"

@dataclass
class ROIMetric:
    """Individual ROI metric measurement"""
    metric_type: MetricType
    value: float
    currency: str = "USD"
    timestamp: datetime = None
    agent_source: str = "unknown"  # social_media_manager, email_campaign_writer
    platform: str = "unknown"
    campaign_id: Optional[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ROISummary:
    """Summary of ROI metrics over a period"""
    period_start: datetime
    period_end: datetime
    total_time_saved_hours: float
    total_revenue_generated: float
    total_cost_savings: float
    engagement_improvement_percent: float
    conversion_improvement_percent: float
    total_roi_value: float
    monthly_projection: float
    annual_projection: float

class ROITracker:
    """
    Comprehensive ROI tracking for marketing automation agents

    Tracks and calculates:
    - Time savings (hours saved * hourly rate)
    - Revenue improvements (direct attribution to AI optimization)
    - Cost reductions (reduced need for manual work)
    - Engagement improvements (better metrics vs. baseline)
    - Overall ROI and projections
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()

        # Metrics storage
        self.metrics: List[ROIMetric] = []

        # Configuration for calculations
        self.hourly_rates = config.get('hourly_rates', {
            'social_media_manager': 50,  # $50/hour for social media management
            'email_marketing': 75,       # $75/hour for email marketing
            'content_creation': 60,      # $60/hour for content creation
            'analytics': 65              # $65/hour for analytics work
        })

        # Industry baselines for comparison
        self.industry_baselines = config.get('baselines', {
            'email_open_rate': 21.3,     # Industry average email open rate
            'email_ctr': 2.6,            # Industry average email CTR
            'social_engagement_rate': 1.9, # Industry average social engagement
            'conversion_rate': 2.35,      # Industry average conversion rate
            'cost_per_lead': 50          # Industry average cost per lead
        })

        # Business metrics
        self.business_metrics = config.get('business_metrics', {
            'average_order_value': 150,
            'customer_lifetime_value': 750,
            'monthly_marketing_spend': 5000
        })

        self.logger.info("ROI Tracker initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for ROI tracker"""
        logger = logging.getLogger('ROITracker')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def track_time_saved(self,
                        hours_saved: float,
                        agent_source: str,
                        activity_description: str = "",
                        platform: str = "general") -> ROIMetric:
        """
        Track time saved by automation

        Args:
            hours_saved: Number of hours saved
            agent_source: Which agent saved the time
            activity_description: Description of the activity
            platform: Platform where time was saved

        Returns:
            ROIMetric object
        """
        try:
            hourly_rate = self.hourly_rates.get(agent_source, 50)
            value_saved = hours_saved * hourly_rate

            metric = ROIMetric(
                metric_type=MetricType.TIME_SAVED,
                value=value_saved,
                agent_source=agent_source,
                platform=platform,
                notes=f"Saved {hours_saved} hours on {activity_description}"
            )

            self.metrics.append(metric)

            self.logger.info(f"Tracked time savings: {hours_saved} hours = ${value_saved:.2f} ({agent_source})")
            return metric

        except Exception as e:
            self.logger.error(f"Error tracking time saved: {str(e)}")
            raise

    def track_revenue_generated(self,
                              revenue: float,
                              agent_source: str,
                              campaign_id: str = None,
                              platform: str = "general",
                              attribution_method: str = "direct") -> ROIMetric:
        """
        Track revenue generated through automation improvements

        Args:
            revenue: Revenue amount generated
            agent_source: Which agent generated the revenue
            campaign_id: Associated campaign ID
            platform: Platform where revenue was generated
            attribution_method: How revenue is attributed (direct, improved_conversion, etc.)

        Returns:
            ROIMetric object
        """
        try:
            metric = ROIMetric(
                metric_type=MetricType.REVENUE_GENERATED,
                value=revenue,
                agent_source=agent_source,
                platform=platform,
                campaign_id=campaign_id,
                notes=f"Revenue via {attribution_method} attribution"
            )

            self.metrics.append(metric)

            self.logger.info(f"Tracked revenue generation: ${revenue:.2f} ({agent_source}, {platform})")
            return metric

        except Exception as e:
            self.logger.error(f"Error tracking revenue: {str(e)}")
            raise

    def track_engagement_improvement(self,
                                   current_rate: float,
                                   baseline_rate: float,
                                   metric_name: str,
                                   agent_source: str,
                                   platform: str = "general",
                                   campaign_id: str = None) -> ROIMetric:
        """
        Track engagement improvements over baseline

        Args:
            current_rate: Current engagement rate
            baseline_rate: Baseline or previous rate
            metric_name: Name of the metric (open_rate, ctr, etc.)
            agent_source: Which agent achieved the improvement
            platform: Platform where improvement occurred
            campaign_id: Associated campaign ID

        Returns:
            ROIMetric object
        """
        try:
            if baseline_rate <= 0:
                improvement_percent = 0
            else:
                improvement_percent = ((current_rate - baseline_rate) / baseline_rate) * 100

            # Convert improvement to monetary value based on impact
            monetary_value = self._calculate_engagement_value(
                improvement_percent, metric_name, platform
            )

            metric = ROIMetric(
                metric_type=MetricType.ENGAGEMENT_IMPROVEMENT,
                value=monetary_value,
                agent_source=agent_source,
                platform=platform,
                campaign_id=campaign_id,
                notes=f"{metric_name} improved {improvement_percent:.2f}% ({current_rate:.2f}% vs {baseline_rate:.2f}%)"
            )

            self.metrics.append(metric)

            self.logger.info(f"Tracked engagement improvement: {metric_name} +{improvement_percent:.2f}% = ${monetary_value:.2f}")
            return metric

        except Exception as e:
            self.logger.error(f"Error tracking engagement improvement: {str(e)}")
            raise

    def track_cost_reduction(self,
                           cost_saved: float,
                           agent_source: str,
                           cost_category: str,
                           platform: str = "general") -> ROIMetric:
        """
        Track cost reductions achieved through automation

        Args:
            cost_saved: Amount of cost reduction
            agent_source: Which agent achieved the savings
            cost_category: Category of cost saved (tools, labor, etc.)
            platform: Platform where cost was saved

        Returns:
            ROIMetric object
        """
        try:
            metric = ROIMetric(
                metric_type=MetricType.COST_REDUCTION,
                value=cost_saved,
                agent_source=agent_source,
                platform=platform,
                notes=f"Cost reduction in {cost_category}"
            )

            self.metrics.append(metric)

            self.logger.info(f"Tracked cost reduction: ${cost_saved:.2f} in {cost_category} ({agent_source})")
            return metric

        except Exception as e:
            self.logger.error(f"Error tracking cost reduction: {str(e)}")
            raise

    def _calculate_engagement_value(self,
                                  improvement_percent: float,
                                  metric_name: str,
                                  platform: str) -> float:
        """
        Calculate monetary value of engagement improvements

        Args:
            improvement_percent: Percentage improvement
            metric_name: Name of the engagement metric
            platform: Platform where improvement occurred

        Returns:
            Estimated monetary value of the improvement
        """
        try:
            # Base monthly impressions/reach estimates by platform
            monthly_reach = {
                'email': 10000,      # 10k email subscribers
                'twitter': 25000,    # 25k monthly impressions
                'linkedin': 15000,   # 15k monthly impressions
                'instagram': 20000,  # 20k monthly impressions
                'facebook': 30000,   # 30k monthly impressions
                'general': 20000     # Average estimate
            }

            # Value per engagement by metric type
            engagement_values = {
                'open_rate': 0.01,        # $0.01 per additional open
                'click_through_rate': 0.15, # $0.15 per additional click
                'engagement_rate': 0.05,  # $0.05 per additional engagement
                'conversion_rate': 5.0,   # $5.00 per additional conversion
                'response_rate': 0.25     # $0.25 per additional response
            }

            platform_reach = monthly_reach.get(platform, monthly_reach['general'])
            engagement_value = engagement_values.get(metric_name, 0.05)

            # Calculate additional engagements from improvement
            baseline_engagements = platform_reach * 0.02  # Assume 2% baseline engagement
            additional_engagements = baseline_engagements * (improvement_percent / 100)

            monetary_value = additional_engagements * engagement_value

            return max(0, monetary_value)  # Ensure non-negative

        except Exception as e:
            self.logger.warning(f"Error calculating engagement value: {str(e)}")
            return 0.0

    def calculate_roi_summary(self,
                            period_days: int = 30,
                            end_date: Optional[datetime] = None) -> ROISummary:
        """
        Calculate comprehensive ROI summary for a period

        Args:
            period_days: Number of days to analyze
            end_date: End date for analysis (defaults to now)

        Returns:
            ROISummary object with comprehensive metrics
        """
        try:
            if end_date is None:
                end_date = datetime.now()

            start_date = end_date - timedelta(days=period_days)

            # Filter metrics for the period
            period_metrics = [
                m for m in self.metrics
                if start_date <= m.timestamp <= end_date
            ]

            if not period_metrics:
                return ROISummary(
                    period_start=start_date,
                    period_end=end_date,
                    total_time_saved_hours=0,
                    total_revenue_generated=0,
                    total_cost_savings=0,
                    engagement_improvement_percent=0,
                    conversion_improvement_percent=0,
                    total_roi_value=0,
                    monthly_projection=0,
                    annual_projection=0
                )

            # Calculate totals by metric type
            time_saved_metrics = [m for m in period_metrics if m.metric_type == MetricType.TIME_SAVED]
            revenue_metrics = [m for m in period_metrics if m.metric_type == MetricType.REVENUE_GENERATED]
            cost_reduction_metrics = [m for m in period_metrics if m.metric_type == MetricType.COST_REDUCTION]
            engagement_metrics = [m for m in period_metrics if m.metric_type == MetricType.ENGAGEMENT_IMPROVEMENT]
            conversion_metrics = [m for m in period_metrics if m.metric_type == MetricType.CONVERSION_IMPROVEMENT]

            # Calculate totals
            total_time_value = sum(m.value for m in time_saved_metrics)
            total_revenue = sum(m.value for m in revenue_metrics)
            total_cost_savings = sum(m.value for m in cost_reduction_metrics)
            total_engagement_value = sum(m.value for m in engagement_metrics)
            total_conversion_value = sum(m.value for m in conversion_metrics)

            # Calculate time saved in hours
            avg_hourly_rate = statistics.mean(self.hourly_rates.values())
            total_time_hours = total_time_value / avg_hourly_rate if avg_hourly_rate > 0 else 0

            # Calculate improvement percentages
            engagement_improvement = self._calculate_period_improvement(
                engagement_metrics, "engagement"
            )
            conversion_improvement = self._calculate_period_improvement(
                conversion_metrics, "conversion"
            )

            # Total ROI value
            total_roi_value = (
                total_time_value +
                total_revenue +
                total_cost_savings +
                total_engagement_value +
                total_conversion_value
            )

            # Project to monthly and annual
            days_in_period = period_days
            monthly_projection = (total_roi_value / days_in_period) * 30 if days_in_period > 0 else 0
            annual_projection = monthly_projection * 12

            summary = ROISummary(
                period_start=start_date,
                period_end=end_date,
                total_time_saved_hours=total_time_hours,
                total_revenue_generated=total_revenue,
                total_cost_savings=total_cost_savings,
                engagement_improvement_percent=engagement_improvement,
                conversion_improvement_percent=conversion_improvement,
                total_roi_value=total_roi_value,
                monthly_projection=monthly_projection,
                annual_projection=annual_projection
            )

            self.logger.info(f"ROI Summary calculated: ${total_roi_value:.2f} total value over {period_days} days")
            return summary

        except Exception as e:
            self.logger.error(f"Error calculating ROI summary: {str(e)}")
            raise

    def _calculate_period_improvement(self,
                                    metrics: List[ROIMetric],
                                    improvement_type: str) -> float:
        """Calculate average improvement percentage for a period"""
        if not metrics:
            return 0.0

        # Extract improvement percentages from metric notes
        improvements = []
        for metric in metrics:
            try:
                # Parse improvement from notes (format: "metric improved X%")
                if "improved" in metric.notes and "%" in metric.notes:
                    parts = metric.notes.split("improved")
                    if len(parts) > 1:
                        percentage_part = parts[1].split("%")[0].strip()
                        improvement = float(percentage_part)
                        improvements.append(improvement)
            except (ValueError, IndexError):
                continue

        return statistics.mean(improvements) if improvements else 0.0

    def get_agent_performance_comparison(self) -> Dict[str, Any]:
        """
        Compare performance between different agents

        Returns:
            Performance comparison data
        """
        try:
            agent_performance = {}

            # Group metrics by agent
            agents = set(m.agent_source for m in self.metrics)

            for agent in agents:
                agent_metrics = [m for m in self.metrics if m.agent_source == agent]

                if not agent_metrics:
                    continue

                # Calculate totals for this agent
                total_value = sum(m.value for m in agent_metrics)
                total_metrics = len(agent_metrics)

                # Calculate by metric type
                time_saved = sum(m.value for m in agent_metrics if m.metric_type == MetricType.TIME_SAVED)
                revenue_generated = sum(m.value for m in agent_metrics if m.metric_type == MetricType.REVENUE_GENERATED)
                cost_savings = sum(m.value for m in agent_metrics if m.metric_type == MetricType.COST_REDUCTION)

                # Recent performance (last 30 days)
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent_metrics = [m for m in agent_metrics if m.timestamp >= thirty_days_ago]
                recent_value = sum(m.value for m in recent_metrics)

                agent_performance[agent] = {
                    'total_roi_value': round(total_value, 2),
                    'total_metrics_count': total_metrics,
                    'time_savings_value': round(time_saved, 2),
                    'revenue_generated': round(revenue_generated, 2),
                    'cost_savings': round(cost_savings, 2),
                    'recent_30day_value': round(recent_value, 2),
                    'avg_value_per_metric': round(total_value / total_metrics, 2) if total_metrics > 0 else 0,
                    'platforms_used': list(set(m.platform for m in agent_metrics))
                }

            # Rank agents by total ROI value
            sorted_agents = sorted(
                agent_performance.items(),
                key=lambda x: x[1]['total_roi_value'],
                reverse=True
            )

            comparison = {
                'agent_rankings': sorted_agents,
                'top_performer': sorted_agents[0][0] if sorted_agents else None,
                'total_agents': len(agents),
                'summary': {
                    'total_combined_value': sum(data['total_roi_value'] for data in agent_performance.values()),
                    'avg_value_per_agent': statistics.mean([data['total_roi_value'] for data in agent_performance.values()]) if agent_performance else 0
                }
            }

            return comparison

        except Exception as e:
            self.logger.error(f"Error creating agent performance comparison: {str(e)}")
            raise

    def get_platform_performance_analysis(self) -> Dict[str, Any]:
        """
        Analyze performance across different platforms

        Returns:
            Platform performance analysis
        """
        try:
            platform_performance = {}

            # Group metrics by platform
            platforms = set(m.platform for m in self.metrics)

            for platform in platforms:
                platform_metrics = [m for m in self.metrics if m.platform == platform]

                if not platform_metrics:
                    continue

                # Calculate platform metrics
                total_value = sum(m.value for m in platform_metrics)
                metric_counts = len(platform_metrics)

                # Breakdown by metric type
                type_breakdown = {}
                for metric_type in MetricType:
                    type_metrics = [m for m in platform_metrics if m.metric_type == metric_type]
                    type_breakdown[metric_type.value] = {
                        'count': len(type_metrics),
                        'total_value': sum(m.value for m in type_metrics),
                        'avg_value': statistics.mean([m.value for m in type_metrics]) if type_metrics else 0
                    }

                # Recent trend (last 30 days vs previous 30 days)
                now = datetime.now()
                recent_period = now - timedelta(days=30)
                previous_period = now - timedelta(days=60)

                recent_metrics = [m for m in platform_metrics if m.timestamp >= recent_period]
                previous_metrics = [m for m in platform_metrics if previous_period <= m.timestamp < recent_period]

                recent_value = sum(m.value for m in recent_metrics)
                previous_value = sum(m.value for m in previous_metrics)

                trend = "stable"
                if previous_value > 0:
                    change_percent = ((recent_value - previous_value) / previous_value) * 100
                    if change_percent > 10:
                        trend = "improving"
                    elif change_percent < -10:
                        trend = "declining"

                platform_performance[platform] = {
                    'total_roi_value': round(total_value, 2),
                    'metric_count': metric_counts,
                    'avg_value_per_metric': round(total_value / metric_counts, 2) if metric_counts > 0 else 0,
                    'type_breakdown': type_breakdown,
                    'recent_trend': trend,
                    'recent_value': round(recent_value, 2),
                    'change_percent': round(((recent_value - previous_value) / previous_value) * 100, 2) if previous_value > 0 else 0,
                    'agents_active': list(set(m.agent_source for m in platform_metrics))
                }

            # Find top performing platform
            top_platform = max(
                platform_performance.keys(),
                key=lambda p: platform_performance[p]['total_roi_value']
            ) if platform_performance else None

            analysis = {
                'platform_performance': platform_performance,
                'top_performing_platform': top_platform,
                'total_platforms': len(platforms),
                'recommendations': self._generate_platform_recommendations(platform_performance)
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing platform performance: {str(e)}")
            raise

    def _generate_platform_recommendations(self, platform_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on platform performance"""
        recommendations = []

        if not platform_data:
            return ["No platform data available for recommendations"]

        # Find best and worst performing platforms
        sorted_platforms = sorted(
            platform_data.items(),
            key=lambda x: x[1]['total_roi_value'],
            reverse=True
        )

        if len(sorted_platforms) >= 2:
            best_platform = sorted_platforms[0]
            worst_platform = sorted_platforms[-1]

            recommendations.append(
                f"Focus more resources on {best_platform[0]} - highest ROI at ${best_platform[1]['total_roi_value']}"
            )

            if worst_platform[1]['total_roi_value'] < best_platform[1]['total_roi_value'] * 0.3:
                recommendations.append(
                    f"Consider optimizing or reducing investment in {worst_platform[0]} - underperforming"
                )

        # Trend-based recommendations
        for platform, data in platform_data.items():
            if data['recent_trend'] == 'improving':
                recommendations.append(f"Scale up {platform} activities - showing positive trend")
            elif data['recent_trend'] == 'declining':
                recommendations.append(f"Investigate {platform} performance decline")

        # Cross-platform opportunities
        email_platforms = [p for p in platform_data.keys() if 'email' in p.lower()]
        social_platforms = [p for p in platform_data.keys() if p in ['twitter', 'linkedin', 'instagram', 'facebook']]

        if email_platforms and social_platforms:
            recommendations.append("Consider integrated campaigns across email and social media for better ROI")

        return recommendations[:5]  # Limit to 5 recommendations

    def export_analytics_report(self, format: str = "json") -> Dict[str, Any]:
        """
        Export comprehensive analytics report

        Args:
            format: Export format (json, summary)

        Returns:
            Comprehensive analytics report
        """
        try:
            # Calculate various summaries
            summary_30_days = self.calculate_roi_summary(30)
            summary_90_days = self.calculate_roi_summary(90)
            agent_comparison = self.get_agent_performance_comparison()
            platform_analysis = self.get_platform_performance_analysis()

            # Key performance indicators
            kpis = {
                'total_roi_value_30_days': summary_30_days.total_roi_value,
                'monthly_projection': summary_30_days.monthly_projection,
                'annual_projection': summary_30_days.annual_projection,
                'time_saved_hours_30_days': summary_30_days.total_time_saved_hours,
                'revenue_generated_30_days': summary_30_days.total_revenue_generated,
                'engagement_improvement_30_days': summary_30_days.engagement_improvement_percent,
                'total_metrics_tracked': len(self.metrics),
                'active_agents': len(set(m.agent_source for m in self.metrics)),
                'active_platforms': len(set(m.platform for m in self.metrics))
            }

            # ROI breakdown by category
            roi_breakdown = {}
            for metric_type in MetricType:
                type_metrics = [m for m in self.metrics if m.metric_type == metric_type]
                roi_breakdown[metric_type.value] = {
                    'count': len(type_metrics),
                    'total_value': sum(m.value for m in type_metrics),
                    'percentage_of_total': (sum(m.value for m in type_metrics) / sum(m.value for m in self.metrics)) * 100 if self.metrics else 0
                }

            # Time series data (weekly performance)
            weekly_performance = self._calculate_weekly_performance()

            report = {
                'report_generated': datetime.now().isoformat(),
                'reporting_period': {
                    'start_date': (datetime.now() - timedelta(days=90)).isoformat(),
                    'end_date': datetime.now().isoformat()
                },
                'key_performance_indicators': kpis,
                'roi_summary_30_days': asdict(summary_30_days),
                'roi_summary_90_days': asdict(summary_90_days),
                'roi_breakdown_by_category': roi_breakdown,
                'agent_performance_comparison': agent_comparison,
                'platform_performance_analysis': platform_analysis,
                'weekly_performance_trend': weekly_performance,
                'business_impact': {
                    'estimated_fte_saved': summary_30_days.total_time_saved_hours / 160,  # 160 hours per month FTE
                    'marketing_efficiency_improvement': (summary_30_days.total_roi_value / self.business_metrics.get('monthly_marketing_spend', 5000)) * 100,
                    'cost_per_lead_reduction': self._calculate_cost_per_lead_improvement(),
                    'customer_acquisition_improvement': self._calculate_customer_acquisition_improvement()
                },
                'recommendations': self._generate_comprehensive_recommendations(
                    summary_30_days, agent_comparison, platform_analysis
                )
            }

            if format == "summary":
                # Return condensed version for quick review
                return {
                    'total_roi_value': kpis['total_roi_value_30_days'],
                    'monthly_projection': kpis['monthly_projection'],
                    'time_saved_hours': kpis['time_saved_hours_30_days'],
                    'top_agent': agent_comparison.get('top_performer'),
                    'top_platform': platform_analysis.get('top_performing_platform'),
                    'key_recommendations': report['recommendations'][:3]
                }

            return report

        except Exception as e:
            self.logger.error(f"Error exporting analytics report: {str(e)}")
            raise

    def _calculate_weekly_performance(self) -> List[Dict[str, Any]]:
        """Calculate weekly performance over the last 12 weeks"""
        weekly_data = []

        for week_offset in range(12, 0, -1):
            week_start = datetime.now() - timedelta(weeks=week_offset)
            week_end = week_start + timedelta(days=7)

            week_metrics = [
                m for m in self.metrics
                if week_start <= m.timestamp < week_end
            ]

            weekly_value = sum(m.value for m in week_metrics)
            weekly_count = len(week_metrics)

            weekly_data.append({
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'total_value': round(weekly_value, 2),
                'metric_count': weekly_count,
                'avg_value_per_metric': round(weekly_value / weekly_count, 2) if weekly_count > 0 else 0
            })

        return weekly_data

    def _calculate_cost_per_lead_improvement(self) -> float:
        """Calculate improvement in cost per lead"""
        try:
            # Get recent conversion improvements
            recent_conversion_metrics = [
                m for m in self.metrics
                if m.metric_type == MetricType.CONVERSION_IMPROVEMENT
                and m.timestamp >= datetime.now() - timedelta(days=30)
            ]

            if not recent_conversion_metrics:
                return 0.0

            # Calculate average conversion improvement
            avg_improvement = statistics.mean([
                float(m.notes.split("improved")[1].split("%")[0].strip())
                for m in recent_conversion_metrics
                if "improved" in m.notes and "%" in m.notes
            ])

            # Estimate cost per lead improvement
            baseline_cost_per_lead = self.industry_baselines.get('cost_per_lead', 50)
            improved_cost_per_lead = baseline_cost_per_lead * (1 - avg_improvement / 100)

            improvement_percent = ((baseline_cost_per_lead - improved_cost_per_lead) / baseline_cost_per_lead) * 100

            return round(improvement_percent, 2)

        except Exception:
            return 0.0

    def _calculate_customer_acquisition_improvement(self) -> float:
        """Calculate improvement in customer acquisition efficiency"""
        try:
            # Calculate based on engagement and conversion improvements
            engagement_metrics = [
                m for m in self.metrics
                if m.metric_type == MetricType.ENGAGEMENT_IMPROVEMENT
                and m.timestamp >= datetime.now() - timedelta(days=30)
            ]

            if not engagement_metrics:
                return 0.0

            # Estimate that engagement improvements lead to acquisition improvements
            total_engagement_value = sum(m.value for m in engagement_metrics)
            monthly_marketing_spend = self.business_metrics.get('monthly_marketing_spend', 5000)

            acquisition_efficiency_improvement = (total_engagement_value / monthly_marketing_spend) * 100

            return round(min(acquisition_efficiency_improvement, 50), 2)  # Cap at 50%

        except Exception:
            return 0.0

    def _generate_comprehensive_recommendations(self,
                                             roi_summary: ROISummary,
                                             agent_comparison: Dict[str, Any],
                                             platform_analysis: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations based on all analytics"""
        recommendations = []

        # ROI-based recommendations
        if roi_summary.total_roi_value > 10000:
            recommendations.append("Excellent ROI performance - consider scaling successful automation strategies")
        elif roi_summary.total_roi_value < 1000:
            recommendations.append("ROI below target - review automation configurations and optimization opportunities")

        # Growth recommendations
        if roi_summary.monthly_projection > roi_summary.total_roi_value:
            recommendations.append("Strong growth trajectory - maintain current strategy and monitor scaling opportunities")

        # Agent-specific recommendations
        top_agent = agent_comparison.get('top_performer')
        if top_agent:
            recommendations.append(f"Leverage {top_agent} strategies across other agents for improved performance")

        # Platform recommendations
        top_platform = platform_analysis.get('top_performing_platform')
        if top_platform:
            recommendations.append(f"Expand investment in {top_platform} - showing strongest ROI")

        # Efficiency recommendations
        if roi_summary.total_time_saved_hours > 40:  # More than 1 FTE
            recommendations.append("Consider reallocating saved time to strategic growth initiatives")

        # Revenue recommendations
        if roi_summary.total_revenue_generated > 5000:
            recommendations.append("Strong revenue generation - document and replicate successful campaign strategies")

        return recommendations[:8]  # Limit to 8 recommendations

# Example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'hourly_rates': {
            'social_media_manager': 50,
            'email_campaign_writer': 75,
            'content_creation': 60,
            'analytics': 65
        },
        'baselines': {
            'email_open_rate': 21.3,
            'email_ctr': 2.6,
            'social_engagement_rate': 1.9,
            'conversion_rate': 2.35,
            'cost_per_lead': 50
        },
        'business_metrics': {
            'average_order_value': 150,
            'customer_lifetime_value': 750,
            'monthly_marketing_spend': 5000
        }
    }

    # Initialize tracker
    tracker = ROITracker(config)

    # Example tracking
    tracker.track_time_saved(
        hours_saved=8.5,
        agent_source="social_media_manager",
        activity_description="automated post creation and scheduling",
        platform="twitter"
    )

    tracker.track_revenue_generated(
        revenue=2500.0,
        agent_source="email_campaign_writer",
        campaign_id="camp_001",
        platform="email",
        attribution_method="improved_conversion_rate"
    )

    tracker.track_engagement_improvement(
        current_rate=28.5,
        baseline_rate=21.3,
        metric_name="open_rate",
        agent_source="email_campaign_writer",
        platform="email"
    )

    # Generate comprehensive report
    report = tracker.export_analytics_report()
    print(json.dumps(report, indent=2, default=str))