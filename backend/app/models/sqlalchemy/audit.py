"""
Audit-related SQLAlchemy models for security and compliance logging.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Text, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class AuditLog(Base):
    """Audit log model for tracking security and compliance events."""
    
    __tablename__ = "audit_logs"
    
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary."""
        return {
            "id": self.uuid,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "timestamp": self.timestamp,
            "severity": self.severity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SystemEvent(Base):
    """System event model for tracking system-level events."""
    
    __tablename__ = "system_events"
    
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    component: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert system event to dictionary."""
        return {
            "id": self.uuid,
            "event_type": self.event_type,
            "component": self.component,
            "event_data": self.event_data,
            "severity": self.severity,
            "source": self.source,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
