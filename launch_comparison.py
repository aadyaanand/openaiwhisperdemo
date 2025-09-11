#!/usr/bin/env python3
"""
Launch script for Voice-to-Text Comparison Demo
Starts the comparison web interface for IPMD testing.
"""

import os
import sys
import subprocess
import webbrowser
import time
import signal

def check_azure_config():
    """Check if Azure Speech Services is configured."""
    azure_key = os.getenv('AZURE_SPEECH_KEY')
    azure_region = os.getenv('AZURE_SPEECH_REGION')
    
    if azure_key and azure_region:
        print("✅ Azure Speech Services configured")
        return True
    else:
        print("⚠️  Azure Speech Services not configured")
        print("   Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables")
        print("   Or edit azure_config_example.txt and source it")
        return False

def main():
    """Launch the comparison demo."""
    print("🎤 Voice-to-Text Comparison Demo - IPMD")
    print("=" * 50)
    
    # Check Azure configuration
    azure_available = check_azure_config()
    
    if not azure_available:
        print("\nYou can still test Whisper-only functionality.")
        response = input("Continue with Whisper-only mode? (y/n): ").lower()
        if response != 'y':
            print("Exiting. Configure Azure Speech Services to enable full comparison.")
            return
    
    print("\n🚀 Starting comparison web interface...")
    print("   URL: http://localhost:5002")
    print("   Press Ctrl+C to stop")
    
    try:
        # Start the comparison web app
        process = subprocess.Popen([sys.executable, 'comparison_web_app.py'])
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open('http://localhost:5002')
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            process.terminate()
            process.wait()
            print("✅ Server stopped")
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
