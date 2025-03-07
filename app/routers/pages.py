from typing import Optional
from fastapi import APIRouter, Request, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.users import get_role_by_id, get_users, get_role_by_id
from app.database import get_db
from app.services.issues import get_all_issues, get_issues_by_user
from app.services.sessions import check_if_session_exists, get_user_by_session
from sqlalchemy.orm import Session
from app.middleware.sessionMangement import role_check

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home_page(
    req: Request, sessionID: Optional[str] = Cookie(None), db: Session = Depends(get_db)
):
    context = {"request": req}
    # This check means a user must be logged in to view this page
    if check_if_session_exists(db, sessionID):
        return templates.TemplateResponse(name="index.html", request=req)
    else:
        return templates.TemplateResponse("unauthorised.html", context)


@router.get("/issues", response_class=HTMLResponse)
def issues_page(
    req: Request, db: Session = Depends(get_db), sessionID: Optional[str] = Cookie(None)
):
    context = {"request": req}
    try:

        if check_if_session_exists(db, sessionID):
            issues = get_issues_by_user(db, get_user_by_session(db, sessionID))
            user_id = get_user_by_session(db, sessionID)
            is_admin = role_check(True, sessionID, db)
            context = {
                "request": req,
                "issues": issues,
                "user_id": user_id,
                "page": "issues",
                "is_admin": is_admin,
            }
            print(context)
            return templates.TemplateResponse("issues.html", context)
        else:

            return templates.TemplateResponse("unauthorised.html", context)
    except:
        return templates.TemplateResponse("unauthorised.html", context)


@router.get("/directory", response_class=HTMLResponse)
def directory_page(
    req: Request, db: Session = Depends(get_db), sessionID: Optional[str] = Cookie(None)
):
    context = {"request": req}
    try:
        if check_if_session_exists(db, sessionID):
            users = get_users(db)
            is_admin = role_check(True, sessionID, db)
            user_id = get_user_by_session(db, sessionID)
            user_role = get_role_by_id(db, get_user_by_session(db, sessionID))
            context = {
                "request": req,
                "users": users,
                "role": user_role,
                "is_admin": is_admin,
                "page": "directory",
                "user_id": user_id,
            }
            return templates.TemplateResponse("userDirectory.html", context)
        else:
            return templates.TemplateResponse("unauthorised.html", context)
    except:
        return templates.TemplateResponse("unauthorised.html", context)


@router.get("/login", response_class=HTMLResponse)
def login_page(req: Request):
    context = {"request": req}
    return templates.TemplateResponse("login.html", context)


@router.get("/manage", response_class=HTMLResponse)
async def manage_page(
    req: Request, db: Session = Depends(get_db), sessionID: Optional[str] = Cookie(None)
):
    context = {"request": req}
    try:
        # SessionID is obtained via cookies
        is_admin = role_check(True, sessionID, db)
        # This check insures only admin users are able to access this site
        if is_admin:
            issues = get_all_issues(db)
            user_id = get_user_by_session(db, sessionID)
            context = {
                "request": req,
                "issues": issues,
                "is_admin": is_admin,
                "page": "manage",
                "user_id": user_id,
            }
            # returns the admin page
            return templates.TemplateResponse("manage.html", context)
        else:
            # If the user is not an admin they will be taken to the unauthorised page
            return templates.TemplateResponse("unauthorised.html", context)
    except:
        return templates.TemplateResponse("unauthorised.html", context)


@router.get("/register", response_class=HTMLResponse)
async def register_page(req: Request):
    context = {"request": req}
    return templates.TemplateResponse("register.html", context)
