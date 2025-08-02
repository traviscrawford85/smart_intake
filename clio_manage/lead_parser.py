"""
Parser utilities for handling different lead data formats.
Supports both direct payloads and Capture Now agent envelope structures.
"""

from typing import Any, Dict, Optional

from loguru import logger

from .schemas import BotDataInput, CaptureNowEnvelope


class LeadDataParser:
    """Parser for various lead data formats with auto-detection."""

    default_url = "https://capture-now-agent.com/"

    def _normalize_url(self, url: Optional[str]) -> str:
        """Normalize and validate URLs, providing defaults for common cases."""
        if not url:
            return self.default_url
        if url.lower() == "vonage":
            return "https://vonage.com/"
        if url.startswith(("http://", "https://")):
            return url
        if "." in url:
            return f"https://{url}"
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
        if "inbox_lead" in data and isinstance(data["inbox_lead"], dict):
            logger.info("Detected direct payload format")
            return "direct"
        if "inbox_leads" in data and isinstance(data["inbox_leads"], list):
            logger.info("Detected Capture Now envelope format")
            return "envelope"
        envelope_indicators = [
            "call_duration",
            "call_recording_url",
            "chat_conversation_id",
            "dispute_status",
            "google_lead_id",
            "inboxable",
            "lead_type",
        ]
        if any(field in data for field in envelope_indicators):
            logger.info("Detected flattened Capture Now envelope format")
            return "envelope"
        basic_fields = ["first_name", "last_name", "email", "message"]
        if any(field in data for field in basic_fields):
            logger.info("Detected simple lead format (treating as envelope)")
            return "envelope"
        logger.warning("Unknown data format detected")
        return "unknown"

    def parse_direct_payload(self, data: Dict[str, Any]) -> BotDataInput:
        """Parse direct payload from web forms."""
        try:
            processed_data = data.copy()
            if "inbox_lead" in processed_data:
                inbox_lead = processed_data["inbox_lead"].copy()
                if "referring_url" in inbox_lead:
                    inbox_lead["referring_url"] = self._normalize_url(
                        inbox_lead["referring_url"]
                    )
                processed_data["inbox_lead"] = inbox_lead
                # Map directly to BotDataInput
                mapped_data = {
                    "first_name": inbox_lead.get("from_first")
                    or inbox_lead.get("first_name")
                    or "Unknown",
                    "last_name": inbox_lead.get("from_last")
                    or inbox_lead.get("last_name")
                    or "Contact",
                    "message": inbox_lead.get("from_message")
                    or inbox_lead.get("message")
                    or "No message provided",
                    "email": inbox_lead.get("from_email") or inbox_lead.get("email"),
                    "phone_number": inbox_lead.get("from_phone")
                    or inbox_lead.get("phone_number"),
                    "referring_url": inbox_lead.get("referring_url")
                    or self.default_url,
                    "source": inbox_lead.get("from_source")
                    or inbox_lead.get("source")
                    or "Web Form",
                }
            else:
                mapped_data = {
                    "first_name": processed_data.get("first_name") or "Unknown",
                    "last_name": processed_data.get("last_name") or "Contact",
                    "message": processed_data.get("message") or "No message provided",
                    "email": processed_data.get("email"),
                    "phone_number": processed_data.get("phone_number"),
                    "referring_url": processed_data.get("referring_url")
                    or self.default_url,
                    "source": processed_data.get("source") or "Web Form",
                }
            logger.info("Successfully parsed direct payload")
            return BotDataInput(**mapped_data)
        except Exception as e:
            logger.error(f"Failed to parse direct payload: {str(e)}")
            raise ValueError(f"Invalid direct payload format: {str(e)}")

    def parse_envelope_payload(self, data: Dict[str, Any]) -> BotDataInput:
        """Parse Capture Now agent envelope structure."""
        try:
            envelope = CaptureNowEnvelope(**data)
            mapped_data = {
                "first_name": "Unknown",
                "last_name": "Contact",
                "message": "Voice agent intake submission",
                "email": None,
                "phone_number": None,
                "referring_url": self.default_url,
                "source": "Capture Now Agent",
            }
            if envelope.inbox_leads and len(envelope.inbox_leads) > 0:
                lead = envelope.inbox_leads[0]
                if lead.first_name:
                    mapped_data["first_name"] = lead.first_name
                if lead.last_name:
                    mapped_data["last_name"] = lead.last_name
                if lead.email:
                    mapped_data["email"] = lead.email
                if lead.phone_number:
                    mapped_data["phone_number"] = lead.phone_number
                if lead.message and lead.message is not False:
                    mapped_data["message"] = str(lead.message)
                if lead.referring_url:
                    mapped_data["referring_url"] = lead.referring_url
                if lead.source:
                    mapped_data["source"] = lead.source
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
            if mapped_data["referring_url"] == "Vonage":
                mapped_data["referring_url"] = "https://vonage-integration.com"
                mapped_data["source"] = "Vonage Voice Agent"
            if mapped_data["message"] in ["", "Voice agent intake submission"]:
                if envelope.call_recording_url:
                    mapped_data["message"] = (
                        f"Voice call recorded. Duration: {envelope.call_duration or 0} seconds. Recording available."
                    )
                else:
                    mapped_data["message"] = "Voice agent conversation completed"
            logger.info(
                "Successfully parsed envelope payload",
                extra={
                    "lead_name": f"{mapped_data['first_name']} {mapped_data['last_name']}",
                    "source": mapped_data["source"],
                    "has_recording": bool(envelope.call_recording_url),
                    "call_duration": envelope.call_duration,
                },
            )
            return BotDataInput(**mapped_data)
        except Exception as e:
            logger.error(f"Failed to parse envelope payload: {str(e)}")
            raise ValueError(f"Invalid envelope format: {str(e)}")

    @staticmethod
    def parse_lead_data(data: Dict[str, Any]) -> BotDataInput:
        """
        Main parser function that auto-detects format and parses accordingly.
        """
        logger.info(
            "Starting lead data parsing",
            extra={"data_keys": list(data.keys()), "data_size": len(str(data))},
        )
        format_type = LeadDataParser.detect_format(data)
        parser = LeadDataParser()
        if format_type == "direct":
            return parser.parse_direct_payload(data)
        elif format_type == "envelope":
            return parser.parse_envelope_payload(data)
        else:
            logger.error("Unsupported data format", extra={"data": data})
            raise ValueError(
                f"Unsupported data format. Received keys: {list(data.keys())}"
            )


def parse_lead_data(data: Dict[str, Any], format_type: str = "auto") -> BotDataInput:
    """Parse lead data with specified or auto-detected format."""
    if format_type == "auto":
        return LeadDataParser.parse_lead_data(data)
    parser = LeadDataParser()
    if format_type == "direct":
        return parser.parse_direct_payload(data)
    else:
        return parser.parse_envelope_payload(data)
