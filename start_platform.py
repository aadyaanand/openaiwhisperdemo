#!/usr/bin/env python3
"""
Startup script for IPMD Voice-to-Text Testing Platform
Starts both Whisper (Python) and Asterisk AEAP (Node.js) servers
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class PlatformManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_whisper_server(self):
        """Start the Whisper web server."""
        print("🐍 Starting Whisper server...")
        try:
            process = subprocess.Popen([
                sys.executable, 'web_app.py'
            ], cwd=os.getcwd())
            self.processes.append(('Whisper', process))
            print("✅ Whisper server started on http://localhost:5001")
            return True
        except Exception as e:
            print(f"❌ Failed to start Whisper server: {e}")
            return False
    
    def start_asterisk_server(self):
        """Start the Asterisk AEAP server."""
        print("⚡ Starting Asterisk AEAP server...")
        try:
            # Check if Node.js is available
            try:
                subprocess.run(['node', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ Node.js not found. Please install Node.js to run Asterisk AEAP server.")
                return False
            
            # Install Node.js dependencies
            asterisk_dir = Path('asterisk-server')
            if asterisk_dir.exists():
                print("📦 Installing Asterisk server dependencies...")
                subprocess.run(['npm', 'install'], cwd=asterisk_dir, check=True)
                
                # Start the server
                process = subprocess.Popen([
                    'node', 'index.js'
                ], cwd=asterisk_dir)
                self.processes.append(('Asterisk', process))
                print("✅ Asterisk AEAP server started on http://localhost:3001")
                return True
            else:
                print("❌ Asterisk server directory not found")
                return False
        except Exception as e:
            print(f"❌ Failed to start Asterisk server: {e}")
            return False
    
    def check_google_credentials(self):
        """Check if Google Speech API credentials are available."""
        google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not google_creds:
            print("⚠️  Warning: GOOGLE_APPLICATION_CREDENTIALS not set.")
            print("   Asterisk AEAP server requires Google Speech API credentials.")
            print("   Set the environment variable to your service account key file.")
            return False
        elif not os.path.exists(google_creds):
            print(f"⚠️  Warning: Google credentials file not found: {google_creds}")
            return False
        else:
            print("✅ Google Speech API credentials found")
            return True
    
    def start_platform(self):
        """Start the entire platform."""
        print("🚀 Starting IPMD Voice-to-Text Testing Platform")
        print("=" * 60)
        
        # Check Google credentials
        self.check_google_credentials()
        
        # Start servers
        whisper_ok = self.start_whisper_server()
        asterisk_ok = self.start_asterisk_server()
        
        if not whisper_ok and not asterisk_ok:
            print("❌ Failed to start any servers")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Platform started successfully!")
        print("=" * 60)
        print("🌐 Web Interface: http://localhost:5001")
        print("🐍 Whisper Engine: Available")
        if asterisk_ok:
            print("⚡ Asterisk AEAP Engine: Available")
        else:
            print("⚡ Asterisk AEAP Engine: Not available (check Google credentials)")
        print("\nPress Ctrl+C to stop all servers")
        print("=" * 60)
        
        return True
    
    def stop_platform(self):
        """Stop all running processes."""
        print("\n🛑 Stopping platform...")
        self.running = False
        
        for name, process in self.processes:
            try:
                print(f"Stopping {name} server...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} server stopped")
            except subprocess.TimeoutExpired:
                print(f"Force killing {name} server...")
                process.kill()
            except Exception as e:
                print(f"Error stopping {name} server: {e}")
        
        print("✅ Platform stopped")
    
    def run(self):
        """Run the platform with signal handling."""
        if not self.start_platform():
            return
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            self.stop_platform()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_platform()

def main():
    """Main function."""
    manager = PlatformManager()
    manager.run()

if __name__ == "__main__":
    main()
