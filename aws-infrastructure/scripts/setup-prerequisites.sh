#!/bin/bash

# Prerequisites Setup Script for AWS Helpdesk Platform
# This script installs all required tools and dependencies

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    log_info "Detected OS: $OS"
}

# Install AWS CLI
install_aws_cli() {
    log_step "Installing AWS CLI..."
    
    if command -v aws &> /dev/null; then
        log_info "AWS CLI is already installed: $(aws --version)"
        return
    fi
    
    if [[ "$OS" == "linux" ]]; then
        curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        unzip awscliv2.zip
        sudo ./aws/install
        rm -rf aws awscliv2.zip
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install awscli
        else
            curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
            sudo installer -pkg AWSCLIV2.pkg -target /
            rm AWSCLIV2.pkg
        fi
    else
        log_error "Please install AWS CLI manually for your OS"
        exit 1
    fi
    
    log_info "AWS CLI installed successfully: $(aws --version)"
}

# Install kubectl
install_kubectl() {
    log_step "Installing kubectl..."
    
    if command -v kubectl &> /dev/null; then
        log_info "kubectl is already installed: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
        return
    fi
    
    if [[ "$OS" == "linux" ]]; then
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install kubectl
        else
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
            sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
        fi
    else
        log_error "Please install kubectl manually for your OS"
        exit 1
    fi
    
    log_info "kubectl installed successfully: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
}

# Install Helm
install_helm() {
    log_step "Installing Helm..."
    
    if command -v helm &> /dev/null; then
        log_info "Helm is already installed: $(helm version --short)"
        return
    fi
    
    if [[ "$OS" == "linux" ]]; then
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install helm
        else
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
        fi
    else
        log_error "Please install Helm manually for your OS"
        exit 1
    fi
    
    log_info "Helm installed successfully: $(helm version --short)"
}

# Install Terraform
install_terraform() {
    log_step "Installing Terraform..."
    
    if command -v terraform &> /dev/null; then
        log_info "Terraform is already installed: $(terraform version -json | jq -r '.terraform_version')"
        return
    fi
    
    if [[ "$OS" == "linux" ]]; then
        wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
        unzip terraform_1.6.0_linux_amd64.zip
        sudo mv terraform /usr/local/bin/
        rm terraform_1.6.0_linux_amd64.zip
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install terraform
        else
            wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_darwin_amd64.zip
            unzip terraform_1.6.0_darwin_amd64.zip
            sudo mv terraform /usr/local/bin/
            rm terraform_1.6.0_darwin_amd64.zip
        fi
    else
        log_error "Please install Terraform manually for your OS"
        exit 1
    fi
    
    log_info "Terraform installed successfully: $(terraform version -json | jq -r '.terraform_version')"
}

# Install Docker
install_docker() {
    log_step "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker is already installed: $(docker --version)"
        return
    fi
    
    if [[ "$OS" == "linux" ]]; then
        # Update package index
        sudo apt-get update
        
        # Install required packages
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # Add Docker's official GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # Set up the repository
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # Install Docker Engine
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # Add user to docker group
        sudo usermod -aG docker $USER
        
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install --cask docker
        else
            log_error "Please install Docker Desktop for Mac manually"
            exit 1
        fi
    else
        log_error "Please install Docker manually for your OS"
        exit 1
    fi
    
    log_info "Docker installed successfully: $(docker --version)"
    log_warn "Please log out and log back in for Docker group changes to take effect"
}

# Install jq
install_jq() {
    log_step "Installing jq..."
    
    if command -v jq &> /dev/null; then
        log_info "jq is already installed: $(jq --version)"
        return
    fi
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt-get update
        sudo apt-get install -y jq
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install jq
        else
            log_error "Please install jq manually"
            exit 1
        fi
    else
        log_error "Please install jq manually for your OS"
        exit 1
    fi
    
    log_info "jq installed successfully: $(jq --version)"
}

