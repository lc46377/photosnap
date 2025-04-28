output "db_endpoint" {
  value       = aws_db_instance.snaps.address
  description = "The RDS endpoint"
}

output "db_sg_id" {
  value       = aws_security_group.rds.id
  description = "The RDS Security Group ID"
}
