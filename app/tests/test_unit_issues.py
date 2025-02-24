import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def login_user():
    client.post(
        "/api/auth/register", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    login_request = client.post(
        "/api/auth/login", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    assert login_request.status_code == 200
    sessionID = login_request.cookies.get("sessionID")
    assert sessionID is not None
    yield
    headers = {"Cookie": f"sessionID={sessionID}"}
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200


@pytest.fixture()
def login_admin():
    login_request = client.post(
        "/api/auth/login",
        data={"email": "admintest@test.com", "password": "test1A$c34"},
    )
    assert login_request.status_code == 200
    sessionID = login_request.cookies.get("sessionID")
    assert sessionID is not None
    yield
    headers = {"Cookie": f"sessionID={sessionID}"}
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == 200


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_issue(test_db, login_user):
    response = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert response.status_code == 200

def test_XSS_attack_on_issue_title(test_db, login_user):
    xss_payload = "<script>alert('XSS')</script>"

    issue = client.post(
        "/api/issues",
        data={
            "title": xss_payload,
            "type": "Bug",
            "description": "really good test issue",
        },
    )

    assert issue.status_code == 200, f"Unexpected status code: {issue.status_code}, Response: {issue.text}"

    issue_response = issue.json()
    issue_id = issue_response
    assert issue_id is not None, "Issue ID is None or invalid"

    # Get user ID
    get_id = client.post("/api/auth/getid", data={"email": "test2@test.com"})
    assert get_id.status_code == 200, f"Failed to retrieve user ID: {get_id.text}"

    user_id = get_id.content.decode().replace('"', "")

    # Fetch issues for the user
    response = client.get(f"/api/issues/{user_id}")
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, Response: {response.text}"

    response_data = response.json()
    assert response_data, "Response data is empty"

    # Ensure the issue exists in the response
    issue_data = next((i for i in response_data if i["id"] == issue_id), None)
    assert issue_data, "Issue not found in response"

    assert issue_data["title"] == xss_payload, "XSS payload was modified or escaped incorrectly"
    assert "<script>" in issue_data["title"], "Script tags were removed (sanitization may be too aggressive)"
    
    print("XSS test passed: Input was stored safely as a string")


def test_create_issue_bad_type(test_db, login_user):
    response = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "wrong_type",
            "description": "really good test issue",
        },
    )
    assert response.status_code == 422


def test_create_issue_bad_type(test_db, login_user):
    response = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "wrong_type",
            "description": "really good test issue",
        },
    )
    assert response.status_code == 422


def test_create_issue_missing_title(test_db, login_user):
    response = client.post(
        "/api/issues",
        data={"title": "", "type": "Bug", "description": "really good test issue"},
    )
    assert response.status_code == 422


def test_create_issue_missing_description(test_db, login_user):
    response = client.post(
        "/api/issues", data={"title": "test issue", "type": "Bug", "description": ""}
    )
    assert response.status_code == 422


def test_create_issue_missing_type(test_db, login_user):
    response = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "",
            "description": "really good test issue",
        },
    )
    assert response.status_code == 422


