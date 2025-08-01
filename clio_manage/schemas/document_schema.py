"""
Pydantic schemas for Document API responses
"""

from datetime import datetime

from pydantic import BaseModel


class DocumentBase(BaseModel):
    """Base document schema for creation/updates"""

    clio_id: str | None = None
    name: str
    category: str | None = None
    is_signed: bool = False
    is_locked: bool = False
    shared: bool = False


class Document(DocumentBase):
    """Full document schema for API responses"""

    id: int

    # File details
    size: int | None = None
    content_type: str | None = None
    uuid: str | None = None

    # Document organization
    parent_id: str | None = None

    # Document status
    is_trashed: bool = False
    is_image: bool = False
    is_pdf: bool = False

    # Sharing settings
    shared_with_client: bool = False
    client_visible: bool = False

    # Tags and metadata
    tags: list | None = None

    # Relationships
    matter_id: int | None = None
    clio_matter_id: str | None = None

    # Version information
    latest_document_version_data: dict | None = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    clio_created_at: datetime | None = None
    clio_updated_at: datetime | None = None

    class Config:
        from_attributes = True


class DocumentCreate(DocumentBase):
    """Schema for creating documents"""

    matter_id: int | None = None


class DocumentUpdate(BaseModel):
    """Schema for updating documents"""

    name: str | None = None
    category: str | None = None
    is_signed: bool | None = None
    shared: bool | None = None


class DocumentVersionBase(BaseModel):
    """Base document version schema"""

    clio_id: str | None = None
    file_name: str
    size: int | None = None
    content_type: str | None = None


class DocumentVersion(DocumentVersionBase):
    """Full document version schema"""

    id: int
    uuid: str | None = None
    version_number: int | None = None
    fully_uploaded: bool = False

    # Relationships
    document_id: int | None = None
    clio_document_id: str | None = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    clio_created_at: datetime | None = None
    clio_updated_at: datetime | None = None

    class Config:
        from_attributes = True
