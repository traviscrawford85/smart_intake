"""
Pydantic schemas for Webhook Event API responses
"""

from datetime import datetime

from pydantic import BaseModel


class WebhookEventBase(BaseModel):
    """Base webhook event schema for creation/updates"""

    event_type: str
    event_data: dict | None = None
    processed: bool = False


class WebhookEvent(WebhookEventBase):
    """Full webhook event schema for API responses"""

    id: int
    created_at: datetime
    processed_at: datetime | None = None

    class Config:
        from_attributes = True


class WebhookEventCreate(WebhookEventBase):
    """Schema for creating webhook events"""

    pass


class WebhookEventUpdate(BaseModel):
    """Schema for updating webhook events"""

    processed: bool | None = None
    processed_at: datetime | None = None
