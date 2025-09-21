#!/usr/bin/env python3
"""
Test script to verify deployment readiness.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and print status."""
    if Path(dir_path).exists() and Path(dir_path).is_dir():
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} - MISSING")
        return False

def main():
    """Main test function."""
    print("🚀 Premium Scraper Deployment Readiness Test")
    print("=" * 50)
    
    all_good = True
    
    # Check backend files
    print("\n📦 Backend Configuration:")
    backend_files = [
        ("railway.json", "Railway configuration"),
        ("Procfile", "Railway Procfile"),
        ("runtime.txt", "Python runtime version"),
        ("requirements-prod.txt", "Production requirements"),
        ("src/api/main.py", "FastAPI main application"),
        ("src/config/supabase.py", "Supabase configuration"),
        ("src/database/models.py", "Database models"),
        ("src/database/service.py", "Database service"),
    ]
    
    for file_path, description in backend_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check frontend files
    print("\n🎨 Frontend Configuration:")
    frontend_files = [
        ("frontend/vercel.json", "Vercel configuration"),
        ("frontend/.vercelignore", "Vercel ignore file"),
        ("frontend/next.config.js", "Next.js configuration"),
        ("frontend/package.json", "Package configuration"),
        ("frontend/app/layout.tsx", "Root layout"),
        ("frontend/lib/api.ts", "API client"),
        ("frontend/components/providers.tsx", "React providers"),
    ]
    
    for file_path, description in frontend_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check deployment files
    print("\n🚀 Deployment Files:")
    deployment_files = [
        ("DEPLOYMENT_GUIDE.md", "Deployment guide"),
        ("SETUP_GUIDE.md", "Setup guide"),
        ("deploy.bat", "Windows deployment script"),
        ("deploy.sh", "Linux/Mac deployment script"),
        (".env.production", "Production environment template"),
        ("frontend/.env.production", "Frontend production environment"),
    ]
    
    for file_path, description in deployment_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check directories
    print("\n📁 Directory Structure:")
    directories = [
        ("src", "Backend source code"),
        ("frontend", "Frontend source code"),
        ("src/api", "API routes"),
        ("src/config", "Configuration"),
        ("src/database", "Database layer"),
        ("src/scraper", "Scraping modules"),
        ("frontend/app", "Next.js app directory"),
        ("frontend/components", "React components"),
        ("frontend/lib", "Utility libraries"),
    ]
    
    for dir_path, description in directories:
        if not check_directory_exists(dir_path, description):
            all_good = False
    
    # Check environment files
    print("\n🔧 Environment Configuration:")
    env_files = [
        (".env.example", "Backend environment example"),
        ("frontend/.env.example", "Frontend environment example"),
    ]
    
    for file_path, description in env_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All deployment files are ready!")
        print("\n📋 Next Steps:")
        print("1. Set up Supabase project and run SQL schema")
        print("2. Configure environment variables")
        print("3. Push code to GitHub")
        print("4. Deploy frontend to Vercel")
        print("5. Deploy backend to Railway")
        print("6. Connect frontend to backend")
        print("\n📚 See DEPLOYMENT_GUIDE.md for detailed instructions")
    else:
        print("❌ Some files are missing. Please check the errors above.")
        print("Make sure you're running this script from the project root directory.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
