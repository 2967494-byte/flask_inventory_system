# SYNAPSE Deployment Script (PowerShell)
# This script rebuilds and restarts the necessary services

Write-Host "🚀 SYNAPSE Deployment Script" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Check if docker is available
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Function to restart a specific service
function Restart-Service {
    param($ServiceName)
    Write-Host "🔄 Restarting $ServiceName..." -ForegroundColor Yellow
    docker compose restart $ServiceName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $ServiceName restarted successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to restart $ServiceName" -ForegroundColor Red
        return $false
    }
    return $true
}

# Function to rebuild and restart a service
function Rebuild-Service {
    param($ServiceName)
    Write-Host "🔨 Rebuilding $ServiceName..." -ForegroundColor Yellow
    docker compose build $ServiceName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $ServiceName built successfully" -ForegroundColor Green
        Restart-Service $ServiceName
    } else {
        Write-Host "❌ Failed to build $ServiceName" -ForegroundColor Red
        return $false
    }
    return $true
}

# Main menu
Write-Host "Select an option:" -ForegroundColor White
Write-Host "1. Restart bot only (fixes login issue)" -ForegroundColor White
Write-Host "2. Rebuild and restart frontend (fixes design updates)" -ForegroundColor White
Write-Host "3. Rebuild and restart all services" -ForegroundColor White
Write-Host "4. View logs" -ForegroundColor White
Write-Host "5. Check service status" -ForegroundColor White
Write-Host ""

$option = Read-Host "Enter option (1-5)"

switch ($option) {
    "1" {
        Restart-Service "bot"
    }
    "2" {
        Rebuild-Service "frontend"
    }
    "3" {
        Write-Host "🔨 Rebuilding all services..." -ForegroundColor Yellow
        docker compose down
        docker compose up -d --build
        Write-Host "✅ All services rebuilt and started" -ForegroundColor Green
    }
    "4" {
        Write-Host "Select service to view logs:" -ForegroundColor White
        Write-Host "1. Backend" -ForegroundColor White
        Write-Host "2. Bot" -ForegroundColor White
        Write-Host "3. Frontend" -ForegroundColor White
        Write-Host "4. Database" -ForegroundColor White
        Write-Host "5. All" -ForegroundColor White
        $logOption = Read-Host "Enter option (1-5)"
        switch ($logOption) {
            "1" { docker compose logs -f backend }
            "2" { docker compose logs -f bot }
            "3" { docker compose logs -f frontend }
            "4" { docker compose logs -f db }
            "5" { docker compose logs -f }
        }
    }
    "5" {
        docker compose ps
    }
    default {
        Write-Host "❌ Invalid option" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "✨ Done!" -ForegroundColor Green
