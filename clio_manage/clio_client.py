
import httpx
from sqlalchemy.orm import Session
from app.auth import get_token_from_db
from app.config import CLIO_API_BASE, CLIO_API_VERSION

async def clio_get(endpoint: str, db: Session, params: dict = None):
    token = get_token_from_db(db)
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "X-API-VERSION": CLIO_API_VERSION
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{CLIO_API_BASE}{endpoint}", headers=headers, params=params)
        response.raise_for_status()
        return response.json()
