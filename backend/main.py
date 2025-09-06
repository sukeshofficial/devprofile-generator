import os
import re
import json
from dotenv import load_dotenv
import httpx
import requests
from typing import List, Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import hashlib

# Import our new modules
from config import settings
from models import User, UserCreate, UserLogin, Analysis, AnalysisCreate
from auth import authenticate_user, create_user_token, get_current_active_user, get_password_hash
from database import db, cache_service
from github_oauth import github_oauth
from pdf_service import pdf_service
from portfolio_service import portfolio_service
from dotenv import load_dotenv

load_dotenv()
# Initialize FastAPI application
app = FastAPI()

# Initialize Jinja2 templates with correct directory path
# Use absolute path to ensure templates are found regardless of working directory
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

# Get OpenRouter API key from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

# Validate environment variables on startup
def validate_environment():
    """Validate required environment variables and configuration."""
    if OPENROUTER_API_KEY == "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":
        print("✅ OpenRouter API key configured")
    else:
        print("⚠️  WARNING: OPENROUTER_API_KEY not set. AI features will not work.")
        print("   Set it with: export OPENROUTER_API_KEY='your-key-here'")

# Run validation on startup
validate_environment()


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """
    Homepage route that displays the main form for GitHub profile input.
    This is the entry point of the application.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/fetch-profile", response_class=HTMLResponse)
async def fetch_profile(request: Request, username: str = Form(...), token: str = Form(...)):
    """
    Fetches GitHub profile and repository data for the given username and token.
    Handles authentication errors and displays appropriate error messages.
    """
    try:
        # Set up GitHub API headers with the provided token
        headers = {"Authorization": f"token {token}"}
        
        # Make concurrent requests to GitHub API for profile and repositories
        async with httpx.AsyncClient(timeout=30.0) as client:
            profile_resp = await client.get(
                f"https://api.github.com/users/{username}", headers=headers
            )
            repos_resp = await client.get(
                f"https://api.github.com/users/{username}/repos", headers=headers
            )

        # Check if profile fetch was successful
        if profile_resp.status_code != 200:
            error_message = "Invalid credentials or user not found"
            if profile_resp.status_code == 404:
                error_message = "User not found. Please check the username."
            elif profile_resp.status_code == 401:
                error_message = "Invalid GitHub token. Please check your token."
            elif profile_resp.status_code == 403:
                error_message = "API rate limit exceeded. Please try again later."
            
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": error_message},
            )

        # Parse JSON responses
        try:
            profile_data = profile_resp.json()
            repos_data = repos_resp.json()
        except json.JSONDecodeError:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Invalid response from GitHub API"},
            )

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "profile": profile_data,
                "repos": repos_data,
                "token": token,  # Pass token to next step
            },
        )
    
    except httpx.TimeoutException:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Request timeout. Please try again."},
        )
    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Network error: {str(e)}"},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"An unexpected error occurred: {str(e)}"},
        )


@app.post("/analyze-readmes", response_class=HTMLResponse)
async def analyze_readmes(
    request: Request,
    username: str = Form(...),
    token: str = Form(...),
    selected_repos: List[str] = Form(...),
):
    """
    Fetches README files from selected GitHub repositories.
    Handles base64 decoding and various error conditions.
    """
    try:
        # Set up GitHub API headers
        headers = {"Authorization": f"token {token}"}
        readmes = {}

        # Fetch README files for each selected repository
        async with httpx.AsyncClient(timeout=30.0) as client:
            for repo in selected_repos:
                try:
                    readme_url = f"https://api.github.com/repos/{username}/{repo}/readme"
                    resp = await client.get(readme_url, headers=headers)
                    
                    if resp.status_code == 200:
                        # Parse the response JSON
                        try:
                            readme_data = resp.json()
                            content = readme_data.get("content", "")
                            encoding = readme_data.get("encoding", "base64")
                            
                            # Decode content based on encoding type
                            if encoding == "base64":
                                import base64
                                try:
                                    decoded = base64.b64decode(content).decode("utf-8")
                                    readmes[repo] = decoded
                                except (base64.binascii.Error, UnicodeDecodeError) as e:
                                    readmes[repo] = f"(Error decoding README: {str(e)})"
                            else:
                                readmes[repo] = content
                        except json.JSONDecodeError:
                            readmes[repo] = "(Invalid JSON response from GitHub API)"
                    elif resp.status_code == 404:
                        readmes[repo] = "(README not found)"
                    elif resp.status_code == 401:
                        readmes[repo] = "(Authentication failed)"
                    elif resp.status_code == 403:
                        readmes[repo] = "(Access forbidden - rate limit or permissions)"
                    else:
                        readmes[repo] = f"(Error {resp.status_code}: {resp.text[:100]})"
                        
                except httpx.TimeoutException:
                    readmes[repo] = "(Request timeout)"
                except httpx.RequestError as e:
                    readmes[repo] = f"(Network error: {str(e)})"
                except Exception as e:
                    readmes[repo] = f"(Unexpected error: {str(e)})"

        return templates.TemplateResponse(
            "readmes.html",
            {
                "request": request,
                "readmes": readmes,
                "username": username,
                "token": token,
            },
        )
    
    except Exception as e:
        return templates.TemplateResponse(
            "readmes.html",
            {
                "request": request,
                "readmes": {"error": f"Failed to fetch README files: {str(e)}"},
                "username": username,
                "token": token,
            },
        )


@app.post("/extract-skills", response_class=HTMLResponse)
async def extract_skills(request: Request):
    """
    Extracts technical skills from README files using AI (OpenRouter API).
    Processes form data and sends content to AI for skill extraction.
    """
    try:
        # Parse form data
        form = await request.form()
        username = form.get("username")
        token = form.get("token")

        # Extract README contents from form data
        readmes = []
        for key in form.keys():
            if key.startswith("readme_"):
                readme_content = form.get(key)
                if readme_content and readme_content.strip():
                    readmes.append(readme_content)

        # Check if we have any README content to process
        if not readmes:
            return templates.TemplateResponse(
                "skills.html",
                {
                    "request": request,
                    "skills": "⚠️ No README content found to analyze.",
                    "username": username,
                    "token": token,
                },
            )

        # Combine all README contents
        combined_readmes = "\n\n".join(readmes)

        # Debug logging (can be removed in production)
        print("----- SENDING TO AI FOR SKILL EXTRACTION -----")
        for i, r in enumerate(readmes, 1):
            print(f"README {i}:\n{r[:200]}...")  # Print first 200 chars
        print("------ END ------")

        # Validate API key
        if not OPENROUTER_API_KEY:
            return templates.TemplateResponse(
                "skills.html",
                {
                    "request": request,
                    "skills": "⚠️ OpenRouter API key not configured. Please set OPENROUTER_API_KEY environment variable.",
                    "username": username,
                    "token": token,
                },
            )

        # Prepare AI prompt for skill extraction
        messages = [
            {"role": "system", "content": "You are an assistant that extracts only technical skills from README files."},
            {
                "role": "user",
                "content": f"""
                Extract the technical skills (languages, frameworks, tools, libraries) from the README content below.
                Return them as a **JSON array of strings**, nothing else.

                Example:
                ["Python", "FastAPI", "Git"]

                README content:
                {combined_readmes}
                """
            },
        ]


        # Make request to OpenRouter API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-3-8b-instruct",  # Free model option
                    "messages": messages,
                    "temperature": 0.3,
                },
            )

        # Check if API request was successful
        if response.status_code != 200:
            error_msg = f"OpenRouter API error (Status {response.status_code}): {response.text}"
            print(f"OpenRouter ERROR: {error_msg}")
            return templates.TemplateResponse(
                "skills.html",
                {
                    "request": request,
                    "skills": f"⚠️ API Error: {error_msg}",
                    "username": username,
                    "token": token,
                },
            )

        # Parse AI response
        try:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                skills_raw = result["choices"][0]["message"]["content"]
            else:
                print("OpenRouter ERROR: Invalid response format:", result)
                return templates.TemplateResponse(
                    "skills.html",
                    {
                        "request": request,
                        "skills": f"⚠️ Invalid response from AI:\n{result}",
                        "username": username,
                        "token": token,
                    },
                )
        except json.JSONDecodeError:
            return templates.TemplateResponse(
                "skills.html",
                {
                    "request": request,
                    "skills": "⚠️ Invalid JSON response from AI service.",
                    "username": username,
                    "token": token,
                },
            )

        return templates.TemplateResponse(
            "skills.html",
            {
                "request": request,
                "skills": skills_raw,
                "username": username,
                "token": token,
            },
        )

    except httpx.TimeoutException:
        return templates.TemplateResponse(
            "skills.html",
            {
                "request": request,
                "skills": "⚠️ Request timeout. The AI service took too long to respond.",
                "username": username,
                "token": token,
            },
        )
    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "skills.html",
            {
                "request": request,
                "skills": f"⚠️ Network error: {str(e)}",
                "username": username,
                "token": token,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "skills.html",
            {
                "request": request,
                "skills": f"⚠️ Unexpected error: {str(e)}",
                "username": username,
                "token": token,
            },
        )


@app.post("/suggest-skills", response_class=HTMLResponse)
async def suggest_skills(request: Request):
    """
    Generates skill improvement suggestions based on extracted skills.
    Uses AI to recommend learning resources with YouTube search terms.
    """
    try:
        # Parse form data
        form = await request.form()
        username = form.get("username")
        token = form.get("token")
        extracted_skills = form.get("skills")

        # Validate input data
        if not extracted_skills or not extracted_skills.strip():
            return templates.TemplateResponse(
                "suggestions.html",
                {
                    "request": request,
                    "suggestions": "⚠️ No skills provided for analysis.",
                    "resources": [],
                    "username": username,
                    "token": token,
                    "skills": extracted_skills,
                },
            )

        # Validate API key
        if not OPENROUTER_API_KEY:
            return templates.TemplateResponse(
                "suggestions.html",
                {
                    "request": request,
                    "suggestions": "⚠️ OpenRouter API key not configured.",
                    "resources": [],
                    "username": username,
                    "token": token,
                    "skills": extracted_skills,
                },
            )

        # Prepare AI prompt for skill suggestions
        messages = [
            {"role": "system", "content": "You are a helpful backend development mentor."},
            {
                "role": "user",
                "content": f"""
            These are the skills the developer already has:

            {extracted_skills}

            Suggest 3–5 missing backend development skills. For each, give a **searchable YouTube title**, not a made-up link.
            Format:

            Skill: Redis  
            Search: Redis Crash Course

            Skill: PostgreSQL  
            Search: PostgreSQL Full Tutorial

            """,
            },
        ]

        # Make request to OpenRouter API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-3-8b-instruct",
                    "messages": messages,
                    "temperature": 0.3,
                },
            )

        # Check if API request was successful
        if response.status_code != 200:
            error_msg = f"OpenRouter API error (Status {response.status_code}): {response.text}"
            print(f"OpenRouter ERROR: {error_msg}")
            return templates.TemplateResponse(
                "suggestions.html",
                {
                    "request": request,
                    "suggestions": f"⚠️ API Error: {error_msg}",
                    "resources": [],
                    "username": username,
                    "token": token,
                    "skills": extracted_skills,
                },
            )

        # Parse AI response
        try:
            result = response.json()
            print("📦 Full OpenRouter Response:\n", json.dumps(result, indent=2))
            
            if "choices" in result and len(result["choices"]) > 0:
                suggestions = result["choices"][0]["message"]["content"].strip()
            else:
                suggestions = ""
                print("❌ GPT response is malformed or empty.")
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as e:
            suggestions = ""
            print(f"❌ Error parsing AI response: {e}")

        # Process suggestions and extract resources
        if not suggestions:
            suggestions = "⚠️ AI did not return any usable output."
            resources = []
        else:
            resources = extract_resources_from_gpt(suggestions)

        return templates.TemplateResponse(
            "suggestions.html",
            {
                "request": request,
                "suggestions": suggestions,
                "resources": resources,
                "username": username,
                "token": token,
                "skills": extracted_skills,
            },
        )

    except httpx.TimeoutException:
        return templates.TemplateResponse(
            "suggestions.html",
            {
                "request": request,
                "suggestions": "⚠️ Request timeout. The AI service took too long to respond.",
                "resources": [],
                "username": username,
                "token": token,
                "skills": extracted_skills,
            },
        )
    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "suggestions.html",
            {
                "request": request,
                "suggestions": f"⚠️ Network error: {str(e)}",
                "resources": [],
                "username": username,
                "token": token,
                "skills": extracted_skills,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "suggestions.html",
            {
                "request": request,
                "suggestions": f"⚠️ Unexpected error: {str(e)}",
                "resources": [],
                "username": username,
                "token": token,
                "skills": extracted_skills,
            },
        )


def extract_resources_from_gpt(content: str):
    """
    Parse GPT responses to extract skill suggestions and YouTube search terms.
    
    Expected format:
    Skill: Redis
    Search: Redis Crash Course
    
    Args:
        content (str): Raw AI response containing skill suggestions
        
    Returns:
        list: List of dictionaries with skill, title, and YouTube URL
    """
    # Regex pattern to match skill and search term pairs
    pattern = r"Skill\s*:\s*(.*?)\s*Search\s*:\s*(.*?)\s*(?=\n|$)"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    resources = []

    # Process each matched skill-search pair
    for skill, search in matches:
        # Get actual YouTube URL for the search term
        url = get_real_youtube_link(search)
        resources.append({
            "skill": skill.strip(), 
            "title": search.strip(), 
            "url": url
        })

    # Debug logging
    if not resources:
        print("⚠️ No skill suggestions found in AI response.")
        print("Raw GPT output:\n", content)
    else:
        print("✅ Successfully parsed skill suggestions:")
        for res in resources:
            print(f"  - {res['skill']}: {res['title']}")

    return resources


def get_real_youtube_link(query: str):
    """
    Search YouTube for a video matching the given query and return the first result URL.
    
    Args:
        query (str): Search term to look up on YouTube
        
    Returns:
        str: YouTube video URL or empty string if no results found
    """
    try:
        # Construct YouTube search URL
        search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        # Make request to YouTube search
        resp = requests.get(search_url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        # Extract video ID from search results
        match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", resp.text)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
        
        return ""
    except requests.RequestException as e:
        print(f"⚠️ Error searching YouTube for '{query}': {e}")
        return ""
    except Exception as e:
        print(f"⚠️ Unexpected error searching YouTube: {e}")
        return ""


def extract_youtube_id(url: str):
    """
    Extract YouTube video ID from various YouTube URL formats.
    
    Args:
        url (str): YouTube URL (youtube.com or youtu.be format)
        
    Returns:
        str: 11-character YouTube video ID or empty string if not found
    """
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    if "youtube.com" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return match.group(1)
    return ""


templates.env.filters["youtube_id"] = extract_youtube_id


# @app.post("/match-jobs", response_class=HTMLResponse)
# async def match_jobs(request: Request):
#     """
#     Matches extracted skills with relevant job opportunities using AI.
#     Generates job recommendations with company logos and skill alignments.
#     """
#     try:
#         # Parse form data
#         form = await request.form()
#         skills = form.get("skills")
#         username = form.get("username")
#         token = form.get("token")

