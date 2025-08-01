
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import config
from app.db import Token

TOKEN_URL = "https://app.clio.com/oauth/token"

def get_token_from_db(db: Session):
    return db.query(Token).first()

def save_token_to_db(db: Session, access_token: str, refresh_token: str, expires_in: int):
    token = db.query(Token).first()
    if not token:
        token = Token(access_token=access_token, refresh_token=refresh_token)
        db.add(token)
    else:
        token.access_token = access_token
        token.refresh_token = refresh_token
    token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
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
            "code": code
        }
        response = await client.post(TOKEN_URL, data=data)
        response.raise_for_status()
        token_data = response.json()
        return save_token_to_db(db, token_data["access_token"], token_data.get("refresh_token"), token_data["expires_in"])
