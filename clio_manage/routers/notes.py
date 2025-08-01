from typing import List

from fastapi import APIRouter, Depends, HTTPException

from clio_manage.clio_base import ClioBaseModel
from clio_manage.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/", response_model=List[NoteResponse])
async def list_notes():
    # TODO: Implement DB/service call
    return []


@router.post("/", response_model=NoteResponse)
async def create_note(note: NoteCreate):
    # TODO: Implement DB/service call
    return NoteResponse(**note.model_dump(), id=1)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int):
    # TODO: Implement DB/service call
    return NoteResponse(id=note_id, body="Sample note body")


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: NoteUpdate):
    # TODO: Implement DB/service call
    return NoteResponse(id=note_id, **note.model_dump())


@router.delete("/{note_id}")
async def delete_note(note_id: int):
    # TODO: Implement DB/service call
    return {"status": "deleted", "id": note_id}
