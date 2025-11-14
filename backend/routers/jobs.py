"""
Jobs API Router - IMPROVED VERSION
- Lower match thresholds
- Better keyword flexibility
- More results returned
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from database.db import get_db
from database.models import Job, Resume, User, JobPreference
from scrapers.enhanced_multi_scraper import EnhancedMultiScraper
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()

class MultiScraperConcrete(EnhancedMultiScraper):
    def parse_job_listing(self, html):
        # Minimal implementation
        return {}  # Return empty dict just to satisfy the abstract requirement


# Initialize scraper
multi_scraper = MultiScraperConcrete()

# Try to load NLP matcher (optional)
try:
    from parsers.nlp_matcher import JobMatcher
    job_matcher = JobMatcher()
    print("✅ NLP job matcher loaded")
except Exception as e:
    print(f"⚠️  NLP matcher unavailable: {e}")
    job_matcher = None

class JobSearchRequest(BaseModel):
    user_id: int
    keywords: List[str]
    location: Optional[str] = None
    remote_only: bool = False
    limit: int = 50
    sources: List[str] = ["all"]

@router.post("/search")
async def search_jobs(
    request: JobSearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Search for jobs - RELAXED FILTERING VERSION
    Returns more jobs with lower match thresholds
    """
    logger.info(f"Searching jobs with keywords: {request.keywords}")
    
    # Get user's resume for matching
    resume = db.query(Resume).filter(
        Resume.user_id == request.user_id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found. Please upload your resume first.")
    
    # Prepare resume data for matching
    resume_data = {
        'skills': resume.skills or [],
        'experience': resume.experience or [],
        'raw_text': resume.raw_text or '',
        'education': resume.education or []
    }
    
    try:
        # Search jobs using multi-scraper with HIGHER limit
        logger.info("Searching multiple job sources...")
        all_jobs = multi_scraper.search_jobs(
            keywords=request.keywords,
            location=request.location,
            remote_only=request.remote_only,
            limit=request.limit * 3  # Get 3x more jobs initially
        )
        
        logger.info(f"Found {len(all_jobs)} total jobs")
        
        if len(all_jobs) == 0:
            return {
                'success': True,
                'total_found': 0,
                'jobs': [],
                'message': 'No jobs found. Try different keywords or remove location filter.'
            }
        
        # Calculate match scores for each job
        jobs_with_scores = []
        for job in all_jobs:
            try:
                # Calculate match score using NLP if available
                if job_matcher:
                    score = job_matcher.compute_match_score(
                        resume_data,
                        job.get('description', ''),
                        job.get('requirements', '')
                    )
                else:
                    # Simple keyword-based scoring if NLP unavailable
                    score = calculate_simple_match(resume_data, job)
                
                job['match_score'] = score
                jobs_with_scores.append(job)
                
            except Exception as e:
                logger.error(f"Error matching job: {e}")
                # Still include the job with a default score
                job['match_score'] = 25.0  # Default moderate score
                jobs_with_scores.append(job)
        
        # Sort by match score (highest first)
        jobs_with_scores.sort(key=lambda x: x['match_score'], reverse=True)
        
        # MUCH LOWER THRESHOLD: Only filter out obviously bad matches
        min_score = 10.0  # Lowered from 30 to 10 - only exclude terrible matches
        quality_jobs = [j for j in jobs_with_scores if j['match_score'] >= min_score]
        
        if len(quality_jobs) == 0:
            logger.warning("All jobs filtered out - returning unfiltered results")
            # Return ALL jobs if filtering is too strict
            quality_jobs = jobs_with_scores
        
        logger.info(f"After filtering: {len(quality_jobs)} jobs (min score: {min_score})")
        
        # Save to database
        saved_jobs = []
        for job_data in quality_jobs[:request.limit]:
            # Check if job already exists
            existing = db.query(Job).filter(
                Job.external_id == job_data['external_id']
            ).first()
            
            if not existing:
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data['location'],
                    description=job_data['description'],
                    requirements=job_data['requirements'],
                    salary_min=job_data.get('salary_min'),
                    salary_max=job_data.get('salary_max'),
                    is_remote=job_data['is_remote'],
                    source=job_data['source'],
                    external_id=job_data['external_id'],
                    url=job_data['url'],
                    application_url=job_data['application_url'],
                    easy_apply=job_data['easy_apply'],
                    posted_date=job_data.get('posted_date')
                )
                db.add(job)
                db.commit()
                db.refresh(job)
                saved_jobs.append({
                    'id': job.id,
                    **job_data
                })
            else:
                saved_jobs.append({
                    'id': existing.id,
                    **job_data
                })
        
        return {
            'success': True,
            'total_found': len(all_jobs),
            'quality_matches': len(quality_jobs),
            'jobs': saved_jobs[:request.limit],
            'message': f'Found {len(quality_jobs)} jobs (showing top {len(saved_jobs[:request.limit])} matches)'
        }
    
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def calculate_simple_match(resume_data: Dict, job: Dict) -> float:
    """
    IMPROVED: More lenient keyword-based matching
    Returns score 0-100
    """
    score = 30.0  # Start with base score so jobs aren't eliminated immediately
    
    # Get resume skills (lowercase)
    resume_skills = [s.lower() for s in resume_data.get('skills', [])]
    
    # Get job text (lowercase)
    job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('requirements', '')}".lower()
    
    # Count skill matches with partial matching
    matched_skills = 0
    for skill in resume_skills:
        skill_parts = skill.split()  # Split multi-word skills
        for part in skill_parts:
            if len(part) > 2 and part in job_text:  # Match any part of skill
                matched_skills += 1
                break  # Only count once per skill
    
    if resume_skills:
        # Score based on percentage of skills matched (more lenient)
        skill_score = (matched_skills / len(resume_skills)) * 50  # Max 50 points
        score += skill_score
    else:
        # If no skills in resume, give neutral score
        score = 50.0
    
    # Check for job level keywords (more lenient)
    job_text_lower = job_text.lower()
    
    # Small bonus for entry-level/junior positions
    if any(term in job_text_lower for term in ['junior', 'entry level', 'entry-level', 'graduate', 'associate']):
        score += 10
    
    # Small penalty for very senior positions (not elimination)
    if any(term in job_text_lower for term in ['senior', 'sr.', 'sr ', 'lead', 'principal', 'staff', 'architect', 'director']):
        score -= 5  # Reduced from 20 to 5
    
    # Check for experience level match
    experience_years = len(resume_data.get('experience', []))
    
    # Bonus if experience aligns
    if experience_years < 3 and 'junior' in job_text_lower:
        score += 15
    elif 3 <= experience_years < 7 and any(term in job_text_lower for term in ['mid', 'intermediate', 'experienced']):
        score += 15
    
    # Bonus for keyword presence in title (strong signal)
    title_lower = job.get('title', '').lower()
    for skill in resume_skills[:5]:  # Check top 5 skills
        if skill in title_lower:
            score += 10
            break
    
    # Normalize score to 0-100
    score = max(0, min(100, score))
    
    return round(score, 2)

