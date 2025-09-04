"""
Pytest configuration and shared fixtures

Provides common test fixtures and configuration for the test suite.
"""

import pytest
import os
from unittest.mock import patch

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_ANON_KEY": "test_anon_key",
        "OPENROUTER_API_KEY": "test_openrouter_key",
        "GITHUB_CLIENT_ID": "test_github_id",
        "GITHUB_CLIENT_SECRET": "test_github_secret",
        "JWT_SECRET": "test_jwt_secret"
    }
    
    with patch.dict(os.environ, test_env):
        yield

@pytest.fixture
def mock_github_response():
    """Mock GitHub API response data"""
    return {
        "user": {
            "id": 12345,
            "login": "testuser",
            "name": "Test User",
            "email": "test@example.com",
            "avatar_url": "https://github.com/avatar.jpg"
        },
        "repos": [
            {
                "name": "test-repo",
                "full_name": "testuser/test-repo",
                "description": "A test repository",
                "stargazers_count": 10,
                "forks_count": 5,
                "html_url": "https://github.com/testuser/test-repo",
                "owner": {"login": "testuser"}
            }
        ],
        "readme": {
            "content": "IyBUZXN0IFJFQURNRQ==",  # "# Test README"
            "encoding": "base64"
        },
        "languages": {
            "Python": 12345,
            "JavaScript": 6789
        }
    }

@pytest.fixture
def mock_openrouter_response():
    """Mock OpenRouter API response data"""
    return {
        "skill_extraction": {
            "repo": "test-repo",
            "languages": ["Python", "JavaScript"],
            "skills": ["FastAPI", "React"],
            "tools": ["Git", "Docker"],
            "methods": ["REST API", "Testing"],
            "outcomes": ["Improved performance"],
            "evidence": ["Built with FastAPI"]
        },
        "job_match": {
            "role": "Backend Developer",
            "score": 85,
            "matches": [{"skill": "Python", "evidence": "Required skill"}],
            "gaps": [{"skill": "Kubernetes", "priority": "medium"}],
            "recommendations": ["Learn container orchestration"]
        },
        "bullets": {
            "bullets": [
                {
                    "project": "Test Project",
                    "text": "Developed API with FastAPI",
                    "action": "Developed",
                    "tool": "FastAPI",
                    "result": "Improved performance",
                    "tags": ["backend", "api"]
                }
            ]
        }
    }