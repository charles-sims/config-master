variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "cluster_version" {
  description = "Kubernetes cluster version"
  type        = string
  default     = "1.28"
}

variable "cluster_endpoint_public_access" {
  description = "Enable public access to cluster endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_private_access" {
  description = "Enable private access to cluster endpoint"
  type        = bool
  default     = true
}

variable "node_groups" {
  description = "EKS node groups configuration"
  type = map(object({
    min_size       = number
    max_size       = number
    desired_size   = number
    instance_types = list(string)
    capacity_type  = string
    labels         = map(string)
    taints         = list(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  default = {
    main = {
      min_size       = 1
      max_size       = 10
      desired_size   = 3
      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
      labels = {
        role = "main"
      }
      taints = []
    }
  }
}

variable "database_config" {
  description = "RDS database configuration"
  type = object({
    engine_version    = string
    instance_class    = string
    allocated_storage = number
    storage_encrypted = bool
    backup_retention  = number
    multi_az          = bool
  })
  default = {
    engine_version    = "15.4"
    instance_class    = "db.t3.micro"
    allocated_storage = 20
    storage_encrypted = true
    backup_retention  = 7
    multi_az          = false
  }
}

variable "redis_config" {
  description = "ElastiCache Redis configuration"
  type = object({
    node_type          = string
    num_cache_nodes    = number
    parameter_group    = string
    engine_version     = string
    at_rest_encryption = bool
    transit_encryption = bool
  })
  default = {
    node_type          = "cache.t3.micro"
    num_cache_nodes    = 1
    parameter_group    = "default.redis7"
    engine_version     = "7.0"
    at_rest_encryption = true
    transit_encryption = true
  }
}

variable "monitoring_config" {
  description = "Monitoring and observability configuration"
  type = object({
    enable_prometheus = bool
    enable_grafana    = bool
    enable_alerting   = bool
    retention_days    = number
  })
  default = {
    enable_prometheus = true
    enable_grafana    = true
    enable_alerting   = true
    retention_days    = 30
  }
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "configmaster.local"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for HTTPS"
  type        = string
  default     = null
}

variable "enable_backup" {
  description = "Enable backup solutions"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}