@router.get("/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)) -> Dict:
    """Get job details"""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        'id': job.id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'description': job.description,
        'requirements': job.requirements,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'is_remote': job.is_remote,
        'url': job.url,
        'application_url': job.application_url,
        'easy_apply': job.easy_apply,
        'source': job.source,
        'posted_date': job.posted_date.isoformat() if job.posted_date else None
    }

@router.get("/user/{user_id}/matches")
async def get_matched_jobs(
    user_id: int,
    min_score: float = 20.0,  # Lowered from 60 to 20
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Dict:
    """Get jobs that match user's resume with score above threshold"""
    # Get more jobs from database
    jobs = db.query(Job).limit(200).all()
    
    # Get user's resume
    resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")
    
    resume_data = {
        'skills': resume.skills or [],
        'experience': resume.experience or [],
        'raw_text': resume.raw_text
    }
    
    # Match and filter
    matched_jobs = []
    for job in jobs:
        if job_matcher:
            score = job_matcher.compute_match_score(
                resume_data,
                job.description or '',
                job.requirements or ''
            )
        else:
            job_dict = {
                'title': job.title,
                'description': job.description,
                'requirements': job.requirements
            }
            score = calculate_simple_match(resume_data, job_dict)
        
        if score >= min_score:
            matched_jobs.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'match_score': score,
                'url': job.url,
                'is_remote': job.is_remote,
                'easy_apply': job.easy_apply
            })
    
    # Sort by score
    matched_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    return {
        'total_matches': len(matched_jobs),
        'jobs': matched_jobs[:limit]
    }