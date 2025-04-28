output "bucket_arn" {
  value       = aws_s3_bucket.raw_snaps.arn
  description = "ARN of raw snaps S3 bucket"
}

output "bucket_name" {
  value       = aws_s3_bucket.raw_snaps.bucket
  description = "Name of raw snaps S3 bucket"
}
