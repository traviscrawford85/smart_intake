"""
Clio API integration service layer.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from clio_manage.models import Contact, CustomAction, WebhookEvent, WebhookSubscription
from clio_manage.schemas.clio_api import (
    ContactCreate,
    ContactResponse,
    CustomActionCreate,
    CustomActionResponse,
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)
from clio_manage.utils.clio_api_helpers import clio_api_helper

logger = logging.getLogger(__name__)


class ClioContactService:
    """Service for managing Clio contacts with local database sync."""

    def __init__(self):
        self.api_helper = clio_api_helper

    async def sync_contacts_from_clio(self, db: AsyncSession) -> int:
        """Sync all contacts from Clio API to local database."""
        async with httpx.AsyncClient() as client:
            try:
                # Get all contacts from Clio
                clio_contacts = await self.api_helper.get_all_contacts(client)

                synced_count = 0
                for contact_data in clio_contacts:
                    await self._sync_single_contact(db, contact_data)
                    synced_count += 1

                await db.commit()
                logger.info(f"Synced {synced_count} contacts from Clio")
                return synced_count

            except Exception as e:
                logger.error(f"Error syncing contacts from Clio: {e}")
                await db.rollback()
                raise

    async def _sync_single_contact(
        self, db: AsyncSession, contact_data: Dict[str, Any]
    ) -> Contact:
        """Sync a single contact from Clio data."""
        clio_contact_id = contact_data.get("id")

        # Check if contact already exists
        stmt = select(Contact).where(Contact.clio_contact_id == clio_contact_id)
        result = await db.execute(stmt)
        existing_contact = result.scalar_one_or_none()

        # Extract contact fields
        contact_fields = {
            "clio_contact_id": clio_contact_id,
            "first_name": contact_data.get("first_name"),
            "last_name": contact_data.get("last_name"),
            "email": contact_data.get("email_address"),
            "phone_number": contact_data.get("phone_number"),
            "company": contact_data.get("company"),
            "title": contact_data.get("title"),
            "contact_type": contact_data.get("type", "Person"),
            "is_client": contact_data.get("is_client", False),
            "primary_address": contact_data.get("primary_address"),
        }

        if existing_contact:
            # Update existing contact
            for field, value in contact_fields.items():
                if field != "clio_contact_id":  # Don't update ID
                    setattr(existing_contact, field, value)
            existing_contact.updated_at = datetime.utcnow()
            return existing_contact
        else:
            # Create new contact
            new_contact = Contact(**contact_fields)
            db.add(new_contact)
            return new_contact

    async def get_local_contacts(
        self, db: AsyncSession, limit: int = 100, offset: int = 0
    ) -> List[Contact]:
        """Get contacts from local database."""
        stmt = (
            select(Contact)
            .offset(offset)
            .limit(limit)
            .order_by(Contact.created_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()


class ClioCustomActionService:
    """Service for managing Clio custom actions."""

    def __init__(self):
        self.api_helper = clio_api_helper

    async def create_smart_intake_action(self, db: AsyncSession) -> CustomAction:
        """Create the Smart Intake custom action in Clio."""
        action_name = "Open Smart Intake"
        action_url = "https://smartintake.cfelab.com/dashboard?contact_id={contact.id}"

        async with httpx.AsyncClient() as client:
            try:
                # Create in Clio
                clio_response = await self.api_helper.create_custom_action(
                    client, name=action_name, url=action_url, http_method="GET"
                )

                # Store locally
                clio_action_data = clio_response.get("data", {})
                custom_action = CustomAction(
                    clio_action_id=clio_action_data.get("id"),
                    name=action_name,
                    url=action_url,
                    http_method="GET",
                    description="Open Smart Intake dashboard for this contact",
                )

                db.add(custom_action)
                await db.commit()

                logger.info(f"Created Smart Intake custom action: {custom_action.id}")
                return custom_action

            except Exception as e:
                logger.error(f"Error creating Smart Intake custom action: {e}")
                await db.rollback()
                raise

    async def sync_custom_actions_from_clio(self, db: AsyncSession) -> int:
        """Sync all custom actions from Clio API to local database."""
        async with httpx.AsyncClient() as client:
            try:
                # Get all custom actions from Clio
                clio_actions = await self.api_helper.get_all_custom_actions(client)

                synced_count = 0
                for action_data in clio_actions:
                    await self._sync_single_custom_action(db, action_data)
                    synced_count += 1

                await db.commit()
                logger.info(f"Synced {synced_count} custom actions from Clio")
                return synced_count

            except Exception as e:
                logger.error(f"Error syncing custom actions from Clio: {e}")
                await db.rollback()
                raise

    async def _sync_single_custom_action(
        self, db: AsyncSession, action_data: Dict[str, Any]
    ) -> CustomAction:
        """Sync a single custom action from Clio data."""
        clio_action_id = action_data.get("id")

        # Check if action already exists
        stmt = select(CustomAction).where(CustomAction.clio_action_id == clio_action_id)
        result = await db.execute(stmt)
        existing_action = result.scalar_one_or_none()

        # Extract action fields
        action_fields = {
            "clio_action_id": clio_action_id,
            "name": action_data.get("name"),
            "url": action_data.get("url"),
            "http_method": action_data.get("http_method", "GET"),
            "enabled": action_data.get("enabled", True),
        }

        if existing_action:
            # Update existing action
            for field, value in action_fields.items():
                if field != "clio_action_id":  # Don't update ID
                    setattr(existing_action, field, value)
            existing_action.updated_at = datetime.utcnow()
            return existing_action
        else:
            # Create new action
            new_action = CustomAction(**action_fields)
            db.add(new_action)
            return new_action


class ClioWebhookService:
    """Service for managing Clio webhook subscriptions."""

    def __init__(self):
        self.api_helper = clio_api_helper

    async def create_intake_webhook_subscription(
        self, db: AsyncSession, webhook_url: str
    ) -> WebhookSubscription:
        """Create webhook subscription for intake-related events."""
        events = [
            "contact.created",
            "contact.updated",
            "lead.created",
            "lead.updated",
            "matter.created",
        ]

        async with httpx.AsyncClient() as client:
            try:
                # Create in Clio
                clio_response = await self.api_helper.create_webhook_subscription(
                    client, url=webhook_url, events=events
                )

                # Store locally
                clio_subscription_data = clio_response.get("data", {})
                webhook_subscription = WebhookSubscription(
                    clio_subscription_id=clio_subscription_data.get("id"),
                    url=webhook_url,
                    events=events,
                    description="Smart Intake webhook for contact and lead events",
                )

                db.add(webhook_subscription)
                await db.commit()

                logger.info(f"Created webhook subscription: {webhook_subscription.id}")
                return webhook_subscription

            except Exception as e:
                logger.error(f"Error creating webhook subscription: {e}")
                await db.rollback()
                raise

    async def process_webhook_event(
        self, db: AsyncSession, payload: Dict[str, Any]
    ) -> WebhookEvent:
        """Process incoming webhook event."""
        try:
            # Extract event information
            events = payload.get("events", [])
            if not events:
                logger.warning("Webhook payload contains no events")
                return None

            # Process each event (for now, just store the first one)
            event_data = events[0]
            event_type = event_data.get("type")

            # Create webhook event record
            webhook_event = WebhookEvent(
                clio_event_id=event_data.get("id"),
                event_type=event_type,
                payload=payload,
                occurred_at=datetime.fromisoformat(
                    event_data.get("occurred_at", "").replace("Z", "+00:00")
                ),
                request_id=payload.get("request_id"),
                delivered_at=datetime.fromisoformat(
                    payload.get("delivered_at", "").replace("Z", "+00:00")
                ),
            )

            db.add(webhook_event)

            # Process specific event types
            if event_type in ["contact.created", "contact.updated"]:
                await self._process_contact_event(db, event_data)
            elif event_type in ["lead.created", "lead.updated"]:
                await self._process_lead_event(db, event_data)

            # Mark as processed
            webhook_event.mark_processed()

            await db.commit()
            logger.info(f"Processed webhook event: {event_type}")
            return webhook_event

        except Exception as e:
            logger.error(f"Error processing webhook event: {e}")
            if "webhook_event" in locals():
                webhook_event.mark_processed(str(e))
            await db.rollback()
            raise

    async def _process_contact_event(
        self, db: AsyncSession, event_data: Dict[str, Any]
    ):
        """Process contact-related webhook events."""
        contact_data = event_data.get("data", {})
        if contact_data:
            contact_service = ClioContactService()
            await contact_service._sync_single_contact(db, contact_data)

    async def _process_lead_event(self, db: AsyncSession, event_data: Dict[str, Any]):
        """Process lead-related webhook events."""
        # For now, just log the event
        logger.info(f"Lead event received: {event_data.get('type')}")


# Service instances
contact_service = ClioContactService()
custom_action_service = ClioCustomActionService()
webhook_service = ClioWebhookService()
