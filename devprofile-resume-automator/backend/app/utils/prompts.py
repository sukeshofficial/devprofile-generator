"""
AI prompt templates for OpenRouter integration

Contains all prompt templates used for skill extraction, job matching,
bullet generation, and other AI-powered features.
"""

# Skill extraction prompt template
SKILL_EXTRACTION_PROMPT = {
    "task": "skill_extraction",
    "schema": {
        "repo": "string",
        "languages": ["string"],
        "skills": ["string"],
        "tools": ["string"],
        "methods": ["string"],
        "outcomes": ["string"],
        "evidence": ["string"]
    },
    "instructions": (
        "Given the repository metadata (name, description, README text, languages, and commit summaries), "
        "extract concise `skills`, `tools`, `methods`, and `outcomes`. "
        "Populate `evidence` with short quoted sentences from README or commit messages. "
        "Output exactly one JSON object matching the schema."
    )
}

# Job matching prompt template
JOB_MATCH_PROMPT = {
    "task": "job_match",
    "schema": {
        "role": "string",
        "score": 0,
        "matches": [{"skill": "string", "evidence": "string"}],
        "gaps": [{"skill": "string", "priority": "low|medium|high"}],
        "recommendations": ["string"]
    },
    "instructions": (
        "Compare provided candidate skills against job description text. "
        "Produce a numeric `score` (0-100). "
        "List `matches` that connect candidate skills to explicit job requirements. "
        "List `gaps` and assign priority. "
        "Provide short actionable recommendations. "
        "Output only the JSON schema."
    )
}

# STAR bullets generation prompt template
GENERATE_BULLETS_PROMPT = {
    "task": "generate_bullets",
    "schema": {
        "bullets": [
            {
                "project": "string",
                "text": "string",
                "action": "string",
                "tool": "string",
                "result": "string",
                "tags": ["string"]
            }
        ]
    },
    "instructions": (
        "From each project summary and extracted skills, produce 6-8 STAR-format bullets per user request. "
        "Each bullet must include action, tool, and quantified result if possible. "
        "Keep each `text` ≤ 200 characters. "
        "Output exactly the JSON schema only."
    )
}

# Portfolio generator prompt template
PORTFOLIO_GENERATOR_PROMPT = {
    "task": "portfolio_generator",
    "schema": {
        "site_name": "string",
        "pages": [
            {"path": "string", "content": "string"}
        ],
        "static_assets": [{"path": "string", "content_base64": "string"}]
    },
    "instructions": (
        "Given user profile, skills, and projects, generate a minimal Next.js TypeScript portfolio scaffold. "
        "For each page produce `path` and `content` (tsx source). "
        "Do not include build artifacts. "
        "Output strictly the JSON schema."
    )
}

# LinkedIn optimization prompt template
LINKEDIN_PROMPT = {
    "task": "linkedin_extras",
    "schema": {
        "headlines": ["string", "string", "string"],
        "summary_lines": ["string", "string", "string"]
    },
    "instructions": (
        "Produce 3 headline options and 3 short summary lines tailored to the user's role/skills. "
        "Output only JSON."
    )
}

# Interview questions prompt template
INTERVIEW_PROMPT = {
    "task": "interview_questions",
    "schema": {
        "questions": ["string", "string", "string", "string", "string"]
    },
    "instructions": (
        "Generate 5 role-specific interview questions (progress from general to deep). "
        "Output only JSON."
    )
}

def get_skill_extraction_prompt(repo_context: dict) -> str:
    """
    Generate skill extraction prompt for a specific repository
    
    Args:
        repo_context: Repository metadata and content
        
    Returns:
        Formatted prompt string
    """
    return f"""
    {SKILL_EXTRACTION_PROMPT['instructions']}
    
    Repository Data:
    - Name: {repo_context.get('repo_name', '')}
    - Description: {repo_context.get('description', '')}
    - Languages: {repo_context.get('languages', [])}
    - README: {repo_context.get('readme', '')[:2000]}
    - Stars: {repo_context.get('stars', 0)}
    - Forks: {repo_context.get('forks', 0)}
    
    Required JSON Schema:
    {SKILL_EXTRACTION_PROMPT['schema']}
    """

def get_job_match_prompt(skills: list, job_description: str) -> str:
    """
    Generate job matching prompt
    
    Args:
        skills: List of candidate skills
        job_description: Job posting text
        
    Returns:
        Formatted prompt string
    """
    return f"""
    {JOB_MATCH_PROMPT['instructions']}
    
    Candidate Skills: {skills}
    Job Description: {job_description}
    
    Required JSON Schema:
    {JOB_MATCH_PROMPT['schema']}
    """

def get_bullet_generation_prompt(projects: list, context: dict) -> str:
    """
    Generate bullet point creation prompt
    
    Args:
        projects: List of project data
        context: Additional user context
        
    Returns:
        Formatted prompt string
    """
    return f"""
    {GENERATE_BULLETS_PROMPT['instructions']}
    
    Projects: {projects}
    Context: {context}
    
    Required JSON Schema:
    {GENERATE_BULLETS_PROMPT['schema']}
    """