"""
Bar & Table Service Manager Agent
Streamlines front-of-house operations and customer service for traditional pubs
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class TableStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"

class OrderStatus(Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"

@dataclass
class Table:
    number: int
    capacity: int
    status: TableStatus = TableStatus.AVAILABLE
    current_party_size: int = 0
    reservation_time: Optional[datetime] = None
    last_cleaned: Optional[datetime] = None
    estimated_turnover: Optional[datetime] = None

@dataclass
class Order:
    id: str
    table_number: int
    items: List[Dict]
    order_time: datetime
    status: OrderStatus = OrderStatus.PENDING
    kitchen_time: Optional[datetime] = None
    ready_time: Optional[datetime] = None
    special_requests: List[str] = field(default_factory=list)

@dataclass
class Tab:
    id: str
    table_number: int
    items: List[Dict] = field(default_factory=list)
    total: float = 0.0
    payments: List[Dict] = field(default_factory=list)
    split_requests: List[Dict] = field(default_factory=list)
    opened_at: datetime = field(default_factory=datetime.now)

class BarTableManager:
    """AI agent for managing bar and table service operations"""

    def __init__(self, pub_config: Dict):
        self.pub_config = pub_config
        self.tables: Dict[int, Table] = self._initialize_tables()
        self.active_orders: Dict[str, Order] = {}
        self.active_tabs: Dict[str, Tab] = {}
        self.reservation_system = ReservationSystem()
        self.menu_intelligence = MenuIntelligence()

    def _initialize_tables(self) -> Dict[int, Table]:
        """Initialize pub table configuration"""
        tables = {}
        table_config = self.pub_config.get('tables', [])

        for config in table_config:
            table = Table(
                number=config['number'],
                capacity=config['capacity']
            )
            tables[config['number']] = table

        return tables

    async def manage_table_booking(self, party_size: int,
                                 preferred_time: Optional[datetime] = None,
                                 duration_estimate: int = 90) -> Dict:
        """Smart table allocation with optimization"""

        if preferred_time is None:
            preferred_time = datetime.now()

        # Find optimal table
        suitable_tables = [
            table for table in self.tables.values()
            if table.capacity >= party_size and
            table.capacity <= party_size + 2  # Avoid oversized tables
        ]

        if not suitable_tables:
            return {
                'success': False,
                'message': 'No suitable tables available',
                'alternative_times': await self._suggest_alternative_times(party_size)
            }

        # Check availability at preferred time
        available_table = None
        for table in suitable_tables:
            if await self._is_table_available(table.number, preferred_time, duration_estimate):
                available_table = table
                break

        if available_table:
            # Make reservation
            available_table.status = TableStatus.RESERVED
            available_table.reservation_time = preferred_time
            available_table.current_party_size = party_size
            available_table.estimated_turnover = preferred_time + timedelta(minutes=duration_estimate)

            return {
                'success': True,
                'table_number': available_table.number,
                'time': preferred_time,
                'estimated_duration': duration_estimate,
                'confirmation_code': self._generate_confirmation_code()
            }

        return {
            'success': False,
            'message': 'Table not available at preferred time',
            'alternative_times': await self._suggest_alternative_times(party_size)
        }

    async def coordinate_food_orders(self, table_number: int, order_items: List[Dict]) -> Dict:
        """Coordinate food orders with kitchen timing"""

        order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{table_number}"

        # Analyze order complexity and timing
        kitchen_time = await self.menu_intelligence.estimate_preparation_time(order_items)

        order = Order(
            id=order_id,
            table_number=table_number,
            items=order_items,
            order_time=datetime.now(),
            kitchen_time=kitchen_time
        )

        # Check if drinks should be served first
        drinks_first = await self._should_serve_drinks_first(order_items)

        # Send to kitchen with timing instructions
        kitchen_instruction = {
            'order_id': order_id,
            'table_number': table_number,
            'items': order_items,
            'estimated_time': kitchen_time,
            'drinks_first': drinks_first,
            'special_instructions': await self._generate_kitchen_notes(order_items)
        }

        self.active_orders[order_id] = order

        return {
            'order_id': order_id,
            'estimated_ready_time': datetime.now() + kitchen_time,
            'kitchen_instruction': kitchen_instruction,
            'drinks_served_first': drinks_first
        }

    async def manage_tab_system(self, table_number: int, action: str, **kwargs) -> Dict:
        """Handle tab creation, updates, and payment processing"""

        tab_id = f"TAB_{table_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if action == 'open_tab':
            tab = Tab(
                id=tab_id,
                table_number=table_number
            )
            self.active_tabs[tab_id] = tab

            return {
                'tab_id': tab_id,
                'status': 'opened',
                'table_number': table_number
            }

        elif action == 'add_items':
            tab = self._get_active_tab(table_number)
            if tab:
                items = kwargs.get('items', [])
                tab.items.extend(items)
                tab.total += sum(item.get('price', 0) for item in items)

                return {
                    'tab_id': tab.id,
                    'items_added': len(items),
                    'new_total': tab.total
                }

        elif action == 'split_bill':
            return await self._handle_split_bill(table_number, kwargs)

        elif action == 'process_payment':
            return await self._process_payment(table_number, kwargs)

        return {'error': 'Invalid action'}

    async def last_orders_management(self) -> Dict:
        """Manage last orders timing and announcements"""

        current_time = datetime.now()
        pub_hours = self.pub_config.get('operating_hours', {})

        # Determine last orders time based on day and season
        last_orders_time = await self._calculate_last_orders_time(current_time, pub_hours)

        if current_time >= last_orders_time:
            # Trigger last orders announcements
            announcements = await self._generate_last_orders_announcements()

            # Update table statuses
            for table in self.tables.values():
                if table.status == TableStatus.OCCUPIED:
                    table.estimated_turnover = current_time + timedelta(minutes=30)

            return {
                'last_orders_active': True,
                'announcements': announcements,
                'estimated_closure': current_time + timedelta(minutes=45)
            }

        return {
            'last_orders_active': False,
            'time_until_last_orders': (last_orders_time - current_time).total_seconds() / 60
        }

    async def handle_split_payments(self, table_number: int, split_config: Dict) -> Dict:
        """Intelligent split bill handling"""

        tab = self._get_active_tab(table_number)
        if not tab:
            return {'error': 'No active tab found'}

        split_type = split_config.get('type', 'equal')

        if split_type == 'equal':
            return await self._split_equally(tab, split_config.get('number_of_people', 2))

        elif split_type == 'by_items':
            return await self._split_by_items(tab, split_config.get('item_assignments', {}))

        elif split_type == 'custom':
            return await self._split_custom(tab, split_config.get('amounts', []))

        return {'error': 'Invalid split type'}

    async def _is_table_available(self, table_number: int, time: datetime, duration: int) -> bool:
        """Check if table is available at specific time"""
        table = self.tables.get(table_number)
        if not table:
            return False

        # Check current status
        if table.status == TableStatus.OCCUPIED:
            if table.estimated_turnover and table.estimated_turnover > time:
                return False

        # Check for existing reservations
        # Implementation would check reservation database
        return True

    async def _suggest_alternative_times(self, party_size: int) -> List[Dict]:
        """Suggest alternative booking times"""
        alternatives = []
        current_time = datetime.now()

        # Check next 4 hours in 30-minute intervals
        for i in range(8):
            check_time = current_time + timedelta(minutes=30 * i)

            suitable_tables = [
                table for table in self.tables.values()
                if table.capacity >= party_size and
                await self._is_table_available(table.number, check_time, 90)
            ]

            if suitable_tables:
                alternatives.append({
                    'time': check_time,
                    'available_tables': len(suitable_tables),
                    'best_table': min(suitable_tables, key=lambda t: t.capacity).number
                })

        return alternatives[:3]  # Return top 3 alternatives

    def _get_active_tab(self, table_number: int) -> Optional[Tab]:
        """Get active tab for table"""
        for tab in self.active_tabs.values():
            if tab.table_number == table_number:
                return tab
        return None

    def _generate_confirmation_code(self) -> str:
        """Generate booking confirmation code"""
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class ReservationSystem:
    """Handles reservation management and optimization"""

    async def optimize_table_allocation(self, reservations: List[Dict]) -> Dict:
        """Optimize table allocation to maximize turnover"""
        # Implementation for table optimization algorithm
        pass


class MenuIntelligence:
    """Provides intelligent menu analysis and timing"""

    async def estimate_preparation_time(self, items: List[Dict]) -> timedelta:
        """Estimate food preparation time based on menu items"""

        base_times = {
            'soup': 5,
            'salad': 8,
            'sandwich': 10,
            'fish_chips': 15,
            'steak': 20,
            'roast': 25
        }

        max_time = 0
        for item in items:
            item_type = item.get('category', 'default')
            prep_time = base_times.get(item_type, 12)
            max_time = max(max_time, prep_time)

        # Add buffer for kitchen coordination
        return timedelta(minutes=max_time + 3)


# Example usage and testing
if __name__ == "__main__":

    pub_config = {
        'tables': [
            {'number': 1, 'capacity': 2},
            {'number': 2, 'capacity': 4},
            {'number': 3, 'capacity': 6},
            {'number': 4, 'capacity': 8}
        ],
        'operating_hours': {
            'monday': {'open': '12:00', 'close': '23:00'},
            'friday': {'open': '12:00', 'close': '01:00'},
            'saturday': {'open': '12:00', 'close': '01:00'},
            'sunday': {'open': '12:00', 'close': '23:00'}
        }
    }

    async def test_manager():
        manager = BarTableManager(pub_config)

        # Test table booking
        booking_result = await manager.manage_table_booking(
            party_size=4,
            preferred_time=datetime.now() + timedelta(hours=2)
        )
        print("Booking result:", booking_result)

        # Test food order coordination
        order_items = [
            {'name': 'Fish & Chips', 'category': 'fish_chips', 'price': 14.50},
            {'name': 'Guinness Stew', 'category': 'stew', 'price': 16.00}
        ]

        order_result = await manager.coordinate_food_orders(2, order_items)
        print("Order result:", order_result)

    # Run test
    asyncio.run(test_manager())