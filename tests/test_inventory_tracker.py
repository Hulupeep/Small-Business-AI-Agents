"""
Comprehensive tests for the Inventory Tracker Agent.

Tests cover:
- Real-time inventory monitoring
- Demand forecasting accuracy
- Purchase order automation
- Business impact calculations
- Integration with external systems
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.agents.inventory_tracker import InventoryTrackerAgent, InventoryAlert, ForecastResult
from src.database.models import (
    DatabaseManager, Product, InventoryItem, Location, SalesHistory,
    PurchaseOrder, Supplier, BusinessMetric, Base
)
from src.utils.forecasting import DemandForecaster

class TestInventoryTrackerAgent:
    """Test suite for Inventory Tracker Agent"""

    @pytest.fixture
    def db_manager(self):
        """Create test database"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return DatabaseManager("sqlite:///:memory:")

    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            'database_url': 'sqlite:///:memory:',
            'notifications': {
                'email_enabled': False,  # Disable for testing
                'smtp_host': 'test.smtp.com',
                'smtp_username': 'test@test.com',
                'smtp_password': 'password',
                'from_email': 'test@test.com',
                'default_email_recipients': ['manager@test.com']
            }
        }

    @pytest.fixture
    def agent(self, sample_config):
        """Create test agent instance"""
        with patch('src.agents.inventory_tracker.NotificationManager'):
            return InventoryTrackerAgent(sample_config)

    @pytest.fixture
    def sample_data(self, agent):
        """Create sample test data"""
        session = agent.db_manager.get_session()

        # Create supplier
        supplier = Supplier(
            name="Test Supplier",
            contact_email="supplier@test.com",
            lead_time_days=7
        )
        session.add(supplier)
        session.flush()

        # Create location
        location = Location(
            name="Main Warehouse",
            address="123 Test St",
            type="warehouse"
        )
        session.add(location)
        session.flush()

        # Create product
        product = Product(
            sku="TEST-001",
            name="Test Product",
            unit_cost=10.0,
            selling_price=25.0,
            reorder_point=20,
            reorder_quantity=100,
            supplier_id=supplier.id
        )
        session.add(product)
        session.flush()

        # Create inventory item
        inventory_item = InventoryItem(
            product_id=product.id,
            location_id=location.id,
            quantity_on_hand=15,  # Below reorder point
            quantity_available=15
        )
        session.add(inventory_item)

        # Create sales history
        for i in range(30):
            sale_date = datetime.utcnow() - timedelta(days=i)
            sales_record = SalesHistory(
                product_id=product.id,
                location_id=location.id,
                quantity_sold=5 + (i % 3),  # Varying demand
                sale_price=25.0,
                sale_date=sale_date,
                season="summer",
                day_of_week=sale_date.weekday()
            )
            session.add(sales_record)

        session.commit()
        agent.db_manager.close_session(session)

        return {
            'supplier_id': supplier.id,
            'location_id': location.id,
            'product_id': product.id
        }

    def test_monitor_inventory_levels(self, agent, sample_data):
        """Test inventory level monitoring"""
        alerts = agent.monitor_inventory_levels()

        assert len(alerts) > 0
        alert = alerts[0]

        assert isinstance(alert, InventoryAlert)
        assert alert.product_id == sample_data['product_id']
        assert alert.current_quantity == 15
        assert alert.reorder_point == 20
        assert alert.urgency_level in ['low', 'medium', 'high', 'critical']
        assert alert.recommended_order_qty > 0

    def test_demand_forecasting(self, agent, sample_data):
        """Test demand forecasting accuracy"""
        forecast = agent.forecast_demand(
            sample_data['product_id'],
            sample_data['location_id'],
            30
        )

        assert isinstance(forecast, ForecastResult)
        assert forecast.predicted_demand > 0
        assert len(forecast.confidence_interval) == 2
        assert forecast.confidence_interval[0] <= forecast.predicted_demand <= forecast.confidence_interval[1]
        assert 0 <= forecast.seasonality_factor <= 5  # Reasonable range
        assert 0 <= forecast.trend_factor <= 5  # Reasonable range

    def test_generate_purchase_orders(self, agent, sample_data):
        """Test automatic purchase order generation"""
        # First generate alerts
        alerts = agent.monitor_inventory_levels()
        assert len(alerts) > 0

        # Set alert urgency to critical to trigger PO generation
        for alert in alerts:
            alert.urgency_level = 'critical'

        # Generate purchase orders
        po_ids = agent.generate_purchase_orders(alerts)

        assert len(po_ids) > 0

        # Verify PO was created in database
        session = agent.db_manager.get_session()
        po = session.query(PurchaseOrder).filter(PurchaseOrder.id == po_ids[0]).first()

        assert po is not None
        assert po.supplier_id == sample_data['supplier_id']
        assert po.status == 'pending'
        assert po.total_amount > 0

        agent.db_manager.close_session(session)

    def test_inventory_optimization(self, agent, sample_data):
        """Test inventory optimization recommendations"""
        optimization_results = agent.optimize_inventory_levels()

        assert 'current_inventory_value' in optimization_results
        assert 'optimized_inventory_value' in optimization_results
        assert 'potential_savings' in optimization_results
        assert 'optimization_percentage' in optimization_results
        assert 'excess_inventory_items' in optimization_results

        assert optimization_results['current_inventory_value'] >= 0
        assert optimization_results['optimized_inventory_value'] >= 0
        assert optimization_results['optimization_percentage'] >= 0

    def test_business_impact_calculation(self, agent, sample_data):
        """Test business impact metrics calculation"""
        # First create some business metrics
        session = agent.db_manager.get_session()

        metric1 = BusinessMetric(
            metric_type='prevented_stockout',
            agent_type='inventory_tracker',
            value=1,
            unit='count',
            date_recorded=datetime.utcnow() - timedelta(days=5)
        )

        metric2 = BusinessMetric(
            metric_type='time_saved',
            agent_type='inventory_tracker',
            value=2.5,
            unit='hours',
            date_recorded=datetime.utcnow() - timedelta(days=3)
        )

        session.add(metric1)
        session.add(metric2)
        session.commit()
        agent.db_manager.close_session(session)

        # Calculate business impact
        impact = agent.calculate_business_impact()

        assert 'monthly_cost_savings' in impact
        assert 'annual_cost_savings' in impact
        assert 'prevented_stockouts_count' in impact
        assert 'automation_time_saved_hours' in impact
        assert 'roi_percentage' in impact

        assert impact['monthly_cost_savings'] >= 0
        assert impact['annual_cost_savings'] >= 0
        assert impact['prevented_stockouts_count'] >= 0

    def test_run_monitoring_cycle(self, agent, sample_data):
        """Test complete monitoring cycle"""
        results = agent.run_monitoring_cycle()

        assert 'alerts_generated' in results
        assert 'critical_alerts' in results
        assert 'purchase_orders_generated' in results
        assert 'optimization_opportunities' in results
        assert 'business_impact' in results

        assert results['alerts_generated'] >= 0
        assert results['critical_alerts'] >= 0
        assert results['purchase_orders_generated'] >= 0

    @patch('src.agents.inventory_tracker.NotificationManager')
    def test_notification_integration(self, mock_notification_manager, agent, sample_data):
        """Test notification system integration"""
        # Mock the notification manager
        mock_notification = Mock()
        agent.notification_manager = mock_notification

        # Run monitoring cycle which should trigger notifications
        results = agent.run_monitoring_cycle()

        # Verify notifications were attempted
        assert mock_notification.send_notification.called

    def test_forecasting_with_insufficient_data(self, agent):
        """Test forecasting behavior with insufficient historical data"""
        # Create product with no sales history
        session = agent.db_manager.get_session()

        product = Product(
            sku="TEST-002",
            name="New Product",
            unit_cost=5.0,
            selling_price=15.0,
            reorder_point=10,
            reorder_quantity=50
        )
        session.add(product)
        session.flush()

        forecast = agent.forecast_demand(product.id, None, 30)

        # Should handle gracefully with default values
        assert isinstance(forecast, ForecastResult)
        assert forecast.predicted_demand > 0  # Should provide reasonable default

        agent.db_manager.close_session(session)

    def test_edge_cases_and_error_handling(self, agent):
        """Test edge cases and error handling"""
        # Test with non-existent product
        forecast = agent.forecast_demand(99999, 99999, 30)
        assert isinstance(forecast, ForecastResult)

        # Test monitoring with empty database
        alerts = agent.monitor_inventory_levels()
        assert isinstance(alerts, list)

        # Test PO generation with empty alerts
        po_ids = agent.generate_purchase_orders([])
        assert isinstance(po_ids, list)
        assert len(po_ids) == 0

    def test_alert_urgency_calculation(self, agent, sample_data):
        """Test alert urgency level calculation"""
        alerts = agent.monitor_inventory_levels()

        for alert in alerts:
            assert alert.urgency_level in ['low', 'medium', 'high', 'critical']

            # Critical alerts should have very low stock
            if alert.urgency_level == 'critical':
                assert alert.current_quantity <= alert.reorder_point * 0.5

    def test_seasonal_demand_patterns(self, agent, sample_data):
        """Test seasonal demand pattern recognition"""
        session = agent.db_manager.get_session()

        # Add seasonal sales data
        product_id = sample_data['product_id']
        location_id = sample_data['location_id']

        # Simulate seasonal patterns
        seasons = ['winter', 'spring', 'summer', 'fall']
        for i in range(120):  # 4 months of data
            sale_date = datetime.utcnow() - timedelta(days=i)
            season = seasons[i // 30]  # Change season every 30 days

            # Simulate seasonal demand variation
            base_demand = 5
            if season == 'winter':
                seasonal_demand = base_demand * 1.5  # Higher winter demand
            elif season == 'summer':
                seasonal_demand = base_demand * 0.7  # Lower summer demand
            else:
                seasonal_demand = base_demand

            sales_record = SalesHistory(
                product_id=product_id,
                location_id=location_id,
                quantity_sold=int(seasonal_demand),
                sale_price=25.0,
                sale_date=sale_date,
                season=season,
                day_of_week=sale_date.weekday()
            )
            session.add(sales_record)

        session.commit()

        # Test forecast with seasonal data
        forecast = agent.forecast_demand(product_id, location_id, 30)

        # Should detect seasonality
        assert forecast.seasonality_factor != 1.0  # Should detect some seasonal pattern

        agent.db_manager.close_session(session)

    def test_multiple_location_inventory(self, agent, sample_data):
        """Test inventory tracking across multiple locations"""
        session = agent.db_manager.get_session()

        # Create second location
        location2 = Location(
            name="Secondary Warehouse",
            address="456 Test Ave",
            type="warehouse"
        )
        session.add(location2)
        session.flush()

        # Create inventory at second location
        inventory_item2 = InventoryItem(
            product_id=sample_data['product_id'],
            location_id=location2.id,
            quantity_on_hand=5,  # Very low stock
            quantity_available=5
        )
        session.add(inventory_item2)
        session.commit()

        # Monitor should detect issues at both locations
        alerts = agent.monitor_inventory_levels()

        # Should have alerts for both locations
        locations_with_alerts = set(alert.location_id for alert in alerts)
        assert len(locations_with_alerts) >= 2

        agent.db_manager.close_session(session)

class TestDemandForecaster:
    """Test suite for Demand Forecasting algorithms"""

    @pytest.fixture
    def forecaster(self):
        """Create forecaster instance"""
        return DemandForecaster()

    @pytest.fixture
    def sample_sales_data(self):
        """Create sample sales data for testing"""
        dates = pd.date_range(start='2023-01-01', end='2023-03-31', freq='D')
        data = []

        for i, date in enumerate(dates):
            # Simulate trend and seasonality
            trend = i * 0.1
            seasonality = 2 * (1 + 0.5 * (i % 7))  # Weekly pattern
            noise = (i % 3) - 1  # Some random variation

            quantity = max(1, int(5 + trend + seasonality + noise))

            data.append({
                'date': date,
                'quantity_sold': quantity,
                'sale_price': 25.0,
                'season': 'winter' if date.month <= 2 else 'spring',
                'day_of_week': date.weekday()
            })

        return pd.DataFrame(data)

    def test_forecasting_methods(self, forecaster, sample_sales_data):
        """Test different forecasting methods"""
        forecast = forecaster.predict_demand(sample_sales_data, 30)

        assert 'predicted_demand' in forecast
        assert 'confidence_interval' in forecast
        assert 'method_used' in forecast
        assert 'forecast_accuracy' in forecast

        assert forecast['predicted_demand'] > 0
        assert len(forecast['confidence_interval']) == 2
        assert forecast['method_used'] in [
            'seasonal_decompose', 'linear_regression', 'exponential_smoothing',
            'moving_average', 'arima'
        ]

    def test_seasonality_detection(self, forecaster, sample_sales_data):
        """Test seasonality detection in data"""
        prepared_data = forecaster._prepare_data(sample_sales_data)
        characteristics = forecaster._analyze_data_characteristics(prepared_data)

        assert 'seasonality' in characteristics
        assert 'has_weekly' in characteristics['seasonality']
        assert isinstance(characteristics['seasonality']['strength'], float)

    def test_trend_analysis(self, forecaster, sample_sales_data):
        """Test trend analysis capabilities"""
        prepared_data = forecaster._prepare_data(sample_sales_data)
        characteristics = forecaster._analyze_data_characteristics(prepared_data)

        assert 'trend_strength' in characteristics
        assert isinstance(characteristics['trend_strength'], float)

    def test_method_selection(self, forecaster, sample_sales_data):
        """Test automatic method selection"""
        prepared_data = forecaster._prepare_data(sample_sales_data)
        characteristics = forecaster._analyze_data_characteristics(prepared_data)
        method = forecaster._select_forecasting_method(characteristics)

        assert method in [
            'seasonal_decompose', 'linear_regression', 'exponential_smoothing',
            'moving_average', 'arima'
        ]

    def test_insufficient_data_handling(self, forecaster):
        """Test handling of insufficient data"""
        # Very limited data
        limited_data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=3),
            'quantity_sold': [1, 2, 3],
            'sale_price': [25.0, 25.0, 25.0]
        })

        forecast = forecaster.predict_demand(limited_data, 7)

        # Should handle gracefully
        assert 'predicted_demand' in forecast
        assert forecast['predicted_demand'] > 0

    def test_accuracy_metrics(self, forecaster, sample_sales_data):
        """Test forecasting accuracy calculation"""
        # Use subset for training
        train_data = sample_sales_data.iloc[:60]  # First 60 days
        test_data = sample_sales_data.iloc[60:]   # Remaining days

        # Get forecast for test period
        forecast = forecaster.predict_demand(train_data, len(test_data))

        # Should include accuracy metrics
        assert 'forecast_accuracy' in forecast
        accuracy = forecast['forecast_accuracy']

        assert 'mae' in accuracy
        assert 'mape' in accuracy
        assert 'rmse' in accuracy

        # Values should be reasonable
        assert accuracy['mae'] >= 0
        assert accuracy['mape'] >= 0
        assert accuracy['rmse'] >= 0