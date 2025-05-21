import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import create_access_token
from app.models.user import User
from app.core.database import Base
from app.schemas.auth import UserCreate

def test_auth_001_register_new_user(client: TestClient, db: Session):
    """
    AUTH 001: Test user registration with valid data
    """
    print(f"User model in test: {User}")
    print(f"User MRO: {User.__mro__}")
    print(f"Base in test: {Base}")
    # Test data
    user_data = {
        "email": "test@example.com",
        "password": "Test123!@#",
        "full_name": "Test User"
    }
    
    # Make registration request
    response = client.post("/api/auth/register", json=user_data)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "password" not in data  # Ensure password is not returned
    
    # Verify user was created in database
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.full_name == user_data["full_name"] 