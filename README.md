
# PhotoSnap MVP - In-Depth Guide

A minimal one-time-view photo-sharing application built on AWS, demonstrating core cloud architecture components and Infrastructure as Code.

---

## Table of Contents

1. [Architecture](#architecture)  
2. [Folder Structure](#folder-structure)  
3. [Prerequisites](#prerequisites)  
4. [Environment Variables & Exports](#environment-variables--exports)  
5. [Day 1: Project Initialization](#day-1-project-initialization)  
6. [Day 2: Networking (Terraform)](#day-2-networking-terraform)  
7. [Day 3: Database & Storage (Terraform)](#day-3-database--storage-terraform)  
8. [Day 4: EC2, Auto Scaling & Flask API (CloudFormation)](#day-4-ec2-auto-scaling--flask-api-cloudformation)  
9. [Day 5: S3 → Lambda Logging Pipeline](#day-5-s3--lambda-logging-pipeline)  
10. [Cleanup](#cleanup)

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
├── diagrams/        # Mermaid architecture diagrams
├── terraform/       # Terraform modules & root configs
├── cfn/             # CloudFormation templates
├── lambda/          # Lambda function code & deployment package
├── backend/         # Flask app & SQL scripts
├── frontend/        # React app scaffold
├── scripts/         # Helper scripts (Boto3, CLI)
└── README.md        # This file
```

---

## Prerequisites

- **AWS CLI** v2 installed and configured  
- **Terraform** v1.x installed  
- **Node.js & npm** installed  
- **Python 3.8+** installed  
- Your AWS user/role must have permissions for:  
  - VPC, EC2, RDS, S3, Lambda, CloudFormation  
  - For RDS: `rds:CreateDBSubnetGroup`, `rds:CreateDBInstance`  

---

## Environment Variables & Exports

Throughout this guide, you will export variables in your terminal. Replace placeholder values as needed.

```bash
# General AWS region
export AWS_REGION=us-east-1

# Terraform outputs (run after terraform apply)
export TF_DIR=terraform
export VPC_ID=$(terraform -chdir=$TF_DIR output -raw vpc_id)
export PUBLIC_SUBNETS=$(terraform -chdir=$TF_DIR output -raw public_subnet_ids)
export PRIVATE_SUBNETS=$(terraform -chdir=$TF_DIR output -raw private_subnet_ids)
export BUCKET_NAME=$(terraform -chdir=$TF_DIR output -raw bucket_name)
export DB_ENDPOINT=$(terraform -chdir=$TF_DIR output -raw db_endpoint)

# CloudFormation / other stacks
export CFN_STACK_API=photosnap-ec2-asg
export CFN_STACK_LOGGER=photosnap-s3-logger

# Key pair for EC2
export KEY_NAME=MyKeyPair

# Database credentials
export DB_USER=photosnap_user
export DB_PASS=password

# Local test file
export TEST_FILE=./test.jpg
```

---

## Day 1: Project Initialization

1. **Git & GitHub**  
   ```bash
   cd photosnap-mvp
   git init
   git remote add origin <your-github-repo-url>
   git add .
   git commit -m "Initial project scaffold"
   git push -u origin main
   ```
2. **SQL Schema** (`backend/snaps.sql`)  
   ```sql
   CREATE TABLE snaps (
     id UUID PRIMARY KEY,
     s3_key TEXT NOT NULL
   );
   ```
3. **Architecture Diagram**  
   - Create `diagrams/day1-arch.mmd`.

---

## Day 2: Networking (Terraform)

**Location**: `terraform/`

1. Initialize & plan:
   ```bash
   cd terraform
   terraform init
   terraform plan -var="enable_nat=false"
   ```
2. Apply:
   ```bash
   terraform apply -var="enable_nat=false" -auto-approve
   ```
3. **Outputs**:
   ```bash
   terraform output vpc_id
   terraform output public_subnet_ids
   terraform output private_subnet_ids
   ```

---

## Day 3: Database & Storage (Terraform)

**Location**: `terraform/`

1. Configure DB password:
   ```bash
   export DB_PASS=<YOUR_DB_PASSWORD>
   ```
2. Plan & apply:
   ```bash
   terraform plan      -var="db_password=$DB_PASS"      -var="enable_nat=false"

   terraform apply      -var="db_password=$DB_PASS"      -var="enable_nat=false" -auto-approve
   ```
3. **Verify**:
   ```bash
   aws rds describe-db-instances      --db-instance-identifier photosnap-db      --query 'DBInstances[0].[DBInstanceStatus,Endpoint.Address]'      --output table

   aws s3api get-bucket-lifecycle-configuration      --bucket $BUCKET_NAME
   ```

---

## Day 4: EC2, Auto Scaling & Flask API (CloudFormation)

**Location**: project root

1. **Fetch latest Amazon Linux 2 AMI**:
   ```bash
   AL2_AMI=$(aws ssm get-parameter      --name /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2      --query Parameter.Value --output text)
   ```
2. **Deploy CFN stack**:
   ```bash
   aws cloudformation deploy      --template-file cfn/ec2-asg.yml      --stack-name $CFN_STACK_API      --parameter-overrides        VpcId=$VPC_ID        PublicSubnetIds=$PUBLIC_SUBNETS        AmiId=$AL2_AMI        KeyName=$KEY_NAME        SnapsBucket=$BUCKET_NAME        DbEndpoint=$DB_ENDPOINT        DbUsername=$DB_USER        DbPassword=$DB_PASS        AwsRegion=$AWS_REGION        InstanceType=t2.micro      --capabilities CAPABILITY_NAMED_IAM
   ```
3. **Smoke Test (Local Terminal)**:
   ```bash
   export ALB_DNS=$(aws cloudformation describe-stacks      --stack-name $CFN_STACK_API      --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue"      --output text)
   export ALB_URL="http://$ALB_DNS"

   # Health check
   curl -v $ALB_URL/

   # Upload & download
   RESP=$(curl -s -X POST $ALB_URL/upload      -H "Content-Type: application/json"      -d "{"filename":"$(basename $TEST_FILE)"}")

   PUT_URL=$(jq -r .put_url <<<"$RESP")
   GET_URL=$(jq -r .get_url <<<"$RESP")

   curl --upload-file $TEST_FILE "$PUT_URL" && echo "Uploaded"
   curl -s "$GET_URL" -o downloaded.jpg && echo "Downloaded"
   ```

---

## Day 5: S3 → Lambda Logging Pipeline

**Folder**: `lambda/`, `cfn/`, `scripts/`

1. **Lambda code**: `lambda/s3_logger.py`  
2. **Package**:
   ```bash
   cd lambda
   zip ../lambda/s3_logger.zip s3_logger.py
   cd ..
   ```
3. **Upload**:
   ```bash
   aws s3 cp lambda/s3_logger.zip s3://$BUCKET_NAME/lambda/s3_logger.zip
   ```
4. **Deploy CFN**:
   ```bash
   aws cloudformation deploy      --template-file cfn/s3-logger.yml      --stack-name $CFN_STACK_LOGGER      --parameter-overrides RawSnapsBucket=$BUCKET_NAME      --capabilities CAPABILITY_NAMED_IAM
   ```
5. **Configure trigger**:
   ```bash
   aws s3api put-bucket-notification-configuration      --bucket $BUCKET_NAME      --notification-configuration '{
       "LambdaFunctionConfigurations": [
         {
           "Id":"InvokeS3Logger",
           "LambdaFunctionArn":"'"$(aws lambda get-function              --function-name photoSnapS3Logger              --query 'Configuration.FunctionArn' --output text)"'",
           "Events":["s3:ObjectCreated:*"]
         }
       ]
     }'
   ```
6. **Verify logs**:
   ```bash
   aws logs filter-log-events      --log-group-name /aws/lambda/photoSnapS3Logger      --limit 5      --query 'events[].message'      --output text
   ```
7. **Helper script**:
   ```bash
   python3 scripts/list_upload_logs.py
   ```

---

## Cleanup

1. **CloudFormation stacks**:
   ```bash
   aws cloudformation delete-stack --stack-name $CFN_STACK_API
   aws cloudformation delete-stack --stack-name $CFN_STACK_LOGGER
   ```
2. **Terraform**:
   ```bash
   cd terraform
   terraform destroy      -var="db_password=$DB_PASS"      -var="enable_nat=false"      -auto-approve
   ```
