# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = local.name
  cluster_version = var.cluster_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  cluster_endpoint_private_access = var.cluster_endpoint_private_access

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    for name, config in var.node_groups : name => {
      min_size       = config.min_size
      max_size       = config.max_size
      desired_size   = config.desired_size
      instance_types = config.instance_types
      capacity_type  = config.capacity_type

      labels = config.labels

      dynamic "taint" {
        for_each = config.taints
        content {
          key    = taint.value.key
          value  = taint.value.value
          effect = taint.value.effect
        }
      }

      update_config = {
        max_unavailable_percentage = 25
      }

      tags = local.tags
    }
  }

  # aws-auth configmap
  manage_aws_auth_configmap = true

  aws_auth_roles = [
    {
      rolearn  = aws_iam_role.configmaster_admin.arn
      username = "configmaster-admin"
      groups   = ["system:masters"]
    },
  ]

  aws_auth_users = [
    {
      userarn  = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      username = "root"
      groups   = ["system:masters"]
    },
  ]

  tags = local.tags
}

# IAM role for ConfigMaster administrators
resource "aws_iam_role" "configmaster_admin" {
  name = "${local.name}-admin"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
      },
    ]
  })

  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "configmaster_admin_eks" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.configmaster_admin.name
}

# OIDC Provider for EKS
data "tls_certificate" "eks" {
  url = module.eks.cluster_oidc_issuer_url
}

resource "aws_iam_openid_connect_provider" "eks" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
  url             = module.eks.cluster_oidc_issuer_url

  tags = local.tags
}

# Service Account for ConfigMaster
resource "kubernetes_namespace" "configmaster" {
  metadata {
    name = "configmaster"
    labels = {
      "app.kubernetes.io/name" = "configmaster"
    }
  }

  depends_on = [module.eks]
}

# IAM role for ConfigMaster service account
module "configmaster_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name = "${local.name}-service-account"

  oidc_providers = {
    ex = {
      provider_arn               = aws_iam_openid_connect_provider.eks.arn
      namespace_service_accounts = ["configmaster:configmaster"]
    }
  }

  role_policy_arns = {
    policy = aws_iam_policy.configmaster_service.arn
  }

  tags = local.tags
}

resource "aws_iam_policy" "configmaster_service" {
  name        = "${local.name}-service"
  description = "IAM policy for ConfigMaster service"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:DescribeVpcs",
          "ecs:ListClusters",
          "ecs:ListContainerInstances",
          "ecs:ListServices",
          "ecs:ListTasks",
          "ecs:DescribeClusters",
          "ecs:DescribeContainerInstances",
          "ecs:DescribeServices",
          "ecs:DescribeTasks",
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "elasticache:DescribeCacheClusters",
          "elasticache:DescribeReplicationGroups",
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.tags
}

resource "kubernetes_service_account" "configmaster" {
  metadata {
    name      = "configmaster"
    namespace = kubernetes_namespace.configmaster.metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = module.configmaster_irsa.iam_role_arn
    }
  }

  depends_on = [module.eks]
}