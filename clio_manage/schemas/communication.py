from typing import List, Optional

from pydantic import BaseModel, Field


class CommunicationBase(BaseModel):
    subject: str
    body: Optional[str] = None
    contact_ids: Optional[List[int]] = None
    matter_id: Optional[int] = None
    sent_at: Optional[str] = None


class CommunicationCreate(CommunicationBase):
    pass


class CommunicationUpdate(CommunicationBase):
    pass


class CommunicationResponse(CommunicationBase):
    id: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
