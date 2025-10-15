# Terraform Outputs for AWS Infrastructure

output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster for the OpenID Connect identity provider"
  value       = module.eks.cluster_oidc_issuer_url
}

output "cluster_oidc_provider_arn" {
  description = "The ARN of the OIDC Provider if one was created"
  value       = module.eks.oidc_provider_arn
}

output "node_groups" {
  description = "EKS node groups"
  value       = module.eks.eks_managed_node_groups
}

output "vpc_id" {
  description = "ID of the VPC where the cluster is deployed"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = module.rds.db_instance_port
}

output "database_name" {
  description = "RDS instance database name"
  value       = module.rds.db_instance_name
}

output "database_username" {
  description = "RDS instance root username"
  value       = module.rds.db_instance_username
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.redis.configuration_endpoint_address
}

output "redis_port" {
  description = "Redis cluster port"
  value       = aws_elasticache_replication_group.redis.port
}

output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "The zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "alb_arn" {
  description = "The ARN of the load balancer"
  value       = aws_lb.main.arn
}

output "static_files_bucket" {
  description = "S3 bucket for static files"
  value       = aws_s3_bucket.static_files.bucket
}

output "media_files_bucket" {
  description = "S3 bucket for media files"
  value       = aws_s3_bucket.media_files.bucket
}

output "static_files_bucket_arn" {
  description = "ARN of the S3 bucket for static files"
  value       = aws_s3_bucket.static_files.arn
}

output "media_files_bucket_arn" {
  description = "ARN of the S3 bucket for media files"
  value       = aws_s3_bucket.media_files.arn
}

output "kubeconfig_command" {
  description = "Command to update kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${var.cluster_name}"
}

output "helm_install_command" {
  description = "Command to install Helm charts"
  value       = "helm repo add stable https://charts.helm.sh/stable && helm repo update"
}

# Connection information for applications
output "database_url" {
  description = "Database connection URL (for application configuration)"
  value       = "postgresql://${module.rds.db_instance_username}:${var.db_password}@${module.rds.db_instance_endpoint}:${module.rds.db_instance_port}/${module.rds.db_instance_name}"
  sensitive   = true
}

output "redis_url" {
  description = "Redis connection URL (for application configuration)"
  value       = "redis://:${var.redis_auth_token}@${aws_elasticache_replication_group.redis.configuration_endpoint_address}:${aws_elasticache_replication_group.redis.port}"
  sensitive   = true
}

# Monitoring and logging outputs
output "cloudwatch_log_groups" {
  description = "CloudWatch log groups created"
  value       = {
    redis = aws_cloudwatch_log_group.redis.name
  }
}

# Security outputs
output "security_groups" {
  description = "Security groups created"
  value       = {
    alb     = aws_security_group.alb.id
    eks     = module.eks.cluster_security_group_id
    rds     = aws_security_group.rds.id
    redis   = aws_security_group.redis.id
  }
}

# Cost estimation (approximate)
output "estimated_monthly_cost" {
  description = "Estimated monthly cost for the infrastructure"
  value       = {
    eks_cluster     = "~$73 (EKS control plane)"
    ec2_instances   = "~$150-300 (depending on instance types and count)"
    rds_database    = "~$50-100 (depending on instance type)"
    elasticache     = "~$30-60 (depending on instance type)"
    alb             = "~$20-40 (depending on usage)"
    s3_storage      = "~$5-20 (depending on storage usage)"
    cloudwatch      = "~$10-30 (depending on log volume)"
    data_transfer   = "~$10-50 (depending on usage)"
    total_estimate  = "~$350-700 per month"
  }
}

