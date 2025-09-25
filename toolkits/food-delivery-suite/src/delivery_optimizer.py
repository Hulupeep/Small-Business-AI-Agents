"""
Delivery Optimization AI Agent

Handles route planning, driver assignment, and delivery management
with real-time optimization and customer communication.
"""

import asyncio
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DriverStatus(Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    PICKING_UP = "picking_up"
    DELIVERING = "delivering"
    RETURNING = "returning"
    OFFLINE = "offline"

class DeliveryStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"

@dataclass
class Location:
    latitude: float
    longitude: float
    address: str

    def distance_to(self, other: 'Location') -> float:
        """Calculate distance in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (math.sin(dlat/2)**2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

@dataclass
class Driver:
    id: str
    name: str
    phone: str
    current_location: Location
    status: DriverStatus
    vehicle_type: str  # bike, scooter, car
    capacity: int  # max orders
    current_orders: List[str]
    rating: float
    total_deliveries: int
    earnings_today: float

@dataclass
class DeliveryOrder:
    order_id: str
    customer_location: Location
    customer_name: str
    customer_phone: str
    items_count: int
    total_value: float
    special_instructions: str
    ready_time: datetime
    target_delivery_time: datetime
    priority: int
    status: DeliveryStatus
    driver_id: Optional[str] = None
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None

@dataclass
class DeliveryRoute:
    driver_id: str
    orders: List[DeliveryOrder]
    total_distance: float
    estimated_time: int  # minutes
    efficiency_score: float

class DeliveryOptimizer:
    """
    AI-powered delivery optimization system that handles route planning,
    driver assignment, and real-time delivery management.
    """

    def __init__(self, restaurant_location: Location):
        self.restaurant_location = restaurant_location
        self.drivers: Dict[str, Driver] = {}
        self.delivery_orders: Dict[str, DeliveryOrder] = {}
        self.active_routes: Dict[str, DeliveryRoute] = {}
        self.delivery_zones = {}
        self.surge_multiplier = 1.0
        self.peak_hours = [12, 13, 18, 19, 20]  # Default peak hours

    def add_driver(self, driver: Driver) -> None:
        """Add a driver to the system"""
        self.drivers[driver.id] = driver
        logger.info(f"Added driver {driver.name} ({driver.id})")

    def remove_driver(self, driver_id: str) -> None:
        """Remove a driver from the system"""
        if driver_id in self.drivers:
            del self.drivers[driver_id]
            logger.info(f"Removed driver {driver_id}")

    def update_driver_location(self, driver_id: str, location: Location) -> None:
        """Update driver's current location"""
        if driver_id in self.drivers:
            self.drivers[driver_id].current_location = location

    def add_delivery_order(self, order: DeliveryOrder) -> None:
        """Add a new delivery order to the system"""
        self.delivery_orders[order.order_id] = order
        logger.info(f"Added delivery order {order.order_id}")

    def calculate_route_optimization(self, orders: List[DeliveryOrder],
                                   driver: Driver) -> DeliveryRoute:
        """
        Calculate optimal route for multiple orders using AI algorithms
        """
        if not orders:
            return DeliveryRoute(driver.id, [], 0, 0, 0)

        # Start from restaurant location
        current_location = self.restaurant_location
        optimized_orders = []
        remaining_orders = orders.copy()
        total_distance = 0
        total_time = 0

        while remaining_orders:
            # Find next best order based on multiple factors
            best_order = self._find_next_best_order(
                current_location, remaining_orders, driver
            )

            optimized_orders.append(best_order)
            remaining_orders.remove(best_order)

            # Calculate distance and time to this order
            distance = current_location.distance_to(best_order.customer_location)
            travel_time = self._calculate_travel_time(distance, driver.vehicle_type)

            total_distance += distance
            total_time += travel_time + 3  # 3 minutes for delivery

            current_location = best_order.customer_location

        # Calculate return distance to restaurant
        return_distance = current_location.distance_to(self.restaurant_location)
        total_distance += return_distance
        total_time += self._calculate_travel_time(return_distance, driver.vehicle_type)

        # Calculate efficiency score
        efficiency_score = self._calculate_efficiency_score(
            optimized_orders, total_distance, total_time
        )

        return DeliveryRoute(
            driver_id=driver.id,
            orders=optimized_orders,
            total_distance=total_distance,
            estimated_time=total_time,
            efficiency_score=efficiency_score
        )

    def _find_next_best_order(self, current_location: Location,
                            orders: List[DeliveryOrder],
                            driver: Driver) -> DeliveryOrder:
        """Find the next best order to deliver based on multiple factors"""
        scores = {}

        for order in orders:
            score = 0

            # Distance factor (closer is better)
            distance = current_location.distance_to(order.customer_location)
            distance_score = max(0, 10 - distance)  # Max 10 points for very close
            score += distance_score * 0.3

            # Priority factor
            score += order.priority * 0.25

            # Time urgency factor
            time_until_target = (order.target_delivery_time - datetime.now()).total_seconds() / 60
            if time_until_target < 30:  # Less than 30 minutes
                score += 5
            elif time_until_target < 60:  # Less than 1 hour
                score += 3

            # Order value factor (higher value orders get slight priority)
            if order.total_value > 50:
                score += 2
            elif order.total_value > 30:
                score += 1

            scores[order.order_id] = score

        # Return order with highest score
        best_order_id = max(scores, key=scores.get)
        return next(order for order in orders if order.order_id == best_order_id)

    def _calculate_travel_time(self, distance_km: float, vehicle_type: str) -> int:
        """Calculate travel time based on distance and vehicle type"""
        speeds = {
            'bike': 15,      # km/h
            'scooter': 25,   # km/h
            'car': 30        # km/h in city traffic
        }

        speed = speeds.get(vehicle_type, 20)
        time_hours = distance_km / speed
        return int(time_hours * 60)  # Convert to minutes

    def _calculate_efficiency_score(self, orders: List[DeliveryOrder],
                                  total_distance: float,
                                  total_time: int) -> float:
        """Calculate route efficiency score"""
        if not orders:
            return 0

        # Base score from number of orders
        base_score = len(orders) * 10

        # Distance efficiency (less distance per order is better)
        distance_per_order = total_distance / len(orders)
        distance_penalty = distance_per_order * 2

        # Time efficiency (less time per order is better)
        time_per_order = total_time / len(orders)
        time_penalty = time_per_order * 0.5

        # Calculate final score
        efficiency_score = max(0, base_score - distance_penalty - time_penalty)
        return round(efficiency_score, 2)

    async def assign_optimal_driver(self, order: DeliveryOrder) -> Optional[str]:
        """Assign the best available driver for an order"""
        available_drivers = [
            driver for driver in self.drivers.values()
            if driver.status == DriverStatus.AVAILABLE and
               len(driver.current_orders) < driver.capacity
        ]

        if not available_drivers:
            logger.warning("No available drivers for order assignment")
            return None

        best_driver = None
        best_score = -1

        for driver in available_drivers:
            score = self._calculate_driver_score(driver, order)
            if score > best_score:
                best_score = score
                best_driver = driver

        if best_driver:
            # Assign order to driver
            order.driver_id = best_driver.id
            order.status = DeliveryStatus.ASSIGNED
            best_driver.current_orders.append(order.order_id)
            best_driver.status = DriverStatus.ASSIGNED

            # Create or update route
            await self._update_driver_route(best_driver.id)

            logger.info(f"Assigned order {order.order_id} to driver {best_driver.name}")
            return best_driver.id

        return None

    def _calculate_driver_score(self, driver: Driver, order: DeliveryOrder) -> float:
        """Calculate how suitable a driver is for an order"""
        score = 0

        # Distance factor (closer driver is better)
        distance = driver.current_location.distance_to(order.customer_location)
        distance_score = max(0, 10 - distance)
        score += distance_score * 0.4

        # Driver rating factor
        score += driver.rating * 2

        # Driver availability factor (fewer current orders is better)
        availability_score = (driver.capacity - len(driver.current_orders)) * 2
        score += availability_score * 0.3

        # Vehicle type factor for distance
        vehicle_bonus = {
            'car': 3 if distance > 5 else 1,
            'scooter': 2,
            'bike': 3 if distance < 3 else 1
        }
        score += vehicle_bonus.get(driver.vehicle_type, 1)

        return score

    async def _update_driver_route(self, driver_id: str) -> None:
        """Update and optimize driver's current route"""
        driver = self.drivers[driver_id]

        # Get all assigned orders for this driver
        driver_orders = [
            self.delivery_orders[order_id]
            for order_id in driver.current_orders
            if order_id in self.delivery_orders
        ]

        # Calculate optimal route
        optimal_route = self.calculate_route_optimization(driver_orders, driver)
        self.active_routes[driver_id] = optimal_route

        # Send route to driver
        await self._send_route_to_driver(driver_id, optimal_route)

    async def _send_route_to_driver(self, driver_id: str, route: DeliveryRoute) -> None:
        """Send optimized route to driver's app"""
        route_data = {
            'driver_id': driver_id,
            'total_orders': len(route.orders),
            'estimated_time': route.estimated_time,
            'total_distance': route.total_distance,
            'stops': [
                {
                    'order_id': order.order_id,
                    'customer_name': order.customer_name,
                    'address': order.customer_location.address,
                    'phone': order.customer_phone,
                    'special_instructions': order.special_instructions
                }
                for order in route.orders
            ]
        }

        # In real implementation, send to driver's mobile app
        logger.info(f"Route sent to driver {driver_id}: {route_data}")

    async def update_delivery_status(self, order_id: str,
                                   status: DeliveryStatus,
                                   location: Optional[Location] = None) -> None:
        """Update delivery status and send notifications"""
        if order_id not in self.delivery_orders:
            return

        order = self.delivery_orders[order_id]
        old_status = order.status
        order.status = status

        # Update timestamps
        if status == DeliveryStatus.PICKED_UP:
            order.pickup_time = datetime.now()
        elif status == DeliveryStatus.DELIVERED:
            order.delivery_time = datetime.now()

        # Send customer notification
        await self._send_delivery_notification(order, status)

        # Update driver status if needed
        if order.driver_id and status == DeliveryStatus.DELIVERED:
            await self._handle_delivery_completion(order)

        logger.info(f"Delivery {order_id}: {old_status.value} -> {status.value}")

    async def _send_delivery_notification(self, order: DeliveryOrder,
                                        status: DeliveryStatus) -> None:
        """Send delivery status notification to customer"""
        messages = {
            DeliveryStatus.ASSIGNED: f"Your order is assigned to our driver. ETA: {self._calculate_eta(order)}",
            DeliveryStatus.PICKED_UP: "Your order has been picked up and is on the way!",
            DeliveryStatus.IN_TRANSIT: f"Your driver is on the way. ETA: {self._calculate_eta(order)}",
            DeliveryStatus.DELIVERED: "Your order has been delivered. Enjoy your meal!"
        }

        if status in messages:
            message = messages[status]
            # In real implementation, send SMS/push notification
            logger.info(f"Customer notification ({order.customer_phone}): {message}")

    def _calculate_eta(self, order: DeliveryOrder) -> str:
        """Calculate estimated time of arrival"""
        if not order.driver_id or order.driver_id not in self.drivers:
            return "Calculating..."

        driver = self.drivers[order.driver_id]
        distance = driver.current_location.distance_to(order.customer_location)
        travel_time = self._calculate_travel_time(distance, driver.vehicle_type)

        eta = datetime.now() + timedelta(minutes=travel_time)
        return eta.strftime("%H:%M")

    async def _handle_delivery_completion(self, order: DeliveryOrder) -> None:
        """Handle completion of a delivery"""
        if not order.driver_id:
            return

        driver = self.drivers[order.driver_id]

        # Remove order from driver's current orders
        if order.order_id in driver.current_orders:
            driver.current_orders.remove(order.order_id)

        # Update driver earnings
        delivery_fee = self._calculate_delivery_fee(order)
        driver.earnings_today += delivery_fee
        driver.total_deliveries += 1

        # Update driver status
        if not driver.current_orders:
            driver.status = DriverStatus.AVAILABLE

        # Update route
        await self._update_driver_route(order.driver_id)

    def _calculate_delivery_fee(self, order: DeliveryOrder) -> float:
        """Calculate delivery fee for driver"""
        base_fee = 3.50

        # Distance bonus
        if order.driver_id:
            driver = self.drivers[order.driver_id]
            distance = self.restaurant_location.distance_to(order.customer_location)
            distance_bonus = distance * 0.50
        else:
            distance_bonus = 0

        # Surge multiplier
        surge_bonus = base_fee * (self.surge_multiplier - 1)

        return round(base_fee + distance_bonus + surge_bonus, 2)

    def set_surge_pricing(self, multiplier: float) -> None:
        """Set surge pricing multiplier"""
        self.surge_multiplier = max(1.0, multiplier)
        logger.info(f"Surge pricing set to {multiplier}x")

    def get_delivery_analytics(self) -> Dict[str, Any]:
        """Get comprehensive delivery analytics"""
        total_deliveries = len(self.delivery_orders)
        completed_deliveries = len([
            order for order in self.delivery_orders.values()
            if order.status == DeliveryStatus.DELIVERED
        ])

        if total_deliveries == 0:
            return {}

        # Calculate average delivery time
        completed_orders = [
            order for order in self.delivery_orders.values()
            if order.delivery_time and order.pickup_time
        ]

        avg_delivery_time = 0
        if completed_orders:
            total_time = sum([
                (order.delivery_time - order.pickup_time).total_seconds() / 60
                for order in completed_orders
            ])
            avg_delivery_time = total_time / len(completed_orders)

        # Driver performance
        driver_stats = {}
        for driver in self.drivers.values():
            driver_stats[driver.id] = {
                'name': driver.name,
                'total_deliveries': driver.total_deliveries,
                'earnings_today': driver.earnings_today,
                'rating': driver.rating,
                'current_orders': len(driver.current_orders)
            }

        return {
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'completion_rate': (completed_deliveries / total_deliveries * 100),
            'average_delivery_time': round(avg_delivery_time, 1),
            'active_drivers': len([d for d in self.drivers.values() if d.status != DriverStatus.OFFLINE]),
            'surge_multiplier': self.surge_multiplier,
            'driver_performance': driver_stats
        }

# Example usage
if __name__ == "__main__":
    async def demo():
        # Restaurant location (Dublin city center)
        restaurant = Location(53.3498, -6.2603, "123 Main St, Dublin 1")

        optimizer = DeliveryOptimizer(restaurant)

        # Add sample driver
        driver = Driver(
            id="driver_001",
            name="John Smith",
            phone="+353 87 123 4567",
            current_location=Location(53.3505, -6.2610, "Near restaurant"),
            status=DriverStatus.AVAILABLE,
            vehicle_type="scooter",
            capacity=3,
            current_orders=[],
            rating=4.8,
            total_deliveries=245,
            earnings_today=67.50
        )

        optimizer.add_driver(driver)

        # Add sample delivery order
        order = DeliveryOrder(
            order_id="ORD_001",
            customer_location=Location(53.3520, -6.2650, "456 Customer St, Dublin 1"),
            customer_name="Alice Johnson",
            customer_phone="+353 87 987 6543",
            items_count=2,
            total_value=28.50,
            special_instructions="Ring doorbell twice",
            ready_time=datetime.now(),
            target_delivery_time=datetime.now() + timedelta(minutes=30),
            priority=3,
            status=DeliveryStatus.PENDING
        )

        optimizer.add_delivery_order(order)

        # Assign driver
        assigned_driver = await optimizer.assign_optimal_driver(order)
        print(f"Assigned driver: {assigned_driver}")

        # Update delivery status
        await optimizer.update_delivery_status(order.order_id, DeliveryStatus.PICKED_UP)
        await optimizer.update_delivery_status(order.order_id, DeliveryStatus.DELIVERED)

        # Get analytics
        analytics = optimizer.get_delivery_analytics()
        print(f"Analytics: {analytics}")

    asyncio.run(demo())