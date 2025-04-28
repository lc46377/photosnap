# PhotoSnap MVP

A minimal one-time-view photo-sharing application built on AWS, demonstrating core cloud architecture components and Infrastructure as Code.

---

## Architecture

```mermaid
graph TD
  ReactApp[React + CloudFront]
  ReactApp -->|HTTPS| API_GW[API Gateway]

  subgraph VPC
    subgraph Public
      IGW[(Internet Gateway)]
      ALB[Application Load Balancer]
      NAT?[(Toggleable NAT Gateway)]
    end
    subgraph Private
      EC2[EC2 (Flask API)]
      RDS[(RDS PostgreSQL)]
    end
  end

  API_GW --> ALB --> EC2
  IGW --> ALB
  EC2 --> RDS
  EC2 -->|PUT/GET| S3[[S3 Bucket]]
  S3 -->|ObjectCreated| Lambda[Lambda → CloudWatch]
```  

---

## Folder Structure

```
photosnap-mvp/
├── diagrams/        # Architecture diagrams (Mermaid files)
├── terraform/       # Terraform modules & root configs
├── cfn/             # CloudFormation templates
├── backend/         # Flask app & SQL schema
├── frontend/        # React app scaffold
├── scripts/         # Boto3 example scripts
└── README.md        # This file
```

---

## Prerequisites

- **AWS CLI** configured with an IAM user having:
  - VPC, EC2, RDS, S3, Lambda, CloudFormation permissions
  - `rds:CreateDBSubnetGroup`, `rds:CreateDBInstance`
- **Terraform v1.x**
- **Node.js & npm** (for the React frontend)
- **Python 3.8+** (for Flask & Boto3 scripts)

---

## Day 1: Setup
1. Initialize Git repository and connect to GitHub.
2. Create `backend/snaps.sql` with PostgreSQL schema.
3. Add `diagrams/day1-arch.mmd` for architecture.

---

## Day 2: Networking
```bash
cd terraform
terraform init
terraform plan -var="enable_nat=false"
terraform apply -var="enable_nat=false" -auto-approve
```
- Creates VPC, public/private subnets, and IGW.
- Toggle NAT via `-var="enable_nat=true"` when needed.

---

## Day 3: Database & Storage
1. Grant RDS permissions to your IAM user.
2. Configure `terraform/variables.tf` with `db_password`.
3. Apply Terraform:
```bash
terraform init -reconfigure
terraform plan -var="db_password=<YOUR_PASS>" -var="enable_nat=false"
terraform apply -var="db_password=<YOUR_PASS>" -var="enable_nat=false" -auto-approve
```
- Provisions RDS PostgreSQL in two AZs (db.t3.micro).
- Creates S3 bucket with 1-day lifecycle.

---

## Verification
```bash
# Get outputs
terraform output bucket_name      # S3 bucket name
terraform output db_endpoint      # RDS endpoint

# Verify S3
aws s3api get-bucket-lifecycle-configuration --bucket $(terraform output -raw bucket_name)
aws s3api get-bucket-versioning            --bucket $(terraform output -raw bucket_name)

# Verify RDS
aws rds describe-db-instances --db-instance-identifier photosnap-db --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address,Endpoint.Port]' --output table
```

---

## Cleanup
```bash
cd terraform
terraform destroy -var="db_password=<YOUR_PASS>" -var="enable_nat=false" -auto-approve
```

---
