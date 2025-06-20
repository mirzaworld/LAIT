# AWS Production Deployment Configuration for LAIT

# This terraform configuration will set up a production-ready deployment
# Run: terraform init && terraform plan && terraform apply

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "lait.yourdomain.com"
}

# VPC and Networking
resource "aws_vpc" "lait_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "lait-vpc-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_internet_gateway" "lait_igw" {
  vpc_id = aws_vpc.lait_vpc.id

  tags = {
    Name        = "lait-igw-${var.environment}"
    Environment = var.environment
  }
}

# Public Subnets
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.lait_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name        = "lait-public-subnet-1-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.lait_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name        = "lait-public-subnet-2-${var.environment}"
    Environment = var.environment
  }
}

# Private Subnets
resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.lait_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name        = "lait-private-subnet-1-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.lait_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name        = "lait-private-subnet-2-${var.environment}"
    Environment = var.environment
  }
}

# Route Tables
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.lait_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.lait_igw.id
  }

  tags = {
    Name        = "lait-public-rt-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_route_table_association" "public_rta_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_rta_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_rt.id
}

# Security Groups
resource "aws_security_group" "alb_sg" {
  name_prefix = "lait-alb-sg-"
  vpc_id      = aws_vpc.lait_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "lait-alb-sg-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_security_group" "ecs_sg" {
  name_prefix = "lait-ecs-sg-"
  vpc_id      = aws_vpc.lait_vpc.id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  ingress {
    from_port       = 5173
    to_port         = 5173
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "lait-ecs-sg-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_security_group" "rds_sg" {
  name_prefix = "lait-rds-sg-"
  vpc_id      = aws_vpc.lait_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  tags = {
    Name        = "lait-rds-sg-${var.environment}"
    Environment = var.environment
  }
}

# RDS Database
resource "aws_db_subnet_group" "lait_db_subnet_group" {
  name       = "lait-db-subnet-group-${var.environment}"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]

  tags = {
    Name        = "lait-db-subnet-group-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_db_instance" "lait_postgres" {
  identifier             = "lait-postgres-${var.environment}"
  engine                 = "postgres"
  engine_version         = "14.9"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  max_allocated_storage  = 100
  storage_type           = "gp2"
  
  db_name  = "legalspend"
  username = "postgres"
  password = "change_this_in_production"  # Use AWS Secrets Manager in production
  
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.lait_db_subnet_group.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true  # Set to false in production
  
  tags = {
    Name        = "lait-postgres-${var.environment}"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "lait_redis_subnet_group" {
  name       = "lait-redis-subnet-group-${var.environment}"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
}

resource "aws_elasticache_cluster" "lait_redis" {
  cluster_id           = "lait-redis-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.lait_redis_subnet_group.name
  security_group_ids   = [aws_security_group.ecs_sg.id]

  tags = {
    Name        = "lait-redis-${var.environment}"
    Environment = var.environment
  }
}

# ECR Repositories
resource "aws_ecr_repository" "lait_backend" {
  name                 = "lait-backend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "lait-backend"
    Environment = var.environment
  }
}

resource "aws_ecr_repository" "lait_frontend" {
  name                 = "lait-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "lait-frontend"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "lait_cluster" {
  name = "lait-cluster-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "lait-cluster-${var.environment}"
    Environment = var.environment
  }
}

# Application Load Balancer
resource "aws_lb" "lait_alb" {
  name               = "lait-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets           = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]

  enable_deletion_protection = false  # Set to true in production

  tags = {
    Name        = "lait-alb-${var.environment}"
    Environment = var.environment
  }
}

# S3 Bucket for file uploads
resource "aws_s3_bucket" "lait_uploads" {
  bucket = "lait-uploads-${var.environment}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "lait-uploads-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "lait_uploads_versioning" {
  bucket = aws_s3_bucket.lait_uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lait_uploads_encryption" {
  bucket = aws_s3_bucket.lait_uploads.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "lait_backend_logs" {
  name              = "/ecs/lait-backend-${var.environment}"
  retention_in_days = 7

  tags = {
    Name        = "lait-backend-logs-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "lait_frontend_logs" {
  name              = "/ecs/lait-frontend-${var.environment}"
  retention_in_days = 7

  tags = {
    Name        = "lait-frontend-logs-${var.environment}"
    Environment = var.environment
  }
}

# Outputs
output "vpc_id" {
  value = aws_vpc.lait_vpc.id
}

output "alb_dns_name" {
  value = aws_lb.lait_alb.dns_name
}

output "rds_endpoint" {
  value = aws_db_instance.lait_postgres.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.lait_redis.cache_nodes[0].address
}

output "ecr_backend_repository_url" {
  value = aws_ecr_repository.lait_backend.repository_url
}

output "ecr_frontend_repository_url" {
  value = aws_ecr_repository.lait_frontend.repository_url
}

output "s3_bucket_name" {
  value = aws_s3_bucket.lait_uploads.bucket
}
