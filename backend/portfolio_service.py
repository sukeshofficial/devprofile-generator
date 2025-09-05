import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiofiles
from pathlib import Path

class PortfolioExportService:
    def __init__(self):
        self.export_dir = Path("exports")
        self.export_dir.mkdir(exist_ok=True)
    
    async def create_html_portfolio(self, user_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> str:
        """Create a static HTML portfolio"""
        portfolio_html = self._generate_html_template(user_data, analysis_data)
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"portfolio_{user_data.get('github_username', 'user')}_{timestamp}.html"
        filepath = self.export_dir / filename
        
        # Write HTML file
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(portfolio_html)
        
        return str(filepath)
    
    async def create_react_portfolio(self, user_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> str:
        """Create a React portfolio (Vite project)"""
        portfolio_dir = self.export_dir / f"react_portfolio_{user_data.get('github_username', 'user')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        portfolio_dir.mkdir(exist_ok=True)
        
        # Create package.json
        package_json = {
            "name": f"portfolio-{user_data.get('github_username', 'user')}",
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "recharts": "^2.8.0",
                "lucide-react": "^0.294.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.43",
                "@types/react-dom": "^18.2.17",
                "@vitejs/plugin-react": "^4.2.1",
                "vite": "^5.0.8"
            }
        }
        
        async with aiofiles.open(portfolio_dir / "package.json", 'w') as f:
            await f.write(json.dumps(package_json, indent=2))
        
        # Create Vite config
        vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './'
})'''
        
        async with aiofiles.open(portfolio_dir / "vite.config.js", 'w') as f:
            await f.write(vite_config)
        
        # Create index.html
        index_html = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Developer Portfolio</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>'''
        
        async with aiofiles.open(portfolio_dir / "index.html", 'w') as f:
            await f.write(index_html)
        
        # Create src directory
        src_dir = portfolio_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create main.jsx
        main_jsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)'''
        
        async with aiofiles.open(src_dir / "main.jsx", 'w') as f:
            await f.write(main_jsx)
        
        # Create App.jsx
        app_jsx = self._generate_react_app(user_data, analysis_data)
        async with aiofiles.open(src_dir / "App.jsx", 'w') as f:
            await f.write(app_jsx)
        
        # Create index.css
        index_css = '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.skill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.skill-item {
  background: #f3f4f6;
  padding: 8px 16px;
  border-radius: 20px;
  text-align: center;
  font-weight: 500;
}

.job-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.job-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.company {
  color: #6b7280;
  margin-bottom: 8px;
}

.description {
  color: #4b5563;
  line-height: 1.5;
}'''
        
        async with aiofiles.open(src_dir / "index.css", 'w') as f:
            await f.write(index_css)
        
        return str(portfolio_dir)
    
    def _generate_html_template(self, user_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> str:
        """Generate HTML portfolio template"""
        skills = analysis_data.get('extracted_skills', [])
        job_matches = analysis_data.get('job_matches', [])
        
        skills_html = ""
        if skills:
            skills_html = '<div class="skills-grid">'
            for skill in skills[:20]:  # Limit to 20 skills
                skill_name = skill.get('name', str(skill)) if isinstance(skill, dict) else str(skill)
                skills_html += f'<div class="skill-item">{skill_name}</div>'
            skills_html += '</div>'
        
        jobs_html = ""
        if job_matches:
            for job in job_matches[:5]:  # Limit to 5 jobs
                jobs_html += f'''
                <div class="job-card">
                    <div class="job-title">{job.get('title', 'Unknown Position')}</div>
                    <div class="company">{job.get('company', 'Unknown Company')}</div>
                    <div class="description">{job.get('description', 'No description available')}</div>
                </div>
                '''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{user_data.get('github_username', 'Developer')} - Portfolio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .skill-item {{
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-align: center;
            font-weight: 500;
            margin: 4px;
            display: inline-block;
        }}
        .job-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #3b82f6;
        }}
    </style>
