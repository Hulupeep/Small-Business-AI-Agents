"""
Supply Chain Coordinator Agent
Streamlined B2B relationships and compliance tracking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from decimal import Decimal

logger = logging.getLogger(__name__)

class ClientType(Enum):
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    FOOD_PROCESSOR = "food_processor"
    RETAILER = "retailer"
    DISTRIBUTOR = "distributor"
    SCHOOL = "school"
    HOSPITAL = "hospital"

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PREPARATION = "in_preparation"
    READY_FOR_DELIVERY = "ready_for_delivery"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class DeliveryMethod(Enum):
    FARM_PICKUP = "farm_pickup"
    FARM_DELIVERY = "farm_delivery"
    THIRD_PARTY = "third_party"
    COURIER = "courier"

class CertificationType(Enum):
    ORGANIC = "organic"
    GAP = "gap"  # Good Agricultural Practices
    HACCP = "haccp"
    BRC = "brc"  # British Retail Consortium
    IFS = "ifs"  # International Featured Standards
    FAIR_TRADE = "fair_trade"
    RAINFOREST_ALLIANCE = "rainforest_alliance"

@dataclass
class B2BClient:
    client_id: str
    name: str
    client_type: ClientType
    contact_person: str
    email: str
    phone: str
    address: str
    payment_terms: int  # days
    preferred_delivery_days: List[int]  # 0=Monday, 6=Sunday
    minimum_order_value: Decimal
    volume_discount_threshold: Decimal
    volume_discount_percentage: float
    active: bool = True
    notes: str = ""

@dataclass
class TraceabilityRecord:
    record_id: str
    product_id: str
    batch_id: str
    field_id: str
    planted_date: datetime
    harvest_date: datetime
    processing_steps: List[Dict]
    storage_locations: List[Dict]
    certifications: List[CertificationType]
    quality_tests: List[Dict]
    destination_client: str

@dataclass
class B2BOrder:
    order_id: str
    client_id: str
    order_date: datetime
    requested_delivery_date: datetime
    items: List[Dict]
    total_amount: Decimal
    status: OrderStatus
    delivery_method: DeliveryMethod
    delivery_address: str
    special_instructions: str
    invoice_number: Optional[str] = None
    delivery_confirmation: Optional[datetime] = None

@dataclass
class DeliveryRoute:
    route_id: str
    delivery_date: datetime
    driver: str
    vehicle: str
    orders: List[str]  # order_ids
    optimized_sequence: List[Tuple[str, str]]  # (order_id, address)
    total_distance_km: float
    estimated_duration_hours: float
    fuel_cost: Decimal
    status: str = "planned"

class SupplyChainCoordinator:
    """
    Comprehensive supply chain management system for B2B relationships,
    traceability, compliance, and logistics optimization.
    """

    def __init__(self, farm_config: Dict):
        self.farm_config = farm_config
        self.clients: Dict[str, B2BClient] = {}
        self.orders: Dict[str, B2BOrder] = {}
        self.traceability_records: Dict[str, TraceabilityRecord] = {}
        self.delivery_routes: Dict[str, DeliveryRoute] = {}
        self.certifications: Dict[CertificationType, Dict] = {}
        self.contracts: Dict[str, Dict] = {}

    async def initialize(self):
        """Initialize the supply chain coordination system"""
        logger.info("Initializing Supply Chain Coordinator")
        await self._load_client_database()
        await self._setup_certification_tracking()
        await self._load_existing_contracts()
        logger.info("Supply Chain Coordinator initialized successfully")

    async def _load_client_database(self):
        """Load existing B2B client relationships"""
        # Sample clients - in production would load from database
        sample_clients = [
            {
                'name': 'Green Garden Restaurant',
                'client_type': ClientType.RESTAURANT,
                'contact_person': 'Chef Marco Rossi',
                'email': 'marco@greengardenrest.com',
                'phone': '+31205551234',
                'address': 'Prinsengracht 123, 1015 Amsterdam',
                'payment_terms': 30,
                'preferred_delivery_days': [1, 3, 5],  # Mon, Wed, Fri
                'minimum_order_value': Decimal('150.00'),
                'volume_discount_threshold': Decimal('500.00'),
                'volume_discount_percentage': 5.0
            },
            {
                'name': 'Hotel Europa',
                'client_type': ClientType.HOTEL,
                'contact_person': 'Anna van der Berg',
                'email': 'procurement@hoteleuropa.nl',
                'phone': '+31205556789',
                'address': 'Damrak 89, 1012 Amsterdam',
                'payment_terms': 21,
                'preferred_delivery_days': [0, 2, 4],  # Mon, Wed, Fri
                'minimum_order_value': Decimal('300.00'),
                'volume_discount_threshold': Decimal('1000.00'),
                'volume_discount_percentage': 8.0
            }
        ]

        for client_data in sample_clients:
            client_id = f"client_{uuid.uuid4().hex[:8]}"
            client = B2BClient(
                client_id=client_id,
                **client_data
            )
            self.clients[client_id] = client

        logger.info(f"Loaded {len(self.clients)} B2B clients")

    async def _setup_certification_tracking(self):
        """Setup certification tracking and compliance monitoring"""
        self.certifications = {
            CertificationType.ORGANIC: {
                'certificate_number': 'NL-BIO-01-004567',
                'issuing_body': 'SKAL Biocontrole',
                'valid_from': datetime(2024, 1, 1),
                'valid_until': datetime(2025, 12, 31),
                'scope': 'Vegetable production, dairy products',
                'inspection_date': datetime(2024, 6, 15),
                'next_inspection': datetime(2024, 12, 15)
            },
            CertificationType.GAP: {
                'certificate_number': 'GAP-NL-2024-789',
                'issuing_body': 'GlobalGAP',
                'valid_from': datetime(2024, 3, 1),
                'valid_until': datetime(2025, 2, 28),
                'scope': 'Crop production',
                'inspection_date': datetime(2024, 8, 20),
                'next_inspection': datetime(2025, 2, 20)
            }
        }

    async def _load_existing_contracts(self):
        """Load existing supply contracts"""
        # Sample contracts
        self.contracts = {
            'contract_001': {
                'client_id': list(self.clients.keys())[0] if self.clients else None,
                'contract_type': 'seasonal_supply',
                'start_date': datetime(2024, 4, 1),
                'end_date': datetime(2024, 10, 31),
                'products': ['organic_tomatoes', 'mixed_vegetables'],
                'minimum_weekly_volume': 50.0,
                'price_protection': True,
                'terms': 'Weekly delivery every Wednesday, payment NET 30'
            }
        }

    async def add_client(self, client_data: Dict) -> str:
        """Add new B2B client"""
        client_id = f"client_{uuid.uuid4().hex[:8]}"

        client = B2BClient(
            client_id=client_id,
            name=client_data['name'],
            client_type=ClientType(client_data['client_type']),
            contact_person=client_data['contact_person'],
            email=client_data['email'],
            phone=client_data['phone'],
            address=client_data['address'],
            payment_terms=client_data['payment_terms'],
            preferred_delivery_days=client_data['preferred_delivery_days'],
            minimum_order_value=Decimal(str(client_data['minimum_order_value'])),
            volume_discount_threshold=Decimal(str(client_data['volume_discount_threshold'])),
            volume_discount_percentage=client_data['volume_discount_percentage'],
            notes=client_data.get('notes', '')
        )

        self.clients[client_id] = client
        logger.info(f"Added B2B client {client_id}: {client.name}")
        return client_id

    async def create_order(self, order_data: Dict) -> str:
        """Create new B2B order"""
        order_id = f"order_{uuid.uuid4().hex[:8]}"

        client = self.clients.get(order_data['client_id'])
        if not client:
            raise ValueError(f"Client {order_data['client_id']} not found")

        # Calculate total amount
        total_amount = Decimal('0')
        for item in order_data['items']:
            item_total = Decimal(str(item['quantity'])) * Decimal(str(item['unit_price']))
            total_amount += item_total

        # Apply volume discount if applicable
        if total_amount >= client.volume_discount_threshold:
            discount = total_amount * Decimal(str(client.volume_discount_percentage / 100))
            total_amount -= discount

        order = B2BOrder(
            order_id=order_id,
            client_id=order_data['client_id'],
            order_date=datetime.now(),
            requested_delivery_date=datetime.fromisoformat(order_data['requested_delivery_date']),
            items=order_data['items'],
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            delivery_method=DeliveryMethod(order_data.get('delivery_method', 'farm_delivery')),
            delivery_address=order_data.get('delivery_address', client.address),
            special_instructions=order_data.get('special_instructions', '')
        )

        self.orders[order_id] = order
        logger.info(f"Created order {order_id} for client {client.name}: €{total_amount:.2f}")
        return order_id

    async def create_traceability_record(self, product_data: Dict) -> str:
        """Create comprehensive traceability record"""
        record_id = f"trace_{uuid.uuid4().hex[:8]}"

        # Determine applicable certifications
        applicable_certs = []
        if product_data.get('organic', False):
            applicable_certs.append(CertificationType.ORGANIC)
        applicable_certs.append(CertificationType.GAP)  # All products have GAP

        record = TraceabilityRecord(
            record_id=record_id,
            product_id=product_data['product_id'],
            batch_id=product_data['batch_id'],
            field_id=product_data['field_id'],
            planted_date=datetime.fromisoformat(product_data['planted_date']),
            harvest_date=datetime.fromisoformat(product_data['harvest_date']),
            processing_steps=product_data.get('processing_steps', []),
            storage_locations=product_data.get('storage_locations', []),
            certifications=applicable_certs,
            quality_tests=product_data.get('quality_tests', []),
            destination_client=product_data.get('destination_client', '')
        )

        self.traceability_records[record_id] = record
        logger.info(f"Created traceability record {record_id} for product {product_data['product_id']}")
        return record_id

    async def optimize_delivery_routes(self, delivery_date: datetime) -> str:
        """Optimize delivery routes for efficiency"""
        route_id = f"route_{delivery_date.strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"

        # Get all orders for delivery date
        orders_for_date = [
            order for order in self.orders.values()
            if (order.requested_delivery_date.date() == delivery_date.date() and
                order.status in [OrderStatus.CONFIRMED, OrderStatus.READY_FOR_DELIVERY])
        ]

        if not orders_for_date:
            return f"No orders for delivery on {delivery_date.date()}"

        # Simple route optimization (in production, use advanced algorithms)
        optimized_sequence = await self._calculate_optimal_route(orders_for_date)

        # Calculate route metrics
        total_distance = await self._calculate_total_distance(optimized_sequence)
        estimated_duration = total_distance / 45  # Assuming 45 km/h average speed
        fuel_cost = Decimal(str(total_distance * 0.15))  # €0.15 per km

        route = DeliveryRoute(
            route_id=route_id,
            delivery_date=delivery_date,
            driver="TBD",  # To be assigned
            vehicle="TBD",  # To be assigned
            orders=[order.order_id for order in orders_for_date],
            optimized_sequence=optimized_sequence,
            total_distance_km=total_distance,
            estimated_duration_hours=estimated_duration,
            fuel_cost=fuel_cost
        )

        self.delivery_routes[route_id] = route

        # Update order statuses
        for order in orders_for_date:
            order.status = OrderStatus.IN_PREPARATION

        logger.info(f"Optimized delivery route {route_id}: {len(orders_for_date)} orders, {total_distance:.1f}km")
        return route_id

    async def _calculate_optimal_route(self, orders: List[B2BOrder]) -> List[Tuple[str, str]]:
        """Calculate optimal delivery sequence (simplified)"""
        # In production, use advanced routing algorithms like Clarke-Wright or genetic algorithms
        farm_location = self.farm_config.get('address', 'Farm Location')

        # Simple nearest neighbor algorithm
        sequence = [(farm_location, farm_location)]  # Start at farm

        for order in orders:
            sequence.append((order.order_id, order.delivery_address))

        sequence.append((farm_location, farm_location))  # Return to farm

        return sequence

    async def _calculate_total_distance(self, sequence: List[Tuple[str, str]]) -> float:
        """Calculate total route distance (simplified)"""
        # In production, use actual mapping services like Google Maps API
        # For demo, assume average 15km between stops
        return len(sequence) * 15.0

    async def track_product_journey(self, product_id: str, batch_id: str) -> Dict:
        """Track complete product journey from field to customer"""
        # Find relevant traceability record
        record = None
        for tr_record in self.traceability_records.values():
            if tr_record.product_id == product_id and tr_record.batch_id == batch_id:
                record = tr_record
                break

        if not record:
            return {'error': f'No traceability record found for product {product_id}, batch {batch_id}'}

        journey = {
            'product_id': product_id,
            'batch_id': batch_id,
            'traceability_record_id': record.record_id,
            'timeline': [
                {
                    'date': record.planted_date.isoformat(),
                    'event': 'Planted',
                    'location': f"Field {record.field_id}",
                    'details': 'Seeds/seedlings planted'
                },
                {
                    'date': record.harvest_date.isoformat(),
                    'event': 'Harvested',
                    'location': f"Field {record.field_id}",
                    'details': 'Crop harvested and collected'
                }
            ],
            'certifications': [cert.value for cert in record.certifications],
            'quality_tests': record.quality_tests,
            'processing_steps': record.processing_steps,
            'storage_chain': record.storage_locations
        }

        # Add processing steps to timeline
        for step in record.processing_steps:
            journey['timeline'].append({
                'date': step.get('date', ''),
                'event': step.get('process', 'Processing'),
                'location': step.get('location', 'Processing facility'),
                'details': step.get('details', '')
            })

        # Add storage information
        for storage in record.storage_locations:
            journey['timeline'].append({
                'date': storage.get('date', ''),
                'event': 'Stored',
                'location': storage.get('location', 'Storage facility'),
                'details': f"Temperature: {storage.get('temperature', 'N/A')}°C, Humidity: {storage.get('humidity', 'N/A')}%"
            })

        # Find if product was delivered to client
        if record.destination_client:
            client = self.clients.get(record.destination_client)
            if client:
                journey['final_destination'] = {
                    'client_name': client.name,
                    'client_type': client.client_type.value,
                    'address': client.address
                }

        # Sort timeline by date
        journey['timeline'].sort(key=lambda x: x['date'])

        return journey

    async def manage_certifications(self) -> Dict:
        """Manage certification status and renewal alerts"""
        certification_status = {
            'active_certifications': [],
            'expiring_soon': [],
            'renewal_actions': []
        }

        current_date = datetime.now()
        warning_period = timedelta(days=90)  # 3 months before expiry

        for cert_type, cert_info in self.certifications.items():
            valid_until = cert_info['valid_until']
            days_until_expiry = (valid_until - current_date).days

            cert_summary = {
                'type': cert_type.value,
                'certificate_number': cert_info['certificate_number'],
                'issuing_body': cert_info['issuing_body'],
                'valid_until': valid_until.isoformat(),
                'days_until_expiry': days_until_expiry,
                'status': 'active' if days_until_expiry > 0 else 'expired'
            }

            if days_until_expiry > 0:
                certification_status['active_certifications'].append(cert_summary)

                if valid_until - current_date <= warning_period:
                    certification_status['expiring_soon'].append(cert_summary)

                    # Generate renewal actions
                    next_inspection = cert_info.get('next_inspection')
                    if next_inspection and next_inspection <= current_date + timedelta(days=30):
                        certification_status['renewal_actions'].append({
                            'action': 'Schedule inspection',
                            'certification': cert_type.value,
                            'deadline': next_inspection.isoformat(),
                            'priority': 'high'
                        })

        return certification_status

    async def generate_compliance_report(self, certification_type: CertificationType,
                                       start_date: datetime, end_date: datetime) -> Dict:
        """Generate compliance report for specific certification"""
        cert_info = self.certifications.get(certification_type)
        if not cert_info:
            return {'error': f'No {certification_type.value} certification found'}

        # Find relevant traceability records
        relevant_records = [
            record for record in self.traceability_records.values()
            if (certification_type in record.certifications and
                start_date <= record.harvest_date <= end_date)
        ]

        # Calculate compliance metrics
        total_production = len(relevant_records)
        compliant_batches = len([r for r in relevant_records if certification_type in r.certifications])
        compliance_percentage = (compliant_batches / total_production * 100) if total_production > 0 else 0

        report = {
            'certification_type': certification_type.value,
            'reporting_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'certificate_details': cert_info,
            'production_summary': {
                'total_batches': total_production,
                'compliant_batches': compliant_batches,
                'compliance_percentage': round(compliance_percentage, 2)
            },
            'batch_details': [
                {
                    'batch_id': record.batch_id,
                    'product_id': record.product_id,
                    'field_id': record.field_id,
                    'harvest_date': record.harvest_date.isoformat(),
                    'certifications': [cert.value for cert in record.certifications],
                    'quality_tests': len(record.quality_tests)
                }
                for record in relevant_records
            ],
            'recommendations': self._generate_compliance_recommendations(certification_type, relevant_records)
        }

        return report

    def _generate_compliance_recommendations(self, cert_type: CertificationType,
                                           records: List[TraceabilityRecord]) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []

        if cert_type == CertificationType.ORGANIC:
            # Check for organic-specific compliance
            if len([r for r in records if len(r.quality_tests) < 2]) > 0:
                recommendations.append("Increase frequency of soil and product testing for organic compliance")

            recommendations.append("Maintain detailed records of all inputs and treatments")
            recommendations.append("Ensure buffer zones between organic and conventional fields")

        elif cert_type == CertificationType.GAP:
            recommendations.append("Regular calibration of equipment and monitoring systems")
            recommendations.append("Maintain worker training records and safety protocols")
            recommendations.append("Document all pest management and fertilizer applications")

        return recommendations

    async def get_client_analytics(self, client_id: str, months: int = 12) -> Dict:
        """Get comprehensive analytics for B2B client"""
        client = self.clients.get(client_id)
        if not client:
            return {'error': f'Client {client_id} not found'}

        start_date = datetime.now() - timedelta(days=months * 30)
        client_orders = [
            order for order in self.orders.values()
            if order.client_id == client_id and order.order_date >= start_date
        ]

        if not client_orders:
            return {
                'client_info': {
                    'name': client.name,
                    'type': client.client_type.value
                },
                'message': 'No orders found in specified period'
            }

        # Calculate metrics
        total_orders = len(client_orders)
        total_revenue = sum(order.total_amount for order in client_orders)
        average_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0')

        # Order frequency analysis
        order_dates = [order.order_date for order in client_orders]
        order_frequency = total_orders / months if months > 0 else 0

        # Product analysis
        product_quantities = {}
        for order in client_orders:
            for item in order.items:
                product_id = item['product_id']
                quantity = item['quantity']
                product_quantities[product_id] = product_quantities.get(product_id, 0) + quantity

        top_products = sorted(product_quantities.items(), key=lambda x: x[1], reverse=True)[:5]

        analytics = {
            'client_info': {
                'name': client.name,
                'type': client.client_type.value,
                'contact_person': client.contact_person,
                'payment_terms': client.payment_terms
            },
            'performance_metrics': {
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'average_order_value': float(average_order_value),
                'order_frequency_per_month': round(order_frequency, 2),
                'currency': 'EUR'
            },
            'top_products': [
                {
                    'product_id': product_id,
                    'total_quantity': quantity
                }
                for product_id, quantity in top_products
            ],
            'delivery_performance': {
                'on_time_deliveries': len([o for o in client_orders if o.status == OrderStatus.DELIVERED]),
                'pending_orders': len([o for o in client_orders if o.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]])
            }
        }

        return analytics

# Example usage and testing
async def main():
    """Example usage of Supply Chain Coordinator"""
    farm_config = {
        'name': 'Green Valley Farm',
        'address': 'Farm Road 123, 1234 AB Farmville'
    }

    coordinator = SupplyChainCoordinator(farm_config)
    await coordinator.initialize()

    # Create a new order
    order_data = {
        'client_id': list(coordinator.clients.keys())[0],
        'requested_delivery_date': (datetime.now() + timedelta(days=2)).isoformat(),
        'items': [
            {'product_id': 'tomatoes_001', 'quantity': 50, 'unit_price': '4.50'},
            {'product_id': 'lettuce_001', 'quantity': 20, 'unit_price': '2.80'}
        ],
        'delivery_method': 'farm_delivery',
        'special_instructions': 'Deliver to kitchen entrance'
    }

    order_id = await coordinator.create_order(order_data)
    print(f"Created order: {order_id}")

    # Create traceability record
    trace_data = {
        'product_id': 'tomatoes_001',
        'batch_id': 'TOM2024001',
        'field_id': 'field_003',
        'planted_date': '2024-05-01T00:00:00',
        'harvest_date': '2024-08-15T00:00:00',
        'organic': True,
        'quality_tests': [
            {'test_type': 'pesticide_residue', 'result': 'negative', 'date': '2024-08-16'},
            {'test_type': 'heavy_metals', 'result': 'within_limits', 'date': '2024-08-16'}
        ]
    }

    trace_id = await coordinator.create_traceability_record(trace_data)
    print(f"Created traceability record: {trace_id}")

    # Track product journey
    journey = await coordinator.track_product_journey('tomatoes_001', 'TOM2024001')
    print("Product Journey:", journey)

    # Check certification status
    cert_status = await coordinator.manage_certifications()
    print("Certification Status:", cert_status)

if __name__ == "__main__":
    asyncio.run(main())