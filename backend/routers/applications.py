"""
Applications API Router - FIXED CSV FORMAT
Generates Gmail Merge compatible CSV with clean single emails
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
import csv
import io
import re

from database.db import get_db
from database.models import JobApplication, Job, User, Resume
from automation.bulk_email_applicator import BulkEmailApplicator
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()

class ApplyRequest(BaseModel):
    user_id: int
    job_id: int
    auto_apply: bool = True

class BulkApplyRequest(BaseModel):
    user_id: int
    job_ids: List[int]

@router.post("/apply")
async def apply_to_job(
    request: ApplyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict:
    """Apply to a single job"""
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    resume = db.query(Resume).filter(
        Resume.user_id == request.user_id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")
    
    # Check if already applied
    existing = db.query(JobApplication).filter(
        JobApplication.user_id == request.user_id,
        JobApplication.job_id == request.job_id
    ).first()
    
    if existing:
        return {
            'success': False,
            'message': 'Already applied to this job',
            'application_id': existing.id
        }
    
    # Create application record
    application = JobApplication(
        user_id=request.user_id,
        job_id=request.job_id,
        status='pending',
        application_method='automated' if request.auto_apply else 'manual'
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    
    # Auto-apply: Generate email template
    if request.auto_apply:
        user_data = {
            'name': resume.parsed_name or user.name,
            'email': resume.parsed_email or user.email,
            'phone': resume.parsed_phone or user.phone,
            'top_skills': resume.skills[:7] if resume.skills else []
        }
        
        job_dict = {
            'title': job.title,
            'company': job.company,
            'url': job.url,
            'description': job.description
        }
        
        background_tasks.add_task(
            submit_application_universal,
            application.id,
            job_dict,
            user_data,
            resume.file_path
        )
        
        return {
            'success': True,
            'message': 'Application email generated!',
            'application_id': application.id,
            'status': 'pending',
            'application_url': job.application_url or job.url
        }
    
    return {
        'success': True,
        'message': 'Application created',
        'application_id': application.id,
        'application_url': job.application_url or job.url
    }

def submit_application_universal(
    application_id: int,
    job_dict: Dict,
    user_data: Dict,
    resume_path: str
):
    """Generate email template with CLEAN single email"""
    from database.db import SessionLocal
    
    db = SessionLocal()
    
    try:
        logger.info(f"Generating application email for application {application_id}")
        
        # Generate email using FIXED bulk email applicator
        email_generator = BulkEmailApplicator()
        email_data = email_generator.generate_application_email(
            job_dict,
            user_data,
            resume_path
        )
        
        # Update application with email template
        app = db.query(JobApplication).filter(
            JobApplication.id == application_id
        ).first()
        
        if app:
            # Store CLEAN email template
            app.response_data = {
                'email_generated': True,
                'email_subject': email_data['subject'],
                'email_body': email_data['body'],
                'to_email': email_data['to'],  # NOW SINGLE CLEAN EMAIL
                'generated_at': datetime.utcnow().isoformat()
            }
            
            app.status = 'email_ready'
            app.success = True
            app.applied_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"Application {application_id}: Email template generated successfully")
    
    except Exception as e:
        logger.error(f"Error generating application email {application_id}: {e}")
        
        app = db.query(JobApplication).filter(
            JobApplication.id == application_id
        ).first()
        
        if app:
            app.status = 'failed'
            app.success = False
            app.error_message = str(e)
            db.commit()
    
    finally:
        db.close()

@router.post("/bulk-apply")
async def bulk_apply(
    request: BulkApplyRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict:
    """Apply to multiple jobs - Generates email templates"""
    results = []
    
    for job_id in request.job_ids:
        try:
            result = await apply_to_job(
                ApplyRequest(user_id=request.user_id, job_id=job_id),
                background_tasks,
                db
            )
            results.append({
                'job_id': job_id,
                **result
            })
        except Exception as e:
            results.append({
                'job_id': job_id,
                'success': False,
                'error': str(e)
            })
    
    return {
        'total_applications': len(results),
        'results': results,
        'message': f'Generated email templates for {len(results)} jobs!'
    }

@router.get("/user/{user_id}")
async def get_user_applications(
    user_id: int,
    status: str = None,
    db: Session = Depends(get_db)
) -> Dict:
    """Get all applications for a user"""
    query = db.query(JobApplication).filter(JobApplication.user_id == user_id)
    
    if status:
        query = query.filter(JobApplication.status == status)
    
    applications = query.order_by(JobApplication.created_at.desc()).all()
    
    results = []
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        results.append({
            'id': app.id,
            'job_id': app.job_id,
            'job_title': job.title if job else 'Unknown',
            'company': job.company if job else 'Unknown',
            'status': app.status,
            'match_score': app.match_score,
            'applied_at': app.applied_at.isoformat() if app.applied_at else None,
            'success': app.success,
            'error_message': app.error_message,
            'created_at': app.created_at.isoformat(),
            'email_data': app.response_data if app.status == 'email_ready' else None
        })
    
    return {
        'total': len(results),
        'applications': results
    }

@router.get("/export-csv/{user_id}")
async def export_applications_csv(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Export applications as CSV for Gmail Merge
    FIXED: Clean single emails, no brackets or multiple addresses
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")
    
    # Get pending/ready applications
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == user_id,
        JobApplication.status.in_(['pending', 'email_ready'])
    ).all()
    
    if not applications:
        raise HTTPException(status_code=404, detail="No pending applications to export")
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # GMAIL MERGE COMPATIBLE HEADERS
    writer.writerow([
        'Company',
        'Job Title',
        'To Email',
        'Subject',
        'Message Body',
        'Job URL',
        'Application ID',
        'Your Name',
        'Your Email',
        'Your Phone'
    ])
    
    user_data = {
        'name': resume.parsed_name or user.name,
        'email': resume.parsed_email or user.email,
        'phone': resume.parsed_phone or user.phone,
        'top_skills': resume.skills[:7] if resume.skills else []
    }
    
    email_generator = BulkEmailApplicator()
    
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if not job:
            continue
        
        # Generate or retrieve email data
        if app.response_data and app.response_data.get('email_generated'):
            to_email = app.response_data['to_email']
            subject = app.response_data['email_subject']
            body = app.response_data['email_body']
        else:
            # Generate new email with FIXED format
            job_dict = {
                'title': job.title,
                'company': job.company,
                'url': job.url,
                'description': job.description
            }
            
            email_data = email_generator.generate_application_email(
                job_dict,
                user_data,
                resume.file_path
            )
            
            to_email = email_data['to']  # NOW SINGLE CLEAN EMAIL
            subject = email_data['subject']
            body = email_data['body']
        
        # Write row with CLEAN data
        writer.writerow([
            job.company,
            job.title,
            to_email,  # SINGLE CLEAN EMAIL (e.g. careers@company.com)
            subject,
            body,
            job.url,
            app.id,
            user_data['name'],
            user_data['email'],
            user_data['phone']
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=job_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )

@router.get("/export-emails/{user_id}")
async def export_email_templates(
    user_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """Generate email templates for all pending applications"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.is_active == True
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")
    
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == user_id,
        JobApplication.status.in_(['pending', 'email_ready'])
    ).all()
    
    if not applications:
        return {
            'success': False,
            'message': 'No applications found',
            'emails': []
        }
    
    user_data = {
        'name': resume.parsed_name or user.name,
        'email': resume.parsed_email or user.email,
        'phone': resume.parsed_phone or user.phone,
        'top_skills': resume.skills[:7] if resume.skills else []
    }
    
    email_generator = BulkEmailApplicator()
    emails = []
    
    for app in applications:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        if job:
            if app.response_data and app.response_data.get('email_generated'):
                email_data = {
                    'to': app.response_data['to_email'],  # CLEAN EMAIL
                    'subject': app.response_data['email_subject'],
                    'body': app.response_data['email_body'],
                    'job_title': job.title,
                    'company': job.company,
                    'job_url': job.url
                }
            else:
                job_dict = {
                    'title': job.title,
                    'company': job.company,
                    'url': job.url,
                    'description': job.description
                }
                
                email_data = email_generator.generate_application_email(
                    job_dict,
                    user_data,
                    resume.file_path
                )
            
            emails.append({
                'application_id': app.id,
                'job_id': job.id,
                **email_data
            })
    
    return {
        'success': True,
        'total': len(emails),
        'emails': emails
    }

@router.post("/mark-emailed/{application_id}")
async def mark_application_emailed(
    application_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """Mark an application as emailed"""
    
    app = db.query(JobApplication).filter(
        JobApplication.id == application_id
    ).first()
    
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app.status = 'applied'
    app.application_method = 'email'
    app.applied_at = datetime.utcnow()
    app.success = True
    
    db.commit()
    
    return {
        'success': True,
        'message': 'Application marked as emailed',
        'application_id': application_id
    }