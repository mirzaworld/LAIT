terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.3"
    }
  }
  
  backend "s3" {
    bucket = "lait-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "LAIT"
      ManagedBy   = "Terraform"
    }
  }
}

# VPC and Network Configuration
module "vpc" {
  source = "./modules/vpc"
  
  environment        = var.environment
  vpc_cidr          = var.vpc_cidr
  availability_zones = var.availability_zones
}

# ECS Cluster and Services
module "ecs" {
  source = "./modules/ecs"
  
  environment     = var.environment
  vpc_id         = module.vpc.vpc_id
  public_subnets = module.vpc.public_subnets
  
  app_name           = "lait"
  container_image    = var.container_image
  container_port     = var.container_port
  desired_count      = var.desired_count
  health_check_path  = "/api/health"
  
  depends_on = [module.vpc]
}

# RDS Database
module "rds" {
  source = "./modules/rds"
  
  environment     = var.environment
  vpc_id         = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  
  db_name     = var.db_name
  db_username = var.db_username
  db_password = var.db_password
  
  depends_on = [module.vpc]
}

# ElastiCache Redis
module "redis" {
  source = "./modules/redis"
  
  environment     = var.environment
  vpc_id         = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  
  redis_node_type = var.redis_node_type
  
  depends_on = [module.vpc]
}

# S3 Bucket for file storage
module "s3" {
  source = "./modules/s3"
  
  environment = var.environment
  bucket_name = var.s3_bucket_name
}

# CloudFront Distribution
module "cloudfront" {
  source = "./modules/cloudfront"
  
  environment = var.environment
  s3_bucket_id = module.s3.bucket_id
  domain_name  = var.domain_name
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"
  
  environment     = var.environment
  vpc_id         = module.vpc.vpc_id
  public_subnets = module.vpc.public_subnets
  
  health_check_path = "/api/health"
  
  depends_on = [module.vpc]
}

# Route53 DNS Records
module "route53" {
  source = "./modules/route53"
  
  domain_name     = var.domain_name
  cloudfront_dist = module.cloudfront.distribution_domain_name
  alb_dns_name    = module.alb.dns_name
}
