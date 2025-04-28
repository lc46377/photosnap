variable "vpc_id"          { type = string }
variable "private_subnets" { type = list(string) }
variable "db_username"     { type = string }
variable "db_password"     { type = string }
variable "vpc_cidr" {
  description = "The VPC CIDR block (for SG ingress)"
  type        = string
}
