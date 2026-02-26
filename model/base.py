"""
Base model classes with common functionality for all trading models.
Provides timestamp tracking and common methods.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func
from .database import Base


class TimestampMixin:
    """Mixin class that adds created_at and updated_at timestamp columns."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model for all trading system models.
    Provides common fields and methods.
    """
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
    
    def __repr__(self):
        """String representation of model instance."""
        return f"<{{self.__class__.__name__}}(id={{self.id}})>"
