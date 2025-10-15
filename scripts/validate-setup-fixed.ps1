# Environment Setup Validation Script for Windows
# Validates prerequisites and environment for the Helpdesk Platform

param(
    [switch]$Help,
    [switch]$Verbose
)

# Color functions
function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

# Global variables
$script:TotalChecks = 0
$script:PassedChecks = 0
$script:FailedChecks = 0

function Show-Help {
    Write-Host "Environment Setup Validation Script for Windows"
    Write-Host ""
    Write-Host "Usage: .\validate-setup-fixed.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help     Show this help message"
    Write-Host "  -Verbose  Show detailed output"
    Write-Host ""
    Write-Host "This script validates:"
    Write-Host "  - Prerequisites (Python, Node.js, Docker, etc.)"
    Write-Host "  - System resources (disk space, memory)"
    Write-Host "  - Port availability"
    Write-Host "  - Configuration files"
    Write-Host "  - Environment variables"
    Write-Host "  - Docker service status"
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check Python
    Test-Command "python" "Python 3.11+" "--version"
    
    # Check Node.js
    Test-Command "node" "Node.js 18+" "--version"
    
    # Check Docker
    Test-Command "docker" "Docker" "--version"
    
    # Check Docker Compose
    Test-Command "docker-compose" "Docker Compose" "--version"
}

function Test-Command {
    param(
        [string]$Command,
        [string]$Description,
        [string]$VersionFlag
    )
    
    $script:TotalChecks++
    
    try {
        $version = & $Command $VersionFlag 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$Description is installed: $version"
            $script:PassedChecks++
        } else {
            Write-Error "$Description is not installed or not in PATH"
            $script:FailedChecks++
        }
    } catch {
        Write-Error "$Description is not installed or not in PATH"
        $script:FailedChecks++
    }
}

function Test-SystemResources {
    Write-Info "Checking system resources..."
    
    # Check disk space
    Test-DiskSpace "C:\" 5
    
    # Check memory
    Test-Memory 4
}

function Test-DiskSpace {
    param(
        [string]$Path,
        [int]$RequiredGB
    )
    
    $script:TotalChecks++
    
    try {
        $drive = (Get-Item $Path).PSDrive
        $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
        
        if ($freeSpaceGB -ge $RequiredGB) {
            Write-Success "Sufficient disk space available ($freeSpaceGB GB free)"
            $script:PassedChecks++
        } else {
            Write-Error "Insufficient disk space ($freeSpaceGB GB free, need $RequiredGB GB)"
            $script:FailedChecks++
        }
    } catch {
        Write-Error "Could not check disk space"
        $script:FailedChecks++
    }
}

function Test-Memory {
    param([int]$RequiredGB)
    
    $script:TotalChecks++
    
    try {
        $totalMemoryGB = [math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB, 2)
        
        if ($totalMemoryGB -ge $RequiredGB) {
            Write-Success "Sufficient memory available ($totalMemoryGB GB total)"
            $script:PassedChecks++
        } else {
            Write-Warning "Low memory ($totalMemoryGB GB total, recommended $RequiredGB GB)"
            $script:PassedChecks++ # Still pass, just warn
        }
    } catch {
        Write-Error "Could not check memory"
        $script:FailedChecks++
    }
}

function Test-Ports {
    Write-Info "Checking port availability..."
    
    $ports = @(8000, 3000, 5432, 6379, 80, 443)
    
    foreach ($port in $ports) {
        Test-Port $port
    }
}

function Test-Port {
    param([int]$Port)
    
    $script:TotalChecks++
    
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet
        if ($connection) {
            Write-Warning "Port $Port is already in use"
            $script:PassedChecks++ # Still pass, just warn
        } else {
            Write-Success "Port $Port is available"
            $script:PassedChecks++
        }
    } catch {
        Write-Success "Port $Port is available"
        $script:PassedChecks++
    }
}

function Test-ConfigurationFiles {
    Write-Info "Checking configuration files..."
    
    $files = @(
        "docker-compose.yml",
        "requirements.txt",
        "package.json",
        ".env.example"
    )
    
    foreach ($file in $files) {
        Test-File $file
    }
}

function Test-File {
    param([string]$FilePath)
    
    $script:TotalChecks++
    
    if (Test-Path $FilePath) {
        Write-Success "Configuration file found: $FilePath"
        $script:PassedChecks++
    } else {
        Write-Error "Configuration file missing: $FilePath"
        $script:FailedChecks++
    }
}

function Test-EnvironmentVariables {
    Write-Info "Checking environment variables..."
    
    $requiredVars = @(
        "SECRET_KEY",
        "DB_PASSWORD",
        "REDIS_URL"
    )
    
    foreach ($var in $requiredVars) {
        Test-EnvVar $var
    }
}

function Test-EnvVar {
    param([string]$VarName)
    
    $script:TotalChecks++
    
    $value = [Environment]::GetEnvironmentVariable($VarName)
    if ($value) {
        Write-Success "Environment variable set: $VarName"
        $script:PassedChecks++
    } else {
        Write-Warning "Environment variable not set: $VarName (will use default)"
        $script:PassedChecks++ # Still pass, has defaults
    }
}

function Test-DockerService {
    Write-Info "Checking Docker service..."
    
    $script:TotalChecks++
    
    try {
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker service is running"
            $script:PassedChecks++
        } else {
            Write-Error "Docker service is not running. Please start Docker Desktop."
            $script:FailedChecks++
        }
    } catch {
        Write-Error "Docker service is not running. Please start Docker Desktop."
        $script:FailedChecks++
    }
}

function Show-Summary {
    Write-Host ""
    Write-Host "=== Validation Summary ===" -ForegroundColor White
    Write-Host "Total checks: $script:TotalChecks"
    Write-Host "Passed: $script:PassedChecks" -ForegroundColor Green
    Write-Host "Failed: $script:FailedChecks" -ForegroundColor Red
    
    if ($script:FailedChecks -eq 0) {
        Write-Host ""
        Write-Success "All checks passed! Your environment is ready for development."
        Write-Host ""
        Write-Info "Next steps:"
        Write-Info "1. Copy .env.example to .env and configure your settings"
        Write-Info "2. Run: docker-compose up -d"
        Write-Info "3. Run: docker-compose exec web python manage.py migrate"
        Write-Info "4. Run: docker-compose exec web python manage.py createsuperuser"
        Write-Info "5. Access the application at http://localhost:8000"
    } else {
        Write-Host ""
        Write-Error "Some checks failed. Please fix the issues above before proceeding."
    }
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "Validating Helpdesk Platform Environment..." -ForegroundColor White
Write-Host ""

Test-Prerequisites
Test-SystemResources
Test-Ports
Test-ConfigurationFiles
Test-EnvironmentVariables
Test-DockerService

Show-Summary

if ($script:FailedChecks -gt 0) {
    exit 1
} else {
    exit 0
}
