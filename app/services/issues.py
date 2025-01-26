from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from app.models.Issuedb import Issue as IssueDb
from app.models.Userdb import User as UserDb
from app.schemas.issue import IssueType, GetIssuesResponse


def get_all_issues(db: Session) -> List[GetIssuesResponse]:
    return db.query(IssueDb).all()


def get_issues_by_user(db: Session, id: str):
    return db.query(IssueDb).filter(IssueDb.user_id == id).all()


def create_issue(
    db: Session, title: str, description: str, type: IssueType, user_id: str
):
    newIssue = IssueDb(
        title=title, description=description, type=type.value, user_id=user_id
    )
    db.add(newIssue)
    db.commit()
    return newIssue.id


def get_Issue_by_id(db: Session, id: str):
    return db.query(IssueDb).filter(IssueDb.id == id).scalar()


def update_issue(db: Session, id: str, toUpdate):
    db.query(IssueDb).filter(IssueDb.id == id).update(toUpdate)
    db.commit()


def delete_issue(db: Session, id: str):
    toDelete = db.query(IssueDb).filter(IssueDb.id == id).first()
    db.delete(toDelete)
    db.commit()


def check_if_issue_exists(db: Session, id: str):
    return db.query(exists().where(IssueDb.id == id)).scalar()


def get_user_by_issue_id(db: Session, issueId: str):
    issue = db.query(IssueDb).filter(IssueDb.id == issueId).first()
    return issue.user_id


def resolve_issue(db: Session, id: str):
    db.query(IssueDb).filter(IssueDb.id == id).update({"is_resolved": True})
    db.commit()
