from datetime import datetime

from sqlalchemy import DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from clio_manage.config import DATABASE_URL
from clio_manage.models import Base as ModelsBase

# Keep the legacy Base for existing models
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column


class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    app_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    integration: Mapped[Optional[str]] = mapped_column(String, nullable=True)


def init_db():
    """Initialize both legacy and new model tables."""
    Base.metadata.create_all(bind=engine)
    ModelsBase.metadata.create_all(bind=engine)
