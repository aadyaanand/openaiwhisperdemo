#!/usr/bin/env python3
"""
Web interface for OpenAI Whisper Demo
A Flask web application for uploading and transcribing audio files.
"""

import os
import time
import tempfile
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from whisper_demo import WhisperDemo
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'wma', 'aac', 'webm'}

# Global Whisper demo instance
whisper_demo = None

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

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and transcription."""
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
        
        # Initialize Whisper if not already done
        init_whisper()
        
        # Transcribe audio
        start_time = time.time()
        result = whisper_demo.transcribe_audio(filepath, language)
        processing_time = time.time() - start_time
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Prepare response
        response = {
            'success': True,
            'text': result['text'],
            'language': result['language'],
            'segments': result['segments'],
            'audio_duration': result['audio_duration'],
            'processing_time': processing_time,
            'speed_ratio': result['audio_duration'] / processing_time if processing_time > 0 else 0
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/asterisk-upload', methods=['POST'])
def asterisk_upload():
    """Handle file upload for Asterisk AEAP transcription."""
    try:
        if 'audio_file' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Debug information
        print(f"Asterisk file details - Filename: {file.filename}, Content-Type: {file.content_type}")
        
        if not is_valid_audio_file(file):
            return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS) + ' or recorded audio'}), 400
        
        # Get language parameter
        language = request.form.get('language', '').strip()
        if not language:
            language = 'en-US'
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Send to Asterisk server
        import requests
        
        asterisk_url = 'http://localhost:3001/transcribe'
        
        with open(filepath, 'rb') as audio_file:
            files = {'audio_file': (filename, audio_file, file.content_type)}
            data = {'language': language}
            
            try:
                response = requests.post(asterisk_url, files=files, data=data, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify(result)
                
            except requests.exceptions.RequestException as e:
                # Clean up uploaded file
                os.remove(filepath)
                return jsonify({'error': f'Asterisk server error: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'whisper_loaded': whisper_demo is not None})

if __name__ == '__main__':
    # Create upload directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("Starting Whisper Web Demo...")
    print("Open your browser and go to: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
