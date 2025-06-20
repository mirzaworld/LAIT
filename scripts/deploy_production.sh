#!/bin/bash

# Production Deployment Script for LAIT
# This script handles the complete deployment process

set -e

echo "🚀 LAIT Production Deployment Script"
echo "=================================="

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
DOMAIN=${DOMAIN:-lait.yourdomain.com}
AWS_REGION=${AWS_REGION:-us-east-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if required tools are installed
    for tool in docker aws terraform; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool is not installed. Please install it first."
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    log_info "Prerequisites check passed ✅"
}

# Deploy infrastructure using Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd infrastructure/terraform
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -var="domain_name=$DOMAIN" -var="aws_region=$AWS_REGION"
    
    # Apply (with confirmation)
    read -p "Do you want to apply these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -var="domain_name=$DOMAIN" -var="aws_region=$AWS_REGION"
        log_info "Infrastructure deployed successfully ✅"
    else
        log_warn "Infrastructure deployment cancelled"
        exit 1
    fi
    
    cd ../..
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    # Get ECR repository URLs from Terraform output
    BACKEND_REPO=$(cd infrastructure/terraform && terraform output -raw ecr_backend_repository_url)
    FRONTEND_REPO=$(cd infrastructure/terraform && terraform output -raw ecr_frontend_repository_url)
    
    # Login to ECR
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $BACKEND_REPO
    
    # Build and push backend
    log_info "Building backend image..."
    docker build -f Dockerfile.backend -t lait-backend:latest .
    docker tag lait-backend:latest $BACKEND_REPO:latest
    docker push $BACKEND_REPO:latest
    
    # Build and push frontend
    log_info "Building frontend image..."
    docker build -f Dockerfile.frontend -t lait-frontend:latest .
    docker tag lait-frontend:latest $FRONTEND_REPO:latest
    docker push $FRONTEND_REPO:latest
    
    log_info "Docker images pushed successfully ✅"
}

# Deploy ECS services
deploy_ecs_services() {
    log_info "Deploying ECS services..."
    
    # Get infrastructure details from Terraform
    CLUSTER_NAME=$(cd infrastructure/terraform && terraform output -raw ecs_cluster_name)
    BACKEND_REPO=$(cd infrastructure/terraform && terraform output -raw ecr_backend_repository_url)
    FRONTEND_REPO=$(cd infrastructure/terraform && terraform output -raw ecr_frontend_repository_url)
    
    # Deploy backend service
    cat > backend-task-definition.json << EOF
{
    "family": "lait-backend-${ENVIRONMENT}",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "lait-backend",
            "image": "${BACKEND_REPO}:latest",
            "portMappings": [
                {
                    "containerPort": 5000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "FLASK_ENV", "value": "production"},
                {"name": "DATABASE_URL", "value": "postgresql://postgres:password@${RDS_ENDPOINT}:5432/legalspend"},
                {"name": "REDIS_URL", "value": "redis://${REDIS_ENDPOINT}:6379/0"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/lait-backend-${ENVIRONMENT}",
                    "awslogs-region": "${AWS_REGION}",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF
    
    # Register task definition
    aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
    
    # Create or update service
    aws ecs create-service \
        --cluster $CLUSTER_NAME \
        --service-name lait-backend-service \
        --task-definition lait-backend-${ENVIRONMENT} \
        --desired-count 2 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
        || aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service lait-backend-service \
            --task-definition lait-backend-${ENVIRONMENT} \
            --desired-count 2
    
    log_info "ECS services deployed successfully ✅"
}

# Setup SSL certificate
setup_ssl() {
    log_info "Setting up SSL certificate..."
    
    # Request ACM certificate
    aws acm request-certificate \
        --domain-name $DOMAIN \
        --validation-method DNS \
        --region $AWS_REGION
    
    log_warn "Please validate the SSL certificate in AWS Console and update ALB listener"
}

# Setup monitoring and alerting
setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Create CloudWatch alarms
    aws cloudwatch put-metric-alarm \
        --alarm-name "LAIT-HighCPUUtilization" \
        --alarm-description "Alarm when CPU exceeds 80%" \
        --metric-name CPUUtilization \
        --namespace AWS/ECS \
        --statistic Average \
        --period 300 \
        --threshold 80 \
        --comparison-operator GreaterThanThreshold \
        --evaluation-periods 2
    
    # Create SNS topic for alerts
    aws sns create-topic --name lait-alerts
    
    log_info "Monitoring setup completed ✅"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # This would typically be done through ECS task
    # For now, we'll show the command that needs to be run
    log_warn "Please run database migrations manually:"
    echo "aws ecs run-task --cluster $CLUSTER_NAME --task-definition lait-backend-migration --launch-type FARGATE"
}

# Main deployment function
main() {
    log_info "Starting LAIT production deployment..."
    
    check_prerequisites
    
    echo
    log_info "Deployment plan:"
    echo "1. Deploy infrastructure (AWS resources)"
    echo "2. Build and push Docker images"
    echo "3. Deploy ECS services"
    echo "4. Setup SSL certificate"
    echo "5. Setup monitoring"
    echo "6. Run database migrations"
    echo
    
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warn "Deployment cancelled"
        exit 1
    fi
    
    deploy_infrastructure
    build_and_push_images
    deploy_ecs_services
    setup_ssl
    setup_monitoring
    run_migrations
    
    echo
    log_info "🎉 Deployment completed successfully!"
    log_info "Your application will be available at: https://$DOMAIN"
    log_warn "Don't forget to:"
    echo "  - Validate SSL certificate in AWS Console"
    echo "  - Update DNS records to point to the ALB"
    echo "  - Run database migrations"
    echo "  - Configure monitoring alerts"
}

# Run main function
main "$@"
