# LAIT Legal Intelligence Platform - Deployment Guide

## 🚀 Quick Deploy to Free Hosting Platforms

### Option 1: Render.com (Recommended - Free Tier)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - Click "New Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the configuration
   - Your app will be live at: `https://your-app-name.onrender.com`

### Option 2: Railway.app (Free Tier)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy**
   ```bash
   railway login
   railway init
   railway up
   ```

### Option 3: Heroku (Free Tier - Limited)

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Deploy**
   ```bash
   heroku create lait-legal-intelligence
   heroku config:set FLASK_APP=backend/enhanced_app.py
   heroku config:set FLASK_ENV=production
   git push heroku main
   ```

## 🔧 Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite for development)

### Quick Start
```bash
# Clone the repository
git clone <your-repo-url>
cd LAIT

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m nltk.downloader punkt

# Frontend setup
cd ..
npm install
npm run build

# Start the application
cd backend
PYTHONPATH=.. python enhanced_app.py
```

## 🌐 Production Environment Variables

Create a `.env` file in the root directory:

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=5003
DEBUG=False
FLASK_APP=backend/enhanced_app.py

# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0

# External APIs (Optional)
COURTLISTENER_API_TOKEN=your-courtlistener-token
```

## 📊 Features Status

### ✅ Working Features
- **ML Models**: Risk prediction, outlier detection, spend analysis
- **Live Data Collection**: Real-time legal data scraping
- **Legal Intelligence**: Court case analysis, attorney verification
- **Dashboard**: Real-time metrics and analytics
- **Invoice Management**: Upload, analysis, and processing
- **Vendor Analytics**: Performance tracking and risk assessment
- **API Health**: Monitoring and diagnostics

### 🔧 Technical Stack
- **Backend**: Flask + SQLAlchemy + ML Models
- **Frontend**: React + TypeScript + Tailwind CSS
- **Database**: PostgreSQL/SQLite
- **ML**: Scikit-learn, NLTK, Custom Models
- **Real-time**: Socket.IO, WebSocket
- **Deployment**: Docker, Render, Railway, Heroku

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   export PYTHONPATH=/path/to/your/project
   ```

2. **ML Model Loading**
   ```bash
   python -m nltk.downloader punkt
   ```

3. **Database Connection**
   - Check DATABASE_URL in environment variables
   - Ensure database is running and accessible

4. **Frontend Build Issues**
   ```bash
   npm install
   npm run build
   ```

## 📈 Monitoring

The application includes built-in monitoring:
- Health check endpoint: `/api/health`
- ML model status: `/api/ml/test`
- System diagnostics: `/api/diagnostics`

## 🔒 Security

- JWT authentication
- Rate limiting
- CORS configuration
- Input validation
- SQL injection protection

## 📞 Support

For deployment issues:
1. Check the logs in your hosting platform
2. Verify environment variables
3. Test locally first
4. Check the health endpoint: `/api/health`

---

**🎉 Your LAIT Legal Intelligence Platform is now ready for deployment!** 