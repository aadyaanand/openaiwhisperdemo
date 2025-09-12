#!/usr/bin/env python3
"""
Setup script for Asterisk AEAP server
Installs Node.js dependencies and checks requirements
"""

import subprocess
import sys
import os
from pathlib import Path

def check_nodejs():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js found: {version}")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def check_npm():
    """Check if npm is available."""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npm found: {version}")
            return True
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False

def install_dependencies():
    """Install Node.js dependencies."""
    asterisk_dir = Path('asterisk-server')
    
    if not asterisk_dir.exists():
        print("❌ Asterisk server directory not found")
        return False
    
    print("📦 Installing Node.js dependencies...")
    try:
        result = subprocess.run(['npm', 'install'], cwd=asterisk_dir, check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_google_credentials():
    """Check Google Speech API credentials."""
    google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not google_creds:
        print("⚠️  GOOGLE_APPLICATION_CREDENTIALS not set")
        print("   To use Asterisk AEAP server, you need Google Speech API credentials.")
        print("   Set the environment variable to your service account key file:")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json")
        return False
    elif not os.path.exists(google_creds):
        print(f"⚠️  Google credentials file not found: {google_creds}")
        return False
    else:
        print("✅ Google Speech API credentials found")
        return True

def main():
    """Main setup function."""
    print("🚀 Setting up Asterisk AEAP Server")
    print("=" * 40)
    
    # Check Node.js
    if not check_nodejs():
        print("\n❌ Please install Node.js first:")
        print("   Visit: https://nodejs.org/")
        return False
    
    # Check npm
    if not check_npm():
        print("\n❌ Please install npm first")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return False
    
    # Check Google credentials
    check_google_credentials()
    
    print("\n" + "=" * 40)
    print("🎉 Asterisk AEAP server setup completed!")
    print("=" * 40)
    print("To start the server:")
    print("  cd asterisk-server")
    print("  node index.js")
    print("\nOr use the platform launcher:")
    print("  python3 start_platform.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
