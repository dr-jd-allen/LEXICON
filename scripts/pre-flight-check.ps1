# LEXICON Pre-Flight Check
# Validates system requirements before first run

Write-Host "LEXICON Pre-Flight Check" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()
$projectRoot = $PSScriptRoot

# 1. Check Windows Version
Write-Host "Checking Windows version..." -NoNewline
$winVer = [System.Environment]::OSVersion.Version
if ($winVer.Major -ge 10) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    $errors += "Windows 10 or later required"
}

# 2. Check RAM
Write-Host "Checking system memory..." -NoNewline
$ram = (Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property capacity -Sum).sum /1gb
if ($ram -ge 16) {
    Write-Host " OK ($([math]::Round($ram))GB)" -ForegroundColor Green
} elseif ($ram -ge 8) {
    Write-Host " WARNING ($([math]::Round($ram))GB)" -ForegroundColor Yellow
    $warnings += "16GB RAM recommended, you have $([math]::Round($ram))GB"
} else {
    Write-Host " FAIL ($([math]::Round($ram))GB)" -ForegroundColor Red
    $errors += "Minimum 8GB RAM required"
}

# 3. Check Disk Space
Write-Host "Checking disk space..." -NoNewline
$drive = (Get-Item $projectRoot).PSDrive.Name
$disk = Get-PSDrive $drive
$freeGB = [math]::Round($disk.Free / 1GB, 2)
if ($freeGB -ge 50) {
    Write-Host " OK (${freeGB}GB free)" -ForegroundColor Green
} elseif ($freeGB -ge 20) {
    Write-Host " WARNING (${freeGB}GB free)" -ForegroundColor Yellow
    $warnings += "50GB free space recommended"
} else {
    Write-Host " FAIL (${freeGB}GB free)" -ForegroundColor Red
    $errors += "Minimum 20GB free space required"
}

# 4. Check Docker Desktop
Write-Host "Checking Docker Desktop..." -NoNewline
$dockerInstalled = Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if ($dockerInstalled) {
    try {
        docker version | Out-Null
        Write-Host " OK (Running)" -ForegroundColor Green
    } catch {
        Write-Host " OK (Installed, not running)" -ForegroundColor Yellow
        $warnings += "Docker Desktop installed but not running"
    }
} else {
    Write-Host " FAIL" -ForegroundColor Red
    $errors += "Docker Desktop not installed"
}

# 5. Check .env file
Write-Host "Checking environment configuration..." -NoNewline
$envPath = Join-Path $projectRoot ".env"
$envExamplePath = Join-Path $projectRoot ".env.example"

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath -Raw
    $requiredKeys = @(
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "SERPAPI_API_KEY"
    )
    
    $missingKeys = @()
    foreach ($key in $requiredKeys) {
        if ($envContent -notmatch "$key=.+") {
            $missingKeys += $key
        }
    }
    
    if ($missingKeys.Count -eq 0) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " WARNING" -ForegroundColor Yellow
        $warnings += "Missing API keys: $($missingKeys -join ', ')"
    }
} else {
    if (Test-Path $envExamplePath) {
        Write-Host " WARNING" -ForegroundColor Yellow
        $warnings += ".env file not found (copy from .env.example)"
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        $errors += ".env file not found"
    }
}

# 6. Check network connectivity
Write-Host "Checking network connectivity..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "https://api.anthropic.com" -Method Head -TimeoutSec 5 -UseBasicParsing
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " WARNING" -ForegroundColor Yellow
    $warnings += "Cannot reach external APIs (check firewall/proxy)"
}

# 7. Check required folders
Write-Host "Checking folder structure..." -NoNewline
$requiredFolders = @(
    "backend",
    "frontend",
    "docker",
    "launcher"
)

$missingFolders = @()
foreach ($folder in $requiredFolders) {
    if (-not (Test-Path (Join-Path $projectRoot $folder))) {
        $missingFolders += $folder
    }
}

if ($missingFolders.Count -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " FAIL" -ForegroundColor Red
    $errors += "Missing folders: $($missingFolders -join ', ')"
}

