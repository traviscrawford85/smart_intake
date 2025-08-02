from typing import Optional

from pydantic import BaseModel


class NoteBase(BaseModel):
    subject: Optional[str] = None
    body: str
    contact_id: Optional[int] = None
    matter_id: Optional[int] = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
