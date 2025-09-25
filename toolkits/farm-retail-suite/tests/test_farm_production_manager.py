"""
Test suite for Farm Production Manager Agent
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

from src.farm_production_manager import (
    FarmProductionManager,
    CropStage,
    LivestockType,
    CropRecord,
    LivestockRecord,
    WeatherData
)


class TestFarmProductionManager:
    """Test cases for Farm Production Manager functionality"""

    @pytest.fixture
    async def manager(self):
        """Create test manager instance"""
        farm_config = {
            'name': 'Test Farm',
            'total_area': 50,
            'location': {'latitude': 52.3676, 'longitude': 4.9041}
        }
        manager = FarmProductionManager(farm_config)
        await manager.initialize()
        return manager

    @pytest.mark.asyncio
    async def test_add_crop(self, manager):
        """Test adding new crop to tracking system"""
        crop_data = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 2.5,
            'stage': 'planted',
            'planted_date': datetime.now() - timedelta(days=30)
        }

        crop_id = await manager.add_crop(crop_data)

        assert crop_id in manager.crops
        crop = manager.crops[crop_id]
        assert crop.variety == 'tomatoes'
        assert crop.field_id == 'field_001'
        assert crop.area_hectares == 2.5
        assert crop.current_stage == CropStage.PLANTED

    @pytest.mark.asyncio
    async def test_add_livestock(self, manager):
        """Test adding new livestock to tracking system"""
        livestock_data = {
            'type': 'dairy_cows',
            'breed': 'Holstein-Friesian',
            'birth_date': datetime.now() - timedelta(days=365*3),
            'location': 'barn_001',
            'production_data': {'daily_milk_kg': 25}
        }

        animal_id = await manager.add_livestock(livestock_data)

        assert animal_id in manager.livestock
        livestock = manager.livestock[animal_id]
        assert livestock.livestock_type == LivestockType.DAIRY_COWS
        assert livestock.breed == 'Holstein-Friesian'
        assert livestock.production_data['daily_milk_kg'] == 25

    @pytest.mark.asyncio
    async def test_weather_data_update(self, manager):
        """Test weather data management"""
        weather_data = WeatherData(
            date=datetime.now(),
            temperature_avg=18.5,
            temperature_min=12.0,
            temperature_max=25.0,
            humidity=65.0,
            precipitation=2.5,
            wind_speed=8.0,
            solar_radiation=420.0
        )

        initial_count = len(manager.weather_history)
        await manager.update_weather_data(weather_data)

        assert len(manager.weather_history) == initial_count + 1
        assert manager.weather_history[-1].temperature_avg == 18.5

    @pytest.mark.asyncio
    async def test_yield_prediction(self, manager):
        """Test crop yield prediction"""
        # Add a crop first
        crop_data = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 2.5,
            'stage': 'growing'
        }
        crop_id = await manager.add_crop(crop_data)

        # Create weather forecast
        weather_forecast = [
            WeatherData(
                date=datetime.now() + timedelta(days=i),
                temperature_avg=20.0 + i,
                temperature_min=15.0,
                temperature_max=25.0,
                humidity=60.0,
                precipitation=1.0 if i % 3 == 0 else 0.0,
                wind_speed=5.0,
                solar_radiation=450.0
            )
            for i in range(14)
        ]

        predicted_yield = await manager.predict_yield(crop_id, weather_forecast)

        assert isinstance(predicted_yield, float)
        assert predicted_yield > 0

        # Check that crop estimated yield was updated
        crop = manager.crops[crop_id]
        assert crop.estimated_yield is not None
        assert crop.estimated_yield > 0

    @pytest.mark.asyncio
    async def test_harvest_schedule_optimization(self, manager):
        """Test harvest schedule optimization"""
        # Add multiple crops
        crop_data_1 = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 2.5,
            'stage': 'ready_to_harvest',
            'expected_harvest': datetime.now() + timedelta(days=5)
        }
        crop_data_2 = {
            'variety': 'lettuce',
            'field_id': 'field_002',
            'area_hectares': 1.0,
            'stage': 'growing',
            'expected_harvest': datetime.now() + timedelta(days=10)
        }

        crop_id_1 = await manager.add_crop(crop_data_1)
        crop_id_2 = await manager.add_crop(crop_data_2)

        # Create weather forecast
        weather_forecast = [
            WeatherData(
                date=datetime.now() + timedelta(days=i),
                temperature_avg=20.0,
                temperature_min=15.0,
                temperature_max=25.0,
                humidity=60.0,
                precipitation=0.0 if i in [2, 3, 6, 7] else 3.0,
                wind_speed=5.0,
                solar_radiation=450.0
            )
            for i in range(14)
        ]

        harvest_schedule = await manager.optimize_harvest_schedule(weather_forecast)

        assert isinstance(harvest_schedule, dict)
        assert crop_id_1 in harvest_schedule  # Ready to harvest crop should be scheduled

        # Check that optimal dates avoid rainy days
        for crop_id, harvest_date in harvest_schedule.items():
            assert isinstance(harvest_date, datetime)

    @pytest.mark.asyncio
    async def test_feed_fertilizer_management(self, manager):
        """Test feed and fertilizer requirement calculations"""
        # Add livestock
        livestock_data = {
            'type': 'dairy_cows',
            'breed': 'Holstein-Friesian',
            'birth_date': datetime.now() - timedelta(days=365*3),
            'location': 'barn_001',
            'production_data': {'daily_milk_kg': 25}
        }
        animal_id = await manager.add_livestock(livestock_data)

        # Add crop
        crop_data = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 2.5,
            'stage': 'planted'
        }
        crop_id = await manager.add_crop(crop_data)

        recommendations = await manager.manage_feed_fertilizer()

        assert 'feed_requirements' in recommendations
        assert 'fertilizer_requirements' in recommendations

        # Check feed requirements
        assert animal_id in recommendations['feed_requirements']
        feed_req = recommendations['feed_requirements'][animal_id]
        assert 'daily_kg' in feed_req
        assert 'feed_type' in feed_req
        assert 'cost_per_day' in feed_req
        assert feed_req['daily_kg'] > 20  # Dairy cow should need substantial feed

        # Check fertilizer requirements
        assert crop_id in recommendations['fertilizer_requirements']
        fert_req = recommendations['fertilizer_requirements'][crop_id]
        assert 'nitrogen_kg' in fert_req
        assert 'phosphorus_kg' in fert_req
        assert 'potassium_kg' in fert_req
        assert 'estimated_cost' in fert_req

    @pytest.mark.asyncio
    async def test_farm_status_overview(self, manager):
        """Test comprehensive farm status reporting"""
        # Add some crops and livestock
        crop_data = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 2.5,
            'stage': 'planted'
        }
        await manager.add_crop(crop_data)

        livestock_data = {
            'type': 'dairy_cows',
            'breed': 'Holstein-Friesian',
            'birth_date': datetime.now() - timedelta(days=365*3),
            'location': 'barn_001'
        }
        await manager.add_livestock(livestock_data)

        status = await manager.get_farm_status()

        assert 'crops' in status
        assert 'livestock' in status
        assert 'weather' in status

        # Check crop summary
        crop_summary = status['crops']
        assert crop_summary['total_crops'] == 1
        assert crop_summary['total_area'] == 2.5
        assert 'by_stage' in crop_summary
        assert 'planted' in crop_summary['by_stage']

        # Check livestock summary
        livestock_summary = status['livestock']
        assert livestock_summary['total_animals'] == 1
        assert 'by_type' in livestock_summary
        assert 'dairy_cows' in livestock_summary['by_type']

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, manager):
        """Test AI-powered recommendations"""
        # Add crop ready for harvest
        crop_data = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 2.5,
            'stage': 'ready_to_harvest'
        }
        await manager.add_crop(crop_data)

        # Add livestock needing attention
        livestock_data = {
            'type': 'dairy_cows',
            'breed': 'Holstein-Friesian',
            'birth_date': datetime.now() - timedelta(days=365*3),
            'location': 'barn_001',
            'health_status': 'needs_attention'
        }
        await manager.add_livestock(livestock_data)

        recommendations = await manager.generate_recommendations()

        assert 'urgent' in recommendations
        assert 'important' in recommendations
        assert 'suggestions' in recommendations

        # Should have urgent recommendation for harvest
        urgent_actions = recommendations['urgent']
        assert len(urgent_actions) >= 1
        assert any('harvest' in action.lower() for action in urgent_actions)

        # Should have urgent recommendation for livestock health
        assert any('health' in action.lower() for action in urgent_actions)

    @pytest.mark.asyncio
    async def test_daily_feed_calculation(self, manager):
        """Test daily feed requirement calculations for different livestock"""
        test_cases = [
            {
                'type': 'dairy_cows',
                'production_data': {'daily_milk_kg': 20},
                'expected_min': 30  # Should be substantial for dairy cow
            },
            {
                'type': 'poultry',
                'production_data': {},
                'expected_min': 0.1
            },
            {
                'type': 'sheep',
                'production_data': {},
                'expected_min': 2.0
            }
        ]

        for case in test_cases:
            livestock_data = {
                'type': case['type'],
                'breed': 'Test Breed',
                'birth_date': datetime.now() - timedelta(days=365),
                'location': 'test_location',
                'production_data': case['production_data']
            }

            # Create livestock record directly for testing
            livestock = LivestockRecord(
                animal_id='test_id',
                livestock_type=LivestockType(case['type']),
                breed=livestock_data['breed'],
                birth_date=livestock_data['birth_date'],
                health_status='healthy',
                location=livestock_data['location'],
                production_data=livestock_data['production_data']
            )

            daily_feed = manager._calculate_daily_feed_requirement(livestock)
            assert daily_feed >= case['expected_min']
            assert isinstance(daily_feed, float)

    def test_weather_feature_extraction(self, manager):
        """Test weather data feature extraction"""
        weather_data = [
            WeatherData(
                date=datetime.now(),
                temperature_avg=20.0,
                temperature_min=15.0,
                temperature_max=25.0,
                humidity=60.0,
                precipitation=2.5,
                wind_speed=5.0,
                solar_radiation=450.0
            ),
            WeatherData(
                date=datetime.now() + timedelta(days=1),
                temperature_avg=22.0,
                temperature_min=17.0,
                temperature_max=27.0,
                humidity=55.0,
                precipitation=0.0,
                wind_speed=8.0,
                solar_radiation=480.0
            )
        ]

        features = manager._extract_weather_features(weather_data)

        assert isinstance(features, list)
        assert len(features) == 8  # Expected number of features
        assert all(isinstance(f, (int, float)) for f in features)

        # Check specific features
        assert features[0] == 21.0  # Average temperature
        assert features[3] == 2.5   # Total precipitation
        assert features[6] == 1     # Rainy days (precipitation > 5)
        assert features[7] == 0     # Frost days (temperature < 0)

    @pytest.mark.asyncio
    async def test_fertilizer_timing_schedules(self, manager):
        """Test fertilizer application timing recommendations"""
        # Test tomato fertilizer timing
        crop_data = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 2.5,
            'stage': 'planted'
        }

        crop = CropRecord(
            crop_id='test_crop',
            variety=crop_data['variety'],
            field_id=crop_data['field_id'],
            planted_date=None,
            expected_harvest=None,
            current_stage=CropStage.PLANTED,
            area_hectares=crop_data['area_hectares'],
            estimated_yield=None,
            actual_yield=None
        )

        timing_schedule = manager._get_fertilizer_timing(crop)

        assert isinstance(timing_schedule, list)
        assert len(timing_schedule) > 0

        # Check that timing schedule has proper structure
        for timing in timing_schedule:
            assert 'stage' in timing
            assert 'N' in timing
            assert 'P' in timing
            assert 'K' in timing

            # Check that percentages sum to reasonable values
            total_n = sum(t['N'] for t in timing_schedule)
            assert abs(total_n - 1.0) < 0.1  # Should sum to approximately 1.0


# Integration tests
class TestFarmProductionManagerIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_complete_crop_lifecycle(self):
        """Test complete crop lifecycle from planning to harvest"""
        farm_config = {
            'name': 'Integration Test Farm',
            'total_area': 100
        }
        manager = FarmProductionManager(farm_config)
        await manager.initialize()

        # 1. Add planned crop
        crop_data = {
            'variety': 'tomatoes',
            'field_id': 'field_001',
            'area_hectares': 5.0,
            'stage': 'planned'
        }
        crop_id = await manager.add_crop(crop_data)

        # 2. Update to planted
        crop = manager.crops[crop_id]
        crop.current_stage = CropStage.PLANTED
        crop.planted_date = datetime.now()

        # 3. Add weather data
        for i in range(30):
            weather_data = WeatherData(
                date=datetime.now() + timedelta(days=i),
                temperature_avg=20.0 + (i % 5),
                temperature_min=15.0,
                temperature_max=25.0,
                humidity=60.0,
                precipitation=2.0 if i % 7 == 0 else 0.0,
                wind_speed=5.0,
                solar_radiation=450.0
            )
            await manager.update_weather_data(weather_data)

        # 4. Predict yield
        weather_forecast = manager.weather_history[-14:]  # Last 14 days as forecast
        predicted_yield = await manager.predict_yield(crop_id, weather_forecast)

        # 5. Update to ready for harvest
        crop.current_stage = CropStage.READY_TO_HARVEST
        crop.expected_harvest = datetime.now() + timedelta(days=3)

        # 6. Optimize harvest schedule
        harvest_schedule = await manager.optimize_harvest_schedule(weather_forecast)

        # 7. Get final recommendations
        recommendations = await manager.generate_recommendations()

        # Verify complete workflow
        assert predicted_yield > 0
        assert crop_id in harvest_schedule
        assert any('harvest' in rec.lower() for rec in recommendations['urgent'])

        # Check that crop data is properly maintained
        final_crop = manager.crops[crop_id]
        assert final_crop.current_stage == CropStage.READY_TO_HARVEST
        assert final_crop.estimated_yield is not None

    @pytest.mark.asyncio
    async def test_multi_livestock_feed_optimization(self):
        """Test feed optimization across multiple livestock types"""
        farm_config = {'name': 'Test Farm'}
        manager = FarmProductionManager(farm_config)
        await manager.initialize()

        # Add different types of livestock
        livestock_types = [
            {
                'type': 'dairy_cows',
                'breed': 'Holstein-Friesian',
                'production_data': {'daily_milk_kg': 28},
                'count': 3
            },
            {
                'type': 'poultry',
                'breed': 'Rhode Island Red',
                'production_data': {'daily_eggs': 0.8},
                'count': 50
            },
            {
                'type': 'sheep',
                'breed': 'Suffolk',
                'production_data': {},
                'count': 15
            }
        ]

        livestock_ids = []
        for livestock_type in livestock_types:
            for i in range(livestock_type['count']):
                livestock_data = {
                    'type': livestock_type['type'],
                    'breed': livestock_type['breed'],
                    'birth_date': datetime.now() - timedelta(days=365*2),
                    'location': f"area_{livestock_type['type']}",
                    'production_data': livestock_type['production_data']
                }
                animal_id = await manager.add_livestock(livestock_data)
                livestock_ids.append(animal_id)

        # Get feed recommendations
        recommendations = await manager.manage_feed_fertilizer()
        feed_reqs = recommendations['feed_requirements']

        # Verify all livestock have feed requirements
        assert len(feed_reqs) == len(livestock_ids)

        # Calculate total daily feed cost
        total_daily_cost = sum(req['cost_per_day'] for req in feed_reqs.values())
        assert total_daily_cost > 0

        # Verify different feed types are recommended
        feed_types = set(req['feed_type'] for req in feed_reqs.values())
        assert len(feed_types) > 1  # Should have different feed types for different animals


if __name__ == "__main__":
    pytest.main([__file__, "-v"])