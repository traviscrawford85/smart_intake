
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from app.config import DATABASE_URL

# Import the new models
from app.models import Base as ModelsBase, IntakeLead

# Keep the legacy Base for existing models
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize both legacy and new model tables."""
    Base.metadata.create_all(bind=engine)
    ModelsBase.metadata.create_all(bind=engine)
