"""
GitHub API client with caching and error handling

Provides methods to fetch GitHub user data, repositories, README files,
and language statistics with proper error handling and caching.
"""

import httpx
import base64
import asyncio
from typing import Optional, Dict, List, Any
from app.utils.cache import cache_get, cache_set

class GitHubClient:
    """GitHub API client with authentication and caching support"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DevProfile/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    async def _make_request(self, url: str, retries: int = 3) -> Dict[str, Any]:
        """Make HTTP request with exponential backoff retry logic"""
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url, 
                        headers=self.headers, 
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 429:
                        # Rate limited - wait and retry
                        wait_time = 2 ** attempt
                        await asyncio.sleep(wait_time)
                        continue
                    elif response.status_code == 404:
                        return {}
                    else:
                        response.raise_for_status()
                        
            except httpx.TimeoutException:
                if attempt == retries - 1:
                    raise Exception("GitHub API timeout")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == retries - 1:
                    raise Exception(f"GitHub API error: {str(e)}")
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    async def get_user_profile(self, username: str) -> Dict[str, Any]:
        """
        Fetch GitHub user profile information
        
        Args:
            username: GitHub username
            
        Returns:
            User profile data
        """
        cache_key = f"github_profile_{username}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/users/{username}"
        profile = await self._make_request(url)
        
        cache_set(cache_key, profile, ttl=3600)  # Cache for 1 hour
        return profile
    
    async def get_user_repos(self, username: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch user repositories sorted by stars
        
        Args:
            username: GitHub username
            limit: Number of repositories to fetch
            
        Returns:
            List of repository data
        """
        cache_key = f"github_repos_{username}_{limit}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/users/{username}/repos"
        params = {
            "sort": "stars",
            "direction": "desc",
            "per_page": limit
        }
        
        # Add query parameters to URL
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"
        
        repos = await self._make_request(full_url)
        
        cache_set(cache_key, repos, ttl=3600)  # Cache for 1 hour
        return repos if isinstance(repos, list) else []
    
    async def get_repo_readme(self, owner: str, repo: str) -> str:
        """
        Fetch repository README content
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content as string
        """
        cache_key = f"github_readme_{owner}_{repo}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"
        
        try:
            response = await self._make_request(url)
            
            if not response or "content" not in response:
                return ""
            
            # Decode base64 content
            content = response["content"]
            encoding = response.get("encoding", "base64")
            
            if encoding == "base64":
                decoded = base64.b64decode(content).decode("utf-8")
                cache_set(cache_key, decoded, ttl=3600)
                return decoded
            else:
                cache_set(cache_key, content, ttl=3600)
                return content
                
        except Exception:
            return ""
    
    async def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        Fetch repository language statistics
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary of languages and their byte counts
        """
        cache_key = f"github_languages_{owner}_{repo}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        try:
            languages = await self._make_request(url)
            cache_set(cache_key, languages, ttl=3600)
            return languages if isinstance(languages, dict) else {}
        except Exception:
            return {}
    
    async def get_repo_commits(self, owner: str, repo: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch recent repository commits
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Number of commits to fetch
            
        Returns:
            List of commit data
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"
        
        try:
            commits = await self._make_request(full_url)
            return commits if isinstance(commits, list) else []
        except Exception:
            return []