"""
OpenRouter API client for AI-powered analysis

Handles communication with OpenRouter-compatible models for skill extraction,
job matching, bullet generation, and other AI features.
"""

import httpx
import json
import os
from typing import Dict, Any, List
import asyncio

class OpenRouterClient:
    """OpenRouter API client with retry logic and JSON validation"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "DevProfile Resume Automator"
        }
        self.default_model = "openai/gpt-3.5-turbo"
    
    async def _make_request(self, messages: List[Dict], temperature: float = 0.1, retries: int = 3) -> Dict[str, Any]:
        """Make request to OpenRouter with retry logic"""
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json={
                            "model": self.default_model,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": 2000
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        content = result["choices"][0]["message"]["content"]
                        
                        # Parse and validate JSON
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError:
                            # Try to extract JSON from response
                            import re
                            json_match = re.search(r'\{.*\}', content, re.DOTALL)
                            if json_match:
                                return json.loads(json_match.group())
                            raise Exception("Invalid JSON response from AI")
                    
                    elif response.status_code == 429:
                        wait_time = 2 ** attempt
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        response.raise_for_status()
                        
            except Exception as e:
                if attempt == retries - 1:
                    raise Exception(f"OpenRouter API error: {str(e)}")
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    async def extract_skills(self, repo_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract skills from repository context
        
        Args:
            repo_context: Repository metadata and content
            
        Returns:
            Structured skill extraction data
        """
        system_prompt = (
            "You are an assistant that must OUTPUT ONLY valid JSON following the specified schema. "
            "Do not include any prose or extra fields."
        )
        
        user_prompt = f"""
        Given the repository metadata, extract concise skills, tools, methods, and outcomes.
        
        Repository: {repo_context.get('repo_name', '')}
        Description: {repo_context.get('description', '')}
        Languages: {repo_context.get('languages', [])}
        README: {repo_context.get('readme', '')[:2000]}
        
        Output JSON schema:
        {{
            "repo": "string",
            "languages": ["string"],
            "skills": ["string"],
            "tools": ["string"],
            "methods": ["string"],
            "outcomes": ["string"],
            "evidence": ["string"]
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self._make_request(messages)
    
    async def match_job(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match candidate skills against job description
        
        Args:
            context: Candidate skills and job description
            
        Returns:
            Job match analysis
        """
        system_prompt = (
            "You are an assistant that must OUTPUT ONLY valid JSON following the specified schema. "
            "Do not include any prose or extra fields."
        )
        
        user_prompt = f"""
        Compare candidate skills against job description and provide match analysis.
        
        Candidate Skills: {context.get('candidate_skills', [])}
        Job Description: {context.get('job_description', '')}
        
        Output JSON schema:
        {{
            "role": "string",
            "score": 0,
            "matches": [{{"skill":"string","evidence":"string"}}],
            "gaps": [{{"skill":"string","priority":"low|medium|high"}}],
            "recommendations": ["string"]
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self._make_request(messages)
    
    async def generate_bullets(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate STAR-format resume bullets
        
        Args:
            context: Project data and user context
            
        Returns:
            Generated bullet points
        """
        system_prompt = (
            "You are an assistant that must OUTPUT ONLY valid JSON following the specified schema. "
            "Do not include any prose or extra fields."
        )
        
        user_prompt = f"""
        Generate 6-8 STAR-format resume bullets from the project data.
        
        Projects: {context.get('projects', [])}
        Context: {context.get('user_context', {})}
        
        Output JSON schema:
        {{
            "bullets": [
                {{
                    "project": "string",
                    "text": "string",
                    "action": "string",
                    "tool": "string",
                    "result": "string",
                    "tags": ["string"]
                }}
            ]
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self._make_request(messages)
    
    async def optimize_linkedin(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate LinkedIn headline and summary suggestions
        
        Args:
            context: Profile data and target role
            
        Returns:
            LinkedIn optimization suggestions
        """
        system_prompt = (
            "You are an assistant that must OUTPUT ONLY valid JSON following the specified schema. "
            "Do not include any prose or extra fields."
        )
        
        user_prompt = f"""
        Generate LinkedIn headline and summary suggestions for the profile.
        
        Profile: {context.get('profile', {})}
        Target Role: {context.get('target_role', '')}
        
        Output JSON schema:
        {{
            "headlines": ["string","string","string"],
            "summary_lines": ["string","string","string"]
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self._make_request(messages)
    
    async def generate_interview_questions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate role-specific interview questions
        
        Args:
            context: Role information
            
        Returns:
            Interview questions
        """
        system_prompt = (
            "You are an assistant that must OUTPUT ONLY valid JSON following the specified schema. "
            "Do not include any prose or extra fields."
        )
        
        user_prompt = f"""
        Generate 5 role-specific interview questions progressing from general to deep.
        
        Role: {context.get('role', '')}
        
        Output JSON schema:
        {{
            "questions": ["string","string","string","string","string"]
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return await self._make_request(messages)