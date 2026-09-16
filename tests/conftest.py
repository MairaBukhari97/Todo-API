import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db

# Separate in-memory database just for tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Overriding the real DB with test DB
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # Create a fresh test database
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    return TestClient(app)

@pytest.fixture
def registered_user(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpass123"
    })
    return {"username": "testuser", "password": "testpass123"}

@pytest.fixture
def auth_token(client, registered_user):
    response = client.post("/auth/login", data={
        "username": registered_user["username"],
        "password": registered_user["password"]
    })
    return response.json()["access_token"]