resource "aws_s3_bucket" "raw_snaps" {
  bucket = var.bucket_name

  tags = {
    Name = "photosnap-raw-snaps"
  }
}

resource "aws_s3_bucket_versioning" "raw_snaps_versioning" {
  bucket = aws_s3_bucket.raw_snaps.id

  versioning_configuration {
    status = "Suspended"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "raw_snaps_lifecycle" {
  bucket = aws_s3_bucket.raw_snaps.id

  rule {
    id     = "expire-snaps"
    status = "Enabled"

    # Apply this rule to all objects
    filter {
      prefix = ""
    }

    expiration {
      days = 1
    }

    noncurrent_version_expiration {
      noncurrent_days = 1
    }
  }
}
