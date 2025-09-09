#!/usr/bin/env python3
"""
Test script to verify recording functionality works
"""

import os
import tempfile
import numpy as np
import soundfile as sf
from whisper_demo import WhisperDemo

def create_test_webm():
    """Create a test webm file to simulate recorded audio."""
    try:
        # Generate test audio
        duration = 3  # seconds
        sample_rate = 16000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Add some variation
        audio += np.sin(2 * np.pi * frequency * 2 * t) * 0.1
        audio += np.random.normal(0, 0.05, len(audio))
        
        # Save as WAV first
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_wav.name, audio, sample_rate)
        temp_wav.close()
        
        # Convert to WEBM using FFmpeg
        temp_webm = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        temp_webm.close()
        
        import subprocess
        result = subprocess.run([
            'ffmpeg', '-i', temp_wav.name, '-c:a', 'libopus', 
            '-b:a', '64k', temp_webm.name, '-y'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr}")
            return None
        
        # Clean up WAV file
        os.unlink(temp_wav.name)
        
        return temp_webm.name
        
    except Exception as e:
        print(f"Error creating test webm: {e}")
        return None

def test_webm_transcription():
    """Test transcription of webm file."""
    print("Testing WEBM transcription...")
    
    # Create test webm file
    webm_file = create_test_webm()
    if not webm_file:
        print("❌ Could not create test webm file")
        return False
    
    try:
        # Test transcription
        demo = WhisperDemo(model_size="tiny")
        demo.load_model()
        
        result = demo.transcribe_audio(webm_file)
        
        print("✅ WEBM transcription successful!")
        print(f"   Detected language: {result['language']}")
        print(f"   Audio duration: {result['audio_duration']:.2f}s")
        print(f"   Processing time: {result['transcription_time']:.2f}s")
        print(f"   Text: {result['text'][:100]}...")
        
        # Clean up
        os.unlink(webm_file)
        return True
        
    except Exception as e:
        print(f"❌ WEBM transcription failed: {e}")
        if webm_file and os.path.exists(webm_file):
            os.unlink(webm_file)
        return False

def main():
    """Run the test."""
    print("🧪 Testing Recording Functionality")
    print("=" * 40)
    
    # Test FFmpeg availability
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg is not working")
            return False
    except Exception as e:
        print(f"❌ FFmpeg error: {e}")
        return False
    
    # Test webm transcription
    success = test_webm_transcription()
    
    if success:
        print("\n🎉 All tests passed! Recording should work now.")
        print("Try recording audio in the web interface at http://localhost:5001")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return success

if __name__ == "__main__":
    main()