#         # Validate input data
#         if not skills or not skills.strip():
#             return templates.TemplateResponse(
#                 "jobmatch.html", 
#                 {
#                     "request": request, 
#                     "jobs": [], 
#                     "username": username,
#                     "error": "No skills provided for job matching"
#                 }
#             )

#         # Validate API key
#         if not OPENROUTER_API_KEY:
#             return templates.TemplateResponse(
#                 "jobmatch.html", 
#                 {
#                     "request": request, 
#                     "jobs": [], 
#                     "username": username,
#                     "error": "OpenRouter API key not configured"
#                 }
#             )

#         # Prepare AI prompt for job matching
#         messages = [
#             {
#                 "role": "system",
#                 "content": "You are a career advisor that maps skills to job opportunities.",
#             },
#             {
#                 "role": "user",
#                 "content": f"""
#                     The following skills were extracted from a developer's GitHub:
#                     If you dont't get any match to job, make sure to give atleast 1 job role.
#                     {skills}

#                     List 4 job roles that fit this skillset. For each, include:

#                     - Job Title
#                     - Short Description
#                     - 3–5 matched skills from above
#                     - A company that typically hires for it

#                     Return as JSON in this format:

#                     {{
#                     "jobs": [
#                         {{
#                         "title": "Backend Engineer",
#                         "description": "Build REST APIs using FastAPI and SQLAlchemy.",
#                         "skills": ["FastAPI", "SQLAlchemy", "Git"],
#                         "company": "Netflix"
#                         }}
#                     ]
#                     }}
#                 """,
#             },
#         ]

