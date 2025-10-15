# Azure Infrastructure for Helpdesk Platform with Microsoft Services Integration
# This Terraform configuration sets up a production-ready Azure infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
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
  
  backend "azurerm" {
    resource_group_name  = "helpdesk-terraform-state"
    storage_account_name = "helpdeskterraformstate"
    container_name       = "tfstate"
    key                  = "infrastructure/terraform.tfstate"
  }
}

# Configure the Azure Provider
provider "azurerm" {
  features {}
}

# Data sources
data "azurerm_client_config" "current" {}

# Variables
variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "cluster_name" {
  description = "AKS cluster name"
  type        = string
  default     = "helpdesk-cluster"
}

variable "node_count" {
  description = "Number of nodes in the node pool"
  type        = number
  default     = 3
}

variable "vm_size" {
  description = "Size of the VMs"
  type        = string
  default     = "Standard_D2s_v3"
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "helpdesk-${var.environment}-rg"
  location = var.location

  tags = {
    Environment = var.environment
    Project     = "Helpdesk Platform"
    ManagedBy   = "Terraform"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "helpdesk-${var.environment}-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = {
    Environment = var.environment
  }
}

# Subnets
resource "azurerm_subnet" "aks" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "database" {
  name                 = "database-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Network Security Group
resource "azurerm_network_security_group" "aks" {
  name                = "aks-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    Environment = var.environment
  }
}

# Associate NSG with subnet
resource "azurerm_subnet_network_security_group_association" "aks" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks.id
}

# Azure Container Registry
resource "azurerm_container_registry" "main" {
  name                = "helpdesk${var.environment}acr"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Premium"
  admin_enabled       = true

  tags = {
    Environment = var.environment
  }
}

# Azure Database for PostgreSQL
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "helpdesk-${var.environment}-postgres"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "15"
  administrator_login    = "helpdesk_admin"
  administrator_password = var.db_password

  backup_retention_days        = 7
  geo_redundant_backup_enabled = true

  storage_mb = 32768
  sku_name   = "GP_Standard_D2s_v3"

  high_availability {
    mode = "ZoneRedundant"
  }

  maintenance_window {
    day_of_week  = 0
    start_hour   = 8
    start_minute = 0
  }

  depends_on = [azurerm_subnet.database]

  tags = {
    Environment = var.environment
  }
}

# PostgreSQL Database
resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "helpdesk"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# Azure Cache for Redis
resource "azurerm_redis_cache" "main" {
  name                = "helpdesk-${var.environment}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 1
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
  minimum_tls_version = "1.2"

  redis_configuration {
    maxmemory_reserved = 2
    maxmemory_delta    = 2
    maxmemory_policy   = "allkeys-lru"
  }

  tags = {
    Environment = var.environment
  }
}

# Azure Storage Account for static files
resource "azurerm_storage_account" "static" {
  name                     = "helpdesk${var.environment}static"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  static_website {
    index_document = "index.html"
  }

  tags = {
    Environment = var.environment
  }
}

# Azure Storage Account for media files
resource "azurerm_storage_account" "media" {
  name                     = "helpdesk${var.environment}media"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  tags = {
    Environment = var.environment
  }
}

# Azure Storage Containers
resource "azurerm_storage_container" "static" {
  name                  = "static"
  storage_account_name  = azurerm_storage_account.static.name
  container_access_type = "blob"
}

resource "azurerm_storage_container" "media" {
  name                  = "media"
  storage_account_name  = azurerm_storage_account.media.name
  container_access_type = "private"
}

# Azure Key Vault for secrets
resource "azurerm_key_vault" "main" {
  name                = "helpdesk-${var.environment}-kv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"

  purge_protection_enabled = true

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete",
      "Purge",
      "Recover"
    ]
  }

  tags = {
    Environment = var.environment
  }
}

# Azure Application Insights
resource "azurerm_application_insights" "main" {
  name                = "helpdesk-${var.environment}-insights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"

  tags = {
    Environment = var.environment
  }
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "helpdesk-${var.environment}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30

  tags = {
    Environment = var.environment
  }
}

# Azure Kubernetes Service
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.cluster_name
  kubernetes_version   = "1.28"

  default_node_pool {
    name                = "default"
    node_count          = var.node_count
    vm_size             = var.vm_size
    vnet_subnet_id      = azurerm_subnet.aks.id
    enable_auto_scaling = true
    min_count           = 2
    max_count           = 10
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
  }

  addon_profile {
    oms_agent {
      enabled                    = true
      log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
    }
  }

  tags = {
    Environment = var.environment
  }
}

# Grant AKS access to ACR
resource "azurerm_role_assignment" "aks_acr" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

# Grant AKS access to Key Vault
resource "azurerm_role_assignment" "aks_kv" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

# Azure Front Door (CDN)
resource "azurerm_frontdoor" "main" {
  name                                         = "helpdesk-${var.environment}-fd"
  resource_group_name                          = azurerm_resource_group.main.name
  enforce_backend_pools_certificate_name_check = false

  routing_rule {
    name               = "routing-rule"
    accepted_protocols = ["Http", "Https"]
    patterns_to_match  = ["/*"]
    frontend_endpoints = ["helpdesk-frontend"]
    forwarding_protocol = "MatchRequest"
    backend_pool_name   = "helpdesk-backend"
  }

  backend_pool_load_balancing {
    name = "load-balancing"
  }

  backend_pool_health_probe {
    name = "health-probe"
    protocol = "Http"
    path = "/health/"
  }

  backend_pool {
    name = "helpdesk-backend"
    backend {
      host_header = "helpdesk.azurewebsites.net"
      address     = "helpdesk.azurewebsites.net"
      http_port   = 80
      https_port  = 443
    }

    load_balancing_name = "load-balancing"
    health_probe_name   = "health-probe"
  }

  frontend_endpoint {
    name      = "helpdesk-frontend"
    host_name = "helpdesk-${var.environment}-fd.azurefd.net"
  }

  tags = {
    Environment = var.environment
  }
}

# Variables that need to be set
variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs
output "cluster_name" {
  description = "Name of the AKS cluster"
  value       = azurerm_kubernetes_cluster.main.name
}

output "cluster_endpoint" {
  description = "Endpoint for AKS control plane"
  value       = azurerm_kubernetes_cluster.main.kube_config.0.host
}

output "cluster_ca_certificate" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = azurerm_kubernetes_cluster.main.kube_config.0.cluster_ca_certificate
}

output "client_key" {
  description = "Client key for AKS cluster"
  value       = azurerm_kubernetes_cluster.main.kube_config.0.client_key
}

output "client_certificate" {
  description = "Client certificate for AKS cluster"
  value       = azurerm_kubernetes_cluster.main.kube_config.0.client_certificate
}

output "database_endpoint" {
  description = "PostgreSQL server endpoint"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "redis_endpoint" {
  description = "Redis cache endpoint"
  value       = azurerm_redis_cache.main.hostname
}

output "redis_port" {
  description = "Redis cache port"
  value       = azurerm_redis_cache.main.port
}

output "storage_account_static" {
  description = "Static files storage account name"
  value       = azurerm_storage_account.static.name
}

output "storage_account_media" {
  description = "Media files storage account name"
  value       = azurerm_storage_account.media.name
}

output "key_vault_name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.main.name
}

output "application_insights_key" {
  description = "Application Insights instrumentation key"
  value       = azurerm_application_insights.main.instrumentation_key
}

output "front_door_hostname" {
  description = "Front Door hostname"
  value       = azurerm_frontdoor.main.frontend_endpoint[0].host_name
}
