from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from app.models.Sessiondb import Session as SessionDb


def create_session(db: Session, user_id: str):
    session = SessionDb(user_id=user_id)
    db.add(session)
    db.commit()
    return session.session_id


def get_user_by_session(db: Session, session_id: str) -> str:
    session = db.query(SessionDb).filter(SessionDb.session_id == session_id).first()
    return session.user_id


def delete_session(db: Session, session_id: str):
    toDelete = db.query(SessionDb).filter(SessionDb.session_id == session_id).first()
    db.delete(toDelete)
    db.commit()


def check_if_session_exists(db: Session, id: str):
    return db.query(exists().where(SessionDb.session_id == id)).scalar()
