"""
RemoteOK Job Scraper - Remote jobs aggregator
RemoteOK has a simple JSON API we can use
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime

from .base_scraper import BaseScraper

class RemoteOKScraper(BaseScraper):
    """Scrape remote jobs from RemoteOK.com"""

    def __init__(self):
        super().__init__()
        self.api_url = "https://remoteok.com/api"

    def search_jobs(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        remote_only: bool = True,  # RemoteOK is all remote
        limit: int = 50
    ) -> List[Dict]:
        """Search RemoteOK for jobs"""
        print("Scraping RemoteOK...")

        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'application/json'
        }

        try:
            response = requests.get(self.api_url, headers=headers, timeout=15)
            response.raise_for_status()
            jobs_data = response.json()
        except Exception as e:
            print(f"Error fetching RemoteOK API: {e}")
            return []

        # First item is metadata, skip it
        if jobs_data and isinstance(jobs_data, list):
            jobs_data = jobs_data[1:]

        # Filter by keywords
        filtered_jobs = []
        keywords_lower = [k.lower() for k in keywords]

        for job in jobs_data:
            if not isinstance(job, dict):
                continue

            # Check if any keyword matches position or tags
            position = job.get('position', '').lower()
            tags = [t.lower() for t in job.get('tags', [])]

            if any(kw in position or any(kw in tag for tag in tags) for kw in keywords_lower):
                parsed_job = self.parse_job_listing(job)
                if parsed_job:
                    filtered_jobs.append(parsed_job)

            if len(filtered_jobs) >= limit:
                break

        return filtered_jobs[:limit]

    def parse_job_listing(self, job_data: Dict) -> Dict:
        """Parse RemoteOK job data"""
        try:
            # Extract salary
            salary_text = job_data.get('salary', '')
            salary_min, salary_max = self.extract_salary(str(salary_text))

            # If no salary from text, try min/max fields
            if not salary_min and job_data.get('salary_min'):
                salary_min = int(job_data['salary_min'])
            if not salary_max and job_data.get('salary_max'):
                salary_max = int(job_data['salary_max'])

            # Date posted
            posted_date = None
            if job_data.get('date'):
                try:
                    # RemoteOK uses epoch timestamp
                    timestamp = int(job_data['date'])
                    posted_date = datetime.fromtimestamp(timestamp)
                except:
                    pass

            # Location (even though it's remote)
            location = job_data.get('location', 'Remote')
            if not location or location == 'false':
                location = 'Remote'

            # Company
            company = job_data.get('company', 'Unknown')

            # Job URL
            slug = job_data.get('slug', '')
            job_url = f"https://remoteok.com/remote-jobs/{slug}"

            # Tags as requirements
            tags = job_data.get('tags', [])
            requirements = ', '.join(tags) if tags else ''

            return self.standardize_job({
                'title': job_data.get('position', ''),
                'company': company,
                'location': location,
                'description': job_data.get('description', ''),
                'requirements': requirements,
                'salary_min': salary_min,
                'salary_max': salary_max,
                'is_remote': True,
                'url': job_url,
                'application_url': job_data.get('apply_url', job_url),
                'easy_apply': bool(job_data.get('apply_url')),
                'external_id': f"remoteok_{job_data.get('id', '')}",
                'posted_date': posted_date
            })

        except Exception as e:
            print(f"Error parsing RemoteOK job: {e}")
            return None


# Example usage
if __name__ == "__main__":
    scraper = RemoteOKScraper()
    jobs = scraper.search_jobs(
        keywords=['Python', 'Backend', 'Full Stack'],
        limit=10
    )

    print(f"Found {len(jobs)} jobs on RemoteOK")
    for job in jobs[:5]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Salary: ${job['salary_min']}-${job['salary_max']}" if job['salary_min'] else "Salary: Not listed")
        print(f"URL: {job['url']}")