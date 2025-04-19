variable "enable_nat" {
  description = "Whether to create the NAT Gateway"
  type        = bool
}

variable "vpc_id" {
  description = "The VPC ID where subnets live"
  type        = string
}

variable "public_subnet_id" {
  description = "A public subnet ID for the NAT Gateway"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs to associate with the private route table"
  type        = list(string)
}
