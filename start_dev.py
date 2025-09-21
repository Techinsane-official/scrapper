#!/usr/bin/env python3
"""
Development startup script for Premium Scraper.
Starts both backend and frontend servers.
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FastAPI backend server...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])
    return backend_process

def start_frontend():
    """Start the Next.js frontend server."""
    print("🎨 Starting Next.js frontend server...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found. Please run this script from the project root.")
        return None
    
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd=frontend_dir)
    return frontend_process

def main():
    """Main function to start both servers."""
    print("🌟 Premium Scraper Development Environment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src").exists() or not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if frontend exists
    if not Path("frontend").exists():
        print("❌ Frontend directory not found. Please set up the frontend first.")
        sys.exit(1)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("⚠️  .env file not found. Please copy .env.example to .env and configure it.")
        print("   cp .env.example .env")
        sys.exit(1)
    
    processes = []
    
    try:
        # Start backend
        backend_process = start_backend()
        processes.append(backend_process)
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        print("\n✅ Both servers are starting up!")
        print("📊 Backend API: http://localhost:8000")
        print("📊 API Docs: http://localhost:8000/docs")
        print("🎨 Frontend: http://localhost:3000")
        print("\nPress Ctrl+C to stop both servers...")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for process in processes:
                if process.poll() is not None:
                    print(f"❌ Process {process.pid} has stopped unexpectedly")
                    return
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        for process in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print("✅ Servers stopped successfully!")

if __name__ == "__main__":
    main()
