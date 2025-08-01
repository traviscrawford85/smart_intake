from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TaskAnalyticsBase(BaseModel):
    task_id: str
    matter_id: str
    user_id: str
    stage: str
    practice_area: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    completed_at: datetime | None = None


class TaskAnalyticsCreate(TaskAnalyticsBase):
    pass


class TaskAnalyticsRead(TaskAnalyticsBase):
    id: int

    class Config:
        from_attributes = True


# KPI Response Models
class TaskCompletionKPI(BaseModel):
    """Task completion KPI data"""

    total_tasks: int
    completed_tasks: int
    completion_rate: float
    average_completion_time: float

    model_config = {"from_attributes": True}


class MatterSummaryKPI(BaseModel):
    """Matter summary KPI data"""

    total_matters: int
    open_matters: int
    closed_matters: int
    active_matters: int

    model_config = {"from_attributes": True}


class TaskLoadByUser(BaseModel):
    """Task load distribution by user"""

    user: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int

    model_config = {"from_attributes": True}


class FilterOptions(BaseModel):
    """Available filter options for analytics"""

    users: list[str]
    practice_areas: list[str]
    matter_stages: list[str]
    responsible_staff: list[str]

    model_config = {"from_attributes": True}


# Webhook Models
class WebhookPayload(BaseModel):
    """Generic webhook payload from Clio"""

    event: str
    data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class WebhookResponse(BaseModel):
    """Standard webhook response"""

    status: str
    event: str
    message: str | None = None

    model_config = {"from_attributes": True}
