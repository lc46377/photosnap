resource "aws_db_subnet_group" "snaps" {
  name       = "photosnap-db-subnet-group"
  subnet_ids = var.private_subnets
  tags = { Name = "photosnap-db-subnet-group" }
}

resource "aws_security_group" "rds" {
  name        = "photosnap-rds-sg"
  description = "Allow only EC2 to connect"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "photosnap-rds-sg" }
}

resource "aws_db_instance" "snaps" {
  identifier             = "photosnap-db"
  engine                 = "postgres"
  engine_version         = "14.12"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.snaps.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  multi_az               = false
  backup_retention_period= 1
  tags                   = { Name = "photosnap-db" }
}
