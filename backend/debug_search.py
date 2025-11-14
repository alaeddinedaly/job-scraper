"""
Debug script to see what's happening with job search
"""
from scrapers.simple_multi_scraper import SimpleMultiScraper
from parsers.resume_parser import ResumeParser
from parsers.nlp_matcher import JobMatcher
from pathlib import Path

print("="*60)
print("DEBUG: Job Search Test")
print("="*60)

# Test 1: Check resume
print("\n1. Testing Resume Parser...")
resume_files = list(Path('../data/resumes').glob('*.pdf'))
if resume_files:
    parser = ResumeParser()
    result = parser.parse_file(str(resume_files[0]))
    print(f"✓ Resume parsed: {result['name']}")
    print(f"✓ Skills found: {len(result['skills'])}")
    print(f"  Skills: {result['skills'][:10]}")
else:
    print("✗ No resume found!")

# Test 2: Check job scraping
print("\n2. Testing Job Scraper...")
scraper = SimpleMultiScraper()
jobs = scraper.search_jobs(
    keywords=['Junior Developer', 'Software Engineer'],
    limit=10
)
print(f"✓ Jobs found: {len(jobs)}")
for i, job in enumerate(jobs[:3], 1):
    print(f"\n  Job {i}:")
    print(f"    Title: {job['title']}")
    print(f"    Company: {job['company']}")
    print(f"    Match Score: {job.get('match_score', 'N/A')}")

# Test 3: Check NLP matching
print("\n3. Testing NLP Matcher...")
try:
    matcher = JobMatcher()
    if resume_files and jobs:
        score = matcher.compute_match_score(
            result,
            jobs[0]['description'],
            jobs[0]['requirements']
        )
        print(f"✓ NLP Matcher working!")
        print(f"  Sample match score: {score}%")
except Exception as e:
    print(f"✗ NLP Matcher failed: {e}")

print("\n" + "="*60)