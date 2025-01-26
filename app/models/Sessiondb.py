from sqlalchemy import Column, String, DateTime
from app.database import Base
import uuid
from datetime import datetime, timedelta


class Session(Base):
    __tablename__ = "sessions"

    user_id = Column(String, nullable=False)
    session_id = Column(
        String,
        unique=True,
        index=True,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    expire_time = Column(
        DateTime, nullable=False, default=lambda: datetime.now() + timedelta(minutes=30)
    )
