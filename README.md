# OpenAI Whisper Demo

A comprehensive demonstration of the OpenAI Whisper speech-to-text model with both command-line and web interfaces.

## Features

- 🎤 **Audio Transcription**: Convert speech to text using OpenAI's Whisper model
- 🌐 **Web Interface**: User-friendly web application for uploading and transcribing audio files
- 📁 **Batch Processing**: Process multiple audio files at once
- 🗣️ **Language Detection**: Automatic language detection or manual specification
- ⏱️ **Timestamps**: Detailed transcription with word-level timestamps
- 🚀 **Multiple Models**: Support for different Whisper model sizes (tiny, base, small, medium, large)
- 📊 **Performance Metrics**: Processing time and speed ratio information

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd openaiwhisperdemo
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python whisper_demo.py --help
   ```

## Quick Start

### Web Interface (Recommended)

1. **Start the web server**
   ```bash
   python web_app.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Upload and transcribe**
   - Select an audio file
   - Optionally specify a language
   - Click "Transcribe Audio"

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
   - Try accessing `http://127.0.0.1:5000`
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
