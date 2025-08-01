# Copilot:
# This module is part of the `clio_kpi_dashboard` project, which uses FastAPI for backend APIs,
# SQLAlchemy for models, and Streamlit for frontend dashboards.
# Implement logic for a modular, resource-specific component (e.g., tasks, matters, clients).
# Follow these conventions:
# - Use Pydantic models for schemas and FastAPI request/response models.
# - Use SQLAlchemy ORM for database queries.
# - Avoid hardcoded strings; use constants/enums where possible.
# - Support filtering, pagination, and sorting as needed.
# - Return JSON-serializable structures (dicts, lists of dicts).
# - Minimize duplication by extracting reusable logic into helpers.
# Extend this file to support the following:
# 1. CRUD operations for [Tasks]
# 2. Metrics/KPI summaries
# 3. Dashboard-friendly aggregations
# The database session is provided via dependency injection (`db: Session`).

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Base task schema
class TaskBase(BaseModel):
    """Base task schema with common fields"""

    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    name: str | None = Field(None, max_length=255, description="Task name")
    description: str | None = Field(None, description="Task description")
    due_date: date | None = Field(None, description="Task due date")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Task status")
    priority: TaskPriority | None = Field(None, description="Task priority")
    assigned_to: str | None = Field(None, max_length=255, description="Assigned user")
    matter_id: int | None = Field(None, description="Associated matter ID")


# Request schemas
class TaskCreate(TaskBase):
    """Schema for creating a new task"""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task"""

    title: str | None = Field(None, min_length=1, max_length=255)
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    due_date: date | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to: str | None = Field(None, max_length=255)
    matter_id: int | None = None
    completed: bool | None = None


# Response schemas
class TaskOut(TaskBase):
    """Schema for task responses"""

    id: int = Field(..., description="Task ID")
    completed: bool = Field(False, description="Task completion status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True  # Updated for Pydantic v2


class TaskList(BaseModel):
    """Schema for paginated task lists"""

    tasks: list[TaskOut] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


# Metrics and analytics schemas
class TaskMetrics(BaseModel):
    """Task performance metrics schema"""

    total_tasks: int = Field(0, description="Total number of tasks")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    pending_tasks: int = Field(0, description="Number of pending tasks")
    in_progress_tasks: int = Field(0, description="Number of in-progress tasks")
    overdue_tasks: int = Field(0, description="Number of overdue tasks")
    completion_rate: float = Field(0.0, description="Task completion rate (0-100)")
    average_completion_time: float | None = Field(
        None, description="Average completion time in days"
    )


class TaskStatusCount(BaseModel):
    """Task count by status"""

    status: TaskStatus = Field(..., description="Task status")
    count: int = Field(..., description="Number of tasks with this status")


class TasksByAssignee(BaseModel):
    """Task distribution by assignee"""

    assignee: str | None = Field(..., description="Assigned user")
    count: int = Field(..., description="Number of tasks assigned")
    completed: int = Field(..., description="Number of completed tasks")
    pending: int = Field(..., description="Number of pending tasks")


# Query parameter schemas
class TaskFilters(BaseModel):
    """Query parameters for filtering tasks"""

    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to: str | None = None
    matter_id: int | None = None
    due_date_from: date | None = None
    due_date_to: date | None = None
    completed: bool | None = None


class PaginationParams(BaseModel):
    """Pagination parameters"""

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")


# Legacy schema for backward compatibility
class TaskSchema(TaskOut):
    """Legacy task schema for backward compatibility"""

    pass


class TaskPerformance(TaskMetrics):
    """Legacy task performance schema for backward compatibility"""

    pass
