"""
SQLAlchemy 2.0 models for storing intake leads, contacts, custom actions, and webhooks.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class IntakeLead(Base):
    """SQLAlchemy model for storing intake lead data."""

    __tablename__ = "intake_leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Contact information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Lead content
    message: Mapped[str] = mapped_column(Text, nullable=False)
    referring_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(
        String(100), nullable=False, default="Capture Now Bot"
    )

    # Clio integration tracking
    clio_lead_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True
    )
    clio_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    clio_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clio_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<IntakeLead(id={self.id}, name='{self.first_name} {self.last_name}', source='{self.source}')>"

    @property
    def full_name(self) -> str:
        """Return the full name of the contact."""
        return f"{self.first_name} {self.last_name}"

    def to_bot_data(self) -> dict:
        """Convert model to bot_data format for Clio API."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "message": self.message,
            "email": self.email,
            "phone_number": self.phone_number,
            "referring_url": self.referring_url,
            "source": self.source,
        }

    def mark_sent_to_clio(self, clio_lead_id: int, status: str, response: str) -> None:
        """Mark the lead as sent to Clio with response details."""
        self.clio_lead_id = clio_lead_id
        self.clio_status = status
        self.clio_sent_at = datetime.utcnow()
        self.clio_response = response


class InboxLeadToken(Base):
    """SQLAlchemy model for storing Clio inbox lead tokens."""

    __tablename__ = "inbox_lead_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<InboxLeadToken(id={self.id}, token='{self.token[:10]}...')>"


class Contact(Base):
    """SQLAlchemy model for storing Clio contacts."""

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Clio contact information
    clio_contact_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, unique=True, index=True
    )

    # Contact details
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Business information
    company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Address information (stored as JSON for flexibility)
    primary_address: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Contact type and status
    contact_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, default="Person"
    )
    is_client: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, clio_id={self.clio_contact_id}, name='{self.first_name} {self.last_name}')>"

    @property
    def full_name(self) -> str:
        """Return the full name of the contact."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return "Unknown Contact"


class CustomAction(Base):
    """SQLAlchemy model for storing Clio custom actions."""

    __tablename__ = "custom_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Clio custom action information
    clio_action_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, unique=True, index=True
    )

    # Action configuration
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    http_method: Mapped[str] = mapped_column(String(10), nullable=False, default="GET")
    url: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional configuration
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<CustomAction(id={self.id}, clio_id={self.clio_action_id}, name='{self.name}')>"

    def to_clio_data(self) -> dict:
        """Convert model to Clio custom action format."""
        return {
            "data": {
                "name": self.name,
                "http_method": self.http_method,
                "url": self.url,
            }
        }

    def increment_usage(self) -> None:
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()


class WebhookSubscription(Base):
    """SQLAlchemy model for storing webhook subscriptions."""

    __tablename__ = "webhook_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Clio webhook subscription information
    clio_subscription_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, unique=True, index=True
    )

    # Subscription configuration
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    events: Mapped[list] = mapped_column(JSON, nullable=False)  # List of event types
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Optional configuration
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Usage tracking
    webhook_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_webhook_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<WebhookSubscription(id={self.id}, clio_id={self.clio_subscription_id}, url='{self.url}')>"

    def increment_webhook_count(self) -> None:
        """Increment webhook count and update last webhook timestamp."""
        self.webhook_count += 1
        self.last_webhook_at = datetime.utcnow()


class WebhookEvent(Base):
    """SQLAlchemy model for storing received webhook events."""

    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Event identification
    clio_event_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Event data
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # Full webhook payload
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Request tracking
    request_id: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<WebhookEvent(id={self.id}, type='{self.event_type}', processed={self.processed})>"

    def mark_processed(self, error: Optional[str] = None) -> None:
        """Mark the event as processed."""
        self.processed = True
        self.processed_at = datetime.utcnow()
        if error:
            self.processing_error = error
