# 📁 Complete Project Structure

```
autojobapply/
│
├── 📄 README.md                    # Main documentation
├── 📄 QUICK_START.md              # Quick setup guide
├── 📄 DEPLOYMENT.md               # Deployment instructions
├── 📄 PROJECT_STRUCTURE.md        # This file
├── 📄 .gitignore                  # Git ignore file
├── 🐳 docker-compose.yml          # Docker configuration
│
├── 🔧 setup.sh                    # Automated setup script
├── 🚀 start-all.sh                # Start both services
├── 🐍 start-backend.sh            # Start backend only
├── ⚛️  start-frontend.sh           # Start frontend only
├── 🧪 test_system.py              # System test script
│
├── 📁 backend/                     # Python FastAPI backend
│   ├── 📄 main.py                 # FastAPI application entry
│   ├── 📄 config.py               # Configuration
│   ├── 📄 requirements.txt        # Python dependencies
│   ├── 📄 .env                    # Environment variables
│   ├── 📄 .env.example            # Example env file
│   │
│   ├── 📁 database/               # Database layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 db.py              # Database connection
│   │   └── 📄 models.py          # SQLAlchemy models
│   │
│   ├── 📁 parsers/                # Resume & NLP parsing
│   │   ├── 📄 __init__.py
│   │   ├── 📄 resume_parser.py   # PDF/DOCX parser
│   │   └── 📄 nlp_matcher.py     # Job matching logic
│   │
│   ├── 📁 scrapers/               # Job board scrapers
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_scraper.py    # Abstract base class
│   │   ├── 📄 indeed_scraper.py  # Indeed scraper
│   │   ├── 📄 remoteok_scraper.py # RemoteOK scraper
│   │   └── 📄 wellfound_scraper.py # Wellfound scraper
│   │
│   ├── 📁 automation/             # Auto-apply automation
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_applicator.py # Base automation class
│   │   ├── 📄 indeed_applicator.py # Indeed automation
│   │   └── 📄 form_filler.py     # Generic form filling
│   │
│   ├── 📁 routers/                # API endpoints
│   │   ├── 📄 __init__.py
│   │   ├── 📄 resume.py          # Resume endpoints
│   │   ├── 📄 jobs.py            # Job search endpoints
│   │   └── 📄 applications.py    # Application endpoints
│   │
│   ├── 📁 utils/                  # Utilities
│   │   ├── 📄 __init__.py
│   │   ├── 📄 logger.py          # Logging setup
│   │   └── 📄 helpers.py         # Helper functions
│   │
│   ├── 📁 tests/                  # Unit tests
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_parsers.py
│   │   ├── 📄 test_scrapers.py
│   │   └── 📄 test_automation.py
│   │
│   └── 📁 venv/                   # Python virtual env (gitignored)
│
├── 📁 frontend/                    # Next.js React frontend
│   ├── 📄 package.json
│   ├── 📄 package-lock.json
│   ├── 📄 tsconfig.json
│   ├── 📄 next.config.js
│   ├── 📄 tailwind.config.ts
│   ├── 📄 postcss.config.js
│   ├── 📄 .env.local              # Frontend environment
│   │
│   ├── 📁 app/                     # Next.js 14 app directory
│   │   ├── 📄 layout.tsx          # Root layout
│   │   ├── 📄 page.tsx            # Home page (upload)
│   │   ├── 📄 globals.css         # Global styles
│   │   │
│   │   ├── 📁 dashboard/          # Dashboard page
│   │   │   └── 📄 page.tsx
│   │   │
│   │   ├── 📁 settings/           # Settings page
│   │   │   └── 📄 page.tsx
│   │   │
│   │   └── 📁 api/                # API proxy routes (optional)
│   │       └── 📄 [...].ts
│   │
│   ├── 📁 components/             # React components
│   │   ├── 📄 ResumeUpload.tsx
│   │   ├── 📄 JobFilters.tsx
│   │   ├── 📄 ApplicationLog.tsx
│   │   ├── 📄 JobCard.tsx
│   │   ├── 📄 Navbar.tsx
│   │   └── 📄 LoadingSpinner.tsx
│   │
│   ├── 📁 lib/                     # Utilities
│   │   ├── 📄 api.ts              # API client
│   │   ├── 📄 utils.ts            # Helper functions
│   │   └── 📄 types.ts            # TypeScript types
│   │
│   ├── 📁 hooks/                   # Custom React hooks
│   │   ├── 📄 useJobs.ts
│   │   ├── 📄 useApplications.ts
│   │   └── 📄 useResume.ts
│   │
│   ├── 📁 public/                  # Static assets
│   │   ├── 📄 favicon.ico
│   │   └── 📁 images/
│   │
│   └── 📁 node_modules/           # NPM packages (gitignored)
│
├── 📁 data/                        # Application data (gitignored)
│   ├── 📄 autojobapply.db         # SQLite database
│   │
│   ├── 📁 resumes/                # Uploaded resumes
│   │   ├── 📄 user1_resume.pdf
│   │   └── 📄 user2_resume.docx
│   │
│   └── 📁 logs/                   # Application logs
│       ├── 📄 autojobapply_2024-01-01.log
│       └── 📄 autojobapply_2024-01-02.log
│
└── 📁 docs/                        # Additional documentation
    ├── 📄 API.md                  # API documentation
    ├── 📄 ARCHITECTURE.md         # System architecture
    ├── 📄 CONTRIBUTING.md         # Contribution guidelines
    └── 📄 FAQ.md                  # Frequently asked questions
```

