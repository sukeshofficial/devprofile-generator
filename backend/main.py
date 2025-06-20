from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from fastapi import Form
from typing import List
import os
import httpx
from fastapi import Request
from fastapi.responses import HTMLResponse
import re
import json
import requests
import os
from fastapi.responses import JSONResponse

templates = Jinja2Templates(directory="templates")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "<your-openrouter-api-key>")

app = FastAPI()
templates = Jinja2Templates(directory="backend/templates")

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/fetch-profile", response_class=HTMLResponse)
async def fetch_profile(request: Request, username: str = Form(...), token: str = Form(...)):
    headers = {"Authorization": f"token {token}"}
    async with httpx.AsyncClient() as client:
        profile_resp = await client.get(f"https://api.github.com/users/{username}", headers=headers)
        repos_resp = await client.get(f"https://api.github.com/users/{username}/repos", headers=headers)

    if profile_resp.status_code != 200:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid credentials or user not found"})

    profile_data = profile_resp.json()
    repos_data = repos_resp.json()

    return templates.TemplateResponse("index.html", {
    "request": request,
    "profile": profile_data,
    "repos": repos_data,
    "token": token  # ✅ Add this line
})

@app.post("/analyze-readmes", response_class=HTMLResponse)
async def analyze_readmes(
    request: Request,
    username: str = Form(...),
    token: str = Form(...),
    selected_repos: List[str] = Form(...)
):
    headers = {"Authorization": f"token {token}"}
    readmes = {}

    async with httpx.AsyncClient() as client:
        for repo in selected_repos:
            readme_url = f"https://api.github.com/repos/{username}/{repo}/readme"
            resp = await client.get(readme_url, headers=headers)
            if resp.status_code == 200:
                content = resp.json().get("content", "")
                encoding = resp.json().get("encoding", "base64")
                if encoding == "base64":
                    import base64
                    decoded = base64.b64decode(content).decode("utf-8")
                    readmes[repo] = decoded
                else:
                    readmes[repo] = content
            else:
                readmes[repo] = "(README not found or inaccessible)"

    return templates.TemplateResponse("readmes.html", {
        "request": request,
        "readmes": readmes,
        "username": username,
        "token": token,
    })


@app.post("/extract-skills", response_class=HTMLResponse)
async def extract_skills(request: Request):
    form = await request.form()
    username = form.get("username")
    token = form.get("token")

    # Extract README contents
    readmes = []
    for key in form.keys():
        if key.startswith("readme_"):
            readme_content = form.get(key)
            if readme_content and readme_content.strip():
                readmes.append(readme_content)


    combined_readmes = "\n\n".join(readmes)

    print("----- SENDING TO GPT -----")
    for i, r in enumerate(readmes, 1):
        print(f"README {i}:\n{r[:200]}...")  # Print first 200 chars
    print("------ END ------")


    # Prompt for skill extraction
    messages = [
                    {"role": "system", "content": "You are a resume analyzer."},
                    {"role": "user", "content": f"""Extract only the **technical skills** from the following README files.

                    ✅ Return just a plain bullet list with no headings or descriptions.
                    ✅ Do not include categories or explanations.
                    ✅ Only include technologies, tools, libraries, languages, frameworks.

                    Here is the content:
                    {combined_readmes}

                    🎯 Format:
                    - Python
                    - FastAPI
                    - Git
                    """}
                ]


    # HTTP request to OpenRouter
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",  # You can change to another free model
                "messages": messages,
                "temperature": 0.3
            }
        )

    result = response.json()
    if "choices" in result:
        skills_raw = result["choices"][0]["message"]["content"]
    else:
        print("OpenRouter ERROR:", result)
        return templates.TemplateResponse("skills.html", {
            "request": request,
            "skills": f"⚠️ Error from OpenRouter:\n{result}",
            "username": username,
            "token": token
        })

    return templates.TemplateResponse("skills.html", {
        "request": request,
        "skills": skills_raw,
        "username": username,
        "token": token
    })

@app.post("/suggest-skills", response_class=HTMLResponse)
async def suggest_skills(request: Request):
    form = await request.form()
    username = form.get("username")
    token = form.get("token")
    extracted_skills = form.get("skills")

    messages = [
        {"role": "system", "content": "You are a helpful backend mentor."},
        {"role": "user", "content": f"""
        These are the skills the developer already has:

        {extracted_skills}

        Suggest 3–5 missing backend development skills. For each, give a **searchable YouTube title**, not a made-up link.
        Format:

        Skill: Redis  
        Search: Redis Crash Course

        Skill: PostgreSQL  
        Search: PostgreSQL Full Tutorial

        """}
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.3
            }
        )

    result = response.json()

    # ✅ Print full OpenRouter result
    print("📦 Full OpenRouter Response:\n", json.dumps(result, indent=2))

    try:
        suggestions = result["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        suggestions = ""
        print("❌ GPT response is malformed or empty.")

    if not suggestions:
        suggestions = "⚠️ GPT did not return any usable output."
        resources = []
    else:
        resources = extract_resources_from_gpt(suggestions)

    return templates.TemplateResponse("suggestions.html", {
        "request": request,
        "suggestions": suggestions,
        "resources": resources,
        "username": username,
        "token": token,
        "skills": extracted_skills
    })

def extract_resources_from_gpt(content: str):
    """
    Parse GPT responses like:
    Skill: Redis
    Search: Redis Crash Course
    """
    pattern = r"Skill\s*:\s*(.*?)\s*Search\s*:\s*(.*?)\s*(?=\n|$)"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    resources = []

    for skill, search in matches:
        url = get_real_youtube_link(search)
        resources.append({
            "skill": skill.strip(),
            "title": search.strip(),
            "url": url
        })

    if not resources:
        print("⚠️ No matches found.")
        print("Raw GPT output:\n", content)
    else:
        print("✅ Parsed Skills:")
        for res in resources:
            print(res)

    return resources

def get_real_youtube_link(query: str):
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(search_url, headers=headers)
    match = re.search(r"watch\?v=([a-zA-Z0-9_-]{11})", resp.text)
    if match:
        return f"https://www.youtube.com/watch?v={match.group(1)}"
    return ""

def extract_youtube_id(url: str):
    if "youtu.be/" in url:
        return url.split("youtu.be/")[-1].split("?")[0]
    if "youtube.com" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return match.group(1)
    return ""

templates.env.filters["youtube_id"] = extract_youtube_id

@app.post("/match-jobs", response_class=HTMLResponse)
async def match_jobs(request: Request):
    form = await request.form()
    skills = form.get("skills")
    username = form.get("username")
    token = form.get("token")

    # GPT prompt to match jobs
    messages = [
        {"role": "system", "content": "You are a career advisor that maps skills to jobs."},
        {
        "role": "user",
        "content": """
                        The following skills were extracted from a developer’s GitHub:

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
                    """.format(skills=skills)
        }
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",  # safer model
                "messages": messages,
                "temperature": 0.4
            }
        )

    result = response.json()
    try:
        parsed = json.loads(result["choices"][0]["message"]["content"])
        jobs = parsed.get("jobs", [])
    except Exception as e:
        print("❌ GPT error or bad JSON:", result)
        jobs = []

    # Add company logo using Clearbit
    for job in jobs:
        company_name = job["company"].lower().replace(" ", "")
        job["logo"] = f"https://logo.clearbit.com/{company_name}.com"

    return templates.TemplateResponse("jobmatch.html", {
        "request": request,
        "jobs": jobs,
        "username": username
    })
