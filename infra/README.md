# LAIT Infrastructure

This directory contains the Docker Compose configuration and related infrastructure files for the LAIT (Legal AI Intelligence Tool) application.

## Architecture

The LAIT infrastructure consists of the following services:

### Core Services
- **PostgreSQL** (`postgres`) - Primary database on port 5432
- **Redis** (`redis`) - Cache and message queue on port 6379
- **MinIO** (`minio`) - Object storage on ports 9000/9001

### Application Services
- **API** (`api`) - Flask backend API on port 5003
- **Worker** (`worker`) - Background job processor with Celery
- **Web** (`web`) - Frontend React application on port 3000

### Utility Services
- **Migrate** (`migrate`) - Database migration and setup

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example ../backend/.env
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Initialize database:**
   ```bash
   docker-compose run --rm migrate
   ```

4. **Access services:**
   - Frontend: http://localhost:3000
   - API: http://localhost:5003
   - MinIO Console: http://localhost:9001

## Environment Configuration

The API service reads configuration from:
1. `../backend/.env` file (mounted as env_file)
2. Environment variables defined in docker-compose.yml
3. Default values in the application

Key environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET_KEY` - JWT signing secret (change in production!)
- `MINIO_*` - Object storage configuration
- `API_PORT` - API server port (5003)

## Service Details

### PostgreSQL Database
- **Image:** postgres:15-alpine
- **Port:** 5432
- **Database:** lait_production
- **User:** lait_user
- **Volume:** postgres_data

### Redis Cache
- **Image:** redis:7-alpine
- **Port:** 6379
- **Password:** lait_redis_password
- **Volume:** redis_data

### MinIO Object Storage
- **Image:** minio/minio:latest
- **Ports:** 9000 (API), 9001 (Console)
- **Root User:** lait_minio
- **Root Password:** lait_minio_password
- **Volume:** minio_data

### API Backend
- **Build:** ../backend (using Dockerfile.api)
- **Port:** 5003
- **Environment:** Reads from ../backend/.env
- **Volumes:** ../backend:/app, api_uploads:/app/uploads
- **Health Check:** GET /api/health

### Background Worker
- **Build:** ../backend (using Dockerfile.worker)
- **Command:** Celery worker with 4 concurrent processes
- **Depends On:** postgres, redis, minio

### Frontend Web
- **Build:** ../frontend (using Dockerfile.web)
- **Port:** 3000
- **Environment:** VITE_API_BASE=http://localhost:5003

## Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis api

# View logs
docker-compose logs -f api
```

### Database Operations
```bash
# Run migrations
docker-compose run --rm migrate

# Access database
docker-compose exec postgres psql -U lait_user -d lait_production

# Backup database
docker-compose exec postgres pg_dump -U lait_user lait_production > backup.sql
```

### Development
```bash
# Rebuild services after code changes
docker-compose build api worker

# Restart API after changes
docker-compose restart api

# Scale workers
docker-compose up -d --scale worker=3
```

### Monitoring
```bash
# Check service health
docker-compose ps

# View resource usage
docker stats

# Check logs
docker-compose logs --tail=50 api
```

## Volumes

Persistent data is stored in Docker volumes:
- `lait_postgres_data` - Database data
- `lait_redis_data` - Redis data
- `lait_minio_data` - Object storage data
- `lait_api_uploads` - API uploaded files
- `lait_worker_data` - Worker temporary data

## Network

All services communicate through the `lait_network` bridge network.

## Security Notes

⚠️ **Important for Production:**

1. Change all default passwords in `.env`
2. Use strong JWT secret key
3. Configure proper CORS origins
4. Enable TLS/SSL for external access
5. Update Docker images regularly
6. Use secrets management for sensitive data

## Troubleshooting

### Common Issues

1. **Port conflicts:** Change ports in docker-compose.yml
2. **Permission denied:** Check file permissions and Docker permissions
3. **Database connection failed:** Wait for postgres health check
4. **API not responding:** Check logs with `docker-compose logs api`

### Health Checks

All services include health checks:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- MinIO: HTTP health endpoint
- API: GET /api/health
- Web: HTTP check on port 3000

### Reset Everything

```bash
# Stop and remove everything
docker-compose down -v --remove-orphans

# Remove all volumes (WARNING: This deletes all data!)
docker volume prune -f

# Rebuild and restart
docker-compose up -d --build
```

## Production Deployment

For production deployment:

1. Use proper secrets management
2. Configure reverse proxy (nginx/traefik)
3. Enable TLS/SSL certificates
4. Set up monitoring and logging
5. Configure backups
6. Use container orchestration (Kubernetes/Docker Swarm)
7. Implement proper security scanning

## Support

For issues and questions:
- Check logs: `docker-compose logs [service]`
- Verify health: `docker-compose ps`
- Review configuration: `docker-compose config`
