# WeatherWise Desktop App - Installation Guide

## 🚀 Automated Installation (Recommended)

I've created an automated installation script for you! Here's how to use it:

### Step 1: Run the Installation Script

1. **Right-click on PowerShell** and select **"Run as Administrator"**
2. **Navigate to your project directory:**
   ```powershell
   cd C:\Users\deb0p\weather_predictor
   ```
3. **Run the installation script:**
   ```powershell
   .\scripts\install-prerequisites.ps1
   ```

The script will automatically:
- ✅ Install Node.js (Latest LTS version)
- ✅ Install Rust toolchain with Cargo
- ✅ Set up environment variables
- ✅ Verify installations

### Step 2: Verify Installation

After the script completes, run the verification script:
```powershell
.\scripts\verify-installation.ps1
```

### Step 3: Start Development

If verification passes:
```powershell
cd desktop
npm install
npm run tauri:dev
```

---

## 📋 Manual Installation (If Automated Fails)

If the automated script doesn't work, follow these manual steps:

### 1. Install Node.js

**Option A: Download from Official Site**
1. Go to https://nodejs.org/
2. Download the **LTS version** (recommended)
3. Run the installer with default settings
4. Restart your terminal

**Option B: Use Windows Package Manager**
```powershell
winget install OpenJS.NodeJS
```

**Verify Installation:**
```powershell
node --version
npm --version
```

### 2. Install Rust

**Option A: Download from Official Site**
1. Go to https://rustup.rs/
2. Download and run `rustup-init.exe`
3. Follow the installation prompts (accept defaults)
4. Restart your terminal

**Option B: Use Windows Package Manager**
```powershell
winget install Rustlang.Rustup
```

**Verify Installation:**
```powershell
cargo --version
rustc --version
```

### 3. Install Visual Studio Build Tools (Windows)

Tauri requires Visual Studio Build Tools for compilation:

1. Go to https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Download "Build Tools for Visual Studio"
3. Install with the "C++ build tools" workload

---

## 🔧 Troubleshooting

### Common Issues:

**"Command not found" after installation:**
- Close and reopen PowerShell/Command Prompt
- Check if the programs are in your PATH environment variable

**Permission issues:**
- Make sure you're running PowerShell as Administrator
- Check Windows execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Build errors:**
- Ensure Visual Studio Build Tools are installed
- Try running: `rustup update`

**Network issues during installation:**
- Check your internet connection
- Try using a VPN if corporate firewall blocks downloads

### Alternative Package Managers:

**Chocolatey (if you prefer):**
```powershell
# Install Chocolatey first
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Then install packages
choco install nodejs rust
```

**Scoop (lightweight option):**
```powershell
# Install Scoop
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Install packages
scoop install nodejs rust
```

---

## ✅ Final Steps

Once everything is installed:

1. **Verify everything works:**
   ```powershell
   .\scripts\verify-installation.ps1
   ```

2. **Install desktop app dependencies:**
   ```powershell
   cd desktop
   npm install
   ```

3. **Start the Python backend:**
   ```powershell
   python api_server.py
   ```

4. **Launch the desktop app:**
   ```powershell
   npm run tauri:dev
   ```

---

## 🆘 Need Help?

If you encounter any issues:

1. **Run the verification script** to see what's missing
2. **Check the error messages** carefully
3. **Try the manual installation** steps
4. **Restart your computer** after installing everything
5. **Make sure you're running as Administrator** when needed

The installation scripts are designed to handle most common scenarios automatically! 🎉