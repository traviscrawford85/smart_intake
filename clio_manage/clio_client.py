from typing import Optional

import httpx
from auth import get_token_from_db
from config import CLIO_API_BASE, CLIO_API_VERSION
from sqlalchemy.orm import Session


async def clio_get(endpoint: str, db: Session, params: Optional[dict] = None):
    token = get_token_from_db(db)
    if token is None or not hasattr(token, "access_token"):
        raise ValueError("No valid access token found in the database.")
    headers = {
        "Authorization": f"Bearer {token.access_token}",
        "X-API-VERSION": CLIO_API_VERSION,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CLIO_API_BASE}{endpoint}", headers=headers, params=params
        )
        response.raise_for_status()
        return response.json()
