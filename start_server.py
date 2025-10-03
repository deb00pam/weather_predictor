#!/usr/bin/env python3
"""
NASA Weather Risk Detection API
Startup script for the backend server
"""

import sys
import subprocess
import os
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        sys.exit(1)

def start_server():
    """Start the FastAPI server"""
    try:
        print("\n🚀 Starting NASA Weather Risk Detection API server...")
        print("Server will be available at: http://localhost:8000")
        print("API documentation: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server\n")
        
        # Start the server
        subprocess.call([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("NASA Weather Risk Detection API - Backend Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Install requirements if needed
    if not Path("venv").exists() and "--skip-install" not in sys.argv:
        install_requirements()
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()