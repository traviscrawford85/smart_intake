#!/usr/bin/env python3
"""
FastAPI proxy server for handling Clio lead submissions.
Receives leads from web forms or Capture Now bot and forwards them to Clio Grow.
"""

from typing import Any, Dict, Optional

import uvicorn
# Import our enhanced functions
from app.send_intake import (create_clio_lead,
                             create_clio_lead_from_any_payload,
                             map_envelope_to_clio_lead,
                             process_envelope_payload, validate_envelope)
from fastapi import FastAPI, HTTPException, Request, status
from loguru import logger
from pydantic import BaseModel, ValidationError

app = FastAPI(
    title="Clio Lead Intake Proxy",
    description="Proxy server for handling web form and voice agent leads to Clio Grow",
    version="1.0.0",
)


# Pydantic models for API documentation
class DirectPayload(BaseModel):
    """Direct payload from web forms (new Clio API format)."""

    inbox_lead: Dict[str, Any]
    inbox_lead_token: Optional[str] = None


class EnvelopePayload(BaseModel):
    """Envelope payload from Capture Now agent or similar sources."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    message: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    referring_url: Optional[str] = None
    source: Optional[str] = None


class LeadResponse(BaseModel):
    """Response from Clio lead creation."""

    status: str
    clio_lead_id: Optional[int] = None
    message: str
    data: Optional[Dict[str, Any]] = None


@app.post("/webhook/web-form", response_model=LeadResponse)
async def handle_web_form(payload: DirectPayload):
    """
    Handle direct payloads from web forms.
    Expects the new Clio API format with inbox_lead structure.
    """
    logger.info(
        "Received web form submission",
        extra={
            "has_inbox_lead": "inbox_lead" in payload.model_dump(),
            "inbox_lead_keys": (
                list(payload.inbox_lead.keys()) if payload.inbox_lead else []
            ),
        },
    )

    try:
        # Extract the inbox_lead data
        lead_data = payload.inbox_lead

        # Use our unified function to process any payload format
        response_data, status_code, saved_leads = create_clio_lead_from_any_payload(
            {"inbox_lead": lead_data}
        )

        if status_code == 201:
            clio_id = (
                response_data.get("id") if isinstance(response_data, dict) else None
            )
            return LeadResponse(
                status="success",
                clio_lead_id=clio_id,
                message="Lead created successfully in Clio",
                data=response_data,
            )
        else:
            raise HTTPException(
                status_code=status_code,
                detail=f"Failed to create lead in Clio: {response_data}",
            )

    except Exception as e:
        logger.error(f"Web form processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.post("/webhook/capture-now", response_model=LeadResponse)
async def handle_capture_now(payload: EnvelopePayload):
    """
    Handle envelope payloads from Capture Now voice agent.
    Expects envelope format with flat structure.
    """
    logger.info(
        "Received Capture Now agent submission",
        extra={
            "contact_name": f"{payload.first_name or ''} {payload.last_name or ''}".strip(),
            "source": payload.source,
            "has_message": bool(payload.message),
        },
    )

    try:
        # Convert Pydantic model to dict
        envelope_data = payload.model_dump(exclude_none=True)

        # Use our envelope processing function
        response_data, status_code = process_envelope_payload(envelope_data)

        if status_code == 201:
            clio_id = (
                response_data.get("inbox_lead", {}).get("id")
                if isinstance(response_data, dict)
                else None
            )
            return LeadResponse(
                status="success",
                clio_lead_id=clio_id,
                message="Voice agent lead created successfully in Clio",
                data=response_data,
            )
        else:
            raise HTTPException(
                status_code=status_code,
                detail=f"Failed to create voice agent lead in Clio: {response_data}",
            )

    except Exception as e:
        logger.error(f"Capture Now processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.post("/webhook/unified", response_model=LeadResponse)
async def handle_unified(request: Request):
    """
    Unified endpoint that auto-detects payload format.
    Handles both web forms and voice agent submissions.
    """
    try:
        # Get raw JSON payload
        payload = await request.json()

        logger.info(
            "Received unified submission",
            extra={
                "payload_keys": list(payload.keys()),
                "payload_size": len(str(payload)),
            },
        )

        # Use our unified function that handles any format
        response_data, status_code, saved_leads = create_clio_lead_from_any_payload(
            payload
        )

        # Handle different response types
        if isinstance(response_data, dict) and "total_leads" in response_data:
            # Multiple leads processed (envelope format)
            return LeadResponse(
                status=(
                    "success"
                    if response_data["successful"] == response_data["total_leads"]
                    else "partial"
                ),
                message=f"Processed {response_data['successful']}/{response_data['total_leads']} leads",
                data=response_data,
            )
        elif status_code == 201:
            # Single lead processed successfully
            clio_id = (
                response_data.get("id") if isinstance(response_data, dict) else None
            )
            return LeadResponse(
                status="success",
                clio_lead_id=clio_id,
                message="Lead created successfully in Clio",
                data=response_data,
            )
        else:
            raise HTTPException(
                status_code=status_code,
                detail=f"Failed to process lead: {response_data}",
            )

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unified processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.post("/webhook/legacy", response_model=LeadResponse)
async def handle_legacy(envelope: Dict[str, Any]):
    """
    Legacy endpoint for simple envelope processing.
    Uses the basic create_clio_lead function.
    """
    logger.info(
        "Received legacy submission", extra={"envelope_keys": list(envelope.keys())}
    )

    try:
        # Use the main create_clio_lead function
        response_data, status_code = create_clio_lead(envelope)

        if status_code == 201:
            clio_id = (
                response_data.get("id") if isinstance(response_data, dict) else None
            )
            return LeadResponse(
                status="success",
                clio_lead_id=clio_id,
                message="Legacy lead created successfully in Clio",
                data=response_data,
            )
        else:
            raise HTTPException(
                status_code=status_code,
                detail=f"Failed to create legacy lead in Clio: {response_data}",
            )

    except Exception as e:
        logger.error(f"Legacy processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Clio Lead Intake Proxy"}


@app.get("/validate/{endpoint}")
async def validate_endpoint(endpoint: str):
    """Validate if an endpoint can handle envelope data."""
    validation_envelope = {
        "first_name": "Test",
        "last_name": "User",
        "message": "Test message",
        "referring_url": "https://test.com",
        "source": "API Test",
    }

    missing_fields = validate_envelope(validation_envelope)
    mapped_payload = map_envelope_to_clio_lead(validation_envelope)

    return {
        "endpoint": endpoint,
        "validation": {
            "missing_fields": missing_fields,
            "is_valid": len(missing_fields) == 0,
            "mapped_payload_structure": list(mapped_payload.keys()),
            "inbox_lead_fields": list(mapped_payload["inbox_lead"].keys()),
        },
    }


if __name__ == "__main__":
    logger.info("🚀 Starting Clio Lead Intake Proxy Server")

    # Run the server
    uvicorn.run(
        "fastapi_proxy:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
