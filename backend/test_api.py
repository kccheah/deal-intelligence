"""
Unit Tests for FastAPI Backend
Run with: pytest test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

# Import your app and models
from main import app, get_db
from models import Base, User, Deal, Property

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ============================================================================
# HEALTH CHECK TESTS
# ============================================================================

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_signup_success():
    """Test user signup"""
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
            "company_name": "Test Corp"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_signup_duplicate_email():
    """Test signup with duplicate email"""
    # First signup
    client.post(
        "/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "pass123",
            "first_name": "John",
            "last_name": "Doe"
        }
    )

    # Second signup with same email
    response = client.post(
        "/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "pass123",
            "first_name": "Jane",
            "last_name": "Doe"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success():
    """Test user login"""
    # Create user
    client.post(
        "/auth/signup",
        json={
            "email": "login@example.com",
            "password": "testpass",
            "first_name": "John",
            "last_name": "Doe"
        }
    )

    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpass"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    """Test login with wrong password"""
    # Create user
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "password": "correct",
            "first_name": "John",
            "last_name": "Doe"
        }
    )

    # Try wrong password
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong"
        }
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

# ============================================================================
# DEALS ENDPOINT TESTS
# ============================================================================

def test_list_deals_empty():
    """Test listing deals when none exist"""
    response = client.get("/deals")
    assert response.status_code == 200
    assert response.json() == []

def test_list_deals_with_filters():
    """Test listing deals with filters"""
    response = client.get("/deals?limit=10&min_score=50")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_deal_not_found():
    """Test getting non-existent deal"""
    response = client.get("/deals/nonexistent")
    assert response.status_code == 404

# ============================================================================
# PROPERTIES ENDPOINT TESTS
# ============================================================================

def test_list_properties_empty():
    """Test listing properties when none exist"""
    response = client.get("/properties")
    assert response.status_code == 200
    assert response.json() == []

def test_list_properties_with_filters():
    """Test listing properties with filters"""
    response = client.get("/properties?country=AE&min_score=50")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ============================================================================
# ALERTS TESTS
# ============================================================================

def test_create_alert_unauthorized():
    """Test creating alert without authentication"""
    response = client.post(
        "/alerts",
        json={
            "alert_name": "Test Alert",
            "alert_type": "deal",
            "criteria": {"sectors": ["tech"]},
            "frequency": "daily"
        }
    )
    # Should fail without token (implementation dependent)
    assert response.status_code in [401, 422]

# ============================================================================
# USER PROFILE TESTS
# ============================================================================

def test_get_profile_unauthorized():
    """Test getting profile without auth"""
    response = client.get("/user/profile")
    assert response.status_code == 401

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_user_flow():
    """Test complete user flow: signup -> login -> view data"""
    # 1. Signup
    signup_response = client.post(
        "/auth/signup",
        json={
            "email": "flow@example.com",
            "password": "flow123",
            "first_name": "Flow",
            "last_name": "Test"
        }
    )
    assert signup_response.status_code == 200
    token = signup_response.json()["access_token"]

    # 2. Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "flow@example.com",
            "password": "flow123"
        }
    )
    assert login_response.status_code == 200

    # 3. View deals
    deals_response = client.get(
        "/deals",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert deals_response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
