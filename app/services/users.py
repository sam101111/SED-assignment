from sqlalchemy.orm import Session
from app.models.Userdb import User as UserDb
from app.schemas.user import *
from sqlalchemy.sql import exists
import hashlib


def create_user(db: Session, email: str, password: str, isAdmin: bool = False):
    user = UserDb(email=email, password=password, isAdmin=isAdmin)
    db.add(user)
    db.commit()


def delete_user(db: Session, id: str):

    toDelete = db.query(UserDb).filter(UserDb.id == id).first()
    db.delete(toDelete)
    db.commit()


def update_user(db: Session, id: str, toUpdate):
    db.query(UserDb).filter(UserDb.id == id).update(toUpdate)
    db.commit()


def get_users(db: Session):
    return db.query(UserDb).all()


def promote_user(db: Session, id: str):
    db.query(UserDb).filter(UserDb.id == id).update({"isAdmin": True})
    db.commit()


def get_user(db: Session, id: str):
    return db.query(UserDb).filter(UserDb.id == id).scalar()


def check_if_user_exists(db: Session, id: str):
    return db.query(exists().where(UserDb.id == id)).scalar()


def check_if_User_exists_by_email(db: Session, email: str):
    return db.query(exists().where(UserDb.email == email)).scalar()


def check_password(db: Session, password: str, email: str):
    user = db.query(UserDb).filter(UserDb.email == email).first()
    if user.password == hashlib.sha256(password.encode()).hexdigest():
        return True
    else:
        return False


def get_id_by_email(db: Session, email: str):
    user = db.query(UserDb).filter(UserDb.email == email).first()
    return user.id


def get_role_by_id(db: Session, id: str):
    user = db.query(UserDb).filter(UserDb.id == id).first()
    return user.isAdmin
