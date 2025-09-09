#!/usr/bin/env python3
"""
Demo launcher script
Provides an easy way to run different parts of the Whisper demo.
"""

import sys
import subprocess
import os

def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 50)
    print("🎤 OpenAI Whisper Demo Launcher")
    print("=" * 50)
    print("1. Start Web Interface")
    print("2. Run Command Line Demo")
    print("3. Run Examples")
    print("4. Test Installation")
    print("5. Setup/Install Dependencies")
    print("6. Exit")
    print("=" * 50)

def run_web_interface():
    """Start the web interface."""
    print("Starting web interface...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    try:
        subprocess.run([sys.executable, "web_app.py"])
    except KeyboardInterrupt:
        print("\nWeb interface stopped.")

def run_command_line():
    """Run command line demo."""
    print("\nCommand Line Demo")
    print("=" * 30)
    print("Available options:")
    print("python whisper_demo.py --help")
    print("\nExample usage:")
    print("python whisper_demo.py --audio your_audio_file.wav")
    print("python whisper_demo.py --batch audio_directory --output transcriptions")
    
    choice = input("\nWould you like to see the help message? (y/n): ").lower()
    if choice == 'y':
        subprocess.run([sys.executable, "whisper_demo.py", "--help"])

def run_examples():
    """Run the example script."""
    print("Running examples...")
    try:
        subprocess.run([sys.executable, "example_usage.py"])
    except KeyboardInterrupt:
        print("\nExamples stopped.")

def test_installation():
    """Test the installation."""
    print("Testing installation...")
    try:
        subprocess.run([sys.executable, "test_demo.py"])
    except KeyboardInterrupt:
        print("\nTest stopped.")

def setup_dependencies():
    """Setup dependencies."""
    print("Setting up dependencies...")
    try:
        subprocess.run([sys.executable, "setup.py"])
    except KeyboardInterrupt:
        print("\nSetup stopped.")

def main():
    """Main launcher function."""
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                run_web_interface()
            elif choice == '2':
                run_command_line()
            elif choice == '3':
                run_examples()
            elif choice == '4':
                test_installation()
            elif choice == '5':
                setup_dependencies()
            elif choice == '6':
                print("Goodbye! 👋")
                break
            else:
                print("Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
