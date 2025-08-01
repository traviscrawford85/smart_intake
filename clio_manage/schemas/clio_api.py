"""
Clio API Pydantic schemas for custom actions, contacts, and webhooks.
Inherits from ClioBaseModel for automatic normalization and field validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl

from clio_manage.clio_base import ClioBaseModel

# === CUSTOM ACTION SCHEMAS ===


class CustomActionData(ClioBaseModel):
    """Schema for custom action data payload."""

    name: str = Field(..., description="Display name of the custom action")
    http_method: str = Field(..., description="HTTP method (GET, POST, PUT, DELETE)")
    url: HttpUrl = Field(..., description="Target URL for the custom action")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Open Smart Intake",
                "http_method": "GET",
                "url": "https://smartintake.cfelab.com/dashboard?contact_id={contact.id}",
            }
        }


class CustomAction(ClioBaseModel):
    """Complete custom action schema."""

    data: CustomActionData = Field(..., description="Custom action configuration")
    enabled: bool = Field(True, description="Whether the custom action is enabled")
    created_by: Optional[int] = Field(
        None, description="User ID who created the action"
    )

    # Clio API metadata
    etag: Optional[str] = Field(None, description="ETag for optimistic concurrency")

    model_config = {"arbitrary_types_allowed": True}


class CustomActionCreate(BaseModel):
    """Schema for creating custom actions."""

    data: CustomActionData = Field(..., description="Custom action configuration")
    enabled: bool = Field(True, description="Whether the custom action is enabled")


class CustomActionUpdate(BaseModel):
    """Schema for updating custom actions."""

    data: Optional[CustomActionData] = Field(None, description="Updated configuration")
    enabled: Optional[bool] = Field(None, description="Updated enabled status")


# === CONTACT SCHEMAS ===


class ContactPhoneNumber(ClioBaseModel):
    """Schema for contact phone numbers."""

    id: Optional[int] = None
    name: Optional[str] = Field(
        None, description="Phone number label (e.g., 'Mobile', 'Work')"
    )
    number: str = Field(..., description="Phone number")
    default_number: bool = Field(
        False, description="Whether this is the default phone number"
    )


class ContactEmailAddress(ClioBaseModel):
    """Schema for contact email addresses."""

    id: Optional[int] = None
    name: Optional[str] = Field(
        None, description="Email label (e.g., 'Personal', 'Work')"
    )
    address: EmailStr = Field(..., description="Email address")
    default_address: bool = Field(
        False, description="Whether this is the default email"
    )


class ContactAddress(ClioBaseModel):
    """Schema for contact addresses."""

    id: Optional[int] = None
    name: Optional[str] = Field(
        None, description="Address label (e.g., 'Home', 'Office')"
    )
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    province: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="ZIP/Postal code")
    country: Optional[str] = Field(None, description="Country")


class Contact(ClioBaseModel):
    """Complete contact schema matching Clio API."""

    type: str = Field("Person", description="Contact type (Person, Company)")

    # Basic information
    first_name: Optional[str] = Field(None, description="Contact's first name")
    middle_name: Optional[str] = Field(None, description="Contact's middle name")
    last_name: Optional[str] = Field(None, description="Contact's last name")
    name: Optional[str] = Field(None, description="Full name or company name")

    # Contact details
    phone_numbers: List[ContactPhoneNumber] = Field(
        default_factory=list, description="Phone numbers"
    )
    email_addresses: List[ContactEmailAddress] = Field(
        default_factory=list, description="Email addresses"
    )
    addresses: List[ContactAddress] = Field(
        default_factory=list, description="Physical addresses"
    )

    # Professional information
    title: Optional[str] = Field(None, description="Professional title")
    company: Optional[str] = Field(None, description="Company name")

    # Metadata
    notes: Optional[str] = Field(None, description="Notes about the contact")
    is_client: bool = Field(False, description="Whether this contact is a client")
    client_type: Optional[str] = Field(None, description="Type of client")

    # Clio API metadata
    prefix: Optional[str] = Field(None, description="Name prefix (Mr., Ms., Dr., etc.)")
    suffix: Optional[str] = Field(None, description="Name suffix (Jr., Sr., III, etc.)")
    etag: Optional[str] = Field(None, description="ETag for optimistic concurrency")


class ContactCreate(BaseModel):
    """Schema for creating contacts."""

    type: str = Field("Person", description="Contact type (Person, Company)")
    first_name: Optional[str] = Field(None, description="Contact's first name")
    last_name: Optional[str] = Field(None, description="Contact's last name")
    name: Optional[str] = Field(None, description="Full name or company name")
    phone_numbers: List[ContactPhoneNumber] = Field(default_factory=list)
    email_addresses: List[ContactEmailAddress] = Field(default_factory=list)
    addresses: List[ContactAddress] = Field(default_factory=list)
    title: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    is_client: bool = False


class ContactUpdate(BaseModel):
    """Schema for updating contacts."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    phone_numbers: Optional[List[ContactPhoneNumber]] = None
    email_addresses: Optional[List[ContactEmailAddress]] = None
    addresses: Optional[List[ContactAddress]] = None
    title: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    is_client: Optional[bool] = None


