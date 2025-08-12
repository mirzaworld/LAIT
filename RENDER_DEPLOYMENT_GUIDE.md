# Render.com Production Deployment Guide

## 🚀 LAIT Backend Production Deployment on Render

### Prerequisites
- GitHub repository with LAIT code
- Render.com account
- Domain name (optional)

---

## 📋 Step-by-Step Deployment

### 1. **Create PostgreSQL Database**

1. Go to Render Dashboard → **New** → **PostgreSQL**
2. Configure database:
   ```
   Name: lait-postgres-prod
   Database: lait_prod
   User: lait_user
   Region: Oregon (US-West) or closest to your users
   PostgreSQL Version: 15
   Plan: Starter ($7/month) or Free (with limitations)
   ```
3. **Save the connection details** - you'll need the `DATABASE_URL`

### 2. **Create Redis Instance**

1. Go to Render Dashboard → **New** → **Redis**
2. Configure Redis:
   ```
   Name: lait-redis-prod
   Region: Oregon (US-West) - same as PostgreSQL
   Plan: Starter ($7/month) or Free (25MB)
   ```
3. **Save the Redis URL** - you'll need the `REDIS_URL`

### 3. **Create Web Service**

1. Go to Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repository: `mirzaworld/LAIT`
3. Configure the service:

#### **Basic Settings:**
```
Name: lait-backend-prod
Region: Oregon (US-West) - same as database/redis
Branch: main
Root Directory: . (leave blank)
Runtime: Docker
```

#### **Build & Deploy Settings:**
```
Dockerfile Path: Dockerfile.prod
Build Command: (leave blank - Docker handles this)
Start Command: (leave blank - uses ENTRYPOINT)
```

#### **Environment Variables:**
Add the following environment variables in Render dashboard:

```bash
# Required Environment Variables
JWT_SECRET=your-super-secure-jwt-secret-key-2025-prod
DATABASE_URL=postgresql://lait_user:password@hostname:5432/lait_prod
REDIS_URL=redis://red-xxxxx:6379

# Optional Environment Variables
FLASK_ENV=production
PYTHONPATH=/app/backend
PORT=5003

# Security & Performance
FLASK_DEBUG=false
SECRET_KEY=your-flask-secret-key-different-from-jwt
```

#### **Advanced Settings:**
```
Auto-Deploy: Yes
Health Check Path: /api/health
Port: 5003 (or leave blank to use default)
```

---

## 🔧 Exact Render Service Settings

### **Service Configuration**
```yaml
Name: lait-backend-prod
Environment: Docker
Region: Oregon (US-West)
Branch: main
Auto-Deploy: Yes
```

### **Build Settings**
```yaml
Dockerfile Path: Dockerfile.prod
Build Command: (empty - handled by Docker)
Start Command: (empty - uses ENTRYPOINT)
```

### **Environment Variables** (Critical!)
```bash
JWT_SECRET=lait-prod-jwt-2025-super-secure-key-change-me
DATABASE_URL=<from-postgres-service>
REDIS_URL=<from-redis-service>
FLASK_ENV=production
PYTHONPATH=/app/backend
```

### **Health Check**
```yaml
Health Check Path: /api/health
Health Check Grace Period: 60 seconds
```

### **Scaling & Resources**
```yaml
Plan: Starter ($7/month minimum for production)
CPU: 0.5 vCPU
Memory: 512 MB
Instances: 1 (can scale up)
```

---

## 🔍 Post-Deployment Verification

### 1. **Check Service Health**
```bash
curl https://your-app-name.onrender.com/api/health
# Expected response: {"ok": true, "timestamp": "..."}
```

### 2. **Verify ML Status**
```bash
curl https://your-app-name.onrender.com/api/ml/status
# Expected response: {"service_available": false, "fallback_mode": true, ...}
```

### 3. **Test Authentication**
```bash
curl -X POST https://your-app-name.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

---

## ⚠️ Important Security Notes

1. **Change Default Secrets**: Replace all default JWT and Flask secrets
2. **Database Security**: Use Render's managed PostgreSQL for automatic backups
3. **HTTPS Only**: Render provides automatic SSL certificates
4. **Environment Variables**: Never commit secrets to Git - use Render's env vars only

---

## 📊 Expected Costs (Monthly)

- **Web Service (Starter)**: $7/month
- **PostgreSQL (Starter)**: $7/month  
- **Redis (Starter)**: $7/month
- **Total**: ~$21/month for production-ready setup

*Free tiers available for development/testing*

---

## 🚨 Troubleshooting

### Build Failures
- Check Dockerfile.prod syntax
- Verify requirements.txt has all dependencies
- Check build logs in Render dashboard

### Runtime Issues  
- Check environment variables are set correctly
- Verify DATABASE_URL format: `postgresql://user:pass@host:port/db`
- Monitor logs in Render dashboard

### Database Connection Issues
- Ensure PostgreSQL service is in same region
- Check DATABASE_URL has correct credentials
- Verify network connectivity (Render handles this automatically)

---

## 📈 Monitoring & Maintenance

1. **Logs**: Available in Render dashboard under service → Logs
2. **Metrics**: CPU, Memory, Response times in dashboard
3. **Alerts**: Set up in Render dashboard for downtime/errors
4. **Backups**: PostgreSQL automatically backed up by Render
5. **Updates**: Auto-deploy on Git push to main branch

---

## ✅ Deployment Checklist

- [ ] PostgreSQL database created
- [ ] Redis instance created  
- [ ] Environment variables configured
- [ ] Health check endpoint working
- [ ] JWT_SECRET and DATABASE_URL set
- [ ] Auto-deploy enabled
- [ ] SSL certificate active (automatic)
- [ ] Custom domain configured (optional)
- [ ] Monitoring alerts set up
