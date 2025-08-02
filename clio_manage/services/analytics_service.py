"""This file contains the implementation of the analytics service for the Clio Manage application."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from clio_manage.models import (
    LeadReview,
    NotificationSent,
    QualifiedLead,
    TriageCallbackOrUpdate,
)
from clio_manage.models.analytics import (
    LeadReview,
    NotificationSent,
    QualifiedLead,
    TriageCallbackOrUpdate,
)
from clio_manage.schemas.analytics_schema import DashboardSummary, PracticeAreaChartData


def get_dashboard_summary(db: Session) -> DashboardSummary:
    total_qualified_leads = db.query(QualifiedLead).count()
    total_lead_reviews = db.query(LeadReview).count()
    notifications_sent = db.query(NotificationSent).count()
    callbacks_or_updates = db.query(TriageCallbackOrUpdate).count()
    practice_area_chart = (
        db.query(QualifiedLead.practice_area, func.count(QualifiedLead.id))
        .group_by(QualifiedLead.practice_area)
        .all()
    )
    chart_data = [
        PracticeAreaChartData(practice_area=pa, lead_count=count)
        for pa, count in practice_area_chart
    ]
    return DashboardSummary(
        total_qualified_leads=total_qualified_leads,
        total_lead_reviews=total_lead_reviews,
        notifications_sent=notifications_sent,
        callbacks_or_updates=callbacks_or_updates,
        practice_area_chart=chart_data,
    )
