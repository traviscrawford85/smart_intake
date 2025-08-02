import requests


def fetch_matters_from_clio() -> list[MatterResponse]:
    response = requests.get("https://api.clio.com/.../matters", headers=...)
    payload = response.json()
    # If the schema is { "data": [ ... ] }
    return [MatterResponse(**item) for item in payload["data"]]
