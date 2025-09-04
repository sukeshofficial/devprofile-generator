"""
PDF generation service using WeasyPrint

Converts HTML resume templates to ATS-friendly PDF documents
using Jinja2 templating and WeasyPrint rendering.
"""

import os
import tempfile
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader
import weasyprint
from datetime import datetime

class PDFGenerator:
    """PDF generator for ATS-friendly resumes"""
    
    def __init__(self):
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    async def generate_resume_html(
        self, 
        profile: Dict[str, Any], 
        bullets: List[Dict[str, Any]], 
        skills: List[str]
    ) -> str:
        """
        Generate HTML resume from template
        
        Args:
            profile: User profile information
            bullets: Resume bullet points
            skills: Technical skills list
            
        Returns:
            Rendered HTML content
        """
        template = self.jinja_env.get_template("resume.html")
        
        # Organize bullets by project
        projects = {}
        for bullet in bullets:
            project_name = bullet.get("project", "Other")
            if project_name not in projects:
                projects[project_name] = []
            projects[project_name].append(bullet)
        
        # Prepare template context
        context = {
            "profile": profile,
            "projects": projects,
            "skills": skills,
            "generated_date": datetime.now().strftime("%B %Y")
        }
        
        return template.render(**context)
    
    async def generate_resume_pdf(
        self, 
        profile: Dict[str, Any], 
        bullets: List[Dict[str, Any]], 
        skills: List[str]
    ) -> str:
        """
        Generate PDF resume from HTML template
        
        Args:
            profile: User profile information
            bullets: Resume bullet points
            skills: Technical skills list
            
        Returns:
            Path to generated PDF file
        """
        # Generate HTML content
        html_content = await self.generate_resume_html(profile, bullets, skills)
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf_path = tmp_file.name
        
        try:
            # Generate PDF using WeasyPrint
            html_doc = weasyprint.HTML(string=html_content)
            html_doc.write_pdf(pdf_path)
            
            return pdf_path
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary PDF file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # Ignore cleanup errors