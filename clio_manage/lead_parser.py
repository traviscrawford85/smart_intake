"""
Parser utilities for handling different lead data formats.
Supports both direct payloads and Capture Now agent envelope structures.
"""
from typing import Dict, Any, Optional, Union, List
from loguru import logger
from pydantic import ValidationError

from app.schemas import (
    UnifiedLeadInput, 
    CaptureNowEnvelope, 
    DirectPayload,
    BotDataInput,
    ClioInboxLead
)


class LeadDataParser:
    """Parser for various lead data formats with auto-detection."""
    
    default_url = "https://capture-now-agent.com/"
    
    def _normalize_url(self, url: Optional[str]) -> str:
        """Normalize and validate URLs, providing defaults for common cases."""
        if not url:
            return self.default_url
        
        # Handle special cases like "Vonage"
        if url.lower() == "vonage":
            return "https://vonage.com/"
        
        # If it looks like a URL, use it
        if url.startswith(("http://", "https://")):
            return url
        
        # If it has domain-like structure, add https
        if "." in url and not url.startswith(("http://", "https://")):
            return f"https://{url}"
        
        # Default fallback
        return self.default_url
    
    @staticmethod
    def detect_format(data: Dict[str, Any]) -> str:
        """
        Detect the format of incoming lead data.
        
        Returns:
            'direct' for direct payloads from web forms
            'envelope' for Capture Now agent envelope structure
            'unknown' for unrecognized formats
        """
        # Check for direct payload structure
        if "inbox_lead" in data and isinstance(data["inbox_lead"], dict):
            logger.info("Detected direct payload format")
            return "direct"
        
        # Check for envelope structure
        if "inbox_leads" in data and isinstance(data["inbox_leads"], list):
            logger.info("Detected Capture Now envelope format")
            return "envelope"
        
        # Check if it's a flattened envelope (top-level fields)
        envelope_indicators = [
            "call_duration", "call_recording_url", "chat_conversation_id",
            "dispute_status", "google_lead_id", "inboxable", "lead_type"
        ]
        
        if any(field in data for field in envelope_indicators):
            logger.info("Detected flattened Capture Now envelope format")
            return "envelope"
        
        # Check if it has basic lead fields at root level
        basic_fields = ["first_name", "last_name", "email", "message"]
        if any(field in data for field in basic_fields):
            logger.info("Detected simple lead format (treating as envelope)")
            return "envelope"
        
        logger.warning("Unknown data format detected")
        return "unknown"
    
    def parse_direct_payload(self, data: Dict[str, Any]) -> BotDataInput:
        """Parse direct payload from web forms."""
        try:
            # Pre-process to fix common issues
            processed_data = data.copy()
            
            if "inbox_lead" in processed_data:
                inbox_lead = processed_data["inbox_lead"].copy()
                
                # Normalize referring_url if present
                if "referring_url" in inbox_lead:
                    inbox_lead["referring_url"] = self._normalize_url(inbox_lead["referring_url"])
                
                processed_data["inbox_lead"] = inbox_lead
            
            # First validate the structure with pre-processing
            lead_input = ClioInboxLead(**processed_data)
            
            # Map to internal format
            inbox_lead = lead_input.inbox_lead
            mapped_data = {
                "first_name": inbox_lead.from_first or "Unknown",
                "last_name": inbox_lead.from_last or "Contact", 
                "message": inbox_lead.from_message or "No message provided",
                "email": inbox_lead.from_email,
                "phone_number": inbox_lead.from_phone,
                "referring_url": inbox_lead.referring_url or self.default_url,
                "source": inbox_lead.from_source or "Web Form"
            }
            
            logger.info("Successfully parsed direct payload")
            return BotDataInput(**mapped_data)
            
        except Exception as e:
            logger.error(f"Failed to parse direct payload: {str(e)}")
            raise ValueError(f"Invalid direct payload format: {str(e)}")
    
    def parse_envelope_payload(self, data: Dict[str, Any]) -> BotDataInput:
        """Parse Capture Now agent envelope structure."""
        try:
            # Handle the envelope structure
            envelope = UnifiedLeadInput(**data)
            
            # Initialize mapped data with defaults
            mapped_data = {
                "first_name": "Unknown",
                "last_name": "Contact",
                "message": "Voice agent intake submission",
                "email": None,
                "phone_number": None,
                "referring_url": "https://capture-now-agent.com",
                "source": "Capture Now Agent"
            }
            
            # Try to extract data from inbox_leads array first
            if envelope.inbox_leads and len(envelope.inbox_leads) > 0:
                lead = envelope.inbox_leads[0]  # Take the first lead
                logger.info("Extracting data from inbox_leads array")
                
                if lead.get("first_name"):
                    mapped_data["first_name"] = lead["first_name"]
                if lead.get("last_name"):
                    mapped_data["last_name"] = lead["last_name"]
                if lead.get("email"):
                    mapped_data["email"] = lead["email"]
                if lead.get("phone_number"):
                    mapped_data["phone_number"] = lead["phone_number"]
                if lead.get("message") and lead["message"] is not False:
                    mapped_data["message"] = str(lead["message"])
                if lead.get("referring_url"):
                    mapped_data["referring_url"] = lead["referring_url"]
                if lead.get("source"):
                    mapped_data["source"] = lead["source"]
            
            # Fall back to root-level fields if inbox_leads is empty or missing
            if envelope.first_name:
                mapped_data["first_name"] = envelope.first_name
            if envelope.last_name:
                mapped_data["last_name"] = envelope.last_name
            if envelope.email:
                mapped_data["email"] = envelope.email
            if envelope.phone_number:
                mapped_data["phone_number"] = envelope.phone_number
            if envelope.message and envelope.message is not False:
                mapped_data["message"] = str(envelope.message)
            if envelope.referring_url:
                mapped_data["referring_url"] = envelope.referring_url
            if envelope.source:
                mapped_data["source"] = envelope.source
            
            # Handle special cases for Capture Now data
            if mapped_data["referring_url"] == "Vonage":
                mapped_data["referring_url"] = "https://vonage-integration.com"
                mapped_data["source"] = "Vonage Voice Agent"
            
            # Ensure message is a proper transcript if available
            if mapped_data["message"] in ["", "Voice agent intake submission"]:
                if envelope.call_recording_url:
                    mapped_data["message"] = f"Voice call recorded. Duration: {envelope.call_duration or 0} seconds. Recording available."
                else:
                    mapped_data["message"] = "Voice agent conversation completed"
            
            logger.info("Successfully parsed envelope payload", extra={
                "lead_name": f"{mapped_data['first_name']} {mapped_data['last_name']}",
                "source": mapped_data['source'],
                "has_recording": bool(envelope.call_recording_url),
                "call_duration": envelope.call_duration
            })
            
            return BotDataInput(**mapped_data)
            
        except Exception as e:
            logger.error(f"Failed to parse envelope payload: {str(e)}")
            raise ValueError(f"Invalid envelope format: {str(e)}")
    
    @staticmethod
    def parse_lead_data(data: Dict[str, Any]) -> BotDataInput:
        """
        Main parser function that auto-detects format and parses accordingly.
        
        Args:
            data: Raw lead data in any supported format
            
        Returns:
            BotDataInput: Standardized lead data
            
        Raises:
            ValueError: If the data format is invalid or unsupported
        """
        logger.info("Starting lead data parsing", extra={
            "data_keys": list(data.keys()),
            "data_size": len(str(data))
        })
        
        # Detect the format
        format_type = LeadDataParser.detect_format(data)
        
        # Parse based on detected format
        if format_type == "direct":
            return LeadDataParser.parse_direct_payload(data)
        elif format_type == "envelope":
            return LeadDataParser.parse_envelope_payload(data)
        else:
            logger.error("Unsupported data format", extra={"data": data})
            raise ValueError(f"Unsupported data format. Received keys: {list(data.keys())}")


