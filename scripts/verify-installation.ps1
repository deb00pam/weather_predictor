# WeatherWise Desktop App - Verification Script
# This script checks if all prerequisites are properly installed

Write-Host "🔍 WeatherWise Desktop App - Verification Script" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Function to test version
function Test-Version($command, $name) {
    Write-Host "Checking $name..." -ForegroundColor Yellow
    if (Test-Command $command) {
        try {
            $version = & $command --version 2>$null
            Write-Host "✅ $name is installed: $version" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "❌ $name command exists but version check failed" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ $name is not installed or not in PATH" -ForegroundColor Red
        return $false
    }
}

$allGood = $true

# Check Node.js
if (-NOT (Test-Version "node" "Node.js")) {
    $allGood = $false
}

# Check npm
if (-NOT (Test-Version "npm" "npm")) {
    $allGood = $false
}

# Check Rust
if (-NOT (Test-Version "cargo" "Rust/Cargo")) {
    $allGood = $false
}

# Check if we're in the right directory
Write-Host ""
Write-Host "Checking project structure..." -ForegroundColor Yellow
if (Test-Path "desktop\package.json") {
    Write-Host "✅ Desktop app structure found" -ForegroundColor Green
} else {
    Write-Host "❌ Desktop app structure not found" -ForegroundColor Red
    Write-Host "   Make sure you are in the weather_predictor root directory" -ForegroundColor Yellow
    $allGood = $false
}

if (Test-Path "api_server.py") {
    Write-Host "✅ Python backend found" -ForegroundColor Green
} else {
    Write-Host "❌ Python backend not found" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""
if ($allGood) {
    Write-Host "🎉 All prerequisites are installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Ready to proceed:" -ForegroundColor Cyan
    Write-Host "1. cd desktop" -ForegroundColor White
    Write-Host "2. npm install" -ForegroundColor White
    Write-Host "3. npm run tauri:dev" -ForegroundColor White
} else {
    Write-Host "⚠️  Some prerequisites are missing!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Please install missing components:" -ForegroundColor Cyan
    Write-Host "- Node.js: https://nodejs.org/" -ForegroundColor White
    Write-Host "- Rust: https://rustup.rs/" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run the installation script: .\scripts\install-prerequisites.ps1" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"