# Install additional tools
install_additional_tools() {
    log_step "Installing additional tools..."
    
    # Install hey for load testing
    if ! command -v hey &> /dev/null; then
        if command -v go &> /dev/null; then
            go install github.com/rakyll/hey@latest
            log_info "hey installed for load testing"
        else
            log_warn "Go not found. Install hey manually: go install github.com/rakyll/hey@latest"
        fi
    fi
    
    # Install k9s for Kubernetes management
    if ! command -v k9s &> /dev/null; then
        if [[ "$OS" == "linux" ]]; then
            wget https://github.com/derailed/k9s/releases/download/v0.27.4/k9s_Linux_amd64.tar.gz
            tar -xzf k9s_Linux_amd64.tar.gz
            sudo mv k9s /usr/local/bin/
            rm k9s_Linux_amd64.tar.gz
        elif [[ "$OS" == "macos" ]]; then
            if command -v brew &> /dev/null; then
                brew install k9s
            else
                log_warn "Install k9s manually for better Kubernetes management"
            fi
        fi
    fi
    
    log_info "Additional tools installation completed"
}

# Configure AWS CLI
configure_aws() {
    log_step "Configuring AWS CLI..."
    
    if aws sts get-caller-identity &> /dev/null; then
        log_info "AWS CLI is already configured"
        aws sts get-caller-identity
        return
    fi
    
    log_warn "AWS CLI is not configured. Please run 'aws configure' with your credentials:"
    echo "1. AWS Access Key ID"
    echo "2. AWS Secret Access Key"
    echo "3. Default region (us-west-2)"
    echo "4. Default output format (json)"
    echo ""
    echo "You can get these from the AWS Console > IAM > Users > Your User > Security Credentials"
    echo ""
    read -p "Press Enter to continue after configuring AWS CLI..."
    
    if aws sts get-caller-identity &> /dev/null; then
        log_info "AWS CLI configured successfully"
        aws sts get-caller-identity
    else
        log_error "AWS CLI configuration failed"
        exit 1
    fi
}

# Verify installations
verify_installations() {
    log_step "Verifying all installations..."
    
    local all_good=true
    
    # Check AWS CLI
    if command -v aws &> /dev/null; then
        log_info "✓ AWS CLI: $(aws --version)"
    else
        log_error "✗ AWS CLI not found"
        all_good=false
    fi
    
    # Check kubectl
    if command -v kubectl &> /dev/null; then
        log_info "✓ kubectl: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
    else
        log_error "✗ kubectl not found"
        all_good=false
    fi
    
    # Check Helm
    if command -v helm &> /dev/null; then
        log_info "✓ Helm: $(helm version --short)"
    else
        log_error "✗ Helm not found"
        all_good=false
    fi
    
    # Check Terraform
    if command -v terraform &> /dev/null; then
        log_info "✓ Terraform: $(terraform version -json | jq -r '.terraform_version')"
    else
        log_error "✗ Terraform not found"
        all_good=false
    fi
    
    # Check Docker
    if command -v docker &> /dev/null; then
        log_info "✓ Docker: $(docker --version)"
    else
        log_error "✗ Docker not found"
        all_good=false
    fi
    
    # Check jq
    if command -v jq &> /dev/null; then
        log_info "✓ jq: $(jq --version)"
    else
        log_error "✗ jq not found"
        all_good=false
    fi
    
    if $all_good; then
        log_info "🎉 All tools installed successfully!"
    else
        log_error "Some tools failed to install. Please check the errors above."
        exit 1
    fi
}

# Main execution
main() {
    echo "🔧 Setting up prerequisites for AWS Helpdesk Platform deployment..."
    echo ""
    
    detect_os
    install_aws_cli
    install_kubectl
    install_helm
    install_terraform
    install_docker
    install_jq
    install_additional_tools
    configure_aws
    verify_installations
    
    echo ""
    log_info "🎉 Prerequisites setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Make sure Docker is running"
    echo "2. Run the quick deployment script: ./aws-infrastructure/scripts/quick-deploy.sh"
    echo "3. Or follow the detailed deployment guide: AWS_DEPLOYMENT_GUIDE.md"
    echo ""
}

# Run main function
main "$@"
