"""Clio Base Model for shared fields across schemas. It supports normalization and recursive field population."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from clio_manage.utils.recursive_field_normalizer import recursive_normalize


class ClioBaseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def normalize_any(cls, v):
        # This will normalize each field, including nested dicts/lists
        return recursive_normalize(v)

    id: Optional[int] = None
    created_at: Optional[str] = Field(
        None, description="Creation timestamp in ISO format"
    )
    updated_at: Optional[str] = Field(
        None, description="Last update timestamp in ISO format"
    )
    errors: Optional[Dict[str, Any]] = Field(None, description="Error details if any")

    class Config:
        """Pydantic configuration."""

        orm_mode = True
        allow_population_by_field_name = True
        use_enum_values = True
