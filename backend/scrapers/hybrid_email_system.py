"""
COMPLETE HYBRID EMAIL FINDING SYSTEM
Combines all free methods for maximum accuracy
100% FREE - Unlimited emails

Methods (in priority order):
1. Scrape company career pages
2. Google/DuckDuckGo search
3. LinkedIn scraping (optional)
4. Email pattern analysis
5. Smart fallback generation
"""
from typing import Dict, List, Optional
import time
import random
from free_email_finder import FreeEmailFinder

# Optional: Only import if user wants LinkedIn scraping
try:
    from advanced_linkedin_scraper import LinkedInEmailFinder
    LINKEDIN_AVAILABLE = True
except:
    LINKEDIN_AVAILABLE = False
    print("⚠️  LinkedIn scraper not available (Selenium not installed)")


class HybridEmailFinder:
    """
    Ultimate free email finder - combines all methods
    NO API KEYS - NO LIMITS - 100% FREE
    """
    
    def __init__(self, use_linkedin: bool = False, linkedin_email: str = None, linkedin_password: str = None):
        """
        Args:
            use_linkedin: Enable LinkedIn scraping (requires Selenium)
            linkedin_email: Your LinkedIn email for better results (optional)
            linkedin_password: Your LinkedIn password (optional)
        """
        self.free_finder = FreeEmailFinder()
        self.linkedin_finder = None
        
        if use_linkedin and LINKEDIN_AVAILABLE:
            try:
                self.linkedin_finder = LinkedInEmailFinder(
                    linkedin_email=linkedin_email,
                    linkedin_password=linkedin_password,
                    headless=True
                )
                print("✅ LinkedIn scraper enabled")
            except Exception as e:
                print(f"⚠️  LinkedIn scraper failed: {e}")
                self.linkedin_finder = None
    
    def find_best_contact(self, company_name: str, company_website: str, job_title: str = "") -> Dict:
        """
        Find the BEST possible contact using all available methods
        Returns highest confidence result
        """
        print(f"   🔍 Finding contact for {company_name}...")
        
        results = []
        
        # Method 1: Web scraping (career pages, Google search, etc.)
        print(f"      → Searching web sources...")
        web_result = self.free_finder.find_hiring_contact(
            company_name, 
            company_website, 
            job_title
        )
        if web_result:
            results.append(web_result)
        
        # Method 2: LinkedIn scraping (if enabled)
        if self.linkedin_finder:
            print(f"      → Searching LinkedIn...")
            try:
                domain = self._extract_domain(company_website)
                if not domain:
                    clean_name = company_name.lower().replace(' ', '').replace(',', '')
                    domain = f"{clean_name}.com"
                
                linkedin_result = self.linkedin_finder.find_hiring_contact(
                    company_name,
                    domain
                )
                if linkedin_result:
                    results.append(linkedin_result)
                
                time.sleep(2)  # Rate limit
            except Exception as e:
                print(f"      ✗ LinkedIn error: {e}")
        
        # Select best result based on confidence
        if results:
            # Prioritize: verified > high > medium > low
            verified = [r for r in results if r.get('verified')]
            high_conf = [r for r in results if r.get('confidence') == 'high']
            medium_conf = [r for r in results if r.get('confidence') == 'medium']
            
            if verified:
                best = verified[0]
            elif high_conf:
                best = high_conf[0]
            elif medium_conf:
                best = medium_conf[0]
            else:
                best = results[0]
            
            # Combine alternatives from all results
            all_alternatives = []
            for r in results:
                if 'alternatives' in r:
                    all_alternatives.extend(r['alternatives'])
                if r != best:
                    all_alternatives.append(r['email'])
            
            best['alternatives'] = list(set(all_alternatives))[:5]
            
            return best
        
        # Fallback
        return self.free_finder._generate_smart_email(company_name, company_website)
    
    def batch_find_emails(
        self, 
        jobs: List[Dict], 
        max_jobs: int = None,
        use_linkedin_for_top: int = 0
    ) -> List[Dict]:
        """
        Find emails for multiple jobs
        
        Args:
            jobs: List of job dictionaries
            max_jobs: Limit number of jobs to process
            use_linkedin_for_top: Use LinkedIn scraping for top N jobs (slower but more accurate)
        """
        if max_jobs:
            jobs = jobs[:max_jobs]
        
        enriched_jobs = []
        
        print(f"\n{'='*60}")
        print(f"BATCH EMAIL FINDING - {len(jobs)} jobs")
        print(f"{'='*60}\n")
        
        for idx, job in enumerate(jobs):
            print(f"[{idx+1}/{len(jobs)}] {job.get('company', 'Unknown')}")
            
            # Use LinkedIn for high-priority jobs
            use_linkedin = (idx < use_linkedin_for_top) and self.linkedin_finder is not None
            
            if use_linkedin:
                print(f"   🔵 Using LinkedIn (high-priority job)")
            
            contact = self.find_best_contact(
                job.get('company', ''),
                job.get('company_website', ''),
                job.get('title', '')
            )
            
            # Add to job
            job['hiring_contact'] = contact
            job['contact_email'] = contact['email']
            job['contact_name'] = contact.get('name', '')
            job['email_confidence'] = contact.get('confidence', 'low')
            job['email_verified'] = contact.get('verified', False)
            job['email_source'] = contact.get('source', 'unknown')
            job['alternative_emails'] = contact.get('alternatives', [])
            
            enriched_jobs.append(job)
            
            # Status
            status_icon = "✓" if contact.get('verified') else ("🎯" if contact['confidence'] == 'high' else "~")
            print(f"   {status_icon} {contact['email']} ({contact['confidence']}) - {contact['source']}\n")
            
            # Rate limiting
            sleep_time = random.uniform(1, 2) if not use_linkedin else random.uniform(3, 5)
            time.sleep(sleep_time)
        
        # Final statistics
        self._print_statistics(enriched_jobs)
        
        return enriched_jobs
    
    def _print_statistics(self, jobs: List[Dict]):
        """Print enrichment statistics"""
        verified = sum(1 for j in jobs if j.get('email_verified'))
        high = sum(1 for j in jobs if j.get('email_confidence') == 'high')
        medium = sum(1 for j in jobs if j.get('email_confidence') == 'medium')
        low = len(jobs) - verified - high - medium
        
        sources = {}
        for j in jobs:
            source = j.get('email_source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n{'='*60}")
        print(f"ENRICHMENT COMPLETE")
        print(f"{'='*60}")
        print(f"Total jobs: {len(jobs)}")
        print(f"\nEmail Quality:")
        print(f"  ✓ Verified:        {verified} ({verified/len(jobs)*100:.1f}%)")
        print(f"  🎯 High confidence: {high} ({high/len(jobs)*100:.1f}%)")
        print(f"  📧 Medium:          {medium} ({medium/len(jobs)*100:.1f}%)")
        print(f"  ⚠️  Low:            {low} ({low/len(jobs)*100:.1f}%)")
        print(f"\nEmail Sources:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {source}: {count}")
        print(f"{'='*60}\n")
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        
        import re
        match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', url)
        if match:
            return match.group(1).replace('www.', '')
        return None
    
    def close(self):
        """Close any active scrapers"""
        if self.linkedin_finder:
            self.linkedin_finder.close()


# Integration with your existing scraper
def integrate_with_enhanced_scraper():
    """
    Example of how to integrate with EnhancedMultiScraper
    """
    from enhanced_multi_scraper import EnhancedMultiScraper
    
    class EnhancedMultiScraperWithEmails(EnhancedMultiScraper):
        """Enhanced scraper with hybrid email finding"""
        
        def __init__(self, use_linkedin: bool = False):
            super().__init__()
            self.email_finder = HybridEmailFinder(use_linkedin=use_linkedin)
        
        def search_jobs(self, keywords: List[str], location: str = None, 
                       remote_only: bool = False, limit: int = 100) -> List[Dict]:
            """Search jobs and enrich with REAL emails"""
            
            # Get jobs from all sources
            all_jobs = super().search_jobs(keywords, location, remote_only, limit)
            
            print(f"\n🌐 Step 1: Getting company websites...")
            all_jobs = self.enrich_with_company_website(all_jobs)
            
            print(f"\n📧 Step 2: Finding REAL hiring contact emails...")
            
            # Use LinkedIn for top 50 jobs (highest match scores)
            # Web scraping for the rest
            all_jobs = self.email_finder.batch_find_emails(
                all_jobs,
                use_linkedin_for_top=50  # LinkedIn for top 50, web scraping for rest
            )
            
            return all_jobs
        
        def close(self):
            """Cleanup"""
            self.email_finder.close()


# Standalone test
if __name__ == "__main__":
    # Test with sample jobs
    test_jobs = [
        {
            'company': 'Shopify',
            'company_website': 'https://shopify.com',
            'title': 'Software Engineer',
            'match_score': 85
        },
        {
            'company': 'Stripe',
            'company_website': 'https://stripe.com',
            'title': 'Backend Developer',
            'match_score': 80
        }
    ]
    
    # Initialize finder
    # Option 1: Web scraping only (fast, free, unlimited)
    finder = HybridEmailFinder(use_linkedin=False)
    
    # Option 2: With LinkedIn (slower, more accurate)
    # finder = HybridEmailFinder(
    #     use_linkedin=True,
    #     linkedin_email="your_email@gmail.com",
    #     linkedin_password="your_password"
    # )
    
    try:
        # Find emails
        results = finder.batch_find_emails(test_jobs, use_linkedin_for_top=1)
        
        # Display results
        print("\n📊 RESULTS:")
        for job in results:
            print(f"\n{job['company']} - {job['title']}")
            print(f"  Primary: {job['contact_email']} ({job['contact_name']})")
            print(f"  Confidence: {job['email_confidence']}")
            print(f"  Source: {job['email_source']}")
            if job.get('alternative_emails'):
                print(f"  Alternatives: {', '.join(job['alternative_emails'][:3])}")
    
    finally:
        finder.close()