"""
Portfolio generator service for Next.js/TypeScript projects

Creates downloadable zip files containing complete Next.js portfolio
websites generated from user profile data.
"""

import os
import tempfile
import zipfile
from typing import Dict, Any
from app.services.openrouter_client import OpenRouterClient

class PortfolioGenerator:
    """Generator for Next.js TypeScript portfolio projects"""
    
    def __init__(self):
        self.openrouter = OpenRouterClient()
    
    async def generate_portfolio_zip(self, profile: Dict[str, Any]) -> str:
        """
        Generate complete Next.js portfolio as zip file
        
        Args:
            profile: User profile and project data
            
        Returns:
            Path to generated zip file
        """
        # Get AI-generated portfolio structure
        portfolio_data = await self._generate_portfolio_structure(profile)
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            portfolio_dir = os.path.join(temp_dir, "portfolio")
            os.makedirs(portfolio_dir)
            
            # Create Next.js project structure
            await self._create_nextjs_structure(portfolio_dir, portfolio_data, profile)
            
            # Create zip file
            zip_path = tempfile.mktemp(suffix=".zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(portfolio_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_name)
            
            return zip_path
    
    async def _generate_portfolio_structure(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate portfolio structure using AI"""
        system_prompt = (
            "You are an assistant that must OUTPUT ONLY valid JSON following the specified schema. "
            "Do not include any prose or extra fields."
        )
        
        user_prompt = f"""
        Generate a minimal Next.js TypeScript portfolio structure for this developer profile.
        
        Profile: {profile}
        
        Output JSON schema:
        {{
            "site_name": "string",
            "pages": [
                {{"path": "string", "content": "string"}}
            ],
            "static_assets": [{{"path":"string","content_base64":"string"}}]
        }}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            return await self.openrouter._make_request(messages)
        except Exception:
            # Fallback to basic structure
            return {
                "site_name": f"{profile.get('name', 'Developer')} Portfolio",
                "pages": [
                    {"path": "pages/index.tsx", "content": self._get_default_index_page(profile)},
                    {"path": "pages/_app.tsx", "content": self._get_default_app_page()},
                ],
                "static_assets": []
            }
    
    async def _create_nextjs_structure(self, portfolio_dir: str, portfolio_data: Dict, profile: Dict):
        """Create Next.js project files"""
        
        # Create package.json
        package_json = {
            "name": portfolio_data.get("site_name", "portfolio").lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.0.0",
                "react": "^18",
                "react-dom": "^18",
                "typescript": "^5",
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18"
            }
        }
        
        with open(os.path.join(portfolio_dir, "package.json"), "w") as f:
            import json
            json.dump(package_json, f, indent=2)
        
        # Create tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "es6"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "forceConsistentCasingInFileNames": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./src/*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        
        with open(os.path.join(portfolio_dir, "tsconfig.json"), "w") as f:
            import json
            json.dump(tsconfig, f, indent=2)
        
        # Create next.config.js
        next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
"""
        with open(os.path.join(portfolio_dir, "next.config.js"), "w") as f:
            f.write(next_config)
        
        # Create pages directory
        pages_dir = os.path.join(portfolio_dir, "pages")
        os.makedirs(pages_dir, exist_ok=True)
        
        # Create pages from AI-generated content
        for page in portfolio_data.get("pages", []):
            page_path = os.path.join(portfolio_dir, page["path"])
            os.makedirs(os.path.dirname(page_path), exist_ok=True)
            
            with open(page_path, "w") as f:
                f.write(page["content"])
        
        # Create README
        readme_content = f"""# {portfolio_data.get('site_name', 'Portfolio')}

A Next.js portfolio website generated by DevProfile.

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the portfolio.

## Deployment

Deploy to Vercel:

```bash
npm install -g vercel
vercel --prod
```

Generated on {datetime.now().strftime('%Y-%m-%d')} by DevProfile Resume Automator.
"""
        
        with open(os.path.join(portfolio_dir, "README.md"), "w") as f:
            f.write(readme_content)
    
    def _get_default_index_page(self, profile: Dict) -> str:
        """Generate default index page content"""
        return f"""import React from 'react';
import Head from 'next/head';

export default function Home() {{
  return (
    <div>
      <Head>
        <title>{profile.get('name', 'Developer')} - Portfolio</title>
        <meta name="description" content="Portfolio of {profile.get('name', 'Developer')}" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              {profile.get('name', 'Developer')}
            </h1>
            <p className="text-xl text-gray-600">
              Full Stack Developer
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-4">About Me</h2>
            <p className="text-gray-700 leading-relaxed">
              Passionate developer with experience in modern web technologies.
              Check out my GitHub profile for more projects and contributions.
            </p>
            
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Connect</h3>
              <div className="flex space-x-4">
                <a 
                  href="{profile.get('github_url', '#')}"
                  className="text-blue-600 hover:text-blue-800"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  GitHub
                </a>
                <a 
                  href="{profile.get('linkedin_url', '#')}"
                  className="text-blue-600 hover:text-blue-800"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  LinkedIn
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}}
"""
    
    def _get_default_app_page(self) -> str:
        """Generate default _app.tsx content"""
        return """import type { AppProps } from 'next/app';
import '../styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}
"""