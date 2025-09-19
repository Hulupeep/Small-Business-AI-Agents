"""
Database models for Inventory Tracker and Meeting Scheduler agents.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

class Product(Base):
    """Product inventory model"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    unit_cost = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    reorder_point = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    inventory_items = relationship("InventoryItem", back_populates="product")
    sales_history = relationship("SalesHistory", back_populates="product")

class Supplier(Base):
    """Supplier model"""
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact_email = Column(String(100))
    contact_phone = Column(String(20))
    address = Column(Text)
    lead_time_days = Column(Integer, default=7)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="supplier")

class Location(Base):
    """Storage location model"""
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    type = Column(String(50))  # warehouse, store, distribution_center
    manager_email = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="location")

class InventoryItem(Base):
    """Inventory tracking per location"""
    __tablename__ = 'inventory_items'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_available = Column(Integer, default=0)
    last_counted = Column(DateTime)
    last_movement = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    location = relationship("Location", back_populates="inventory_items")

class SalesHistory(Base):
    """Sales history for demand forecasting"""
    __tablename__ = 'sales_history'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))
    quantity_sold = Column(Integer, nullable=False)
    sale_price = Column(Float, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    season = Column(String(20))  # spring, summer, fall, winter
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="sales_history")

class PurchaseOrder(Base):
    """Purchase order tracking"""
    __tablename__ = 'purchase_orders'

    id = Column(Integer, primary_key=True)
    po_number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    status = Column(String(20), default='pending')  # pending, sent, received, cancelled
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery = Column(DateTime)
    total_amount = Column(Float, default=0.0)
    notes = Column(Text)
    created_by = Column(String(50), default='inventory_agent')

    # Relationships
    supplier = relationship("Supplier")
    line_items = relationship("PurchaseOrderItem", back_populates="purchase_order")

class PurchaseOrderItem(Base):
    """Purchase order line items"""
    __tablename__ = 'purchase_order_items'

    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="line_items")
    product = relationship("Product")

# Meeting Scheduler Models

class Calendar(Base):
    """Calendar configuration"""
    __tablename__ = 'calendars'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    owner_email = Column(String(100), nullable=False)
    calendar_id = Column(String(200))  # External calendar ID
    provider = Column(String(50))  # google, outlook, calendly
    timezone = Column(String(50), default='UTC')
    is_primary = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sync_token = Column(String(500))
    credentials = Column(Text)  # Encrypted API credentials
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    meetings = relationship("Meeting", back_populates="calendar")

class Meeting(Base):
    """Meeting/appointment model"""
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True)
    calendar_id = Column(Integer, ForeignKey('calendars.id'), nullable=False)
    external_id = Column(String(200))  # External meeting ID
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String(50), default='UTC')
    location = Column(String(500))
    meeting_url = Column(String(500))
    status = Column(String(20), default='scheduled')  # scheduled, cancelled, completed
    organizer_email = Column(String(100))
    attendee_emails = Column(Text)  # JSON array
    reminder_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    calendar = relationship("Calendar", back_populates="meetings")

class SchedulingRequest(Base):
    """Natural language scheduling requests"""
    __tablename__ = 'scheduling_requests'

    id = Column(Integer, primary_key=True)
    requester_email = Column(String(100), nullable=False)
    original_text = Column(Text, nullable=False)
    parsed_intent = Column(Text)  # JSON with extracted information
    proposed_times = Column(Text)  # JSON array of proposed meeting times
    status = Column(String(20), default='processing')  # processing, scheduled, failed
    meeting_id = Column(Integer, ForeignKey('meetings.id'))
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    # Relationships
    meeting = relationship("Meeting")

class ConflictResolution(Base):
    """Track conflict resolution attempts"""
    __tablename__ = 'conflict_resolutions'

    id = Column(Integer, primary_key=True)
    scheduling_request_id = Column(Integer, ForeignKey('scheduling_requests.id'))
    conflict_type = Column(String(50))  # time_overlap, double_booking, timezone_issue
    original_time = Column(DateTime)
    suggested_alternatives = Column(Text)  # JSON array
    resolution_method = Column(String(50))
    final_time = Column(DateTime)
    resolved_at = Column(DateTime)

    # Relationships
    scheduling_request = relationship("SchedulingRequest")

# Business Metrics Models

class BusinessMetric(Base):
    """Track business impact metrics"""
    __tablename__ = 'business_metrics'

    id = Column(Integer, primary_key=True)
    metric_type = Column(String(50), nullable=False)  # inventory_savings, time_saved, revenue_impact
    agent_type = Column(String(50), nullable=False)  # inventory_tracker, meeting_scheduler
    value = Column(Float, nullable=False)
    unit = Column(String(20))  # dollars, hours, percentage
    calculation_method = Column(Text)
    date_recorded = Column(DateTime, default=datetime.utcnow)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    notes = Column(Text)

class DatabaseManager:
    """Database connection and session management"""

    def __init__(self, database_url: str = "sqlite:///automation_agents.db"):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def close_session(self, session):
        """Close database session"""
        session.close()