#         # Make request to OpenRouter API
#         async with httpx.AsyncClient(timeout=60.0) as client:
#             response = await client.post(
#                 "https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                     "Content-Type": "application/json",
#                 },
#                 json={
#                     "model": "meta-llama/llama-3-8b-instruct",  # Reliable model for JSON generation
#                     "messages": messages,
#                     "temperature": 0.4,
#                 },
#             )

#         # Check if API request was successful
#         if response.status_code != 200:
#             error_msg = f"OpenRouter API error (Status {response.status_code}): {response.text}"
#             print(f"OpenRouter ERROR: {error_msg}")
#             return templates.TemplateResponse(
#                 "jobmatch.html", 
#                 {
#                     "request": request, 
#                     "jobs": [], 
#                     "username": username,
#                     "error": f"API Error: {error_msg}"
#                 }
#             )

#         # Parse AI response
#         try:
#             result = response.json()
#             if "choices" in result and len(result["choices"]) > 0:
#                 ai_content = result["choices"][0]["message"]["content"]
#                 parsed = json.loads(ai_content)
#                 jobs = parsed.get("jobs", [])
#             else:
#                 print("❌ Invalid AI response format:", result)
#                 jobs = []
#         except (json.JSONDecodeError, KeyError, IndexError) as e:
#             print(f"❌ Error parsing AI response: {e}")
#             print("Raw AI response:", result)
#             jobs = []

