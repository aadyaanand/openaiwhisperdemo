#!/usr/bin/env python3
"""
Setup script for OpenAI Whisper Demo
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ["uploads", "audio_files", "transcriptions"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def test_installation():
    """Test if the installation works."""
    print("\nTesting installation...")
    try:
        import whisper
        import torch
        import librosa
        import flask
        print("✅ All required packages are available!")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up OpenAI Whisper Demo...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("Setup failed. Please check the error messages above.")
        return False
    
    # Create directories
    create_directories()
    
    # Test installation
    if not test_installation():
        print("Setup completed with warnings. Some features may not work.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Run the web interface: python web_app.py")
    print("2. Or try the command line: python whisper_demo.py --help")
    print("3. Check out the examples: python example_usage.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
