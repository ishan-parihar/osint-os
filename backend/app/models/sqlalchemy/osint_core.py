"""
Core OSINT models for evidence chain of custody and source management.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Text, Boolean, JSON, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class DataSource(Base):
    """Data source model for tracking OSINT sources and reliability."""
    
    __tablename__ = "data_sources"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)  # web, social, api, etc.
    url: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 to 1.0
    last_accessed: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    credentials_required: Mapped[bool] = mapped_column(Boolean, default=False)
    collection_parameters: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "source_type": self.source_type,
            "url": self.url,
            "description": self.description,
            "reliability_score": self.reliability_score,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "is_active": self.is_active,
            "credentials_required": self.credentials_required,
            "collection_parameters": self.collection_parameters,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EvidenceChain(Base):
    """Evidence chain of custody model."""
    
    __tablename__ = "evidence_chains"
    
    evidence_uuid: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    handler: Mapped[str] = mapped_column(String(100), nullable=False)  # User ID or system
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # created, accessed, modified, exported
    location: Mapped[str] = mapped_column(String(500), nullable=False)  # Storage location
    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_metadata: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "uuid": self.uuid,
            "evidence_uuid": self.evidence_uuid,
            "handler": self.handler,
            "action": self.action,
            "location": self.location,
            "purpose": self.purpose,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "metadata": self.evidence_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ThreatActor(Base):
    """Threat actor model for intelligence tracking."""
    
    __tablename__ = "threat_actors"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    alias: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of aliases
    actor_type: Mapped[str] = mapped_column(String(100), nullable=False)  # APT, hacktivist, criminal, etc.
    motivation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capabilities: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    known_attributions: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    first_seen: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    threat_level: Mapped[str] = mapped_column(String(20), default="unknown")
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "uuid": self.uuid,
            "name": self.name,
            "alias": self.alias,
            "actor_type": self.actor_type,
            "motivation": self.motivation,
            "capabilities": self.capabilities,
            "known_attributions": self.known_attributions,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "threat_level": self.threat_level,
            "confidence": self.confidence,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ThreatIndicator(Base):
    """Threat indicator (IOC) model."""
    
    __tablename__ = "threat_indicators"
    
    indicator_type: Mapped[str] = mapped_column(String(100), nullable=False)  # ip, domain, hash, email, etc.
    value: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    first_seen: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    last_seen: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tags: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    related_actors: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "uuid": self.uuid,
            "indicator_type": self.indicator_type,
            "value": self.value,
            "description": self.description,
            "source": self.source,
            "confidence": self.confidence,
            "severity": self.severity,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "is_active": self.is_active,
            "tags": self.tags,
            "related_actors": self.related_actors,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CollectionJob(Base):
    """Collection job model for scheduled data collection."""
    
    __tablename__ = "collection_jobs"
    
    job_name: Mapped[str] = mapped_column(String(200), nullable=False)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)  # web_scraping, api_query, social_monitor
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    schedule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # cron expression
    parameters: Mapped[str] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="scheduled")  # scheduled, running, completed, failed
    priority: Mapped[int] = mapped_column(Integer, default=5)  # 1-10
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_run: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    run_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "uuid": self.uuid,
            "job_name": self.job_name,
            "job_type": self.job_type,
            "source_id": self.source_id,
            "schedule": self.schedule,
            "parameters": self.parameters,
            "status": self.status,
            "priority": self.priority,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "error_message": self.error_message,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LegalHold(Base):
    """Legal hold model for data preservation."""
    
    __tablename__ = "legal_holds"
    
    case_name: Mapped[str] = mapped_column(String(200), nullable=False)
    case_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requested_by: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[datetime] = mapped_column(String(50), nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, expired, released
    scope: Mapped[str] = mapped_column(JSON, nullable=False)  # What data is preserved
    custodians: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # List of custodians
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "uuid": self.uuid,
            "case_name": self.case_name,
            "case_number": self.case_number,
            "description": self.description,
            "requested_by": self.requested_by,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "status": self.status,
            "scope": self.scope,
            "custodians": self.custodians,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
