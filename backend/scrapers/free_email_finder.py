"""
100% FREE Unlimited Email Finder
Scrapes LinkedIn, company websites, and Google to find REAL recruiter emails
No API keys needed - completely free and unlimited
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urlparse
import json

class FreeEmailFinder:
    """Find real recruiter emails using web scraping - 100% FREE"""
    
    def __init__(self):
        self.session = requests.Session()
        self.email_cache = {}
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
    def find_hiring_contact(self, company_name: str, company_website: str, job_title: str = "") -> Dict:
        """
        Find real hiring contact using multiple free methods
        Returns verified email with confidence score
        """
        cache_key = f"{company_name}_{company_website}"
        if cache_key in self.email_cache:
            return self.email_cache[cache_key]
        
        print(f"   🔍 Finding contact for {company_name}...")
        
        result = None
        
        # Method 1: Scrape company careers/about page (BEST - most reliable)
        result = self._scrape_company_careers_page(company_website, company_name)
        if result and result['confidence'] == 'high':
            self.email_cache[cache_key] = result
            return result
        
        # Method 2: Google search for "[company] recruiter email"
        if not result or result['confidence'] != 'high':
            google_result = self._google_search_recruiter(company_name, company_website)
            if google_result and (not result or google_result['confidence'] == 'high'):
                result = google_result
        
        # Method 3: Scrape LinkedIn company page for employees
        if not result or result['confidence'] != 'high':
            linkedin_result = self._scrape_linkedin_employees(company_name, job_title)
            if linkedin_result and (not result or linkedin_result['confidence'] == 'high'):
                result = linkedin_result
        
        # Method 4: Extract emails from company website using email patterns
        if not result or result['confidence'] != 'high':
            pattern_result = self._find_email_patterns(company_website, company_name)
            if pattern_result and (not result or pattern_result['confidence'] == 'high'):
                result = pattern_result
        
        # Fallback: Generate smart guess
        if not result:
            result = self._generate_smart_email(company_name, company_website)
        
        self.email_cache[cache_key] = result
        return result
    
    def _scrape_company_careers_page(self, company_website: str, company_name: str) -> Optional[Dict]:
        """
        Scrape company's careers/about page for contact emails
        This is the BEST method - companies often list recruiting contacts
        """
        if not company_website:
            return None
        
        try:
            domain = self._extract_domain(company_website)
            
            # Try multiple career page variations
            career_paths = [
                '/careers',
                '/jobs',
                '/careers/contact',
                '/about/careers',
                '/work-with-us',
                '/join-us',
                '/about',
                '/contact'
            ]
            
            for path in career_paths:
                try:
                    url = f"https://{domain}{path}"
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    
                    response = self.session.get(url, headers=headers, timeout=8, allow_redirects=True)
                    
                    if response.status_code != 200:
                        continue
                    
                    # Extract emails from page
                    emails = self._extract_emails_from_html(response.text)
                    
                    if emails:
                        # Prioritize recruiting-related emails
                        best_email = self._select_best_recruiting_email(emails, response.text)
                        
                        if best_email:
                            # Try to find associated name
                            name = self._extract_name_near_email(response.text, best_email)
                            
                            print(f"      ✓ Found on {path}: {best_email}")
                            return {
                                'email': best_email,
                                'name': name or 'Hiring Team',
                                'title': self._guess_title_from_email(best_email),
                                'confidence': 'high',
                                'source': f'company_website_{path}',
                                'verified': True,
                                'found_on': url
                            }
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"      ✗ Career page error: {e}")
            return None
    
    def _google_search_recruiter(self, company_name: str, company_website: str) -> Optional[Dict]:
        """
        Use Google search to find recruiter emails
        Searches for: "company recruiter email" OR "company talent acquisition email"
        """
        try:
            domain = self._extract_domain(company_website) if company_website else ""
            
            # Multiple search queries
            queries = [
                f'"{company_name}" recruiter email',
                f'"{company_name}" talent acquisition email',
                f'"{company_name}" hiring manager email',
                f'site:{domain} recruiter email' if domain else None,
                f'site:{domain} careers contact' if domain else None,
            ]
            
            for query in queries:
                if not query:
                    continue
                
                try:
                    # Use DuckDuckGo HTML (more scraper-friendly than Google)
                    search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    
                    response = self.session.get(search_url, headers=headers, timeout=8)
                    
                    if response.status_code != 200:
                        continue
                    
                    # Extract emails from search results
                    emails = self._extract_emails_from_html(response.text)
                    
                    if emails:
                        # Filter for company domain
                        company_emails = [e for e in emails if domain and domain in e]
                        
                        if company_emails:
                            best_email = self._select_best_recruiting_email(company_emails, response.text)
                            
                            if best_email:
                                print(f"      ✓ Found via search: {best_email}")
                                return {
                                    'email': best_email,
                                    'name': 'Talent Acquisition Team',
                                    'title': 'Recruiter',
                                    'confidence': 'high',
                                    'source': 'google_search',
                                    'verified': True
                                }
                    
                    time.sleep(random.uniform(1, 2))
                    
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"      ✗ Search error: {e}")
            return None
    
    def _scrape_linkedin_employees(self, company_name: str, job_title: str) -> Optional[Dict]:
        """
        Scrape LinkedIn to find recruiter profiles and generate emails
        Looks for recruiters, talent acquisition, HR
        """
        try:
            # Search LinkedIn for company recruiters (public profiles)
            search_terms = [
                f'{company_name} recruiter',
                f'{company_name} talent acquisition',
                f'{company_name} HR'
            ]
            
            for term in search_terms:
                try:
                    # LinkedIn public search URL
                    url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(term)}"
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    
                    response = self.session.get(url, headers=headers, timeout=10)
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for profile names (LinkedIn shows these publicly)
                    profiles = soup.find_all('span', {'class': re.compile('entity-result__title')})
                    
                    for profile in profiles[:5]:  # Check first 5
                        name_text = profile.get_text(strip=True)
                        
                        # Extract name
                        name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', name_text)
                        if name_match:
                            name = name_match.group(1)
                            
                            # Generate email using common patterns
                            company_domain = self._extract_domain(company_name)
                            if company_domain:
                                email = self._generate_email_from_name(name, company_domain)
                                
                                print(f"      ✓ Found LinkedIn profile: {name}")
                                return {
                                    'email': email,
                                    'name': name,
                                    'title': 'Talent Acquisition',
                                    'confidence': 'medium',
                                    'source': 'linkedin_scrape',
                                    'verified': False
                                }
                    
                    time.sleep(random.uniform(2, 3))
                    
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"      ✗ LinkedIn error: {e}")
            return None
    
    def _find_email_patterns(self, company_website: str, company_name: str) -> Optional[Dict]:
        """
        Scrape company website and find email patterns
        Analyzes existing emails to determine format (firstname.lastname@ vs firstnamelastname@)
        """
        if not company_website:
            return None
        
        try:
            domain = self._extract_domain(company_website)
            
            # Scrape homepage and about page
            pages_to_check = [
                f"https://{domain}",
                f"https://{domain}/about",
                f"https://{domain}/team",
                f"https://{domain}/contact"
            ]
            
            all_emails = []
            
            for url in pages_to_check:
                try:
                    headers = {'User-Agent': random.choice(self.user_agents)}
                    response = self.session.get(url, headers=headers, timeout=8)
                    
                    if response.status_code == 200:
                        emails = self._extract_emails_from_html(response.text)
                        all_emails.extend(emails)
                    
                    time.sleep(random.uniform(0.5, 1))
                    
                except:
                    continue
            
            if not all_emails:
                return None
            
            # Analyze email pattern
            pattern = self._detect_email_pattern(all_emails)
            
            # Generate recruiting email using detected pattern
            if pattern:
                recruiting_email = self._generate_recruiting_email_with_pattern(domain, pattern)
                
                if recruiting_email:
                    print(f"      ✓ Pattern-based email: {recruiting_email}")
                    return {
                        'email': recruiting_email,
                        'name': 'Talent Team',
                        'title': 'Recruiting',
                        'confidence': 'medium',
                        'source': 'pattern_analysis',
                        'verified': False
                    }
            
            return None
            
        except Exception as e:
            print(f"      ✗ Pattern analysis error: {e}")
            return None
    
    def _extract_emails_from_html(self, html: str) -> List[str]:
        """Extract all email addresses from HTML"""
        # Comprehensive email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, html)
        
        # Filter out common non-recruiter emails
        exclude_patterns = [
            'noreply', 'no-reply', 'donotreply', 'support', 
            'info@', 'hello@', 'contact@', 'webmaster', 'admin@',
            'example.com', 'test@', 'privacy@', 'legal@'
        ]
        
        filtered = []
        for email in emails:
            email_lower = email.lower()
            if not any(pattern in email_lower for pattern in exclude_patterns):
                filtered.append(email)
        
        return list(set(filtered))  # Remove duplicates
    
    def _select_best_recruiting_email(self, emails: List[str], context: str = "") -> Optional[str]:
        """Select the most likely recruiting/hiring email from list"""
        recruiting_keywords = [
            'recruit', 'talent', 'hr', 'hiring', 'career', 
            'job', 'people', 'acquisition', 'staffing'
        ]
        
        scored_emails = []
        
        for email in emails:
            score = 0
            email_lower = email.lower()
            
            # Score based on email prefix
            for keyword in recruiting_keywords:
                if keyword in email_lower:
                    score += 10
            
            # Check context around email in HTML
            if context:
                context_lower = context.lower()
                email_index = context_lower.find(email_lower)
                
                if email_index > -1:
                    # Get surrounding text (50 chars before and after)
                    start = max(0, email_index - 50)
                    end = min(len(context_lower), email_index + len(email_lower) + 50)
                    surrounding = context_lower[start:end]
                    
                    for keyword in recruiting_keywords:
                        if keyword in surrounding:
                            score += 5
            
            scored_emails.append((score, email))
        
        # Sort by score
        scored_emails.sort(reverse=True, key=lambda x: x[0])
        
        return scored_emails[0][1] if scored_emails and scored_emails[0][0] > 0 else (emails[0] if emails else None)
    
    def _extract_name_near_email(self, html: str, email: str) -> Optional[str]:
        """Try to extract person's name near the email in HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text = soup.get_text()
            
            # Find email position
            email_index = text.lower().find(email.lower())
            
            if email_index > -1:
                # Get surrounding text
                start = max(0, email_index - 100)
                end = min(len(text), email_index + 100)
                surrounding = text[start:end]
                
                # Look for name patterns (capitalized words)
                name_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'
                names = re.findall(name_pattern, surrounding)
                
                if names:
                    return names[0]
            
            return None
            
        except:
            return None
    
    def _guess_title_from_email(self, email: str) -> str:
        """Guess job title from email prefix"""
        email_lower = email.lower()
        
        if 'recruit' in email_lower or 'talent' in email_lower:
            return 'Recruiter'
        elif 'hr' in email_lower or 'people' in email_lower:
            return 'HR Manager'
        elif 'career' in email_lower or 'job' in email_lower:
            return 'Career Services'
        elif 'hiring' in email_lower:
            return 'Hiring Manager'
        else:
            return 'Hiring Contact'
    
    def _detect_email_pattern(self, emails: List[str]) -> Optional[str]:
        """
        Detect email naming pattern from sample emails
        Returns: 'firstname.lastname', 'firstnamelastname', 'first.last', etc.
        """
        patterns = {
            'firstname.lastname': 0,
            'firstnamelastname': 0,
            'first.last': 0,
            'flastname': 0,
            'firstnamel': 0
        }
        
        for email in emails:
            prefix = email.split('@')[0].lower()
            
            # Check patterns
            if '.' in prefix and len(prefix.split('.')) == 2:
                parts = prefix.split('.')
                if len(parts[0]) > 2 and len(parts[1]) > 2:
                    patterns['firstname.lastname'] += 1
                elif len(parts[0]) <= 2 and len(parts[1]) > 2:
                    patterns['first.last'] += 1
            elif len(prefix) > 8 and '.' not in prefix:
                patterns['firstnamelastname'] += 1
            elif len(prefix) <= 8 and prefix[0].isalpha():
                if len(prefix) > 3:
                    patterns['flastname'] += 1
                else:
                    patterns['firstnamel'] += 1
        
        # Return most common pattern
        if any(patterns.values()):
            return max(patterns.items(), key=lambda x: x[1])[0]
        
        return 'firstname.lastname'  # Default
    
    def _generate_recruiting_email_with_pattern(self, domain: str, pattern: str) -> str:
        """Generate recruiting email using detected pattern"""
        recruiting_names = [
            ('talent', 'team'),
            ('recruiting', 'team'),
            ('careers', 'team'),
            ('hiring', 'team'),
            ('hr', 'team')
        ]
        
        first, last = recruiting_names[0]
        
        if pattern == 'firstname.lastname':
            return f"{first}.{last}@{domain}"
        elif pattern == 'firstnamelastname':
            return f"{first}{last}@{domain}"
        elif pattern == 'first.last':
            return f"{first[0]}.{last}@{domain}"
        elif pattern == 'flastname':
            return f"{first[0]}{last}@{domain}"
        else:
            return f"careers@{domain}"
    
    def _generate_email_from_name(self, name: str, domain: str) -> str:
        """Generate email from person's name"""
        parts = name.lower().split()
        
        if len(parts) >= 2:
            first = parts[0]
            last = parts[-1]
            
            # Try common patterns
            return f"{first}.{last}@{domain}"
        
        return f"careers@{domain}"
    
    def _generate_smart_email(self, company_name: str, company_website: str) -> Dict:
        """Generate smart fallback email with multiple alternatives"""
        domain = self._extract_domain(company_website) if company_website else None
        
        if not domain:
            clean_name = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
            domain = f"{clean_name}.com"
        
        alternatives = [
            f"careers@{domain}",
            f"jobs@{domain}",
            f"recruiting@{domain}",
            f"talent@{domain}",
            f"hr@{domain}",
            f"hiring@{domain}",
            f"talentacquisition@{domain}",
            f"people@{domain}"
        ]
        
        return {
            'email': alternatives[0],
            'alternatives': alternatives[1:],
            'name': 'Hiring Team',
            'title': 'Talent Acquisition',
            'confidence': 'low',
            'source': 'generated',
            'verified': False
        }
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract clean domain from URL"""
        if not url:
            return None
        
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = domain.replace('www.', '')
            
            return domain if domain else None
        except:
            return None
    
    def batch_find_emails(self, jobs: List[Dict], max_jobs: int = None) -> List[Dict]:
        """
        Find emails for multiple jobs with rate limiting
        100% FREE - no API limits!
        """
        if max_jobs:
            jobs = jobs[:max_jobs]
        
        enriched_jobs = []
        
        for idx, job in enumerate(jobs):
            print(f"\n[{idx+1}/{len(jobs)}] Processing {job.get('company', 'Unknown')}")
            
            contact = self.find_hiring_contact(
                job.get('company', ''),
                job.get('company_website', ''),
                job.get('title', '')
            )
            
            # Add contact info to job
            job['hiring_contact'] = contact
            job['contact_email'] = contact['email']
            job['contact_name'] = contact.get('name', '')
            job['email_confidence'] = contact.get('confidence', 'low')
            job['email_verified'] = contact.get('verified', False)
            job['email_source'] = contact.get('source', 'unknown')
            
            enriched_jobs.append(job)
            
            # Rate limiting to be respectful
            time.sleep(random.uniform(1, 2))
        
        # Statistics
        verified_count = sum(1 for j in enriched_jobs if j.get('email_verified'))
        high_conf_count = sum(1 for j in enriched_jobs if j.get('email_confidence') == 'high')
        medium_conf_count = sum(1 for j in enriched_jobs if j.get('email_confidence') == 'medium')
        
        print(f"\n{'='*60}")
        print(f"✅ EMAIL ENRICHMENT COMPLETE")
        print(f"{'='*60}")
        print(f"   Total jobs processed: {len(enriched_jobs)}")
        print(f"   ✓ Verified emails: {verified_count}")
        print(f"   🎯 High confidence: {high_conf_count}")
        print(f"   📧 Medium confidence: {medium_conf_count}")
        print(f"   ⚠️  Low confidence: {len(enriched_jobs) - verified_count - high_conf_count - medium_conf_count}")
        
        return enriched_jobs


# Test the email finder
if __name__ == "__main__":
    finder = FreeEmailFinder()
    
    test_jobs = [
        {
            'company': 'Shopify',
            'company_website': 'https://shopify.com',
            'title': 'Software Engineer'
        }
    ]
    
    results = finder.batch_find_emails(test_jobs)
    
    for job in results:
        print(f"\n{job['company']}:")
        print(f"  Email: {job['contact_email']}")
        print(f"  Name: {job['contact_name']}")
        print(f"  Confidence: {job['email_confidence']}")
        print(f"  Verified: {job['email_verified']}")
        print(f"  Source: {job['email_source']}")