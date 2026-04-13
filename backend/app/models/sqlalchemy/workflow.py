"""
Workflow-related SQLAlchemy models for data persistence.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class WorkflowState(Base):
    """Workflow state model for storing workflow execution states."""
    
    __tablename__ = "workflow_states"
    __table_args__ = {"extend_existing": True}
    
    # Override base fields for this specific table
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    workflow_data: Mapped[str] = mapped_column(Text, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow state to dictionary."""
        return {
            "id": self.uuid,
            "workflow_id": self.workflow_id,
            "workflow_data": self.workflow_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Workflow(Base):
    """Workflow model for storing workflow definitions."""
    
    __tablename__ = "workflows"
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    definition: Mapped[str] = mapped_column(JSON, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "id": self.uuid,
            "name": self.name,
            "description": self.description,
            "definition": self.definition,
            "version": self.version,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WorkflowTransition(Base):
    """Workflow transition model for tracking workflow state changes."""
    
    __tablename__ = "workflow_transitions"
    
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    from_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    to_state: Mapped[str] = mapped_column(String(100), nullable=False)
    transition_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    triggered_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow transition to dictionary."""
        return {
            "id": self.uuid,
            "workflow_id": self.workflow_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "transition_data": self.transition_data,
            "triggered_by": self.triggered_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class URLInfo(Base):
    """URL information model for storing URL metadata and analysis results."""
    
    __tablename__ = "url_info"
    
    url: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status_code: Mapped[Optional[int]] = mapped_column(String(10), nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content_length: Mapped[Optional[int]] = mapped_column(String(20), nullable=True)
    last_crawled: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    url_metadata: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert URL info to dictionary."""
        return {
            "id": self.uuid,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "domain": self.domain,
            "status_code": self.status_code,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "last_crawled": self.last_crawled,
            "metadata": self.url_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SchemaField(Base):
    """Schema field model for storing form schema definitions."""
    
    __tablename__ = "schema_fields"
    
    field_name: Mapped[str] = mapped_column(String(200), nullable=False)
    field_type: Mapped[str] = mapped_column(String(100), nullable=False)
    field_label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    field_options: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    default_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validation_rules: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema field to dictionary."""
        return {
            "id": self.uuid,
            "field_name": self.field_name,
            "field_type": self.field_type,
            "field_label": self.field_label,
            "field_options": self.field_options,
            "required": self.required,
            "default_value": self.default_value,
            "validation_rules": self.validation_rules,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ApprovalRequest(Base):
    """Approval request model for workflow approval processes."""
    
    __tablename__ = "approval_requests"
    
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    request_type: Mapped[str] = mapped_column(String(100), nullable=False)
    request_data: Mapped[str] = mapped_column(JSON, nullable=False)
    requested_by: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert approval request to dictionary."""
        return {
            "id": self.uuid,
            "workflow_id": self.workflow_id,
            "request_type": self.request_type,
            "request_data": self.request_data,
            "requested_by": self.requested_by,
            "status": self.status,
            "approved_by": self.approved_by,
            "approval_notes": self.approval_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PipelineExecution(Base):
    """Pipeline execution model for tracking pipeline runs."""
    
    __tablename__ = "pipeline_executions"
    
    pipeline_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    execution_data: Mapped[str] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    started_by: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline execution to dictionary."""
        return {
            "id": self.uuid,
            "pipeline_id": self.pipeline_id,
            "execution_data": self.execution_data,
            "status": self.status,
            "started_by": self.started_by,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
