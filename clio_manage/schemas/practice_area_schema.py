"""
Pydantic schemas for Practice Area API responses
"""

from datetime import datetime

from pydantic import BaseModel


class PracticeAreaBase(BaseModel):
    """Base practice area schema for creation/updates"""

    name: str
    description: str | None = None
    color: str | None = None


class PracticeArea(PracticeAreaBase):
    """Full practice area schema for API responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PracticeAreaCreate(PracticeAreaBase):
    """Schema for creating practice areas"""

    pass


class PracticeAreaUpdate(BaseModel):
    """Schema for updating practice areas"""

    name: str | None = None
    description: str | None = None
    color: str | None = None
