"""
Resume Parser - Extract structured data from PDF/DOCX resumes
Improved version with better experience and education parsing
"""
import re
from pathlib import Path
from typing import Dict, List, Optional
import spacy
import pdfplumber
from docx import Document

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("⚠️  spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

class ResumeParser:
    """Parse resumes and extract structured information"""
    
    def __init__(self):
        self.nlp = nlp
    
    def parse_file(self, file_path: str) -> Dict:
        """Parse resume from file path"""
        file_path = Path(file_path)
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self._extract_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Parse the extracted text
        return self.parse_text(text)
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF using pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(str(file_path)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(str(file_path))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")
    
    def parse_text(self, text: str) -> Dict:
        """Parse resume text and extract structured data"""
        result = {
            "raw_text": text,
            "name": self._extract_name(text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text)
        }
        return result
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract person's name from resume"""
        lines = text.split("\n")
        # Usually name is in first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and len(line) > 3:
                # Simple heuristic: if line has 2-4 words and looks like a name
                if not any(char.isdigit() for char in line):
                    if not re.search(r'@|http|www|developer|engineer', line, re.IGNORECASE):
                        return line
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number"""
        # Match various phone formats including international
        phone_patterns = [
            r'\+\d{1,3}\s*\d{2,3}\s*\d{3}\s*\d{3,4}',  # +216 58 247 509
            r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b',     # 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.\s]??\d{4}',          # (123) 456-7890
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills"""
        # Common skill keywords
        skill_keywords = [
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby',
            'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql',
            
            # Frameworks & Libraries
            'react', 'angular', 'vue', 'svelte', 'node.js', 'express', 'django',
            'flask', 'fastapi', 'spring boot', 'spring', 'laravel', '.net',
            'react native', 'expo', 'flutter', 'electron',
            
            # Databases
            'mongodb', 'postgresql', 'mysql', 'redis', 'cassandra', 'dynamodb',
            'oracle', 'sqlite', 'mariadb', 'elasticsearch',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd',
            'terraform', 'ansible', 'linux', 'bash', 'shell',
            
            # Tools & Concepts
            'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
            'agile', 'scrum', 'rest', 'graphql', 'microservices', 'api',
            'oauth', 'jwt', 'rbac', 'maven', 'gradle', 'npm', 'yarn',
            
            # AI/ML
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'scikit-learn', 'pandas', 'numpy', 'opencv', 'nlp', 'computer vision',
            'artificial intelligence', 'neural networks', 'cnn', 'rnn',
            
            # Other
            'html', 'css', 'tailwind', 'bootstrap', 'sass', 'webpack',
            'postman', 'swagger', 'figma', 'adobe', 'photoshop', 'illustrator'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                # Capitalize properly
                if skill in ['html', 'css', 'sql', 'api', 'rest', 'jwt', 'npm', 'ci/cd', 'aws', 'gcp', 'nlp', 'cnn', 'rnn', 'rbac']:
                    found_skills.append(skill.upper())
                else:
                    found_skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience - IMPROVED VERSION"""
        experience = []
        
        # Look for experience section - support multiple variations
        exp_patterns = [
            r'(professional experience|work experience|experience|employment)(.*?)(?=education|skills|projects|certifications|$)',
            r'(PROFESSIONAL EXPERIENCE|WORK EXPERIENCE|EXPERIENCE)(.*?)(?=EDUCATION|SKILLS|PROJECTS|CERTIFICATIONS|$)'
        ]
        
        exp_section = None
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                exp_section = match.group(2)
                break
        
        if not exp_section:
            return experience
        
        # Split by date patterns to find individual job entries
        # Matches: 06/2025 – 07/2025, 2020-2021, Jan 2020 - Present, etc.
        date_patterns = [
            r'\d{2}/\d{4}\s*[–-]\s*\d{2}/\d{4}',           # 06/2025 – 07/2025
            r'\d{2}/\d{4}\s*[–-]\s*(?:Present|Current)',   # 06/2025 – Present
            r'\d{4}\s*[–-]\s*\d{4}',                       # 2020 - 2021
            r'\d{4}\s*[–-]\s*(?:Present|Current)',         # 2020 - Present
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[–-]\s*\d{4}',  # Jan 2020 - 2021
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*[–-]\s*(?:Present|Current)'  # Jan 2020 - Present
        ]
        
        # Find all date matches
        all_matches = []
        for pattern in date_patterns:
            matches = list(re.finditer(pattern, exp_section, re.IGNORECASE))
            all_matches.extend(matches)
        
        # Sort by position in text
        all_matches.sort(key=lambda x: x.start())
        
        # Extract text for each job entry
        for i, match in enumerate(all_matches):
            start_pos = match.start()
            
            # Find end position (next date or end of section)
            if i < len(all_matches) - 1:
                end_pos = all_matches[i + 1].start()
            else:
                end_pos = len(exp_section)
            
            # Extract job text
            job_text = exp_section[start_pos:end_pos].strip()
            
            # Split into lines to extract details
            lines = [line.strip() for line in job_text.split('\n') if line.strip()]
            
            if len(lines) >= 2:
                job_entry = {
                    "period": match.group(0),
                    "company": lines[1] if len(lines) > 1 else "",
                    "title": lines[2] if len(lines) > 2 else "",
                    "description": "\n".join(lines[3:]) if len(lines) > 3 else ""
                }
                experience.append(job_entry)
        
        return experience
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information - IMPROVED VERSION"""
        education = []
        
        # Look for education section
        edu_patterns = [
            r'(education|academic background|qualifications)(.*?)(?=experience|skills|projects|certifications|$)',
            r'(EDUCATION|ACADEMIC BACKGROUND|QUALIFICATIONS)(.*?)(?=EXPERIENCE|SKILLS|PROJECTS|CERTIFICATIONS|$)'
        ]
        
        edu_section = None
        for pattern in edu_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                edu_section = match.group(2)
                break
        
        if not edu_section:
            return education
        
        # Common degree keywords
        degree_keywords = [
            "bachelor", "master", "phd", "doctorate", "associate", "diploma",
            "certificate", "degree", "b.s.", "m.s.", "b.a.", "m.a.", "b.sc", "m.sc"
        ]
        
        lines = edu_section.split('\n')
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a degree
            if any(degree in line.lower() for degree in degree_keywords):
                # Save previous entry if exists
                if current_entry:
                    education.append(current_entry)
                
                current_entry = {"degree": line}
            
            # Check for year (2020-2024, 2023 – Present, etc.)
            elif re.search(r'\d{4}', line):
                if current_entry:
                    current_entry["period"] = line
            
            # Institution name (usually has specific keywords)
            elif any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school', 'academy']):
                if current_entry:
                    current_entry["institution"] = line
            
            # Additional info
            elif current_entry and 'description' not in current_entry:
                current_entry["description"] = line
        
        # Add last entry
        if current_entry:
            education.append(current_entry)
        
        return education


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    result = parser.parse_file("../data/resumes/Resume (1).pdf")
    
    print("=== PARSED RESUME ===")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Phone: {result['phone']}")
    print(f"\nSkills ({len(result['skills'])}):")
    for skill in result['skills']:
        print(f"  - {skill}")
    
    print(f"\nExperience ({len(result['experience'])}):")
    for i, exp in enumerate(result['experience'], 1):
        print(f"\n{i}. {exp.get('period', 'N/A')}")
        print(f"   Company: {exp.get('company', 'N/A')}")
        print(f"   Title: {exp.get('title', 'N/A')}")
        print(f"   Description: {exp.get('description', 'N/A')[:100]}...")
    
    print(f"\nEducation ({len(result['education'])}):")
    for i, edu in enumerate(result['education'], 1):
        print(f"\n{i}. {edu.get('degree', 'N/A')}")
        print(f"   Institution: {edu.get('institution', 'N/A')}")
        print(f"   Period: {edu.get('period', 'N/A')}")