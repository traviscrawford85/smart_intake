# Encoded Intake Documentation

## Overview

The `send_encoded_intake` functionality provides base64 encoding/decoding capabilities for envelope data, allowing secure transmission of intake information. This follows the exact pattern you specified for encoding JSON data as base64 strings.

## Key Functions

### 1. `encode_envelope_data(envelope_data: dict) -> str`

Encodes envelope data as a base64 string for transmission.

**Parameters:**
- `envelope_data`: Dictionary containing envelope data to encode

**Returns:**
- Base64 encoded string of the JSON serialized envelope data

**Example:**
```python
envelope_data = {
    "first_name": "John",
    "last_name": "Doe",
    "message": "Hello world",
    "email": "john.doe@example.com",
    "phone_number": "555-123-4567",
    "referring_url": "https://lawfirm.com",
    "source": "Voice Agent"
}

encoded = encode_envelope_data(envelope_data)
# Returns: "eyJmaXJzdF9uYW1lIjogIkpvaG4iLCAibGFzdF9uYW1lIjogIkRvZSIsIC..."
```

### 2. `decode_envelope_data(encoded_data: str) -> dict`

Decodes base64 encoded envelope data back to dictionary.

**Parameters:**
- `encoded_data`: Base64 encoded string containing envelope data

**Returns:**
- Decoded dictionary with envelope data

**Example:**
```python
encoded = "eyJmaXJzdF9uYW1lIjogIkpvaG4iLCAibGFzdF9uYW1lIjogIkRvZSIsIC..."
decoded = decode_envelope_data(encoded)
# Returns: {"first_name": "John", "last_name": "Doe", ...}
```

### 3. `send_encoded_intake(envelope_data: dict, call_id: Optional[int] = None, timestamp: Optional[int] = None) -> Tuple[dict, int]`

Sends intake data with base64 encoded envelope payload.

**Parameters:**
- `envelope_data`: Dictionary containing the envelope data to encode and send
- `call_id`: Optional call ID for tracking
- `timestamp`: Optional timestamp (defaults to current time if not provided)

**Returns:**
- Tuple of (response_data, status_code)

**Example:**
```python
envelope_data = {
    "first_name": "Jane",
    "last_name": "Smith",
    "message": "I need legal help",
    "email": "jane@example.com",
    "phone_number": "555-987-6543",
    "referring_url": "https://lawfirm.com/contact",
    "source": "Capture Now Bot"
}

response, status = send_encoded_intake(envelope_data, call_id=1234)

if status == 201:
    print("Success!")
    print(f"Clio Lead ID: {response['inbox_lead']['id']}")
    print(f"Call ID: {response['transmission_metadata']['call_id']}")
```

### 4. `create_encoded_transmission_payload(envelope_data: dict, call_id: Optional[int] = None, additional_metadata: Optional[dict] = None) -> dict`

Creates a transmission payload with encoded envelope data, following your exact example pattern.

**Parameters:**
- `envelope_data`: Dictionary containing the envelope data to encode
- `call_id`: Optional call ID for tracking
- `additional_metadata`: Optional additional metadata to include

**Returns:**
- Dictionary with encoded payload ready for transmission

**Example:**
```python
envelope_data = {
    "first_name": "Alice",
    "last_name": "Johnson",
    "message": "Car accident case",
    # ... other fields
}

payload = create_encoded_transmission_payload(
    envelope_data=envelope_data,
    call_id=1234,
    additional_metadata={"version": "1.0", "client": "intake_agent"}
)

# Returns:
# {
#   "timestamp": 1753812732,
#   "message": "eyJmaXJzdF9uYW1lIjogIkFsaWNlIiwgImxhc3RfbmFtZSI6ICJKB2huc29uIi...",
#   "callId": 1234,
#   "version": "1.0",
#   "client": "intake_agent"
# }
```

## Your Example Pattern Implementation

Following your exact example:

```python
import json
import base64

# The data you want to send
data = {
    "first_name": "John",
    "last_name": "Doe",
    "message": "Hello world",
    "email": "john.doe@example.com",
    "phone_number": "555-123-4567",
    "referring_url": "https://lawfirm.com",
    "source": "Voice Agent"
}

# Serialize to JSON string
json_str = json.dumps(data)

# Encode JSON string to bytes (utf-8), then Base64 encode
b64_bytes = base64.b64encode(json_str.encode('utf-8'))
b64_str = b64_bytes.decode('utf-8')

# Now you can send this in your REST payload
payload = {
    "timestamp": 1234567890,
    "callId": 1234,
    "message": b64_str
}

print(payload)
```

## Integration with Clio

The encoded intake system seamlessly integrates with your existing Clio pipeline:

1. **Encode** → Your envelope data is base64 encoded
2. **Transmit** → The encoded data can be sent via REST API
3. **Decode** → The system automatically decodes the data
4. **Process** → Uses existing envelope processing functions
5. **Submit** → Sends to Clio Grow Lead Inbox API

## Response Format

Successful responses include transmission metadata:

```json
{
  "inbox_lead": {
    "id": 27198494,
    "errors": {},
    "from_first": "John",
    "from_last": "Doe",
    "from_phone": "555-123-4567",
    "from_email": "john.doe@example.com",
    "from_message": "Hello world, I need legal assistance",
    "from_source": "Voice Agent"
  },
  "transmission_metadata": {
    "call_id": 1234,
    "timestamp": 1234567890,
    "encoded": true,
    "encoding_method": "base64"
  }
}
```

## Error Handling

The system includes comprehensive error handling:

- **Encoding errors**: Invalid data structure
- **Decoding errors**: Malformed base64 data
- **Transmission errors**: Network or API issues
- **Validation errors**: Missing required fields

All errors are logged using loguru with structured logging.

## Usage Examples

### Basic Usage
```python
from app.send_intake import send_encoded_intake

envelope_data = {
    "first_name": "Test",
    "last_name": "User",
    "message": "Test message",
    "email": "test@example.com",
    "phone_number": "555-000-0000",
    "referring_url": "https://example.com",
    "source": "Test Bot"
}

response, status = send_encoded_intake(envelope_data, call_id=5678)
```

### Manual Encoding
```python
from app.send_intake import encode_envelope_data, decode_envelope_data

# Encode
encoded = encode_envelope_data(envelope_data)

# Later... decode
decoded = decode_envelope_data(encoded)
```

### Creating Transmission Payloads
```python
from app.send_intake import create_encoded_transmission_payload

payload = create_encoded_transmission_payload(
    envelope_data=envelope_data,
    call_id=1234,
    additional_metadata={"source_system": "voice_agent_v2"}
)
```

## Testing

Run the test scripts to verify functionality:

```bash
# Comprehensive tests
python test_encoded_intake.py

# Simple example
python example_encoded_intake.py
```

## Benefits

1. **Security**: Encoded data is less readable during transmission
2. **Integrity**: Base64 encoding helps preserve data structure
3. **Compatibility**: Works with existing envelope processing
4. **Tracking**: Includes call_id and timestamp metadata
5. **Logging**: Full loguru integration for debugging

## Notes

- All functions include comprehensive logging
- Error handling follows existing patterns
- Maintains backward compatibility
- Integrates seamlessly with Clio API
- Supports both manual and automatic processing
