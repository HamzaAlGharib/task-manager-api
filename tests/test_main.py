import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.database.database import get_db
from src.database.models import Base
from src.main import app

# Load environment variables
load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not configured")

# Setup test database engine and session
test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture
def client():
    # 1. Create database tables
    Base.metadata.create_all(bind=test_engine)

    # 2. Clean up data from previous test runs
    with TestingSessionLocal() as db:
        db.execute(text("DELETE FROM refresh_tokens"))
        db.execute(text("DELETE FROM tasks"))
        db.execute(text("DELETE FROM users"))
        db.commit()

    # 3. Define dependency override
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # 4. Yield the client to the tests
    with TestClient(app) as test_client:
        yield test_client

    # 5. Teardown: clear overrides after the test finishes
    app.dependency_overrides.clear()


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Task Manager API is running"}


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    assert "id" in response.json()


def test_register_duplicate_email(client):
    user = {
        "email": "duplicate@example.com",
        "password": "StrongPass123!",
    }

    first_response = client.post("/auth/register", json=user)
    second_response = client.post("/auth/register", json=user)

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


def test_login_success(client):
    client.post(
        "/auth/register",
        json={
            "email": "Hamza@example.com",
            "password": "StrongPass123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "Hamza@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "StrongPass123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_create_task(client):
    client.post(
        "/auth/register",
        json={
            "email": "taskuser@example.com",
            "password": "StrongPass123!",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "taskuser@example.com",
            "password": "StrongPass123!",
        },
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "title": "Learn pytest",
            "description": "Test task creation",
            "completed": False,
            "priority": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Learn pytest"
    assert response.json()["priority"] == 1
    assert "id" in response.json()


def test_get_tasks_requires_authentication(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_user_cannot_access_another_users_task(client):
    # Register two users.
    client.post(
        "/auth/register",
        json={
            "email": "owner@example.com",
            "password": "StrongPass123!",
        },
    )

    client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "StrongPass123!",
        },
    )

    # Log in as User A.
    owner_login = client.post(
        "/auth/login",
        json={
            "email": "owner@example.com",
            "password": "StrongPass123!",
        },
    )

    owner_token = owner_login.json()["access_token"]

    # User A creates a task.
    task_response = client.post(
        "/tasks",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={
            "title": "Private task",
            "description": "Only the owner should access this",
            "completed": False,
            "priority": 1,
        },
    )

    assert task_response.status_code == 200
    task_id = task_response.json()["id"]

    # Log in as User B.
    other_login = client.post(
        "/auth/login",
        json={
            "email": "other@example.com",
            "password": "StrongPass123!",
        },
    )

    other_token = other_login.json()["access_token"]

    # User B attempts to access User A's task.
    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"