</head>
<body class="gradient-bg min-h-screen">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="text-center mb-12">
            <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl mx-auto">
                <img src="{user_data.get('avatar_url', '')}" alt="Profile" class="w-32 h-32 rounded-full mx-auto mb-6 border-4 border-blue-200">
                <h1 class="text-4xl font-bold text-gray-900 mb-2">{user_data.get('name', user_data.get('github_username', 'Developer'))}</h1>
                <p class="text-xl text-gray-600 mb-4">{user_data.get('bio', 'Full Stack Developer')}</p>
                <div class="flex justify-center space-x-6 text-gray-500">
                    <span><i class="fab fa-github mr-2"></i>GitHub: {user_data.get('github_username', 'N/A')}</span>
                    <span><i class="fas fa-code mr-2"></i>{len(analysis_data.get('selected_repos', []))} Repositories Analyzed</span>
                </div>
            </div>
        </div>

        <!-- Skills Section -->
        <div class="bg-white rounded-2xl shadow-2xl p-8 mb-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">Technical Skills</h2>
            {skills_html if skills_html else '<p class="text-gray-500 text-center">No skills data available</p>'}
        </div>

        <!-- Job Matches Section -->
        <div class="bg-white rounded-2xl shadow-2xl p-8 mb-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-6 text-center">Career Opportunities</h2>
            {jobs_html if jobs_html else '<p class="text-gray-500 text-center">No job matches available</p>'}
        </div>

        <!-- Footer -->
        <div class="text-center text-white">
            <p>Generated by DevProfile Generator on {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </div>
</body>
</html>'''
    
    def _generate_react_app(self, user_data: Dict[str, Any], analysis_data: Dict[str, Any]) -> str:
        """Generate React App component"""
        return f'''import React from 'react'
import {{ RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer }} from 'recharts'
import {{ Github, Code, Briefcase, Star }} from 'lucide-react'

function App() {{
  const skills = {json.dumps(analysis_data.get('extracted_skills', []))}
  const jobMatches = {json.dumps(analysis_data.get('job_matches', []))}
  
  // Prepare data for radar chart
  const skillCategories = {{
    'Programming Languages': skills.filter(s => typeof s === 'string' && ['Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'Go', 'Rust'].some(lang => s.includes(lang))).length,
    'Frameworks': skills.filter(s => typeof s === 'string' && ['React', 'Vue', 'Angular', 'Django', 'Flask', 'Express', 'Spring'].some(fw => s.includes(fw))).length,
    'Databases': skills.filter(s => typeof s === 'string' && ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite'].some(db => s.includes(db))).length,
    'Tools': skills.filter(s => typeof s === 'string' && ['Docker', 'Kubernetes', 'Git', 'AWS', 'Azure', 'GCP'].some(tool => s.includes(tool))).length,
    'Cloud Services': skills.filter(s => typeof s === 'string' && ['AWS', 'Azure', 'GCP', 'Heroku', 'Vercel', 'Netlify'].some(cloud => s.includes(cloud))).length
  }}
  
  const chartData = Object.entries(skillCategories).map(([category, value]) => ({{
    category,
    value: Math.min(value, 10) // Cap at 10 for better visualization
  }}))
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <!-- Header -->

        <div className="text-center mb-12">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-4xl mx-auto">
            <img 
              src="{user_data.get('avatar_url', '')}" 
              alt="Profile" 
              className="w-32 h-32 rounded-full mx-auto mb-6 border-4 border-blue-200"
            />
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              {user_data.get('name', user_data.get('github_username', 'Developer'))}
            </h1>
            <p className="text-xl text-gray-600 mb-4">{user_data.get('bio', 'Full Stack Developer')}</p>
            <div className="flex justify-center space-x-6 text-gray-500">
              <span className="flex items-center">
                <Github className="w-5 h-5 mr-2" />
                {user_data.get('github_username', 'N/A')}
              </span>
              <span className="flex items-center">
                <Code className="w-5 h-5 mr-2" />
                {len(analysis_data.get('selected_repos', []))} Repositories
              </span>
            </div>
          </div>
        </div>

        <!-- Skills Section -->

        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Technical Skills</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {{skills.slice(0, 24).map((skill, index) => (
              <div key={{index}} className="skill-item">
                {{typeof skill === 'string' ? skill : skill.name || 'Unknown'}}
              </div>
            ))}}
          </div>
        </div>

        <!-- Skills Chart -->

        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Skills Distribution</h2>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={{chartData}}>
                <PolarGrid />
                <PolarAngleAxis dataKey="category" />
                <PolarRadiusAxis angle={{90}} domain={{[0, 10]}} />
                <Radar
                  name="Skills"
                  dataKey="value"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={{0.3}}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <!-- Job Matches Section -->

        <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Career Opportunities</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {{jobMatches.slice(0, 4).map((job, index) => (
              <div key={{index}} className="job-card">
                <div className="flex items-center mb-3">
                  <Briefcase className="w-6 h-6 text-blue-600 mr-3" />
                  <h3 className="text-xl font-bold text-gray-900">{{job.title || 'Unknown Position'}}</h3>
                </div>
                <p className="text-blue-600 font-medium mb-2">{{job.company || 'Unknown Company'}}</p>
                <p className="text-gray-600 text-sm">{{job.description || 'No description available'}}</p>
                {{job.matched_skills && job.matched_skills.length > 0 && (
                  <div className="mt-3">
                    <p className="text-sm font-medium text-gray-700 mb-2">Matched Skills:</p>
                    <div className="flex flex-wrap gap-1">
                      {{job.matched_skills.slice(0, 3).map((skill, skillIndex) => (
                        <span key={{skillIndex}} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          {{skill}}
                        </span>
                      ))}}
                    </div>
                  </div>
                )}}
              </div>
            ))}}
          </div>
        </div>

        <!-- Footer -->

        <div className="text-center text-gray-600">
          <p>Generated by DevProfile Generator on {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
      </div>
    </div>
  )
}}

export default App'''
    
    async def create_zip_archive(self, portfolio_path: str) -> str:
        """Create a ZIP archive of the portfolio"""
        import zipfile
        
        zip_path = f"{portfolio_path}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isfile(portfolio_path):
                zipf.write(portfolio_path, os.path.basename(portfolio_path))
            else:
                for root, dirs, files in os.walk(portfolio_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, portfolio_path)
                        zipf.write(file_path, arcname)
        
        return zip_path

# Global instance
portfolio_service = PortfolioExportService()
