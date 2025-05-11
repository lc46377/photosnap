resource "random_id" "bucket_suffix" {
  byte_length = 4
}

locals {
  bucket_name = "photosnap-raw-snaps-${random_id.bucket_suffix.hex}"
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source            = "./modules/vpc"
  vpc_cidr          = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
}

module "nat" {
  source            = "./modules/nat"
  enable_nat        = var.enable_nat
  vpc_id            = module.vpc.vpc_id
  public_subnet_id  = module.vpc.public_subnet_ids[0]
  private_subnet_ids = module.vpc.private_subnet_ids
}

module "db" {
  source           = "./modules/db"
  vpc_id           = module.vpc.vpc_id
  private_subnets  = module.vpc.private_subnet_ids
  db_username      = var.db_username
  db_password      = var.db_password
  vpc_cidr         = var.vpc_cidr
}

module "s3" {
  source      = "./modules/s3"
  bucket_name = local.bucket_name
}

output "vpc_id" {
  description = "The VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Comma-separated public subnet IDs for CFN"
  value       = join(",", module.vpc.public_subnet_ids)
  sensitive   = false
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "bucket_name" {
  description = "The name of the raw-snaps S3 bucket"
  value       = local.bucket_name
}

output "db_endpoint" {
  description = "RDS endpoint for Flask"
  value       = module.db.db_endpoint
}