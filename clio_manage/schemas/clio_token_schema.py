"""
Pydantic schemas for Clio Token API responses
"""

from datetime import datetime

from pydantic import BaseModel


class ClioTokenBase(BaseModel):
    """Base Clio token schema for creation/updates"""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_at: datetime | None = None


class ClioToken(ClioTokenBase):
    """Full Clio token schema for API responses"""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClioTokenCreate(ClioTokenBase):
    """Schema for creating Clio tokens"""

    pass


class ClioTokenUpdate(BaseModel):
    """Schema for updating Clio tokens"""

    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None