def test_get_user_issues(test_db, login_user):
    issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    issue_response = issue.json()
    issue_id = issue_response
    assert issue.status_code == 200
    get_id = client.post("/api/auth/getid", data={"email": "test2@test.com"})
    assert get_id.status_code == 200
    user_id = get_id.content.decode().replace('"', "")
    expected = [
        {
            "title": "test issue",
            "type": "Bug",
            "id": f"{issue_id}",
            "user_id": f"{user_id}",
            "description": "really good test issue",
            "is_resolved": False,
        }
    ]
    response = client.get(f"/api/issues/{user_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data[0]["id"] == issue_id


def test_get_user_issues_as_wrong_user(test_db):
    client.post(
        "/api/auth/register", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    login_request = client.post(
        "/api/auth/login", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    assert login_request.status_code == 200

    issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    issue_response = issue.json()
    issue_id = issue_response
    assert issue.status_code == 200
    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200

    create_user = client.post(
        "/api/auth/register", data={"email": "test15@test.com", "password": "2£23AacD"}
    )
    assert create_user.status_code == 200

    login_request = client.post(
        "/api/auth/login", data={"email": "test15@test.com", "password": "2£23AacD"}
    )
    assert login_request.status_code == 200

    get_id = client.post("/api/auth/getid", data={"email": "test2@test.com"})
    assert get_id.status_code == 200
    user_id = get_id.content.decode().replace('"', "")
    response = client.get(f"/api/issues/{user_id}")
    assert response.status_code == 403
    response_data = response.json()
    assert response_data == {"detail": "User does not have necessary permission"}


def test_update_issue_title(test_db, login_user):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    issue_id = create_issue.json()
    updated_issue = client.patch(
        f"/api/issues/{issue_id}", data={"title": "updating title test"}
    )
    assert updated_issue.status_code == 200


def test_update_issue_wrong_type(test_db, login_user):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    issue_id = create_issue.json()
    updated_issue = client.patch(f"/api/issues/{issue_id}", data={"type": "wrong_type"})
    assert updated_issue.status_code == 422


def test_update_issue_all(test_db, login_user):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    issue_id = create_issue.json()
    updated_issue = client.patch(
        f"/api/issues/{issue_id}",
        data={
            "type": "Service request",
            "title": "updated title",
            "description": "updated description",
        },
    )
    assert updated_issue.status_code == 200


def test_update_issue_as_wrong_id(test_db, login_user):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    issue_id = create_issue.json()
    updated_issue = client.patch(
        f"/api/issues/1",
        data={
            "type": "Service request",
            "title": "updated title",
            "description": "updated description",
        },
    )
    assert updated_issue.status_code == 403


def test_update_issue_as_wrong_user(test_db, login_user):
    client.post(
        "/api/auth/register", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    login_request = client.post(
        "/api/auth/login", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    assert login_request.status_code == 200

    issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    issue_response = issue.json()
    issue_id = issue_response
    assert issue.status_code == 200
    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200

    create_user = client.post(
        "/api/auth/register", data={"email": "test15@test.com", "password": "2£23AacD"}
    )
    assert create_user.status_code == 200
    login_request = client.post(
        "/api/auth/login", data={"email": "test15@test.com", "password": "2£23AacD"}
    )
    assert login_request.status_code == 200
    updated_issue = client.patch(
        f"/api/issues/{issue_id}",
        data={
            "type": "Service request",
            "title": "updated title",
            "description": "updated description",
        },
    )
    assert updated_issue.status_code == 403


def test_update_issue_as_admin(test_db, login_user):
    client.post(
        "/api/auth/register", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    login_request = client.post(
        "/api/auth/login", data={"email": "test2@test.com", "password": "2£23AacD"}
    )
    assert login_request.status_code == 200

    issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    issue_response = issue.json()
    issue_id = issue_response
    assert issue.status_code == 200
    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200

    login_request = client.post(
        "/api/auth/login",
        data={"email": "admintest@test.com", "password": "test1A$c34"},
    )
    assert login_request.status_code == 200
    updated_issue = client.patch(
        f"/api/issues/{issue_id}",
        data={
            "type": "Service request",
            "title": "updated title",
            "description": "updated description",
        },
    )
    assert updated_issue.status_code == 200


def test_update_issue_empty(test_db, login_user):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    issue_id = create_issue.json()
    updated_issue = client.patch(f"/api/issues/{issue_id}", data={""})
    assert updated_issue.status_code == 422


def test_delete_issue_wrong_id(test_db, login_admin):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    issue_id = create_issue.json()
    updated_issue = client.delete(f"/api/issues/{issue_id}")
    assert updated_issue.status_code == 200


def test_delete_issue_as_admin(test_db, login_admin):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    updated_issue = client.delete(f"/api/issues/1")
    assert updated_issue.status_code == 404


def test_delete_issue_as_user(test_db, login_user):
    create_issue = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert create_issue.status_code == 200
    issue_id = create_issue.json()
    updated_issue = client.delete(f"/api/issues/{issue_id}")
    assert updated_issue.status_code == 403


def test_get_all_issues_as_user(test_db, login_user):
    get_id = client.post("/api/auth/getid", data={"email": "test2@test.com"})
    assert get_id.status_code == 200

    created_issue_1 = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
            "is_resolved": False,
        },
    )
    # assert created_issue_1.status_code == 200
    created_issue_2 = client.post(
        "/api/issues",
        data={
            "title": "test2 issue",
            "type": "Bug",
            "description": "really really good test issue",
            "is_resolved": False,
        },
    )
    assert created_issue_2.status_code == 200
    get_issues = client.get("/api/issues")
    assert get_issues.status_code == 403
    response_data = get_issues.json()
    assert response_data == {"detail": "User does not have necessary permission"}


def test_get_all_issues_as_admin(test_db, login_admin):
    get_id = client.post("/api/auth/getid", data={"email": "admintest@test.com"})
    assert get_id.status_code == 200

    created_issue_1 = client.post(
        "/api/issues",
        data={
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
        },
    )
    assert created_issue_1.status_code == 200
    created_issue_2 = client.post(
        "/api/issues",
        data={
            "title": "test2 issue",
            "type": "Bug",
            "description": "really really good test issue",
        },
    )
    assert created_issue_2.status_code == 200
    expected = [
        {
            "title": "test issue",
            "type": "Bug",
            "description": "really good test issue",
            "user_id": f"{get_id.json()}",
            "id": f"{created_issue_1.json()}",
            "is_resolved": False,
        },
        {
            "title": "test2 issue",
            "type": "Bug",
            "description": "really really good test issue",
            "user_id": f"{get_id.json()}",
            "id": f"{created_issue_2.json()}",
            "is_resolved": False,
        },
    ]

    get_issues = client.get("/api/issues")
    assert get_issues.status_code == 200
    issues = get_issues.json()
    assert issues[0]["id"] == created_issue_1.json()
    assert issues[1]["id"] == created_issue_2.json()
