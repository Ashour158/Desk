# Environment Setup Validation Script for Windows PowerShell
# Validates prerequisites and environment configuration for the Helpdesk Platform

param(
    [switch]$Help,
    [switch]$Verbose,
    [switch]$Quiet
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

# Configuration
$RequiredPythonVersion = "3.11"
$RequiredNodeVersion = "18"
$RequiredDockerVersion = "20"
$RequiredDockerComposeVersion = "2.0"

# Counters
$TotalChecks = 0
$PassedChecks = 0
$FailedChecks = 0
$WarningChecks = 0

# Helper functions
function Write-Header {
    Write-Host "================================" -ForegroundColor $Blue
    Write-Host "  Helpdesk Platform Setup Check" -ForegroundColor $Blue
    Write-Host "================================" -ForegroundColor $Blue
    Write-Host ""
}

function Write-Success {
    param($Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
    $script:PassedChecks++
}

function Write-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
    $script:FailedChecks++
}

function Write-Warning {
    param($Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
    $script:WarningChecks++
}

function Write-Info {
    param($Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Blue
}

function Test-Command {
    param(
        [string]$Command,
        [string]$Name,
        [string]$RequiredVersion = $null
    )
    
    $script:TotalChecks++
    
    try {
        $commandInfo = Get-Command $Command -ErrorAction Stop
        
        if ($RequiredVersion) {
            $version = Get-Version $Command
            if (Test-Version $version $RequiredVersion) {
                Write-Success "$Name is installed (version: $version)"
            } else {
                Write-Error "$Name version $version is too old. Required: $RequiredVersion+"
            }
        } else {
            Write-Success "$Name is installed"
        }
    } catch {
        Write-Error "$Name is not installed"
    }
}

function Get-Version {
    param([string]$Command)
    
    switch ($Command) {
        "python" { 
            $version = python --version 2>&1
            return $version.Split(' ')[1]
        }
        "node" { 
            $version = node --version
            return $version.TrimStart('v')
        }
        "docker" { 
            $version = docker --version
            return $version.Split(' ')[2].TrimEnd(',')
        }
        "docker-compose" { 
            $version = docker-compose --version
            return $version.Split(' ')[2].TrimEnd(',')
        }
        default { return "unknown" }
    }
}

function Test-Version {
    param(
        [string]$Version1,
        [string]$Version2
    )
    
    $v1 = [Version]$Version1
    $v2 = [Version]$Version2
    
    return $v1 -ge $v2
}

function Test-File {
    param(
        [string]$Path,
        [string]$Name,
        [bool]$Required = $true
    )
    
    $script:TotalChecks++
    
    if (Test-Path $Path) {
        if ($Required) {
            Write-Success "$Name exists"
        } else {
            Write-Success "$Name exists (optional)"
        }
    } else {
        if ($Required) {
            Write-Error "$Name is missing"
        } else {
            Write-Warning "$Name is missing (optional)"
        }
    }
}

function Test-EnvironmentVariable {
    param(
        [string]$Variable,
        [string]$Name,
        [bool]$Required = $true
    )
    
    $script:TotalChecks++
    
    $value = [Environment]::GetEnvironmentVariable($Variable)
    
    if ($value) {
        Write-Success "$Name is set"
    } else {
        if ($Required) {
            Write-Error "$Name is not set"
        } else {
            Write-Warning "$Name is not set (optional)"
        }
    }
}

function Test-Port {
    param(
        [int]$Port,
        [string]$Service
    )
    
    $script:TotalChecks++
    
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    
    if ($connection) {
        Write-Warning "Port $Port is in use (may conflict with $Service)"
    } else {
        Write-Success "Port $Port is available"
    }
}

function Test-DockerService {
    $script:TotalChecks++
    
    try {
        docker info | Out-Null
        Write-Success "Docker service is running"
    } catch {
        Write-Error "Docker service is not running"
    }
}

function Test-DiskSpace {
    param(
        [int]$RequiredGB,
        [string]$Path = "."
    )
    
    $script:TotalChecks++
    
    $drive = (Get-Item $Path).PSDrive
    $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
    
    if ($freeSpaceGB -ge $RequiredGB) {
        Write-Success "Sufficient disk space available ($freeSpaceGB GB free)"
    } else {
        Write-Error "Insufficient disk space ($freeSpaceGB GB free, need $RequiredGB GB)"
    }
}

function Test-Memory {
    param([int]$RequiredGB)
    
    $script:TotalChecks++
    
    $totalMemoryGB = [math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB, 2)
    
    if ($totalMemoryGB -ge $RequiredGB) {
        Write-Success "Sufficient memory available ($totalMemoryGB GB total)"
    } else {
        Write-Warning "Low memory ($totalMemoryGB GB total, recommended $RequiredGB GB)"
    }
}

function Show-Help {
    Write-Host "Environment Setup Validation Script for Windows"
    Write-Host ""
    Write-Host "Usage: .\validate-setup.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help      Show this help message"
    Write-Host "  -Verbose   Enable verbose output"
    Write-Host "  -Quiet     Suppress output except errors"
    Write-Host ""
    Write-Host "This script validates your development environment for the Helpdesk Platform."
    Write-Host "It checks prerequisites, configuration, and system requirements."
}

function Write-Summary {
    Write-Host "================================" -ForegroundColor $Blue
    Write-Host "  Validation Summary" -ForegroundColor $Blue
    Write-Host "================================" -ForegroundColor $Blue
    Write-Host ""
    Write-Host "Total checks: $TotalChecks"
    Write-Host "Passed: $PassedChecks" -ForegroundColor $Green
    Write-Host "Warnings: $WarningChecks" -ForegroundColor $Yellow
    Write-Host "Failed: $FailedChecks" -ForegroundColor $Red
    Write-Host ""
    
    if ($FailedChecks -eq 0) {
        if ($WarningChecks -eq 0) {
            Write-Host "🎉 All checks passed! You're ready to start development." -ForegroundColor $Green
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor $Blue
            Write-Host "1. Review and update .env file if needed"
            Write-Host "2. Run: docker-compose up -d"
            Write-Host "3. Run: docker-compose exec web python manage.py migrate"
            Write-Host "4. Run: docker-compose exec web python manage.py createsuperuser"
            Write-Host "5. Access the application at http://localhost:8000"
        } else {
            Write-Host "⚠️  Setup completed with warnings. Review the warnings above." -ForegroundColor $Yellow
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor $Blue
            Write-Host "1. Address any warnings above"
            Write-Host "2. Run: docker-compose up -d"
        }
    } else {
        Write-Host "❌ Setup validation failed. Please fix the errors above." -ForegroundColor $Red
        Write-Host ""
        Write-Host "Common solutions:" -ForegroundColor $Blue
        Write-Host "1. Install missing prerequisites"
        Write-Host "2. Start Docker service"
        Write-Host "3. Create .env file from template"
        Write-Host "4. Check port availability"
        exit 1
    }
}

# Main validation function
function Invoke-Validation {
    Write-Header
    
    Write-Host "Checking prerequisites..." -ForegroundColor $Blue
    Write-Host ""
    
    # Check system requirements
    Test-Command "python" "Python" $RequiredPythonVersion
    Test-Command "node" "Node.js" $RequiredNodeVersion
    Test-Command "docker" "Docker" $RequiredDockerVersion
    Test-Command "docker-compose" "Docker Compose" $RequiredDockerComposeVersion
    
    Write-Host ""
    Write-Host "Checking Docker service..." -ForegroundColor $Blue
    Test-DockerService
    
    Write-Host ""
    Write-Host "Checking system resources..." -ForegroundColor $Blue
    Test-DiskSpace 5
    Test-Memory 4
    
    Write-Host ""
    Write-Host "Checking project files..." -ForegroundColor $Blue
    Test-File "docker-compose.yml" "Docker Compose configuration" $true
    Test-File "env.example" "Environment template" $true
    Test-File "README.md" "README documentation" $true
    Test-File "core/requirements/production.txt" "Python requirements" $true
    Test-File "customer-portal/package.json" "Node.js package.json" $true
    
    Write-Host ""
    Write-Host "Checking environment configuration..." -ForegroundColor $Blue
    
    # Check if .env file exists
    if (Test-Path ".env") {
        Write-Success ".env file exists"
        
        # Load environment variables from .env file
        Get-Content ".env" | ForEach-Object {
            if ($_ -match "^([^#][^=]+)=(.*)$") {
                [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
            }
        }
        
        # Check required environment variables
        Test-EnvironmentVariable "SECRET_KEY" "SECRET_KEY" $true
        Test-EnvironmentVariable "DB_PASSWORD" "DB_PASSWORD" $true
        Test-EnvironmentVariable "REDIS_URL" "REDIS_URL" $true
        
        # Check optional but recommended variables
        Test-EnvironmentVariable "OPENAI_API_KEY" "OPENAI_API_KEY" $false
        Test-EnvironmentVariable "GOOGLE_MAPS_API_KEY" "GOOGLE_MAPS_API_KEY" $false
        Test-EnvironmentVariable "TWILIO_ACCOUNT_SID" "TWILIO_ACCOUNT_SID" $false
        Test-EnvironmentVariable "SENDGRID_API_KEY" "SENDGRID_API_KEY" $false
    } else {
        Write-Error ".env file not found"
        Write-Info "Creating .env file from template..."
        if (Test-Path "env.example") {
            Copy-Item "env.example" ".env"
            Write-Success ".env file created from template"
            Write-Warning "Please edit .env file with your configuration"
        } else {
            Write-Error "env.example file not found"
        }
    }
    
    Write-Host ""
    Write-Host "Checking port availability..." -ForegroundColor $Blue
    Test-Port 8000 "Django application"
    Test-Port 3000 "React development server"
    Test-Port 5432 "PostgreSQL database"
    Test-Port 6379 "Redis cache"
    Test-Port 80 "Nginx web server"
    
    Write-Host ""
    Write-Host "Checking Docker images..." -ForegroundColor $Blue
    
    # Check if required Docker images exist
    try {
        $postgisImages = docker images | Select-String "postgis/postgis"
        if ($postgisImages) {
            Write-Success "PostGIS image available"
        } else {
            Write-Info "PostGIS image will be downloaded on first run"
        }
    } catch {
        Write-Info "PostGIS image will be downloaded on first run"
    }
    
    try {
        $redisImages = docker images | Select-String "redis"
        if ($redisImages) {
            Write-Success "Redis image available"
        } else {
            Write-Info "Redis image will be downloaded on first run"
        }
    } catch {
        Write-Info "Redis image will be downloaded on first run"
    }
    
    try {
        $nginxImages = docker images | Select-String "nginx"
        if ($nginxImages) {
            Write-Success "Nginx image available"
        } else {
            Write-Info "Nginx image will be downloaded on first run"
        }
    } catch {
        Write-Info "Nginx image will be downloaded on first run"
    }
    
    Write-Host ""
    Write-Host "Checking network configuration..." -ForegroundColor $Blue
    
    # Check if Docker network exists
    try {
        $networks = docker network ls | Select-String "desk_default"
        if ($networks) {
            Write-Success "Docker network exists"
        } else {
            Write-Info "Docker network will be created on first run"
        }
    } catch {
        Write-Info "Docker network will be created on first run"
    }
    
    Write-Host ""
    Write-Summary
}

# Show help if requested
if ($Help) {
    Show-Help
    exit 0
}

# Run validation
Invoke-Validation
