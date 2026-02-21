import httpx
from typing import Optional, Dict, Any
from config import settings
from models import GitHubProfile, Repository
import json

class GitHubOAuth:
    def __init__(self):
        self.client_id = settings.GITHUB_CLIENT_ID
        self.client_secret = settings.GITHUB_CLIENT_SECRET
        self.redirect_uri = "http://localhost:8000/api/auth/github/callback"
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate GitHub OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email,read:user,repo",
            "state": state or "random_state"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://github.com/login/oauth/authorize?{query_string}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    },
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("access_token")
                return None
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    async def get_user_profile(self, access_token: str) -> Optional[GitHubProfile]:
        """Get GitHub user profile using access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return GitHubProfile(
                        login=data["login"],
                        name=data.get("name"),
                        bio=data.get("bio"),
                        avatar_url=data["avatar_url"],
                        public_repos=data["public_repos"],
                        followers=data["followers"],
                        following=data["following"],
                        location=data.get("location"),
                        company=data.get("company"),
                        blog=data.get("blog"),
                        twitter_username=data.get("twitter_username")
                    )
                return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    async def get_user_repositories(self, access_token: str, username: str) -> list[Repository]:
        """Get user repositories using access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/users/{username}/repos",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    params={"sort": "updated", "per_page": 100}
                )
                
                if response.status_code == 200:
                    repos_data = response.json()
                    repositories = []
                    
                    for repo in repos_data:
                        repositories.append(Repository(
                            name=repo["name"],
                            description=repo.get("description"),
                            language=repo.get("language"),
                            stargazers_count=repo["stargazers_count"],
                            forks_count=repo["forks_count"],
                            created_at=repo["created_at"],
                            updated_at=repo["updated_at"],
                            html_url=repo["html_url"],
                            clone_url=repo["clone_url"],
                            topics=repo.get("topics", [])
                        ))
                    
                    return repositories
                return []
        except Exception as e:
            print(f"Error getting user repositories: {e}")
            return []
    
    async def get_repository_readme(self, access_token: str, username: str, repo_name: str) -> Optional[str]:
        """Get repository README content"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.github.com/repos/{username}/{repo_name}/readme",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", "")
                    encoding = data.get("encoding", "base64")
                    
                    if encoding == "base64":
                        import base64
                        try:
                            return base64.b64decode(content).decode("utf-8")
                        except (base64.binascii.Error, UnicodeDecodeError):
                            return None
                    else:
                        return content
                return None
        except Exception as e:
            print(f"Error getting repository README: {e}")
            return None

# Global instance
github_oauth = GitHubOAuth()