#         # Add company logos using Clearbit service
#         for job in jobs:
#             if "company" in job:
#                 company_name = job["company"].lower().replace(" ", "").replace(".", "")
#                 job["logo"] = f"https://logo.clearbit.com/{company_name}.com"

#         return templates.TemplateResponse(
#             "jobmatch.html", 
#             {
#                 "request": request, 
#                 "jobs": jobs, 
#                 "username": username
#             }
#         )

#     except httpx.TimeoutException:
#         return templates.TemplateResponse(
#             "jobmatch.html", 
#             {
#                 "request": request, 
#                 "jobs": [], 
#                 "username": username,
#                 "error": "Request timeout. The AI service took too long to respond."
#             }
#         )
#     except httpx.RequestError as e:
#         return templates.TemplateResponse(
#             "jobmatch.html", 
#             {
#                 "request": request, 
#                 "jobs": [], 
#                 "username": username,
#                 "error": f"Network error: {str(e)}"
#             }
#         )
#     except Exception as e:
#         return templates.TemplateResponse(
#             "jobmatch.html", 
#             {
#                 "request": request, 
#                 "jobs": [], 
#                 "username": username,
#                 "error": f"Unexpected error: {str(e)}"
#             }
#         )

@app.post("/match-jobs", response_class=HTMLResponse)
async def match_jobs(request: Request):
    """
    Matches extracted skills with relevant job opportunities using AI.
    Generates job recommendations with company logos and skill alignments.
    """
    try:
        # Parse form data
        form = await request.form()
        skills = form.get("skills")
        username = form.get("username")
        token = form.get("token")

        # Validate input data
        if not skills or not skills.strip():
            return templates.TemplateResponse(
                "jobmatch.html",
                {
                    "request": request,
                    "jobs": [],
                    "username": username,
                    "error": "No skills provided for job matching",
                },
            )

        # Validate API key
        if not OPENROUTER_API_KEY:
            return templates.TemplateResponse(
                "jobmatch.html",
                {
                    "request": request,
                    "jobs": [],
                    "username": username,
                    "error": "OpenRouter API key not configured",
                },
            )

        # Prepare AI prompt
        messages = [
            {
                "role": "system",
                "content": "You are a career advisor that maps skills to job opportunities.",
            },
            {
                "role": "user",
                "content": f"""
                The following skills were extracted from a developer's GitHub:
                {skills}

                List 4 job roles that fit this skillset. For each, include:

                - Job Title
                - Short Description
                - 3–5 matched skills from above
                - A company that typically hires for it

                Return as JSON in this format:

                {{
                  "jobs": [
                    {{
                      "title": "Backend Engineer",
                      "description": "Build REST APIs using FastAPI and SQLAlchemy.",
                      "skills": ["FastAPI", "SQLAlchemy", "Git"],
                      "company": "Netflix"
                    }}
                  ]
                }}
                """,
            },
        ]

        # Call OpenRouter
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-3-8b-instruct",
                    "messages": messages,
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"},  # ✅ enforce JSON
                },
            )

        # Check API response
        if response.status_code != 200:
            error_msg = f"OpenRouter API error (Status {response.status_code}): {response.text}"
            print(f"OpenRouter ERROR: {error_msg}")
            return templates.TemplateResponse(
                "jobmatch.html",
                {
                    "request": request,
                    "jobs": [],
                    "username": username,
                    "error": f"API Error: {error_msg}",
                },
            )

        # Parse AI response safely
        result = response.json()
        jobs = []
        try:
            ai_content = result["choices"][0]["message"]["content"].strip()

            # Strip ```json fences if present
            import re
            ai_content = re.sub(r"^```json|```$", "", ai_content, flags=re.MULTILINE).strip()

            parsed = json.loads(ai_content)
            jobs = parsed.get("jobs", [])
        except Exception as e:
            print(f"❌ Error parsing AI response: {e}")
            print("Raw AI response:", result)
            jobs = []

        # Add company logos
        for job in jobs:
            if "company" in job:
                company_name = job["company"].lower().replace(" ", "").replace(".", "")
                job["logo"] = f"https://www.google.com/s2/favicons?sz=128&domain={company_name}.com"

        return templates.TemplateResponse(
            "jobmatch.html", {"request": request, "jobs": jobs, "username": username}
        )

    except httpx.TimeoutException:
        return templates.TemplateResponse(
            "jobmatch.html",
            {
                "request": request,
                "jobs": [],
                "username": username,
                "error": "Request timeout. The AI service took too long to respond.",
            },
        )
    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "jobmatch.html",
            {
                "request": request,
                "jobs": [],
                "username": username,
                "error": f"Network error: {str(e)}",
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "jobmatch.html",
            {
                "request": request,
                "jobs": [],
                "username": username,
                "error": f"Unexpected error: {str(e)}",
            },
        )


