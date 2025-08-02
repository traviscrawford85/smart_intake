"""
Envelope and payload parsing module for handling different Clio input formats.

This module provides unified parsing for:
1. Direct payloads from web forms (new Clio API format)
2. Envelope payloads from Capture Now agent (legacy Clio API format)
3. Mixed/malformed payloads that need normalization
"""

import os
from typing import Any, Dict, List, Optional, Union

from app.schemas import (
    BotDataInput,
    CaptureNowEnvelope,
    CaptureNowInboxLead,
    ClioInboxLead,
    DirectPayload,
    UnifiedLeadInput,
)

# Load environment variables
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
load_dotenv(".env")
load_dotenv("../.env")
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class PayloadParser:
    """Unified parser for handling different payload formats."""

    @staticmethod
    def detect_payload_type(payload: Dict[str, Any]) -> str:
        """
        Detect the type of payload based on structure.

        Returns:
            str: 'direct', 'envelope', 'mixed', or 'unknown'
        """
        logger.info(
            "Detecting payload type", extra={"payload_keys": list(payload.keys())}
        )

        # Direct payload: has 'inbox_lead' and 'inbox_lead_token' keys
        if "inbox_lead" in payload and "inbox_lead_token" in payload:
            logger.info("Detected direct payload format")
            return "direct"

        # Envelope payload: has 'inbox_leads' array
        if "inbox_leads" in payload:
            logger.info("Detected envelope payload format")
            return "envelope"

        # Mixed/flattened payload: has lead fields at root level
        lead_fields = ["first_name", "last_name", "email", "message"]
        if any(field in payload for field in lead_fields):
            logger.info("Detected mixed/flattened payload format")
            return "mixed"

        logger.warning("Unknown payload format detected")
        return "unknown"

    @staticmethod
    def parse_direct_payload(payload: Dict[str, Any]) -> BotDataInput:
        """
        Parse direct payload from web forms.

        Expected format:
        {
          "inbox_lead": {
            "from_first": "John",
            "from_last": "Smith",
            "from_message": "Message",
            "from_email": "john@example.com",
            "from_phone": "1234567890",
            "referring_url": "https://example.com",
            "from_source": "Website Contact Form"
          },
          "inbox_lead_token": "token"
        }
        """
        logger.info("Parsing direct payload")

        try:
            direct = DirectPayload(**payload)
            inbox_lead = direct.inbox_lead

            # Map from Clio format to internal format
            mapped_data = {
                "first_name": inbox_lead.get("from_first", ""),
                "last_name": inbox_lead.get("from_last", ""),
                "message": inbox_lead.get("from_message", ""),
                "email": inbox_lead.get("from_email"),
                "phone_number": inbox_lead.get("from_phone"),
                "referring_url": inbox_lead.get("referring_url", "https://unknown.com"),
                "source": inbox_lead.get("from_source", "Unknown Source"),
            }

            logger.info(
                "Direct payload parsed successfully",
                extra={
                    "lead_name": f"{mapped_data['first_name']} {mapped_data['last_name']}",
                    "source": mapped_data["source"],
                },
            )

            return BotDataInput(**mapped_data)

        except Exception as e:
            logger.error("Failed to parse direct payload", extra={"error": str(e)})
            raise ValueError(f"Invalid direct payload: {e}")

    @staticmethod
    def parse_envelope_payload(payload: Dict[str, Any]) -> List[BotDataInput]:
        """
        Parse envelope payload from Capture Now agent.

        Expected format:
        {
          "inbox_leads": [
            {
              "id": 27173864,
              "first_name": "Minnie",
              "last_name": "mouse",
              "email": "mini.mouse@disney.plus.com",
              "message": false,  // or actual message
              "call_duration": 0,
              "call_recording_url": null,
              ...
            }
          ],
          // other envelope fields...
        }
        """
        logger.info("Parsing envelope payload")

        try:
            envelope = CaptureNowEnvelope(**payload)
            parsed_leads = []

            if not envelope.inbox_leads:
                logger.warning("No inbox_leads found in envelope")
                return []

            for i, lead in enumerate(envelope.inbox_leads):
                try:
                    # Map envelope lead to internal format
                    mapped_data = PayloadParser._map_envelope_lead_to_bot_data(
                        lead, envelope
                    )
                    bot_data = BotDataInput(**mapped_data)
                    parsed_leads.append(bot_data)

                    logger.info(
                        f"Envelope lead {i+1} parsed successfully",
                        extra={
                            "lead_name": f"{mapped_data['first_name']} {mapped_data['last_name']}",
                            "source": mapped_data["source"],
                        },
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to parse envelope lead {i+1}", extra={"error": str(e)}
                    )
                    continue

            logger.info(f"Envelope payload parsed: {len(parsed_leads)} leads")
            return parsed_leads

        except Exception as e:
            logger.error("Failed to parse envelope payload", extra={"error": str(e)})
            raise ValueError(f"Invalid envelope payload: {e}")

    @staticmethod
    def parse_mixed_payload(payload: Dict[str, Any]) -> BotDataInput:
        """
        Parse mixed/flattened payload where lead fields are at root level.
        """
        logger.info("Parsing mixed payload")

        try:
            unified = UnifiedLeadInput(**payload)

            # Extract lead data from various possible locations
            mapped_data = {
                "first_name": unified.first_name or "Unknown",
                "last_name": unified.last_name or "Contact",
                "message": PayloadParser._extract_message(unified.message)
                or "Voice agent intake submission",
                "email": unified.email,
                "phone_number": unified.phone_number,
                "referring_url": unified.referring_url or "https://intake-system.local",
                "source": unified.source or "Mixed Payload Source",
            }

            logger.info(
                "Mixed payload parsed successfully",
                extra={
                    "lead_name": f"{mapped_data['first_name']} {mapped_data['last_name']}",
                    "source": mapped_data["source"],
                },
            )

            return BotDataInput(**mapped_data)

        except Exception as e:
            logger.error("Failed to parse mixed payload", extra={"error": str(e)})
            raise ValueError(f"Invalid mixed payload: {e}")

    @staticmethod
    def _map_envelope_lead_to_bot_data(
        lead: CaptureNowInboxLead, envelope: CaptureNowEnvelope
    ) -> Dict[str, Any]:
        """
        Map envelope lead data to internal bot data format.
        Uses fallback values from envelope root level if lead fields are missing.
        """

        # Extract message (handle both string and boolean)
        message = PayloadParser._extract_message(lead.message)
        if not message:
            message = PayloadParser._extract_message(envelope.message)
        if not message:
            message = "Voice agent intake submission"

        # Build referring URL from available data
        referring_url = lead.referring_url or envelope.referring_url
        if not referring_url:
            if lead.call_recording_url:
                referring_url = "https://capture-now-agent.com/call"
            else:
                referring_url = "https://intake-system.local"

        # Determine source
        source = lead.source or envelope.source or "Capture Now Agent"

        mapped_data = {
            "first_name": lead.first_name or envelope.first_name or "Unknown",
            "last_name": lead.last_name or envelope.last_name or "Contact",
            "message": message,
            "email": lead.email or envelope.email,
            "phone_number": lead.phone_number or envelope.phone_number,
            "referring_url": referring_url,
            "source": source,
        }

        return mapped_data

    @staticmethod
    def _extract_message(message: Union[str, bool, None]) -> Optional[str]:
        """
        Extract message string from various formats.
        Capture Now agent sometimes sends message: false instead of actual message.
        """
        if isinstance(message, str) and message.strip():
            return message.strip()
        elif isinstance(message, bool) and not message:
            # message: false means no message was captured
            return None
        elif message is None:
            return None
        else:
            return str(message)


