#!/usr/bin/env python3
"""
OpenAI Whisper Demo
A comprehensive demonstration of the OpenAI Whisper speech-to-text model.
"""

import os
import sys
import time
import argparse
import ssl
import whisper
import torch
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, Any

# Fix SSL certificate issues on macOS
ssl._create_default_https_context = ssl._create_unverified_context


class WhisperDemo:
    """A comprehensive demo class for OpenAI Whisper functionality."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the Whisper demo with a specified model size.
        
        Args:
            model_size: Size of the Whisper model to use (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
    def load_model(self) -> None:
        """Load the Whisper model."""
        print(f"Loading Whisper model '{self.model_size}'...")
        start_time = time.time()
        
        try:
            self.model = whisper.load_model(self.model_size, device=self.device)
            load_time = time.time() - start_time
            print(f"Model loaded successfully in {load_time:.2f} seconds")
        except Exception as e:
            print(f"Error loading model: {e}")
            sys.exit(1)
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Dictionary containing transcription results
        """
        if self.model is None:
            self.load_model()
        
        print(f"Transcribing audio: {audio_path}")
        
        # Validate audio file
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load and preprocess audio
        audio_data = self._load_audio(audio_path)
        
        # Transcribe
        start_time = time.time()
        result = self.model.transcribe(
            audio_data,
            language=language,
            fp16=False if self.device == "cpu" else True
        )
        transcription_time = time.time() - start_time
        
        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "transcription_time": transcription_time,
            "audio_duration": len(audio_data) / 16000  # Assuming 16kHz sample rate
        }
    
    def _load_audio(self, audio_path: str) -> np.ndarray:
        """
        Load and preprocess audio file for Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Preprocessed audio array
        """
        try:
            # For webm files, use whisper's built-in loading which handles FFmpeg
            if audio_path.lower().endswith('.webm'):
                return whisper.load_audio(audio_path)
            
            # For other formats, try librosa first
            audio, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            # Ensure audio is float32
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            return audio
            
        except Exception as e:
            print(f"Error loading audio with librosa: {e}")
            # Fallback to whisper's built-in loading (uses FFmpeg)
            try:
                return whisper.load_audio(audio_path)
            except Exception as e2:
                print(f"Error loading audio with whisper: {e2}")
                raise e2
    
    def transcribe_with_timestamps(self, audio_path: str, language: Optional[str] = None) -> None:
        """
        Transcribe audio and display results with timestamps.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code
        """
        result = self.transcribe_audio(audio_path, language)
        
        print("\n" + "="*60)
        print("TRANSCRIPTION RESULTS")
        print("="*60)
        print(f"Audio file: {audio_path}")
        print(f"Detected language: {result['language']}")
        print(f"Audio duration: {result['audio_duration']:.2f} seconds")
        print(f"Transcription time: {result['transcription_time']:.2f} seconds")
        print(f"Speed ratio: {result['audio_duration'] / result['transcription_time']:.2f}x")
        print("\nFull transcription:")
        print("-" * 40)
        print(result['text'])
        
        if result['segments']:
            print("\nDetailed segments with timestamps:")
            print("-" * 40)
            for i, segment in enumerate(result['segments'], 1):
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()
                print(f"[{start_time:6.1f}s - {end_time:6.1f}s] {text}")
    
    def batch_transcribe(self, input_dir: str, output_dir: str, language: Optional[str] = None) -> None:
        """
        Transcribe multiple audio files in a directory.
        
        Args:
            input_dir: Directory containing audio files
            output_dir: Directory to save transcription results
            language: Optional language code
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Supported audio formats
        audio_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma'}
        
        audio_files = [f for f in input_path.iterdir() 
                      if f.suffix.lower() in audio_extensions]
        
        if not audio_files:
            print(f"No audio files found in {input_dir}")
            return
        
        print(f"Found {len(audio_files)} audio files to transcribe")
        
        for audio_file in audio_files:
            try:
                print(f"\nProcessing: {audio_file.name}")
                result = self.transcribe_audio(str(audio_file), language)
                
                # Save results
                output_file = output_path / f"{audio_file.stem}_transcription.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"File: {audio_file.name}\n")
                    f.write(f"Language: {result['language']}\n")
                    f.write(f"Duration: {result['audio_duration']:.2f}s\n")
                    f.write(f"Transcription time: {result['transcription_time']:.2f}s\n")
                    f.write("\nTranscription:\n")
                    f.write(result['text'])
                
                print(f"Results saved to: {output_file}")
                
            except Exception as e:
                print(f"Error processing {audio_file.name}: {e}")


def main():
    """Main function to run the Whisper demo."""
    parser = argparse.ArgumentParser(description="OpenAI Whisper Demo")
    parser.add_argument("--model", default="base", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model size")
    parser.add_argument("--audio", type=str, help="Path to audio file to transcribe")
    parser.add_argument("--language", type=str, help="Language code (e.g., 'en', 'es', 'fr')")
    parser.add_argument("--batch", type=str, help="Directory containing audio files for batch processing")
    parser.add_argument("--output", type=str, help="Output directory for batch processing")
    
    args = parser.parse_args()
    
    # Initialize demo
    demo = WhisperDemo(model_size=args.model)
    
    if args.audio:
        # Single file transcription
        demo.transcribe_with_timestamps(args.audio, args.language)
    elif args.batch:
        # Batch processing
        output_dir = args.output or "transcriptions"
        demo.batch_transcribe(args.batch, output_dir, args.language)
    else:
        print("Please provide either --audio for single file or --batch for directory processing")
        print("Use --help for more information")


if __name__ == "__main__":
    main()
