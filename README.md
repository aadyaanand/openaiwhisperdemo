# IPMD Voice-to-Text Testing Platform

A comprehensive testing platform for comparing different speech-to-text engines: OpenAI Whisper (Python) and Asterisk AEAP (JavaScript/Node.js). Built for IPMD to evaluate and compare voice recognition solutions.

## Features

### 🐍 OpenAI Whisper (Python)
- **Advanced AI Model**: High accuracy speech recognition with 99+ language support
- **Offline Processing**: Works without internet connection
- **Multiple Model Sizes**: tiny, base, small, medium, large for speed/accuracy tradeoffs
- **Word-level Timestamps**: Detailed transcription with precise timing
- **Language Detection**: Automatic language identification

### ⚡ Asterisk AEAP (JavaScript/Node.js)
- **Real-time Streaming**: Designed for telephony systems
- **Google Speech API**: Cloud-based processing with high accuracy
- **AEAP Protocol**: Asterisk External Application Protocol integration
- **Confidence Scores**: Detailed confidence metrics for each transcription
- **WebSocket Support**: Real-time communication with Asterisk

### 🌐 Unified Web Interface
- **Side-by-side Comparison**: Test both engines with the same audio
- **Recording & Upload**: Direct microphone recording or file upload
- **Performance Metrics**: Processing time, speed ratios, and accuracy scores
- **Mobile Responsive**: Works on desktop and mobile devices
- **Batch Processing**: Process multiple files with different engines

## Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/aadyaanand/openaiwhisperdemo.git
   cd openaiwhisperdemo
   ```

2. **Install Python dependencies**
   ```bash
   python3 setup.py
   ```

3. **Install Node.js dependencies (for Asterisk AEAP)**
   ```bash
   python3 setup_asterisk.py
   ```

4. **Set up Google Speech API credentials (for Asterisk AEAP)**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
   ```

5. **Verify installation**
   ```bash
   python3 test_demo.py
   ```

## Quick Start

### Complete Platform (Both Engines)

1. **Start the entire platform**
   ```bash
   python3 start_platform.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5001`

3. **Test both engines**
   - Choose between Whisper (Python) or Asterisk AEAP (JavaScript)
   - Upload an audio file or record directly
   - Compare results side-by-side

### Individual Engines

**Whisper Only:**
```bash
python3 web_app.py
# Access at http://localhost:5001
```

**Asterisk AEAP Only:**
```bash
cd asterisk-server
node index.js
# Access at http://localhost:3001
```

### Command Line Interface

1. **Single file transcription**
   ```bash
   python whisper_demo.py --audio your_audio_file.wav
   ```

2. **Batch processing**
   ```bash
   python whisper_demo.py --batch audio_directory --output transcriptions
   ```

3. **With specific language**
   ```bash
   python whisper_demo.py --audio your_audio_file.wav --language en
   ```

## Usage Examples

### Basic Transcription

```python
from whisper_demo import WhisperDemo

# Initialize with base model
demo = WhisperDemo(model_size="base")

# Transcribe a single file
result = demo.transcribe_audio("audio.wav")
print(result['text'])

# Transcribe with timestamps
demo.transcribe_with_timestamps("audio.wav", language="en")
```

### Batch Processing

```python
# Process multiple files
demo.batch_transcribe("input_directory", "output_directory", language="en")
```

### Different Model Sizes

```python
# Use different model sizes for different speed/accuracy tradeoffs
demo_tiny = WhisperDemo(model_size="tiny")    # Fastest, least accurate
demo_base = WhisperDemo(model_size="base")    # Balanced
demo_large = WhisperDemo(model_size="large")  # Slowest, most accurate
```

## Supported Audio Formats

- WAV
- MP3
- M4A
- FLAC
- OGG
- WMA
- AAC

## Model Sizes

| Model  | Parameters | English-only | Multilingual | Required VRAM | Relative speed |
|--------|------------|--------------|--------------|---------------|----------------|
| tiny   | 39 M       | ✓            | ✓            | ~1 GB         | ~32x           |
| base   | 74 M       | ✓            | ✓            | ~1 GB         | ~16x           |
| small  | 244 M      | ✓            | ✓            | ~2 GB         | ~6x            |
| medium | 769 M      | ✓            | ✓            | ~5 GB         | ~2x            |
| large  | 1550 M     | ✗            | ✓            | ~10 GB        | 1x             |

## Command Line Options

```bash
python whisper_demo.py [OPTIONS]

Options:
  --model {tiny,base,small,medium,large}
                        Whisper model size (default: base)
  --audio PATH          Path to audio file to transcribe
  --language TEXT       Language code (e.g., 'en', 'es', 'fr')
  --batch PATH          Directory containing audio files for batch processing
  --output PATH         Output directory for batch processing
  --help                Show help message
```

## Web Interface Features

- **Drag & Drop**: Upload files by dragging them to the upload area
- **Real-time Processing**: See processing progress and results in real-time
- **Detailed Results**: View transcription with timestamps and metadata
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Clear error messages for troubleshooting

## API Endpoints

### POST /upload
Upload and transcribe an audio file.

**Request:**
- `audio_file`: Audio file (multipart/form-data)
- `language`: Optional language code (form data)

**Response:**
```json
{
  "success": true,
  "text": "Transcribed text...",
  "language": "en",
  "segments": [...],
  "audio_duration": 10.5,
  "processing_time": 2.3,
  "speed_ratio": 4.57
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "whisper_loaded": true
}
```

## Performance Tips

1. **Use appropriate model size**: Choose based on your accuracy vs speed requirements
2. **GPU acceleration**: Install PyTorch with CUDA support for faster processing
3. **Audio preprocessing**: Ensure audio is in a supported format and reasonable quality
4. **Batch processing**: Process multiple files together to amortize model loading time

## Troubleshooting

### Common Issues

1. **Model loading errors**
   - Ensure you have sufficient disk space (models are large)
   - Check internet connection for initial download
   - Verify PyTorch installation

2. **Audio file errors**
   - Check file format is supported
   - Ensure file is not corrupted
   - Try converting to WAV format

3. **Memory errors**
   - Use smaller model size
   - Process shorter audio files
   - Close other applications

4. **Web interface not loading**
   - Check if port 5000 is available
   - Check firewall settings

### Getting Help

- Check the console output for error messages
- Verify all dependencies are installed correctly
- Try with a simple audio file first
- Check the example usage script

## Examples

See `example_usage.py` for comprehensive usage examples including:
- Single file transcription
- Batch processing
- Model comparison
- Language detection
- Sample audio generation

## Requirements

- Python 3.7+
- PyTorch 1.9.0+
- OpenAI Whisper
- Flask (for web interface)
- librosa (for audio processing)
- soundfile (for audio I/O)

## License

This project is for demonstration purposes. Please check OpenAI's license terms for commercial use of Whisper.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this demo.

## Acknowledgments

- OpenAI for the Whisper model
- The open-source community for the excellent libraries used
