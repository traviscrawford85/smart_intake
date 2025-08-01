"""
Pydantic v2 schemas for the Clio Grow intake agent.
"""
from typing import Optional, Union, List, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from app.clio_base import ClioBaseModel


class BotDataInput(BaseModel):
    """Schema for incoming bot data from intake sources."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Contact's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Contact's last name")
    message: str = Field(..., min_length=1, description="Message or transcript from the contact")
    email: Optional[EmailStr] = Field(None, description="Contact's email address")
    phone_number: Optional[str] = Field(None, max_length=20, description="Contact's phone number")
    referring_url: HttpUrl = Field(..., description="URL where the lead originated")
    source: str = Field(default="Capture Now Bot", max_length=100, description="Source of the lead")


class CaptureNowInboxLead(BaseModel):
    """Schema for Capture Now agent envelope inbox lead structure."""
    id: Optional[int] = None
    errors: Optional[dict] = None
    created_at: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    message: Optional[Union[str, bool]] = None  # Can be string or false
    referring_url: Optional[str] = None
    source: Optional[str] = None
    
    # Additional Capture Now fields
    call_duration: Optional[int] = None
    call_recording_url: Optional[str] = None
    chat_conversation_id: Optional[str] = None
    dispute_status: Optional[str] = None
    google_lead_id: Optional[str] = None
    hidden: Optional[bool] = None
    inboxable: Optional[str] = None
    inboxable_type: Optional[str] = None
    lead_type: Optional[str] = None
    location: Optional[str] = None


class CaptureNowEnvelope(BaseModel):
    """Schema for the full Capture Now agent envelope."""
    inbox_leads: List[CaptureNowInboxLead] = Field(default_factory=list)
    
    # Additional envelope fields that might be present
    call_duration: Optional[int] = None
    call_recording_url: Optional[str] = None
    chat_conversation_id: Optional[str] = None
    created_at: Optional[str] = None
    dispute_status: Optional[str] = None
    email: Optional[str] = None
    errors: Optional[dict] = None
    first_name: Optional[str] = None
    google_lead_id: Optional[str] = None
    hidden: Optional[bool] = None
    id: Optional[int] = None
    inboxable: Optional[str] = None
    inboxable_type: Optional[str] = None
    last_name: Optional[str] = None
    lead_type: Optional[str] = None
    location: Optional[str] = None
    message: Optional[Union[str, bool]] = None

class LeadRequiredInfo(ClioBaseModel):
    """Schema for required lead information."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Contact's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Contact's last name")
    email: EmailStr = Field(..., description="Contact's email address")
    phone_number: str = Field(..., max_length=20, description="Contact's phone number")
    message: str = Field(..., min_length=1, description="Message or transcript from the contact")


class DirectPayload(BaseModel):
    """Schema for direct payload from web forms."""
    inbox_lead: dict
    inbox_lead_token: Optional[str] = None


class UnifiedLeadInput(BaseModel):
    """Unified schema that can handle both envelope and direct payloads."""
    # Direct payload fields
    inbox_lead: Optional[dict] = None
    inbox_lead_token: Optional[str] = None
    
    # Envelope fields (flattened)
    inbox_leads: Optional[List[dict]] = None
    
    # Common fields that might appear at root level
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    message: Optional[Union[str, bool]] = None
    referring_url: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[str] = None
    id: Optional[int] = None
    
    # Additional fields
    call_duration: Optional[int] = None
    call_recording_url: Optional[str] = None
    chat_conversation_id: Optional[str] = None
    dispute_status: Optional[str] = None
    errors: Optional[dict] = None
    google_lead_id: Optional[str] = None
    hidden: Optional[bool] = None
    inboxable: Optional[str] = None
    inboxable_type: Optional[str] = None
    lead_type: Optional[str] = None
    location: Optional[str] = None


class ClioInboxLead(BaseModel):
    """Schema for the Clio Grow inbox lead structure."""
    from_first: str = Field(..., min_length=1, max_length=100)
    from_last: str = Field(..., min_length=1, max_length=100)
    from_message: str = Field(..., min_length=1)
    from_email: Optional[str] = Field(None, max_length=255)
    from_phone: Optional[str] = Field(None, max_length=20)
    referring_url: str = Field(..., min_length=1)
    from_source: str = Field(..., min_length=1, max_length=100)


class ClioGrowPayload(BaseModel):
    """Complete payload schema for Clio Grow Lead Inbox API."""
    inbox_lead: ClioInboxLead
    inbox_lead_token: str = Field(..., min_length=1, description="Lead inbox token for authentication")


class LeadResponse(BaseModel):
    """Schema for successful lead creation response."""
    id: Optional[int] = None
    status: str
    message: Optional[str] = None
    created_at: Optional[str] = None


class ClioInboxLeadErrors(BaseModel):
    """Schema for Clio inbox lead validation errors."""
    from_first: Optional[list[str]] = None
    from_last: Optional[list[str]] = None
    from_message: Optional[list[str]] = None
    referring_url: Optional[list[str]] = None
    from_source: Optional[list[str]] = None
    from_email: Optional[list[str]] = None
    from_phone: Optional[list[str]] = None


class ClioErrorInboxLead(BaseModel):
    """Schema for Clio error response inbox_lead structure."""
    id: Optional[int] = None
    errors: ClioInboxLeadErrors
    from_first: str = ""
    from_last: str = ""
    from_phone: str = ""
    from_email: str = ""
    from_message: str = ""
    from_source: Optional[str] = None


class ClioErrorResponse(BaseModel):
    """Schema for Clio Grow API error responses (422 validation errors)."""
    inbox_lead: ClioErrorInboxLead


class LeadErrorResponse(BaseModel):
    """Schema for general error responses."""
    error: str
    details: Optional[dict] = None
    status_code: int
