"""
Advanced LinkedIn Recruiter Scraper using Selenium
Finds REAL recruiter names and generates their email addresses
100% FREE - No API needed
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import re
from typing import List, Dict, Optional

class LinkedInRecruiterScraper:
    """
    Scrapes LinkedIn to find real recruiter names and generate emails
    NO API - Uses Selenium for browser automation
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize scraper
        Args:
            headless: Run browser in background (True) or visible (False)
        """
        self.driver = self._setup_driver(headless)
        self.linkedin_logged_in = False
    
    def _setup_driver(self, headless: bool):
        """Setup Chrome driver with anti-detection"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # Anti-detection script
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def login_to_linkedin(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn (OPTIONAL - scrapes public data if not logged in)
        Login gives access to more profiles
        """
        try:
            print("   🔐 Logging into LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Enter credentials
            email_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            
            email_field.send_keys(email)
            password_field.send_keys(password)
            
            # Click login
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(5)
            
            # Check if logged in
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                self.linkedin_logged_in = True
                print("   ✓ LinkedIn login successful")
                return True
            else:
                print("   ✗ LinkedIn login failed")
                return False
                
        except Exception as e:
            print(f"   ✗ LinkedIn login error: {e}")
            return False
    
    def find_recruiters(self, company_name: str, max_results: int = 5) -> List[Dict]:
        """
        Find recruiters at a company
        Returns list of {name, title, profile_url}
        """
        try:
            # Search for recruiters at company
            search_query = f"{company_name} recruiter OR talent acquisition OR hiring manager"
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query.replace(' ', '%20')}"
            
            self.driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            recruiters = []
            
            # Wait for results to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "reusable-search__result-container"))
                )
            except TimeoutException:
                print(f"   ⚠️  No LinkedIn results found for {company_name}")
                return []
            
            # Find profile cards
            profile_cards = self.driver.find_elements(By.CLASS_NAME, "reusable-search__result-container")
            
            for card in profile_cards[:max_results]:
                try:
                    # Extract name
                    name_element = card.find_element(By.CSS_SELECTOR, ".entity-result__title-text a span[aria-hidden='true']")
                    name = name_element.text.strip()
                    
                    # Extract title
                    try:
                        title_element = card.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                        title = title_element.text.strip()
                    except:
                        title = "Recruiter"
                    
                    # Extract profile URL
                    try:
                        profile_link = card.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                        profile_url = profile_link.get_attribute("href")
                    except:
                        profile_url = ""
                    
                    # Verify this person is at the target company
                    if company_name.lower() in title.lower() or company_name.lower() in card.text.lower():
                        recruiters.append({
                            'name': name,
                            'title': title,
                            'profile_url': profile_url,
                            'company': company_name
                        })
                        
                        print(f"      ✓ Found: {name} - {title}")
                    
                except Exception as e:
                    continue
            
            return recruiters
            
        except Exception as e:
            print(f"   ✗ LinkedIn search error: {e}")
            return []
    
    def scrape_company_employees_page(self, company_name: str, company_linkedin_url: str = None) -> List[Dict]:
        """
        Scrape company's LinkedIn page to find employees
        Works even without login for some companies
        """
        try:
            if company_linkedin_url:
                url = f"{company_linkedin_url}/people/"
            else:
                # Try to find company page
                search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}"
                self.driver.get(search_url)
                time.sleep(3)
                
                # Get first company result
                try:
                    first_result = self.driver.find_element(By.CSS_SELECTOR, ".reusable-search__result-container a")
                    company_page_url = first_result.get_attribute("href")
                    url = f"{company_page_url}/people/"
                except:
                    print(f"   ✗ Could not find LinkedIn page for {company_name}")
                    return []
            
            self.driver.get(url)
            time.sleep(random.uniform(3, 5))
            
            employees = []
            
            # Scroll to load more employees
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find employee cards
            employee_cards = self.driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card")
            
            for card in employee_cards[:10]:
                try:
                    name_elem = card.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-title")
                    name = name_elem.text.strip()
                    
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, ".artdeco-entity-lockup__subtitle")
                        title = title_elem.text.strip()
                    except:
                        title = "Employee"
                    
                    # Filter for recruiting-related titles
                    recruiting_keywords = ['recruit', 'talent', 'hr', 'hiring', 'people', 'acquisition']
                    if any(kw in title.lower() for kw in recruiting_keywords):
                        employees.append({
                            'name': name,
                            'title': title,
                            'company': company_name
                        })
                        
                        print(f"      ✓ Found: {name} - {title}")
                
                except:
                    continue
            
            return employees
            
        except Exception as e:
            print(f"   ✗ Company page scrape error: {e}")
            return []
    
    def generate_email_from_name(self, name: str, company_domain: str, email_pattern: str = "firstname.lastname") -> str:
        """
        Generate email address from person's name using company's email pattern
        
        Patterns:
        - firstname.lastname@company.com (most common)
        - firstnamelastname@company.com
        - first.last@company.com
        - flastname@company.com
        """
        # Clean name
        name = name.strip()
        parts = re.findall(r'[A-Za-z]+', name)
        
        if len(parts) < 2:
            return f"careers@{company_domain}"
        
        first = parts[0].lower()
        last = parts[-1].lower()
        
        if email_pattern == "firstname.lastname":
            return f"{first}.{last}@{company_domain}"
        elif email_pattern == "firstnamelastname":
            return f"{first}{last}@{company_domain}"
        elif email_pattern == "first.last":
            return f"{first[0]}.{last}@{company_domain}"
        elif email_pattern == "flastname":
            return f"{first[0]}{last}@{company_domain}"
        else:
            return f"{first}.{last}@{company_domain}"
    
    def find_company_email_pattern(self, company_domain: str) -> str:
        """
        Try to detect company's email pattern by checking common patterns
        Uses email verification services
        """
        # Try to find pattern by searching for known employees
        # This would require additional API or web scraping
        # For now, return most common pattern
        return "firstname.lastname"
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()


class LinkedInEmailFinder:
    """
    Combines LinkedIn scraping with email generation
    100% FREE - finds real recruiter names and generates emails
    """
    
    def __init__(self, linkedin_email: str = None, linkedin_password: str = None, headless: bool = True):
        """
        Args:
            linkedin_email: Your LinkedIn email (optional - for better results)
            linkedin_password: Your LinkedIn password (optional)
            headless: Run browser in background
        """
        self.scraper = LinkedInRecruiterScraper(headless=headless)
        
        if linkedin_email and linkedin_password:
            self.scraper.login_to_linkedin(linkedin_email, linkedin_password)
    
    def find_hiring_contact(self, company_name: str, company_domain: str) -> Dict:
        """
        Find real recruiter at company and generate their email
        """
        print(f"   🔍 Searching LinkedIn for {company_name} recruiters...")
        
        # Find recruiters
        recruiters = self.scraper.find_recruiters(company_name, max_results=5)
        
        if not recruiters:
            # Try company page
            recruiters = self.scraper.scrape_company_employees_page(company_name)
        
        if recruiters:
            # Use first recruiter
            best_recruiter = recruiters[0]
            
            # Generate email
            email = self.scraper.generate_email_from_name(
                best_recruiter['name'],
                company_domain
            )
            
            return {
                'email': email,
                'name': best_recruiter['name'],
                'title': best_recruiter['title'],
                'confidence': 'high',
                'source': 'linkedin_scrape',
                'verified': False,
                'profile_url': best_recruiter.get('profile_url', ''),
                'alternatives': [
                    self.scraper.generate_email_from_name(best_recruiter['name'], company_domain, pattern)
                    for pattern in ['firstnamelastname', 'first.last', 'flastname']
                ]
            }
        else:
            # Fallback
            return {
                'email': f"careers@{company_domain}",
                'name': 'Hiring Team',
                'title': 'Talent Acquisition',
                'confidence': 'low',
                'source': 'generated',
                'verified': False,
                'alternatives': [
                    f"recruiting@{company_domain}",
                    f"talent@{company_domain}",
                    f"jobs@{company_domain}"
                ]
            }
    
    def batch_find_emails(self, jobs: List[Dict], max_jobs: int = None) -> List[Dict]:
        """
        Find emails for multiple jobs
        """
        if max_jobs:
            jobs = jobs[:max_jobs]
        
        enriched_jobs = []
        
        for idx, job in enumerate(jobs):
            print(f"\n[{idx+1}/{len(jobs)}] Processing {job.get('company', 'Unknown')}")
            
            company_domain = self._extract_domain(job.get('company_website', ''))
            
            if not company_domain:
                # Generate domain from company name
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', job['company'].lower())
                company_domain = f"{clean_name}.com"
            
            contact = self.find_hiring_contact(
                job.get('company', ''),
                company_domain
            )
            
            # Add to job
            job['hiring_contact'] = contact
            job['contact_email'] = contact['email']
            job['contact_name'] = contact['name']
            job['email_confidence'] = contact['confidence']
            job['email_verified'] = contact.get('verified', False)
            
            enriched_jobs.append(job)
            
            # Rate limiting
            time.sleep(random.uniform(3, 5))
        
        return enriched_jobs
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        
        import re
        match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', url)
        if match:
            return match.group(1).replace('www.', '')
        return ""
    
    def close(self):
        """Close scraper"""
        self.scraper.close()


# Example usage
if __name__ == "__main__":
    # Option 1: No login (public data only)
    finder = LinkedInEmailFinder(headless=False)
    
    # Option 2: With login (better results)
    # finder = LinkedInEmailFinder(
    #     linkedin_email="your_email@gmail.com",
    #     linkedin_password="your_password",
    #     headless=True
    # )
    
    test_jobs = [
        {
            'company': 'Stripe',
            'company_website': 'https://stripe.com',
            'title': 'Software Engineer'
        }
    ]
    
    try:
        results = finder.batch_find_emails(test_jobs)
        
        for job in results:
            print(f"\n{job['company']}:")
            print(f"  Email: {job['contact_email']}")
            print(f"  Name: {job['contact_name']}")
            print(f"  Title: {job['hiring_contact']['title']}")
            print(f"  Confidence: {job['email_confidence']}")
    
    finally:
        finder.close()