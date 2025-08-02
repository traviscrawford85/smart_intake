import base64
import json


def try_base64_decode(value):
    """
    Try base64 decode. Return decoded string if successful, else return original.
    """
    if not isinstance(value, str):
        return value
    try:
        # Try decode (ignore if value isn't valid base64)
        decoded = base64.b64decode(value, validate=True)
        # Only accept if result decodes cleanly to utf-8
        as_str = decoded.decode("utf-8")
        # Avoid false positives: base64'd JSON will look like {" or [
        if as_str.strip().startswith(("{", "[")):
            return as_str
        return value  # Looks like plain text, not base64-JSON
    except Exception:
        return value


def try_json_parse(value):
    """
    Try json.loads. Return dict/list if possible, else original.
    """
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except Exception:
        return value


def normalize_field(value):
    """
    For a field that could be:
      - Plain text
      - Base64-encoded text
      - Base64-encoded JSON string
    Try to decode and parse, and always return the deepest object.
    """
    v = try_base64_decode(value)
    v = try_json_parse(v)
    # If parsing led to another base64 string, try again (recursion, max 2x to avoid endless loop)
    if isinstance(v, str):
        v2 = try_base64_decode(v)
        v2 = try_json_parse(v2)
        if v2 != v:
            return v2
    return v


# Example: parsing message fields in an array of leads
def normalize_leads(data):
    """
    Walks through list of leads (dicts), normalizing 'message' and optionally other fields.
    """
    normalized = []
    for lead in data.get("inbox_leads", []):
        # Normalize 'message' field
        if "message" in lead:
            lead["message"] = normalize_field(lead["message"])
        # If you know other fields that need it, do the same:
        # if 'notes' in lead: lead['notes'] = normalize_field(lead['notes'])
        normalized.append(lead)
    return normalized


# Example usage:
# payload = ... (dict from Clio or elsewhere)
# leads = normalize_leads(payload)
# print(leads[0]['message'])  # Now will be plain text or dict, never base64 junk
