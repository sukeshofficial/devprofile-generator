from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    github_username: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class AnalysisBase(BaseModel):
    user_id: str
    github_username: str
    selected_repos: List[str]
    extracted_skills: List[str]
    job_matches: List[Dict[str, Any]]
    skill_suggestions: List[Dict[str, Any]]

class AnalysisCreate(AnalysisBase):
    pass

class Analysis(AnalysisBase):
    id: str
    created_at: datetime
    updated_at: datetime
    is_public: bool = False
    public_link: Optional[str] = None

class PortfolioExport(BaseModel):
    user_id: str
    analysis_id: str
    export_type: str  # "html", "react", "pdf"
    export_url: str
    created_at: datetime

class GitHubProfile(BaseModel):
    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: str
    public_repos: int
    followers: int
    following: int
    location: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    twitter_username: Optional[str] = None

class Repository(BaseModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int
    forks_count: int
    created_at: str
    updated_at: str
    html_url: str
    clone_url: str
    topics: List[str] = []

class SkillCategory(str, Enum):
    PROGRAMMING_LANGUAGES = "programming_languages"
    FRAMEWORKS = "frameworks"
    DATABASES = "databases"
    TOOLS = "tools"
    CLOUD_SERVICES = "cloud_services"
    OTHER = "other"

class Skill(BaseModel):
    name: str
    category: SkillCategory
    proficiency_level: int  # 1-5 scale
    years_experience: Optional[float] = None
    last_used: Optional[datetime] = None

class JobMatch(BaseModel):
    title: str
    description: str
    company: str
    logo_url: Optional[str] = None
    matched_skills: List[str]
    salary_range: Optional[str] = None
    location: Optional[str] = None
    remote: bool = False
    experience_level: str = "mid"  # junior, mid, senior, lead

class SkillSuggestion(BaseModel):
    skill_name: str
    reason: str
    learning_resources: List[Dict[str, str]]  # [{"title": "Video Title", "url": "youtube_url"}]
    difficulty: str  # "beginner", "intermediate", "advanced"
    estimated_time: str  # "1 week", "1 month", etc.
