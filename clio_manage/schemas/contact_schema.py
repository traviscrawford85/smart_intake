"""
Pydantic schemas for Contact API responses
"""

from datetime import datetime

from pydantic import BaseModel


class ContactBase(BaseModel):
    """Base contact schema for creation/updates"""

    clio_id: str | None = None
    name: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    company: str | None = None


class Contact(ContactBase):
    """Full contact schema for API responses"""

    id: int
    title: str | None = None
    mobile_phone: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    type: str | None = None
    is_client: bool = False
    created_at: datetime
    updated_at: datetime
    clio_created_at: datetime | None = None
    clio_updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ContactCreate(ContactBase):
    """Schema for creating contacts"""

    pass


class ContactUpdate(BaseModel):
    """Schema for updating contacts"""

    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    company: str | None = None
