from typing import List

from fastapi import APIRouter

from clio_manage.schemas.communication import (
    CommunicationCreate,
    CommunicationResponse,
    CommunicationUpdate,
)

router = APIRouter(prefix="/communications", tags=["Communications"])


@router.get("/", response_model=List[CommunicationResponse])
async def list_communications():
    # TODO: Implement DB/service call
    return []


@router.post("/", response_model=CommunicationResponse)
async def create_communication(comm: CommunicationCreate):
    # TODO: Implement DB/service call
    return CommunicationResponse(**comm.model_dump(), id=1)


@router.get("/{comm_id}", response_model=CommunicationResponse)
async def get_communication(comm_id: int):
    # TODO: Implement DB/service call
    return CommunicationResponse(id=comm_id, subject="Sample subject")


@router.put("/{comm_id}", response_model=CommunicationResponse)
async def update_communication(comm_id: int, comm: CommunicationUpdate):
    # TODO: Implement DB/service call
    return CommunicationResponse(id=comm_id, **comm.model_dump())


@router.delete("/{comm_id}")
async def delete_communication(comm_id: int):
    # TODO: Implement DB/service call
    return {"status": "deleted", "id": comm_id}