# ==================== NEW AUTHENTICATION ROUTES ====================

@app.post("/auth/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...), password: str = Form(...), full_name: str = Form(None)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await db.get_user_by_email(email)
        if existing_user:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "User with this email already exists"}
            )
        
        # Create user data
        user_data = {
            "email": email,
            "username": username,
            "full_name": full_name,
            "password_hash": get_password_hash(password),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        # Save user to database
        user = await db.create_user(user_data)
        if not user:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Failed to create user account"}
            )
        
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "success": "Account created successfully! Please log in."}
        )
    
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Registration failed: {str(e)}"}
        )

@app.post("/auth/login", response_class=HTMLResponse)
async def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    """Login user and create session"""
    try:
        user = await authenticate_user(email, password)
        if not user:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Invalid email or password"}
            )
        
        # Create access token
        access_token = create_user_token(user)
        
        # Store token in session (you might want to use cookies instead)
        response = templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": user.dict(), "token": access_token}
        )
        
        return response
    
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Login failed: {str(e)}"}
        )

@app.get("/auth/github")
async def github_login():
    """Initiate GitHub OAuth flow"""
    from fastapi.responses import RedirectResponse
    auth_url = github_oauth.get_authorization_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/github/callback")
async def github_callback(request: Request, code: str = None, state: str = None):
    """Handle GitHub OAuth callback"""
    try:
        if not code:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "GitHub authorization failed"}
            )
        
        # Exchange code for access token
        access_token = await github_oauth.exchange_code_for_token(code)
        if not access_token:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Failed to get GitHub access token"}
            )
        
        # Get GitHub user profile
        github_profile = await github_oauth.get_user_profile(access_token)
        if not github_profile:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Failed to get GitHub profile"}
            )
        
        # Check if user exists in our database
        user = await db.get_user_by_email(f"{github_profile.login}@github.com")
        
        if not user:
            # Create new user from GitHub profile
            user_data = {
                "email": f"{github_profile.login}@github.com",
                "username": github_profile.login,
                "full_name": github_profile.name,
                "github_username": github_profile.login,
                "avatar_url": github_profile.avatar_url,
                "password_hash": "",  # No password for OAuth users
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            user = await db.create_user(user_data)
        
        # Create access token
        access_token_jwt = create_user_token(User(**user))
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "token": access_token_jwt,
                "github_profile": github_profile.dict()
            }
        )
    
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"GitHub login failed: {str(e)}"}
        )

