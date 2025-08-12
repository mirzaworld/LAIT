# 🚀 LAIT Platform - Launch Guide

## 🎯 Quick Start

### Local Development (Fastest)
```bash
# 1. Backend
cd backend
source venv_real/bin/activate
python app_real.py

# 2. Frontend (new terminal)
cd frontend
npm run dev

# 3. Open: http://localhost:5173
```

### Docker Compose (Recommended)
```bash
# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

## 📋 Environment Variables

| Variable | Development | Production | Description |
|----------|-------------|------------|-------------|
| `DATABASE_URL` | `sqlite:///lait.db` | `postgresql://...` | Database connection |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://...` | Redis cache URL |
| `SECRET_KEY` | `dev-key-change` | `random-256-bit-key` | Flask secret key |
| `JWT_SECRET_KEY` | `jwt-dev-key` | `random-jwt-secret` | JWT signing key |
| `FRONTEND_URL` | `http://localhost:5173` | `https://your-app.com` | CORS origin |
| `UPLOAD_FOLDER` | `./uploads` | `/app/uploads` | File upload directory |

## 🌐 Production Deployment (Render.com)

### 1. Repository Setup
```bash
# Ensure render.yaml exists (✅ already created)
git push origin main
```

### 2. Render.com Configuration
1. Connect GitHub repository
2. Render will auto-detect `render.yaml`
3. Set environment variables:
   ```
   DATABASE_URL=postgresql://...  (auto-provided by Render)
   REDIS_URL=redis://...         (add Redis service)
   SECRET_KEY=your-random-secret-256-bit
   JWT_SECRET_KEY=your-jwt-secret-256-bit
   FRONTEND_URL=https://your-app.onrender.com
   ```

### 3. Verify Deployment
```bash
# Health check
curl https://your-app.onrender.com/api/health

# API docs
open https://your-app.onrender.com/api/docs
```

## 🧪 End-to-End Demo

### 1. Health Check
```bash
curl http://localhost:5003/api/health
# Expected: {"ok": true, "timestamp": "..."}
```

### 2. User Registration
```bash
curl -X POST http://localhost:5003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "name": "Test User"
  }'
# Expected: {"token": "eyJ...", "user": {...}}
```

### 3. Login
```bash
curl -X POST http://localhost:5003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
# Expected: {"access_token": "eyJ...", "refresh_token": "eyJ..."}
```

### 4. Upload Invoice
```bash
# Create test file
echo "Legal Services: Attorney John Smith, $450/hr, 8.5 hours, Total: $3,825.00" > sample.txt

# Upload with JWT token
curl -X POST http://localhost:5003/api/invoices/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@sample.txt" \
  -F "vendor=Test Vendor"
# Expected: {"invoice_id": 1, "lines_processed": 1, ...}
```

### 5. View Dashboard
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5003/api/dashboard/metrics
# Expected: {"invoices_count": 1, "total_spend": 3825.0, ...}
```

### 6. List Invoices
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5003/api/invoices
# Expected: [{"id": 1, "vendor": "Test Vendor", ...}]
```

## 🎯 Demo Data Seeding
```bash
# Seed demo user + 10 sample invoices
make seed

# Login with demo credentials
# Email: demo@lait.com
# Password: demo123!

# Or use frontend: http://localhost:5173
```

## 📊 API Documentation

### Interactive Swagger UI
- **Development**: http://localhost:5003/api/docs
- **Production**: https://your-app.onrender.com/api/docs

### OpenAPI Specification
- **JSON**: `/api/openapi.json`

### Postman Collection
```bash
# Import collection from:
docs/postman_collection.json

# Environment variables:
# - base_url: http://localhost:5003 (dev) or https://your-app.com (prod)
# - token: (auto-populated after login)
```

## 🔧 Development Commands

```bash
# Backend health check
make health

# Seed demo data
make seed

# Dashboard metrics
make metrics

# Run smoke tests
bash scripts/smoke.sh

# Test all API routes
python scripts/route_probe.py

# Run E2E tests (requires dependencies)
pytest tests/test_e2e_pytest.py -v
```

## 📁 Project Structure
```
LAIT/
├── backend/           # Flask API server
│   ├── app_real.py    # Main application
│   ├── models/        # Database models
│   ├── services/      # Business logic
│   └── uploads/       # File uploads
├── frontend/          # React application
│   ├── src/           # Source code
│   └── dist/          # Built assets
├── docs/              # API documentation
├── scripts/           # Automation scripts
├── tests/             # Test suites
├── docker-compose.yml # Local development
└── render.yaml        # Production deployment
```

## ⚠️ Known Limitations

### ML Service Fallback
- **Issue**: If ML models not present, uses deterministic fallback
- **Impact**: Scoring uses rule-based logic instead of ML models
- **Solution**: Train models with `python scripts/train_real_models.py`

### File Upload Limits
- **Limit**: 16MB per file (configurable)
- **Formats**: TXT, PDF, CSV (extensible)

### Authentication
- **JWT Expiry**: 24 hours access token, 7 days refresh token
- **Security**: bcrypt password hashing, rate limiting enabled

### Database
- **Development**: SQLite (single file)
- **Production**: PostgreSQL (recommended)
- **Migration**: Manual schema updates required

## 🚑 Troubleshooting

### Backend Won't Start
```bash
# Check Python environment
cd backend && source venv_real/bin/activate
python --version

# Install dependencies
pip install -r requirements.txt

# Check database
python -c "from app_real import db; db.create_all()"
```

### Frontend Build Issues
```bash
cd frontend
npm install
npm run build
```

### Docker Issues
```bash
# Rebuild containers
docker compose down
docker compose up --build

# View logs
docker compose logs -f lait-app
```

### API Connectivity
```bash
# Check if backend is running
curl http://localhost:5003/api/health

# Check CORS configuration
curl -H "Origin: http://localhost:5173" \
  http://localhost:5003/api/health
```

## 🎉 Success Verification

✅ **Backend**: `curl http://localhost:5003/api/health` returns `{"ok": true}`  
✅ **Frontend**: `http://localhost:5173` loads login page  
✅ **Authentication**: Can register/login users  
✅ **File Upload**: Can upload and process invoices  
✅ **Dashboard**: Displays metrics and analytics  
✅ **API Docs**: Interactive documentation at `/api/docs`  
✅ **Demo Data**: `make seed` creates sample invoices  

---

## 📞 Support

- **API Documentation**: http://localhost:5003/api/docs
- **Project Repository**: GitHub.com/mirzaworld/LAIT
- **Issue Tracker**: Create GitHub issues for bugs/features

**🎯 You're ready to launch! 🚀**
