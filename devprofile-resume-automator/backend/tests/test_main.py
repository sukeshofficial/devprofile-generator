"""
Tests for main FastAPI application

Tests application startup, health check, and basic routing
functionality.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    assert "DevProfile backend running" in data["message"]

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "DevProfile Resume & Portfolio Automator API" in data["message"]
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/docs"

def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/health")
    assert response.status_code == 200

def test_api_docs_available():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema():
    """Test OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    schema = response.json()
    assert schema["info"]["title"] == "DevProfile API"
    assert schema["info"]["version"] == "1.0.0"

def test_invalid_endpoint():
    """Test 404 for invalid endpoints"""
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_github_routes_included():
    """Test that GitHub routes are properly included"""
    response = client.get("/api/github/user/testuser/repos")
    # Should return error but route should exist (not 404)
    assert response.status_code != 404

@pytest.mark.asyncio
async def test_ai_routes_included():
    """Test that AI routes are properly included"""
    response = client.post("/api/ai/extract-skills", json={"repos": []})
    # Should return error but route should exist (not 404)
    assert response.status_code != 404