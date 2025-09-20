output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID of the EKS cluster"
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

output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster OIDC Issuer"
  value       = module.eks.cluster_oidc_issuer_url
}

output "vpc_id" {
  description = "ID of the VPC where resources are created"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
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
  value       = aws_db_instance.configmaster.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.configmaster.port
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_cluster.configmaster.cache_nodes[0].address
}

output "redis_port" {
  description = "Redis cluster port"
  value       = aws_elasticache_cluster.configmaster.cache_nodes[0].port
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for backups"
  value       = aws_s3_bucket.configmaster_backups.bucket
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.configmaster.repository_url
}

output "load_balancer_dns" {
  description = "DNS name of the load balancer"
  value       = aws_lb.configmaster.dns_name
}

output "configmaster_namespace" {
  description = "Kubernetes namespace for ConfigMaster"
  value       = kubernetes_namespace.configmaster.metadata[0].name
}

output "service_account_role_arn" {
  description = "ARN of the service account IAM role"
  value       = module.configmaster_irsa.iam_role_arn
}

output "database_secret_arn" {
  description = "ARN of the database connection secret"
  value       = aws_secretsmanager_secret.db_connection.arn
  sensitive   = true
}

output "monitoring_grafana_url" {
  description = "URL for Grafana dashboard"
  value       = var.monitoring_config.enable_grafana ? "http://${aws_lb.configmaster.dns_name}/grafana" : null
}

output "api_endpoint" {
  description = "ConfigMaster API endpoint"
  value       = "http://${aws_lb.configmaster.dns_name}/api"
}

output "frontend_url" {
  description = "ConfigMaster frontend URL"
  value       = "http://${aws_lb.configmaster.dns_name}"
}