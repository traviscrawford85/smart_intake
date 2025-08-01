"""
Pydantic v2 schemas for Entity Relationship models
Type-safe API schemas with validation
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Base schemas
class EntityRelationshipBase(BaseModel):
    """Base schema for entity relationships"""

    source_entity_type: str = Field(..., description="Type of the source entity")
    source_entity_id: str = Field(..., description="ID of the source entity")
    relationship_type: str = Field(..., description="Type of relationship")
    target_entity_type: str = Field(..., description="Type of the target entity")
    target_entity_id: str = Field(..., description="ID of the target entity")
    label: str | None = Field(None, description="Human-readable label")
    description: str | None = Field(
        None, description="Description of the relationship"
    )
    relationship_data: dict[str, Any] | None = Field(
        None, description="Additional relationship data"
    )
    is_active: bool = Field(True, description="Whether the relationship is active")
    strength: float | None = Field(1.0, description="Relationship strength")


class EntityRelationshipCreate(EntityRelationshipBase):
    """Schema for creating entity relationships"""

    clio_id: int | None = Field(None, description="Clio relationship ID")
    clio_etag: str | None = Field(None, description="Clio etag for change tracking")
    clio_created_at: datetime | None = Field(
        None, description="Creation timestamp from Clio"
    )
    clio_updated_at: datetime | None = Field(
        None, description="Update timestamp from Clio"
    )


class EntityRelationshipUpdate(BaseModel):
    """Schema for updating entity relationships"""

    label: str | None = None
    description: str | None = None
    relationship_data: dict[str, Any] | None = None
    is_active: bool | None = None
    strength: float | None = None
    clio_etag: str | None = None
    clio_updated_at: datetime | None = None


class EntityRelationshipResponse(EntityRelationshipBase):
    """Schema for entity relationship responses"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    relationship_id: str
    clio_id: int | None = None
    clio_etag: str | None = None
    created_at: datetime
    updated_at: datetime
    clio_created_at: datetime | None = None
    clio_updated_at: datetime | None = None


# Entity Metadata schemas
class EntityMetadataBase(BaseModel):
    """Base schema for entity metadata"""

    entity_type: str = Field(..., description="Type of the entity")
    entity_id: str = Field(..., description="ID of the entity")
    display_name: str | None = Field(None, description="Human-readable name")
    status: str | None = Field(None, description="Current status")
    entity_data: dict[str, Any] | None = Field(
        None, description="Full entity data from Clio"
    )
    is_active: bool = Field(True, description="Whether the entity is active")


class EntityMetadataCreate(EntityMetadataBase):
    """Schema for creating entity metadata"""

    clio_etag: str | None = Field(None, description="Clio etag")
    clio_created_at: datetime | None = Field(
        None, description="Creation timestamp from Clio"
    )
    clio_updated_at: datetime | None = Field(
        None, description="Update timestamp from Clio"
    )


class EntityMetadataUpdate(BaseModel):
    """Schema for updating entity metadata"""

    display_name: str | None = None
    status: str | None = None
    entity_data: dict[str, Any] | None = None
    is_active: bool | None = None
    clio_etag: str | None = None
    clio_updated_at: datetime | None = None


class EntityMetadataResponse(EntityMetadataBase):
    """Schema for entity metadata responses"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    clio_etag: str | None = None
    clio_created_at: datetime | None = None
    clio_updated_at: datetime | None = None
    local_created_at: datetime
    local_updated_at: datetime
    last_synced_at: datetime | None = None


# Clio Relationship schemas (direct mapping of Clio API)
class ClioMatter(BaseModel):
    """Schema for matter data in Clio relationships"""

    id: int
    etag: str
    number: int | None = None
    display_number: str | None = None
    custom_number: str | None = None
    description: str | None = None
    status: str | None = None
    location: str | None = None
    client_reference: str | None = None
    client_id: int | None = None
    billable: bool | None = None
    billing_method: str | None = None
    open_date: datetime | None = None
    close_date: datetime | None = None
    pending_date: datetime | None = None
    created_at: datetime
    updated_at: datetime
    shared: bool | None = None
    has_tasks: bool | None = None
    last_activity_date: datetime | None = None
    matter_stage_updated_at: datetime | None = None


class ClioContact(BaseModel):
    """Schema for contact data in Clio relationships"""

    id: int
    etag: str
    name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    date_of_birth: datetime | None = None
    type: str | None = None
    created_at: datetime
    updated_at: datetime
    prefix: str | None = None
    title: str | None = None
    initials: str | None = None
    primary_email_address: str | None = None
    secondary_email_address: str | None = None
    primary_phone_number: str | None = None
    secondary_phone_number: str | None = None
    is_client: bool | None = None
    is_co_counsel: bool | None = None
    is_bill_recipient: bool | None = None


class ClioRelationshipBase(BaseModel):
    """Base schema for Clio relationships"""

    clio_id: int = Field(..., alias="id", description="Clio relationship ID")
    clio_etag: str = Field(..., alias="etag", description="Clio etag")
    description: str | None = Field(None, description="Relationship description")
    clio_created_at: datetime = Field(
        ..., alias="created_at", description="Creation timestamp"
    )
    clio_updated_at: datetime = Field(
        ..., alias="updated_at", description="Update timestamp"
    )
    matter: ClioMatter | None = Field(None, description="Matter information")
    contact: ClioContact | None = Field(None, description="Contact information")


class ClioRelationshipCreate(ClioRelationshipBase):
    """Schema for creating Clio relationships"""

    pass


class ClioRelationshipResponse(ClioRelationshipBase):
    """Schema for Clio relationship responses"""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    local_created_at: datetime
    local_updated_at: datetime
    raw_matter_data: dict[str, Any] | None = None
    raw_contact_data: dict[str, Any] | None = None


# Batch and bulk operation schemas
class BatchEntityRelationshipCreate(BaseModel):
    """Schema for batch creating entity relationships"""

    relationships: list[EntityRelationshipCreate] = Field(
        ..., description="List of relationships to create"
    )


class BatchEntityRelationshipResponse(BaseModel):
    """Schema for batch entity relationship operation responses"""

    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    total: int = Field(..., description="Total number of operations")
    relationships_created: int = Field(
        ..., description="Number of relationships created"
    )
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Error details"
    )


# Query schemas
class EntityNetworkQuery(BaseModel):
    """Schema for entity network queries"""

    entity_type: str = Field(..., description="Type of the central entity")
    entity_id: str = Field(..., description="ID of the central entity")
    max_depth: int = Field(2, description="Maximum relationship depth to traverse")
    relationship_types: list[str] | None = Field(
        None, description="Filter by relationship types"
    )
    include_inactive: bool = Field(False, description="Include inactive relationships")


class EntityNetworkResponse(BaseModel):
    """Schema for entity network responses"""

    central_entity: dict[str, str] = Field(
        ..., description="Central entity information"
    )
    relationships: list[EntityRelationshipResponse] = Field(
        ..., description="Network relationships"
    )
    entities: dict[str, EntityMetadataResponse] = Field(
        ..., description="Related entities metadata"
    )
    network_stats: dict[str, Any] = Field(..., description="Network statistics")


class RelationshipStatistics(BaseModel):
    """Schema for relationship statistics"""

    total_relationships: int = Field(..., description="Total number of relationships")
    active_relationships: int = Field(..., description="Number of active relationships")
    relationship_types: dict[str, int] = Field(
        ..., description="Count by relationship type"
    )
    entity_types: dict[str, int] = Field(..., description="Count by entity type")
    top_connected_entities: list[dict[str, Any]] = Field(
        ..., description="Most connected entities"
    )
