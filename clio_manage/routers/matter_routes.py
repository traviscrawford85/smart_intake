from app.clio_client import clio_get
from app.db import SessionLocal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def list_matters(db: Session = Depends(get_db)):
    return await clio_get("/matters", db, {"limit": 5})
