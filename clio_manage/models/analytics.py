from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

from clio_manage.db import Base

Base = declarative_base()


class QualifiedLead(Base):
    __tablename__ = "qualified_leads"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    practice_area = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LeadReview(Base):
    __tablename__ = "lead_reviews"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("qualified_leads.id"), nullable=False)
    reviewer_id = Column(Integer, nullable=False)
    reviewed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)
    notes = Column(String, nullable=True)


class NotificationSent(Base):
    __tablename__ = "notifications_sent"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("qualified_leads.id"), nullable=False)
    recipient = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)


class TriageCallbackOrUpdate(Base):
    __tablename__ = "triage_callbacks_updates"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("qualified_leads.id"), nullable=False)
    type = Column(String, nullable=False)  # "callback" or "update"
    requested_by = Column(String, nullable=False)
    requested_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)
