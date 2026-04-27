import re
import os
from typing import List, Set

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file."""
    if not PDF_AVAILABLE:
        return ""
    
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text.lower()
    except Exception:
        return ""


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file."""
    if not DOCX_AVAILABLE:
        return ""
    
    try:
        doc = docx.Document(file_path)
        text = " ".join([para.text for para in doc.paragraphs])
        return text.lower()
    except Exception:
        return ""


def extract_resume_text(resume_path: str) -> str:
    """Extract text from resume file (PDF or DOCX)."""
    if not resume_path or not os.path.exists(resume_path):
        return ""
    
    ext = os.path.splitext(resume_path)[1].lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(resume_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(resume_path)
    else:
        # Try to read as plain text
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                return f.read().lower()
        except Exception:
            return ""


def clean_text(text: str) -> Set[str]:
    """Clean and tokenize text into words."""
    # Remove special characters and split into words
    words = re.findall(r'\b[a-zA-Z0-9+#]+\b', text.lower())
    return set(words)


def calculate_ats_score(seeker_profile, job) -> float:
    """
    Calculate ATS score based on:
    - Skills match (40%)
    - Resume keyword match (30%)
    - Experience match (20%)
    - Education keywords (10%)
    """
    score = 0.0
    
    # 1. Skills Match (40 points max)
    job_skills = set(job.get_skills_list())
    seeker_skills = set(seeker_profile.get_skills_list())
    
    if job_skills:
        skills_match = len(job_skills & seeker_skills) / len(job_skills)
        score += skills_match * 40
    
    # 2. Resume Keyword Match (30 points max)
    if seeker_profile.resume:
        try:
            resume_text = extract_resume_text(seeker_profile.resume.path)
            resume_words = clean_text(resume_text)
            
            # Check job description keywords in resume
            job_words = clean_text(job.description + " " + job.required_skills)
            
            if job_words:
                keyword_match = len(job_words & resume_words) / len(job_words)
                score += min(keyword_match * 50, 30)  # Cap at 30
        except Exception:
            pass
    
    # 3. Experience Match (20 points max)
    if seeker_profile.experience_years >= job.experience_required:
        score += 20
    elif job.experience_required > 0:
        exp_ratio = seeker_profile.experience_years / job.experience_required
        score += min(exp_ratio * 20, 15)  # Partial credit, max 15
    
    # 4. Location Match (10 points max)
    if seeker_profile.location and job.location:
        if seeker_profile.location.lower() in job.location.lower() or \
           job.location.lower() in seeker_profile.location.lower():
            score += 10
        elif 'remote' in job.location.lower():
            score += 10
    
    return round(score, 2)


def rank_applications(applications):
    """
    Rank applications by ATS score.
    Returns list of applications sorted by score descending.
    """
    scored_apps = []
    
    for app in applications:
        app.ats_score = calculate_ats_score(app.seeker, app.job)
        app.save(update_fields=['ats_score'])
        scored_apps.append(app)
    
    return sorted(scored_apps, key=lambda x: x.ats_score, reverse=True)
