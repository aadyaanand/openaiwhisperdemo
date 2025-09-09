#!/usr/bin/env python3
"""
Example usage of the OpenAI Whisper Demo
This script demonstrates various ways to use the Whisper demo functionality.
"""

import os
import sys
from whisper_demo import WhisperDemo
import time

def example_single_file():
    """Example: Transcribe a single audio file."""
    print("=" * 60)
    print("EXAMPLE 1: Single File Transcription")
    print("=" * 60)
    
    # Initialize demo with base model
    demo = WhisperDemo(model_size="base")
    
    # Example audio file path (you would replace this with your actual file)
    audio_file = "example_audio.wav"
    
    if not os.path.exists(audio_file):
        print(f"Audio file '{audio_file}' not found.")
        print("Please place an audio file named 'example_audio.wav' in the current directory")
        print("or modify the audio_file variable to point to your audio file.")
        return
    
    try:
        # Transcribe with timestamps
        demo.transcribe_with_timestamps(audio_file, language="en")
    except Exception as e:
        print(f"Error during transcription: {e}")

def example_batch_processing():
    """Example: Batch process multiple audio files."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Batch Processing")
    print("=" * 60)
    
    # Initialize demo
    demo = WhisperDemo(model_size="base")
    
    # Input and output directories
    input_dir = "audio_files"
    output_dir = "transcriptions"
    
    # Create input directory if it doesn't exist
    os.makedirs(input_dir, exist_ok=True)
    
    if not os.path.exists(input_dir) or not os.listdir(input_dir):
        print(f"Input directory '{input_dir}' is empty or doesn't exist.")
        print("Please add some audio files to the 'audio_files' directory")
        return
    
    try:
        # Process all audio files in the directory
        demo.batch_transcribe(input_dir, output_dir, language="en")
        print(f"\nBatch processing completed. Results saved to '{output_dir}' directory.")
    except Exception as e:
        print(f"Error during batch processing: {e}")

def example_different_models():
    """Example: Compare different model sizes."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Model Size Comparison")
    print("=" * 60)
    
    audio_file = "example_audio.wav"
    
    if not os.path.exists(audio_file):
        print(f"Audio file '{audio_file}' not found.")
        return
    
    models = ["tiny", "base", "small"]
    
    for model_size in models:
        print(f"\n--- Testing {model_size} model ---")
        
        try:
            demo = WhisperDemo(model_size=model_size)
            start_time = time.time()
            result = demo.transcribe_audio(audio_file)
            total_time = time.time() - start_time
            
            print(f"Model: {model_size}")
            print(f"Load + Transcribe time: {total_time:.2f}s")
            print(f"Transcription time: {result['transcription_time']:.2f}s")
            print(f"Speed ratio: {result['audio_duration'] / result['transcription_time']:.2f}x")
            print(f"Text preview: {result['text'][:100]}...")
            
        except Exception as e:
            print(f"Error with {model_size} model: {e}")

def example_language_detection():
    """Example: Language detection and transcription."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Language Detection")
    print("=" * 60)
    
    demo = WhisperDemo(model_size="base")
    
    # Test files in different languages (you would need actual files)
    test_files = [
        ("english_audio.wav", "en"),
        ("spanish_audio.wav", "es"),
        ("french_audio.wav", "fr"),
    ]
    
    for audio_file, expected_lang in test_files:
        if os.path.exists(audio_file):
            try:
                print(f"\nProcessing: {audio_file}")
                result = demo.transcribe_audio(audio_file)
                
                print(f"Expected language: {expected_lang}")
                print(f"Detected language: {result['language']}")
                print(f"Text: {result['text'][:200]}...")
                
            except Exception as e:
                print(f"Error processing {audio_file}: {e}")
        else:
            print(f"File {audio_file} not found, skipping...")

def create_sample_audio():
    """Create a sample audio file for testing (requires librosa)."""
    print("\n" + "=" * 60)
    print("CREATING SAMPLE AUDIO FILE")
    print("=" * 60)
    
    try:
        import librosa
        import numpy as np
        
        # Generate a simple sine wave as sample audio
        duration = 5  # seconds
        sample_rate = 16000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Add some variation to make it more interesting
        audio += np.sin(2 * np.pi * frequency * 2 * t) * 0.1
        audio += np.random.normal(0, 0.05, len(audio))
        
        # Save as WAV file
        output_file = "sample_audio.wav"
        librosa.output.write_wav(output_file, audio, sample_rate)
        
        print(f"Sample audio file created: {output_file}")
        print("You can now use this file for testing the transcription.")
        
    except ImportError:
        print("librosa not available. Cannot create sample audio file.")
        print("Please install librosa or provide your own audio file.")
    except Exception as e:
        print(f"Error creating sample audio: {e}")

def main():
    """Run all examples."""
    print("OpenAI Whisper Demo - Example Usage")
    print("=" * 60)
    
    # Create sample audio if possible
    create_sample_audio()
    
    # Run examples
    example_single_file()
    example_batch_processing()
    example_different_models()
    example_language_detection()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nTo run the web interface:")
    print("python web_app.py")
    print("\nTo run command-line transcription:")
    print("python whisper_demo.py --audio your_audio_file.wav")
    print("python whisper_demo.py --batch audio_directory --output transcriptions")

if __name__ == "__main__":
    main()
