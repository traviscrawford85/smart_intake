"""
Clio Grow Lead Inbox Submission Module with Pydantic v2 and SQLAlchemy 2.0 support.

This module provides typed functions to send new intake leads to the Clio Grow Lead Inbox API,
maintaining the correct request structure as required by Clio's latest documentation.
"""
import base64
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.orm import Session

# Load environment variables from multiple possible locations
load_dotenv()  # Current directory
load_dotenv('.env')  # Explicit current directory
load_dotenv('../.env')  # Parent directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))  # Project root

from app.lead_parser import LeadDataParser, auto_parse_lead_data
from app.models import IntakeLead
from app.payload_parser import normalize_to_clio_format, parse_incoming_payload
from app.schemas import (
    BotDataInput,
    ClioErrorResponse,
    ClioGrowPayload,
    ClioInboxLead,
    LeadErrorResponse,
    LeadResponse,
)

# === CONFIGURATION ===
CLIO_GROW_INBOX_URL = os.getenv("CLIO_GROW_INBOX_URL", "https://grow.clio.com/inbox_leads")
LEAD_INBOX_TOKEN = os.getenv("LEAD_INBOX_TOKEN", "YOUR_LEAD_INBOX_TOKEN")

# === FIELD MAPPING CONFIGURATION ===
# Voice agent/bot fields mapped to Clio API fields
FIELD_MAPPING = {
    "first_name": "from_first",
    "last_name": "from_last", 
    "message": "from_message",
    "email": "from_email",
    "phone_number": "from_phone",
    "referring_url": "referring_url",
    "source": "from_source"
}

# Required fields with safe fallbacks
REQUIRED_FIELDS_WITH_FALLBACKS = {
    "first_name": "Unknown",
    "last_name": "Contact", 
    "message": "Voice agent intake submission",
    "referring_url": "https://intake-system.local",
    "source": "Voice Agent Bot"
}

# Required fields for validation
REQUIRED_FIELDS = ["first_name", "last_name", "message", "referring_url", "source"]

# Configure loguru logger - focus on actionable, high-value information
logger.remove()  # Remove default handler

# File logging - structured for parsing and analysis
logger.add(
    "logs/clio_intake.log",
    rotation="10 MB",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {function}:{line} | {message}",
    backtrace=False,  # Suppress noisy tracebacks
    diagnose=False,   # Remove sensitive info from logs
    enqueue=True,     # Thread-safe logging
    serialize=True    # JSON structured logging for better parsing
)

# Console logging - clean, actionable output only
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO", 
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    backtrace=False,
    diagnose=False,
    filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "CRITICAL"]  # Skip DEBUG
)

# === EXAMPLE BOT DATA ===
bot_data = {
    "first_name": "Minnie",
    "last_name": "mouse",
    "message": "This is a sample transcript from the voice agent.",
    "email": "mini.mouse@disney.plus.com",
    "phone_number": "4045141488",
    "referring_url": "http://lcx.com",
    "source": "Capture Now Bot"
}

