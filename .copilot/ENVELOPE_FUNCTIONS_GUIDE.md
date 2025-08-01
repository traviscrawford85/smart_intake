# Envelope Processing Functions - Usage Guide

## 🎯 Overview
Your Clio Intake Agent now supports multiple payload formats with dedicated envelope processing functions for handling Capture Now voice agent data and web form submissions.

## ✅ Available Functions

### 1. **validate_envelope(envelope: dict) -> list[str]**
Returns a list of missing required fields from an envelope.

```python
from app.send_intake import validate_envelope

envelope = {
    "first_name": "John",
    "message": "I need legal help"
    # Missing: last_name, referring_url, source
}

missing = validate_envelope(envelope)
print(missing)  # ['last_name', 'referring_url', 'source']
```

### 2. **map_envelope_to_clio_lead(envelope: dict) -> dict**
Maps Capture Now envelope fields to Clio Grow Lead Inbox payload format.

```python
from app.send_intake import map_envelope_to_clio_lead

envelope = {
    "first_name": "Minnie",
    "last_name": "Mouse",
    "message": "Full voice transcript here...",
    "email": "mini.mouse@disney.plus.com",
    "phone_number": "4045141488",
    "referring_url": "http://lcx.com",
    "source": "LCX"
}

payload = map_envelope_to_clio_lead(envelope)
# Add your token
payload["inbox_lead_token"] = "YOUR_LEAD_INBOX_TOKEN"

# Result:
{
  "inbox_lead": {
    "from_first": "Minnie",
    "from_last": "Mouse", 
    "from_message": "Full voice transcript here...",
    "from_email": "mini.mouse@disney.plus.com",
    "from_phone": "4045141488",
    "referring_url": "http://lcx.com",
    "from_source": "LCX"
  },
  "inbox_lead_token": "YOUR_LEAD_INBOX_TOKEN"
}
```

### 3. **process_envelope_payload(envelope: dict) -> Tuple[dict, int]**
Complete processing of a Capture Now envelope - validates, maps, and sends to Clio.

```python
from app.send_intake import process_envelope_payload

envelope = {
    "first_name": "Sarah",
    "last_name": "Johnson",
    "message": "I was in a car accident and need legal help...",
    "email": "sarah@email.com",
    "phone_number": "555-123-4567",
    "referring_url": "phone",
    "source": "Capture Now Bot"
}

response, status = process_envelope_payload(envelope)

if status == 201:
    print("✅ Lead created successfully!")
    print(f"Clio ID: {response['inbox_lead']['id']}")
else:
    print(f"❌ Failed: {status} - {response}")
```

### 4. **create_clio_lead(data: dict) -> Tuple[dict, int]**
Enhanced main function that auto-detects and handles both envelope and direct formats.

```python
from app.send_intake import create_clio_lead

# Works with envelope format
envelope_data = {
    "first_name": "John",
    "last_name": "Smith", 
    "message": "Legal consultation needed",
    "email": "john@example.com",
    "referring_url": "https://law-firm.com",
    "source": "Voice Agent"
}

# Works with direct format
direct_data = {
    "inbox_lead": {
        "from_first": "Jane",
        "from_last": "Doe",
        "from_message": "Personal injury case",
        "from_email": "jane@example.com"
    }
}

# Both work the same way
response1, status1 = create_clio_lead(envelope_data)
response2, status2 = create_clio_lead(direct_data)
```

## 🚀 FastAPI Integration

Use the FastAPI proxy server for production webhook handling:

```python
# Start the server
python fastapi_proxy.py

# Endpoints available:
# POST /webhook/web-form        - Direct Clio format
# POST /webhook/capture-now     - Envelope format  
# POST /webhook/unified         - Auto-detect format
# POST /webhook/legacy          - Simple processing
# GET  /health                  - Health check
# GET  /validate/{endpoint}     - Validation test
```

### Webhook Examples

**Capture Now Voice Agent:**
```bash
curl -X POST http://localhost:8000/webhook/capture-now \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "message": "Full Voice agent transcript here.",
    "email": "john@example.com", 
    "phone_number": "0987654321",
    "referring_url": "phone",
    "source": "Capture Now Agent"
  }'
```

**Web Contact Form:**
```bash
curl -X POST http://localhost:8000/webhook/web-form \
  -H "Content-Type: application/json" \
  -d '{
    "inbox_lead": {
      "from_first": "Jane",
      "from_last": "Doe",
      "from_message": "I was in an Auto Accident", 
      "from_email": "jane@example.com",
      "from_phone": "1234567890",
      "referring_url": "https://www.ledyardlaw.com/contact",
      "from_source": "Website Contact Form"
    }
  }'
```

## 🔧 Configuration

### Required Fields
```python
REQUIRED_FIELDS = ["first_name", "last_name", "message", "referring_url", "source"]
```

### Fallback Values
```python
# Used when envelope fields are missing
"from_first": envelope.get("first_name", "Unknown")
"from_last": envelope.get("last_name", "Unknown")  
"from_message": envelope.get("message", "")
"from_email": envelope.get("email", "")
"from_phone": envelope.get("phone_number", "")
"referring_url": envelope.get("referring_url", "phone")
"from_source": envelope.get("source", "Capture Now Bot")
```

## 📊 Real-World Examples

### Voice Agent Webhook
Your voice agent sends this envelope:
```json
{
  "first_name": "Maria",
  "last_name": "Rodriguez",
  "phone_number": "555-987-6543", 
  "email": "maria@email.com",
  "message": "State: California City: Los Angeles ... I need help with a personal injury case from a car accident last month...",
  "referring_url": "phone",
  "source": "Capture Now Bot",
  "call_duration": "4:32",
  "timestamp": "2025-07-29T14:30:00Z"
}
```

Process it:
```python
response, status = process_envelope_payload(envelope)
# ✅ Status: 201 - Lead created with ID 27193151
```

### Web Form Submission  
Your website sends this direct payload:
```json
{
  "inbox_lead": {
    "from_first": "David",
    "from_last": "Chen", 
    "from_message": "I need help with divorce proceedings",
    "from_email": "david@email.com",
    "from_phone": "555-123-4567",
    "referring_url": "https://family-law.com/contact",
    "from_source": "Website Contact Form"
  },
  "inbox_lead_token": "YOUR_TOKEN"
}
```

Process it:
```python
response, status = create_clio_lead(direct_payload)
# ✅ Status: 201 - Lead created successfully
```

## 🎯 Best Practices

1. **Use Specific Endpoints**: Use `/webhook/capture-now` for voice agents, `/webhook/web-form` for forms
2. **Fallback to Unified**: Use `/webhook/unified` for mixed environments
3. **Validate Before Sending**: Use `validate_envelope()` to check data quality
4. **Monitor Logs**: All functions provide detailed logging with loguru
5. **Handle Errors Gracefully**: Check status codes and handle 401/422 responses
6. **Database Integration**: Pass `db` session to save leads locally

## ✅ Testing Results

All envelope functions tested successfully:
- ✅ Envelope validation working
- ✅ Envelope mapping working  
- ✅ Complete envelope processing working
- ✅ FastAPI integration working
- ✅ Real Clio API integration working (Status 201)
- ✅ Auto-detection working
- ✅ Fallback handling working

Your envelope processing system is **production-ready**! 🚀
