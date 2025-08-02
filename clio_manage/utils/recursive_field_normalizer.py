import base64
import json


def try_base64_decode(value):
    if not isinstance(value, str):
        return value
    try:
        decoded = base64.b64decode(value, validate=True)
        as_str = decoded.decode("utf-8")
        if as_str.strip().startswith(("{", "[")):
            return as_str
        return value
    except Exception:
        return value


def try_json_parse(value):
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except Exception:
        return value


def normalize_field(value):
    v = try_base64_decode(value)
    v = try_json_parse(v)
    # Try again if it’s a string that might need another decode
    if isinstance(v, str):
        v2 = try_base64_decode(v)
        v2 = try_json_parse(v2)
        if v2 != v:
            return v2
    return v


def recursive_normalize(data):
    """
    Recursively walk through a dict or list, normalizing all string fields that might be base64 or JSON.
    """
    if isinstance(data, dict):
        return {k: recursive_normalize(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_normalize(item) for item in data]
    else:
        return normalize_field(data)
