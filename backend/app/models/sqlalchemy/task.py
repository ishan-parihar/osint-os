"""
Task-related SQLAlchemy models for task management and execution tracking.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, Text, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class TaskResult(Base):
    """Task result model for storing task execution results."""
    
    __tablename__ = "task_results"
    
    task_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    result_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(String(50), nullable=True)
    execution_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task result to dictionary."""
        return {
            "id": self.uuid,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
