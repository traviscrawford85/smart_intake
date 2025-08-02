from fastapi import APIRouter, Request

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/receive")
async def receive_webhook(request: Request):
    payload = await request.json()
    # TODO: Validate and process webhook payload
    return {"status": "received", "payload": payload}
