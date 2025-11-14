"""
AutoJobApply - Main FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from database.db import init_db
from routers import resume, jobs, applications
from utils.logger import setup_logger

# Setup logger
logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize app on startup"""
    logger.info("🚀 Starting AutoJobApply API...")

    # Create necessary directories
    os.makedirs("../data/resumes", exist_ok=True)
    os.makedirs("../data/logs", exist_ok=True)

    # Initialize database
    init_db()
    logger.info("✅ Database initialized")

    yield

    logger.info("👋 Shutting down AutoJobApply API")

# Create FastAPI app
app = FastAPI(
    title="AutoJobApply API",
    description="Automated Job Application System - 100% Free & Open Source",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AutoJobApply API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )