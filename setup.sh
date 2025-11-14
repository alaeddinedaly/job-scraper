#!/bin/bash

echo "🚀 AutoJobApply - Setup Script"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python found: $(python3 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js found: $(node --version)"

# Create project structure
echo ""
echo "📁 Creating project structure..."
mkdir -p autojobapply/{backend,frontend,data/{resumes,logs}}
cd autojobapply

# Setup Backend
echo ""
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/Scripts/activate # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23

# Resume Parsing
pdfminer.six==20221105
python-docx==1.1.0
PyMuPDF==1.23.8

# Web Scraping
beautifulsoup4==4.12.2
lxml==4.9.3
requests==2.31.0
playwright==1.40.0

# NLP and Matching
spacy==3.7.2
sentence-transformers==2.2.2
scikit-learn==1.3.2

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dateutil==2.8.2
loguru==0.7.2
EOF

# Install dependencies
echo "📦 Installing Python packages (this may take a few minutes)..."
pip install -r requirements.txt

# Download spaCy model
echo "📚 Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
playwright install chromium

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=sqlite:///../data/autojobapply.db
UPLOAD_DIR=../data/resumes
LOG_DIR=../data/logs
FRONTEND_URL=http://localhost:3000
BACKEND_PORT=8000
EOF

echo -e "${GREEN}✓${NC} Backend setup complete!"

# Setup Frontend
cd ../frontend
echo ""
echo "⚛️  Setting up Next.js frontend..."

# Initialize Next.js (skip interactive prompts)
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias="@/*" --use-npm << 'PROMPTS'
y
PROMPTS

# Install additional dependencies
echo "📦 Installing frontend packages..."
npm install axios date-fns lucide-react

# Create .env.local
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

echo -e "${GREEN}✓${NC} Frontend setup complete!"

# Create start scripts
cd ..
echo ""
echo "📝 Creating startup scripts..."

# Backend start script
cat > start-backend.sh << 'EOF'
#!/bin/bash
cd backend
source venv/Scripts/activate
uvicorn main:app --reload --port 8000
EOF
chmod +x start-backend.sh

# Frontend start script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
cd frontend
npm run dev
EOF
chmod +x start-frontend.sh

# Combined start script
cat > start-all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting AutoJobApply..."
echo ""

# Start backend in background
cd backend
source venv/Scripts/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

echo "✓ Backend started (PID: $BACKEND_PID)"

# Wait a bit for backend to start
sleep 3

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo ""
echo "======================================"
echo "🎉 AutoJobApply is running!"
echo "======================================"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
chmod +x start-all.sh

# Create README
cat > QUICK_START.md << 'EOF'
# 🚀 Quick Start Guide

## First Time Setup

Run this once to install everything:
```bash
./setup.sh
```

## Running the Application

### Option 1: Start Everything (Recommended)
```bash
./start-all.sh
```

### Option 2: Start Separately

**Terminal 1 - Backend:**
```bash
cd backend
source venv/Scripts/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Usage

1. Upload your resume (PDF or DOCX)
2. Go to Dashboard
3. Search for jobs with keywords
4. Click "Auto-Apply" on matched jobs
5. Track applications in the dashboard

## Troubleshooting

### Backend won't start
```bash
cd backend
source venv/Scripts/activate
pip install -r requirements.txt
```

### Frontend errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database locked
```bash
rm ../data/autojobapply.db
# Restart backend to recreate database
```

## Support

- Check logs in `data/logs/`
- API documentation at http://localhost:8000/docs
- GitHub issues for bug reports
EOF

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "📖 Next steps:"
echo ""
echo "1. Start the application:"
echo "   ./start-all.sh"
echo ""
echo "2. Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "3. Upload your resume and start applying!"
echo ""
echo "For more details, see QUICK_START.md"
echo ""