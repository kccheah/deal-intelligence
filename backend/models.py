"""
SQLAlchemy ORM Models
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, LargeBinary, ForeignKey, ARRAY, Numeric, Date, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

# ============================================================================
# USERS & AUTHENTICATION
# ============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    company_name = Column(String(255))
    subscription_tier = Column(String(50), default="trial")  # trial | deal_intel | property_dd | bundle
    subscription_status = Column(String(50), default="active")  # active | trial | paused | cancelled
    stripe_customer_id = Column(String(255), unique=True, index=True)
    trial_ends_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)

    # Relationships
    alerts = relationship("UserAlert", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    api_usage = relationship("APIUsage", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"

# ============================================================================
# DEAL INTELLIGENCE
# ============================================================================

class Deal(Base):
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_source_id = Column(String(500))
    source = Column(String(50), nullable=False, index=True)  # crunchbase | preqin | news | pitchbook | linkedin
    deal_type = Column(String(50), index=True)  # ma | pe | jv | fdi | other
    company_name = Column(String(255), nullable=False)
    industry = Column(String(100))
    industry_tags = Column(ARRAY(String), index=True)
    deal_value_usd = Column(Integer)
    announced_date = Column(Date, index=True)
    closed_date = Column(Date)
    target_geography = Column(String(2), index=True)  # ISO country code
    target_region = Column(String(100))
    acquiring_company = Column(String(255))
    acquiring_geography = Column(String(2))
    deal_description = Column(Text)
    deal_url = Column(String(500))

    # Scoring
    score = Column(Integer, index=True)  # 1-100
    score_breakdown = Column(JSONB)  # {sector: 20, geo: 30, size: 25, strategic: 25}
    scoring_methodology = Column(String(100))
    scoring_version = Column(Integer, default=1)

    # Raw data
    raw_data = Column(JSONB)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    indexed_at = Column(DateTime)

    # Relationships
    alert_triggers = relationship("AlertTrigger", back_populates="deal", cascade="all, delete-orphan")
    scoring_history = relationship("ScoringHistory", back_populates="deal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Deal {self.company_name} - {self.deal_type}>"

# ============================================================================
# PROPERTY DATA
# ============================================================================

class Property(Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_source_id = Column(String(500))
    source = Column(String(50))
    property_type = Column(String(50), index=True)  # residential | commercial | industrial | mixed
    address = Column(String(500))
    city = Column(String(100))
    country_code = Column(String(2), nullable=False, index=True)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))

    # Property Details
    price_usd = Column(Integer)
    size_sqm = Column(Numeric(10, 2))
    year_built = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)

    # Legal Status
    ownership_legal_status = Column(String(50))  # freehold | leasehold | restricted | mixed
    lease_remaining_years = Column(Integer)
    freehold_eligible = Column(Boolean)
    foreign_ownership_allowed = Column(Boolean)

    # Due Diligence
    dd_status = Column(String(50), default="pending", index=True)  # pending | in_progress | completed | flagged
    dd_data = Column(JSONB)  # {legal: {...}, tax: {...}, regulatory: {...}, risks: [...]}
    investment_score = Column(Integer, index=True)  # 1-100
    risk_level = Column(String(20), index=True)  # low | medium | high
    acquisition_timeline_months = Column(Integer)

    # Market Data
    market_comparable_price_usd = Column(Integer)
    appreciation_rate_annual = Column(Numeric(5, 2))
    rental_yield_annual = Column(Numeric(5, 2))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alert_triggers = relationship("AlertTrigger", back_populates="property", cascade="all, delete-orphan")
    scoring_history = relationship("ScoringHistory", back_populates="property", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Property {self.address} - {self.city}>"

# ============================================================================
# USER ALERTS
# ============================================================================

class UserAlert(Base):
    __tablename__ = "user_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(50))  # deal | property | both
    alert_name = Column(String(255))

    # Criteria
    criteria = Column(JSONB)  # {sectors: [...], geographies: [...], value_min: ..., value_max: ...}

    # Settings
    frequency = Column(String(50), default="realtime")  # realtime | daily | weekly
    enabled = Column(Boolean, default=True, index=True)
    last_triggered_at = Column(DateTime)
    trigger_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="alerts")
    triggers = relationship("AlertTrigger", back_populates="alert", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserAlert {self.alert_name}>"

# ============================================================================
# ALERT TRIGGERS
# ============================================================================

class AlertTrigger(Base):
    __tablename__ = "alert_triggers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("user_alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="SET NULL"), index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="SET NULL"), index=True)

    # Alert details
    alert_message = Column(Text)
    match_score = Column(Numeric(5, 2))  # 0-1
    was_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    alert = relationship("UserAlert", back_populates="triggers")
    deal = relationship("Deal", back_populates="alert_triggers")
    property = relationship("Property", back_populates="alert_triggers")

    def __repr__(self):
        return f"<AlertTrigger {self.id}>"

# ============================================================================
# SCORING HISTORY
# ============================================================================

class ScoringHistory(Base):
    __tablename__ = "scoring_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(UUID(as_uuid=True), ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), index=True)

    scoring_version = Column(Integer)
    score_value = Column(Integer)
    score_breakdown = Column(JSONB)
    methodology = Column(String(100))
    model_version = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    deal = relationship("Deal", back_populates="scoring_history")
    property = relationship("Property", back_populates="scoring_history")

    def __repr__(self):
        return f"<ScoringHistory v{self.scoring_version}>"

# ============================================================================
# SUBSCRIPTIONS
# ============================================================================

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    tier = Column(String(50))  # deal_intel | property_dd | bundle
    status = Column(String(50), index=True)  # active | paused | cancelled

    stripe_subscription_id = Column(String(255), unique=True)
    stripe_price_id = Column(String(255))
    current_period_start = Column(Date)
    current_period_end = Column(Date)

    cancel_at_period_end = Column(Boolean, default=False)
    cancelled_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")

    def __repr__(self):
        return f"<Subscription {self.tier}>"

# ============================================================================
# API USAGE TRACKING
# ============================================================================

class APIUsage(Base):
    __tablename__ = "api_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    endpoint = Column(String(255))
    method = Column(String(10))
    status_code = Column(Integer)
    response_time_ms = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="api_usage")

    def __repr__(self):
        return f"<APIUsage {self.endpoint}>"

# ============================================================================
# AUDIT LOG
# ============================================================================

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)

    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(String(255))
    details = Column(JSONB)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action}>"