def parse_incoming_payload(
    payload: Dict[str, Any],
) -> Union[BotDataInput, List[BotDataInput]]:
    """
    Main function to parse any incoming payload format.

    Args:
        payload: Raw payload from web form, Capture Now agent, or other source

    Returns:
        BotDataInput for single leads, List[BotDataInput] for envelope with multiple leads

    Raises:
        ValueError: If payload cannot be parsed
    """
    logger.info(
        "Starting payload parsing",
        extra={
            "payload_size": len(str(payload)),
            "top_level_keys": list(payload.keys()),
        },
    )

    parser = PayloadParser()
    payload_type = parser.detect_payload_type(payload)

    try:
        if payload_type == "direct":
            return parser.parse_direct_payload(payload)

        elif payload_type == "envelope":
            return parser.parse_envelope_payload(payload)

        elif payload_type == "mixed":
            return parser.parse_mixed_payload(payload)

        else:
            logger.error(
                "Cannot parse unknown payload format", extra={"payload": payload}
            )
            raise ValueError(f"Unknown payload format. Keys: {list(payload.keys())}")

    except Exception as e:
        logger.error(
            "Payload parsing failed",
            extra={"error": str(e), "payload_type": payload_type},
        )
        raise


def normalize_to_clio_format(bot_data: BotDataInput) -> ClioInboxLead:
    """
    Convert internal BotDataInput to Clio API format.

    Args:
        bot_data: Validated internal lead data

    Returns:
        ClioInboxLead ready for API submission
    """
    logger.info(
        "Normalizing to Clio format",
        extra={
            "lead_name": f"{bot_data.first_name} {bot_data.last_name}",
            "source": bot_data.source,
        },
    )

    return ClioInboxLead(
        from_first=bot_data.first_name,
        from_last=bot_data.last_name,
        from_message=bot_data.message,
        from_email=bot_data.email or "",
        from_phone=bot_data.phone_number or "",
        referring_url=str(bot_data.referring_url),
        from_source=bot_data.source,
    )


# Example usage and testing
if __name__ == "__main__":
    logger.info("🧪 Testing payload parsing")

    # Test direct payload
    direct_payload = {
        "inbox_lead": {
            "from_first": "John",
            "from_last": "Smith",
            "from_message": "Full Voice agent transcript here.",
            "from_email": "john@example.com",
            "from_phone": "0987654321",
            "referring_url": "https://vonage.com/voice-agent",
            "from_source": "Capture Now Agent",
        },
        "inbox_lead_token": "YOUR_TOKEN",
    }

    # Test envelope payload
    envelope_payload = {
        "inbox_leads": [
            {
                "id": 27173864,
                "errors": {},
                "created_at": "July 28, 2025 at 3:36 pm (EDT)",
                "first_name": "Minnie",
                "last_name": "mouse",
                "email": "mini.mouse@disney.plus.com",
                "phone_number": None,
                "message": False,  # Common in Capture Now
                "call_duration": 0,
                "call_recording_url": None,
                "source": None,
            }
        ],
        "call_duration": 0,
        "created_at": "July 28, 2025 at 3:36 pm (EDT)",
    }

    try:
        # Test direct parsing
        logger.info("Testing direct payload parsing")
        direct_result = parse_incoming_payload(direct_payload)
        print(f"Direct result: {direct_result}")

        # Test envelope parsing
        logger.info("Testing envelope payload parsing")
        envelope_result = parse_incoming_payload(envelope_payload)
        print(f"Envelope result: {envelope_result}")

        logger.info("✅ All payload parsing tests passed")

    except Exception as e:
        logger.error(f"❌ Payload parsing test failed: {e}")
