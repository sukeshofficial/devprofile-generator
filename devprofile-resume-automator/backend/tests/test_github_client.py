"""
Tests for GitHub client service

Tests GitHub API integration, caching, and error handling
with mocked HTTP responses.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from app.services.github_client import GitHubClient

@pytest.fixture
def github_client():
    """Create GitHub client instance for testing"""
    return GitHubClient(token="test_token")

@pytest.mark.asyncio
async def test_get_user_profile_success(github_client):
    """Test successful user profile fetch"""
    mock_response = {
        "id": 12345,
        "login": "testuser",
        "name": "Test User",
        "email": "test@example.com",
        "avatar_url": "https://github.com/avatar.jpg"
    }
    
    with patch.object(github_client, '_make_request', return_value=mock_response):
        profile = await github_client.get_user_profile("testuser")
        
        assert profile["login"] == "testuser"
        assert profile["name"] == "Test User"
        assert profile["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_repos_success(github_client):
    """Test successful repository fetch"""
    mock_response = [
        {
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "description": "A test repository",
            "stargazers_count": 10,
            "forks_count": 5,
            "html_url": "https://github.com/testuser/test-repo"
        }
    ]
    
    with patch.object(github_client, '_make_request', return_value=mock_response):
        repos = await github_client.get_user_repos("testuser", limit=5)
        
        assert len(repos) == 1
        assert repos[0]["name"] == "test-repo"
        assert repos[0]["stargazers_count"] == 10

@pytest.mark.asyncio
async def test_get_repo_readme_success(github_client):
    """Test successful README fetch"""
    mock_response = {
        "content": "IyBUZXN0IFJFQURNRQ==",  # Base64 for "# Test README"
        "encoding": "base64"
    }
    
    with patch.object(github_client, '_make_request', return_value=mock_response):
        readme = await github_client.get_repo_readme("testuser", "test-repo")
        
        assert readme == "# Test README"

@pytest.mark.asyncio
async def test_get_repo_readme_not_found(github_client):
    """Test README fetch when file doesn't exist"""
    with patch.object(github_client, '_make_request', return_value={}):
        readme = await github_client.get_repo_readme("testuser", "test-repo")
        
        assert readme == ""

@pytest.mark.asyncio
async def test_get_repo_languages_success(github_client):
    """Test successful language statistics fetch"""
    mock_response = {
        "Python": 12345,
        "JavaScript": 6789,
        "HTML": 1234
    }
    
    with patch.object(github_client, '_make_request', return_value=mock_response):
        languages = await github_client.get_repo_languages("testuser", "test-repo")
        
        assert "Python" in languages
        assert "JavaScript" in languages
        assert languages["Python"] == 12345

@pytest.mark.asyncio
async def test_request_retry_logic(github_client):
    """Test retry logic for failed requests"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock client that fails twice then succeeds
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        
        mock_client.return_value.__aenter__.return_value.get.side_effect = [
            Exception("Network error"),
            Exception("Network error"),
            mock_response
        ]
        
        result = await github_client._make_request("https://api.github.com/test")
        assert result == {"success": True}

@pytest.mark.asyncio
async def test_rate_limit_handling(github_client):
    """Test rate limit handling"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock 429 response followed by success
        mock_429 = AsyncMock()
        mock_429.status_code = 429
        
        mock_200 = AsyncMock()
        mock_200.status_code = 200
        mock_200.json.return_value = {"success": True}
        
        mock_client.return_value.__aenter__.return_value.get.side_effect = [
            mock_429,
            mock_200
        ]
        
        with patch('asyncio.sleep'):  # Speed up test
            result = await github_client._make_request("https://api.github.com/test")
            assert result == {"success": True}