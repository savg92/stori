#!/bin/bash
# Clean up all existing AWS resources for Stori application
# This will delete everything so we can redeploy from scratch with Terraform

set -e  # Exit on any error

AWS_REGION="us-east-1"
CLUSTER_NAME="stori-cluster"

echo "🗑️  Starting AWS resource cleanup for fresh deployment..."
echo "⚠️   This will delete ALL existing Stori resources in AWS!"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "🔄 Step 1: Stopping ECS Services..."

# Stop ECS services by setting desired count to 0
aws ecs update-service \
    --cluster "$CLUSTER_NAME" \
    --service "stori-backend-service" \
    --desired-count 0 \
    --region "$AWS_REGION" || echo "Backend service not found or already stopped"

aws ecs update-service \
    --cluster "$CLUSTER_NAME" \
    --service "stori-frontend-service" \
    --desired-count 0 \
    --region "$AWS_REGION" || echo "Frontend service not found or already stopped"

echo "⏳ Waiting for services to stop..."
sleep 30

echo ""
echo "🗑️  Step 2: Deleting ECS Services..."

aws ecs delete-service \
    --cluster "$CLUSTER_NAME" \
    --service "stori-backend-service" \
    --region "$AWS_REGION" || echo "Backend service not found"

aws ecs delete-service \
    --cluster "$CLUSTER_NAME" \
    --service "stori-frontend-service" \
    --region "$AWS_REGION" || echo "Frontend service not found"

echo ""
echo "🗑️  Step 3: Deleting ECS Cluster..."
aws ecs delete-cluster \
    --cluster "$CLUSTER_NAME" \
    --region "$AWS_REGION" || echo "Cluster not found"

echo ""
echo "🗑️  Step 4: Deleting Load Balancer..."
ALB_ARN=$(aws elbv2 describe-load-balancers \
    --names "stori-alb" \
    --region "$AWS_REGION" \
    --query 'LoadBalancers[0].LoadBalancerArn' \
    --output text 2>/dev/null || echo "")

if [ "$ALB_ARN" != "" ] && [ "$ALB_ARN" != "None" ]; then
    aws elbv2 delete-load-balancer \
        --load-balancer-arn "$ALB_ARN" \
        --region "$AWS_REGION"
    echo "Load balancer deleted"
else
    echo "Load balancer not found"
fi

echo ""
echo "🗑️  Step 5: Deleting Target Groups..."
aws elbv2 delete-target-group \
    --target-group-arn $(aws elbv2 describe-target-groups \
        --names "stori-backend-tg" \
        --region "$AWS_REGION" \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text 2>/dev/null) \
    --region "$AWS_REGION" 2>/dev/null || echo "Backend target group not found"

aws elbv2 delete-target-group \
    --target-group-arn $(aws elbv2 describe-target-groups \
        --names "stori-frontend-tg" \
        --region "$AWS_REGION" \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text 2>/dev/null) \
    --region "$AWS_REGION" 2>/dev/null || echo "Frontend target group not found"

echo ""
echo "🗑️  Step 6: Deleting ECR Repositories..."
aws ecr delete-repository \
    --repository-name "stori-backend" \
    --region "$AWS_REGION" \
    --force || echo "Backend ECR repository not found"

aws ecr delete-repository \
    --repository-name "stori-frontend" \
    --region "$AWS_REGION" \
    --force || echo "Frontend ECR repository not found"

echo ""
echo "🗑️  Step 7: Deleting IAM Roles..."
# Detach policies first
aws iam detach-role-policy \
    --role-name "stori-ecs-task-execution-role" \
    --policy-arn "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" 2>/dev/null || echo "Policy not attached"

aws iam delete-role-policy \
    --role-name "stori-ecs-task-execution-role" \
    --policy-name "stori-ecs-secrets-policy" 2>/dev/null || echo "Inline policy not found"

aws iam delete-role \
    --role-name "stori-ecs-task-execution-role" 2>/dev/null || echo "Task execution role not found"

aws iam delete-role \
    --role-name "stori-ecs-task-role" 2>/dev/null || echo "Task role not found"

echo ""
echo "🗑️  Step 8: Deleting Secrets Manager Secret..."
aws secretsmanager delete-secret \
    --secret-id "stori/production/app-secrets" \
    --region "$AWS_REGION" \
    --force-delete-without-recovery 2>/dev/null || echo "Secret not found"

echo ""
echo "🗑️  Step 9: Deleting CloudWatch Log Groups..."
aws logs delete-log-group \
    --log-group-name "/aws/ecs/stori-backend" \
    --region "$AWS_REGION" 2>/dev/null || echo "Backend log group not found"

aws logs delete-log-group \
    --log-group-name "/aws/ecs/stori-frontend" \
    --region "$AWS_REGION" 2>/dev/null || echo "Frontend log group not found"

echo ""
echo "⏳ Waiting for resources to be fully deleted..."
sleep 60

echo ""
echo "✅ AWS resource cleanup complete!"
echo "🚀 You can now run the infrastructure deployment to create everything fresh."
echo ""
echo "Next steps:"
echo "1. Commit and push with [deploy-infra] message"
echo "2. Watch GitHub Actions deploy clean infrastructure"
echo "3. Verify ECS services start successfully"