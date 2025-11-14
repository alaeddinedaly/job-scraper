"""
NLP-based Job Matching using Sentence Transformers
Computes similarity between resume and job descriptions
"""
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Tuple
import numpy as np

class JobMatcher:
    """Match jobs to resume using semantic similarity"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize matcher with sentence transformer model
        all-MiniLM-L6-v2 is lightweight and fast (~80MB)
        """
        print(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("✅ Model loaded successfully")

    def compute_match_score(
        self,
        resume_data: Dict,
        job_description: str,
        job_requirements: str = ""
    ) -> float:
        """
        Compute match score between resume and job (0-100)

        Args:
            resume_data: Parsed resume dict with skills, experience, etc.
            job_description: Job description text
            job_requirements: Job requirements text (optional)

        Returns:
            Match score as percentage (0-100)
        """
        # Build resume text from structured data
        resume_text = self._build_resume_text(resume_data)

        # Combine job description and requirements
        job_text = f"{job_description}\n{job_requirements}"

        # Encode texts
        resume_embedding = self.model.encode(resume_text, convert_to_tensor=True)
        job_embedding = self.model.encode(job_text, convert_to_tensor=True)

        # Compute cosine similarity
        similarity = util.cos_sim(resume_embedding, job_embedding)

        # Convert to percentage
        score = float(similarity[0][0]) * 100
        return round(score, 2)

    def batch_match_jobs(
        self,
        resume_data: Dict,
        jobs: List[Dict]
    ) -> List[Tuple[Dict, float]]:
        """
        Match resume against multiple jobs efficiently

        Args:
            resume_data: Parsed resume data
            jobs: List of job dicts with 'description' and 'requirements'

        Returns:
            List of (job, score) tuples sorted by score descending
        """
        resume_text = self._build_resume_text(resume_data)

        # Encode resume once
        resume_embedding = self.model.encode(resume_text, convert_to_tensor=True)

        # Encode all job descriptions
        job_texts = [
            f"{job.get('description', '')}\n{job.get('requirements', '')}"
            for job in jobs
        ]
        job_embeddings = self.model.encode(job_texts, convert_to_tensor=True)

        # Compute similarities
        similarities = util.cos_sim(resume_embedding, job_embeddings)

        # Create results
        results = []
        for i, job in enumerate(jobs):
            score = float(similarities[0][i]) * 100
            results.append((job, round(score, 2)))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _build_resume_text(self, resume_data: Dict) -> str:
        """Build searchable text from resume data"""
        parts = []

        # Add skills (most important for matching)
        if resume_data.get('skills'):
            skills_text = ", ".join(resume_data['skills'])
            parts.append(f"Skills: {skills_text}")

        # Add experience descriptions
        if resume_data.get('experience'):
            for exp in resume_data['experience']:
                parts.append(exp.get('description', ''))

        # Add education
        if resume_data.get('education'):
            for edu in resume_data['education']:
                parts.append(edu.get('degree', ''))

        # Add raw text as fallback
        if resume_data.get('raw_text'):
            parts.append(resume_data['raw_text'][:1000])  # First 1000 chars

        return "\n".join(parts)

    def explain_match(
        self,
        resume_data: Dict,
        job_description: str,
        top_k: int = 5
    ) -> Dict:
        """
        Explain why a job matches or doesn't match
        Returns matching and missing skills
        """
        resume_skills = set(s.lower() for s in resume_data.get('skills', []))

        # Extract skills from job description (simple keyword matching)
        job_text_lower = job_description.lower()

        # Common tech skills to check
        all_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular',
            'vue', 'node.js', 'django', 'flask', 'sql', 'mongodb', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'machine learning', 'ai'
        ]

        job_skills = set()
        for skill in all_skills:
            if skill in job_text_lower:
                job_skills.add(skill)

        # Find matches and gaps
        matching_skills = resume_skills.intersection(job_skills)
        missing_skills = job_skills - resume_skills

        return {
            "matching_skills": list(matching_skills),
            "missing_skills": list(missing_skills),
            "match_percentage": len(matching_skills) / len(job_skills) * 100 if job_skills else 0
        }


# Example usage
if __name__ == "__main__":
    matcher = JobMatcher()

    # Sample resume data
    resume = {
        "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker"],
        "experience": [
            {"description": "Built RESTful APIs using Python and FastAPI"}
        ]
    }

    # Sample job
    job_desc = """
    We're looking for a Backend Developer with strong Python skills.
    Experience with FastAPI, PostgreSQL, and Docker is required.
    React knowledge is a plus.
    """

    score = matcher.compute_match_score(resume, job_desc)
    print(f"Match Score: {score}%")

    explanation = matcher.explain_match(resume, job_desc)
    print(f"Matching Skills: {explanation['matching_skills']}")
    print(f"Missing Skills: {explanation['missing_skills']}")