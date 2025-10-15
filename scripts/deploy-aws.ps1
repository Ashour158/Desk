# AWS Production Deployment Script for Helpdesk Platform
# This script handles the complete AWS production deployment process

param(
    [Parameter(Mandatory=$true)]
    [string]$StackName = "helpdesk-platform",
    
    [Parameter(Mandatory=$true)]
    [string]$DatabasePassword,
    
    [Parameter(Mandatory=$true)]
    [string]$DomainName,
    
    [string]$Environment = "production",
    [string]$TemplateFile = "deploy/aws/cloudformation.yaml",
    [string]$Region = "us-east-1",
    [switch]$DryRun,
    [switch]$Verbose
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$White = "White"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Check if AWS CLI is installed and configured
function Test-AWSCLI {
    Write-Status "Checking AWS CLI configuration..."
    
    try {
        $awsVersion = aws --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "AWS CLI not found"
        }
        Write-Success "AWS CLI is installed: $awsVersion"
    } catch {
        Write-Error "AWS CLI is not installed or not in PATH"
        Write-Error "Please install AWS CLI and configure it with your credentials"
        exit 1
    }
    
    # Check AWS credentials
    try {
        $awsIdentity = aws sts get-caller-identity 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "AWS credentials not configured"
        }
        Write-Success "AWS credentials are configured"
    } catch {
        Write-Error "AWS credentials are not configured"
        Write-Error "Please run 'aws configure' to set up your credentials"
        exit 1
    }
}

# Check if CloudFormation template exists
function Test-TemplateFile {
    Write-Status "Checking CloudFormation template..."
    
    if (-not (Test-Path $TemplateFile)) {
        Write-Error "CloudFormation template not found: $TemplateFile"
        exit 1
    }
    
    Write-Success "CloudFormation template found: $TemplateFile"
}

# Validate CloudFormation template
function Test-TemplateValidation {
    Write-Status "Validating CloudFormation template..."
    
    try {
        aws cloudformation validate-template --template-body file://$TemplateFile --region $Region 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Template validation failed"
        }
        Write-Success "CloudFormation template is valid"
    } catch {
        Write-Error "CloudFormation template validation failed"
        Write-Error "Please check the template syntax and try again"
        exit 1
    }
}

# Deploy CloudFormation stack
function Deploy-CloudFormationStack {
    Write-Status "Deploying CloudFormation stack: $StackName"
    
    $deployCommand = @(
        "aws", "cloudformation", "deploy",
        "--template-file", $TemplateFile,
        "--stack-name", $StackName,
        "--parameter-overrides",
        "Environment=$Environment",
        "DatabasePassword=$DatabasePassword",
        "DomainName=$DomainName",
        "--capabilities", "CAPABILITY_IAM",
        "--region", $Region
    )
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - No actual deployment will occur"
        Write-Status "Command that would be executed:"
        Write-Host ($deployCommand -join " ") -ForegroundColor $White
        return
    }
    
    try {
        & $deployCommand[0] $deployCommand[1..($deployCommand.Length-1)]
        if ($LASTEXITCODE -ne 0) {
            throw "CloudFormation deployment failed"
        }
        Write-Success "CloudFormation stack deployed successfully"
    } catch {
        Write-Error "CloudFormation deployment failed"
        Write-Error "Check the AWS CloudFormation console for details"
        exit 1
    }
}

# Wait for stack deployment to complete
function Wait-StackCompletion {
    Write-Status "Waiting for stack deployment to complete..."
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - Skipping stack completion wait"
        return
    }
    
    try {
        aws cloudformation wait stack-create-complete --stack-name $StackName --region $Region 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Stack deployment did not complete successfully"
        }
        Write-Success "Stack deployment completed successfully"
    } catch {
        Write-Error "Stack deployment did not complete successfully"
        Write-Error "Check the AWS CloudFormation console for details"
        exit 1
    }
}

# Get stack outputs
function Get-StackOutputs {
    Write-Status "Retrieving stack outputs..."
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - Skipping stack outputs retrieval"
        return
    }
    
    try {
        $outputs = aws cloudformation describe-stacks --stack-name $StackName --region $Region --query "Stacks[0].Outputs" --output table 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to retrieve stack outputs"
        }
        Write-Success "Stack outputs retrieved successfully"
        Write-Host $outputs -ForegroundColor $White
    } catch {
        Write-Error "Failed to retrieve stack outputs"
        Write-Error "Check the AWS CloudFormation console for details"
    }
}

