# LAIT Production Deployment Guide - Render.com
# ==============================================

## 🎯 Quick Deployment Overview

This guide covers deploying LAIT with production-ready configurations:
- **Backend**: Gunicorn WSGI server with `app_real.py`
- **Frontend**: Nginx-served React SPA with environment injection
- **Database**: PostgreSQL 15 with Redis caching
- **Deployment**: Render.com Blueprint automation

## 📋 Deployment Files Created

### Backend Production Files
```
backend/
├── start_gunicorn.sh          # Production Gunicorn startup script
├── Dockerfile.prod            # Multi-stage production container  
└── requirements.txt           # Already includes gunicorn==21.2.0
```

### Frontend Production Files  
```
Dockerfile.frontend            # Enhanced Nginx + React build
```

### Deployment Blueprint
```
render.yaml                    # Complete Render.com infrastructure
```

## 🚀 One-Click Deployment Steps

### 1. Deploy via Render Blueprint
1. Push all files to your GitHub repository
2. Go to [Render.com](https://render.com) → **New** → **Blueprint**
3. Connect your GitHub repo and select branch
4. Click **"Apply Blueprint"** - Render creates everything automatically:
   - PostgreSQL database (`lait-postgres`)
   - Redis cache (`lait-redis`) 
   - Backend API service (`lait-api`)
   - Frontend static site (`lait-web`)

### 2. Critical Post-Deployment Configuration

#### ⚠️ REQUIRED: Set Frontend API URL
**This is the ONLY manual step required:**

1. Wait for initial deployment (5-10 minutes)
2. Go to Render Dashboard → **`lait-web`** service
3. Click **"Environment"** tab  
4. Set `VITE_API_BASE` to your backend URL:
   ```
   VITE_API_BASE = https://lait-api.onrender.com
   ```
   *(Replace with your actual backend URL from the `lait-api` service)*
5. Click **"Save Changes"** - frontend rebuilds automatically

## 🏗️ Architecture & Environment Variables

### Backend Service (`lait-api`)
**Auto-configured by Blueprint:**

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Flask environment mode |
| `FLASK_DEBUG` | `false` | Debug disabled for security |
| `JWT_SECRET_KEY` | *Auto-generated* | Secure token signing |
| `DATABASE_URL` | *Auto-linked* | PostgreSQL connection |  
| `REDIS_URL` | *Auto-linked* | Redis cache connection |
| `ALLOWED_ORIGINS` | `https://lait-web.onrender.com` | CORS policy |
| `UPLOAD_FOLDER` | `/app/uploads` | File storage path |
| `MAX_CONTENT_LENGTH` | `16777216` | 16MB upload limit |

### Frontend Service (`lait-web`)
**Manual configuration required:**

| Variable | Value | Status |
|----------|-------|--------|
| `VITE_API_BASE` | `https://lait-api.onrender.com` | **🔴 SET MANUALLY** |
| `NODE_ENV` | `production` | Auto-configured |

## 🧪 Testing Production Deployment

### 1. Backend Health Check
```bash
curl -f https://lait-api.onrender.com/api/health

# Expected Response:
{
  "status": "healthy",
  "timestamp": "2025-08-12T15:30:00Z", 
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

### 2. Frontend Application Test
Visit: `https://lait-web.onrender.com`

**Test Workflow:**
1. ✅ Registration page loads
2. ✅ Create new user account  
3. ✅ Login with credentials
4. ✅ Dashboard shows after authentication
5. ✅ Upload invoice file successfully
6. ✅ View uploaded invoices in list

### 3. End-to-End API Test
```bash
# Register test user
curl -X POST https://lait-api.onrender.com/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{"email":"demo@test.com","password":"TestPass123"}'

# Login and verify JWT
curl -X POST https://lait-api.onrender.com/api/auth/login \\
  -H "Content-Type: application/json" \\  
  -d '{"email":"demo@test.com","password":"TestPass123"}'
```

## 📊 Production Monitoring

### Service Health Monitoring
**Render Dashboard Locations:**
- **API Logs**: `lait-api` → Logs tab
- **Frontend Build**: `lait-web` → Logs tab  
- **Database**: `lait-postgres` → Metrics tab
- **Redis**: `lait-redis` → Metrics tab

### Key Metrics to Watch
- **API Response Time**: < 500ms for health checks
- **Memory Usage**: Backend should stay < 400MB (Starter plan)
- **Database Connections**: Monitor for pool exhaustion
- **Error Rate**: < 1% of requests should fail

### Setting Alerts
1. Go to each service → **Settings** → **Notifications**
2. Enable alerts for:
   - Deploy failures
   - Health check failures  
   - High resource usage (>80%)
   - Service downtime

## 🚨 Troubleshooting Common Issues

### Issue 1: "Internal Server Error" from API
**Symptoms**: Frontend shows network errors, `/api/health` returns 500

**Debug Steps:**
1. Check `lait-api` service logs for detailed errors
2. Verify `DATABASE_URL` is properly linked to PostgreSQL
3. Confirm Gunicorn started successfully:
   ```
   Look for: "🚀 Launching Gunicorn server..." in logs
   ```
4. Test database connection manually

### Issue 2: Frontend Shows "Network Error"  
**Symptoms**: App loads but can't reach API

**Solution:**
1. Verify `VITE_API_BASE` is set to correct backend URL
2. Check browser console for CORS errors
3. Test API directly: `curl https://your-backend.onrender.com/api/health`
4. Ensure `ALLOWED_ORIGINS` includes frontend domain

### Issue 3: File Upload Failures
**Symptoms**: Upload form works but files don't persist

**Resolution:**
1. Check persistent disk is mounted at `/app/uploads`
2. Verify disk usage: Dashboard → `lait-api` → Resources
3. Confirm `MAX_CONTENT_LENGTH` allows file size
4. Check upload directory permissions in logs

## 💰 Production Cost Breakdown

### Render.com Starter Plans (August 2025)
| Service | Plan | Cost | Resources |
|---------|------|------|-----------|
| Backend (`lait-api`) | Starter | $7/month | 0.5 CPU, 512MB RAM |
| Frontend (`lait-web`) | Static | **Free** | Global CDN included |
| Database (`lait-postgres`) | Starter | $7/month | 256MB RAM, 1GB storage |
| Cache (`lait-redis`) | Starter | $7/month | 25MB storage |

**Total Production Cost: $21/month**

### Free Tier Limitations
- Services sleep after 15 minutes of inactivity
- 750 hours/month limit across all services
- Good for development/demo, not production traffic

## 🔐 Production Security Features

### Automatic Security (Blueprint Enabled)
- ✅ **HTTPS/TLS**: Auto SSL certificates for all services
- ✅ **JWT Security**: Auto-generated signing keys, secure token handling
- ✅ **Database Encryption**: AES-256 at rest, TLS in transit
- ✅ **CORS Protection**: Restricted to frontend domain only
- ✅ **Security Headers**: XSS, CSP, and frame protection
- ✅ **Rate Limiting**: Built-in API throttling via Redis

### Additional Hardening
- File uploads restricted to safe paths and size limits
- Environment variables secured (no secrets in code)
- Database runs in isolated VPC
- DDoS protection included
- Regular automated security updates

## 📈 Scaling Your Deployment

### Performance Optimization Path
1. **Start**: Starter plans ($21/month) - handles ~1,000 users
2. **Growth**: Professional plans ($65/month) - handles ~10,000 users  
3. **Scale**: Enterprise custom infrastructure

### Upgrade Triggers
- **CPU Usage** consistently >80%
- **Memory Usage** consistently >80%
- **Response Time** >2 seconds regularly
- **Database Connections** approaching limits

### Horizontal Scaling Options
- Multiple backend instances with load balancing
- Database read replicas for heavy read workloads
- CDN optimization for static assets
- External file storage (S3) for uploads

## 🔄 Maintenance & Updates

### Regular Tasks
- **Weekly**: Review service health metrics and error rates
- **Monthly**: Check resource usage trends and costs
- **Quarterly**: Update dependencies and review security
- **As Needed**: Scale services based on usage patterns

### Backup Strategy
- **Database**: Automatic daily backups (retained 7 days)
- **Code**: Git repository is source of truth
- **Configuration**: Document environment variable changes
- **Uploads**: Consider S3 integration for critical files

### Update Process
1. Test changes in development branch
2. Deploy to staging environment (if available)  
3. Deploy to production via Blueprint update
4. Monitor deployment success and rollback if needed

---

## 📞 Support Information

### Getting Help
1. **Render Status**: [status.render.com](https://status.render.com)
2. **Render Docs**: [render.com/docs](https://render.com/docs)
3. **LAIT Issues**: Include deployment logs and service URLs

### Emergency Contacts
- **Service Down**: Check Render status page first
- **Data Issues**: Database backups available in dashboard  
- **Security Issues**: Rotate JWT secrets via environment variables

**Guide Version**: 2.0.0  
**Compatible**: Render.com Blueprint v2, LAIT Platform v1.0.0  
**Last Updated**: August 12, 2025
