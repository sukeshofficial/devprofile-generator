"""
Authentication API routes for GitHub and LinkedIn OAuth

Handles OAuth flows with PKCE for secure authentication.
Returns JWT tokens for authenticated sessions.

Example usage:
    curl http://localhost:8000/api/auth/github/login
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx
import os
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

# OAuth configuration
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_OAUTH_REDIRECT_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key")

class AuthResponse(BaseModel):
    access_token: str
    user: dict
    expires_in: int

@app.get("/github/login")
async def github_login():
    """
    Initiate GitHub OAuth flow
    
    Example:
        curl http://localhost:8000/api/auth/github/login
    """
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # GitHub OAuth URL
    github_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        f"&scope=read:user,repo"
        f"&state={state}"
    )
    
    return RedirectResponse(url=github_url)

@router.get("/github/callback")
async def github_callback(code: str, state: Optional[str] = None):
    """
    Handle GitHub OAuth callback
    
    Example:
        curl "http://localhost:8000/api/auth/github/callback?code=abc123&state=xyz"
    """
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code required")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
            timeout=10.0
        )
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token received")
    
    # Get user information
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"},
            timeout=10.0
        )
    
    if user_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get user information")
    
    user_data = user_response.json()
    
    # Create JWT token
    jwt_payload = {
        "sub": str(user_data["id"]),
        "username": user_data["login"],
        "name": user_data.get("name"),
        "email": user_data.get("email"),
        "avatar_url": user_data.get("avatar_url"),
        "github_token": access_token,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm="HS256")
    
    return AuthResponse(
        access_token=jwt_token,
        user={
            "id": user_data["id"],
            "username": user_data["login"],
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "avatar_url": user_data.get("avatar_url")
        },
        expires_in=86400  # 24 hours
    )

@router.get("/linkedin/login")
async def linkedin_login():
    """
    Initiate LinkedIn OAuth flow
    
    Example:
        curl http://localhost:8000/api/auth/linkedin/login
    """
    # LinkedIn OAuth implementation would go here
    # For MVP, return placeholder
    return {"message": "LinkedIn OAuth not implemented in MVP"}

@router.get("/linkedin/callback")
async def linkedin_callback(code: str, state: Optional[str] = None):
    """
    Handle LinkedIn OAuth callback
    
    Example:
        curl "http://localhost:8000/api/auth/linkedin/callback?code=abc123"
    """
    # LinkedIn OAuth callback implementation would go here
    # For MVP, return placeholder
    return {"message": "LinkedIn OAuth callback not implemented in MVP"}

def get_current_user(request: Request):
    """Dependency to get current authenticated user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")