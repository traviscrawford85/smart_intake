from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Communication(Base):
    __tablename__ = "communications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    matter_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sent_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Many-to-many with contacts can be added if needed