# === WEBHOOK SCHEMAS ===


class WebhookEvent(ClioBaseModel):
    """Schema for webhook event data."""

    event_id: Optional[str] = Field(None, description="Event ID", alias="id")
    type: str = Field(..., description="Event type (e.g., 'contact.created')")
    occurred_at: datetime = Field(..., description="When the event occurred")


class WebhookPayload(ClioBaseModel):
    """Schema for complete webhook payload from Clio."""

    webhook_id: Optional[str] = Field(None, description="Webhook ID", alias="id")
    events: List[WebhookEvent] = Field(
        ..., description="List of events in this webhook"
    )
    delivered_at: datetime = Field(..., description="When the webhook was delivered")
    request_id: Optional[str] = Field(None, description="Clio request ID for tracking")


class WebhookSubscription(ClioBaseModel):
    """Schema for webhook subscription configuration."""

    subscription_id: Optional[int] = Field(
        None, description="Clio webhook subscription ID", alias="id"
    )
    url: str = Field(..., description="URL to receive webhooks")
    events: List[str] = Field(..., description="List of event types to subscribe to")
    active: bool = Field(True, description="Whether subscription is active")
    created_at: Optional[datetime] = Field(
        None, description="When subscription was created"
    )
    updated_at: Optional[datetime] = Field(
        None, description="When subscription was last updated"
    )


class WebhookSubscriptionCreate(BaseModel):
    """Schema for creating webhook subscriptions."""

    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    events: List[str] = Field(..., description="List of event types to subscribe to")
    enabled: bool = Field(True, description="Whether the webhook should be enabled")
    secret: Optional[str] = Field(None, description="Optional webhook signing secret")
    description: Optional[str] = Field(None, description="Optional description")


class WebhookSubscriptionUpdate(BaseModel):
    """Schema for updating webhook subscriptions."""

    url: Optional[HttpUrl] = Field(None, description="Updated webhook endpoint URL")
    events: Optional[List[str]] = Field(None, description="Updated event types")
    enabled: Optional[bool] = Field(None, description="Updated enabled status")
    secret: Optional[str] = Field(None, description="Updated signing secret")
    description: Optional[str] = Field(None, description="Updated description")


# === RESPONSE WRAPPERS ===


class ClioApiResponse(BaseModel):
    """Generic Clio API response wrapper."""

    data: Dict[str, Any] = Field(..., description="Response data")
    meta: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


class ClioListResponse(BaseModel):
    """Clio API list response with pagination."""

    data: List[Dict[str, Any]] = Field(..., description="List of items")
    meta: Dict[str, Any] = Field(..., description="Pagination and metadata")


class PaginationMeta(BaseModel):
    """Pagination metadata from Clio API."""

    paging: Dict[str, Any] = Field(..., description="Pagination information")
    records: int = Field(..., description="Total number of records")


# === ERROR SCHEMAS ===


class ClioApiError(BaseModel):
    """Clio API error response."""

    error: str = Field(..., description="Error message")
    error_description: Optional[str] = Field(
        None, description="Detailed error description"
    )
    errors: Optional[Dict[str, List[str]]] = Field(
        None, description="Field-specific errors"
    )


class WebhookDeliveryError(BaseModel):
    """Webhook delivery error information."""

    attempt: int = Field(..., description="Failed delivery attempt number")
    error: str = Field(..., description="Error message")
    attempted_at: datetime = Field(..., description="When the delivery was attempted")
    next_attempt_at: Optional[datetime] = Field(
        None, description="When the next attempt will be made"
    )
