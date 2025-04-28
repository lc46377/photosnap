variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDRs for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDRs for private subnets (requires ≥2 AZs for RDS)"
  type        = list(string)
  default     = ["10.0.2.0/24", "10.0.3.0/24"]
}

variable "enable_nat" {
  description = "Whether to create a NAT instance"
  type        = bool
  default     = false
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "photosnap_user"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}