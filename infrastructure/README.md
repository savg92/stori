# Stori Expense Tracker - AWS Deployment Guide

## AWS Free Tier Deployment

This infrastructure is optimized for the **AWS Free Tier** and should cost **$0-1.20/month** after the free tier expires.

### Free Tier Resources Used

- **ECS Fargate**: 20GB-hours/month (current usage: ~15GB-hours)
- **Application Load Balancer**: 750 hours/month + 15GB data processing
- **ECR**: 500MB container storage
- **CloudWatch**: 5GB log storage
- **Secrets Manager**: 30-day trial, then $0.40/secret/month

### Prerequisites

1. **AWS Account** with free tier available
2. **AWS CLI** installed and configured
3. **Terraform** installed (>= 1.0)
4. **Docker** installed for image building
5. **Domain** (optional, can use ALB DNS name)

### Quick Setup

#### 1. Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (us-east-1 recommended)
```

#### 2. Prepare Terraform Variables

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values
```

#### 3. Deploy Infrastructure

```bash
terraform init
terraform plan
terraform apply
```

#### 4. Build and Push Docker Images

```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd ../backend
docker build -t stori-backend .
docker tag stori-backend:latest <ecr-backend-url>:latest
docker push <ecr-backend-url>:latest

# Build and push frontend
cd ../frontend
docker build -t stori-frontend .
docker tag stori-frontend:latest <ecr-frontend-url>:latest
docker push <ecr-frontend-url>:latest
```

#### 5. Update ECS Services

```bash
# Update services to use the new images
aws ecs update-service --cluster stori-cluster --service stori-backend-service --force-new-deployment
aws ecs update-service --cluster stori-cluster --service stori-frontend-service --force-new-deployment
```

### Cost Monitoring

Monitor your AWS costs in the [AWS Billing Dashboard](https://console.aws.amazon.com/billing/home). With this setup:

- **First 12 months**: Should stay within free tier ($0/month)
- **After free tier**: Approximately $0.40-1.20/month
- **Traffic dependent**: Costs increase with data transfer and usage

### Architecture

```
Internet → ALB → ECS Fargate Tasks
                ├── Frontend (React/Nginx)
                └── Backend (FastAPI)
                    └── Supabase (hosted database)
```

### Scaling

To handle more traffic while staying cost-effective:

1. **Increase task count** during peak hours
2. **Enable auto-scaling** based on CPU/memory
3. **Add CloudFront CDN** for better frontend performance
4. **Implement health checks** for better reliability

### Security Features

- ✅ Private container images in ECR
- ✅ Secrets stored in AWS Secrets Manager
- ✅ Security groups restricting network access
- ✅ ALB with health checks
- ✅ Container security scanning

### Cleanup

To avoid charges, destroy resources when not needed:

```bash
terraform destroy
```

**Note**: This will delete all resources but preserve your Supabase database.

## Troubleshooting

### Common Issues

1. **ECS Task Failing**: Check CloudWatch logs
2. **Health Check Failing**: Verify container ports and health endpoints
3. **Image Pull Errors**: Ensure ECR repositories exist and images are pushed
4. **Secrets Access**: Verify IAM roles have proper permissions

### Useful Commands

```bash
# View ECS service status
aws ecs describe-services --cluster stori-cluster --services stori-backend-service

# View container logs
aws logs describe-log-groups
aws logs tail /aws/ecs/stori-backend --follow

# Check ALB health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

## Next Steps

1. **Custom Domain**: Add Route 53 hosted zone and SSL certificate
2. **CI/CD Pipeline**: Integrate with GitHub Actions for automated deployments
3. **Monitoring**: Add CloudWatch alarms and dashboards
4. **Backup**: Implement database backup strategy
5. **CDN**: Add CloudFront for global content delivery
