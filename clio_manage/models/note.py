from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Note(Base):
    __tablename__ = "notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    body: Mapped[str] = mapped_column(String, nullable=False)
    contact_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("contacts.id"), nullable=True
    )
    matter_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)
