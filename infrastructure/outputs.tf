# Outputs
output "ecr_backend_url" {
  description = "ECR repository URL for backend"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "ECR repository URL for frontend"
  value       = aws_ecr_repository.frontend.repository_url
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}

output "backend_api_url" {
  description = "URL to access the backend API"
  value       = "http://${aws_lb.main.dns_name}/api"
}

output "api_documentation_url" {
  description = "URL to access the API documentation"
  value       = "http://${aws_lb.main.dns_name}/docs"
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "secrets_manager_arn" {
  description = "ARN of the secrets manager secret"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "aws_region" {
  description = "AWS region used for deployment"
  value       = var.aws_region
}

# Cost estimation outputs
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown"
  value = {
    ecs_fargate = "FREE (20GB-hours included in free tier)"
    load_balancer = "FREE (750 hours + 15GB data processing included)"
    ecr_storage = "FREE (500MB included in free tier)"
    cloudwatch_logs = "FREE (5GB included in free tier)"
    secrets_manager = "$0.40 per secret per month (after 30-day trial)"
    estimated_total = "$0.40 - $1.20 per month (after free tier expires)"
  }
}

output "free_tier_limits" {
  description = "AWS Free Tier limits and current usage"
  value = {
    ecs_fargate_hours = "20GB-hours per month (current usage: ~15GB-hours with 1 task each)"
    alb_hours = "750 hours per month (current usage: 24/7 = 744 hours)"
    alb_data_processing = "15GB per month"
    ecr_storage = "500MB per month"
    cloudwatch_logs = "5GB storage per month"
    note = "This configuration stays well within free tier limits"
  }
}