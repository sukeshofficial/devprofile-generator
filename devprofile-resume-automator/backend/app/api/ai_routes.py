"""
AI-powered analysis routes using OpenRouter

Provides endpoints for skill extraction, job matching, bullet generation,
and other AI-powered features using OpenRouter-compatible models.

Example usage:
    curl -X POST http://localhost:8000/api/ai/extract-skills
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.services.openrouter_client import OpenRouterClient
from app.utils.prompts import (
    SKILL_EXTRACTION_PROMPT,
    JOB_MATCH_PROMPT,
    GENERATE_BULLETS_PROMPT,
    LINKEDIN_PROMPT,
    INTERVIEW_PROMPT
)

router = APIRouter()

# Request/Response Models
class SkillExtractionRequest(BaseModel):
    repos: List[Dict[str, Any]]

class SkillExtractionResponse(BaseModel):
    repo: str
    languages: List[str]
    skills: List[str]
    tools: List[str]
    methods: List[str]
    outcomes: List[str]
    evidence: List[str]

class JobMatchRequest(BaseModel):
    skills: List[str]
    job_text: str

class JobMatchResponse(BaseModel):
    role: str
    score: int
    matches: List[Dict[str, str]]
    gaps: List[Dict[str, str]]
    recommendations: List[str]

class BulletGenerationRequest(BaseModel):
    projects: List[Dict[str, Any]]
    context: Dict[str, Any]

class BulletResponse(BaseModel):
    bullets: List[Dict[str, str]]

class LinkedInRequest(BaseModel):
    profile: Dict[str, Any]
    role: str

class InterviewRequest(BaseModel):
    role: str

@router.post("/extract-skills")
async def extract_skills(request: SkillExtractionRequest) -> List[SkillExtractionResponse]:
    """
    Extract skills from GitHub repositories using AI
    
    Example:
        curl -X POST http://localhost:8000/api/ai/extract-skills \
             -H "Content-Type: application/json" \
             -d '{"repos": [{"name": "my-repo", "readme": "Built with React..."}]}'
    """
    try:
        openrouter = OpenRouterClient()
        results = []
        
        for repo in request.repos:
            # Prepare context for AI
            context = {
                "repo_name": repo.get("name", ""),
                "description": repo.get("description", ""),
                "readme": repo.get("readme", ""),
                "languages": repo.get("languages", []),
                "stars": repo.get("stars", 0),
                "forks": repo.get("forks", 0)
            }
            
            # Call OpenRouter for skill extraction
            response = await openrouter.extract_skills(context)
            
            # Validate response matches schema
            skill_data = SkillExtractionResponse(
                repo=repo.get("name", ""),
                languages=response.get("languages", []),
                skills=response.get("skills", []),
                tools=response.get("tools", []),
                methods=response.get("methods", []),
                outcomes=response.get("outcomes", []),
                evidence=response.get("evidence", [])
            )
            
            results.append(skill_data)
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Skill extraction failed: {str(e)}"
        )

@router.post("/job-match")
async def job_match(request: JobMatchRequest) -> JobMatchResponse:
    """
    Match user skills against job description
    
    Example:
        curl -X POST http://localhost:8000/api/ai/job-match \
             -H "Content-Type: application/json" \
             -d '{"skills": ["Python", "React"], "job_text": "Looking for Python developer..."}'
    """
    try:
        openrouter = OpenRouterClient()
        
        context = {
            "candidate_skills": request.skills,
            "job_description": request.job_text
        }
        
        response = await openrouter.match_job(context)
        
        return JobMatchResponse(
            role=response.get("role", ""),
            score=response.get("score", 0),
            matches=response.get("matches", []),
            gaps=response.get("gaps", []),
            recommendations=response.get("recommendations", [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Job matching failed: {str(e)}"
        )

@router.post("/generate-bullets")
async def generate_bullets(request: BulletGenerationRequest) -> BulletResponse:
    """
    Generate STAR-format resume bullets from projects
    
    Example:
        curl -X POST http://localhost:8000/api/ai/generate-bullets \
             -H "Content-Type: application/json" \
             -d '{"projects": [...], "context": {...}}'
    """
    try:
        openrouter = OpenRouterClient()
        
        context = {
            "projects": request.projects,
            "user_context": request.context
        }
        
        response = await openrouter.generate_bullets(context)
        
        return BulletResponse(
            bullets=response.get("bullets", [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Bullet generation failed: {str(e)}"
        )

@router.post("/linkedin")
async def linkedin_optimization(request: LinkedInRequest):
    """
    Generate LinkedIn headline and summary suggestions
    
    Example:
        curl -X POST http://localhost:8000/api/ai/linkedin \
             -H "Content-Type: application/json" \
             -d '{"profile": {...}, "role": "Software Engineer"}'
    """
    try:
        openrouter = OpenRouterClient()
        
        context = {
            "profile": request.profile,
            "target_role": request.role
        }
        
        response = await openrouter.optimize_linkedin(context)
        
        return {
            "headlines": response.get("headlines", []),
            "summary_lines": response.get("summary_lines", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LinkedIn optimization failed: {str(e)}"
        )

@router.post("/interview")
async def generate_interview_questions(request: InterviewRequest):
    """
    Generate role-specific interview questions
    
    Example:
        curl -X POST http://localhost:8000/api/ai/interview \
             -H "Content-Type: application/json" \
             -d '{"role": "Backend Engineer"}'
    """
    try:
        openrouter = OpenRouterClient()
        
        context = {
            "role": request.role
        }
        
        response = await openrouter.generate_interview_questions(context)
        
        return {
            "questions": response.get("questions", [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Interview question generation failed: {str(e)}"
        )