# Convenience functions for backward compatibility
def parse_capture_now_envelope(data: Dict[str, Any]) -> BotDataInput:
    """Parse Capture Now agent envelope structure."""
    return LeadDataParser.parse_envelope_payload(data)


def parse_direct_payload(data: Dict[str, Any]) -> BotDataInput:
    """Parse direct payload from web forms.""" 
    return LeadDataParser.parse_direct_payload(data)


def auto_parse_lead_data(raw_data: Dict[str, Any]) -> BotDataInput:
    """Auto-detect format and parse lead data from various sources."""
    logger.info("Starting lead data parsing")
    
    # Detect format
    format_type = LeadDataParser.detect_format(raw_data)
    parser = LeadDataParser()
    
    if format_type == "direct":
        return parser.parse_direct_payload(raw_data)
    elif format_type == "envelope":
        return parser.parse_envelope_payload(raw_data)
    else:
        # Default to envelope parsing for unknown formats
        logger.warning("Unknown format detected, attempting envelope parsing")
        return parser.parse_envelope_payload(raw_data)


# For backward compatibility and external usage
def parse_lead_data(data: Dict[str, Any], format_type: str = "auto") -> BotDataInput:
    """Parse lead data with specified or auto-detected format."""
    if format_type == "auto":
        return auto_parse_lead_data(data)
    
    parser = LeadDataParser()
    if format_type == "direct":
        return parser.parse_direct_payload(data)
    else:
        return parser.parse_envelope_payload(data)
