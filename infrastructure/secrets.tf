# AWS Secrets Manager for environment variables
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "stori/production/app-secrets"
  description             = "Application secrets for Stori Expense Tracker"
  recovery_window_in_days = 7  # Minimum for deletion

  tags = {
    Name        = "stori-app-secrets"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  
  secret_string = jsonencode({
    SUPABASE_URL              = var.supabase_url
    SUPABASE_ANON_KEY        = var.supabase_anon_key
    SUPABASE_PUBLISHABLE_KEY  = var.supabase_anon_key
    SUPABASE_SERVICE_ROLE_KEY = var.supabase_service_key
    OPENROUTER_API_KEY       = var.openrouter_api_key
    OPENROUTER_MODEL         = "z-ai/glm-4.5-air:free"
    JWT_SECRET_KEY           = random_password.jwt_secret.result
    ENVIRONMENT              = var.environment
    DEBUG                    = "false"
    DEFAULT_LLM_PROVIDER     = "openrouter"
    LLM_PROVIDER             = "openrouter"
    USE_LOCAL_SUPABASE       = "false"
  })
}

# Generate random JWT secret
resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# CloudWatch Log Groups (Free tier: 5GB storage, never expires)
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/aws/ecs/stori-backend"
  retention_in_days = 7  # Keep costs minimal
  
  tags = {
    Name = "stori-backend-logs"
  }
}

resource "aws_cloudwatch_log_group" "frontend" {
  name              = "/aws/ecs/stori-frontend"
  retention_in_days = 7  # Keep costs minimal
  
  tags = {
    Name = "stori-frontend-logs"
  }
}