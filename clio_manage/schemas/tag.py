from typing import Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagResponse(TagBase):
    id: int