# 8. Check port availability
Write-Host "Checking port availability..." -NoNewline
$ports = @(80, 5000, 3000, 6379, 8000)
$blockedPorts = @()

foreach ($port in $ports) {
    $connection = New-Object System.Net.Sockets.TcpClient
    try {
        $connection.Connect("localhost", $port)
        $blockedPorts += $port
        $connection.Close()
    } catch {
        # Port is free
    }
}

if ($blockedPorts.Count -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " WARNING" -ForegroundColor Yellow
    $warnings += "Ports in use: $($blockedPorts -join ', ')"
}

# Summary
Write-Host ""
Write-Host "Pre-Flight Check Summary" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    Write-Host "✓ All critical checks passed" -ForegroundColor Green
} else {
    Write-Host "✗ Critical errors found:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠ Warnings:" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
}

Write-Host ""

# Create setup helper if .env missing
if (-not (Test-Path $envPath) -and (Test-Path $envExamplePath)) {
    Write-Host "Would you like to create your .env file now? (Y/N): " -NoNewline
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Copy-Item $envExamplePath $envPath
        Write-Host ".env file created. Please edit it with your API keys." -ForegroundColor Green
        Start-Process notepad $envPath
    }
}

# 9. Performance baseline check
Write-Host ""
Write-Host "Running performance baseline check..." -ForegroundColor Cyan
Write-Host ""

# Test CPU performance
Write-Host "CPU Performance:" -NoNewline
$cpuTest = Measure-Command {
    $sum = 0
    for ($i = 0; $i -lt 1000000; $i++) {
        $sum += [math]::Sqrt($i)
    }
}
$cpuScore = 1000 / $cpuTest.TotalMilliseconds
if ($cpuScore -gt 0.5) {
    Write-Host " OK (Score: $([math]::Round($cpuScore, 2)))" -ForegroundColor Green
} else {
    Write-Host " SLOW (Score: $([math]::Round($cpuScore, 2)))" -ForegroundColor Yellow
    $warnings += "CPU performance below optimal"
}

# Test disk I/O
Write-Host "Disk I/O Performance:" -NoNewline
$tempFile = Join-Path $env:TEMP "lexicon_io_test.tmp"
$ioTest = Measure-Command {
    $data = "A" * 1048576  # 1MB string
    for ($i = 0; $i -lt 10; $i++) {
        $data | Out-File $tempFile -Force
        Get-Content $tempFile | Out-Null
    }
}
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
$ioScore = 10 / $ioTest.TotalSeconds
if ($ioScore -gt 5) {
    Write-Host " OK ($([math]::Round($ioScore, 1)) MB/s)" -ForegroundColor Green
} else {
    Write-Host " SLOW ($([math]::Round($ioScore, 1)) MB/s)" -ForegroundColor Yellow
    $warnings += "Disk I/O performance below optimal"
}

# Estimate processing times
Write-Host ""
Write-Host "Estimated processing times:" -ForegroundColor Cyan
Write-Host "  Small case (10 docs): ~2-3 minutes" -ForegroundColor Gray
Write-Host "  Medium case (50 docs): ~10-15 minutes" -ForegroundColor Gray
Write-Host "  Large case (200 docs): ~30-45 minutes" -ForegroundColor Gray

# Return status
if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Please fix critical errors before running LEXICON." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
} else {
    Write-Host ""
    Write-Host "System ready for LEXICON!" -ForegroundColor Green
    if ($warnings.Count -eq 0) {
        Write-Host "You can now run LEXICON.bat" -ForegroundColor Green
    } else {
        Write-Host "You can run LEXICON.bat, but review warnings above." -ForegroundColor Yellow
    }
    
    # Ask about running performance diagnostics
    Write-Host ""
    Write-Host "Would you like to run detailed performance diagnostics? (Y/N): " -NoNewline
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Starting performance diagnostics..." -ForegroundColor Cyan
        python (Join-Path $projectRoot "backend\performance_monitor.py")
    }
    
    Read-Host "Press Enter to continue"
    exit 0
}