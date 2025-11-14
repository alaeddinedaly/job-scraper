from parsers.resume_parser import ResumeParser
from pathlib import Path

resume_path = Path('../data/resumes/Resume_en.pdf')
parser = ResumeParser()

# Get raw text to see what we're working with
result = parser.parse_file(str(resume_path))

print("=== RAW TEXT (first 2000 chars) ===")
print(result['raw_text'][:2000])
print("\n=== CURRENT PARSING ===")
print(f"Experience entries: {len(result['experience'])}")
print(f"Education entries: {len(result['education'])}")