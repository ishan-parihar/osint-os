"""
SQLAlchemy models for Chain of Custody tracking system.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from .base import Base


class CustodyActionType(str, Enum):
    CREATED = "CREATED"
    ACCESSED = "ACCESSED"
    MODIFIED = "MODIFIED"
    COPIED = "COPIED"
    MOVED = "MOVED"
    EXPORTED = "EXPORTED"
    PRINTED = "PRINTED"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"
    RESTORED = "RESTORED"
    VERIFIED = "VERIFIED"
    ANALYZED = "ANALYZED"


class CustodyEventType(str, Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    AUTOMATED = "AUTOMATED"
    BATCH = "BATCH"
    EMERGENCY = "EMERGENCY"


class EvidenceChain(Base):
    """Main chain of custody record for a piece of evidence."""
    __tablename__ = "evidence_chains"

    evidence_id = Column(String, nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False)  # digital, physical, document
    evidence_hash = Column(String(128), nullable=False, index=True)  # SHA-256 or similar
    original_location = Column(Text)
    current_location = Column(Text)
    status = Column(String(20), default="ACTIVE")  # ACTIVE, ARCHIVED, DELETED
    classification = Column(String(20), default="UNCLASSIFIED")
    handling_instructions = Column(Text)
    retention_policy = Column(String(100))  # policy name or ID
    retention_until = Column(DateTime)
    legal_hold = Column(Boolean, default=False)
    legal_hold_reason = Column(Text)
    legal_hold_requested_by = Column(String)
    legal_hold_requested_at = Column(DateTime)
    
    # Metadata
    initial_collector = Column(String)  # user ID
    initial_collection_time = Column(DateTime, default=datetime.utcnow)
    last_modified_by = Column(String)  # user ID
    last_modified_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    custody_events = relationship("CustodyEvent", back_populates="evidence_chain", cascade="all, delete-orphan")
    access_logs = relationship("CustodyAccessLog", back_populates="evidence_chain", cascade="all, delete-orphan")
    integrity_checks = relationship("IntegrityCheck", back_populates="evidence_chain", cascade="all, delete-orphan")


class CustodyEvent(Base):
    """Individual events in the chain of custody."""
    __tablename__ = "custody_events"

    evidence_chain_id = Column(String, ForeignKey("evidence_chains.uuid"), nullable=False)
    action_type = Column(String(50), nullable=False)  # CustodyActionType
    event_type = Column(String(20), nullable=False)  # CustodyEventType
    performed_by = Column(String, nullable=False)  # user ID
    performed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Event details
    description = Column(Text)
    previous_location = Column(Text)
    new_location = Column(Text)
    previous_hash = Column(String(128))
    new_hash = Column(String(128))
    
    # Access control
    access_level_required = Column(String(20))
    access_granted_to = Column(JSON)  # list of user IDs if shared access
    session_id = Column(String)  # for tracking user sessions
    
    # Technical details
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    workstation_id = Column(String)
    method = Column(String(10))  # GET, POST, PUT, DELETE
    
    # Change details
    changes_made = Column(JSON)  # detailed change tracking
    reason_for_change = Column(Text)
    approval_required = Column(Boolean, default=False)
    approved_by = Column(String)  # user ID
    approved_at = Column(DateTime)
    
    # Relationships
    evidence_chain = relationship("EvidenceChain", back_populates="custody_events")


class CustodyAccessLog(Base):
    """Detailed access logging for evidence."""
    __tablename__ = "custody_access_logs"

    evidence_chain_id = Column(String, ForeignKey("evidence_chains.uuid"), nullable=False)
    user_id = Column(String, nullable=False)
    access_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    access_type = Column(String(20), nullable=False)  # READ, WRITE, EXECUTE, DELETE
    
    # Session details
    session_id = Column(String)
    session_start = Column(DateTime)
    session_duration = Column(Float)  # in seconds
    
    # Access details
    ip_address = Column(String(45))
    user_agent = Column(Text)
    workstation_id = Column(String)
    success = Column(Boolean, default=True)
    failure_reason = Column(Text)
    
    # Data accessed
    fields_accessed = Column(JSON)  # list of fields accessed
    data_exported = Column(Boolean, default=False)
    export_format = Column(String(20))
    export_destination = Column(Text)
    
    # Security
    authentication_method = Column(String(20))
    multi_factor_used = Column(Boolean, default=False)
    privilege_level = Column(String(20))
    
    # Relationships
    evidence_chain = relationship("EvidenceChain", back_populates="access_logs")


class IntegrityCheck(Base):
    """Integrity verification for evidence."""
    __tablename__ = "integrity_checks"

    evidence_chain_id = Column(String, ForeignKey("evidence_chains.uuid"), nullable=False)
    check_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    check_type = Column(String(50), nullable=False)  # HASH, SIGNATURE, FORMAT, COMPLETENESS
    performed_by = Column(String, nullable=False)
    
    # Check results
    check_passed = Column(Boolean, nullable=False)
    expected_hash = Column(String(128))
    actual_hash = Column(String(128))
    algorithm = Column(String(20))  # SHA-256, MD5, etc.
    
    # Detailed results
    check_details = Column(JSON)
    anomalies_found = Column(JSON)
    recommendations = Column(Text)
    
    # Signature verification
    signature_valid = Column(Boolean)
    signer_certificate = Column(Text)
    signature_timestamp = Column(DateTime)
    
    # File format checks
    format_valid = Column(Boolean)
    format_details = Column(JSON)
    corruption_detected = Column(Boolean)
    corruption_details = Column(Text)
    
    # Relationships
    evidence_chain = relationship("EvidenceChain", back_populates="integrity_checks")


class CustodyTransfer(Base):
    """Formal transfer of evidence custody."""
    __tablename__ = "custody_transfers"

    evidence_chain_id = Column(String, ForeignKey("evidence_chains.uuid"), nullable=False)
    transfer_id = Column(String, unique=True, nullable=False, index=True)
    
    # Transfer details
    from_user = Column(String, nullable=False)
    to_user = Column(String, nullable=False)
    transfer_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    reason_for_transfer = Column(Text)
    
    # Approval
    approval_required = Column(Boolean, default=True)
    approved_by = Column(String)
    approved_at = Column(DateTime)
    approval_comments = Column(Text)
    
    # Transfer method
    transfer_method = Column(String(50))  # DIGITAL, PHYSICAL, COURIER, ELECTRONIC
    tracking_number = Column(String)
    expected_delivery = Column(DateTime)
    actual_delivery = Column(DateTime)
    
    # Acceptance
    accepted_by = Column(String)
    accepted_at = Column(DateTime)
    acceptance_conditions = Column(JSON)
    declined_reason = Column(Text)
    
    # Chain of custody continuity
    previous_transfer_id = Column(String)
    next_transfer_id = Column(String)
    
    # Metadata
    transfer_notes = Column(Text)
    attachments = Column(JSON)  # list of document IDs


class CustodyAuditReport(Base):
    """Generated audit reports for chain of custody."""
    __tablename__ = "custody_audit_reports"

    report_id = Column(String, unique=True, nullable=False, index=True)
    evidence_chain_id = Column(String, ForeignKey("evidence_chains.uuid"), nullable=False)
    
    # Report details
    report_type = Column(String(50), nullable=False)  # FULL, SUMMARY, COMPLIANCE, LEGAL
    generated_by = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    # Report content
    report_content = Column(JSON)
    summary_findings = Column(Text)
    anomalies_detected = Column(JSON)
    compliance_status = Column(String(20))
    
    # Distribution
    distributed_to = Column(JSON)
    distribution_method = Column(String(20))
    distribution_time = Column(DateTime)
    
    # Review
    reviewed_by = Column(String)
    reviewed_at = Column(DateTime)
    review_status = Column(String(20))  # PENDING, APPROVED, REJECTED
    review_comments = Column(Text)


class LegalHoldRequest(Base):
    """Legal hold requests for evidence preservation."""
    __tablename__ = "legal_hold_requests"

    hold_request_id = Column(String, unique=True, nullable=False, index=True)
    evidence_chain_id = Column(String, ForeignKey("evidence_chains.uuid"), nullable=False)
    
    # Request details
    requested_by = Column(String, nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    case_number = Column(String, nullable=False)
    case_title = Column(String, nullable=False)
    jurisdiction = Column(String)
    
    # Hold parameters
    hold_reason = Column(Text, nullable=False)
    hold_scope = Column(String(20))  # EVIDENCE, INVESTIGATION, USER, SYSTEM
    hold_duration = Column(String)  # PERMANENT, TEMPORARY, UNTIL_DATE
    hold_until = Column(DateTime)
    
    # Legal details
    legal_basis = Column(Text)
    counsel_name = Column(String)
    counsel_contact = Column(String)
    court_order_number = Column(String)
    court_order_date = Column(DateTime)
    
    # Status
    status = Column(String(20), default="ACTIVE")  # ACTIVE, RELEASED, EXTENDED
    released_by = Column(String)
    released_at = Column(DateTime)
    release_reason = Column(Text)
    
    # Notifications
    notified_parties = Column(JSON)
    notification_methods = Column(JSON)
    last_notification = Column(DateTime)