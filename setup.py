#!/usr/bin/env python
"""
Production Setup Script for RGPV Flask Application
Helps with initial setup and deployment verification
"""

import os
import sys
import json
import secrets
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False

def check_virtual_environment():
    """Check if running in virtual environment"""
    print_header("Checking Virtual Environment")
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print_success(f"Virtual environment active: {sys.prefix}")
        return True
    else:
        print_warning("Not running in virtual environment")
        print("  Create one with: python -m venv venv")
        return False

def install_requirements():
    """Install requirements from requirements.txt"""
    print_header("Installing Requirements")
    if not os.path.exists("requirements.txt"):
        print_error("requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print_success("Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install requirements")
        return False

def setup_env_file():
    """Setup .env file"""
    print_header("Setting Up Environment File")
    
    if os.path.exists(".env"):
        print_warning(".env already exists, skipping")
        return True
    
    if not os.path.exists(".env.example"):
        print_error(".env.example not found")
        return False
    
    # Read .env.example
    with open(".env.example", "r") as f:
        example_content = f.read()
    
    # Generate SECRET_KEY
    secret_key = secrets.token_hex(32)
    
    # Create .env with generated secret key
    env_content = example_content.replace(
        "SECRET_KEY=your-super-secret-key-change-this-to-random-string-in-production",
        f"SECRET_KEY={secret_key}"
    )
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print_success(".env file created with generated SECRET_KEY")
    print_warning("Please review and update other values in .env")
    return True

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")
    
    directories = ["logs", "data", "data/backups", "templates", "static"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_success(f"Directory created/verified: {directory}")
    
    return True

def test_database():
    """Test database connection"""
    print_header("Testing Database Connection")
    
    try:
        from app import init_db
        init_db()
        print_success("Database initialized successfully")
        return True
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False

def check_static_files():
    """Check if required static files exist"""
    print_header("Checking Static Files")
    
    required_files = [
        "StudentInfoPage.html",
        "result.html",
        "index.html",
        "style.css",
        "styles.css"
    ]
    
    all_found = True
    for file in required_files:
        if os.path.exists(file):
            print_success(f"Found: {file}")
        else:
            print_warning(f"Missing: {file}")
            all_found = False
    
    return all_found

def generate_secret_key():
    """Generate a new SECRET_KEY"""
    print_header("Generating New SECRET_KEY")
    secret_key = secrets.token_hex(32)
    print(f"Generated SECRET_KEY: {secret_key}")
    print_warning("Add this to your .env file as SECRET_KEY=")
    return secret_key

def deployment_checklist():
    """Show deployment checklist"""
    print_header("Deployment Checklist")
    
    checklist = {
        "Security": [
            ("Debug Mode OFF", "FLASK_DEBUG=False"),
            ("SECRET_KEY Generated", "Use `python setup.py --generate-key`"),
            ("CORS Configured", "Whitelist specific origins"),
            ("Input Validation", "All user inputs validated"),
        ],
        "Performance": [
            ("Static Files", "Using url_for() in templates"),
            ("Database", "Indexes on frequently queried fields"),
            ("Logging", "Error logs configured"),
            ("WSGI Server", "Gunicorn or Waitress configured"),
        ],
        "Deployment": [
            ("Requirements.txt", "All dependencies listed"),
            (".env File", "Production values set"),
            (".gitignore", ".env is ignored"),
            ("SSL/HTTPS", "Certificate configured"),
        ],
    }
    
    for category, items in checklist.items():
        print(f"\n{category}:")
        for item, recommendation in items:
            print(f"  □ {item}")
            print(f"    └─ {recommendation}")

def run_all_checks():
    """Run all checks"""
    results = {
        "Python Version": check_python_version(),
        "Virtual Environment": check_virtual_environment(),
        "Static Files": check_static_files(),
    }
    
    print_header("Setup Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nChecks Passed: {passed}/{total}")
    
    if passed == total:
        print_success("All checks passed! Ready for next steps.")
    else:
        print_warning("Please fix the errors above before deploying.")

def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("  RGPV Flask Application - Production Setup")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser(description="Production setup script")
    parser.add_argument("--full-setup", action="store_true", help="Run complete setup")
    parser.add_argument("--generate-key", action="store_true", help="Generate new SECRET_KEY")
    parser.add_argument("--check-all", action="store_true", help="Run all checks")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    
    args = parser.parse_args()
    
    if args.generate_key:
        generate_secret_key()
    elif args.full_setup:
        check_python_version()
        check_virtual_environment()
        install_requirements()
        setup_env_file()
        create_directories()
        test_database()
        check_static_files()
        deployment_checklist()
    elif args.install_deps:
        install_requirements()
    elif args.check_all:
        run_all_checks()
        deployment_checklist()
    else:
        # Default: show checklist
        deployment_checklist()
        print_header("Quick Start")
        print("Setup options:")
        print("  python setup.py --full-setup       # Complete setup")
        print("  python setup.py --generate-key    # Generate SECRET_KEY")
        print("  python setup.py --install-deps    # Install dependencies")
        print("  python setup.py --check-all       # Run all checks")

if __name__ == "__main__":
    main()