# ==================== DASHBOARD ROUTES ====================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_active_user)):
    """User dashboard"""
    try:
        # Get user's analyses
        analyses = await db.get_user_analyses(current_user.id)
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": current_user.dict(),
                "analyses": analyses
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Dashboard error: {str(e)}"}
        )

@app.post("/save-analysis", response_class=JSONResponse)
async def save_analysis(
    request: Request,
    analysis_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Save analysis to database"""
    try:
        analysis_record = {
            "user_id": current_user.id,
            "github_username": analysis_data.get("github_username"),
            "selected_repos": analysis_data.get("selected_repos", []),
            "extracted_skills": analysis_data.get("extracted_skills", []),
            "job_matches": analysis_data.get("job_matches", []),
            "skill_suggestions": analysis_data.get("skill_suggestions", []),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_public": False
        }
        
        saved_analysis = await db.create_analysis(analysis_record)
        return {"success": True, "analysis_id": saved_analysis["id"]}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== EXPORT ROUTES ====================

@app.post("/export/pdf", response_class=FileResponse)
async def export_pdf(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Export analysis as PDF"""
    try:
        analysis = await db.get_analysis_by_id(analysis_id)
        if not analysis or analysis["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Create PDF
        pdf_bytes = pdf_service.get_pdf_bytes(analysis, "analysis")
        
        # Save to temporary file
        temp_path = f"temp_analysis_{analysis_id}.pdf"
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)
        
        return FileResponse(
            temp_path,
            media_type="application/pdf",
            filename=f"analysis_{analysis_id}.pdf"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/portfolio/html", response_class=FileResponse)
async def export_html_portfolio(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Export portfolio as HTML"""
    try:
        analysis = await db.get_analysis_by_id(analysis_id)
        if not analysis or analysis["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get user data
        user_data = {
            "github_username": analysis["github_username"],
            "name": current_user.full_name or current_user.username,
            "avatar_url": current_user.avatar_url or "",
            "bio": f"Developer with {len(analysis['extracted_skills'])} skills"
        }
        
        # Create HTML portfolio
        portfolio_path = await portfolio_service.create_html_portfolio(user_data, analysis)
        
        return FileResponse(
            portfolio_path,
            media_type="text/html",
            filename=f"portfolio_{analysis_id}.html"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/portfolio/react", response_class=FileResponse)
async def export_react_portfolio(
    analysis_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Export portfolio as React project"""
    try:
        analysis = await db.get_analysis_by_id(analysis_id)
        if not analysis or analysis["user_id"] != current_user.id:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get user data
        user_data = {
            "github_username": analysis["github_username"],
            "name": current_user.full_name or current_user.username,
            "avatar_url": current_user.avatar_url or "",
            "bio": f"Developer with {len(analysis['extracted_skills'])} skills"
        }
        
        # Create React portfolio
        portfolio_path = await portfolio_service.create_react_portfolio(user_data, analysis)
        
        # Create ZIP archive
        zip_path = await portfolio_service.create_zip_archive(portfolio_path)
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"react_portfolio_{analysis_id}.zip"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== UPDATED EXISTING ROUTES WITH CACHING ====================

@app.post("/fetch-profile", response_class=HTMLResponse)
async def fetch_profile(request: Request, username: str = Form(...), token: str = Form(...)):
    """
    Fetches GitHub profile and repository data for the given username and token.
    Now includes caching for better performance.
    """
    try:
        # Check cache first
        cached_profile = await cache_service.get_github_profile(username)
        cached_repos = await cache_service.get_github_repos(username)
        
        if cached_profile and cached_repos:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "profile": cached_profile,
                    "repos": cached_repos,
                    "token": token,
                },
            )
        
        # Set up GitHub API headers with the provided token
        headers = {"Authorization": f"token {token}"}
        
        # Make concurrent requests to GitHub API for profile and repositories
        async with httpx.AsyncClient(timeout=30.0) as client:
            profile_resp = await client.get(
                f"https://api.github.com/users/{username}", headers=headers
            )
            repos_resp = await client.get(
                f"https://api.github.com/users/{username}/repos", headers=headers
            )

        # Check if profile fetch was successful
        if profile_resp.status_code != 200:
            error_message = "Invalid credentials or user not found"
            if profile_resp.status_code == 404:
                error_message = "User not found. Please check the username."
            elif profile_resp.status_code == 401:
                error_message = "Invalid GitHub token. Please check your token."
            elif profile_resp.status_code == 403:
                error_message = "API rate limit exceeded. Please try again later."
            
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": error_message},
            )

        # Parse JSON responses
        try:
            profile_data = profile_resp.json()
            repos_data = repos_resp.json()
        except json.JSONDecodeError:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "Invalid response from GitHub API"},
            )

        # Cache the results
        await cache_service.set_github_profile(username, profile_data)
        await cache_service.set_github_repos(username, repos_data)

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "profile": profile_data,
                "repos": repos_data,
                "token": token,  # Pass token to next step
            },
        )
    
    except httpx.TimeoutException:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Request timeout. Please try again."},
        )
    except httpx.RequestError as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"Network error: {str(e)}"},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": f"An unexpected error occurred: {str(e)}"},
        )

# Main execution block - starts the FastAPI server
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # Railway sets PORT
    uvicorn.run(
        "main:app",
        host="0.0.0.0",   # listen on all interfaces
        port=port,
        reload=False,     # disable reload in prod
        log_level="info"
    )
