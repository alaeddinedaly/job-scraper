"""
Ultimate Job Scraper
Combines ALL free sources for maximum results
Gets 100-200+ jobs per search
"""
from typing import List, Dict
import os
from .base_scraper import BaseScraper
from .simple_multi_scraper import SimpleMultiScraper
from .adzuna_scraper import AdzunaScraper
from .jsearch_scraper import JSearchScraper

class UltimateScraper(BaseScraper):
    """
    Ultimate scraper combining all sources
    - RemoteOK (free, no key needed)
    - Remotive (free, no key needed)
    - Arbeitnow (free, no key needed)
    - Adzuna (free, requires API key)
    - JSearch (free, requires RapidAPI key)
    
    Total: 100-200+ jobs per search
    """
    
    def __init__(self):
        super().__init__()
        self.simple_scraper = SimpleMultiScraper()
        
        # Initialize Adzuna if API key exists
        self.adzuna_scraper = None
        if os.getenv('ADZUNA_APP_ID') and os.getenv('ADZUNA_API_KEY'):
            self.adzuna_scraper = AdzunaScraper()
            print("✓ Adzuna API configured")
        else:
            print("ℹ️  Adzuna API not configured (add ADZUNA_APP_ID and ADZUNA_API_KEY to .env)")
        
        # Initialize JSearch if RapidAPI key exists
        self.jsearch_scraper = None
        if os.getenv('RAPIDAPI_KEY'):
            self.jsearch_scraper = JSearchScraper()
            print("✓ JSearch API configured")
        else:
            print("ℹ️  JSearch API not configured (add RAPIDAPI_KEY to .env)")
    
    def parse_job_listing(self, job_data: Dict) -> Dict:
        """Parse job listing"""
        return self.standardize_job(job_data)
    
    def search_jobs(
        self,
        keywords: List[str],
        location: str = None,
        remote_only: bool = False,
        limit: int = 100
    ) -> List[Dict]:
        """
        Search ALL available sources
        Returns deduplicated results
        """
        all_jobs = []
        seen_urls = set()
        seen_titles_companies = set()  # Prevent duplicates by title+company
        
        print(f"\n{'='*60}")
        print(f"🔍 ULTIMATE JOB SEARCH")
        print(f"Keywords: {', '.join(keywords)}")
        print(f"Location: {location or 'Any'}")
        print(f"Remote Only: {remote_only}")
        print(f"{'='*60}\n")
        
        # Source 1: Simple Multi-Scraper (RemoteOK, Remotive, Arbeitnow)
        try:
            print("📡 Source 1: Free APIs (RemoteOK, Remotive, Arbeitnow)")
            simple_jobs = self.simple_scraper.search_jobs(
                keywords, location, remote_only, limit // 3
            )
            
            for job in simple_jobs:
                job_key = f"{job['title'].lower()}_{job['company'].lower()}"
                if job['url'] not in seen_urls and job_key not in seen_titles_companies:
                    seen_urls.add(job['url'])
                    seen_titles_companies.add(job_key)
                    all_jobs.append(job)
            
            print(f"✅ Added {len(simple_jobs)} jobs from free APIs\n")
        except Exception as e:
            print(f"❌ Free APIs error: {e}\n")
        
        # Source 2: Adzuna (if configured)
        if self.adzuna_scraper:
            try:
                print("📡 Source 2: Adzuna API (LinkedIn, Indeed, Monster aggregator)")
                adzuna_jobs = self.adzuna_scraper.search_jobs(
                    keywords, location, remote_only, limit // 2
                )
                
                added = 0
                for job in adzuna_jobs:
                    job_key = f"{job['title'].lower()}_{job['company'].lower()}"
                    if job['url'] not in seen_urls and job_key not in seen_titles_companies:
                        seen_urls.add(job['url'])
                        seen_titles_companies.add(job_key)
                        all_jobs.append(job)
                        added += 1
                
                print(f"✅ Added {added} unique jobs from Adzuna\n")
            except Exception as e:
                print(f"❌ Adzuna error: {e}\n")
        
        # Source 3: JSearch (if configured)
        if self.jsearch_scraper:
            try:
                print("📡 Source 3: JSearch API (LinkedIn, Indeed, Glassdoor, ZipRecruiter)")
                jsearch_jobs = self.jsearch_scraper.search_jobs(
                    keywords, location, remote_only, limit // 2
                )
                
                added = 0
                for job in jsearch_jobs:
                    job_key = f"{job['title'].lower()}_{job['company'].lower()}"
                    if job['url'] not in seen_urls and job_key not in seen_titles_companies:
                        seen_urls.add(job['url'])
                        seen_titles_companies.add(job_key)
                        all_jobs.append(job)
                        added += 1
                
                print(f"✅ Added {added} unique jobs from JSearch\n")
            except Exception as e:
                print(f"❌ JSearch error: {e}\n")
        
        print(f"{'='*60}")
        print(f"🎉 TOTAL UNIQUE JOBS FOUND: {len(all_jobs)}")
        print(f"{'='*60}\n")
        
        if len(all_jobs) == 0:
            print("⚠️  No jobs found. Try:")
            print("   1. Different keywords (e.g., 'Developer', 'Engineer', 'Software')")
            print("   2. Add API keys for Adzuna and JSearch (see setup guide)")
            print("   3. Change location or remove location filter")
        
        return all_jobs[:limit]


# Test
if __name__ == "__main__":
    scraper = UltimateScraper()
    
    print("\n" + "="*60)
    print("Testing Ultimate Scraper")
    print("="*60 + "\n")
    
    jobs = scraper.search_jobs(
        keywords=['Junior Developer', 'Software Engineer', 'Full Stack'],
        location='United States',
        remote_only=False,
        limit=50
    )
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {len(jobs)} jobs found")
    print(f"{'='*60}\n")
    
    print("First 10 results:\n")
    for i, job in enumerate(jobs[:10], 1):
        print(f"{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Remote: {'Yes' if job['is_remote'] else 'No'}")
        if job['salary_min']:
            print(f"   Salary: ${job['salary_min']:,} - ${job['salary_max']:,}")
        print(f"   Source: {job['source']}")
        print()