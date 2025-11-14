"""
Indeed Job Scraper
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote_plus
from datetime import datetime
import re

from .base_scraper import BaseScraper

class IndeedScraper(BaseScraper):
    """Scrape jobs from Indeed.com"""

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.indeed.com"
        self.search_url = f"{self.base_url}/jobs"

    def search_jobs(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """Search Indeed for jobs"""
        all_jobs = []

        # Combine keywords
        query = " OR ".join(keywords)

        # Build search parameters
        params = {
            'q': query,
            'l': location or '',
            'fromage': '14',  # Last 14 days
            'sort': 'date'
        }

        if remote_only:
            params['sc'] = '0kf%3Aattr%28DSQF7%29%3B'  # Remote filter

        page = 0
        while len(all_jobs) < limit:
            # Add pagination
            params['start'] = page * 10

            url = f"{self.search_url}?{urlencode(params)}"

            print(f"Scraping Indeed page {page + 1}...")
            jobs = self._scrape_search_page(url)

            if not jobs:
                break

            all_jobs.extend(jobs)
            page += 1

            # Respectful delay
            self.random_delay()

        return all_jobs[:limit]

    def _scrape_search_page(self, url: str) -> List[Dict]:
        """Scrape a single search results page"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9',
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching Indeed page: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = []

        # Find job cards (Indeed's structure may change)
        job_cards = soup.find_all('div', class_=re.compile('job_seen_beacon'))

        for card in job_cards:
            try:
                job = self._parse_job_card(card)
                if job:
                    jobs.append(job)
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

        return jobs

    def _parse_job_card(self, card) -> Optional[Dict]:
        """Parse individual job card from search results"""
        try:
            # Title and link
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                return None

            link_elem = title_elem.find('a')
            title = title_elem.get_text(strip=True)
            job_id = link_elem.get('data-jk', '') if link_elem else ''

            # Company
            company_elem = card.find('span', {'data-testid': 'company-name'})
            company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

            # Location
            location_elem = card.find('div', {'data-testid': 'text-location'})
            location = location_elem.get_text(strip=True) if location_elem else ''

            # Salary
            salary_elem = card.find('div', class_=re.compile('salary-snippet'))
            salary_text = salary_elem.get_text(strip=True) if salary_elem else ''
            salary_min, salary_max = self.extract_salary(salary_text)

            # Snippet
            snippet_elem = card.find('div', class_='job-snippet')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''

            # Remote check
            is_remote = 'remote' in location.lower() or 'remote' in snippet.lower()

            # Job URL
            job_url = f"{self.base_url}/viewjob?jk={job_id}" if job_id else ''

            return self.standardize_job({
                'title': title,
                'company': company,
                'location': location,
                'description': snippet,
                'requirements': '',
                'salary_min': salary_min,
                'salary_max': salary_max,
                'is_remote': is_remote,
                'url': job_url,
                'application_url': job_url,
                'easy_apply': False,  # Need to check on job page
                'external_id': f"indeed_{job_id}",
                'posted_date': None
            })

        except Exception as e:
            print(f"Error parsing job card: {e}")
            return None

    def parse_job_listing(self, job_url: str) -> Dict:
        """Get full job details from job page"""
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9',
        }

        try:
            response = requests.get(job_url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error fetching job page: {e}")
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')

        # Job description
        desc_elem = soup.find('div', {'id': 'jobDescriptionText'})
        description = desc_elem.get_text(separator='\n', strip=True) if desc_elem else ''

        # Check for easy apply
        easy_apply = bool(soup.find('button', {'id': re.compile('indeedApplyButton')}))

        return {
            'description': description,
            'easy_apply': easy_apply
        }


# Example usage
if __name__ == "__main__":
    scraper = IndeedScraper()
    jobs = scraper.search_jobs(
        keywords=['Python Developer', 'Backend Engineer'],
        location='Remote',
        remote_only=True,
        limit=10
    )

    print(f"Found {len(jobs)} jobs")
    for job in jobs[:3]:
        print(f"\n{job['title']} at {job['company']}")
        print(f"Location: {job['location']}")
        print(f"URL: {job['url']}")