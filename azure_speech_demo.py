#!/usr/bin/env python3
"""
Azure Speech Services Demo
A comprehensive demonstration of Azure Speech Services for speech-to-text.
"""

import os
import sys
import time
import argparse
import azure.cognitiveservices.speech as speechsdk
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, Any, List
import tempfile


class AzureSpeechDemo:
    """A comprehensive demo class for Azure Speech Services functionality."""
    
    def __init__(self, subscription_key: str = None, region: str = None):
        """
        Initialize the Azure Speech demo.
        
        Args:
            subscription_key: Azure Speech Services subscription key
            region: Azure region (e.g., 'eastus', 'westus2')
        """
        self.subscription_key = subscription_key or os.getenv('AZURE_SPEECH_KEY')
        self.region = region or os.getenv('AZURE_SPEECH_REGION', 'eastus')
        
        if not self.subscription_key:
            raise ValueError("Azure Speech Services subscription key is required. Set AZURE_SPEECH_KEY environment variable or pass subscription_key parameter.")
        
        print(f"Using Azure region: {self.region}")
        
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file using Azure Speech Services.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code (e.g., 'en-US', 'es-ES', 'fr-FR')
            
        Returns:
            Dictionary containing transcription results
        """
        print(f"Transcribing audio with Azure Speech Services: {audio_path}")
        
        # Validate audio file
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Configure speech service
        speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key, 
            region=self.region
        )
        
        # Set language if provided
        if language:
            speech_config.speech_recognition_language = language
        else:
            # Default to auto-detection
            speech_config.speech_recognition_language = "en-US"
        
        # Configure audio input
        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        
        # Create speech recognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        # Transcribe
        start_time = time.time()
        result = speech_recognizer.recognize_once_async().get()
        transcription_time = time.time() - start_time
        
        # Get audio duration
        audio_duration = self._get_audio_duration(audio_path)
        
        # Process result
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = result.text
            confidence = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult, "{}")
        elif result.reason == speechsdk.ResultReason.NoMatch:
            text = ""
            print(f"No speech could be recognized: {result.no_match_details}")
        else:
            text = ""
            print(f"Speech recognition failed: {result.cancellation_details}")
        
        return {
            "text": text.strip(),
            "language": language or "auto-detected",
            "segments": [],  # Azure doesn't provide word-level timestamps in basic mode
            "transcription_time": transcription_time,
            "audio_duration": audio_duration,
            "confidence": confidence,
            "service": "Azure Speech Services"
        }
    
    def transcribe_with_timestamps(self, audio_path: str, language: Optional[str] = None) -> None:
        """
        Transcribe audio and display results with timestamps.
        
        Args:
            audio_path: Path to the audio file
            language: Optional language code
        """
        result = self.transcribe_audio(audio_path, language)
        
        print("\n" + "="*60)
        print("AZURE SPEECH SERVICES TRANSCRIPTION RESULTS")
        print("="*60)
        print(f"Audio file: {audio_path}")
        print(f"Language: {result['language']}")
        print(f"Audio duration: {result['audio_duration']:.2f} seconds")
        print(f"Transcription time: {result['transcription_time']:.2f} seconds")
        print(f"Speed ratio: {result['audio_duration'] / result['transcription_time']:.2f}x")
        print(f"Service: {result['service']}")
        print("\nFull transcription:")
        print("-" * 40)
        print(result['text'])
    
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
        audio_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma', '.webm'}
        
        audio_files = [f for f in input_path.iterdir() 
                      if f.suffix.lower() in audio_extensions]
        
        if not audio_files:
            print(f"No audio files found in {input_dir}")
            return
        
        print(f"Found {len(audio_files)} audio files to transcribe with Azure Speech Services")
        
        for audio_file in audio_files:
            try:
                print(f"\nProcessing: {audio_file.name}")
                result = self.transcribe_audio(str(audio_file), language)
                
                # Save results
                output_file = output_path / f"{audio_file.stem}_azure_transcription.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"File: {audio_file.name}\n")
                    f.write(f"Service: Azure Speech Services\n")
                    f.write(f"Language: {result['language']}\n")
                    f.write(f"Duration: {result['audio_duration']:.2f}s\n")
                    f.write(f"Transcription time: {result['transcription_time']:.2f}s\n")
                    f.write(f"Speed ratio: {result['audio_duration'] / result['transcription_time']:.2f}x\n")
                    f.write("\nTranscription:\n")
                    f.write(result['text'])
                
                print(f"Results saved to: {output_file}")
                
            except Exception as e:
                print(f"Error processing {audio_file.name}: {e}")
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds."""
        try:
            audio, sr = librosa.load(audio_path, sr=None)
            return len(audio) / sr
        except Exception:
            # Fallback method
            try:
                import wave
                with wave.open(audio_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    return frames / sample_rate
            except Exception:
                return 0.0
    
    def compare_with_whisper(self, audio_path: str, whisper_demo, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare Azure Speech Services with Whisper on the same audio file.
        
        Args:
            audio_path: Path to the audio file
            whisper_demo: WhisperDemo instance
            language: Optional language code
            
        Returns:
            Dictionary with comparison results
        """
        print(f"\nComparing Azure Speech Services vs Whisper on: {audio_path}")
        print("=" * 60)
        
        # Azure transcription
        print("Running Azure Speech Services...")
        azure_start = time.time()
        azure_result = self.transcribe_audio(audio_path, language)
        azure_total_time = time.time() - azure_start
        
        # Whisper transcription
        print("Running Whisper...")
        whisper_start = time.time()
        whisper_result = whisper_demo.transcribe_audio(audio_path, language)
        whisper_total_time = time.time() - whisper_start
        
        # Comparison
        comparison = {
            "audio_file": audio_path,
            "audio_duration": azure_result['audio_duration'],
            "azure": {
                "text": azure_result['text'],
                "transcription_time": azure_result['transcription_time'],
                "total_time": azure_total_time,
                "speed_ratio": azure_result['audio_duration'] / azure_result['transcription_time']
            },
            "whisper": {
                "text": whisper_result['text'],
                "transcription_time": whisper_result['transcription_time'],
                "total_time": whisper_total_time,
                "speed_ratio": whisper_result['audio_duration'] / whisper_result['transcription_time']
            }
        }
        
        # Display comparison
        print(f"\nCOMPARISON RESULTS")
        print("=" * 40)
        print(f"Audio duration: {comparison['audio_duration']:.2f}s")
        print(f"\nAzure Speech Services:")
        print(f"  Text: {comparison['azure']['text'][:100]}...")
        print(f"  Transcription time: {comparison['azure']['transcription_time']:.2f}s")
        print(f"  Total time: {comparison['azure']['total_time']:.2f}s")
        print(f"  Speed ratio: {comparison['azure']['speed_ratio']:.2f}x")
        
        print(f"\nWhisper:")
        print(f"  Text: {comparison['whisper']['text'][:100]}...")
        print(f"  Transcription time: {comparison['whisper']['transcription_time']:.2f}s")
        print(f"  Total time: {comparison['whisper']['total_time']:.2f}s")
        print(f"  Speed ratio: {comparison['whisper']['speed_ratio']:.2f}x")
        
        return comparison


def main():
    """Main function to run the Azure Speech demo."""
    parser = argparse.ArgumentParser(description="Azure Speech Services Demo")
    parser.add_argument("--audio", type=str, help="Path to audio file to transcribe")
    parser.add_argument("--language", type=str, help="Language code (e.g., 'en-US', 'es-ES', 'fr-FR')")
    parser.add_argument("--batch", type=str, help="Directory containing audio files for batch processing")
    parser.add_argument("--output", type=str, help="Output directory for batch processing")
    parser.add_argument("--key", type=str, help="Azure Speech Services subscription key")
    parser.add_argument("--region", type=str, help="Azure region")
    
    args = parser.parse_args()
    
    try:
        # Initialize demo
        demo = AzureSpeechDemo(subscription_key=args.key, region=args.region)
        
        if args.audio:
            # Single file transcription
            demo.transcribe_with_timestamps(args.audio, args.language)
        elif args.batch:
            # Batch processing
            output_dir = args.output or "azure_transcriptions"
            demo.batch_transcribe(args.batch, output_dir, args.language)
        else:
            print("Please provide either --audio for single file or --batch for directory processing")
            print("Use --help for more information")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables")
        print("Or use --key and --region command line arguments")


if __name__ == "__main__":
    main()