def validate_required_fields(bot_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate required fields and apply safe fallbacks to avoid 422 errors.
    
    Args:
        bot_data: Raw bot data dictionary
        
    Returns:
        Validated bot data with fallbacks applied
        
    Raises:
        Exception: If critical validation fails
    """
    logger.info("Validating bot data", extra={"data_keys": list(bot_data.keys())})
    
    # Check required fields
    required_fields = ["first_name", "last_name", "message", "referring_url", "source"]
    missing = [f for f in required_fields if not bot_data.get(f)]
    
    if missing:
        logger.warning("Missing required fields, applying fallbacks", extra={"missing_fields": missing})
        
        # Apply safe fallbacks to prevent 422 errors
        validated_data = bot_data.copy()
        for field in missing:
            if field in REQUIRED_FIELDS_WITH_FALLBACKS:
                validated_data[field] = REQUIRED_FIELDS_WITH_FALLBACKS[field]
                logger.info(f"Applied fallback for {field}", extra={"fallback_value": validated_data[field]})
        
        return validated_data
    
    logger.info("All required fields present", extra={"field_count": len(required_fields)})
    return bot_data


def map_voice_agent_fields(bot_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map voice agent/bot fields to Clio API field names.
    
    Args:
        bot_data: Bot data with original field names
        
    Returns:
        Mapped data with Clio-compatible field names
    """
    mapped_data = {}
    
    for bot_field, clio_field in FIELD_MAPPING.items():
        if bot_field in bot_data and bot_data[bot_field] is not None:
            mapped_data[bot_field] = bot_data[bot_field]
    
    # Ensure all fields are present with safe defaults
    for field, fallback in REQUIRED_FIELDS_WITH_FALLBACKS.items():
        if field not in mapped_data or not mapped_data[field]:
            mapped_data[field] = fallback
    
    logger.info("Field mapping completed", extra={
        "original_fields": len(bot_data),
        "mapped_fields": len(mapped_data)
    })
    
    return mapped_data


def validate_envelope(envelope: dict) -> list[str]:
    """Return a list of missing required fields."""
    missing = [f for f in REQUIRED_FIELDS if not envelope.get(f)]
    return missing


def map_envelope_to_clio_lead(envelope: dict) -> dict:
    """Map Capture Now envelope fields to Clio Grow Lead Inbox payload."""
    return {
        "inbox_lead": {
            "from_first": envelope.get("first_name", "Unknown"),
            "from_last": envelope.get("last_name", "Unknown"),
            "from_message": envelope.get("message", ""),   # Full transcript, fine to send as-is
            "from_email": envelope.get("email", ""),
            "from_phone": envelope.get("phone_number", ""),
            "referring_url": envelope.get("referring_url", "phone"),
            "from_source": envelope.get("source", "Capture Now Bot"),
        }
        # inbox_lead_token will be added in your main POST code!
    }


def process_envelope_payload(envelope: dict) -> Tuple[dict, int]:
    """
    Process a Capture Now envelope payload and send it to Clio.
    
    Args:
        envelope: Raw envelope data from Capture Now voice agent
        
    Returns:
        Tuple of (response_data, status_code)
    """
    logger.info("Processing Capture Now envelope payload", extra={
        "envelope_keys": list(envelope.keys()),
        "has_message": bool(envelope.get("message")),
        "contact_name": f"{envelope.get('first_name', '')} {envelope.get('last_name', '')}"
    })
    
    # Validate the envelope
    missing_fields = validate_envelope(envelope)
    if missing_fields:
        logger.warning("Envelope missing required fields", extra={"missing_fields": missing_fields})
    
    # Map envelope to Clio payload format
    payload = map_envelope_to_clio_lead(envelope)
    
    # Add the token
    payload["inbox_lead_token"] = LEAD_INBOX_TOKEN
    
    logger.info("Envelope mapped to Clio format", extra={
        "payload_keys": list(payload.keys()),
        "inbox_lead_keys": list(payload["inbox_lead"].keys())
    })
    
    # Send to Clio
    try:
        response = requests.post(
            CLIO_GROW_INBOX_URL, 
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info("Received Clio response for envelope", extra={
            "status_code": response.status_code,
            "response_size": len(response.content) if response.content else 0
        })
        
        # Parse response
        try:
            response_data = response.json()
        except ValueError as e:
            logger.error("Failed to parse JSON response for envelope", extra={"error": str(e)})
            response_data = {"error": "Invalid JSON response from Clio"}
        
        # Log result
        if response.status_code == 201:
            logger.info("Envelope lead created successfully", extra={
                "clio_lead_id": response_data.get("id"),
                "contact_name": f"{envelope.get('first_name', '')} {envelope.get('last_name', '')}"
            })
        else:
            logger.error("Envelope lead creation failed", extra={
                "status_code": response.status_code,
                "response": response_data
            })
        
        return response_data, response.status_code
        
    except requests.RequestException as e:
        error_response = {"error": f"Request failed: {str(e)}"}
        logger.error("Envelope request failed", extra={"error": str(e)})
        return error_response, 500


def validate_bot_data_typed(data: dict) -> BotDataInput:
    """Validate and parse bot data using Pydantic schema."""
    try:
        # First validate required fields and apply fallbacks
        validated_data = validate_required_fields(data)
        
        # Map voice agent fields to standard format
        mapped_data = map_voice_agent_fields(validated_data)
        
        # Parse with Pydantic
        return BotDataInput(**mapped_data)
    except ValidationError as e:
        logger.error("Pydantic validation failed", extra={"errors": str(e)})
        raise ValueError(f"Invalid bot data: {e}")
    except Exception as e:
        logger.error("Unexpected validation error", extra={"error": str(e)})
        raise


def create_intake_lead_db(bot_data: BotDataInput, db: Session) -> IntakeLead:
    """Create and save an IntakeLead to the database."""
    lead = IntakeLead(
        first_name=bot_data.first_name,
        last_name=bot_data.last_name,
        message=bot_data.message,
        email=bot_data.email,
        phone_number=bot_data.phone_number,
        referring_url=str(bot_data.referring_url),
        source=bot_data.source,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def map_to_clio_format(bot_data: BotDataInput) -> ClioInboxLead:
    """Map validated bot data to Clio Grow format."""
    return ClioInboxLead(
        from_first=bot_data.first_name,
        from_last=bot_data.last_name,
        from_message=bot_data.message,
        from_email=bot_data.email or "",
        from_phone=bot_data.phone_number or "",
        referring_url=str(bot_data.referring_url),
        from_source=bot_data.source,
    )


def post_lead_to_clio_grow_typed(
    bot_data: BotDataInput, 
    db: Optional[Session] = None
) -> Tuple[dict, int, Optional[IntakeLead]]:
    """
    Post validated bot data to Clio Grow Lead Inbox API with full typing support.
    
    Args:
        bot_data: Validated Pydantic model with lead data
        db: Optional database session to save lead locally
        
    Returns:
        Tuple of (response_data, status_code, saved_lead_model)
    """
    logger.info("Starting Clio lead submission", extra={
        "lead_name": f"{bot_data.first_name} {bot_data.last_name}",
        "source": bot_data.source,
        "has_email": bool(bot_data.email),
        "has_phone": bool(bot_data.phone_number)
    })
    
    # Map to Clio format
    clio_lead = map_to_clio_format(bot_data)
    
    # Create payload exactly as documented
    payload = ClioGrowPayload(
        inbox_lead=clio_lead,
        inbox_lead_token=LEAD_INBOX_TOKEN
    )
    
    # Log payload structure (without sensitive data)
    logger.info("Payload created", extra={
        "payload_structure": {
            "has_inbox_lead": "inbox_lead" in payload.model_dump(),
            "has_token": "inbox_lead_token" in payload.model_dump(),
            "token_length": len(LEAD_INBOX_TOKEN) if LEAD_INBOX_TOKEN != "YOUR_LEAD_INBOX_TOKEN" else 0
        }
    })
    
    # Save to database if session provided
    saved_lead = None
    if db:
        try:
            saved_lead = create_intake_lead_db(bot_data, db)
            logger.info("Lead saved to database", extra={"lead_id": saved_lead.id})
        except Exception as e:
            logger.error("Failed to save lead to database", extra={"error": str(e)})
    
    # Send to Clio with comprehensive error handling
    try:
        logger.info("Sending request to Clio", extra={"url": CLIO_GROW_INBOX_URL})
        
        response = requests.post(
            CLIO_GROW_INBOX_URL, 
            json=payload.model_dump(),
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        logger.info("Received Clio response", extra={
            "status_code": response.status_code,
            "response_size": len(response.content) if response.content else 0
        })
        
        # Parse response
        try:
            response_data = response.json()
        except ValueError as e:
            logger.error("Failed to parse JSON response", extra={"error": str(e)})
            response_data = {"error": "Invalid JSON response from Clio"}
        
        # Handle different response codes
        if response.status_code == 201:
            # Success
            logger.info("Lead created successfully", extra={
                "clio_lead_id": response_data.get("id"),
                "lead_name": f"{bot_data.first_name} {bot_data.last_name}"
            })
            
            if saved_lead and db:
                clio_id = response_data.get("id")
                if clio_id:
                    try:
                        clio_lead_id = int(clio_id) if clio_id else None
                        if clio_lead_id:
                            saved_lead.mark_sent_to_clio(
                                clio_lead_id=clio_lead_id,
                                status="sent",
                                response=str(response_data)
                            )
                            db.commit()
                            logger.info("Database updated with Clio response", extra={"clio_id": clio_lead_id})
                    except (ValueError, TypeError) as e:
                        logger.error("Failed to parse Clio lead ID", extra={"clio_id": clio_id, "error": str(e)})
                    
        elif response.status_code == 401:
            # Authentication error
            logger.error("Authentication failed - Invalid Lead Inbox Token", extra={
                "token_configured": LEAD_INBOX_TOKEN != "YOUR_LEAD_INBOX_TOKEN",
                "response": response_data
            })
            
            if saved_lead and db:
                saved_lead.clio_status = "auth_failed"
                saved_lead.clio_response = str(response_data)
                db.commit()
                
        elif response.status_code == 422:
            # Validation error
            errors_data = {}
            if isinstance(response_data, dict) and "inbox_lead" in response_data:
                inbox_lead = response_data["inbox_lead"]
                if isinstance(inbox_lead, dict) and "errors" in inbox_lead:
                    errors_data = inbox_lead["errors"]
            
            logger.warning("Validation error from Clio", extra={
                "errors": errors_data,
                "lead_data": {
                    "first_name": bot_data.first_name,
                    "last_name": bot_data.last_name,
                    "has_message": bool(bot_data.message),
                    "source": bot_data.source
                }
            })
            
            if saved_lead and db:
                saved_lead.clio_status = "validation_failed"
                saved_lead.clio_response = str(response_data)
                db.commit()
                
        else:
            # Unexpected error
            logger.error("Unexpected response from Clio", extra={
                "status_code": response.status_code,
                "response": response_data
            })
            
            if saved_lead and db:
                saved_lead.clio_status = "failed"
                saved_lead.clio_response = str(response_data)
                db.commit()
            
        return response_data, response.status_code, saved_lead
        
    except requests.Timeout:
        error_response = {"error": "Request timed out after 30 seconds"}
        logger.error("Request timeout", extra={"timeout": 30})
        
        if saved_lead and db:
            saved_lead.clio_status = "timeout"
            saved_lead.clio_response = str(error_response)
            db.commit()
        return error_response, 500, saved_lead
        
    except requests.ConnectionError as e:
        error_response = {"error": f"Connection failed: {str(e)}"}
        logger.error("Connection error", extra={"error": str(e)})
        
        if saved_lead and db:
            saved_lead.clio_status = "connection_error"
            saved_lead.clio_response = str(error_response)
            db.commit()
        return error_response, 500, saved_lead
        
    except requests.RequestException as e:
        error_response = {"error": f"Request failed: {str(e)}"}
        logger.error("Request exception", extra={"error": str(e)})
        
        if saved_lead and db:
            saved_lead.clio_status = "error"
            saved_lead.clio_response = str(error_response)
            db.commit()
        return error_response, 500, saved_lead


def create_clio_lead_from_any_payload(payload: dict, db: Optional[Session] = None) -> Tuple[dict, int, Optional[List[IntakeLead]]]:
    """
    Main function to create Clio leads from any payload format.
    Handles direct payloads, envelope payloads, and mixed formats.
    
    Args:
        payload: Raw payload from any source (web form, Capture Now agent, etc.)
        db: Optional database session to save leads locally
        
    Returns:
        Tuple of (response_data, status_code, saved_lead_models)
    """
    logger.info("Processing payload of any format", extra={
        "payload_keys": list(payload.keys()),
        "payload_size": len(str(payload))
    })
    
    try:
        # Parse the incoming payload
        parsed_data = parse_incoming_payload(payload)
        
        # Handle single lead vs multiple leads
        if isinstance(parsed_data, list):
            # Multiple leads (envelope format)
            logger.info(f"Processing {len(parsed_data)} leads from envelope")
            
            results = []
            saved_leads = []
            
            for i, bot_data in enumerate(parsed_data):
                logger.info(f"Processing lead {i+1}/{len(parsed_data)}")
                response_data, status_code, saved_lead = post_lead_to_clio_grow_typed(bot_data, db)
                results.append((response_data, status_code))
                
                if saved_lead:
                    saved_leads.append(saved_lead)
            
            # Return summary of all results
            successful = sum(1 for _, status in results if status == 201)
            summary = {
                "total_leads": len(parsed_data),
                "successful": successful,
                "failed": len(parsed_data) - successful,
                "results": results
            }
            
            overall_status = 201 if successful == len(parsed_data) else 207  # 207 = Multi-Status
            
            logger.info("Envelope processing completed", extra={
                "total": len(parsed_data),
                "successful": successful,
                "failed": len(parsed_data) - successful
            })
            
            return summary, overall_status, saved_leads
            
        else:
            # Single lead (direct or mixed format)
            logger.info("Processing single lead")
            response_data, status_code, saved_lead = post_lead_to_clio_grow_typed(parsed_data, db)
            
            return response_data, status_code, [saved_lead] if saved_lead else []
            
    except ValueError as e:
        logger.error("Payload parsing failed", extra={"error": str(e)})
        return {"error": f"Invalid payload format: {str(e)}"}, 422, []
    except Exception as e:
        logger.error("Unexpected error processing payload", extra={"error": str(e)})
        return {"error": f"Processing failed: {str(e)}"}, 500, []


def create_clio_lead(bot_data: dict) -> Tuple[dict, int]:
    """
    Main function to create a Clio lead - handles both direct and envelope formats.
    Enhanced with auto-detection, validation, field mapping, and comprehensive error handling.
    
    Args:
        bot_data: Dictionary containing lead data (any supported format)
        
    Returns:
        Tuple of (response_data, status_code)
    """
    logger.info("Starting lead creation process", extra={
        "input_fields": list(bot_data.keys()),
        "data_size": len(str(bot_data))
    })
    
    try:
        # Auto-detect format and parse the data
        validated_data = auto_parse_lead_data(bot_data)
        logger.info("Data parsing and validation successful", extra={
            "validated_name": f"{validated_data.first_name} {validated_data.last_name}",
            "source": validated_data.source,
            "format": "auto-detected"
        })
        
        # Use the typed function to send to Clio
        response_data, status_code, _ = post_lead_to_clio_grow_typed(validated_data)
        
        # Log final result
        if status_code == 201:
            logger.info("Lead creation completed successfully", extra={
                "status_code": status_code,
                "clio_lead_id": response_data.get("id") if isinstance(response_data, dict) else None
            })
        else:
            logger.warning("Lead creation completed with issues", extra={
                "status_code": status_code,
                "response_type": type(response_data).__name__
            })
        
        return response_data, status_code
        
    except ValidationError as e:
        logger.error("Validation failed", extra={"validation_errors": str(e)})
        return {"error": f"Validation failed: {str(e)}"}, 422
    except ValueError as e:
        logger.error("Data parsing failed", extra={"parsing_error": str(e)})
        return {"error": f"Data parsing failed: {str(e)}"}, 400
    except Exception as e:
        logger.error("Unexpected error during lead creation", extra={"error": str(e)})
        return {"error": f"Unexpected error: {str(e)}"}, 500


def create_clio_lead_legacy(bot_data: dict) -> Tuple[dict, int]:
    """
    Legacy function for backward compatibility with old validation approach.
    
    Args:
        bot_data: Dictionary containing lead data in the old format
        
    Returns:
        Tuple of (response_data, status_code)
    """
    logger.info("Using legacy lead creation process", extra={
        "input_fields": list(bot_data.keys())
    })
    
    try:
        # Validate input data with enhanced validation and fallbacks
        validated_data = validate_bot_data_typed(bot_data)
        logger.info("Legacy data validation successful", extra={
            "validated_name": f"{validated_data.first_name} {validated_data.last_name}",
            "source": validated_data.source
        })
        
        # Use the typed function to send to Clio
        response_data, status_code, _ = post_lead_to_clio_grow_typed(validated_data)
        
        # Log final result
        if status_code == 201:
            logger.info("Legacy lead creation completed successfully", extra={
                "status_code": status_code,
                "clio_lead_id": response_data.get("id") if isinstance(response_data, dict) else None
            })
        else:
            logger.warning("Legacy lead creation completed with issues", extra={
                "status_code": status_code,
                "response_type": type(response_data).__name__
            })
        
        return response_data, status_code
        
    except ValidationError as e:
        logger.error("Legacy validation failed", extra={"validation_errors": str(e)})
        return {"error": f"Validation failed: {str(e)}"}, 422
    except Exception as e:
        logger.error("Legacy error during lead creation", extra={"error": str(e)})
        return {"error": f"Unexpected error: {str(e)}"}, 500


# Legacy function for backward compatibility
def validate_bot_data(data: dict) -> list[str]:
    """Check for any missing required fields in bot_data (legacy function)."""
    try:
        BotDataInput(**data)
        return []
    except ValidationError as e:
        return [str(error) for error in e.errors()]


def encode_envelope_data(envelope_data: dict) -> str:
    """
    Encode envelope data as base64 string for transmission.
    
    Args:
        envelope_data: Dictionary containing envelope data to encode
        
    Returns:
        Base64 encoded string of the JSON serialized envelope data
    """
    logger.info("Encoding envelope data", extra={
        "data_keys": list(envelope_data.keys()),
        "data_size": len(str(envelope_data))
    })
    
    try:
        # Serialize to JSON string
        json_str = json.dumps(envelope_data)
        
        # Encode JSON string to bytes (utf-8), then Base64 encode
        b64_bytes = base64.b64encode(json_str.encode('utf-8'))
        b64_str = b64_bytes.decode('utf-8')
        
        logger.info("Envelope data encoded successfully", extra={
            "original_size": len(json_str),
            "encoded_size": len(b64_str)
        })
        
        return b64_str
        
    except Exception as e:
        logger.error("Failed to encode envelope data", extra={"error": str(e)})
        raise ValueError(f"Encoding failed: {str(e)}")


def decode_envelope_data(encoded_data: str) -> dict:
    """
    Decode base64 encoded envelope data back to dictionary.
    
    Args:
        encoded_data: Base64 encoded string containing envelope data
        
    Returns:
        Decoded dictionary with envelope data
    """
    logger.info("Decoding envelope data", extra={
        "encoded_size": len(encoded_data)
    })
    
    try:
        # Decode Base64 to bytes, then decode bytes to string
        json_bytes = base64.b64decode(encoded_data.encode('utf-8'))
        json_str = json_bytes.decode('utf-8')
        
        # Parse JSON string back to dictionary
        envelope_data = json.loads(json_str)
        
        logger.info("Envelope data decoded successfully", extra={
            "decoded_keys": list(envelope_data.keys()),
            "decoded_size": len(str(envelope_data))
        })
        
        return envelope_data
        
    except Exception as e:
        logger.error("Failed to decode envelope data", extra={"error": str(e)})
        raise ValueError(f"Decoding failed: {str(e)}")


def send_encoded_intake(envelope_data: dict, call_id: Optional[int] = None, timestamp: Optional[int] = None) -> Tuple[dict, int]:
    """
    Send intake data with base64 encoded envelope payload.
    
    Args:
        envelope_data: Dictionary containing the envelope data to encode and send
        call_id: Optional call ID for tracking
        timestamp: Optional timestamp (defaults to current time if not provided)
        
    Returns:
        Tuple of (response_data, status_code)
    """
    import time
    
    logger.info("Starting encoded intake submission", extra={
        "envelope_keys": list(envelope_data.keys()),
        "call_id": call_id,
        "has_timestamp": timestamp is not None
    })
    
    try:
        # Encode the envelope data
        encoded_envelope = encode_envelope_data(envelope_data)
        
        # Create the transmission payload with encoded data
        transmission_payload = {
            "timestamp": timestamp or int(time.time()),
            "encoded_envelope": encoded_envelope
        }
        
        # Add call_id if provided
        if call_id is not None:
            transmission_payload["call_id"] = call_id
        
        logger.info("Transmission payload created", extra={
            "payload_keys": list(transmission_payload.keys()),
            "encoded_envelope_size": len(encoded_envelope)
        })
        
        # For actual transmission, decode the envelope and process normally
        # This demonstrates the round-trip: encode -> transmit -> decode -> process
        
        # Decode the envelope back for processing
        decoded_envelope = decode_envelope_data(encoded_envelope)
        
        logger.info("Processing decoded envelope through standard pipeline")
        
        # Process the decoded envelope using existing envelope processing
        response_data, status_code = process_envelope_payload(decoded_envelope)
        
        # Add transmission metadata to response
        if isinstance(response_data, dict):
            response_data["transmission_metadata"] = {
                "call_id": call_id,
                "timestamp": transmission_payload["timestamp"],
                "encoded": True,
                "encoding_method": "base64"
            }
        
        logger.info("Encoded intake submission completed", extra={
            "status_code": status_code,
            "call_id": call_id,
            "transmission_successful": status_code == 201
        })
        
        return response_data, status_code
        
    except ValueError as e:
        logger.error("Encoding/decoding error in encoded intake", extra={"error": str(e)})
        return {"error": f"Encoding error: {str(e)}"}, 400
    except Exception as e:
        logger.error("Unexpected error in encoded intake", extra={"error": str(e)})
        return {"error": f"Processing error: {str(e)}"}, 500


def create_encoded_transmission_payload(envelope_data: dict, call_id: Optional[int] = None, additional_metadata: Optional[dict] = None) -> dict:
    """
    Create a transmission payload with encoded envelope data, following your example pattern.
    
    Args:
        envelope_data: Dictionary containing the envelope data to encode
        call_id: Optional call ID for tracking
        additional_metadata: Optional additional metadata to include
        
    Returns:
        Dictionary with encoded payload ready for transmission
    """
    import time
    
    logger.info("Creating encoded transmission payload", extra={
        "envelope_keys": list(envelope_data.keys()),
        "call_id": call_id,
        "has_metadata": additional_metadata is not None
    })
    
    try:
        # Encode the envelope data
        encoded_envelope = encode_envelope_data(envelope_data)
        
        # Create the transmission payload (following your example structure)
        payload = {
            "timestamp": int(time.time()),
            "message": encoded_envelope  # Using 'message' field as in your example
        }
        
        # Add call_id if provided (following your example with callId)
        if call_id is not None:
            payload["callId"] = call_id
        
        # Add any additional metadata
        if additional_metadata:
            payload.update(additional_metadata)
        
        logger.info("Encoded transmission payload created", extra={
            "payload_keys": list(payload.keys()),
            "encoded_message_size": len(encoded_envelope),
            "call_id": call_id
        })
        
        return payload
        
    except Exception as e:
        logger.error("Failed to create encoded transmission payload", extra={"error": str(e)})
        raise ValueError(f"Payload creation failed: {str(e)}")


def post_lead_to_clio_grow(bot_data: dict) -> Tuple[dict, int]:
    """Legacy function - use post_lead_to_clio_grow_typed for new code."""
    return create_clio_lead(bot_data)
# === EXAMPLE USAGE ===
if __name__ == "__main__":
    # Example bot data matching your API specification
    # This demonstrates both complete data and missing field scenarios
    
    # Complete data example
    complete_bot_data = {
        "first_name": "John",
        "last_name": "Doe",
        "message": "I need a lawyer for a personal injury case",
        "email": "johndoe@email.com",
        "phone_number": "8987648934",
        "referring_url": "http://lawfirmwebsite.com/intake-form",
        "source": "Law Firm Landing Page"
    }
    
    # Incomplete data example (will use fallbacks)
    incomplete_bot_data = {
        "first_name": "Jane",
        "message": "Need legal help",
        "email": "jane@example.com"
        # Missing: last_name, referring_url, source - fallbacks will be applied
    }
    
    # Test with complete data
    logger.info("=== Testing with complete data ===")
    data, status = create_clio_lead(complete_bot_data)
    
    if status == 201:
        logger.info("✅ Lead created successfully", extra={"clio_response": data})
    elif status == 401:
        logger.error("❌ Invalid lead inbox token")
    elif status == 422:
        # Handle validation errors with proper structure
        if isinstance(data, dict) and "inbox_lead" in data and "errors" in data["inbox_lead"]:
            logger.error("❌ Validation error from Clio", extra={"errors": data["inbox_lead"]["errors"]})
        else:
            logger.error("❌ Validation error", extra={"error_data": data})
    else:
        logger.error("❌ Unexpected error", extra={"status": status, "data": data})
    
    # Test with incomplete data (demonstrating fallbacks)
    logger.info("=== Testing with incomplete data (fallbacks) ===")
    data2, status2 = create_clio_lead(incomplete_bot_data)
    
    if status2 == 201:
        logger.info("✅ Lead created with fallbacks", extra={"clio_response": data2})
    elif status2 == 401:
        logger.error("❌ Invalid lead inbox token")
    elif status2 == 422:
        if isinstance(data2, dict) and "inbox_lead" in data2 and "errors" in data2["inbox_lead"]:
            logger.error("❌ Validation error with fallbacks", extra={"errors": data2["inbox_lead"]["errors"]})
        else:
            logger.error("❌ Validation error", extra={"error_data": data2})
    else:
        logger.error("❌ Unexpected error with fallbacks", extra={"status": status2, "data": data2})
