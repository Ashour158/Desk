# DigitalOcean Infrastructure for Helpdesk Platform
# This Terraform configuration sets up a production-ready DO infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

# Configure the DigitalOcean Provider
provider "digitalocean" {
  token = var.do_token
}

# Variables
variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc3"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "cluster_name" {
  description = "Kubernetes cluster name"
  type        = string
  default     = "helpdesk-cluster"
}

variable "node_count" {
  description = "Number of nodes in the node pool"
  type        = number
  default     = 3
}

variable "node_size" {
  description = "Size of the nodes"
  type        = string
  default     = "s-2vcpu-4gb"
}

# DigitalOcean Kubernetes Cluster
resource "digitalocean_kubernetes_cluster" "main" {
  name    = var.cluster_name
  region  = var.region
  version = "1.28.2-do.0"

  node_pool {
    name       = "worker-pool"
    size       = var.node_size
    node_count = var.node_count
    auto_scale = true
    min_nodes  = 2
    max_nodes  = 10
  }

  tags = [
    "helpdesk",
    var.environment
  ]
}

# DigitalOcean Container Registry
resource "digitalocean_container_registry" "main" {
  name                   = "helpdesk-${var.environment}-registry"
  subscription_tier_slug = "starter"
  region                = var.region
}

# DigitalOcean Database (PostgreSQL)
resource "digitalocean_database_cluster" "postgres" {
  name       = "helpdesk-${var.environment}-postgres"
  engine     = "pg"
  version    = "15"
  size       = "db-s-2vcpu-4gb"
  region     = var.region
  node_count = 1

  tags = [
    "helpdesk",
    var.environment
  ]
}

# PostgreSQL Database
resource "digitalocean_database_db" "main" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "helpdesk"
}

# PostgreSQL User
resource "digitalocean_database_user" "main" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "helpdesk_user"
}

# DigitalOcean Spaces (S3-compatible storage)
resource "digitalocean_spaces_bucket" "static" {
  name   = "helpdesk-${var.environment}-static"
  region = var.region

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

resource "digitalocean_spaces_bucket" "media" {
  name   = "helpdesk-${var.environment}-media"
  region = var.region

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    allowed_origins = ["*"]
    max_age_seconds = 3000
  }
}

# DigitalOcean Load Balancer
resource "digitalocean_loadbalancer" "main" {
  name   = "helpdesk-${var.environment}-lb"
  region = var.region

  forwarding_rule {
    entry_protocol  = "http"
    entry_port      = 80
    target_protocol = "http"
    target_port     = 30080
  }

  forwarding_rule {
    entry_protocol  = "https"
    entry_port      = 443
    target_protocol = "http"
    target_port     = 30080
    tls_passthrough = true
  }

  healthcheck {
    protocol               = "http"
    port                   = 30080
    path                   = "/health/"
    check_interval_seconds = 10
    response_timeout_seconds = 5
    unhealthy_threshold    = 3
    healthy_threshold      = 2
  }

  droplet_ids = digitalocean_kubernetes_cluster.main.node_pool[0].nodes[*].droplet_id
}

# DigitalOcean Monitoring
resource "digitalocean_monitor_alert" "cpu" {
  alerts {
    email = [var.alert_email]
  }
  compare = "GreaterThan"
  description = "CPU usage is above 80%"
  enabled = true
  entities = [digitalocean_kubernetes_cluster.main.id]
  tags = ["helpdesk"]
  type = "v1/insights/droplet/cpu"
  value = 80
  window = "5m"
}

resource "digitalocean_monitor_alert" "memory" {
  alerts {
    email = [var.alert_email]
  }
  compare = "GreaterThan"
  description = "Memory usage is above 80%"
  enabled = true
  entities = [digitalocean_kubernetes_cluster.main.id]
  tags = ["helpdesk"]
  type = "v1/insights/droplet/memory_utilization_percent"
  value = 80
  window = "5m"
}

# DigitalOcean Firewall
resource "digitalocean_firewall" "main" {
  name = "helpdesk-${var.environment}-firewall"

  droplet_ids = digitalocean_kubernetes_cluster.main.node_pool[0].nodes[*].droplet_id

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "30000-32767"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}

# Variables that need to be set
variable "alert_email" {
  description = "Email for monitoring alerts"
  type        = string
}

# Outputs
output "cluster_id" {
  description = "ID of the Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.main.id
}

output "cluster_endpoint" {
  description = "Endpoint for Kubernetes control plane"
  value       = digitalocean_kubernetes_cluster.main.endpoint
}

output "cluster_ca_certificate" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = digitalocean_kubernetes_cluster.main.kube_config[0].cluster_ca_certificate
}

output "cluster_token" {
  description = "Token for Kubernetes cluster"
  value       = digitalocean_kubernetes_cluster.main.kube_config[0].token
}

output "database_endpoint" {
  description = "PostgreSQL database endpoint"
  value       = digitalocean_database_cluster.postgres.host
}

output "database_port" {
  description = "PostgreSQL database port"
  value       = digitalocean_database_cluster.postgres.port
}

output "database_name" {
  description = "PostgreSQL database name"
  value       = digitalocean_database_db.main.name
}

output "database_user" {
  description = "PostgreSQL database user"
  value       = digitalocean_database_user.main.name
}

output "database_password" {
  description = "PostgreSQL database password"
  value       = digitalocean_database_user.main.password
  sensitive   = true
}

output "spaces_static_bucket" {
  description = "Static files Spaces bucket"
  value       = digitalocean_spaces_bucket.static.name
}

output "spaces_media_bucket" {
  description = "Media files Spaces bucket"
  value       = digitalocean_spaces_bucket.media.name
}

output "spaces_endpoint" {
  description = "Spaces endpoint"
  value       = digitalocean_spaces_bucket.static.endpoint
}

output "load_balancer_ip" {
  description = "Load balancer IP address"
  value       = digitalocean_loadbalancer.main.ip
}

output "registry_endpoint" {
  description = "Container registry endpoint"
  value       = digitalocean_container_registry.main.server_url
}

# Cost estimation
output "estimated_monthly_cost" {
  description = "Estimated monthly cost for the infrastructure"
  value = {
    kubernetes_cluster = "~$60 (3 nodes x $20)"
    database          = "~$60 (db-s-2vcpu-4gb)"
    load_balancer     = "~$12"
    spaces_storage    = "~$5-20 (depending on usage)"
    container_registry = "~$5"
    monitoring        = "~$0 (included)"
    total_estimate    = "~$140-200 per month"
  }
}
