from typing import List

from fastapi import APIRouter, Depends, HTTPException

from clio_manage.clio_base import ClioBaseModel
from clio_manage.schemas.tag import TagCreate, TagResponse, TagUpdate

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/", response_model=List[TagResponse])
async def list_tags():
    # TODO: Implement DB/service call
    return []


@router.post("/", response_model=TagResponse)
async def create_tag(tag: TagCreate):
    # TODO: Implement DB/service call
    return TagResponse(**tag.model_dump(), id=1)


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: int):
    # TODO: Implement DB/service call
    return TagResponse(id=tag_id, name="Sample Tag")


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, tag: TagUpdate):
    # TODO: Implement DB/service call
    return TagResponse(id=tag_id, **tag.model_dump())


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int):
    # TODO: Implement DB/service call
    return {"status": "deleted", "id": tag_id}
