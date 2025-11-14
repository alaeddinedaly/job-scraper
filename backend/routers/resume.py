"""
Resume API Router
Endpoints for uploading and parsing resumes
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
import os
from pathlib import Path
import shutil

from database.db import get_db
from database.models import User, Resume
from parsers.resume_parser import ResumeParser
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger()
parser = ResumeParser()

UPLOAD_DIR = Path("../data/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload and parse a resume
    """
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.doc'}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Resume uploaded: {file.filename}")

        # Parse resume
        parsed_data = parser.parse_file(str(file_path))
        logger.info(f"Resume parsed successfully")

        # Get or create user
        user = db.query(User).filter(
            User.email == parsed_data.get('email')
        ).first()

        if not user:
            user = User(
                name=parsed_data.get('name'),
                email=parsed_data.get('email'),
                phone=parsed_data.get('phone')
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Save resume record
        resume = Resume(
            user_id=user.id,
            filename=file.filename,
            file_path=str(file_path),
            raw_text=parsed_data.get('raw_text'),
            parsed_name=parsed_data.get('name'),
            parsed_email=parsed_data.get('email'),
            parsed_phone=parsed_data.get('phone'),
            skills=parsed_data.get('skills'),
            experience=parsed_data.get('experience'),
            education=parsed_data.get('education'),
            is_active=True
        )

        db.add(resume)
        db.commit()
        db.refresh(resume)

        return {
            'success': True,
            'message': 'Resume uploaded and parsed successfully',
            'resume_id': resume.id,
            'user_id': user.id,
            'parsed_data': {
                'name': parsed_data.get('name'),
                'email': parsed_data.get('email'),
                'phone': parsed_data.get('phone'),
                'skills': parsed_data.get('skills', []),
                'num_experiences': len(parsed_data.get('experience', [])),
                'num_education': len(parsed_data.get('education', []))
            }
        }

    except Exception as e:
        logger.error(f"Error processing resume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_resume(user_id: int, db: Session = Depends(get_db)) -> Dict:
    """Get user's active resume"""
    resume = db.query(Resume).filter(
        Resume.user_id == user_id,
        Resume.is_active == True
    ).first()

    if not resume:
        raise HTTPException(status_code=404, detail="No active resume found")

    return {
        'id': resume.id,
        'filename': resume.filename,
        'name': resume.parsed_name,
        'email': resume.parsed_email,
        'phone': resume.parsed_phone,
        'skills': resume.skills,
        'experience': resume.experience,
        'education': resume.education,
        'uploaded_at': resume.uploaded_at.isoformat()
    }

@router.delete("/{resume_id}")
async def delete_resume(resume_id: int, db: Session = Depends(get_db)) -> Dict:
    """Delete a resume"""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete file
    try:
        os.remove(resume.file_path)
    except:
        pass

    # Delete from database
    db.delete(resume)
    db.commit()

    return {'success': True, 'message': 'Resume deleted'}