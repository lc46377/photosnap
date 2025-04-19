terraform {
  backend "s3" {
    bucket = "photosnap-lc46377-bucket"
    key    = "photosnap/terraform.tfstate"
    region = "us-east-1"
  }
}
