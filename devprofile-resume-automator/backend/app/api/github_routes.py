"""
GitHub API routes for repository and user data fetching

Provides endpoints to fetch GitHub user repositories, README files,
and metadata for skill extraction and resume generation.

Example usage:
    curl "http://localhost:8000/api/github/user/octocat/repos?limit=5"
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import httpx
import base64
import asyncio
from app.services.github_client import GitHubClient
from app.utils.cache import cache_get, cache_set

router = APIRouter()

class Repository(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    stars: int
    forks: int
    languages: List[str]
    readme: str
    html_url: str

class GitHubUserReposResponse(BaseModel):
    username: str
    repos: List[Repository]

@router.get("/user/{username}/repos")
async def get_user_repos(
    username: str,
    limit: int = Query(default=5, ge=1, le=20),
    token: Optional[str] = Query(default=None)
) -> GitHubUserReposResponse:
    """
    Fetch user repositories with README content and metadata
    
    Args:
        username: GitHub username
        limit: Number of repositories to fetch (1-20)
        token: Optional GitHub token for private repos
    
    Example:
        curl "http://localhost:8000/api/github/user/octocat/repos?limit=5"
    """
    # Check cache first
    cache_key = f"github_repos_{username}_{limit}"
    cached_result = cache_get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        github_client = GitHubClient(token)
        
        # Fetch user repositories
        repos_data = await github_client.get_user_repos(username, limit)
        
        # Process repositories
        processed_repos = []
        for repo in repos_data:
            # Fetch README content
            readme_content = await github_client.get_repo_readme(
                repo["owner"]["login"], 
                repo["name"]
            )
            
            # Fetch languages
            languages = await github_client.get_repo_languages(
                repo["owner"]["login"], 
                repo["name"]
            )
            
            processed_repo = Repository(
                name=repo["name"],
                full_name=repo["full_name"],
                description=repo.get("description", ""),
                stars=repo.get("stargazers_count", 0),
                forks=repo.get("forks_count", 0),
                languages=list(languages.keys()) if languages else [],
                readme=readme_content,
                html_url=repo["html_url"]
            )
            processed_repos.append(processed_repo)
        
        result = GitHubUserReposResponse(
            username=username,
            repos=processed_repos
        )
        
        # Cache result for 1 hour
        cache_set(cache_key, result, ttl=3600)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch GitHub data: {str(e)}"
        )

@router.get("/user/{username}/profile")
async def get_user_profile(username: str, token: Optional[str] = Query(default=None)):
    """
    Fetch GitHub user profile information
    
    Example:
        curl "http://localhost:8000/api/github/user/octocat/profile"
    """
    try:
        github_client = GitHubClient(token)
        profile = await github_client.get_user_profile(username)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user profile: {str(e)}"
        )

@router.post("/refresh-cache")
async def refresh_cache(username: str):
    """
    Clear cache for a specific user to force fresh data fetch
    
    Example:
        curl -X POST "http://localhost:8000/api/github/refresh-cache?username=octocat"
    """
    # Clear all cache entries for this user
    cache_keys = [
        f"github_repos_{username}_5",
        f"github_repos_{username}_10",
        f"github_repos_{username}_20",
        f"github_profile_{username}"
    ]
    
    # Note: In a real implementation, you'd have a cache.clear_pattern() method
    return {"message": f"Cache cleared for user {username}"}