# WeatherWise Desktop App - Automated Installation Script
# This script will install Node.js and Rust for you

Write-Host "🌤️ WeatherWise Desktop App - Installation Script" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-NOT (Test-Admin)) {
    Write-Host "⚠️  This script needs to be run as Administrator to install software." -ForegroundColor Yellow
    Write-Host "   Please right-click on PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green
Write-Host ""

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Install winget if not available
if (-NOT (Test-Command "winget")) {
    Write-Host "📦 Installing Windows Package Manager (winget)..." -ForegroundColor Yellow
    try {
        # Download and install App Installer which includes winget
        $appInstallerUrl = "https://aka.ms/getwinget"
        $tempFile = "$env:TEMP\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
        Invoke-WebRequest -Uri $appInstallerUrl -OutFile $tempFile
        Add-AppxPackage -Path $tempFile
        Write-Host "✅ winget installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install winget automatically" -ForegroundColor Red
        Write-Host "   Please install manually from: https://aka.ms/getwinget" -ForegroundColor Yellow
        Read-Host "Press Enter to continue with manual installation"
    }
}

# Install Node.js
Write-Host "📦 Installing Node.js..." -ForegroundColor Yellow
if (Test-Command "node") {
    $nodeVersion = node --version
    Write-Host "✅ Node.js is already installed: $nodeVersion" -ForegroundColor Green
} else {
    try {
        if (Test-Command "winget") {
            winget install OpenJS.NodeJS --accept-package-agreements --accept-source-agreements
        } else {
            Write-Host "   Downloading Node.js installer..." -ForegroundColor Yellow
            $nodeUrl = "https://nodejs.org/dist/v20.8.0/node-v20.8.0-x64.msi"
            $nodeInstaller = "$env:TEMP\node-installer.msi"
            Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller
            Write-Host "   Running Node.js installer..." -ForegroundColor Yellow
            Start-Process msiexec.exe -Wait -ArgumentList "/I $nodeInstaller /quiet"
        }
        Write-Host "✅ Node.js installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install Node.js automatically" -ForegroundColor Red
        Write-Host "   Please download and install manually from: https://nodejs.org/" -ForegroundColor Yellow
    }
}

# Install Rust
Write-Host "🦀 Installing Rust..." -ForegroundColor Yellow
if (Test-Command "cargo") {
    $rustVersion = cargo --version
    Write-Host "✅ Rust is already installed: $rustVersion" -ForegroundColor Green
} else {
    try {
        if (Test-Command "winget") {
            winget install Rustlang.Rustup --accept-package-agreements --accept-source-agreements
        } else {
            Write-Host "   Downloading Rust installer..." -ForegroundColor Yellow
            $rustUrl = "https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe"
            $rustInstaller = "$env:TEMP\rustup-init.exe"
            Invoke-WebRequest -Uri $rustUrl -OutFile $rustInstaller
            Write-Host "   Running Rust installer..." -ForegroundColor Yellow
            Start-Process $rustInstaller -Wait -ArgumentList "-y"
        }
        Write-Host "✅ Rust installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install Rust automatically" -ForegroundColor Red
        Write-Host "   Please download and install manually from: https://rustup.rs/" -ForegroundColor Yellow
    }
}

# Refresh environment variables
Write-Host "🔄 Refreshing environment variables..." -ForegroundColor Yellow
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host ""
Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Close and reopen PowerShell/Command Prompt" -ForegroundColor White
Write-Host "2. Navigate to the desktop directory: cd desktop" -ForegroundColor White
Write-Host "3. Install npm dependencies: npm install" -ForegroundColor White
Write-Host "4. Start the Python backend: python api_server.py" -ForegroundColor White
Write-Host "5. Run the desktop app: npm run tauri:dev" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"