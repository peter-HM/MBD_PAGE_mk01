variable "aws_region" {
  description = "AWS region"
  default = "ap-northeast-2"
}

variable "instance_type" {
  description = "EC2 instance type"
  default = "t3.micro"
}

variable "key_name" {
  description = "EC2 key pair name"
  default = "mbd-page-key"
}

variable "project_name" {
  description = "project name"
  default = "mbd-page"
}

