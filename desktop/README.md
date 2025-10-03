# WeatherWise Desktop App

## Prerequisites

Before running the desktop app, you need to install:

### 1. Node.js and npm
Download and install from: https://nodejs.org/
- Choose the LTS version
- This will also install npm

### 2. Rust and Cargo
Download and install from: https://rustup.rs/
- Run the installer and follow the prompts
- This will install Rust, Cargo, and rustup

### 3. Tauri Prerequisites
Follow the platform-specific setup guide at: https://tauri.app/v1/guides/getting-started/prerequisites

**For Windows:**
- Microsoft Visual Studio C++ Build Tools
- WebView2 (usually pre-installed on Windows 10/11)

## Setup Instructions

1. **Install dependencies:**
```bash
cd desktop
npm install
```

2. **Install Tauri CLI:**
```bash
npm install -g @tauri-apps/cli
```

3. **Start the Python backend:**
```bash
# In the root directory
python api_server.py
```

4. **Run the desktop app in development:**
```bash
# In the desktop directory
npm run tauri:dev
```

## Building for Production

```bash
# Build the desktop app
npm run tauri:build
```

The built application will be in `src-tauri/target/release/bundle/`

## Features

- 🌤️ **Weather Risk Assessment** - Get predictions for very hot, cold, windy, wet, and uncomfortable conditions
- 🎯 **Activity-Specific Recommendations** - Tailored advice for hiking, fishing, vacation, camping, cycling, and outdoor sports  
- 📊 **Visual Risk Indicators** - Easy-to-read probability bars and risk levels
- ⚡ **Real-time Backend Integration** - Connects to Python ML backend via REST API
- 🔄 **Auto Health Monitoring** - Checks backend connection status automatically

## App Structure

```
desktop/
├── src/                    # Frontend (HTML/CSS/JS)
│   ├── index.html         # Main UI
│   ├── styles.css         # Styling
│   └── script.js          # Frontend logic
├── src-tauri/             # Rust backend
│   ├── src/main.rs        # Tauri app entry point
│   ├── Cargo.toml         # Rust dependencies
│   ├── tauri.conf.json    # App configuration
│   └── build.rs           # Build script
├── package.json           # Node.js dependencies
└── vite.config.js         # Vite configuration
```

## API Integration

The desktop app connects to the Python backend at `http://localhost:8000`:

- **POST /predict** - Get weather predictions
- **GET /health** - Check backend status

Make sure the Python backend is running before starting the desktop app.

## Troubleshooting

### Backend Connection Issues
- Ensure Python backend is running: `python api_server.py`
- Check that the backend is accessible at `http://localhost:8000/health`
- Verify firewall settings aren't blocking the connection

### Build Issues
- Make sure all prerequisites are installed
- Try clearing node_modules: `rm -rf node_modules && npm install`
- Check Rust installation: `cargo --version`

### Development Mode Issues
- Ensure Vite dev server starts on port 1420
- Check for conflicting processes on that port
- Try restarting with: `npm run tauri:dev`