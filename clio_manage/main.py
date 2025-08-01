from fastapi import FastAPI

from clio_manage.routers import api_router

app = FastAPI(title="Clio Manage Backend API")

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
