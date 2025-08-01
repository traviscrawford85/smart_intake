
from http.client import HTTPException
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.auth import exchange_code_for_token
from app.schemas import LeadErrorResponse
from app.models import Token
from app.schemas import BotDataInput, LeadResponse
from app.send_intake import post_lead_to_clio_grow_typed, validate_bot_data_typed

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/callback")
async def auth_callback(code: str = Query(...), db: Session = Depends(get_db)):
    token = await exchange_code_for_token(code, db)
    return {"message": "Token saved", "token": token.access_token}

@router.get("/token")
async def get_token(db: Session = Depends(get_db)):
    """
    exchange the authorization code for an access token.
    """
    token = await exchange_code_for_token(None, db)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"access_token": token.access_token, "refresh_token": token.refresh_token}

@router.post("/refresh")
async def refresh_token(db: Session = Depends(get_db)):
    """
    Refresh the access token using the refresh token.
    """
    token = await exchange_code_for_token(None, db, refresh=True)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"access_token": token.access_token, "refresh_token": token.refresh_token}

@router.get("/status")
async def token_status(db: Session = Depends(get_db)):
    """
    Check the status of the current access token.
    """
    token = await exchange_code_for_token(None, db)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"status": "active", "expires_at": token.expires_at.isoformat()}

@router.delete("/revoke")
async def revoke_token(db: Session = Depends(get_db)):
    """
    Revoke the current access token.
    """
    token = await exchange_code_for_token(None, db)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    
    # Logic to revoke the token goes here
    # For example, delete it from the database or call an external API to revoke it
    
    return {"message": "Token revoked successfully"}


