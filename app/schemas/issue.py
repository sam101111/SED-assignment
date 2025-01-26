from enum import Enum
from pydantic import BaseModel
from typing import Optional

from app.schemas.user import GetAllUsersResponse


class IssueType(str, Enum):
    SERVICE_REQUEST = "Service request"
    INCIDENT_REPORT = "Incident report"
    BUG = "Bug"
    ACCOUNT_AND_ACCESS = "Account and Access"


class IssueBase(BaseModel):
    title: str
    type: IssueType
    description: str

    class Config:
        orm_mode = True
        from_attributes = True


class GetIssuesByUserResponse(IssueBase):
    id: str
    user_id: str
    is_resolved: bool
    user: GetAllUsersResponse

    class Config:
        orm_mode = True
        from_attributes = True


class GetIssuesResponse(IssueBase):
    id: str
    user_id: str
    is_resolved: bool
    user: GetAllUsersResponse

    class Config:
        orm_mode = True
        from_attributes = True


class CreateIssue(IssueBase):
    user_id: str


class ReadIssues(BaseModel):
    user_id: str


class ReadAllIssues(BaseModel):
    pass


class ReadIssue(IssueBase):
    pass


class UpdateIssue(BaseModel):
    type: Optional[IssueType]
    title: Optional[str]
    description: Optional[str]


class DeleteIssue(BaseModel):
    id: str


class IssueResponse:
    pass
