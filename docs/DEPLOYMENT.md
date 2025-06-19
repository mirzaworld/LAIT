# LAIT - Legal AI Invoice Tracking System

## Deployment Guide

### Prerequisites

- AWS Account with appropriate permissions
- Terraform >= 1.0
- Docker & Docker Compose
- Node.js >= 18
- Python >= 3.10

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LAIT.git
cd LAIT
```

2. Run the development setup script:
```bash
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh
```

3. Start the development services:
```bash
docker-compose up
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Production Deployment

#### 1. Infrastructure Setup

1. Configure AWS credentials:
```bash
aws configure
```

2. Initialize Terraform:
```bash
cd terraform
terraform init
```

3. Create terraform.tfvars:
```hcl
environment        = "prod"
domain_name        = "your-domain.com"
db_name           = "lait_db"
db_username       = "your_db_username"
db_password       = "your_secure_password"
s3_bucket_name    = "your-s3-bucket"
container_image   = "your-ecr-repo/lait-backend:latest"
```

4. Apply Terraform configuration:
```bash
terraform plan
terraform apply
```

#### 2. Application Deployment

1. Build and push Docker images:
```bash
# Build images
docker build -t lait-backend ./backend
docker build -t lait-frontend .

# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REGISTRY
docker tag lait-backend:latest $ECR_REGISTRY/lait-backend:latest
docker tag lait-frontend:latest $ECR_REGISTRY/lait-frontend:latest
docker push $ECR_REGISTRY/lait-backend:latest
docker push $ECR_REGISTRY/lait-frontend:latest
```

2. Update ECS services:
```bash
aws ecs update-service --cluster lait-cluster --service lait-backend --force-new-deployment
aws ecs update-service --cluster lait-cluster --service lait-frontend --force-new-deployment
```

### Configuration

#### Environment Variables

Backend:
- `FLASK_ENV`: Environment (development/production)
- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_BUCKET`: S3 bucket name

Frontend:
- `VITE_API_URL`: Backend API URL

### Monitoring & Maintenance

1. View application logs:
```bash
# Backend logs
aws logs get-log-events --log-group-name /ecs/lait-backend --log-stream-name <stream-name>

# Frontend logs
aws logs get-log-events --log-group-name /ecs/lait-frontend --log-stream-name <stream-name>
```

2. Monitor performance:
- Use AWS CloudWatch for metrics
- Set up alarms for CPU, memory usage
- Monitor API response times

### Backup & Recovery

1. Database backups:
- Automated daily snapshots (configured in Terraform)
- Manual backup:
```bash
aws rds create-db-snapshot --db-instance-identifier lait-db --db-snapshot-identifier manual-backup
```

2. S3 bucket versioning:
- Enabled by default in Terraform config
- Access previous versions through AWS Console or CLI

### Security Considerations

1. Access Control:
- Use IAM roles for service access
- Implement least privilege principle
- Regular audit of IAM permissions

2. Data Protection:
- Enable encryption at rest
- Use SSL for data in transit
- Regular security audits

3. Compliance:
- Enable AWS CloudTrail
- Monitor security groups
- Regular compliance checks

### Troubleshooting

Common issues and solutions:

1. Database Connection Issues:
- Check security group rules
- Verify credentials in environment variables
- Test connection from bastion host

2. S3 Access Issues:
- Verify IAM roles
- Check bucket permissions
- Validate environment variables

3. Application Errors:
- Check CloudWatch logs
- Verify environment variables
- Check container health status

### Scaling

1. Horizontal Scaling:
- Adjust desired_count in ECS services
- Monitor CPU/memory metrics
- Configure auto-scaling policies

2. Database Scaling:
- Monitor RDS metrics
- Consider read replicas
- Plan for storage increases

### Maintenance Tasks

1. Regular Updates:
- Update dependencies monthly
- Apply security patches
- Review and update IAM policies

2. Performance Optimization:
- Review CloudWatch metrics
- Optimize database queries
- Update resource allocations

3. Backup Verification:
- Test database restores
- Verify backup integrity
- Update disaster recovery plan
