# Troubleshooting Guide

## Application Issues

### Backend Service Not Starting

1. Check logs:
```bash
docker logs lait-backend
```

Common issues:
- Database connection errors
  - Verify DATABASE_URL in environment
  - Check database is running and accessible
  - Verify network connectivity
- Redis connection errors
  - Check REDIS_URL configuration
  - Verify Redis service is running
- AWS credential issues
  - Validate AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
  - Check IAM permissions

2. Verify environment variables:
```bash
docker exec lait-backend env
```

3. Check database migrations:
```bash
flask db current
flask db check
```

### Frontend Service Issues

1. White screen / Loading issues:
- Check browser console for errors
- Verify API endpoint configuration
- Check for JavaScript errors
- Validate build process

2. Authentication issues:
- Clear browser cache and cookies
- Check JWT token expiration
- Verify API connectivity

3. Performance issues:
- Check browser network tab
- Verify CDN configuration
- Monitor API response times

## ML Model Issues

### Model Training Failures

1. Check error logs:
```bash
tail -f logs/ml_training.log
```

2. Common issues:
- Memory errors
  - Check available system memory
  - Reduce batch size
  - Optimize data loading
- Data quality issues
  - Validate input data format
  - Check for missing values
  - Verify data types

3. Validation steps:
```python
# Check data shape
print(data.shape)
# Verify data types
print(data.dtypes)
# Check for nulls
print(data.isnull().sum())
```

### Prediction Issues

1. Model loading errors:
- Verify model file exists
- Check model version compatibility
- Validate input data format

2. Performance degradation:
- Monitor prediction latency
- Check model metrics
- Review feature distributions

## Infrastructure Issues

### AWS ECS

1. Container health checks failing:
```bash
aws ecs describe-services --cluster lait-cluster --services lait-backend
```

2. Task definition issues:
- Check CPU/memory allocation
- Verify container definitions
- Validate environment variables

3. Networking issues:
- Check security groups
- Verify VPC configuration
- Test connectivity

### Database

1. Connection issues:
```bash
psql $DATABASE_URL -c "\dx"
```

2. Performance problems:
- Check slow query log
- Monitor connection count
- Review index usage

3. Storage issues:
- Monitor disk usage
- Check WAL size
- Review table bloat

### Redis

1. Connection refused:
```bash
redis-cli -u $REDIS_URL ping
```

2. Memory issues:
- Monitor used_memory
- Check maxmemory setting
- Review eviction policy

## Security Issues

### JWT Token Problems

1. Token validation failures:
- Check token expiration
- Verify signing key
- Validate token format

2. Authorization issues:
- Review user roles
- Check permission settings
- Verify role assignments

### File Upload Issues

1. S3 upload failures:
- Check bucket permissions
- Verify CORS settings
- Validate file size limits

2. File processing errors:
- Check file format
- Verify virus scan status
- Monitor processing queue

## Performance Issues

### API Response Time

1. Slow endpoints:
```bash
curl -w "@curl-format.txt" -o /dev/null -s "https://api.domain.com/health"
```

2. Database queries:
- Review query plans
- Check index usage
- Monitor connection pool

3. Caching issues:
- Verify cache hits/misses
- Check cache size
- Review TTL settings

### Resource Utilization

1. CPU/Memory usage:
```bash
docker stats lait-backend lait-frontend
```

2. Network bottlenecks:
- Monitor bandwidth usage
- Check network latency
- Review request patterns

## Monitoring Alerts

### High Error Rate

1. Check application logs:
```bash
aws logs get-log-events --log-group-name /ecs/lait-backend
```

2. Review error patterns:
- Track error frequencies
- Identify common causes
- Monitor error trends

3. Alert response:
- Assess impact
- Implement fixes
- Update documentation

### Resource Exhaustion

1. Memory alerts:
- Check memory usage
- Review memory limits
- Monitor swap usage

2. Disk space alerts:
- Clean old logs
- Archive unused data
- Increase capacity

## Recovery Procedures

### Database Recovery

1. Point-in-time recovery:
```bash
aws rds restore-db-instance-to-point-in-time
```

2. Backup restoration:
- Identify backup point
- Test restoration
- Verify data integrity

### Service Recovery

1. Rolling back deployments:
```bash
aws ecs update-service --cluster lait-cluster --service lait-backend --task-definition PREVIOUS_VERSION
```

2. Emergency procedures:
- Stop affected services
- Restore from backup
- Verify functionality

## Preventive Measures

### Regular Maintenance

1. System updates:
```bash
apt update && apt upgrade
```

2. Dependency updates:
```bash
pip install --upgrade -r requirements.txt
npm audit fix
```

3. Security patches:
- Review security advisories
- Apply critical patches
- Test after updates

### Monitoring Setup

1. Configure alerting:
```bash
aws cloudwatch put-metric-alarm
```

2. Dashboard setup:
- Create metric widgets
- Set up log insights
- Configure notifications

### Backup Procedures

1. Database backups:
- Verify backup schedule
- Test restoration process
- Monitor backup size

2. Application state:
- Backup configurations
- Archive important files
- Document procedures
