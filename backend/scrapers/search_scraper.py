"""
JSearch API via RapidAPI
Scrapes LinkedIn, Indeed, Glassdoor, ZipRecruiter
FREE: 100 searches/month
"""
import requests
import os
from typing import List, Dict
from datetime import datetime
from .base_scraper import BaseScraper

class JSearchScraper(BaseScraper):
    """
    JSearch API - Aggregates from LinkedIn, Indeed, Glassdoor
    FREE: 100 calls/month on RapidAPI
    Get API key at: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
    """
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.base_url = "https://jsearch.p.rapidapi.com/search"
    
    def parse_job_listing(self, job_data: Dict) -> Dict:
        """Parse job listing"""
        return self.standardize_job(job_data)
    
    def search_jobs(
        self,
        keywords: List[str],
        location: str = None,
        remote_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Search JSearch for jobs"""
        
        if not self.api_key:
            print("⚠️  RapidAPI key not found in .env file")
            return []
        
        # Build query
        query_parts = keywords.copy()
        if remote_only:
            query_parts.append('remote')
        if location and location.lower() != 'remote':
            query_parts.append(f'in {location}')
        
        query = ' '.join(query_parts)
        
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        
        params = {
            "query": query,
            "page": "1",
            "num_pages": "2",  # 2 pages = ~20 results
            "date_posted": "month"  # Jobs from last month
        }
        
        jobs = []
        
        try:
            print(f"   Searching JSearch: '{query}'...")
            response = requests.get(self.base_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('data', [])
            
            print(f"   Found {len(results)} jobs from JSearch")
            
            for job in results[:limit]:
                parsed = self._parse_jsearch_job(job)
                if parsed:
                    jobs.append(parsed)
        
        except Exception as e:
            print(f"   JSearch error: {e}")
        
        return jobs
    
    def _parse_jsearch_job(self, job: Dict) -> Dict:
        """Parse JSearch job listing"""
        try:
            # Get salary
            salary_min = job.get('job_min_salary')
            salary_max = job.get('job_max_salary')
            
            # Parse date
            posted_date = None
            if job.get('job_posted_at_datetime_utc'):
                try:
                    posted_date = datetime.fromisoformat(
                        job['job_posted_at_datetime_utc'].replace('Z', '+00:00')
                    )
                except:
                    pass
            
            # Build location string
            location_parts = []
            if job.get('job_city'):
                location_parts.append(job['job_city'])
            if job.get('job_state'):
                location_parts.append(job['job_state'])
            if job.get('job_country'):
                location_parts.append(job['job_country'])
            
            location = ', '.join(location_parts) if location_parts else 'Not specified'
            
            # Check if remote
            is_remote = job.get('job_is_remote', False)
            if not is_remote:
                employment_type = str(job.get('job_employment_type', '')).lower()
                is_remote = 'remote' in employment_type
            
            # Get requirements
            requirements = []
            if job.get('job_required_experience', {}).get('required_experience_in_months'):
                months = job['job_required_experience']['required_experience_in_months']
                years = months // 12
                requirements.append(f"{years} years experience")
            if job.get('job_required_education', {}).get('postgraduate_degree'):
                if job['job_required_education']['postgraduate_degree']:
                    requirements.append("Graduate degree")
            if job.get('job_required_skills'):
                requirements.extend(job['job_required_skills'])
            
            return self.standardize_job({
                'title': job.get('job_title', ''),
                'company': job.get('employer_name', 'Unknown'),
                'location': location,
                'description': job.get('job_description', ''),
                'requirements': ', '.join(requirements),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'is_remote': is_remote,
                'url': job.get('job_apply_link', ''),
                'application_url': job.get('job_apply_link', ''),
                'easy_apply': job.get('job_apply_is_direct', False),
                'external_id': f"jsearch_{job.get('job_id', '')}",
                'posted_date': posted_date
            })
        
        except Exception as e:
            print(f"      Error parsing JSearch job: {e}")
            return None


# Test
if __name__ == "__main__":
    scraper = JSearchScraper()
    
    if not scraper.api_key:
        print("\n❌ Please set RAPIDAPI_KEY in .env file")
        print("\nGet free API key at:")
        print("https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch")
    else:
        jobs = scraper.search_jobs(
            keywords=['Software Engineer', 'Junior Developer'],
            location='United States',
            limit=10
        )
        
        print(f"\n{'='*60}")
        print(f"Found {len(jobs)} jobs")
        print(f"{'='*60}\n")
        
        for i, job in enumerate(jobs[:5], 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Remote: {job['is_remote']}")
            print()