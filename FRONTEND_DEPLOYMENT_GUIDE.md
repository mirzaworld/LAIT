# Frontend Production Deployment Guide

## 🚀 LAIT Frontend Production Deployment

### 📋 Overview

The LAIT frontend is built with Vite and deployed using a multi-stage Docker container with Nginx for production serving and API proxying.

---

## 🏗️ Build Process

### Local Build Verification
```bash
# Ensure build works locally
npm run build

# Verify dist/ directory is created
ls -la dist/
# Should show: index.html, assets/
```

### Docker Build Test
```bash
# Build the production container
docker build -f Dockerfile.frontend -t lait-frontend-prod .

# Test run with environment variable
docker run -e BACKEND_URL="your-backend-url.com:5003" -p 8080:80 lait-frontend-prod
```

---

## 🌐 Render.com Deployment

### Step 1: Create Web Service

1. Go to Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repository: `mirzaworld/LAIT`
3. Configure the service:

#### **Basic Settings:**
```yaml
Name: lait-frontend-prod
Region: Oregon (US-West)
Branch: main
Runtime: Docker
```

#### **Build Configuration:**
```yaml
Dockerfile Path: Dockerfile.frontend
Build Command: (leave empty)
Start Command: (leave empty - uses ENTRYPOINT)
```

#### **Environment Variables:**
```bash
# CRITICAL: Set your backend URL
BACKEND_URL=your-backend-service.onrender.com

# Example if backend is on Render:
BACKEND_URL=lait-backend-prod.onrender.com

# For local development:
BACKEND_URL=localhost:5003
```

#### **Service Settings:**
```yaml
Health Check Path: /health
Auto-Deploy: Yes
Plan: Starter ($7/month) or Free
Port: 80 (auto-detected)
```

### Step 2: Configure Custom Domain (Optional)
```bash
# In Render Dashboard → Settings → Custom Domains
# Add: yourdomain.com
# Render will provide SSL certificate automatically
```

---

## 🚄 Railway Deployment

### Step 1: Create New Project

1. Go to Railway Dashboard → **New Project**
2. **Deploy from GitHub repo**: Connect `mirzaworld/LAIT`
3. Configure the service:

#### **Service Configuration:**
```yaml
Name: lait-frontend
Root Directory: . (leave empty)
Build Command: (auto-detected from Dockerfile)
Start Command: (auto-detected from Dockerfile)
```

#### **Environment Variables:**
```bash
# Add in Railway Dashboard → Variables tab
BACKEND_URL=your-backend-railway-url.railway.app

# Example format:
BACKEND_URL=lait-backend-production.up.railway.app
```

#### **Dockerfile Configuration:**
```yaml
Dockerfile Path: Dockerfile.frontend
```

### Step 2: Configure Domain (Optional)
```bash
# In Railway Dashboard → Settings → Domains
# Add custom domain or use Railway-provided domain
```

---

## 🔧 Environment Variable Configuration

### Backend URL Examples

#### **Production (Render):**
```bash
BACKEND_URL=lait-backend-prod.onrender.com
```

#### **Production (Railway):**
```bash
BACKEND_URL=your-app-name.up.railway.app
```

#### **Production (Custom Domain):**
```bash
BACKEND_URL=api.yourdomain.com
```

#### **Development/Staging:**
```bash
BACKEND_URL=localhost:5003
```

### Important Notes:
- **No Protocol**: Don't include `http://` or `https://` in BACKEND_URL
- **No Port for HTTPS**: For production deployments with SSL, don't include `:443`
- **Include Port for HTTP**: For development or HTTP deployments, include the port

---

## 📊 Complete Deployment Steps

### For Render.com:

1. **Create Backend Service First** (from previous guide)
2. **Create Frontend Service:**
   ```
   Repository: mirzaworld/LAIT
   Dockerfile: Dockerfile.frontend
   Environment Variable: BACKEND_URL=your-backend-service.onrender.com
   Health Check: /health
   ```
3. **Deploy and Test:**
   ```bash
   # Test frontend
   curl https://your-frontend.onrender.com/health
   # Expected: "healthy"

   # Test API proxy
   curl https://your-frontend.onrender.com/api/health
   # Expected: {"ok": true, "timestamp": "..."}
   ```

### For Railway:

1. **Create Backend Service First**
2. **Create Frontend Service:**
   ```
   New Project → GitHub → mirzaworld/LAIT
   Variables → BACKEND_URL=your-backend.railway.app
   ```
3. **Deploy and Test:**
   ```bash
   # Test frontend
   curl https://your-app.up.railway.app/health
   
   # Test API proxy  
   curl https://your-app.up.railway.app/api/health
   ```

---

## ⚠️ Troubleshooting

### Build Issues:
```bash
# Check build logs for:
npm WARN deprecated
Module not found errors
Permission denied errors
```

### Runtime Issues:
```bash
# Check nginx logs for:
upstream prematurely closed connection
502 Bad Gateway
CORS errors
```

### API Proxy Issues:
```bash
# Verify BACKEND_URL is set correctly:
echo $BACKEND_URL

# Test direct backend connection:
curl http://$BACKEND_URL/api/health
```

---

## 🎯 Expected Costs

### Render.com:
- **Frontend**: $0-7/month (Free tier available, Starter recommended)
- **Backend**: $7/month (Starter minimum for production)
- **Database**: $7/month (PostgreSQL Starter)
- **Total**: ~$14-21/month

### Railway:
- **Frontend + Backend**: $5-20/month (usage-based)
- **Database**: Included in usage or separate PostgreSQL addon
- **Total**: ~$10-25/month

---

## ✅ Production Checklist

- [ ] Frontend builds successfully (`npm run build`)
- [ ] Docker image builds without errors
- [ ] Environment variable `BACKEND_URL` is set correctly
- [ ] Health check endpoint `/health` returns "healthy"  
- [ ] API proxy `/api/*` routes to backend correctly
- [ ] SSL certificates are active (automatic on Render/Railway)
- [ ] Custom domain configured (optional)
- [ ] Auto-deploy from `main` branch enabled
- [ ] Both frontend and backend services are running
- [ ] End-to-end testing completed

---

## 🚀 Quick Deploy Commands

### Test Entire Stack Locally:
```bash
# Terminal 1: Start backend
cd backend && python app_real.py

# Terminal 2: Build and run frontend
npm run build
docker build -f Dockerfile.frontend -t lait-frontend .
docker run -e BACKEND_URL="localhost:5003" -p 8080:80 lait-frontend

# Terminal 3: Test
curl http://localhost:8080/health        # Frontend health
curl http://localhost:8080/api/health    # API proxy
```

The frontend is now production-ready with nginx serving static files and proxying API requests!
