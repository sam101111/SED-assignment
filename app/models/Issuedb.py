from sqlalchemy import Column, ForeignKey, String, Enum as dbEnum, Boolean
from sqlalchemy.orm import relationship
from app.schemas.issue import IssueType
from app.database import Base
import uuid


class Issue(Base):
    __tablename__ = "issues"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True, nullable=False)
    description = Column(String, index=True, nullable=False)
    type = Column(dbEnum(IssueType), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="issues")
