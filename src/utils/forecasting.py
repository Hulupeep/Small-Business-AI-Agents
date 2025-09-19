"""
Advanced demand forecasting algorithms for inventory optimization.

Implements multiple forecasting methods including:
- ARIMA time series analysis
- Seasonal decomposition
- Linear regression with features
- Moving averages with trend detection
- Exponential smoothing
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass
class ForecastConfig:
    """Configuration for demand forecasting"""
    method: str = 'auto'  # auto, arima, linear, exponential, moving_average
    seasonality_period: int = 7  # Days for seasonality detection
    trend_window: int = 30  # Days for trend analysis
    confidence_level: float = 0.95
    min_data_points: int = 10

class DemandForecaster:
    """
    Advanced demand forecasting engine using multiple algorithms
    with automatic method selection based on data characteristics.
    """

    def __init__(self, config: Optional[ForecastConfig] = None):
        self.config = config or ForecastConfig()
        self.scaler = StandardScaler()

    def predict_demand(self, sales_data: pd.DataFrame, forecast_days: int) -> Dict:
        """
        Main forecasting method that selects optimal algorithm and generates predictions.

        Args:
            sales_data: DataFrame with columns ['date', 'quantity_sold']
            forecast_days: Number of days to forecast

        Returns:
            Dictionary with prediction results and metadata
        """
        try:
            if len(sales_data) < self.config.min_data_points:
                return self._simple_average_forecast(sales_data, forecast_days)

            # Prepare data
            prepared_data = self._prepare_data(sales_data)

            # Detect data characteristics
            characteristics = self._analyze_data_characteristics(prepared_data)

            # Select optimal forecasting method
            method = self._select_forecasting_method(characteristics)

            # Generate forecast based on selected method
            if method == 'seasonal_decompose':
                result = self._seasonal_decomposition_forecast(prepared_data, forecast_days)
            elif method == 'linear_regression':
                result = self._linear_regression_forecast(prepared_data, forecast_days)
            elif method == 'exponential_smoothing':
                result = self._exponential_smoothing_forecast(prepared_data, forecast_days)
            elif method == 'moving_average':
                result = self._moving_average_forecast(prepared_data, forecast_days)
            else:
                result = self._arima_forecast(prepared_data, forecast_days)

            # Add metadata
            result.update({
                'method_used': method,
                'data_characteristics': characteristics,
                'forecast_accuracy': self._calculate_accuracy_metrics(prepared_data, method),
                'recommendation_confidence': self._calculate_recommendation_confidence(result, characteristics)
            })

            return result

        except Exception as e:
            logger.error(f"Error in demand forecasting: {e}")
            return self._simple_average_forecast(sales_data, forecast_days)

    def _prepare_data(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """Prepare and clean data for forecasting"""
        df = sales_data.copy()

        # Ensure datetime column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

        # Aggregate by date if multiple records per day
        if 'date' in df.columns:
            df = df.groupby('date')['quantity_sold'].sum().reset_index()

        # Create date range and fill missing dates with 0
        if len(df) > 1:
            date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
            df = df.set_index('date').reindex(date_range, fill_value=0).reset_index()
            df.rename(columns={'index': 'date'}, inplace=True)

        # Add time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

        # Calculate moving averages
        df['ma_7'] = df['quantity_sold'].rolling(window=7, min_periods=1).mean()
        df['ma_30'] = df['quantity_sold'].rolling(window=30, min_periods=1).mean()

        return df

    def _analyze_data_characteristics(self, data: pd.DataFrame) -> Dict:
        """Analyze data to determine optimal forecasting approach"""
        characteristics = {}

        # Basic statistics
        characteristics['data_points'] = len(data)
        characteristics['mean_demand'] = data['quantity_sold'].mean()
        characteristics['std_demand'] = data['quantity_sold'].std()
        characteristics['cv'] = characteristics['std_demand'] / max(characteristics['mean_demand'], 1)

        # Trend analysis
        if len(data) >= 14:
            early_period = data.head(len(data)//2)['quantity_sold'].mean()
            late_period = data.tail(len(data)//2)['quantity_sold'].mean()
            characteristics['trend_strength'] = (late_period - early_period) / max(early_period, 1)
        else:
            characteristics['trend_strength'] = 0

        # Seasonality detection
        characteristics['seasonality'] = self._detect_seasonality(data)

        # Volatility analysis
        characteristics['volatility'] = data['quantity_sold'].std() / max(data['quantity_sold'].mean(), 1)

        # Zero demand frequency
        characteristics['zero_demand_ratio'] = (data['quantity_sold'] == 0).sum() / len(data)

        return characteristics

    def _detect_seasonality(self, data: pd.DataFrame) -> Dict:
        """Detect seasonal patterns in the data"""
        seasonality = {'has_weekly': False, 'has_monthly': False, 'strength': 0}

        if len(data) < 14:
            return seasonality

        # Weekly seasonality
        weekly_pattern = data.groupby('day_of_week')['quantity_sold'].mean()
        weekly_cv = weekly_pattern.std() / max(weekly_pattern.mean(), 1)
        seasonality['weekly_strength'] = weekly_cv
        seasonality['has_weekly'] = weekly_cv > 0.2

        # Monthly seasonality (if enough data)
        if len(data) >= 60:
            monthly_pattern = data.groupby('day_of_month')['quantity_sold'].mean()
            monthly_cv = monthly_pattern.std() / max(monthly_pattern.mean(), 1)
            seasonality['monthly_strength'] = monthly_cv
            seasonality['has_monthly'] = monthly_cv > 0.15

        seasonality['strength'] = max(seasonality.get('weekly_strength', 0),
                                    seasonality.get('monthly_strength', 0))

        return seasonality

    def _select_forecasting_method(self, characteristics: Dict) -> str:
        """Select optimal forecasting method based on data characteristics"""

        # If very little data, use simple methods
        if characteristics['data_points'] < 14:
            return 'moving_average'

        # Strong seasonality - use seasonal decomposition
        if characteristics['seasonality']['strength'] > 0.3:
            return 'seasonal_decompose'

        # Strong trend - use linear regression
        if abs(characteristics['trend_strength']) > 0.2:
            return 'linear_regression'

        # High volatility - use exponential smoothing
        if characteristics['volatility'] > 1.0:
            return 'exponential_smoothing'

        # Stable demand - use ARIMA
        if characteristics['cv'] < 0.5:
            return 'arima'

        # Default to exponential smoothing
        return 'exponential_smoothing'

    def _seasonal_decomposition_forecast(self, data: pd.DataFrame, forecast_days: int) -> Dict:
        """Forecast using seasonal decomposition"""
        try:
            # Simple seasonal forecast
            recent_data = data.tail(28)  # Last 4 weeks

            # Calculate seasonal factors by day of week
            seasonal_factors = recent_data.groupby('day_of_week')['quantity_sold'].mean()
            overall_mean = recent_data['quantity_sold'].mean()

            # Normalize seasonal factors
            if overall_mean > 0:
                seasonal_factors = seasonal_factors / overall_mean
            else:
                seasonal_factors = pd.Series([1.0] * 7, index=range(7))

            # Calculate trend
            trend = self._calculate_trend(recent_data['quantity_sold'])

            # Generate forecast
            base_demand = max(overall_mean, 1)
            forecast_values = []

            for i in range(forecast_days):
                future_date = data['date'].max() + timedelta(days=i+1)
                day_of_week = future_date.weekday()

                # Apply trend and seasonality
                seasonal_factor = seasonal_factors.get(day_of_week, 1.0)
                trend_factor = 1 + (trend * (i + 1) / 30)  # Monthly trend application

                forecasted_demand = base_demand * seasonal_factor * trend_factor
                forecast_values.append(max(0, forecasted_demand))

            total_forecast = sum(forecast_values)

            # Calculate confidence interval
            std_error = recent_data['quantity_sold'].std() / np.sqrt(len(recent_data))
            confidence_interval = (
                total_forecast - 1.96 * std_error * np.sqrt(forecast_days),
                total_forecast + 1.96 * std_error * np.sqrt(forecast_days)
            )

            return {
                'predicted_demand': total_forecast,
                'confidence_interval': confidence_interval,
                'seasonality_factor': seasonal_factors.mean(),
                'trend_factor': 1 + trend,
                'daily_forecast': forecast_values
            }

        except Exception as e:
            logger.error(f"Error in seasonal decomposition forecast: {e}")
            return self._simple_average_forecast(data, forecast_days)

    def _linear_regression_forecast(self, data: pd.DataFrame, forecast_days: int) -> Dict:
        """Forecast using linear regression with time-based features"""
        try:
            # Prepare features
            features = ['day_of_week', 'day_of_month', 'month', 'is_weekend']
            available_features = [f for f in features if f in data.columns]

            if not available_features:
                return self._moving_average_forecast(data, forecast_days)

            # Add time index as feature
            data_copy = data.copy()
            data_copy['time_index'] = range(len(data_copy))
            available_features.append('time_index')

            X = data_copy[available_features].fillna(0)
            y = data_copy['quantity_sold']

            # Train model
            model = LinearRegression()
            model.fit(X, y)

            # Generate future features
            future_features = []
            last_date = data['date'].max()

            for i in range(forecast_days):
                future_date = last_date + timedelta(days=i+1)
                feature_row = {
                    'day_of_week': future_date.weekday(),
                    'day_of_month': future_date.day,
                    'month': future_date.month,
                    'is_weekend': int(future_date.weekday() >= 5),
                    'time_index': len(data) + i
                }
                future_features.append([feature_row.get(f, 0) for f in available_features])

            # Make predictions
            future_X = np.array(future_features)
            predictions = model.predict(future_X)
            predictions = np.maximum(predictions, 0)  # No negative demand

            total_forecast = sum(predictions)

            # Calculate confidence interval using prediction error
            train_predictions = model.predict(X)
            residuals = y - train_predictions
            std_error = np.std(residuals)

            confidence_interval = (
                total_forecast - 1.96 * std_error * np.sqrt(forecast_days),
                total_forecast + 1.96 * std_error * np.sqrt(forecast_days)
            )

            return {
                'predicted_demand': total_forecast,
                'confidence_interval': confidence_interval,
                'seasonality_factor': 1.0,
                'trend_factor': model.coef_[-1] if len(model.coef_) > 0 else 1.0,
                'daily_forecast': predictions.tolist(),
                'model_r2': model.score(X, y)
            }

        except Exception as e:
            logger.error(f"Error in linear regression forecast: {e}")
            return self._moving_average_forecast(data, forecast_days)

    def _exponential_smoothing_forecast(self, data: pd.DataFrame, forecast_days: int) -> Dict:
        """Forecast using exponential smoothing"""
        try:
            values = data['quantity_sold'].values

            if len(values) == 0:
                return self._simple_average_forecast(data, forecast_days)

            # Simple exponential smoothing parameters
            alpha = 0.3  # Smoothing parameter

            # Initialize
            smoothed = [values[0]]

            # Calculate smoothed values
            for i in range(1, len(values)):
                smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
                smoothed.append(smoothed_value)

            # Forecast
            last_smoothed = smoothed[-1]
            daily_forecast = [last_smoothed] * forecast_days
            total_forecast = sum(daily_forecast)

            # Calculate confidence interval
            residuals = values[1:] - smoothed[:-1]
            std_error = np.std(residuals) if len(residuals) > 1 else np.std(values)

            confidence_interval = (
                total_forecast - 1.96 * std_error * np.sqrt(forecast_days),
                total_forecast + 1.96 * std_error * np.sqrt(forecast_days)
            )

            return {
                'predicted_demand': total_forecast,
                'confidence_interval': confidence_interval,
                'seasonality_factor': 1.0,
                'trend_factor': 1.0,
                'daily_forecast': daily_forecast,
                'smoothing_parameter': alpha
            }

        except Exception as e:
            logger.error(f"Error in exponential smoothing forecast: {e}")
            return self._simple_average_forecast(data, forecast_days)

    def _moving_average_forecast(self, data: pd.DataFrame, forecast_days: int) -> Dict:
        """Forecast using moving average with trend adjustment"""
        try:
            values = data['quantity_sold'].values

            if len(values) == 0:
                return {'predicted_demand': 0, 'confidence_interval': (0, 0),
                       'seasonality_factor': 1.0, 'trend_factor': 1.0}

            # Calculate moving average
            window = min(14, len(values))  # 2 weeks or available data
            recent_values = values[-window:]
            ma_value = np.mean(recent_values)

            # Calculate trend
            trend = self._calculate_trend(recent_values)

            # Apply trend to forecast
            daily_forecasts = []
            for i in range(forecast_days):
                trend_adjusted = ma_value * (1 + trend * (i + 1) / 30)
                daily_forecasts.append(max(0, trend_adjusted))

            total_forecast = sum(daily_forecasts)

            # Calculate confidence interval
            std_dev = np.std(recent_values) if len(recent_values) > 1 else ma_value * 0.5
            confidence_interval = (
                total_forecast - 1.96 * std_dev * np.sqrt(forecast_days),
                total_forecast + 1.96 * std_dev * np.sqrt(forecast_days)
            )

            return {
                'predicted_demand': total_forecast,
                'confidence_interval': confidence_interval,
                'seasonality_factor': 1.0,
                'trend_factor': 1 + trend,
                'daily_forecast': daily_forecasts
            }

        except Exception as e:
            logger.error(f"Error in moving average forecast: {e}")
            return self._simple_average_forecast(data, forecast_days)

    def _arima_forecast(self, data: pd.DataFrame, forecast_days: int) -> Dict:
        """Simple ARIMA-like forecast (simplified implementation)"""
        try:
            values = data['quantity_sold'].values

            if len(values) < 5:
                return self._moving_average_forecast(data, forecast_days)

            # Simple auto-regressive approach
            # Calculate lag-1 correlation
            if len(values) > 1:
                lag1_corr = np.corrcoef(values[:-1], values[1:])[0, 1]
                if np.isnan(lag1_corr):
                    lag1_corr = 0
            else:
                lag1_corr = 0

            # Use AR(1) model approximation
            last_value = values[-1]
            mean_value = np.mean(values)

            daily_forecasts = []
            for i in range(forecast_days):
                if i == 0:
                    forecast_value = lag1_corr * last_value + (1 - lag1_corr) * mean_value
                else:
                    # Multi-step forecast
                    forecast_value = lag1_corr * daily_forecasts[i-1] + (1 - lag1_corr) * mean_value

                daily_forecasts.append(max(0, forecast_value))

            total_forecast = sum(daily_forecasts)

            # Calculate confidence interval
            residuals = values[1:] - (lag1_corr * values[:-1] + (1 - lag1_corr) * mean_value)
            std_error = np.std(residuals) if len(residuals) > 1 else np.std(values)

            confidence_interval = (
                total_forecast - 1.96 * std_error * np.sqrt(forecast_days),
                total_forecast + 1.96 * std_error * np.sqrt(forecast_days)
            )

            return {
                'predicted_demand': total_forecast,
                'confidence_interval': confidence_interval,
                'seasonality_factor': 1.0,
                'trend_factor': 1.0,
                'daily_forecast': daily_forecasts,
                'ar_coefficient': lag1_corr
            }

        except Exception as e:
            logger.error(f"Error in ARIMA forecast: {e}")
            return self._moving_average_forecast(data, forecast_days)

    def _simple_average_forecast(self, data: pd.DataFrame, forecast_days: int) -> Dict:
        """Fallback simple average forecast"""
        if 'quantity_sold' in data.columns and len(data) > 0:
            avg_demand = data['quantity_sold'].mean()
            std_demand = data['quantity_sold'].std()
        else:
            avg_demand = 5.0  # Default conservative estimate
            std_demand = 2.0

        total_forecast = avg_demand * forecast_days

        confidence_interval = (
            max(0, total_forecast - 1.96 * std_demand * np.sqrt(forecast_days)),
            total_forecast + 1.96 * std_demand * np.sqrt(forecast_days)
        )

        return {
            'predicted_demand': total_forecast,
            'confidence_interval': confidence_interval,
            'seasonality_factor': 1.0,
            'trend_factor': 1.0,
            'daily_forecast': [avg_demand] * forecast_days
        }

    def _calculate_trend(self, values: np.ndarray) -> float:
        """Calculate trend coefficient"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        try:
            # Simple linear regression for trend
            trend_coef = np.polyfit(x, values, 1)[0]
            return trend_coef / max(np.mean(values), 1)  # Normalize by mean
        except:
            return 0.0

    def _calculate_accuracy_metrics(self, data: pd.DataFrame, method: str) -> Dict:
        """Calculate forecasting accuracy metrics"""
        try:
            if len(data) < 10:
                return {'mae': 0, 'mape': 0, 'rmse': 0}

            # Use last 30% of data for validation
            split_point = int(len(data) * 0.7)
            train_data = data.iloc[:split_point]
            test_data = data.iloc[split_point:]

            if len(test_data) < 3:
                return {'mae': 0, 'mape': 0, 'rmse': 0}

            # Generate forecast for test period
            test_forecast = self.predict_demand(train_data, len(test_data))

            # Calculate metrics
            actual = test_data['quantity_sold'].values
            predicted = test_forecast.get('daily_forecast', [np.mean(actual)] * len(actual))
            predicted = predicted[:len(actual)]  # Match lengths

            mae = mean_absolute_error(actual, predicted)
            rmse = np.sqrt(mean_squared_error(actual, predicted))

            # MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((actual - predicted) / np.maximum(actual, 1))) * 100

            return {'mae': mae, 'mape': mape, 'rmse': rmse}

        except Exception as e:
            logger.error(f"Error calculating accuracy metrics: {e}")
            return {'mae': 0, 'mape': 0, 'rmse': 0}

    def _calculate_recommendation_confidence(self, forecast_result: Dict,
                                          characteristics: Dict) -> float:
        """Calculate confidence in the forecast recommendation"""
        confidence = 0.5  # Base confidence

        # Increase confidence based on data quality
        if characteristics['data_points'] >= 30:
            confidence += 0.2
        elif characteristics['data_points'] >= 14:
            confidence += 0.1

        # Adjust for volatility
        if characteristics['volatility'] < 0.5:
            confidence += 0.2
        elif characteristics['volatility'] > 1.5:
            confidence -= 0.2

        # Adjust for seasonality detection
        if characteristics['seasonality']['strength'] > 0.3:
            confidence += 0.1

        # Adjust for accuracy metrics
        accuracy = forecast_result.get('forecast_accuracy', {})
        if accuracy.get('mape', 100) < 20:  # Less than 20% error
            confidence += 0.2
        elif accuracy.get('mape', 100) > 50:  # More than 50% error
            confidence -= 0.2

        return max(0.1, min(1.0, confidence))