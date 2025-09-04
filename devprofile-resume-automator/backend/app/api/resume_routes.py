"""
Resume generation and export routes

Handles PDF generation, JSON export, sharing functionality,
and public resume rendering.

Example usage:
    curl -X POST http://localhost:8000/api/resume/pdf
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import os
from app.services.pdf_generator import PDFGenerator
from app.services.portfolio_generator import PortfolioGenerator
from app.utils.cache import cache_set, cache_get

router = APIRouter()

class ResumeProfile(BaseModel):
    name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    github_url: Optional[str]
    linkedin_url: Optional[str]
    summary: str

class ResumeBullet(BaseModel):
    project: str
    text: str
    action: str
    tool: str
    result: str
    tags: List[str]

class ResumeRequest(BaseModel):
    profile: ResumeProfile
    bullets: List[ResumeBullet]
    skills: List[str]

class ShareResponse(BaseModel):
    slug: str
    url: str

@router.post("/pdf")
async def generate_pdf(request: ResumeRequest, background_tasks: BackgroundTasks):
    """
    Generate ATS-friendly PDF resume
    
    Example:
        curl -X POST http://localhost:8000/api/resume/pdf \
             -H "Content-Type: application/json" \
             -d '{"profile": {...}, "bullets": [...]}' \
             --output resume.pdf
    """
    try:
        pdf_generator = PDFGenerator()
        
        # Generate PDF in background
        pdf_path = await pdf_generator.generate_resume_pdf(
            profile=request.profile.dict(),
            bullets=[bullet.dict() for bullet in request.bullets],
            skills=request.skills
        )
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"{request.profile.name.replace(' ', '_')}_resume.pdf"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

@router.post("/json")
async def generate_json_resume(request: ResumeRequest):
    """
    Generate JSON Resume format
    
    Example:
        curl -X POST http://localhost:8000/api/resume/json \
             -H "Content-Type: application/json" \
             -d '{"profile": {...}, "bullets": [...]}'
    """
    try:
        # Convert to JSON Resume schema
        json_resume = {
            "basics": {
                "name": request.profile.name,
                "email": request.profile.email,
                "phone": request.profile.phone,
                "location": {"address": request.profile.location},
                "url": request.profile.github_url,
                "summary": request.profile.summary,
                "profiles": [
                    {
                        "network": "GitHub",
                        "username": request.profile.github_url.split("/")[-1] if request.profile.github_url else "",
                        "url": request.profile.github_url
                    }
                ]
            },
            "work": [
                {
                    "name": bullet.project,
                    "position": "Developer",
                    "summary": bullet.text,
                    "highlights": [bullet.result]
                }
                for bullet in request.bullets
            ],
            "skills": [
                {
                    "name": "Technical Skills",
                    "keywords": request.skills
                }
            ]
        }
        
        return json_resume
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"JSON resume generation failed: {str(e)}"
        )

@router.post("/share")
async def share_resume(request: ResumeRequest) -> ShareResponse:
    """
    Create shareable public resume link
    
    Example:
        curl -X POST http://localhost:8000/api/resume/share \
             -H "Content-Type: application/json" \
             -d '{"profile": {...}, "bullets": [...]}'
    """
    try:
        # Generate unique slug
        slug = str(uuid.uuid4())[:8]
        
        # Generate HTML resume
        pdf_generator = PDFGenerator()
        html_content = await pdf_generator.generate_resume_html(
            profile=request.profile.dict(),
            bullets=[bullet.dict() for bullet in request.bullets],
            skills=request.skills
        )
        
        # Cache the HTML content
        cache_key = f"shared_resume_{slug}"
        cache_set(cache_key, html_content, ttl=86400 * 30)  # 30 days
        
        # In production, save to database
        # For MVP, use cache
        
        return ShareResponse(
            slug=slug,
            url=f"http://localhost:8000/r/{slug}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume sharing failed: {str(e)}"
        )

@router.get("/r/{slug}")
async def view_shared_resume(slug: str):
    """
    View public shared resume
    
    Example:
        curl http://localhost:8000/r/abc12345
    """
    try:
        cache_key = f"shared_resume_{slug}"
        html_content = cache_get(cache_key)
        
        if not html_content:
            raise HTTPException(status_code=404, detail="Resume not found or expired")
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load shared resume: {str(e)}"
        )

@router.post("/portfolio/generate")
async def generate_portfolio(profile: Dict[str, Any]):
    """
    Generate Next.js portfolio zip file
    
    Example:
        curl -X POST http://localhost:8000/api/portfolio/generate \
             -H "Content-Type: application/json" \
             -d '{"profile": {...}}'
    """
    try:
        portfolio_generator = PortfolioGenerator()
        zip_path = await portfolio_generator.generate_portfolio_zip(profile)
        
        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"{profile.get('name', 'portfolio').replace(' ', '_')}_portfolio.zip"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio generation failed: {str(e)}"
        )