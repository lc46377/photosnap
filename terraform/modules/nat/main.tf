# 1) Allocate an EIP for the NAT Gateway
resource "aws_eip" "nat_eip" {
  count  = var.enable_nat ? 1 : 0
  domain = "vpc"
}

# 2) Create the NAT Gateway
resource "aws_nat_gateway" "natgw" {
  count         = var.enable_nat ? 1 : 0
  allocation_id = aws_eip.nat_eip[0].id
  subnet_id     = var.public_subnet_id
  tags = {
    Name = "photosnap-nat-gateway"
  }
}

# 3) Private route table
resource "aws_route_table" "private" {
  count  = var.enable_nat ? 1 : 0
  vpc_id = var.vpc_id
  tags = {
    Name = "photosnap-private-rt"
  }
}

# 4) Default route in the private RT via the NAT Gateway
resource "aws_route" "private_nat_route" {
  count                  = var.enable_nat ? 1 : 0
  route_table_id         = aws_route_table.private[0].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.natgw[0].id
}

# 5) Associate each private subnet to that private RT
resource "aws_route_table_association" "private_assoc" {
  count          = var.enable_nat ? length(var.private_subnet_ids) : 0
  subnet_id      = var.private_subnet_ids[count.index]
  route_table_id = aws_route_table.private[0].id
}
