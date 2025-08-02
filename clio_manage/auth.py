from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from clio_manage import config
from clio_manage.db import Token

TOKEN_URL = "https://app.clio.com/oauth/token"


def refresh_access_token(db: Session):
    """
    Refresh the access token using the stored refresh token.
    """
    token = get_token_from_db(db)
    if not token or not token.refresh_token:
        return None
    data = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
        "client_id": config.CLIO_CLIENT_ID,
        "client_secret": config.CLIO_CLIENT_SECRET,
        "redirect_uri": config.CLIO_REDIRECT_URI,
    }
    with httpx.Client() as client:
        response = client.post(TOKEN_URL, data=data)
        if response.status_code != 200:
            return None
        token_data = response.json()
        return save_token_to_db(
            db,
            token_data["access_token"],
            token_data.get("refresh_token", token.refresh_token),
            token_data["expires_in"],
            token.app_id,
            token.integration,
        )


from sqlalchemy.orm import Session

TOKEN_URL = "https://app.clio.com/oauth/token"


def get_token_from_db(db: Session):
    return db.query(Token).first()


def save_token_to_db(
    db: Session,
    access_token: str,
    refresh_token: str,
    expires_in: int,
    app_id: Optional[str] = None,
    integration: Optional[str] = None,
):
    token = db.query(Token).first()
    if not token:
        token = Token()
        db.add(token)
    object.__setattr__(token, "access_token", access_token)
    object.__setattr__(token, "refresh_token", refresh_token)
    object.__setattr__(token, "app_id", app_id)
    object.__setattr__(token, "integration", integration)
    object.__setattr__(
        token, "expires_at", datetime.utcnow() + timedelta(seconds=expires_in)
    )
    db.commit()
    db.refresh(token)
    return token


async def exchange_code_for_token(code: str, db: Session):
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "authorization_code",
            "client_id": config.CLIO_CLIENT_ID,
            "client_secret": config.CLIO_CLIENT_SECRET,
            "redirect_uri": config.CLIO_REDIRECT_URI,
            "code": code,
        }
        response = await client.post(TOKEN_URL, data=data)
        response.raise_for_status()
        token_data = response.json()
        return save_token_to_db(
            db,
            token_data["access_token"],
            token_data.get("refresh_token"),
            token_data["expires_in"],
        )
