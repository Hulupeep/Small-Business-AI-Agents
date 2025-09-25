"""
Farm Production Manager Agent
Intelligent crop and livestock management with predictive analytics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class CropStage(Enum):
    PLANNED = "planned"
    PLANTED = "planted"
    GROWING = "growing"
    READY_TO_HARVEST = "ready_to_harvest"
    HARVESTED = "harvested"

class LivestockType(Enum):
    DAIRY_COWS = "dairy_cows"
    BEEF_CATTLE = "beef_cattle"
    POULTRY = "poultry"
    SHEEP = "sheep"
    GOATS = "goats"
    PIGS = "pigs"

@dataclass
class CropRecord:
    crop_id: str
    variety: str
    field_id: str
    planted_date: Optional[datetime]
    expected_harvest: Optional[datetime]
    current_stage: CropStage
    area_hectares: float
    estimated_yield: Optional[float]
    actual_yield: Optional[float]

@dataclass
class LivestockRecord:
    animal_id: str
    livestock_type: LivestockType
    breed: str
    birth_date: datetime
    health_status: str
    location: str
    production_data: Dict

@dataclass
class WeatherData:
    date: datetime
    temperature_avg: float
    temperature_min: float
    temperature_max: float
    humidity: float
    precipitation: float
    wind_speed: float
    solar_radiation: float

class FarmProductionManager:
    """
    AI-powered farm production management system that optimizes
    crop planning, livestock management, and resource allocation.
    """

    def __init__(self, farm_config: Dict):
        self.farm_config = farm_config
        self.crops: Dict[str, CropRecord] = {}
        self.livestock: Dict[str, LivestockRecord] = {}
        self.weather_history: List[WeatherData] = []
        self.yield_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_model_trained = False

    async def initialize(self):
        """Initialize the production manager with historical data"""
        logger.info("Initializing Farm Production Manager")
        await self._load_historical_data()
        await self._train_yield_prediction_model()
        logger.info("Farm Production Manager initialized successfully")

    async def _load_historical_data(self):
        """Load historical crop, livestock, and weather data"""
        # In production, this would load from database
        # For demo, we'll simulate some data
        pass

    async def _train_yield_prediction_model(self):
        """Train machine learning model for yield prediction"""
        # Simulate training data
        # In production, this would use real historical data
        X_sample = np.random.rand(1000, 8)  # weather features
        y_sample = np.random.rand(1000) * 10  # yield data

        X_scaled = self.scaler.fit_transform(X_sample)
        self.yield_predictor.fit(X_scaled, y_sample)
        self.is_model_trained = True
        logger.info("Yield prediction model trained successfully")

    async def add_crop(self, crop_data: Dict) -> str:
        """Add new crop to tracking system"""
        crop_id = f"crop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        crop = CropRecord(
            crop_id=crop_id,
            variety=crop_data['variety'],
            field_id=crop_data['field_id'],
            planted_date=crop_data.get('planted_date'),
            expected_harvest=crop_data.get('expected_harvest'),
            current_stage=CropStage(crop_data.get('stage', 'planned')),
            area_hectares=crop_data['area_hectares'],
            estimated_yield=crop_data.get('estimated_yield'),
            actual_yield=None
        )

        self.crops[crop_id] = crop
        logger.info(f"Added crop {crop_id}: {crop.variety} in field {crop.field_id}")
        return crop_id

    async def add_livestock(self, livestock_data: Dict) -> str:
        """Add new livestock to tracking system"""
        animal_id = livestock_data.get('animal_id') or f"animal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        livestock = LivestockRecord(
            animal_id=animal_id,
            livestock_type=LivestockType(livestock_data['type']),
            breed=livestock_data['breed'],
            birth_date=livestock_data['birth_date'],
            health_status=livestock_data.get('health_status', 'healthy'),
            location=livestock_data['location'],
            production_data=livestock_data.get('production_data', {})
        )

        self.livestock[animal_id] = livestock
        logger.info(f"Added livestock {animal_id}: {livestock.breed} {livestock.livestock_type.value}")
        return animal_id

    async def update_weather_data(self, weather_data: WeatherData):
        """Update weather data for planning and predictions"""
        self.weather_history.append(weather_data)
        # Keep only last 365 days
        cutoff_date = datetime.now() - timedelta(days=365)
        self.weather_history = [w for w in self.weather_history if w.date >= cutoff_date]
        logger.debug(f"Updated weather data for {weather_data.date}")

    async def predict_yield(self, crop_id: str, weather_forecast: List[WeatherData]) -> float:
        """Predict crop yield based on current conditions and weather forecast"""
        if not self.is_model_trained:
            await self._train_yield_prediction_model()

        crop = self.crops.get(crop_id)
        if not crop:
            raise ValueError(f"Crop {crop_id} not found")

        # Extract features from weather data
        features = self._extract_weather_features(weather_forecast)
        features_scaled = self.scaler.transform([features])

        predicted_yield = self.yield_predictor.predict(features_scaled)[0]

        # Update crop record
        crop.estimated_yield = predicted_yield * crop.area_hectares

        logger.info(f"Predicted yield for {crop_id}: {predicted_yield:.2f} tons/hectare")
        return predicted_yield

    def _extract_weather_features(self, weather_data: List[WeatherData]) -> List[float]:
        """Extract relevant features from weather data"""
        if not weather_data:
            return [0] * 8

        temps = [w.temperature_avg for w in weather_data]
        humidity = [w.humidity for w in weather_data]
        precipitation = [w.precipitation for w in weather_data]
        radiation = [w.solar_radiation for w in weather_data]

        features = [
            np.mean(temps),
            np.std(temps),
            np.mean(humidity),
            np.sum(precipitation),
            np.max(precipitation),
            np.mean(radiation),
            len([p for p in precipitation if p > 5]),  # rainy days
            len([t for t in temps if t < 0])  # frost days
        ]

        return features

    async def optimize_harvest_schedule(self, weather_forecast: List[WeatherData]) -> Dict[str, datetime]:
        """Optimize harvest timing based on weather and crop maturity"""
        harvest_schedule = {}

        for crop_id, crop in self.crops.items():
            if crop.current_stage in [CropStage.GROWING, CropStage.READY_TO_HARVEST]:
                optimal_date = await self._calculate_optimal_harvest_date(
                    crop, weather_forecast
                )
                harvest_schedule[crop_id] = optimal_date
                logger.info(f"Optimal harvest date for {crop_id}: {optimal_date}")

        return harvest_schedule

    async def _calculate_optimal_harvest_date(self, crop: CropRecord, weather_forecast: List[WeatherData]) -> datetime:
        """Calculate optimal harvest date considering weather and maturity"""
        base_date = crop.expected_harvest or datetime.now() + timedelta(days=30)

        # Find weather windows (no rain for 2+ consecutive days)
        suitable_dates = []
        for i in range(len(weather_forecast) - 1):
            if (weather_forecast[i].precipitation < 1 and
                weather_forecast[i + 1].precipitation < 1):
                suitable_dates.append(weather_forecast[i].date)

        # Choose closest suitable date to expected harvest
        if suitable_dates:
            optimal_date = min(suitable_dates, key=lambda d: abs((d - base_date).days))
        else:
            optimal_date = base_date

        return optimal_date

    async def manage_feed_fertilizer(self) -> Dict[str, Dict]:
        """Manage feed for livestock and fertilizer for crops"""
        recommendations = {
            'feed_requirements': {},
            'fertilizer_requirements': {}
        }

        # Calculate feed requirements
        for animal_id, livestock in self.livestock.items():
            daily_feed = self._calculate_daily_feed_requirement(livestock)
            recommendations['feed_requirements'][animal_id] = {
                'daily_kg': daily_feed,
                'feed_type': self._get_optimal_feed_type(livestock),
                'cost_per_day': daily_feed * self._get_feed_cost_per_kg(livestock.livestock_type)
            }

        # Calculate fertilizer requirements
        for crop_id, crop in self.crops.items():
            if crop.current_stage in [CropStage.PLANTED, CropStage.GROWING]:
                fertilizer_plan = self._calculate_fertilizer_requirement(crop)
                recommendations['fertilizer_requirements'][crop_id] = fertilizer_plan

        return recommendations

    def _calculate_daily_feed_requirement(self, livestock: LivestockRecord) -> float:
        """Calculate daily feed requirement for livestock"""
        feed_rates = {
            LivestockType.DAIRY_COWS: 25.0,  # kg/day
            LivestockType.BEEF_CATTLE: 12.0,
            LivestockType.POULTRY: 0.12,
            LivestockType.SHEEP: 2.5,
            LivestockType.GOATS: 2.0,
            LivestockType.PIGS: 3.0
        }

        base_requirement = feed_rates.get(livestock.livestock_type, 5.0)

        # Adjust for production data (e.g., milk yield for dairy cows)
        if livestock.livestock_type == LivestockType.DAIRY_COWS:
            milk_yield = livestock.production_data.get('daily_milk_kg', 20)
            base_requirement += milk_yield * 0.4  # Additional feed for milk production

        return base_requirement

    def _get_optimal_feed_type(self, livestock: LivestockRecord) -> str:
        """Get optimal feed type for livestock"""
        feed_types = {
            LivestockType.DAIRY_COWS: "high_protein_silage",
            LivestockType.BEEF_CATTLE: "grass_hay",
            LivestockType.POULTRY: "layer_feed",
            LivestockType.SHEEP: "pasture_grass",
            LivestockType.GOATS: "mixed_hay",
            LivestockType.PIGS: "pig_feed_pellets"
        }

        return feed_types.get(livestock.livestock_type, "general_feed")

    def _get_feed_cost_per_kg(self, livestock_type: LivestockType) -> float:
        """Get current feed cost per kg"""
        costs = {
            LivestockType.DAIRY_COWS: 0.45,  # EUR/kg
            LivestockType.BEEF_CATTLE: 0.35,
            LivestockType.POULTRY: 0.55,
            LivestockType.SHEEP: 0.30,
            LivestockType.GOATS: 0.32,
            LivestockType.PIGS: 0.40
        }

        return costs.get(livestock_type, 0.35)

    def _calculate_fertilizer_requirement(self, crop: CropRecord) -> Dict:
        """Calculate fertilizer requirements for crop"""
        # Base fertilizer requirements per hectare
        fertilizer_rates = {
            'tomatoes': {'N': 150, 'P': 80, 'K': 200},
            'lettuce': {'N': 120, 'P': 60, 'K': 150},
            'carrots': {'N': 100, 'P': 70, 'K': 180},
            'potatoes': {'N': 140, 'P': 90, 'K': 220},
            'wheat': {'N': 180, 'P': 60, 'K': 40},
            'barley': {'N': 120, 'P': 50, 'K': 30},
            'apples': {'N': 80, 'P': 40, 'K': 120}
        }

        base_rates = fertilizer_rates.get(crop.variety, {'N': 100, 'P': 50, 'K': 100})

        return {
            'nitrogen_kg': base_rates['N'] * crop.area_hectares,
            'phosphorus_kg': base_rates['P'] * crop.area_hectares,
            'potassium_kg': base_rates['K'] * crop.area_hectares,
            'estimated_cost': (base_rates['N'] * 1.2 + base_rates['P'] * 1.5 + base_rates['K'] * 0.8) * crop.area_hectares,
            'application_timing': self._get_fertilizer_timing(crop)
        }

    def _get_fertilizer_timing(self, crop: CropRecord) -> List[Dict]:
        """Get optimal fertilizer application timing"""
        timing_schedules = {
            'tomatoes': [
                {'stage': 'planting', 'N': 0.3, 'P': 1.0, 'K': 0.5},
                {'stage': 'flowering', 'N': 0.4, 'P': 0.0, 'K': 0.3},
                {'stage': 'fruiting', 'N': 0.3, 'P': 0.0, 'K': 0.2}
            ],
            'wheat': [
                {'stage': 'planting', 'N': 0.4, 'P': 1.0, 'K': 1.0},
                {'stage': 'tillering', 'N': 0.3, 'P': 0.0, 'K': 0.0},
                {'stage': 'grain_filling', 'N': 0.3, 'P': 0.0, 'K': 0.0}
            ]
        }

        return timing_schedules.get(crop.variety, [{'stage': 'planting', 'N': 1.0, 'P': 1.0, 'K': 1.0}])

    async def get_farm_status(self) -> Dict:
        """Get comprehensive farm status overview"""
        status = {
            'crops': {
                'total_crops': len(self.crops),
                'by_stage': {},
                'total_area': sum(crop.area_hectares for crop in self.crops.values()),
                'estimated_total_yield': sum(crop.estimated_yield or 0 for crop in self.crops.values())
            },
            'livestock': {
                'total_animals': len(self.livestock),
                'by_type': {},
                'health_summary': {}
            },
            'weather': {
                'last_update': max(w.date for w in self.weather_history) if self.weather_history else None,
                'recent_conditions': self.weather_history[-7:] if len(self.weather_history) >= 7 else self.weather_history
            }
        }

        # Aggregate crop data
        for crop in self.crops.values():
            stage = crop.current_stage.value
            status['crops']['by_stage'][stage] = status['crops']['by_stage'].get(stage, 0) + 1

        # Aggregate livestock data
        for livestock in self.livestock.values():
            ltype = livestock.livestock_type.value
            status['livestock']['by_type'][ltype] = status['livestock']['by_type'].get(ltype, 0) + 1

            health = livestock.health_status
            status['livestock']['health_summary'][health] = status['livestock']['health_summary'].get(health, 0) + 1

        return status

    async def generate_recommendations(self) -> Dict[str, List[str]]:
        """Generate AI-powered recommendations for farm management"""
        recommendations = {
            'urgent': [],
            'important': [],
            'suggestions': []
        }

        # Check for urgent actions
        for crop_id, crop in self.crops.items():
            if crop.current_stage == CropStage.READY_TO_HARVEST:
                recommendations['urgent'].append(f"Harvest {crop.variety} in field {crop.field_id} (Crop ID: {crop_id})")

        # Check livestock health
        for animal_id, livestock in self.livestock.items():
            if livestock.health_status == 'needs_attention':
                recommendations['urgent'].append(f"Check health of {livestock.breed} {livestock.livestock_type.value} (ID: {animal_id})")

        # Important tasks
        if len([c for c in self.crops.values() if c.current_stage == CropStage.PLANNED]) > 0:
            recommendations['important'].append("Several crops are planned but not yet planted")

        # Suggestions for optimization
        total_area = sum(crop.area_hectares for crop in self.crops.values())
        if total_area < self.farm_config.get('total_area', 50) * 0.8:
            recommendations['suggestions'].append("Consider utilizing more farmland for increased production")

        return recommendations

# Example usage and testing
async def main():
    """Example usage of Farm Production Manager"""
    farm_config = {
        'name': 'Green Valley Farm',
        'total_area': 50,
        'location': {'latitude': 52.3676, 'longitude': 4.9041}
    }

    manager = FarmProductionManager(farm_config)
    await manager.initialize()

    # Add some crops
    crop_data = {
        'variety': 'tomatoes',
        'field_id': 'field_001',
        'area_hectares': 2.5,
        'stage': 'planted',
        'planted_date': datetime.now() - timedelta(days=30)
    }
    crop_id = await manager.add_crop(crop_data)

    # Add livestock
    livestock_data = {
        'type': 'dairy_cows',
        'breed': 'Holstein-Friesian',
        'birth_date': datetime.now() - timedelta(days=365*3),
        'location': 'barn_001',
        'production_data': {'daily_milk_kg': 25}
    }
    await manager.add_livestock(livestock_data)

    # Get farm status
    status = await manager.get_farm_status()
    print("Farm Status:", status)

    # Get recommendations
    recommendations = await manager.generate_recommendations()
    print("Recommendations:", recommendations)

if __name__ == "__main__":
    asyncio.run(main())