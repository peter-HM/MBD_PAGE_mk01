terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 보안 그룹
resource "aws_security_group" "mbd_page_sg" {
  name        = "${var.project_name}-sg"
  description = "Security group for ${var.project_name}"

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # App
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 외부 통신 허용
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-sg"
  }
}

# EC2 인스턴스
resource "aws_instance" "mbd_page_server" {
  ami                    = "ami-042e76978adeb8c48"  # Ubuntu 24.04 서울 리전
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.mbd_page_sg.id]

  tags = {
    Name = "${var.project_name}-server"
  }
}

# Elastic IP
resource "aws_eip" "mbd_page_eip" {
  instance = aws_instance.mbd_page_server.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }
}