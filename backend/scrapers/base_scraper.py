"""
Base Scraper - Abstract class for job board scrapers
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import random
from datetime import datetime

class BaseScraper(ABC):
    """Abstract base class for all job scrapers"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        self.delay_min = 1  # Minimum delay between requests (seconds)
        self.delay_max = 3  # Maximum delay between requests

    def get_random_user_agent(self) -> str:
        """Get random user agent to avoid detection"""
        return random.choice(self.user_agents)

    def random_delay(self):
        """Add random delay between requests to be respectful"""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)

    @abstractmethod
    def search_jobs(
        self,
        keywords: List[str],
        location: Optional[str] = None,
        remote_only: bool = False,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search for jobs based on criteria

        Args:
            keywords: List of job titles or keywords
            location: Location string (e.g., "New York, NY")
            remote_only: Filter for remote jobs only
            limit: Maximum number of jobs to return

        Returns:
            List of job dictionaries with standardized fields
        """
        pass

    @abstractmethod
    def parse_job_listing(self, job_data: Dict) -> Dict:
        """
        Parse raw job data into standardized format

        Returns:
            Dict with fields: title, company, location, description,
            requirements, salary_min, salary_max, is_remote, url, etc.
        """
        pass

    def standardize_job(self, raw_data: Dict) -> Dict:
        """
        Convert raw scraped data to standardized format
        """
        return {
            "title": raw_data.get("title", ""),
            "company": raw_data.get("company", ""),
            "location": raw_data.get("location", ""),
            "description": raw_data.get("description", ""),
            "requirements": raw_data.get("requirements", ""),
            "salary_min": raw_data.get("salary_min"),
            "salary_max": raw_data.get("salary_max"),
            "is_remote": raw_data.get("is_remote", False),
            "url": raw_data.get("url", ""),
            "application_url": raw_data.get("application_url", ""),
            "easy_apply": raw_data.get("easy_apply", False),
            "posted_date": raw_data.get("posted_date"),
            "source": self.name.replace("Scraper", "").lower(),
            "external_id": raw_data.get("external_id", ""),
            "scraped_at": datetime.utcnow()
        }

    def extract_salary(self, text: str) -> tuple:
        """
        Extract salary range from text
        Returns: (min_salary, max_salary) or (None, None)
        """
        import re

        # Look for patterns like "$80,000 - $120,000" or "$80k-$120k"
        patterns = [
            r'\$\s*(\d+)[,]?(\d+)?\s*-\s*\$\s*(\d+)[,]?(\d+)?',
            r'(\d+)k\s*-\s*(\d+)k',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    if 'k' in pattern:
                        min_sal = int(groups[0]) * 1000
                        max_sal = int(groups[1]) * 1000
                    else:
                        min_sal = int(groups[0] + (groups[1] or ''))
                        max_sal = int(groups[2] + (groups[3] or ''))
                    return (min_sal, max_sal)
                except:
                    continue

        return (None, None)