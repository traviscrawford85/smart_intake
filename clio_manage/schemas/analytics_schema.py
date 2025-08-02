from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class QualifiedLead(BaseModel):
    id: int
    first_name: str
    last_name: str
    practice_area: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadReview(BaseModel):
    id: int
    lead_id: int
    reviewer_id: int
    reviewed_at: datetime
    status: str  # e.g. "approved", "rejected", "callback", "update_requested"
    notes: Optional[str]

    model_config = {"from_attributes": True}


class PracticeAreaChartData(BaseModel):
    practice_area: str
    lead_count: int

    model_config = {"from_attributes": True}


class NotificationSent(BaseModel):
    id: int
    lead_id: int
    recipient: str
    notification_type: str  # e.g. "email", "sms"
    sent_at: datetime
    status: str  # e.g. "delivered", "failed"

    model_config = {"from_attributes": True}


class TriageCallbackOrUpdate(BaseModel):
    id: int
    lead_id: int
    type: str  # "callback" or "update"
    requested_by: str
    requested_at: datetime
    status: str  # e.g. "pending", "completed"

    model_config = {"from_attributes": True}


class DashboardSummary(BaseModel):
    total_qualified_leads: int
    total_lead_reviews: int
    notifications_sent: int
    callbacks_or_updates: int
    practice_area_chart: List[PracticeAreaChartData]

    model_config = {"from_attributes": True}
