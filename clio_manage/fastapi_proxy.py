"""
FastAPI integration example for handling multiple payload formats.
This shows how to use the payload parser in a FastAPI proxy server.
"""

from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel

from app.lead_parser import auto_parse_lead_data
from app.send_intake import (
    create_clio_lead_from_any_payload,
    post_lead_to_clio_grow_typed,
)


def _flatten_response_list(responses):
    """Helper to ensure all items are dicts, not tuples."""
    result = []
    for r in responses:
        if isinstance(r, tuple) and isinstance(r[0], dict):
            result.append(r[0])
        else:
            result.append(r)
    return result

app = FastAPI(
    title="Clio Intake Proxy API",
    description="Unified proxy for handling web forms and Capture Now agent payloads",
    version="1.0.0"
)

class GenericPayload(BaseModel):
    """Generic payload that accepts any structure."""
    payload: Dict[str, Any]

class ProcessingResult(BaseModel):
    """Result of payload processing."""
    success: bool
    total_leads: int
    successful_leads: int
    failed_leads: int
    clio_responses: List[Dict[str, Any]]
    errors: List[str] = []

@app.post("/webhook/clio-intake", response_model=ProcessingResult)
async def receive_intake_payload(payload: Dict[str, Any]):
    """
    Unified webhook endpoint for receiving intake data from any source.
    Supports:
    - Web form direct payloads
    - Capture Now agent envelope payloads
    - Mixed/flattened payloads
    """
    logger.info("Received intake webhook", extra={
        "payload_keys": list(payload.keys()),
        "payload_size": len(str(payload)),
        "has_inbox_leads": "inbox_leads" in payload,
        "lead_count": len(payload.get("inbox_leads", [])) if "inbox_leads" in payload else 1
    })

    try:
        # Check if payload contains inbox_leads (multiple leads)
        if "inbox_leads" in payload:
            leads = payload["inbox_leads"]
            results = []
            successful = 0
            failed = 0

            for lead in leads:
                try:
                    bot_data = auto_parse_lead_data(lead)
                    response_data, status_code, _ = post_lead_to_clio_grow_typed(bot_data)
                    results.append(response_data)
                    if status_code == 201:
                        successful += 1
                    else:
                        failed += 1
                except Exception as lead_error:
                    logger.error("Failed to process individual lead", extra={
                        "error": str(lead_error),
                        "lead_data_keys": list(lead.keys()) if isinstance(lead, dict) else "invalid_lead_format"
                    })
                    failed += 1
                    results.append({"error": str(lead_error)})

            # Log processing summary
            logger.info("Batch processing completed", extra={
                "total_leads": len(leads),
                "successful": successful,
                "failed": failed,
                "success_rate": f"{(successful/len(leads)*100):.1f}%" if leads else "0%"
            })

            return ProcessingResult(
                success=successful == len(leads),
                total_leads=len(leads),
                successful_leads=successful,
                failed_leads=failed,
                clio_responses=_flatten_response_list(results),
                errors=[],
            )
        else:
            # Single lead processing - fallback to original logic
            response_data, status_code, _ = create_clio_lead_from_any_payload(payload)

            # Handle batch-style response (very rare on this path)
            if isinstance(response_data, dict) and "total_leads" in response_data and "results" in response_data:
                return ProcessingResult(
                    success=status_code in [201, 207],
                    total_leads=response_data.get("total_leads", 1),
                    successful_leads=response_data.get("successful", 0),
                    failed_leads=response_data.get("failed", 0),
                    clio_responses=_flatten_response_list(response_data["results"]),
                    errors=[]
                )
            else:
                return ProcessingResult(
                    success=status_code == 201,
                    total_leads=1,
                    successful_leads=1 if status_code == 201 else 0,
                    failed_leads=0 if status_code == 201 else 1,
                    clio_responses=_flatten_response_list([response_data]),
                    errors=[] if status_code == 201 else [str(response_data)]
                )
    except Exception as e:
        logger.error("Webhook processing failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "payload_structure": {
                "has_inbox_leads": "inbox_leads" in payload,
                "has_inbox_lead": "inbox_lead" in payload, 
                "top_level_keys": list(payload.keys())
            }
        })
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process payload: {str(e)}"
        )

@app.post("/webhook/direct", response_model=ProcessingResult)
async def receive_direct_payload(payload: Dict[str, Any]):
    """
    Endpoint specifically for direct payloads from web forms.
    """
    logger.info("Received direct payload", extra={"has_inbox_lead": "inbox_lead" in payload})

    if "inbox_lead" not in payload:
        raise HTTPException(
            status_code=422,
            detail="Direct payload must contain 'inbox_lead' field"
        )

    return await receive_intake_payload(payload)

@app.post("/webhook/envelope", response_model=ProcessingResult)
async def receive_envelope_payload(payload: Dict[str, Any]):
    """
    Endpoint specifically for envelope payloads from Capture Now agent.
    """
    logger.info("Received envelope payload", extra={"has_inbox_leads": "inbox_leads" in payload})

    if "inbox_leads" not in payload:
        raise HTTPException(
            status_code=422,
            detail="Envelope payload must contain 'inbox_leads' field"
        )

    return await receive_intake_payload(payload)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "clio-intake-proxy"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Clio Intake Proxy API",
        "version": "1.0.0",
        "endpoints": {
            "/webhook/clio-intake": "Unified endpoint for any payload format",
            "/webhook/direct": "Direct payloads from web forms",
            "/webhook/envelope": "Envelope payloads from Capture Now agent",
            "/health": "Health check",
            "/docs": "API documentation"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Clio Intake Proxy API")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
