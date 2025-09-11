#!/usr/bin/env python3
"""
Voice-to-Text Comparison Web App
A Flask web application for comparing OpenAI Whisper vs Azure Speech Services.
"""

import os
import time
import tempfile
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from whisper_demo import WhisperDemo
from azure_speech_demo import AzureSpeechDemo
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'wma', 'aac', 'webm'}

# Global demo instances
whisper_demo = None
azure_demo = None

def allowed_file(filename):
    """Check if file has allowed extension."""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_audio_file(file):
    """Check if uploaded file is a valid audio file."""
    # Check if it's a file upload with extension
    if hasattr(file, 'filename') and file.filename:
        return allowed_file(file.filename)
    
    # Check if it's a recorded audio blob (no filename)
    if hasattr(file, 'content_type'):
        # MediaRecorder typically creates webm or ogg files
        return file.content_type in ['audio/webm', 'audio/ogg', 'audio/wav', 'audio/mp4']
    
    # For recorded audio blobs without filename
    return True

def init_whisper():
    """Initialize Whisper model."""
    global whisper_demo
    if whisper_demo is None:
        whisper_demo = WhisperDemo(model_size="base")
        whisper_demo.load_model()

def init_azure():
    """Initialize Azure Speech Services."""
    global azure_demo
    if azure_demo is None:
        try:
            azure_demo = AzureSpeechDemo()
            print("Azure Speech Services initialized successfully")
        except ValueError as e:
            print(f"Azure Speech Services not available: {e}")
            return False
    return True

@app.route('/')
def index():
    """Main page."""
    return render_template('comparison.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and transcription comparison."""
    try:
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Debug information
        print(f"File details - Filename: {file.filename}, Content-Type: {file.content_type}")
        
        if not is_valid_audio_file(file):
            return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS) + ' or recorded audio'}), 400
        
        # Get language parameter
        language = request.form.get('language', '').strip()
        if not language:
            language = None
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Initialize services
        init_whisper()
        azure_available = init_azure()
        
        results = {
            'success': True,
            'audio_duration': 0,
            'whisper': None,
            'azure': None,
            'comparison': None
        }
        
        # Get audio duration
        try:
            import librosa
            audio, sr = librosa.load(filepath, sr=None)
            results['audio_duration'] = len(audio) / sr
        except:
            results['audio_duration'] = 0
        
        # Whisper transcription
        try:
            print("Running Whisper transcription...")
            whisper_start = time.time()
            whisper_result = whisper_demo.transcribe_audio(filepath, language)
            whisper_total_time = time.time() - whisper_start
            
            results['whisper'] = {
                'text': whisper_result['text'],
                'language': whisper_result['language'],
                'transcription_time': whisper_result['transcription_time'],
                'total_time': whisper_total_time,
                'speed_ratio': whisper_result['audio_duration'] / whisper_result['transcription_time'] if whisper_result['transcription_time'] > 0 else 0,
                'segments': whisper_result['segments'],
                'service': 'OpenAI Whisper'
            }
        except Exception as e:
            print(f"Whisper error: {e}")
            results['whisper'] = {'error': str(e)}
        
        # Azure transcription
        if azure_available:
            try:
                print("Running Azure Speech Services transcription...")
                azure_start = time.time()
                azure_result = azure_demo.transcribe_audio(filepath, language)
                azure_total_time = time.time() - azure_start
                
                results['azure'] = {
                    'text': azure_result['text'],
                    'language': azure_result['language'],
                    'transcription_time': azure_result['transcription_time'],
                    'total_time': azure_total_time,
                    'speed_ratio': azure_result['audio_duration'] / azure_result['transcription_time'] if azure_result['transcription_time'] > 0 else 0,
                    'segments': azure_result['segments'],
                    'service': 'Azure Speech Services'
                }
            except Exception as e:
                print(f"Azure error: {e}")
                results['azure'] = {'error': str(e)}
        else:
            results['azure'] = {'error': 'Azure Speech Services not configured. Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION environment variables.'}
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy', 
        'whisper_loaded': whisper_demo is not None,
        'azure_available': init_azure()
    })

if __name__ == '__main__':
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("Starting Voice-to-Text Comparison Demo...")
    print("Open your browser and go to: http://localhost:5002")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
