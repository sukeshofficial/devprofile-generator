"""
DevProfile Resume & Portfolio Automator - Main FastAPI Application

This is the main entry point for the DevProfile backend API.
Provides endpoints for GitHub integration, AI-powered skill extraction,
resume generation, and portfolio creation.

Example usage:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routers
from app.api.auth import router as auth_router
from app.api.github_routes import router as github_router
from app.api.ai_routes import router as ai_router
from app.api.resume_routes import router as resume_router

# Create FastAPI application
app = FastAPI(
    title="DevProfile API",
    description="AI-powered resume and portfolio generator",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(github_router, prefix="/api/github", tags=["github"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(resume_router, prefix="/api/resume", tags=["resume"])

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Example:
        curl http://localhost:8000/health
    """
    return {"status": "ok", "message": "DevProfile backend running"}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "DevProfile Resume & Portfolio Automator API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)