"""
Tests for OpenRouter client service

Tests AI integration, prompt handling, and JSON validation
with mocked API responses.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from app.services.openrouter_client import OpenRouterClient

@pytest.fixture
def openrouter_client():
    """Create OpenRouter client instance for testing"""
    return OpenRouterClient()

@pytest.mark.asyncio
async def test_extract_skills_success(openrouter_client):
    """Test successful skill extraction"""
    mock_response = {
        "repo": "test-repo",
        "languages": ["Python", "JavaScript"],
        "skills": ["FastAPI", "React"],
        "tools": ["Git", "Docker"],
        "methods": ["REST API", "Testing"],
        "outcomes": ["Improved performance", "Reduced bugs"],
        "evidence": ["Built with FastAPI", "Uses React hooks"]
    }
    
    with patch.object(openrouter_client, '_make_request', return_value=mock_response):
        repo_context = {
            "repo_name": "test-repo",
            "description": "A test repository",
            "readme": "# Test\nBuilt with FastAPI and React",
            "languages": ["Python", "JavaScript"]
        }
        
        result = await openrouter_client.extract_skills(repo_context)
        
        assert result["repo"] == "test-repo"
        assert "Python" in result["languages"]
        assert "FastAPI" in result["skills"]

@pytest.mark.asyncio
async def test_match_job_success(openrouter_client):
    """Test successful job matching"""
    mock_response = {
        "role": "Backend Developer",
        "score": 85,
        "matches": [
            {"skill": "Python", "evidence": "Listed in job requirements"},
            {"skill": "FastAPI", "evidence": "Mentioned as preferred framework"}
        ],
        "gaps": [
            {"skill": "Kubernetes", "priority": "medium"}
        ],
        "recommendations": ["Learn container orchestration", "Practice system design"]
    }
    
    with patch.object(openrouter_client, '_make_request', return_value=mock_response):
        context = {
            "candidate_skills": ["Python", "FastAPI", "React"],
            "job_description": "Looking for Backend Developer with Python and FastAPI experience"
        }
        
        result = await openrouter_client.match_job(context)
        
        assert result["role"] == "Backend Developer"
        assert result["score"] == 85
        assert len(result["matches"]) == 2
        assert len(result["gaps"]) == 1

@pytest.mark.asyncio
async def test_generate_bullets_success(openrouter_client):
    """Test successful bullet generation"""
    mock_response = {
        "bullets": [
            {
                "project": "E-commerce API",
                "text": "Developed REST API using FastAPI that handles 1000+ requests/minute",
                "action": "Developed",
                "tool": "FastAPI",
                "result": "1000+ requests/minute",
                "tags": ["backend", "api", "performance"]
            },
            {
                "project": "React Dashboard",
                "text": "Built responsive dashboard with React reducing load time by 40%",
                "action": "Built",
                "tool": "React",
                "result": "40% faster load time",
                "tags": ["frontend", "react", "performance"]
            }
        ]
    }
    
    with patch.object(openrouter_client, '_make_request', return_value=mock_response):
        context = {
            "projects": [
                {"name": "E-commerce API", "description": "REST API for online store"},
                {"name": "React Dashboard", "description": "Admin dashboard"}
            ],
            "user_context": {"role": "Full Stack Developer"}
        }
        
        result = await openrouter_client.generate_bullets(context)
        
        assert len(result["bullets"]) == 2
        assert result["bullets"][0]["project"] == "E-commerce API"
        assert "FastAPI" in result["bullets"][0]["tool"]

@pytest.mark.asyncio
async def test_json_validation_error(openrouter_client):
    """Test handling of invalid JSON responses"""
    with patch.object(openrouter_client, '_make_request') as mock_request:
        # Mock invalid JSON response
        mock_request.side_effect = Exception("Invalid JSON response from AI")
        
        with pytest.raises(Exception) as exc_info:
            await openrouter_client.extract_skills({})
        
        assert "Invalid JSON response" in str(exc_info.value)

@pytest.mark.asyncio
async def test_api_timeout_handling(openrouter_client):
    """Test API timeout handling"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("OpenRouter API error: timeout")
        
        with pytest.raises(Exception) as exc_info:
            await openrouter_client.extract_skills({})
        
        assert "OpenRouter API error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_optimize_linkedin_success(openrouter_client):
    """Test LinkedIn optimization"""
    mock_response = {
        "headlines": [
            "Full Stack Developer | Python & React Expert",
            "Backend Engineer | API & Database Specialist",
            "Software Developer | Building Scalable Web Applications"
        ],
        "summary_lines": [
            "Experienced developer with 5+ years in web development",
            "Passionate about clean code and scalable architecture",
            "Open source contributor and continuous learner"
        ]
    }
    
    with patch.object(openrouter_client, '_make_request', return_value=mock_response):
        context = {
            "profile": {"name": "Test User", "skills": ["Python", "React"]},
            "target_role": "Full Stack Developer"
        }
        
        result = await openrouter_client.optimize_linkedin(context)
        
        assert len(result["headlines"]) == 3
        assert len(result["summary_lines"]) == 3
        assert "Full Stack Developer" in result["headlines"][0]