# Deploy application to ECS
function Deploy-Application {
    Write-Status "Deploying application to ECS..."
    
    if ($DryRun) {
        Write-Warning "DRY RUN MODE - Skipping application deployment"
        return
    }
    
    try {
        # Get ECS cluster name from stack outputs
        $clusterName = aws cloudformation describe-stacks --stack-name $StackName --region $Region --query "Stacks[0].Outputs[?OutputKey=='ECSClusterName'].OutputValue" --output text 2>$null
        
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($clusterName)) {
            throw "Failed to retrieve ECS cluster name"
        }
        
        Write-Status "ECS Cluster: $clusterName"
        
        # Update ECS service
        $serviceName = aws cloudformation describe-stacks --stack-name $StackName --region $Region --query "Stacks[0].Outputs[?OutputKey=='ECSServiceName'].OutputValue" --output text 2>$null
        
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($serviceName)) {
            throw "Failed to retrieve ECS service name"
        }
        
        Write-Status "ECS Service: $serviceName"
        
        # Force new deployment
        aws ecs update-service --cluster $clusterName --service $serviceName --force-new-deployment --region $Region 2>$null
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to update ECS service"
        }
        
        Write-Success "Application deployed to ECS successfully"
    } catch {
        Write-Error "Application deployment failed"
        Write-Error "Check the AWS ECS console for details"
        exit 1
    }
}

# Show deployment summary
function Show-DeploymentSummary {
    Write-Success "🎉 AWS Production deployment completed successfully!"
    Write-Host ""
    Write-Host "📊 Deployment Summary:" -ForegroundColor $White
    Write-Host "=====================" -ForegroundColor $White
    Write-Host "✅ CloudFormation stack deployed" -ForegroundColor $Green
    Write-Host "✅ ECS cluster and services created" -ForegroundColor $Green
    Write-Host "✅ RDS Aurora PostgreSQL database created" -ForegroundColor $Green
    Write-Host "✅ ElastiCache Redis cluster created" -ForegroundColor $Green
    Write-Host "✅ Application Load Balancer configured" -ForegroundColor $Green
    Write-Host "✅ SSL certificates configured" -ForegroundColor $Green
    Write-Host ""
    Write-Host "🌐 Access Points:" -ForegroundColor $White
    Write-Host "=================" -ForegroundColor $White
    Write-Host "• Application URL: https://$DomainName" -ForegroundColor $Blue
    Write-Host "• API Documentation: https://$DomainName/api/swagger/" -ForegroundColor $Blue
    Write-Host "• Health Check: https://$DomainName/health/" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "📝 Next Steps:" -ForegroundColor $White
    Write-Host "==============" -ForegroundColor $White
    Write-Host "1. Configure DNS records to point to the Application Load Balancer" -ForegroundColor $Yellow
    Write-Host "2. Set up SSL certificates for your domain" -ForegroundColor $Yellow
    Write-Host "3. Configure monitoring and alerting" -ForegroundColor $Yellow
    Write-Host "4. Set up backup strategies" -ForegroundColor $Yellow
    Write-Host "5. Configure auto-scaling policies" -ForegroundColor $Yellow
    Write-Host ""
    Write-Host "🔧 Useful Commands:" -ForegroundColor $White
    Write-Host "===================" -ForegroundColor $White
    Write-Host "• View stack status: aws cloudformation describe-stacks --stack-name $StackName --region $Region" -ForegroundColor $Blue
    Write-Host "• View ECS services: aws ecs list-services --cluster $StackName-cluster --region $Region" -ForegroundColor $Blue
    Write-Host "• View logs: aws logs describe-log-groups --region $Region" -ForegroundColor $Blue
    Write-Host "• Delete stack: aws cloudformation delete-stack --stack-name $StackName --region $Region" -ForegroundColor $Blue
    Write-Host ""
}

# Main deployment function
function Main {
    Write-Host "🚀 Helpdesk Platform AWS Production Deployment" -ForegroundColor $White
    Write-Host "=============================================" -ForegroundColor $White
    Write-Host ""
    
    # Run deployment steps
    Test-AWSCLI
    Test-TemplateFile
    Test-TemplateValidation
    Deploy-CloudFormationStack
    Wait-StackCompletion
    Get-StackOutputs
    Deploy-Application
    Show-DeploymentSummary
    
    Write-Success "🎉 AWS Production deployment completed successfully!"
}

# Run main function
Main
