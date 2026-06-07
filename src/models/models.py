"""Database models for Healthcare Care Coordinator"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean, Text, 
    ForeignKey, Table, JSON, Enum as SQLEnum, Float, and_
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB
from sqlalchemy.types import String, JSON

# Fallback for SQLite
class UUID(String):
    def __init__(self, length=36, as_uuid=False, **kwargs):
        super().__init__(length=36, **kwargs)
JSONB = JSON
import uuid
from src.database import Base


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    CARE_COORDINATOR = "care_coordinator"
    PATIENT = "patient"
    PHYSICIAN = "physician"
    NURSE = "nurse"
    APPROVER = "approver"  # For care plan approval


class AppointmentStatus(str, Enum):
    """Appointment status values"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class CarePlanStatus(str, Enum):
    """Care plan status values"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class AuditAction(str, Enum):
    """Audit log action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"
    EXECUTE = "execute"


# Association tables
user_care_team = Table(
    'user_care_team',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('user.id')),
    Column('patient_id', UUID(as_uuid=True), ForeignKey('user.id'))
)


class User(Base):
    """User model"""
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.PATIENT, nullable=False)
    is_active = Column(Boolean, default=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(255), nullable=True)  # For care coordinators, physicians
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships are defined on child tables to avoid ambiguity



class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False, index=True)
    scheduled_by_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    appointment_type = Column(String(100), nullable=False)  # checkup, follow-up, etc.
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    
    scheduled_at = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)
    location = Column(String(255), nullable=True)
    
    notes = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # Generated after completion
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scheduled_by = relationship("User", foreign_keys=[scheduled_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])


class CarePlan(Base):
    """Care plan model"""
    __tablename__ = "care_plan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False, index=True)
    coordinator_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(CarePlanStatus), default=CarePlanStatus.DRAFT)
    
    goals = Column(JSONB, default=[])  # Array of goal objects
    interventions = Column(JSONB, default=[])  # Array of intervention objects
    timeline = Column(String(255), nullable=True)  # e.g., "2 weeks", "1 month"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    activated_at = Column(DateTime, nullable=True)

    # Relationships
    coordinator = relationship("User", foreign_keys=[coordinator_id])
    approval_request = relationship("ApprovalRequest", uselist=False)


class Medication(Base):
    """Medication reminder model"""
    __tablename__ = "medication"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)  # e.g., "twice daily", "every 8 hours"
    route = Column(String(100), nullable=False)  # oral, injection, etc.
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    
    instructions = Column(Text, nullable=True)
    side_effects = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("User")


class Document(Base):
    """Medical document storage"""
    __tablename__ = "document"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False, index=True)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    
    filename = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)  # lab_result, scan, note, etc.
    description = Column(Text, nullable=True)
    
    file_path = Column(String(512), nullable=False)  # S3 path or local path
    file_size = Column(Integer)  # bytes
    mime_type = Column(String(100))
    
    indexed = Column(Boolean, default=False)  # Whether it's indexed in vector DB
    embedding_id = Column(String(255), nullable=True)  # Vector DB reference
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])


class ApprovalRequest(Base):
    """Approval request for care plans and other actions"""
    __tablename__ = "approval_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    care_plan_id = Column(UUID(as_uuid=True), ForeignKey('care_plan.id'), nullable=False, unique=True)
    approver_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=True)
    
    requested_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    decision_at = Column(DateTime, nullable=True)
    
    request_data = Column(JSONB)  # Full request context
    decision_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    care_plan = relationship("CarePlan", overlaps="approval_request")
    approver = relationship("User")


class AuditLog(Base):
    """Comprehensive audit logging"""
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), nullable=True)
    
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # user, appointment, care_plan, etc.
    resource_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    details = Column(JSONB)  # Full details of the action
    changes = Column(JSONB, nullable=True)  # Before/after for updates
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    
    status = Column(String(50), default="success")  # success, failure
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User")


class PolicyViolation(Base):
    """Policy violation tracking"""
    __tablename__ = "policy_violation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_rule = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    violation_details = Column(JSONB)
    severity = Column(String(50))  # low, medium, high, critical
    
    resolved = Column(Boolean, default=False)
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
