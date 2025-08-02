from datetime import datetime, timedelta
from typing import Optional

import httpx

from clio_manage.utils.clio_api_helpers import clio_api_helper


class TriageService:
    def __init__(self, api_helper=None):
        self.api_helper = api_helper or clio_api_helper
        self.base_url = "https://app.clio.com/api/v4"

    async def triage_lead(
        self,
        client: httpx.AsyncClient,
        lead_data: dict,
        note_content: str,
        assignee_id: str,
        due_at: Optional[datetime] = None,
        communication_body: Optional[str] = None,
        lead_tag_id: Optional[str] = None,
        notify_email: Optional[str] = None,
    ):
        # 1. Create Contact
        contact_payload = {
            "data": {
                "first_name": lead_data["first_name"],
                "last_name": lead_data["last_name"],
                "email": lead_data.get("email"),
                "phone_number": lead_data.get("phone_number"),
            }
        }
        if lead_tag_id:
            contact_payload["data"]["tag_ids"] = [lead_tag_id]
        contact_resp = await client.post(
            f"{self.base_url}/contacts", json=contact_payload
        )
        contact_resp.raise_for_status()
        contact = contact_resp.json()["data"]
        contact_id = contact["id"]

        # 2. Add Note
        note_payload = {
            "data": {
                "content": note_content,
                "notable_type": "Contact",
                "notable_id": contact_id,
            }
        }
        note_resp = await client.post(f"{self.base_url}/notes", json=note_payload)
        note_resp.raise_for_status()

        # 3. Create Task
        task_payload = {
            "data": {
                "description": f"Review new intake lead: {lead_data['first_name']} {lead_data['last_name']}. Needs triage or referral.",
                "assignee_id": assignee_id,
                "due_at": (
                    due_at or (datetime.utcnow() + timedelta(days=1))
                ).isoformat()
                + "Z",
                "related_resource_id": contact_id,
                "related_resource_type": "Contact",
            }
        }
        task_resp = await client.post(f"{self.base_url}/tasks", json=task_payload)
        task_resp.raise_for_status()

        # 4. (Optional) Log Communication
        comm_result = None
        if communication_body:
            comm_payload = {
                "data": {
                    "type": "note",
                    "body": communication_body,
                    "contact_id": contact_id,
                    "date": datetime.utcnow().isoformat() + "Z",
                }
            }
            comm_resp = await client.post(
                f"{self.base_url}/communications", json=comm_payload
            )
            comm_resp.raise_for_status()
            comm_result = comm_resp.json()["data"]

        # 5. (Optional) Notify outside Clio (email)
        if notify_email:
            await self.send_email_notification(
                to_email=notify_email,
                subject="New Lead Requires Review",
                body=f"A new lead for {lead_data['first_name']} {lead_data['last_name']} requires review. See Clio contact: {contact_id}",
            )

        return {
            "contact": contact,
            "note": note_resp.json()["data"],
            "task": task_resp.json()["data"],
            "communication": comm_result,
        }

    async def send_email_notification(self, to_email: str, subject: str, body: str):
        # Implement your email sending logic here (e.g., SMTP, SendGrid, etc.)
        # For now, just log the notification
        print(f"[EMAIL] To: {to_email}\nSubject: {subject}\nBody: {body}")
        # You can integrate with an async email library or background task
        return True


# Usage: triage_service = TriageService()
