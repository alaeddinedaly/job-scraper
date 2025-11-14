# 🌐 Deployment Guide

This guide covers deploying AutoJobApply to various free hosting platforms.

## 🚀 Deployment Options

### 1. Local Machine (Recommended for Personal Use)

**Pros:**

- 100% private and secure
- No rate limits
- Full control over data
- Can run browser automation

**Setup:**

```bash
./setup.sh
./start-all.sh
```

---

### 2. Railway.app (Free Tier)

**Backend Deployment:**

1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI:

```bash
npm install -g @railway/cli
```

3. Deploy backend:

```bash
cd backend
railway init
railway up
```

4. Set environment variables in Railway dashboard:

```
DATABASE_URL=postgresql://... (Railway provides this)
UPLOAD_DIR=/data/resumes
LOG_DIR=/data/logs
```

**Frontend Deployment:**

1. Deploy to Vercel (see below)
2. Update `NEXT_PUBLIC_API_URL` to Railway backend URL

---

### 3. Render.com (Free Tier)

**Backend:**

1. Create `render.yaml` in project root:

```yaml
services:
  - type: web
    name: autojobapply-api
    env: python
    buildCommand: "pip install -r backend/requirements.txt && python -m spacy download en_core_web_sm"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.10.0
```

2. Connect GitHub repo to Render
3. Deploy will start automatically

**Limitations:**

- Free tier spins down after 15 min inactivity
- No persistent file storage (use cloud storage for resumes)

---

### 4. Vercel (Frontend Only)

**Deploy Frontend:**

```bash
cd frontend
npm install -g vercel
vercel
```

**Environment Variables:**

- `NEXT_PUBLIC_API_URL`: Your backend URL

---

### 5. Replit (Quick Demo)

**All-in-One Deployment:**

1. Go to [replit.com](https://replit.com)
2. Create new Python Repl
3. Upload all backend files
4. Install dependencies:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

5. Run:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**For Frontend:**

- Create separate Node.js Repl
- Upload frontend files
- Update API URL to backend Repl URL
- Run: `npm run dev`

---

## 🔒 Security Considerations

### Production Checklist

- [ ] Set strong SECRET_KEY for JWT if implementing auth
- [ ] Use HTTPS only
- [ ] Enable CORS only for trusted domains
- [ ] Store resumes encrypted
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Use environment variables for all secrets
- [ ] Enable logging and monitoring
- [ ] Implement user authentication
- [ ] Add CAPTCHA for form submissions

### Environment Variables

**Backend (.env):**

```env
# Database
DATABASE_URL=sqlite:///./data/autojobapply.db

# Storage
UPLOAD_DIR=./data/resumes
LOG_DIR=./data/logs

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://yourfrontend.com

# Scraping (optional)
USER_AGENT=Mozilla/5.0...
PROXY_URL=http://proxy:port
```

**Frontend (.env.local):**

```env
NEXT_PUBLIC_API_URL=https://your-backend.com
```

---

## 📦 Docker Deployment

**Build and Run:**

```bash
docker-compose up -d
```

**Production Docker Compose:**

```yaml
version: "3.8"

services:
  backend:
    build: ./backend
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - resume-data:/app/data
    environment:
      - DATABASE_URL=postgresql://...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    restart: always
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  # Optional: Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  resume-data:
```

---

## 🌍 Cloud Storage for Resumes

### AWS S3 (Free Tier)

```python
# backend/utils/s3_storage.py
import boto3
from botocore.exceptions import ClientError

class S3Storage:
    def __init__(self):
        self.s3 = boto3.client('s3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
        )
        self.bucket = os.getenv('S3_BUCKET_NAME')

    def upload_resume(self, file_path, object_name):
        try:
            self.s3.upload_file(file_path, self.bucket, object_name)
            return True
        except ClientError as e:
            print(f"Error: {e}")
            return False
```

### Cloudflare R2 (Free 10GB)

Similar to S3 but with zero egress fees.

---

## 🔄 Database Options

### SQLite (Default - Local Only)

- Perfect for single-user/local deployment
- No setup required
- File-based

### PostgreSQL (Production)

**Render.com (Free):**

- Auto-provisioned with deployment
- 100MB storage free

**Supabase (Free Tier):**

```python
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
```

**Migration:**

```bash
# Export SQLite
sqlite3 data/autojobapply.db .dump > backup.sql

# Import to PostgreSQL
psql $DATABASE_URL < backup.sql
```

---

## 📊 Monitoring

### Free Monitoring Tools

1. **UptimeRobot** - Check if service is up
2. **Sentry** - Error tracking (free tier)
3. **LogTail** - Log aggregation

### Add to Backend:

```python
# main.py
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0
)
```

---

## 🚨 Troubleshooting Deployments

### Backend Issues

**"Module not found":**

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
playwright install chromium
```

**"Database locked":**

- Use PostgreSQL in production
- Or set `check_same_thread=False` for SQLite

**"Port already in use":**

```bash
# Find process
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Frontend Issues

**"Network error":**

- Check NEXT_PUBLIC_API_URL is correct
- Verify CORS settings on backend
- Check if backend is running

**Build fails:**

```bash
rm -rf .next node_modules
npm install
npm run build
```

---

## 📈 Scaling Considerations

### When to Scale

- More than 100 users
- 1000+ job applications per day
- Need for high availability

### Scaling Strategy

1. **Horizontal Scaling:**

   - Deploy multiple backend instances
   - Use load balancer (Nginx/Cloudflare)
   - Implement job queue (Redis + Celery)

2. **Database:**

   - Upgrade to managed PostgreSQL
   - Add read replicas
   - Implement caching (Redis)

3. **File Storage:**

   - Move to S3/R2
   - Use CDN for static assets

4. **Background Jobs:**
   - Use Celery for scraping
   - Redis for job queue
   - Separate workers for automation

---

## 💰 Cost Estimation

### Free Tier (Recommended Start)

- **Railway**: Backend (500 hours/month)
- **Vercel**: Frontend (unlimited)
- **Supabase**: PostgreSQL (500MB)
- **Total**: $0/month

### Paid Tier (Heavy Use)

- **Railway Pro**: $5/month
- **Vercel Pro**: $20/month
- **Database**: $15/month
- **S3 Storage**: $5/month
- **Total**: ~$45/month

---

## ✅ Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database migrations run
- [ ] spaCy models downloaded
- [ ] Playwright browsers installed
- [ ] CORS configured correctly
- [ ] Error tracking enabled
- [ ] Logging configured
- [ ] Health checks working
- [ ] Rate limiting implemented
- [ ] User authentication (if multi-user)
- [ ] Backup strategy in place

---

## 🆘 Getting Help

- Check logs: `tail -f data/logs/*.log`
- Test API: `http://localhost:8000/docs`
- Run tests: `python test_system.py`
- GitHub Issues for bugs

---

**Note**: Always test thoroughly in a staging environment before deploying to production!
