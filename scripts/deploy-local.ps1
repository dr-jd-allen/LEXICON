# LEXICON Local Deployment Script for PowerShell
# Advanced deployment with health checks and monitoring

param(
    [switch]$SkipBuild,
    [switch]$GenerateSSL,
    [switch]$EnableMonitoring,
    [string]$BackupPath = ".\backups"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LEXICON Local Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command "docker")) {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

if (-not $SkipBuild) {
    if (-not (Test-Command "npm")) {
        Write-Host "ERROR: Node.js/npm is not installed" -ForegroundColor Red
        exit 1
    }
}

# Create directory structure
Write-Host "Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    "local-storage\chromadb",
    "local-storage\redis",
    "local-storage\uploads",
    "local-storage\generated-briefs",
    "local-storage\anonymized",
    "local-storage\case-summaries",
    "local-storage\strategic-recommendations",
    "backups\chromadb",
    "backups\daily",
    "backups\weekly",
    "backups\monthly",
    "logs\nginx",
    "logs\webapp",
    "logs\agents",
    "ssl",
    "monitoring\grafana",
    "monitoring\prometheus"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# Check/Create .env file
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env template..." -ForegroundColor Yellow
    
    $envTemplate = @"
# LEXICON Environment Variables
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# API Keys
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key
SERPAPI_API_KEY=your-serpapi-api-key
COURTLISTENER_API_KEY=your-courtlistener-api-key
COURTWHISPERER_API_KEY=your-courtwhisperer-api-key
FIRECRAWL_API_KEY=your-firecrawl-api-key
PUBMED_API_KEY=your-pubmed-api-key

# Security
SECRET_KEY=$(New-Guid)
CHROMA_AUTH_TOKEN=lexicon-$(Get-Random -Maximum 999999)-secure
REDIS_PASSWORD=redis-$(Get-Random -Maximum 999999)-secure

# Configuration
MAX_UPLOAD_SIZE=104857600
CORS_ORIGINS=http://localhost,https://localhost,http://localhost:3000
LOG_LEVEL=INFO

# Backup Settings
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"
"@
    
    $envTemplate | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "WARNING: .env file created. Please edit it with your API keys!" -ForegroundColor Red
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Build frontend
if (-not $SkipBuild) {
    Write-Host "`nBuilding frontend application..." -ForegroundColor Yellow
    
    Push-Location frontend
    try {
        npm install
        npm run build
        
        if (-not (Test-Path "build\index.html")) {
            throw "Frontend build failed - index.html not found"
        }
    } finally {
        Pop-Location
    }
} else {
    Write-Host "Skipping frontend build (--SkipBuild flag set)" -ForegroundColor Gray
}

# Generate SSL certificates
if ($GenerateSSL) {
    Write-Host "`nGenerating self-signed SSL certificates..." -ForegroundColor Yellow
    
    if (Test-Command "openssl") {
        $subject = "/C=US/ST=State/L=City/O=LEXICON/CN=localhost"
        & openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
            -keyout ssl\lexicon.key -out ssl\lexicon.crt `
            -subj $subject 2>$null
        
        Write-Host "SSL certificates generated successfully" -ForegroundColor Green
    } else {
        Write-Host "OpenSSL not found - skipping SSL generation" -ForegroundColor Yellow
    }
}

# Stop existing containers
Write-Host "`nStopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose-local.yml down 2>$null

# Build and start services
Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
docker-compose -f docker-compose-local.yml build

Write-Host "`nStarting LEXICON services..." -ForegroundColor Yellow
docker-compose -f docker-compose-local.yml up -d

# Wait for services
Write-Host "`nWaiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Health checks
Write-Host "`nPerforming health checks..." -ForegroundColor Yellow

$services = @{
    "Web Interface" = "http://localhost/health"
    "API Gateway" = "http://localhost:8000/health"
    "ChromaDB" = "http://localhost:8100/api/v1"
    "File Server" = "http://localhost:8080"
}

$healthStatus = @{}
foreach ($service in $services.GetEnumerator()) {
    try {
        $response = Invoke-WebRequest -Uri $service.Value -Method GET -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $($service.Key): Online" -ForegroundColor Green
            $healthStatus[$service.Key] = "Online"
        } else {
            Write-Host "✗ $($service.Key): Error (Status: $($response.StatusCode))" -ForegroundColor Red
            $healthStatus[$service.Key] = "Error"
        }
    } catch {
        Write-Host "✗ $($service.Key): Offline" -ForegroundColor Red
        $healthStatus[$service.Key] = "Offline"
    }
}

# Set up automated backups
Write-Host "`nConfiguring automated backups..." -ForegroundColor Yellow
docker exec lexicon-backup-local sh -c "echo '0 2 * * * /scripts/backup.sh' | crontab -"

# Enable monitoring (optional)
if ($EnableMonitoring) {
    Write-Host "`nSetting up monitoring stack..." -ForegroundColor Yellow
    # Add Prometheus and Grafana configuration here
    Write-Host "Monitoring setup not yet implemented" -ForegroundColor Gray
}

# Create desktop shortcuts
Write-Host "`nCreating desktop shortcuts..." -ForegroundColor Yellow

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcut = @"
[InternetShortcut]
URL=http://localhost
IconIndex=0
IconFile=%SystemRoot%\system32\SHELL32.dll
"@
$shortcut | Out-File -FilePath "$desktop\LEXICON.url" -Encoding ASCII

# Display summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "LEXICON Local Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  Web Interface:    http://localhost" -ForegroundColor White
Write-Host "  API Gateway:      http://localhost:8000" -ForegroundColor White
Write-Host "  ChromaDB:         http://localhost:8100" -ForegroundColor White
Write-Host "  File Server:      http://localhost:8080/files" -ForegroundColor White
Write-Host ""
Write-Host "Storage Locations:" -ForegroundColor Yellow
Write-Host "  Uploads:          $PWD\local-storage\uploads" -ForegroundColor White
Write-Host "  Generated Briefs: $PWD\local-storage\generated-briefs" -ForegroundColor White
Write-Host "  Backups:          $PWD\backups" -ForegroundColor White
Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "lexicon"
Write-Host ""
Write-Host "Management Commands:" -ForegroundColor Yellow
Write-Host "  View logs:        docker-compose -f docker-compose-local.yml logs -f" -ForegroundColor Gray
Write-Host "  Stop services:    docker-compose -f docker-compose-local.yml down" -ForegroundColor Gray
Write-Host "  Backup now:       docker exec lexicon-backup-local /scripts/backup.sh" -ForegroundColor Gray
Write-Host "  Restore backup:   docker exec lexicon-backup-local /scripts/restore.sh [file]" -ForegroundColor Gray
Write-Host ""

# Save deployment info
$deploymentInfo = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Services = $healthStatus
    Version = "1.0.0-alpha"
    Storage = @{
        Uploads = (Get-ChildItem "local-storage\uploads" -ErrorAction SilentlyContinue).Count
        Briefs = (Get-ChildItem "local-storage\generated-briefs" -ErrorAction SilentlyContinue).Count
    }
}

$deploymentInfo | ConvertTo-Json | Out-File -FilePath "logs\deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"

Write-Host "Deployment completed successfully!" -ForegroundColor Green