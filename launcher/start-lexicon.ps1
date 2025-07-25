# LEXICON Silent Launcher
# Runs in background and manages the application

$ErrorActionPreference = "SilentlyContinue"

# Set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

# Create mutex to prevent multiple instances
$mutex = New-Object System.Threading.Mutex($false, "LEXICON_MUTEX")
if (-not $mutex.WaitOne(0)) {
    [System.Windows.Forms.MessageBox]::Show(
        "LEXICON is already running. Check your system tray.",
        "LEXICON",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Information
    )
    exit
}

# Function to show balloon notification
function Show-Notification {
    param($Title, $Text, $Icon = "Info")
    
    Add-Type -AssemblyName System.Windows.Forms
    $notification = New-Object System.Windows.Forms.NotifyIcon
    $notification.Icon = [System.Drawing.SystemIcons]::Information
    $notification.BalloonTipTitle = $Title
    $notification.BalloonTipText = $Text
    $notification.BalloonTipIcon = $Icon
    $notification.Visible = $true
    $notification.ShowBalloonTip(3000)
    Start-Sleep -Milliseconds 3000
    $notification.Dispose()
}

# Check Docker
$dockerRunning = $false
try {
    docker info | Out-Null
    $dockerRunning = $true
} catch {
    # Try to start Docker Desktop
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Show-Notification "LEXICON" "Starting Docker Desktop..."
        Start-Process $dockerPath -WindowStyle Hidden
        
        # Wait for Docker
        $attempts = 0
        while (-not $dockerRunning -and $attempts -lt 60) {
            Start-Sleep -Seconds 2
            try {
                docker info | Out-Null
                $dockerRunning = $true
            } catch {
                $attempts++
            }
        }
    }
}

if (-not $dockerRunning) {
    [System.Windows.Forms.MessageBox]::Show(
        "Docker Desktop is required but not running. Please start Docker Desktop manually.",
        "LEXICON Error",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    $mutex.ReleaseMutex()
    exit
}

# Start LEXICON services
Show-Notification "LEXICON" "Starting LEXICON services..."

# Run deployment in background
$deployJob = Start-Job -ScriptBlock {
    Set-Location $using:projectRoot
    & docker-compose -f docker-compose-local.yml up -d
} 

# Wait for services with timeout
$timeout = 120
$elapsed = 0
while ($deployJob.State -eq "Running" -and $elapsed -lt $timeout) {
    Start-Sleep -Seconds 1
    $elapsed++
}

if ($deployJob.State -ne "Completed") {
    Stop-Job $deployJob
    Remove-Job $deployJob
    
    [System.Windows.Forms.MessageBox]::Show(
        "Failed to start LEXICON services. Please check the logs.",
        "LEXICON Error",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    $mutex.ReleaseMutex()
    exit
}

# Check if services are healthy
Start-Sleep -Seconds 5
$healthy = $true
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -ne 200) {
        $healthy = $false
    }
} catch {
    $healthy = $false
}

if ($healthy) {
    # Success - open browser
    Show-Notification "LEXICON Ready" "Click here to open LEXICON" "Info"
    Start-Process "http://localhost"
    
    # Create system tray icon
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    
    # Create context menu
    $contextMenu = New-Object System.Windows.Forms.ContextMenuStrip
    
    $openItem = New-Object System.Windows.Forms.ToolStripMenuItem
    $openItem.Text = "Open LEXICON"
    $openItem.Add_Click({
        Start-Process "http://localhost"
    })
    $contextMenu.Items.Add($openItem)
    
    $contextMenu.Items.Add("-")
    
    $docsItem = New-Object System.Windows.Forms.ToolStripMenuItem
    $docsItem.Text = "Open Documents Folder"
    $docsItem.Add_Click({
        Start-Process "$env:USERPROFILE\Documents\LEXICON"
    })
    $contextMenu.Items.Add($docsItem)
    
    $contextMenu.Items.Add("-")
    
    $backupItem = New-Object System.Windows.Forms.ToolStripMenuItem
    $backupItem.Text = "Backup Now"
    $backupItem.Add_Click({
        docker exec lexicon-backup-local /scripts/backup.sh
        Show-Notification "LEXICON Backup" "Backup completed successfully"
    })
    $contextMenu.Items.Add($backupItem)
    
    $contextMenu.Items.Add("-")
    
    $exitItem = New-Object System.Windows.Forms.ToolStripMenuItem
    $exitItem.Text = "Exit"
    $exitItem.Add_Click({
        $result = [System.Windows.Forms.MessageBox]::Show(
            "Stop LEXICON services?",
            "Exit LEXICON",
            [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Question
        )
        
        if ($result -eq "Yes") {
            docker-compose -f docker-compose-local.yml down
            $notifyIcon.Visible = $false
            $notifyIcon.Dispose()
            $mutex.ReleaseMutex()
            [System.Windows.Forms.Application]::Exit()
        }
    })
    $contextMenu.Items.Add($exitItem)
    
    # Create tray icon
    $notifyIcon = New-Object System.Windows.Forms.NotifyIcon
    $iconPath = Join-Path $projectRoot "launcher\assets\icon.ico"
    if (Test-Path $iconPath) {
        $notifyIcon.Icon = New-Object System.Drawing.Icon($iconPath)
    } else {
        $notifyIcon.Icon = [System.Drawing.SystemIcons]::Application
    }
    $notifyIcon.Text = "LEXICON Legal AI System"
    $notifyIcon.ContextMenuStrip = $contextMenu
    $notifyIcon.Visible = $true
    
    # Handle double-click
    $notifyIcon.Add_DoubleClick({
        Start-Process "http://localhost"
    })
    
    # Keep running
    [System.Windows.Forms.Application]::Run()
    
} else {
    [System.Windows.Forms.MessageBox]::Show(
        "LEXICON services started but web interface is not responding. Please check the logs.",
        "LEXICON Warning",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Warning
    )
}

$mutex.ReleaseMutex()