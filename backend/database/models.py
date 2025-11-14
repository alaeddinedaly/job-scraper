"""
Database Models for AutoJobApply
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User profile"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50))
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user")
    preferences = relationship("JobPreference", back_populates="user", uselist=False)
    applications = relationship("JobApplication", back_populates="user")

class Resume(Base):
    """Parsed resume data"""
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    file_path = Column(String(500))
    raw_text = Column(Text)

    # Parsed fields
    parsed_name = Column(String(255))
    parsed_email = Column(String(255))
    parsed_phone = Column(String(50))
    skills = Column(JSON)  # List of skills
    experience = Column(JSON)  # List of work experiences
    education = Column(JSON)  # List of education entries

    # Metadata
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="resumes")

class JobPreference(Base):
    """User job search preferences"""
    __tablename__ = "job_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    # Search criteria
    job_titles = Column(JSON)  # List of desired job titles
    keywords = Column(JSON)  # List of keywords
    locations = Column(JSON)  # List of preferred locations
    remote_only = Column(Boolean, default=False)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)

    # Job boards to search
    search_indeed = Column(Boolean, default=True)
    search_remoteok = Column(Boolean, default=True)
    search_wellfound = Column(Boolean, default=True)

    # Auto-apply settings
    auto_apply_enabled = Column(Boolean, default=False)
    min_match_score = Column(Float, default=60.0)  # Minimum match percentage

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preferences")

class Job(Base):
    """Job listing from various sources"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    # Job details
    title = Column(String(500))
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    requirements = Column(Text)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    is_remote = Column(Boolean, default=False)

    # Source information
    source = Column(String(50))  # indeed, remoteok, wellfound
    external_id = Column(String(255), unique=True, index=True)
    url = Column(String(1000))

    # Application metadata
    application_url = Column(String(1000))
    easy_apply = Column(Boolean, default=False)

    # Timestamps
    posted_date = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    applications = relationship("JobApplication", back_populates="job")

class JobApplication(Base):
    """Track job applications"""
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))

    # Application status
    status = Column(String(50), default="pending")  # pending, applied, failed, rejected
    match_score = Column(Float)  # How well job matches resume (0-100)

    # Application details
    applied_at = Column(DateTime, nullable=True)
    application_method = Column(String(50))  # automated, manual

    # Results
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    response_data = Column(JSON, nullable=True)

    # Follow-up
    response_received = Column(Boolean, default=False)
    interview_scheduled = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")