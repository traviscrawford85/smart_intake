from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from clio_manage import config
from clio_manage.auth import (exchange_code_for_token, get_token_from_db,
                              refresh_access_token)
from clio_manage.db import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/authorize")
def authorize(state: str = "", scope: str = "all"):
    """
    Redirect user to Clio's OAuth2 authorization endpoint.
    """
    params = {
        "response_type": "code",
        "client_id": config.CLIO_CLIENT_ID,
        "redirect_uri": config.CLIO_REDIRECT_URI,
        "scope": scope,
        "state": state,
    }
    from urllib.parse import urlencode

    url = f"https://app.clio.com/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url)


@router.get("/callback")
async def auth_callback(
    request: Request,
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    db: Session = Depends(get_db),
):
    if error:
        return {
            "error": error,
            "description": request.query_params.get("error_description", ""),
        }
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")
    token = await exchange_code_for_token(code, db)
    return {"message": "Token saved", "token": token.access_token, "state": state}


@router.get("/token")
def get_token(db: Session = Depends(get_db)):
    token = get_token_from_db(db)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "expires_at": token.expires_at,
    }


@router.post("/refresh")
async def refresh_token(db: Session = Depends(get_db)):
    token = refresh_access_token(db)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found or refresh failed")
    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "expires_at": token.expires_at,
    }


@router.get("/status")
def token_status(db: Session = Depends(get_db)):
    token = get_token_from_db(db)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    return {"status": "active", "expires_at": token.expires_at.isoformat()}


@router.delete("/revoke")
def revoke_token(db: Session = Depends(get_db)):
    token = get_token_from_db(db)
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    db.delete(token)
    db.commit()
    return {"message": "Token revoked successfully"}
