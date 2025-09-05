from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import Dict, List, Any
import os
from datetime import datetime
import io

class PDFExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2563eb')
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#1d4ed8')
        ))
        
        # Section style
        self.styles.add(ParagraphStyle(
            name='CustomSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#1e40af')
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
    
    def create_skills_analysis_pdf(self, analysis_data: Dict[str, Any], output_path: str) -> str:
        """Create a PDF for skills analysis"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("DevProfile Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # User info
        story.append(Paragraph("Profile Information", self.styles['CustomSubtitle']))
        user_info = [
            ["GitHub Username:", analysis_data.get('github_username', 'N/A')],
            ["Analysis Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Repositories Analyzed:", str(len(analysis_data.get('selected_repos', [])))]
        ]
        
        user_table = Table(user_info, colWidths=[2*inch, 4*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ]))
        
        story.append(user_table)
        story.append(Spacer(1, 20))
        
        # Skills section
        story.append(Paragraph("Extracted Skills", self.styles['CustomSubtitle']))
        skills = analysis_data.get('extracted_skills', [])
        
        if skills:
            # Create skills table
            skills_data = [["Skill", "Category", "Proficiency"]]
            for skill in skills[:20]:  # Limit to first 20 skills
                if isinstance(skill, dict):
                    skills_data.append([
                        skill.get('name', 'Unknown'),
                        skill.get('category', 'Other'),
                        str(skill.get('proficiency_level', 'N/A'))
                    ])
                else:
                    skills_data.append([str(skill), 'Other', 'N/A'])
            
            skills_table = Table(skills_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            skills_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(skills_table)
        else:
            story.append(Paragraph("No skills were extracted from the analysis.", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        # Job matches section
        story.append(Paragraph("Job Matches", self.styles['CustomSubtitle']))
        job_matches = analysis_data.get('job_matches', [])
        
        if job_matches:
            for i, job in enumerate(job_matches[:5], 1):  # Limit to first 5 jobs
                story.append(Paragraph(f"{i}. {job.get('title', 'Unknown Position')}", self.styles['CustomSection']))
                story.append(Paragraph(f"Company: {job.get('company', 'N/A')}", self.styles['CustomBody']))
                story.append(Paragraph(f"Description: {job.get('description', 'No description available')}", self.styles['CustomBody']))
                
                matched_skills = job.get('matched_skills', [])
                if matched_skills:
                    skills_text = ", ".join(matched_skills[:5])  # Limit to first 5 skills
                    story.append(Paragraph(f"Matched Skills: {skills_text}", self.styles['CustomBody']))
                
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("No job matches found.", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        # Skill suggestions section
        story.append(Paragraph("Learning Recommendations", self.styles['CustomSubtitle']))
        suggestions = analysis_data.get('skill_suggestions', [])
        
        if suggestions:
            for i, suggestion in enumerate(suggestions[:5], 1):  # Limit to first 5 suggestions
                story.append(Paragraph(f"{i}. {suggestion.get('skill_name', 'Unknown Skill')}", self.styles['CustomSection']))
                story.append(Paragraph(f"Reason: {suggestion.get('reason', 'No reason provided')}", self.styles['CustomBody']))
                story.append(Paragraph(f"Difficulty: {suggestion.get('difficulty', 'Unknown')}", self.styles['CustomBody']))
                story.append(Paragraph(f"Estimated Time: {suggestion.get('estimated_time', 'Unknown')}", self.styles['CustomBody']))
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("No learning recommendations available.", self.styles['CustomBody']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated by DevProfile Generator", self.styles['CustomBody']))
        story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def create_portfolio_pdf(self, portfolio_data: Dict[str, Any], output_path: str) -> str:
        """Create a PDF portfolio"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("Developer Portfolio", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Personal info
        story.append(Paragraph("About Me", self.styles['CustomSubtitle']))
        story.append(Paragraph(f"GitHub: {portfolio_data.get('github_username', 'N/A')}", self.styles['CustomBody']))
        story.append(Paragraph(f"Bio: {portfolio_data.get('bio', 'No bio available')}", self.styles['CustomBody']))
        story.append(Spacer(1, 20))
        
        # Skills
        story.append(Paragraph("Technical Skills", self.styles['CustomSubtitle']))
        skills = portfolio_data.get('skills', [])
        
        if skills:
            skills_text = ", ".join([skill.get('name', str(skill)) for skill in skills[:15]])
            story.append(Paragraph(skills_text, self.styles['CustomBody']))
        else:
            story.append(Paragraph("No skills listed.", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        # Projects
        story.append(Paragraph("Featured Projects", self.styles['CustomSubtitle']))
        projects = portfolio_data.get('projects', [])
        
        if projects:
            for i, project in enumerate(projects[:5], 1):
                story.append(Paragraph(f"{i}. {project.get('name', 'Unknown Project')}", self.styles['CustomSection']))
                story.append(Paragraph(f"Description: {project.get('description', 'No description')}", self.styles['CustomBody']))
                story.append(Paragraph(f"Language: {project.get('language', 'N/A')}", self.styles['CustomBody']))
                story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("No projects available.", self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        return output_path
    
    def get_pdf_bytes(self, analysis_data: Dict[str, Any], pdf_type: str = "analysis") -> bytes:
        """Get PDF as bytes for API response"""
        buffer = io.BytesIO()
        
        if pdf_type == "analysis":
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = self._build_analysis_story(analysis_data)
        else:
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = self._build_portfolio_story(analysis_data)
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _build_analysis_story(self, analysis_data: Dict[str, Any]) -> List:
        """Build story for analysis PDF"""
        story = []
        
        # Title
        story.append(Paragraph("DevProfile Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Add content similar to create_skills_analysis_pdf
        # ... (implementation details)
        
        return story
    
    def _build_portfolio_story(self, portfolio_data: Dict[str, Any]) -> List:
        """Build story for portfolio PDF"""
        story = []
        
        # Title
        story.append(Paragraph("Developer Portfolio", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Add content similar to create_portfolio_pdf
        # ... (implementation details)
        
        return story

# Global instance
pdf_service = PDFExportService()
