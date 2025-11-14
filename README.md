# 🚀 AutoJobApply - Automated Job Application System

A fully automated job application system that scrapes job boards, matches opportunities to your resume, and applies on your behalf - **100% free and open-source**.

## ✨ Features

- 📄 **Resume Parsing**: Extracts text from PDF/DOCX resumes
- 🔍 **Smart Job Matching**: Uses NLP to match jobs to your skills (sentence-transformers)
- 🤖 **Auto-Apply**: Headless browser automation fills application forms
- 📊 **Dashboard**: Track all applications, successes, and failures
- 🎯 **Multi-Platform**: Supports Indeed, RemoteOK, and Wellfound
- 💾 **Local-First**: SQLite database, no cloud dependencies
- 🆓 **100% Free**: No paid APIs required

## 🛠️ Tech Stack

**Frontend:**

- Next.js 14 (App Router)
- React 18
- Tailwind CSS
- shadcn/ui components

**Backend:**

- FastAPI (Python 3.10+)
- SQLAlchemy + SQLite
- Playwright (browser automation)
- BeautifulSoup4 (web scraping)
- spaCy + sentence-transformers (NLP)

## 📦 Installation

### Prerequisites

- Node.js 18+
- Python 3.10-3.12 (⚠️ **Avoid Python 3.13+** - use 3.11 for best compatibility)
- pip and npm

### 🪟 Windows Users - Important!

**If you're on Windows, use the simplified setup:**

```bash
# Method 1: PowerShell (Recommended)
powershell -ExecutionPolicy Bypass -File setup-windows.ps1

# Method 2: Batch file
setup-windows.bat
```

**If you encounter issues, see `WINDOWS_FIX.md` or `FIX_NOW.md` for solutions.**

---

### 1. Clone and Setup Backend

```bash
# Create project directory
mkdir autojobapply && cd autojobapply

# Create backend
mkdir backend && cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (see requirements.txt below)
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Install Playwright browsers
playwright install chromium

# Create data directories
mkdir -p ../data/resumes ../data/logs
```

### 2. Setup Frontend

```bash
# From project root
cd ..
mkdir frontend && cd frontend

# Initialize Next.js
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir

# Install additional dependencies
npm install axios date-fns lucide-react
```

### 3. Environment Variables

Create `.env` in backend directory:

```env
DATABASE_URL=sqlite:///../data/autojobapply.db
UPLOAD_DIR=../data/resumes
LOG_DIR=../data/logs
FRONTEND_URL=http://localhost:3000
BACKEND_PORT=8000
```

Create `.env.local` in frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at: `http://localhost:3000`

## 📖 Usage Guide

### 1. Upload Resume

1. Navigate to `http://localhost:3000`
2. Upload your resume (PDF or DOCX)
3. The system automatically parses and extracts:
   - Name, email, phone
   - Skills and technologies
   - Work experience
   - Education

### 2. Set Job Preferences

1. Go to Settings
2. Configure filters:
   - Job titles/keywords
   - Location (remote/onsite)
   - Minimum salary
   - Industry preferences

### 3. Search & Apply

1. Click "Find Jobs" from dashboard
2. System scrapes job boards based on your criteria
3. Review matched jobs (sorted by relevance score)
4. Click "Auto-Apply" to apply to selected jobs
5. Monitor progress in real-time

### 4. Track Applications

- View all applications in the dashboard
- Filter by status: Applied, Pending, Failed
- Export to CSV for records

## 🏗️ Architecture

### Resume Parser Flow

```
PDF/DOCX → pdfminer/python-docx → Text Extraction →
spaCy NLP → Entity Recognition → Structured Data → Database
```

### Job Scraping Flow

```
User Criteria → Job Board APIs/Scraping →
Raw Job Data → Cleaning/Normalization →
NLP Matching (cosine similarity) → Ranked Jobs → Database
```

### Auto-Application Flow

```
Selected Job → Playwright Browser Launch →
Navigate to Application → Fill Form Fields →
Upload Resume → Submit → Capture Result → Log to DB
```

## 🔧 Configuration

### Supported Job Boards

1. **Indeed** - Full automation support
2. **RemoteOK** - Scraping + partial automation
3. **Wellfound** - Scraping only (requires manual application)

### Matching Algorithm

The system uses sentence-transformers to compute similarity:

- Extracts skills from resume
- Compares to job description
- Ranks jobs by cosine similarity (0-100%)
- Threshold: 60% minimum match recommended

## 🐛 Troubleshooting

### "Playwright browser not found"

```bash
playwright install chromium
```

### "ModuleNotFoundError: No module named 'sentence_transformers'"

```bash
pip install sentence-transformers
```

### "Database locked" error

- Close any other connections to the SQLite database
- Ensure only one backend instance is running

### Scraping blocked/captcha

- Add delays between requests (configured in scrapers)
- Use residential proxies (optional, advanced)
- Rotate user agents (already implemented)

## 📝 Development

### Adding a New Job Board

1. Create scraper in `backend/scrapers/new_site_scraper.py`
2. Inherit from `BaseScraper`
3. Implement required methods:
   - `search_jobs()`
   - `parse_job_listing()`
4. Add automation in `backend/automation/new_site_applicator.py`

### Running Tests

```bash
cd backend
pytest tests/
```

## 🚨 Legal & Ethical Considerations

⚠️ **Important**:

- Respect robots.txt and terms of service
- Add delays between requests (implemented)
- Don't overwhelm job boards with requests
- Review applications before submission
- This tool is for educational purposes
- Some sites prohibit automated applications

## 🎯 Roadmap

- [ ] LinkedIn integration (public listings)
- [ ] Email notifications
- [ ] Cover letter generation (local LLM)
- [ ] Chrome extension for one-click apply
- [ ] Application analytics dashboard
- [ ] Interview scheduler integration

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - use freely for personal projects

## 🙏 Acknowledgments

- sentence-transformers for NLP
- Playwright for browser automation
- FastAPI for amazing developer experience

---

**Note**: This is a powerful automation tool. Use responsibly and ethically. Always review applications before they're submitted.
