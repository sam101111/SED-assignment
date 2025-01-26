from fastapi import APIRouter, Request, Depends, HTTPException, Form, Cookie
from typing import Annotated
from fastapi.responses import HTMLResponse
from app.middleware.sessionMangement import role_check
from app.schemas.issue import *
from app.services.issues import *
from app.services.users import check_if_user_exists, get_role_by_id
from app.services.sessions import check_if_session_exists, get_user_by_session
from app.database import get_db


router = APIRouter()


# Within the codebase Form() is used extensively,
# this is because to directly send HTML form data to the server the correct types need to be used
# Directly sending HTML form data heavily simplifies the code as there is no need for converting the data at any point.
@router.post("/")
async def post_issue(
    request: Request,
    title: Annotated[str, Form()],
    type: Annotated[IssueType, Form()],
    description: Annotated[str, Form()],
    db: Session = Depends(get_db),
    sessionID: str = Cookie(None),
):
    try:
        userId = get_user_by_session(db, sessionID)
        print(userId)
        return create_issue(db, title, description, type, userId)

    except:
        raise HTTPException(status_code=401, detail="Invalid session token provided")


@router.get("/{user_id}")
async def get_by_user(
    user_id: str, db: Session = Depends(get_db), sessionID: str = Cookie(None)
) -> list[GetIssuesByUserResponse]:
    if (
        get_user_by_session(db, sessionID) == user_id
        or role_check(True, sessionID, db) == True
    ):
        if not check_if_user_exists(db, user_id):
            raise HTTPException(status_code=404, detail="ID of user not found")
        return get_issues_by_user(db, user_id)
    else:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )


@router.get("/")
async def get_issues(
    db: Session = Depends(get_db), sessionID: str = Cookie(None)
) -> list[GetIssuesResponse]:
    try:
        is_admin = role_check(True, sessionID, db)
        print(is_admin)
        if is_admin:
            if not check_if_user_exists(db, get_user_by_session(db, sessionID)):
                raise HTTPException(status_code=404, detail="ID of user not found")
            return get_all_issues(db)

        else:
            raise HTTPException(
                status_code=403, detail="User does not have necessary permission"
            )
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )


@router.patch("/{id}")
# The "= None" ensures the user can update as many or as little values as they want without errors
async def patch_issue(
    id: str,
    title: Annotated[Optional[str], Form()] = None,
    type: Annotated[Optional[IssueType], Form()] = None,
    description: Annotated[Optional[str], Form()] = None,
    db: Session = Depends(get_db),
    sessionID: str = Cookie(None),
):
    try:
        userId = get_user_by_session(db, sessionID)
        userRole = get_role_by_id(db, userId)
        userIssueId = get_user_by_issue_id(db, id)
        if not check_if_issue_exists(db, id):
            raise HTTPException(status_code=404, detail="ID of issue not found")
    except:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )

    # Checks if the Issue that is being updated is owned by the user that made the request or if the user is an admin, if not raise 403
    if userIssueId == userId or userRole == True:
        issue = {"title": title, "type": type, "description": description}
        # loops through each pair and filters out any pairs where the value is None
        filteredIssue = {
            key: value for key, value in issue.items() if value is not None
        }
        print(filteredIssue)
        print(sessionID)
        try:
            update_issue(db, id, filteredIssue)
        except:
            raise HTTPException(status_code=422, detail="Must enter at least one value")
        raise HTTPException(status_code=200, detail="Issue has been updated")
    else:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )


@router.delete("/{id}")
async def delete(id: str, db: Session = Depends(get_db), sessionID: str = Cookie(None)):
    try:
        is_admin = role_check(True, sessionID, db)
    except:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )
    # As only admins can delete, this check ensures the user is an admin
    if is_admin:
        if not check_if_issue_exists(db, id):
            raise HTTPException(status_code=404, detail="ID of issue not found")
        delete_issue(db, id)
    else:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )


# Used to resolve an issue if a solution is found
@router.patch("/resolve/{id}")
async def resolve(
    id: str, db: Session = Depends(get_db), sessionID: str = Cookie(None)
):
    try:
        is_admin = role_check(True, sessionID, db)
    except:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )

    if is_admin:
        if not check_if_issue_exists(db, id):
            raise HTTPException(status_code=404, detail="ID of issue not found")
        resolve_issue(db, id)
    else:
        raise HTTPException(
            status_code=403, detail="User does not have necessary permission"
        )
