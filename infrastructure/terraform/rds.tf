# RDS Subnet Group
resource "aws_db_subnet_group" "configmaster" {
  name       = local.name
  subnet_ids = module.vpc.intra_subnets

  tags = merge(local.tags, {
    Name = "${local.name}-db-subnet-group"
  })
}

# Random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = "${local.name}-db-password"
  description = "Database password for ConfigMaster"

  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = "configmaster"
    password = random_password.db_password.result
  })
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "configmaster" {
  identifier = local.name

  engine         = "postgres"
  engine_version = var.database_config.engine_version
  instance_class = var.database_config.instance_class

  allocated_storage     = var.database_config.allocated_storage
  max_allocated_storage = var.database_config.allocated_storage * 2
  storage_type          = "gp3"
  storage_encrypted     = var.database_config.storage_encrypted

  db_name  = "configmaster"
  username = "configmaster"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.configmaster_db.id]
  db_subnet_group_name   = aws_db_subnet_group.configmaster.name

  backup_retention_period = var.database_config.backup_retention
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  multi_az               = var.database_config.multi_az
  publicly_accessible    = false
  copy_tags_to_snapshot  = true
  deletion_protection    = var.environment == "prod"
  skip_final_snapshot    = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${local.name}-final-snapshot" : null

  # Enhanced monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn

  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7

  tags = merge(local.tags, {
    Name = "${local.name}-database"
  })
}

# IAM role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "${local.name}-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# Database parameter group
resource "aws_db_parameter_group" "configmaster" {
  family = "postgres15"
  name   = local.name

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  tags = local.tags
}

# Create database secret for application
resource "aws_secretsmanager_secret" "db_connection" {
  name        = "${local.name}-db-connection"
  description = "Database connection details for ConfigMaster"

  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "db_connection" {
  secret_id = aws_secretsmanager_secret.db_connection.id
  secret_string = jsonencode({
    host     = aws_db_instance.configmaster.address
    port     = aws_db_instance.configmaster.port
    database = aws_db_instance.configmaster.db_name
    username = aws_db_instance.configmaster.username
    password = random_password.db_password.result
    url      = "postgresql://${aws_db_instance.configmaster.username}:${random_password.db_password.result}@${aws_db_instance.configmaster.address}:${aws_db_instance.configmaster.port}/${aws_db_instance.configmaster.db_name}"
  })
}