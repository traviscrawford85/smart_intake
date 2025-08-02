from datetime import datetime

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from clio_manage.schemas import ContactCreate
from clio_manage.services.triage_service import TriageService

router = APIRouter(prefix="/triage", tags=["Triage"])

triage_service = TriageService()

from typing import Optional


class TriageRequest(BaseModel):
    lead: ContactCreate
    note: str
    assignee_id: str
    due_at: Optional[str] = None  # ISO8601 string, optional
    communication_body: Optional[str] = None
    lead_tag_id: Optional[str] = None
    notify_email: Optional[str] = None


@router.post("/lead_review")
async def lead_review(request: TriageRequest):
    try:
        async with httpx.AsyncClient() as client:
            result = await triage_service.triage_lead(
                client=client,
                lead_data=request.lead.dict(),
                note_content=request.note,
                assignee_id=request.assignee_id,
                due_at=(
                    datetime.fromisoformat(request.due_at) if request.due_at else None
                ),
                communication_body=request.communication_body,
                lead_tag_id=request.lead_tag_id,
                notify_email=request.notify_email,
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
