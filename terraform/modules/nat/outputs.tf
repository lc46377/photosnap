output "nat_gateway_id" {
  value       = var.enable_nat ? aws_nat_gateway.natgw[0].id : ""
  description = "NAT Gateway ID (empty if disabled)"
}

output "nat_eip" {
  value       = var.enable_nat ? aws_eip.nat_eip[0].public_ip : ""
  description = "Elastic IP for the NAT Gateway"
}
