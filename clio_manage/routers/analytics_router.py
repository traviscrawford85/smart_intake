"""Analytics router for Clio Smart Intake Dashboard"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from clio_manage.db import SessionLocal as get_db
from clio_manage.models import LeadReview as LeadReviewModel
from clio_manage.models import NotificationSent as NotificationSentModel
from clio_manage.models import QualifiedLead as QualifiedLeadModel
from clio_manage.models import TriageCallbackOrUpdate as TriageCallbackOrUpdateModel
from clio_manage.schemas.analytics_schema import DashboardSummary
from clio_manage.schemas.analytics_schema import LeadReview as LeadReviewSchema
from clio_manage.schemas.analytics_schema import (
    NotificationSent as NotificationSentSchema,
)
from clio_manage.schemas.analytics_schema import PracticeAreaChartData
from clio_manage.schemas.analytics_schema import QualifiedLead as QualifiedLeadSchema
from clio_manage.schemas.analytics_schema import (
    TriageCallbackOrUpdate as TriageCallbackOrUpdateSchema,
)
from clio_manage.services.analytics_service import get_dashboard_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary_endpoint(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)


@router.get("/qualified_leads", response_model=List[QualifiedLeadSchema])
def get_qualified_leads(db: Session = Depends(get_db)):
    return db.query(QualifiedLeadModel).all()


@router.get("/lead_reviews", response_model=List[LeadReviewSchema])
def get_lead_reviews(db: Session = Depends(get_db)):
    return db.query(LeadReviewModel).all()


@router.get("/practice_area_chart", response_model=List[PracticeAreaChartData])
def get_practice_area_chart(db: Session = Depends(get_db)):
    results = (
        db.query(QualifiedLeadModel.practice_area, func.count(QualifiedLeadModel.id))
        .group_by(QualifiedLeadModel.practice_area)
        .all()
    )
    return [
        PracticeAreaChartData(practice_area=pa, lead_count=count)
        for pa, count in results
    ]


@router.get("/notifications", response_model=List[NotificationSentSchema])
def get_notifications(db: Session = Depends(get_db)):
    return db.query(NotificationSentModel).all()


@router.get(
    "/triage_callbacks_updates", response_model=List[TriageCallbackOrUpdateSchema]
)
def get_triage_callbacks_updates(db: Session = Depends(get_db)):
    return db.query(TriageCallbackOrUpdateModel).all()
