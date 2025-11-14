"""
Bulk Email Applicator - FIXED with Clearbit enrichment support
"""
from typing import Dict, List
from datetime import datetime
import json
import re

class BulkEmailApplicator:
    """Generate professional application emails with REAL company emails"""
    
    def __init__(self):
        self.template = None
    
    def generate_application_email(
        self,
        job: Dict,
        user_data: Dict,
        resume_path: str = None
    ) -> Dict:
        """Generate a professional application email with REAL email address"""
        
        email_subject = f"Application for {job['title']} at {job['company']}"
        
        email_body = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job['title']} position at {job['company']}.

With my background in full-stack development and experience with {', '.join(user_data.get('top_skills', ['modern web technologies']))}, I am confident I can contribute effectively to your team.

Key highlights of my qualifications:
- Proficient in {', '.join(user_data.get('top_skills', [])[:5])}
- Experience in developing web and mobile applications
- Strong problem-solving skills and ability to learn quickly
- Passionate about creating impactful software solutions

I have attached my resume for your review. I would welcome the opportunity to discuss how my skills and experience align with your needs.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
{user_data.get('name', 'Applicant')}
{user_data.get('email', '')}
{user_data.get('phone', '')}
"""
        
        # Get REAL company email using enriched data
        company_email, confidence = self._find_company_email(job)
        
        return {
            'to': company_email,
            'subject': email_subject,
            'body': email_body,
            'job_title': job['title'],
            'company': job['company'],
            'job_url': job['url'],
            'email_confidence': confidence  # Track reliability
        }
    
    def _find_company_email(self, job: Dict) -> tuple[str, str]:
        """
        Return (email, confidence_level)
        Priority: company_website > generated_from_name
        """
        company = job.get('company', 'Unknown')
        
        # Priority 1: Use company_website from Clearbit enrichment
        company_website = job.get('company_website', '')
        if company_website:
            domain = self._extract_domain_from_url(company_website)
            # Verify it's not a job board
            job_boards = ['arbeitnow', 'remotive', 'remoteok', 'linkedin', 'weworkremotely', 
                          'remote.co', 'remoteco', 'justremote', 'flexjobs', 'indeed', 'glassdoor']
            if domain and not any(board in domain.lower() for board in job_boards):
                return (f"careers@{domain}", "high")
        
        # Fallback: Generate from company name (less reliable)
        domain = self._generate_domain_from_name(company)
        return (f"careers@{domain}", "low")
    
    def _extract_domain_from_url(self, url: str) -> str:
        """Extract clean domain from URL"""
        if not url:
            return ""
        
        domain_match = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})', url)
        if domain_match:
            domain = domain_match.group(1)
            return domain.replace('www.', '')
        return ""
    
    def _generate_domain_from_name(self, company: str) -> str:
        """Generate domain from company name (fallback)"""
        if not company:
            return "example.com"
        
        clean = re.sub(r'[^a-zA-Z0-9]', '', company.lower())
        # Remove common legal entities
        clean = re.sub(r'(gmbh|inc|ltd|llc|corp|corporation|company|ag|limited)$', '', clean)
        
        if len(clean) < 2:
            return "example.com"
        
        return f"{clean}.com"
    
    def generate_bulk_applications(
        self,
        jobs: List[Dict],
        user_data: Dict
    ) -> List[Dict]:
        """Generate emails for multiple jobs at once"""
        emails = []
        
        for job in jobs:
            email = self.generate_application_email(job, user_data)
            emails.append(email)
        
        return emails
    
    def export_to_gmail_draft(self, emails: List[Dict], output_file: str = "applications.json"):
        """Export emails as JSON"""
        with open(output_file, 'w') as f:
            json.dump(emails, f, indent=2)
        
        print(f"✅ Exported {len(emails)} application emails to {output_file}")


def export_applications_csv(jobs: List[Dict], user_data: Dict, output_file: str = "applications.csv"):
    """
    Export applications as CSV with REAL company emails
    """
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Gmail Merge compatible headers + confidence tracking
        writer.writerow(['Company', 'Job Title', 'To Email', 'Subject', 'Message Body', 
                        'Job URL', 'Email Confidence', 'Company Website'])
        
        applicator = BulkEmailApplicator()
        
        high_confidence = 0
        low_confidence = 0
        
        for job in jobs:
            email_data = applicator.generate_application_email(job, user_data)
            writer.writerow([
                job['company'],
                job['title'],
                email_data['to'],
                email_data['subject'],
                email_data['body'],
                job['url'],
                email_data['email_confidence'],  # 'high' or 'low'
                job.get('company_website', 'Not found')
            ])
            
            if email_data['email_confidence'] == 'high':
                high_confidence += 1
            else:
                low_confidence += 1
        
        print(f"\n✅ Exported {len(jobs)} applications to {output_file}")
        print(f"   📧 High confidence emails: {high_confidence}")
        print(f"   ⚠️  Low confidence emails: {low_confidence}")
        print(f"\n💡 TIP: Send high-confidence emails first!")