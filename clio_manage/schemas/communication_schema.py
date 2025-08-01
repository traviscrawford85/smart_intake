"""
Pydantic schemas for Communication API responses
"""

from datetime import datetime

from pydantic import BaseModel


class CommunicationBase(BaseModel):
    """Base communication schema for creation/updates"""

    clio_id: str | None = None
    subject: str | None = None
    body: str | None = None
    type: str | None = None
    from_address: str | None = None


class Communication(CommunicationBase):
    """Full communication schema for API responses"""

    id: int

    # Email specifics
    body_text_type: str | None = None
    to_addresses: list | None = None
    cc_addresses: list | None = None
    bcc_addresses: list | None = None

    # Status
    read: bool = False

    # Relationships
    matter_id: int | None = None
    clio_matter_id: str | None = None
    contact_id: int | None = None
    clio_contact_id: str | None = None

    # Attachments
    attachments_data: dict | None = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    clio_created_at: datetime | None = None
    clio_updated_at: datetime | None = None

    class Config:
        from_attributes = True


class CommunicationCreate(CommunicationBase):
    """Schema for creating communications"""

    matter_id: int | None = None
    contact_id: int | None = None


class CommunicationUpdate(BaseModel):
    """Schema for updating communications"""

    subject: str | None = None
    body: str | None = None
    read: bool | None = None
