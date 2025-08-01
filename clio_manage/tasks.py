
from celery import Celery
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.clio_client import clio_get

celery = Celery(__name__, broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

@celery.task
def check_matter_deadlines():
    db = SessionLocal()
    params = {"limit": 200, "offset": 0}
    results = []
    while True:
        data = asyncio.run(clio_get("/matters", db, params))
        results.extend(data.get("matters", []))
        if len(data.get("matters", [])) < 200:
            break
        params["offset"] += 200
    print(f"Fetched {len(results)} matters.")
    # TODO: Deadline logic
