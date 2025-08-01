"""
Pydantic schemas for User API responses
"""

from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    """Base user schema for creation/updates"""

    clio_id: str | None = None
    email: str
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    role: str | None = None


class User(UserBase):
    """Full user schema for API responses"""

    id: int
    enabled: bool = True
    subscription_type: str | None = None
    rate: str | None = None
    created_at: datetime
    updated_at: datetime
    clio_created_at: datetime | None = None
    clio_updated_at: datetime | None = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    """Schema for creating users"""

    pass


class UserUpdate(BaseModel):
    """Schema for updating users"""

    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    role: str | None = None
    enabled: bool | None = None
