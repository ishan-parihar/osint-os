"""
Base model for SQLAlchemy ORM models.
"""

from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Any, Dict
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models with common fields."""

    # Primary key using UUID for consistency across all models
    uuid: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )

    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=True
    )  # Soft delete support

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary."""
        for key, value in data.items():
            if hasattr(self, key) and key not in ["uuid", "created_at"]:
                setattr(self, key, value)
        self.updated_at = datetime.now()
