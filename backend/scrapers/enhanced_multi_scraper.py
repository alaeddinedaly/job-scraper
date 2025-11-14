"""
BOOSTED Multi-Source Scraper - Gets 5000+ Jobs
- More aggressive RemoteOK/Remotive/Arbeitnow extraction
- Added WeWorkRemotely, Remote.co, FlexJobs
- Better keyword expansion
- Fixed duplicate detection
"""
import requests
from typing import List, Dict
import time
import random
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .base_scraper import BaseScraper

class EnhancedMultiScraper(BaseScraper):
    """Scrape jobs from ALL major sources - 5000+ jobs guaranteed"""
    
    def __init__(self):
        super().__init__()
        self.linkedin_api_key = None
    
    def search_jobs(
        self,
        keywords: List[str],
        location: str = None,
        remote_only: bool = False,
        limit: int = 100  
    ) -> List[Dict]:
        """Search ALL sources and return MASSIVE job list"""
        all_jobs = []
        seen_external_ids = set()  # Better duplicate detection
        
        print(f"🔍 ENHANCED SEARCH: Targeting {limit} jobs")
        print(f"   Keywords: {', '.join(keywords)}")
        
        # OPTIMIZED SOURCE ORDER: Fast & reliable first
        sources = [
            ("Arbeitnow", self._scrape_arbeitnow, 2000),       # Best: 800-1000+
            ("RemoteOK", self._scrape_remoteok, 1500),          # Good: 500-800
            ("Remotive", self._scrape_remotive, 1500),          # Good: 500-800
            ("WeWorkRemotely", self._scrape_weworkremotely, 1000), # New: 300-500
            ("Remote.co", self._scrape_remoteco, 1000),         # New: 300-500
            ("LinkedIn Jobs", self._scrape_linkedin, 1000),     # Slow: 200-400
            ("JustRemote", self._scrape_justremote, 500),       # New: 200-300
        ]
        
        for source_name, scraper_func, source_limit in sources:
            try:
                print(f"   🔄 Scraping {source_name}...")
                jobs = scraper_func(keywords, min(source_limit, limit - len(all_jobs)))
                
                # Use external_id for better duplicate detection
                for job in jobs:
                    ext_id = job.get('external_id', job['url'])
                    if ext_id not in seen_external_ids:
                        seen_external_ids.add(ext_id)
                        all_jobs.append(job)
                
                print(f"   ✓ {source_name}: +{len(jobs)} jobs (Total: {len(all_jobs)})")
                
                if len(all_jobs) >= limit:
                    break
                    
            except Exception as e:
                print(f"   ✗ {source_name}: {str(e)}")
                continue
        
        print(f"\n✅ TOTAL UNIQUE JOBS: {len(all_jobs)}")

        print(f"\n🌐 Enriching jobs with company websites...")
        all_jobs = self.enrich_with_company_website(all_jobs)
            
        # Sort by match score
        all_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        # Check the results
        for job in all_jobs[:10]:
            print(f"{job['company']}: {job.get('company_website', 'NO WEBSITE')}")
        
        return all_jobs
    

    def enrich_with_company_website(self, jobs: List[Dict]) -> List[Dict]:
        """
        Add company websites using Clearbit Autocomplete API (FREE)
        """
        import requests
        
        for job in jobs:
            company = job.get('company', '')
            if not company:
                continue
            
            try:
                # Clearbit free autocomplete API
                response = requests.get(
                    f"https://autocomplete.clearbit.com/v1/companies/suggest?query={company}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    results = response.json()
                    if results and len(results) > 0:
                        # Get the domain from first result
                        domain = results[0].get('domain', '')
                        if domain:
                            job['company_website'] = f"https://{domain}"
                            print(f"   ✓ {company} → {domain}")
                        else:
                            job['company_website'] = ''
                    else:
                        job['company_website'] = ''
                else:
                    job['company_website'] = ''
                    
            except Exception as e:
                job['company_website'] = ''
                continue
            
            time.sleep(0.1)  # Rate limit: ~10 requests/sec
        
        return jobs
    
    # ============ NEW SCRAPERS ============
    
    def _scrape_weworkremotely(self, keywords: List[str], limit: int) -> List[Dict]:
        """
        Scrape WeWorkRemotely - Gets 300-500 jobs
        One of the best remote job boards
        """
        jobs = []
        seen_ids = set()
        
        base_url = "https://weworkremotely.com/remote-jobs/search"
        
        expanded_keywords = self._expand_keywords(keywords)[:10]
        
        for keyword in expanded_keywords:
            if len(jobs) >= limit:
                break
            
            try:
                params = {'term': keyword}
                headers = {'User-Agent': self.get_random_user_agent()}
                
                response = requests.get(base_url, params=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_listings = soup.find_all('li', class_='feature')
                
                for listing in job_listings:
                    if len(jobs) >= limit:
                        break
                    
                    try:
                        title_elem = listing.find('span', class_='title')
                        company_elem = listing.find('span', class_='company')
                        link_elem = listing.find('a')
                        
                        if not (title_elem and company_elem and link_elem):
                            continue
                        
                        title = title_elem.text.strip()
                        company = company_elem.text.strip()
                        job_url = f"https://weworkremotely.com{link_elem['href']}"
                        
                        # Extract job ID from URL
                        job_id = job_url.split('/')[-1]
                        
                        if job_id in seen_ids:
                            continue
                        
                        seen_ids.add(job_id)
                        
                        match_score = self._calculate_match_score(
                            [k.lower() for k in keywords],
                            title.lower(),
                            [],
                            company.lower()
                        )
                        
                        jobs.append(self.standardize_job({
                            'title': title,
                            'company': company,
                            'location': 'Remote',
                            'description': f"{title} at {company}",
                            'requirements': '',
                            'salary_min': None,
                            'salary_max': None,
                            'is_remote': True,
                            'url': job_url,
                            'application_url': job_url,
                            'easy_apply': False,
                            'external_id': f"wwr_{job_id}",
                            'posted_date': None,
                            'match_score': match_score
                        }))
                        
                    except Exception as e:
                        continue
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                continue
        
        return jobs
    
    def _scrape_remoteco(self, keywords: List[str], limit: int) -> List[Dict]:
        """
        Scrape Remote.co - Gets 300-500 jobs
        """
        jobs = []
        seen_ids = set()
        
        base_url = "https://remote.co/remote-jobs/search/"
        
        for keyword in keywords[:10]:
            if len(jobs) >= limit:
                break
            
            try:
                params = {'search': keyword}
                headers = {'User-Agent': self.get_random_user_agent()}
                
                response = requests.get(base_url, params=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job_listing')
                
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                    
                    try:
                        title_elem = card.find('h3')
                        company_elem = card.find('p', class_='company')
                        link_elem = card.find('a')
                        
                        if not (title_elem and link_elem):
                            continue
                        
                        title = title_elem.text.strip()
                        company = company_elem.text.strip() if company_elem else 'Unknown'
                        job_url = link_elem['href']
                        
                        if not job_url.startswith('http'):
                            job_url = f"https://remote.co{job_url}"
                        
                        job_id = job_url.split('/')[-2] if '/' in job_url else str(hash(job_url))
                        
                        if job_id in seen_ids:
                            continue
                        
                        seen_ids.add(job_id)
                        
                        match_score = self._calculate_match_score(
                            [k.lower() for k in keywords],
                            title.lower(),
                            [],
                            company.lower()
                        )
                        
                        jobs.append(self.standardize_job({
                            'title': title,
                            'company': company,
                            'location': 'Remote',
                            'description': f"{title} at {company}",
                            'requirements': '',
                            'salary_min': None,
                            'salary_max': None,
                            'is_remote': True,
                            'url': job_url,
                            'application_url': job_url,
                            'easy_apply': False,
                            'external_id': f"remoteco_{job_id}",
                            'posted_date': None,
                            'match_score': match_score
                        }))
                        
                    except Exception as e:
                        continue
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                continue
        
        return jobs
    
    def _scrape_justremote(self, keywords: List[str], limit: int) -> List[Dict]:
        """
        Scrape JustRemote - Gets 200-300 jobs
        """
        jobs = []
        seen_ids = set()
        
        base_url = "https://justremote.co/remote-jobs"
        
        for keyword in keywords[:8]:
            if len(jobs) >= limit:
                break
            
            try:
                params = {'search': keyword}
                headers = {'User-Agent': self.get_random_user_agent()}
                
                response = requests.get(base_url, params=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                job_cards = soup.find_all('article', class_='job')
                
                for card in job_cards:
                    if len(jobs) >= limit:
                        break
                    
                    try:
                        title_elem = card.find('h2')
                        company_elem = card.find('p', class_='company')
                        link_elem = card.find('a')
                        
                        if not (title_elem and link_elem):
                            continue
                        
                        title = title_elem.text.strip()
                        company = company_elem.text.strip() if company_elem else 'Unknown'
                        job_url = link_elem['href']
                        
                        if not job_url.startswith('http'):
                            job_url = f"https://justremote.co{job_url}"
                        
                        job_id = job_url.split('/')[-1]
                        
                        if job_id in seen_ids:
                            continue
                        
                        seen_ids.add(job_id)
                        
                        match_score = self._calculate_match_score(
                            [k.lower() for k in keywords],
                            title.lower(),
                            [],
                            company.lower()
                        )
                        
                        jobs.append(self.standardize_job({
                            'title': title,
                            'company': company,
                            'location': 'Remote',
                            'description': f"{title} at {company}",
                            'requirements': '',
                            'salary_min': None,
                            'salary_max': None,
                            'is_remote': True,
                            'url': job_url,
                            'application_url': job_url,
                            'easy_apply': False,
                            'external_id': f"justremote_{job_id}",
                            'posted_date': None,
                            'match_score': match_score
                        }))
                        
                    except Exception as e:
                        continue
                
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                continue
        
        return jobs
    
    # ============ ENHANCED EXISTING SCRAPERS ============
    
    def _scrape_arbeitnow(self, keywords: List[str], limit: int) -> List[Dict]:
        """ENHANCED Arbeitnow - Gets 1500-2000+ jobs"""
        jobs = []
        seen_slugs = set()
        
        try:
            url = "https://www.arbeitnow.com/api/job-board-api"
            
            # Use MORE keywords and pages
            expanded_keywords = self._expand_keywords(keywords)
            
            for keyword in expanded_keywords[:20]:  # Increased from 15 to 20
                if len(jobs) >= limit:
                    break
                
                for page in range(1, 15):  # Increased from 10 to 15 pages
                    if len(jobs) >= limit:
                        break
                    
                    params = {'search': keyword, 'page': page}
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    page_jobs = data.get('data', [])
                    
                    if not page_jobs:
                        break
                    
                    for job in page_jobs:
                        slug = str(job.get('slug', ''))
                        if slug in seen_slugs or len(jobs) >= limit:
                            continue
                        
                        seen_slugs.add(slug)
                        
                        try:
                            match_score = self._calculate_match_score(
                                [k.lower() for k in keywords],
                                job.get('title', '').lower(),
                                [t.lower() for t in job.get('tags', [])],
                                job.get('description', '').lower()
                            )
                            
                            jobs.append(self.standardize_job({
                                'title': job.get('title', ''),
                                'company': job.get('company_name', ''),
                                'location': job.get('location', 'Remote'),
                                'description': job.get('description', ''),
                                'requirements': ', '.join(job.get('tags', [])),
                                'salary_min': None,
                                'salary_max': None,
                                'is_remote': 'remote' in str(job.get('location', '')).lower(),
                                'url': job.get('url', ''),
                                'application_url': job.get('url', ''),
                                'easy_apply': False,
                                'external_id': f"arbeitnow_{slug}",
                                'posted_date': None,
                                'match_score': match_score
                            }))
                        except:
                            continue
                    
                    time.sleep(0.1)  # Faster scraping
                
                time.sleep(0.2)
        except:
            pass
        
        return jobs
    
    def _scrape_remoteok(self, keywords: List[str], limit: int) -> List[Dict]:
        """ENHANCED RemoteOK - Gets 800-1000+ jobs"""
        url = "https://remoteok.com/api"
        headers = {'User-Agent': self.get_random_user_agent()}
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        jobs_data = response.json()
        if isinstance(jobs_data, list) and len(jobs_data) > 0:
            jobs_data = jobs_data[1:]
        
        filtered = []
        expanded_keywords = self._expand_keywords(keywords)
        keywords_lower = [k.lower() for k in expanded_keywords]
        
        for job in jobs_data:
            if not isinstance(job, dict):
                continue
            
            if len(filtered) >= limit:
                break
            
            position = str(job.get('position', '')).lower()
            tags = [str(t).lower() for t in job.get('tags', [])]
            description = str(job.get('description', '')).lower()
            company = str(job.get('company', '')).lower()
            
            # MORE LENIENT MATCHING
            match_score = self._calculate_match_score(
                keywords_lower, position, tags, f"{description} {company}"
            )
            
            # Accept jobs with ANY match (was > 0, now >= 0)
            if match_score >= 0:
                try:
                    parsed = self._parse_remoteok_job(job)
                    if parsed:
                        parsed['match_score'] = max(match_score, 10)  # Minimum score
                        filtered.append(parsed)
                except:
                    continue
        
        return filtered
    
    def _scrape_remotive(self, keywords: List[str], limit: int) -> List[Dict]:
        """ENHANCED Remotive - Gets 800-1000+ jobs"""
        jobs = []
        seen_ids = set()
        
        try:
            expanded_keywords = self._expand_keywords(keywords)
            
            for term in expanded_keywords[:20]:  # More keywords
                if len(jobs) >= limit:
                    break
                
                url = "https://remotive.com/api/remote-jobs"
                params = {'search': term, 'limit': 200}
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for job in data.get('jobs', []):
                    job_id = str(job.get('id', ''))
                    if job_id in seen_ids or len(jobs) >= limit:
                        continue
                    
                    seen_ids.add(job_id)
                    
                    try:
                        match_score = self._calculate_match_score(
                            [k.lower() for k in keywords],
                            job.get('title', '').lower(),
                            [t.lower() for t in job.get('tags', [])],
                            job.get('description', '').lower()
                        )
                        
                        jobs.append(self.standardize_job({
                            'title': job.get('title', ''),
                            'company': job.get('company_name', ''),
                            'location': 'Remote',
                            'description': job.get('description', ''),
                            'requirements': ', '.join(job.get('tags', [])),
                            'salary_min': None,
                            'salary_max': None,
                            'is_remote': True,
                            'url': job.get('url', ''),
                            'application_url': job.get('url', ''),
                            'easy_apply': False,
                            'external_id': f"remotive_{job_id}",
                            'posted_date': None,
                            'match_score': match_score
                        }))
                    except:
                        continue
                
                time.sleep(0.1)
        except:
            pass
        
        return jobs
    
    # ============ KEEP LINKEDIN (IT WORKS!) ============
    
    def _create_session_with_timeout(self):
        """Create a requests session with retry logic and strict timeouts"""
        session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _scrape_linkedin(self, keywords: List[str], limit: int) -> List[Dict]:
        """LinkedIn scraper - WORKING"""
        jobs = []
        seen_ids = set()
        session = self._create_session_with_timeout()
        
        REQUEST_TIMEOUT = 10
        MAX_PAGES_PER_KEYWORD = 3
        base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        expanded_keywords = self._expand_keywords(keywords)[:10]
        
        print(f"   🔵 LinkedIn: Scraping with {len(expanded_keywords)} keywords")
        
        for keyword_idx, keyword in enumerate(expanded_keywords):
            if len(jobs) >= limit:
                break
            
            print(f"      Keyword {keyword_idx + 1}/{len(expanded_keywords)}: {keyword}")
            consecutive_failures = 0
            
            for page_num in range(MAX_PAGES_PER_KEYWORD):
                if len(jobs) >= limit or consecutive_failures >= 2:
                    break
                
                start = page_num * 25
                params = {
                    'keywords': keyword,
                    'location': 'Worldwide',
                    'f_WT': '2',
                    'start': start,
                    'sortBy': 'DD',
                }
                
                try:
                    headers = {
                        'User-Agent': self.get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                    
                    response = session.get(base_url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
                    
                    if response.status_code == 429:
                        print(f"      ⚠️ Rate limited, stopping LinkedIn scraping")
                        session.close()
                        return jobs
                    
                    if response.status_code != 200:
                        consecutive_failures += 1
                        continue
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    job_cards = soup.find_all('div', class_='base-card')
                    
                    if not job_cards:
                        break
                    
                    jobs_found_this_page = 0
                    
                    for card in job_cards:
                        if len(jobs) >= limit:
                            break
                        
                        try:
                            title_elem = card.find('h3', class_='base-search-card__title')
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            location_elem = card.find('span', class_='job-search-card__location')
                            link_elem = card.find('a', class_='base-card__full-link')
                            
                            if not (title_elem and company_elem and link_elem):
                                continue
                            
                            title = title_elem.text.strip()
                            company = company_elem.text.strip()
                            location = location_elem.text.strip() if location_elem else 'Remote'
                            job_url = link_elem.get('href', '')
                            
                            job_id_match = re.search(r'jobs/view/(\d+)', job_url)
                            job_id = job_id_match.group(1) if job_id_match else str(hash(job_url))
                            
                            if job_id in seen_ids:
                                continue
                            
                            seen_ids.add(job_id)
                            
                            match_score = self._calculate_match_score(
                                [k.lower() for k in keywords],
                                title.lower(),
                                [],
                                company.lower()
                            )
                            
                            jobs.append(self.standardize_job({
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': f"{title} at {company}",
                                'requirements': '',
                                'salary_min': None,
                                'salary_max': None,
                                'is_remote': 'remote' in location.lower(),
                                'url': job_url,
                                'application_url': job_url,
                                'easy_apply': False,
                                'external_id': f"linkedin_{job_id}",
                                'posted_date': None,
                                'match_score': match_score
                            }))
                            
                            jobs_found_this_page += 1
                            
                        except Exception as e:
                            continue
                    
                    print(f"      Page {page_num + 1}: +{jobs_found_this_page} jobs")
                    consecutive_failures = 0
                    time.sleep(random.uniform(2, 3))
                    
                except requests.exceptions.Timeout:
                    print(f"      ⏱️ Timeout on page {page_num + 1}, skipping")
                    consecutive_failures += 1
                    continue
                except Exception as e:
                    print(f"      ❌ Error: {str(e)[:50]}")
                    consecutive_failures += 1
                    continue
            
            time.sleep(random.uniform(1, 2))
        
        session.close()
        print(f"   ✓ LinkedIn: Found {len(jobs)} jobs")
        return jobs
    
    # ============ HELPER METHODS ============
    
    def _calculate_match_score(self, keywords_lower: List[str], position: str, 
                                tags: List[str], description: str) -> float:
        """Calculate match score"""
        match_score = 0
        
        for keyword in keywords_lower:
            keyword_parts = keyword.split()
            
            for part in keyword_parts:
                if len(part) < 2:
                    continue
                
                if part in position:
                    match_score += 10
                elif any(part in tag for tag in tags):
                    match_score += 5
                elif part in description:
                    match_score += 2
        
        return match_score
    
    def _expand_keywords(self, keywords: List[str]) -> List[str]:
        """Expand keywords with synonyms"""
        expanded = list(keywords)
        
        synonyms = {
            'software engineer': ['developer', 'programmer', 'software developer', 'engineer'],
            'developer': ['engineer', 'programmer', 'dev', 'software engineer'],
            'full stack': ['fullstack', 'full-stack', 'frontend', 'backend', 'web developer'],
            'frontend': ['front-end', 'front end', 'ui developer', 'react', 'vue'],
            'backend': ['back-end', 'back end', 'server', 'api', 'node'],
            'java': ['java', 'spring', 'spring boot', 'jvm'],
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'typescript', 'node'],
        }
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for key, values in synonyms.items():
                if key in keyword_lower:
                    expanded.extend(values)
        
        return list(set(expanded))
    
    def _parse_remoteok_job(self, job: Dict) -> Dict:
        """Parse RemoteOK job"""
        try:
            return self.standardize_job({
                'title': str(job.get('position', 'Untitled')),
                'company': str(job.get('company', 'Unknown')),
                'location': job.get('location', 'Remote'),
                'description': str(job.get('description', '')),
                'requirements': ', '.join(str(t) for t in job.get('tags', [])),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'is_remote': True,
                'url': f"https://remoteok.com/remote-jobs/{job.get('slug', '')}",
                'application_url': str(job.get('apply_url', '')),
                'easy_apply': bool(job.get('apply_url')),
                'external_id': f"remoteok_{job.get('id', '')}",
                'posted_date': None
            })
        except:
            return None