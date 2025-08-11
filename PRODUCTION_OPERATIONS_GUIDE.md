# LAIT Production Operations Guide

## 🚀 Production Deployment

### Quick Start
```bash
# One-click deployment
./deploy-production-final.sh

# Skip tests (faster deployment)
./deploy-production-final.sh --skip-tests
```

### Manual Deployment Steps
1. **Prerequisites Check**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env.production
   # Edit .env.production with production values
   ```

3. **Deploy Services**
   ```bash
   docker-compose -f docker-compose.production.yml up -d
   ```

## 📊 Monitoring & Health Checks

### Health Endpoints
- **Backend Health**: `GET /api/health`
- **Backend Readiness**: `GET /api/readiness`
- **Frontend**: `GET /` (should return 200)

### System Monitoring
```bash
# Check all services
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Check resource usage
docker stats

# Check disk usage
df -h
```

### Database Monitoring
```bash
# Connect to database
docker-compose -f docker-compose.production.yml exec postgres psql -U lait -d lait

# Check database size
docker-compose -f docker-compose.production.yml exec postgres psql -U lait -d lait -c "SELECT pg_size_pretty(pg_database_size('lait'));"

# Active connections
docker-compose -f docker-compose.production.yml exec postgres psql -U lait -d lait -c "SELECT count(*) FROM pg_stat_activity;"
```

## 🔒 Security

### Authentication
- JWT tokens expire in 1 hour
- Refresh tokens expire in 7 days
- Rate limiting: 100 requests/minute per IP
- Failed login protection: 5 attempts then 15min lockout

### Environment Variables (Production)
```bash
# Required Production Variables
JWT_SECRET_KEY=<strong-random-key>
POSTGRES_PASSWORD=<secure-password>
REDIS_PASSWORD=<secure-password>
API_KEY_OPENAI=<your-openai-key>
API_KEY_LEGAL_DATABASE=<your-legal-api-key>

# Optional but Recommended
SSL_CERT_PATH=/path/to/ssl/cert
SSL_KEY_PATH=/path/to/ssl/key
LOG_LEVEL=INFO
BACKUP_ENCRYPTION_KEY=<backup-encryption-key>
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for performance
CREATE INDEX CONCURRENTLY idx_invoices_date ON invoices(date);
CREATE INDEX CONCURRENTLY idx_invoices_vendor ON invoices(vendor_id);
CREATE INDEX CONCURRENTLY idx_notifications_user ON notifications(user_id, created_at);
CREATE INDEX CONCURRENTLY idx_line_items_invoice ON line_items(invoice_id);
```

### Caching
- Redis cache for API responses (5 min TTL)
- Static assets cached for 1 year
- Database query caching enabled

### Resource Limits
```yaml
# In docker-compose.production.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

## 🔄 Backup & Recovery

### Automated Backups
```bash
# Daily backup (add to crontab)
0 2 * * * /path/to/lait/scripts/backup.sh

# Backup script content:
#!/bin/bash
BACKUP_DIR="/backups/$(date +\%Y\%m\%d)"
mkdir -p "$BACKUP_DIR"
docker-compose -f docker-compose.production.yml exec postgres pg_dumpall -c -U lait > "$BACKUP_DIR/lait_backup.sql"
tar -czf "$BACKUP_DIR/lait_full_backup.tar.gz" -C /path/to/lait .
```

### Recovery
```bash
# Restore database
docker-compose -f docker-compose.production.yml exec postgres psql -U lait -d lait < backup.sql

# Restore full application
tar -xzf lait_full_backup.tar.gz
docker-compose -f docker-compose.production.yml up -d
```

## 🚨 Troubleshooting

### Common Issues

#### Backend Not Starting
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs backend

# Common fixes
docker-compose -f docker-compose.production.yml restart backend
docker system prune -f
```

#### Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.production.yml exec postgres pg_isready -U lait

# Reset database connections
docker-compose -f docker-compose.production.yml restart postgres
```

#### High Memory Usage
```bash
# Check memory usage
docker stats --no-stream

# Scale down if needed
docker-compose -f docker-compose.production.yml scale backend=1
```

### Log Analysis
```bash
# Error logs only
docker-compose -f docker-compose.production.yml logs | grep ERROR

# Performance logs
docker-compose -f docker-compose.production.yml logs | grep "latency_ms"

# Authentication logs
docker-compose -f docker-compose.production.yml logs | grep "auth"
```

## 🔧 Maintenance

### Daily Tasks
- [ ] Check health endpoints
- [ ] Review error logs
- [ ] Check disk space
- [ ] Verify backups

### Weekly Tasks
- [ ] Update dependencies (test in staging first)
- [ ] Clean up old logs
- [ ] Review performance metrics
- [ ] Test backup restoration

### Monthly Tasks
- [ ] Security updates
- [ ] Performance optimization review
- [ ] Capacity planning
- [ ] Disaster recovery test

## 📊 API Error Codes Reference

### Authentication (4xx)
- `400`: Invalid credentials format
- `401`: Invalid/expired token
- `403`: Insufficient permissions
- `429`: Rate limit exceeded

### Application (5xx)
- `500`: Internal server error
- `503`: Service temporarily unavailable
- `502`: Database connection failed

### Custom Error Codes
- `LEGAL_001`: Legal database unavailable
- `ML_001`: ML model not ready
- `FILE_001`: File processing failed

## 🔄 Notification Event Types

### System Notifications
- `system.startup`: Application started
- `system.shutdown`: Application stopping
- `system.error`: System error occurred

### Invoice Processing
- `invoice.uploaded`: New invoice uploaded
- `invoice.processed`: Invoice analysis complete
- `invoice.flagged`: Invoice flagged for review

### Legal Intelligence
- `legal.search_complete`: Legal search finished
- `legal.verification_complete`: Attorney verification done

## 🎯 Performance Targets

### Response Times (95th percentile)
- Health endpoint: < 100ms
- Invoice upload: < 5s
- Legal search: < 10s
- Dashboard load: < 2s

### Availability
- Target: 99.9% uptime
- Max downtime per month: 43 minutes
- Recovery time objective (RTO): 15 minutes
- Recovery point objective (RPO): 1 hour

### Capacity
- Concurrent users: 100+
- Invoices per day: 1,000+
- Legal searches per day: 500+
- Storage: 100GB+ (with auto-scaling)

## 📞 Support Contacts

### Emergency Contacts
- **System Admin**: admin@lait.com
- **Database Admin**: dba@lait.com
- **Security Team**: security@lait.com

### External Services
- **OpenAI Support**: API issues
- **Legal Database Provider**: Legal data issues
- **Cloud Provider**: Infrastructure issues

---

**Last Updated**: January 2025
**Version**: 1.0.0
