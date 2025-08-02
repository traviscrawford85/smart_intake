API_SETTINGS = "http://127.0.0.1:8000/settings"


# --- Settings & Webhooks API ---
def get_api_tokens():
    resp = requests.get(f"{API_SETTINGS}/api_tokens")
    if resp.ok:
        return resp.json().get("tokens", [])
    return []


def revoke_api_token(token: str):
    return requests.post(f"{API_SETTINGS}/api_tokens/revoke", json={"token": token})


def generate_api_token():
    return requests.post(f"{API_SETTINGS}/api_tokens/generate")


def get_incoming_webhooks():
    resp = requests.get(f"{API_SETTINGS}/webhooks/incoming")
    if resp.ok:
        return resp.json().get("webhooks", [])
    return []


def toggle_incoming_webhook(url: str):
    return requests.post(f"{API_SETTINGS}/webhooks/incoming/toggle", json={"url": url})


def add_incoming_webhook(url: str, enabled: bool):
    return requests.post(
        f"{API_SETTINGS}/webhooks/incoming/add", json={"url": url, "enabled": enabled}
    )


def get_outgoing_webhooks():
    resp = requests.get(f"{API_SETTINGS}/webhooks/outgoing")
    if resp.ok:
        return resp.json().get("webhooks", [])
    return []


def delete_outgoing_webhook(webhook_id: str):
    return requests.delete(f"{API_SETTINGS}/webhooks/outgoing/{webhook_id}/delete")


def add_outgoing_webhook(name: str, url: str, event_types: list[str]):
    payload = {"name": name, "url": url, "event_types": event_types}
    return requests.post(f"{API_SETTINGS}/webhooks/outgoing/add", json=payload)


"""
Backend API client for Smart Intake Dashboard analytics.
"""
from typing import Any, Dict, List, Optional

import requests

API_BASE = "http://127.0.0.1:8000/api/analytics"


def get_dashboard_summary() -> Optional[Dict[str, Any]]:
    resp = requests.get(f"{API_BASE}/summary")
    if resp.ok:
        return resp.json()
    return None


def get_qualified_leads() -> List[Dict[str, Any]]:
    resp = requests.get(f"{API_BASE}/qualified_leads")
    return resp.json() if resp.ok else []


def get_lead_reviews() -> List[Dict[str, Any]]:
    resp = requests.get(f"{API_BASE}/lead_reviews")
    return resp.json() if resp.ok else []


def get_practice_area_chart() -> List[Dict[str, Any]]:
    resp = requests.get(f"{API_BASE}/practice_area_chart")
    return resp.json() if resp.ok else []


def get_notifications() -> List[Dict[str, Any]]:
    resp = requests.get(f"{API_BASE}/notifications")
    return resp.json() if resp.ok else []


def get_triage_callbacks_updates() -> List[Dict[str, Any]]:
    resp = requests.get(f"{API_BASE}/triage_callbacks_updates")
    return resp.json() if resp.ok else []
