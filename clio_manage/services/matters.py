import requests
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from utils.universal_normalizer_function import normalize_field

def fetch_matters_from_clio() -> list[MatterResponse]:
    response = requests.get("https://api.clio.com/.../matters", headers=...)
    payload = response.json()
    # If the schema is { "data": [ ... ] }
    return [MatterResponse(**item) for item in payload["data"]]
