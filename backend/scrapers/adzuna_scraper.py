"""
Adzuna Job Board API
FREE - 50+ searches per month
Best accuracy for keywords
"""
import requests
import os
from typing import List, Dict
from datetime import datetime
from .base_scraper import BaseScraper

class AdzunaScraper(BaseScraper):
    """
    Adzuna API - Aggregates jobs from multiple sources
    FREE: 500 calls/month
    Get API key at: https://developer.adzuna.com/
    """
    
    def __init__(self):
        super().__init__()
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.api_key = os.getenv('ADZUNA_API_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
    
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
        """
        Search Adzuna for jobs
        
        Supported countries:
        - us (United States)
        - gb (United Kingdom) 
        - ca (Canada)
        - de (Germany)
        - fr (France)
        - au (Australia)
        - nl (Netherlands)
        - at (Austria)
        - br (Brazil)
        - ch (Switzerland)
        - in (India)
        - it (Italy)
        - nz (New Zealand)
        - pl (Poland)
        - ru (Russia)
        - sg (Singapore)
        - za (South Africa)
        """
        
        if not self.app_id or not self.api_key:
            print("⚠️  Adzuna API credentials not found in .env file")
            return []
        
        # Determine country based on location
        country = self._get_country_code(location)
        
        # Build search query
        what = ' '.join(keywords)
        where = location if location and location.lower() != 'remote' else ''
        
        jobs = []
        pages_to_fetch = min(3, (limit // 50) + 1)  # Adzuna returns 50 per page
        
        for page in range(1, pages_to_fetch + 1):
            try:
                url = f"{self.base_url}/{country}/search/{page}"
                
                params = {
                    'app_id': self.app_id,
                    'app_key': self.api_key,
                    'what': what,
                    'where': where,
                    'results_per_page': 50,
                    'content-type': 'application/json'
                }
                
                if remote_only:
                    params['what'] += ' remote'
                
                print(f"   Fetching Adzuna page {page}...")
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                results = data.get('results', [])
                
                for job in results:
                    parsed = self._parse_adzuna_job(job)
                    if parsed:
                        jobs.append(parsed)
                
                # Check if we have more results
                if len(results) < 50:
                    break  # No more pages
                
                if len(jobs) >= limit:
                    break
                
                self.random_delay()
                
            except Exception as e:
                print(f"   Error fetching Adzuna page {page}: {e}")
                break
        
        return jobs[:limit]
    
    def _parse_adzuna_job(self, job: Dict) -> Dict:
        """Parse Adzuna job listing"""
        try:
            # Get salary
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            
            # Parse date
            posted_date = None
            if job.get('created'):
                try:
                    posted_date = datetime.fromisoformat(job['created'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Get location
            location_parts = []
            if job.get('location', {}).get('display_name'):
                location_parts.append(job['location']['display_name'])
            location = ', '.join(location_parts) if location_parts else 'Not specified'
            
            # Check if remote
            description = str(job.get('description', '')).lower()
            title = str(job.get('title', '')).lower()
            is_remote = 'remote' in description or 'remote' in title or 'work from home' in description
            
            return self.standardize_job({
                'title': job.get('title', ''),
                'company': job.get('company', {}).get('display_name', 'Unknown'),
                'location': location,
                'description': job.get('description', ''),
                'requirements': job.get('category', {}).get('label', ''),
                'salary_min': salary_min,
                'salary_max': salary_max,
                'is_remote': is_remote,
                'url': job.get('redirect_url', ''),
                'application_url': job.get('redirect_url', ''),
                'easy_apply': False,
                'external_id': f"adzuna_{job.get('id', '')}",
                'posted_date': posted_date
            })
        except Exception as e:
            print(f"      Error parsing Adzuna job: {e}")
            return None
    
    def _get_country_code(self, location: str) -> str:
        """Map location to Adzuna country code"""
        if not location:
            return 'us'  # Default to US
        
        location_lower = location.lower()
        
        country_map = {
            'us': ['united states', 'usa', 'america'],
            'gb': ['united kingdom', 'uk', 'britain', 'england'],
            'ca': ['canada', 'canadian'],
            'de': ['germany', 'german', 'deutschland'],
            'fr': ['france', 'french'],
            'au': ['australia', 'australian'],
            'nl': ['netherlands', 'dutch'],
            'at': ['austria', 'austrian'],
            'ch': ['switzerland', 'swiss'],
            'in': ['india', 'indian'],
            'it': ['italy', 'italian'],
            'nz': ['new zealand'],
            'sg': ['singapore'],
            'za': ['south africa']
        }
        
        for code, names in country_map.items():
            if any(name in location_lower for name in names):
                return code
        
        return 'us'  # Default


# Test
if __name__ == "__main__":
    scraper = AdzunaScraper()
    
    if not scraper.app_id:
        print("\n❌ Please set ADZUNA_APP_ID and ADZUNA_API_KEY in .env file")
        print("\nGet free API key at: https://developer.adzuna.com/signup")
    else:
        jobs = scraper.search_jobs(
            keywords=['Junior Developer', 'Software Engineer'],
            location='United States',
            limit=20
        )
        
        print(f"\n{'='*60}")
        print(f"Found {len(jobs)} jobs")
        print(f"{'='*60}\n")
        
        for i, job in enumerate(jobs[:5], 1):
            print(f"{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            if job['salary_min']:
                print(f"   Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
            print()