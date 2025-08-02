"""Analytics router for Clio Smart Intake Dashboard"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from clio_manage.db import SessionLocal as get_db
from clio_manage.models import (
    LeadReview,
    NotificationSent,
    QualifiedLead,
    TriageCallbackOrUpdate,
)
from clio_manage.schemas.analytics_schema import (
    DashboardSummary,
    LeadReview,
    NotificationSent,
    PracticeAreaChartData,
    QualifiedLead,
    TriageCallbackOrUpdate,
)
from clio_manage.services.analytics_service import get_dashboard_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary_endpoint(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/qualified_leads", response_model=List[QualifiedLead])
def get_qualified_leads(db: Session = Depends(get_db)):
    return db.query(QualifiedLead).all()


@router.get("/lead_reviews", response_model=List[LeadReview])
def get_lead_reviews(db: Session = Depends(get_db)):
    return db.query(LeadReview).all()


@router.get("/practice_area_chart", response_model=List[PracticeAreaChartData])
def get_practice_area_chart(db: Session = Depends(get_db)):
    from sqlalchemy import func

    from clio_manage.schemas.analytics_schema import PracticeAreaChartData

    results = (
        db.query(QualifiedLead.practice_area, func.count(QualifiedLead.id))
        .group_by(QualifiedLead.practice_area)
        .all()
    )
    return [
        PracticeAreaChartData(practice_area=pa, lead_count=count)
        for pa, count in results
    ]


@router.get("/notifications", response_model=List[NotificationSent])
def get_notifications(db: Session = Depends(get_db)):
    return db.query(NotificationSent).all()


@router.get("/triage_callbacks_updates", response_model=List[TriageCallbackOrUpdate])
def get_triage_callbacks_updates(db: Session = Depends(get_db)):
    return db.query(TriageCallbackOrUpdate).all()
