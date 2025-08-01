from typing import List

from fastapi import APIRouter, Depends, HTTPException

from clio_manage.clio_base import ClioBaseModel
from clio_manage.schemas.contact import (
    ContactCreate,
    ContactResponse,
    ContactUpdate,
)

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("/", response_model=List[ContactResponse])
async def list_contacts():
    # TODO: Implement DB/service call
    return []


@router.post("/", response_model=ContactResponse)
async def create_contact(contact: ContactCreate):
    # TODO: Implement DB/service call
    return ContactResponse(**contact.model_dump(), id=1)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int):
    # TODO: Implement DB/service call
    return ContactResponse(id=contact_id, first_name="John", last_name="Doe")


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, contact: ContactUpdate):
    # TODO: Implement DB/service call
    return ContactResponse(id=contact_id, **contact.model_dump())


@router.delete("/{contact_id}")
async def delete_contact(contact_id: int):
    # TODO: Implement DB/service call
    return {"status": "deleted", "id": contact_id}