## 📊 Key Files Explained

### Backend Core Files

| File                 | Purpose                                          |
| -------------------- | ------------------------------------------------ |
| `main.py`            | FastAPI app initialization, middleware, routes   |
| `config.py`          | Configuration management                         |
| `database/models.py` | Database schema (User, Resume, Job, Application) |
| `database/db.py`     | Database connection and session management       |

### Parsing & Matching

| File                       | Purpose                                                |
| -------------------------- | ------------------------------------------------------ |
| `parsers/resume_parser.py` | Extract text from PDF/DOCX and parse structure         |
| `parsers/nlp_matcher.py`   | Match jobs to resume using NLP (sentence-transformers) |

### Scraping

| File                           | Purpose                              |
| ------------------------------ | ------------------------------------ |
| `scrapers/base_scraper.py`     | Abstract base class for all scrapers |
| `scrapers/indeed_scraper.py`   | Scrape job listings from Indeed      |
| `scrapers/remoteok_scraper.py` | Scrape remote jobs from RemoteOK     |

### Automation

| File                              | Purpose                                       |
| --------------------------------- | --------------------------------------------- |
| `automation/indeed_applicator.py` | Playwright automation for Indeed applications |
| `automation/form_filler.py`       | Generic form filling utilities                |

### Frontend Pages

| File                     | Purpose                              |
| ------------------------ | ------------------------------------ |
| `app/page.tsx`           | Resume upload page                   |
| `app/dashboard/page.tsx` | Job search and application dashboard |
| `app/settings/page.tsx`  | User preferences and filters         |

## 🔧 Configuration Files

### Backend Environment (`.env`)

```env
DATABASE_URL=sqlite:///../data/autojobapply.db
UPLOAD_DIR=../data/resumes
LOG_DIR=../data/logs
FRONTEND_URL=http://localhost:3000
BACKEND_PORT=8000
```

### Frontend Environment (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📦 Dependencies

### Backend (`requirements.txt`)

- **Web Framework**: FastAPI, Uvicorn
- **Database**: SQLAlchemy
- **Parsing**: pdfminer, python-docx, PyMuPDF
- **Scraping**: BeautifulSoup4, requests, Playwright
- **NLP**: spaCy, sentence-transformers
- **Utilities**: python-dotenv, loguru

### Frontend (`package.json`)

- **Framework**: Next.js 14, React 18
- **Styling**: Tailwind CSS
- **Icons**: lucide-react
- **HTTP**: axios
- **Date**: date-fns

## 🗄️ Database Schema

### Tables

1. **users** - User profiles
2. **resumes** - Parsed resume data
3. **job_preferences** - User job search preferences
4. **jobs** - Job listings from various sources
5. **job_applications** - Application tracking

### Relationships

```
users (1) ──→ (many) resumes
users (1) ──→ (1) job_preferences
users (1) ──→ (many) job_applications
jobs (1) ──→ (many) job_applications
```

## 🔄 Data Flow

```
1. UPLOAD
   User → Frontend → Backend → Resume Parser → Database

2. SEARCH
   User → Frontend → Backend → Scrapers → NLP Matcher → Database

3. APPLY
   User → Frontend → Backend → Playwright → Job Site → Database (log)

4. TRACK
   User → Frontend → Backend → Database → Frontend (display)
```

## 📝 API Endpoints

### Resume

- `POST /api/resume/upload` - Upload and parse resume
- `GET /api/resume/user/{user_id}` - Get user's resume
- `DELETE /api/resume/{resume_id}` - Delete resume

### Jobs

- `POST /api/jobs/search` - Search for jobs
- `GET /api/jobs/{job_id}` - Get job details
- `GET /api/jobs/user/{user_id}/matches` - Get matched jobs

### Applications

- `POST /api/applications/apply` - Apply to a job
- `POST /api/applications/bulk-apply` - Apply to multiple jobs
- `GET /api/applications/user/{user_id}` - Get user's applications
- `GET /api/applications/{application_id}` - Get application details

## 🎨 Frontend Routes

- `/` - Home (resume upload)
- `/dashboard` - Job search and applications
- `/settings` - User preferences

## 🧪 Testing

Run all tests:

```bash
python test_system.py
```

Individual tests:

```bash
cd backend
pytest tests/test_parsers.py
pytest tests/test_scrapers.py
pytest tests/test_automation.py
```

## 📚 Additional Resources

- API Documentation: `http://localhost:8000/docs`
- Logs: `data/logs/`
- Database: `data/autojobapply.db`
