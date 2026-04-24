output "instance_id" {
  description = "EC2 인스턴스 ID"
  value       = aws_instance.mbd_page_server.id
}

output "elastic_ip" {
  description = "Elastic IP 주소"
  value       = aws_eip.mbd_page_eip.public_ip
}

output "security_group_id" {
  description = "보안 그룹 ID"
  value       = aws_security_group.mbd_page_sg.id
}

output "ssh_command" {
  description = "SSH 접속 명령어"
  value       = "ssh -i ~/.ssh/mbd-page-key.pem ubuntu@${aws_eip.mbd_page_eip.public_ip}"
}
