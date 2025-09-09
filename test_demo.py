#!/usr/bin/env python3
"""
Test script for OpenAI Whisper Demo
This script tests the basic functionality without requiring actual audio files.
"""

import os
import sys
import tempfile
import numpy as np
from whisper_demo import WhisperDemo

def create_test_audio():
    """Create a simple test audio file."""
    try:
        import librosa
        import soundfile as sf
        
        # Generate a simple sine wave
        duration = 2  # seconds
        sample_rate = 16000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Add some variation
        audio += np.sin(2 * np.pi * frequency * 2 * t) * 0.1
        audio += np.random.normal(0, 0.05, len(audio))
        
        # Save as temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_file.name, audio, sample_rate)
        temp_file.close()
        
        return temp_file.name
        
    except ImportError:
        print("librosa or soundfile not available, cannot create test audio")
        return None
    except Exception as e:
        print(f"Error creating test audio: {e}")
        return None

def test_model_loading():
    """Test if Whisper model can be loaded."""
    print("Testing model loading...")
    try:
        demo = WhisperDemo(model_size="tiny")  # Use tiny model for faster testing
        demo.load_model()
        print("✅ Model loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False

def test_audio_processing():
    """Test audio processing functionality."""
    print("Testing audio processing...")
    
    # Create test audio
    test_audio = create_test_audio()
    if not test_audio:
        print("❌ Could not create test audio file")
        return False
    
    try:
        demo = WhisperDemo(model_size="tiny")
        demo.load_model()
        
        # Test transcription
        result = demo.transcribe_audio(test_audio)
        
        print("✅ Audio processing successful!")
        print(f"   Detected language: {result['language']}")
        print(f"   Audio duration: {result['audio_duration']:.2f}s")
        print(f"   Processing time: {result['transcription_time']:.2f}s")
        
        # Clean up
        os.unlink(test_audio)
        return True
        
    except Exception as e:
        print(f"❌ Audio processing failed: {e}")
        if test_audio and os.path.exists(test_audio):
            os.unlink(test_audio)
        return False

def test_web_imports():
    """Test if web app dependencies are available."""
    print("Testing web app dependencies...")
    try:
        import flask
        from werkzeug.utils import secure_filename
        print("✅ Web app dependencies available!")
        return True
    except ImportError as e:
        print(f"❌ Web app dependencies missing: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing OpenAI Whisper Demo")
    print("=" * 40)
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Audio Processing", test_audio_processing),
        ("Web Dependencies", test_web_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The demo is ready to use.")
        print("\nTo start the web interface: python web_app.py")
        print("To run examples: python example_usage.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("You may need to install missing dependencies or check your setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
