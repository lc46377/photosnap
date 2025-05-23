resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "photosnap-vpc" }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "public" {
  for_each               = toset(var.public_subnet_cidrs)
  vpc_id                 = aws_vpc.this.id
  cidr_block             = each.value
  map_public_ip_on_launch = true

  # Pick the AZ by index: 0→AZ‑1, 1→AZ‑2
  availability_zone = data.aws_availability_zones.available.names[
    index(var.public_subnet_cidrs, each.value)
  ]

  tags = {
    Name = "public-${each.value}"
    AZ   = data.aws_availability_zones.available.names[
             index(var.public_subnet_cidrs, each.value)
          ]
  }
}

resource "aws_subnet" "private" {
  for_each               = toset(var.private_subnet_cidrs)
  vpc_id                 = aws_vpc.this.id
  cidr_block             = each.value
  map_public_ip_on_launch = false

  availability_zone = data.aws_availability_zones.available.names[
    index(var.private_subnet_cidrs, each.value)
  ]

  tags = {
    Name = "private-${each.value}"
    AZ   = data.aws_availability_zones.available.names[
             index(var.private_subnet_cidrs, each.value)
           ]
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.this.id
  tags = { Name = "photosnap-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_assoc" {
  for_each       = aws_subnet.public
  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

output "vpc_id"               { value = aws_vpc.this.id }
output "public_subnet_ids"    { value = [ for s in aws_subnet.public : s.id ] }
output "private_subnet_ids"   { value = [ for s in aws_subnet.private : s.id ] }
