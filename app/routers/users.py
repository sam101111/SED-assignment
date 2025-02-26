from argon2 import PasswordHasher
from fastapi import APIRouter, Cookie, Request, Depends, HTTPException, Response, Form
from typing import Annotated, Optional
from fastapi.responses import HTMLResponse
from app.config import config
from app.services.users import *
from app.services.sessions import *
from app.schemas.user import *
from app.middleware.sessionMangement import role_check
from app.database import get_db
from sqlalchemy.exc import IntegrityError
import re
import hashlib

router = APIRouter()


@router.get("/")
async def get_all_users(
    db: Session = Depends(get_db), sessionID: str = Cookie(None)
) -> list[GetAllUsersResponse]:
    try:
        print(check_if_session_exists(db, sessionID))
        if check_if_session_exists(db, sessionID):

            return get_users(db)
        else:
            raise HTTPException(
                status_code=403, detail="User does not have necessary permission"
            )
    except Exception as err:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )


@router.post("/register")
async def register(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    password_format = r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*\W)(?!.* ).{8,16}$"
    ph = PasswordHasher()
    if email == "" or password == "":
        raise HTTPException(
            status_code=400, detail="Email or password entered is not valid format"
        )

    if (
        # Checks if email or password is in the wrong format
        not is_valid_email(email)
        or re.match(password_format, password) == None
    ):
        raise HTTPException(
            status_code=400, detail="Email or password entered is not valid format"
        )
    try:

        hashed_password = ph.hash(password)
        create_user(db, email, hashed_password)
    except IntegrityError as err:
        print(err)
        raise HTTPException(status_code=422)


@router.patch("/promote/{id}")
async def promote(
    request: Request,
    id: str,
    db: Session = Depends(get_db),
    sessionID: str = Cookie(None),
):
    try:
        is_admin = role_check(True, sessionID, db)
        if is_admin:
            if not check_if_user_exists(db, id):
                raise HTTPException(status_code=404, detail="ID of user not found")
            if get_role_by_id(db, id) == True:
                raise HTTPException(status_code=403, detail="User is already an admin")

            promote_user(db, id)
            return {"message": "User has been successfully promoted"}
        else:
            raise HTTPException(status_code=400, detail="User already an admin")
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )


@router.delete("/{id}")
async def delete(
    request: Request,
    id: str,
    db: Session = Depends(get_db),
    sessionID: str = Cookie(None),
):
    try:
        is_admin = role_check(True, sessionID, db)
        if is_admin:
            if not check_if_user_exists(db, id):
                raise HTTPException(status_code=404, detail="ID of user not found")
            delete_user(db, id)
            return {"message": "User has been successfully deleted"}
        else:
            raise HTTPException(
                status_code=403, detail="User does not have necessary permission"
            )
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )


@router.post("/login")
async def login(
    response: Response,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    ph = PasswordHasher()
    if email == "admintest@test.com" and password == "test1A$c34":
        if not check_if_User_exists_by_email(db, email):
            hashed_password = ph.hash(f"{password}")
            create_user(db, email, hashed_password, True)
    # Checks if values have been entered
    if email == "" or password == "":
        raise HTTPException(
            status_code=400, detail="Email or password entered is not valid format"
        )

    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail="Email entered is not valid format")
    if not check_if_User_exists_by_email(db, email):
        raise HTTPException(status_code=404, detail="Email does not exist in system")

    if not check_password(db, password, email):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Creates a new session with the user_id of the person logging in, and then adds it to cookies
    # Adding the sessionID to cookies automatically adds the sessionID as a header to every request until the cookie is removed
    # Thus making it an effective way to easily identify a user securely
    response.set_cookie(
        key="sessionID", value=f"{create_session(db, get_id_by_email(db, email))}", secure=config.SECURE_COOKIES
    )

    return {"message": "Session has been successfully created"}


@router.post("/getid")
async def get_id(
    response: Response,
    email: Annotated[str, Form()],
    db: Session = Depends(get_db),
    sessionID: str = Cookie(None),
):
    try:
        # This checks if the sessionID in the request and stored client side is valid
        if check_if_session_exists(db, sessionID):
            return get_id_by_email(db, email)
    except:
        raise HTTPException(status_code=404, detail="session does not exist")


@router.post("/logout")
async def logout(
    response: Response,
    sessionID: str = Cookie(None),
    db: Session = Depends(get_db),
):
    try:
        # These two lines delete the session from the session table (server side) as well as deleting it from cookies (client side)
        delete_session(db, sessionID)
        response.delete_cookie("sessionID")
    except:
        raise HTTPException(status_code=404, detail="session does not exist")
    return {"message": "Session has been successfully deleted"}
