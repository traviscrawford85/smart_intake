from fastapi import APIRouter

from .communications import router as communications_router
from .contacts import router as contacts_router
from .notes import router as notes_router
from .tags import router as tags_router
from .triage_routes import router as triage_router
from .webhooks import router as webhooks_router

api_router = APIRouter()
api_router.include_router(contacts_router)
api_router.include_router(notes_router)
api_router.include_router(communications_router)
api_router.include_router(tags_router)
api_router.include_router(webhooks_router)
api_router.include_router(triage_router)
