#!/usr/bin/env node

/**
 * Asterisk AEAP Speech-to-Text Server
 * Based on https://github.com/asterisk/aeap-speech-to-text
 * Modified for IPMD testing platform
 */

const WebSocket = require('ws');
const speech = require('@google-cloud/speech');
const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const ffmpeg = require('fluent-ffmpeg');

// Configuration
const PORT = process.env.PORT || 9099;
const HTTP_PORT = process.env.HTTP_PORT || 3001;
const UPLOAD_DIR = 'uploads';

// Create upload directory
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Initialize Google Speech client
const speechClient = new speech.SpeechClient();

// Express app for file uploads
const app = express();
app.use(cors());
app.use(express.json());

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD_DIR);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ 
    storage: storage,
    limits: { fileSize: 100 * 1024 * 1024 } // 100MB limit
});

// Convert audio to format supported by Google Speech API
function convertAudio(inputPath, outputPath) {
    return new Promise((resolve, reject) => {
        ffmpeg(inputPath)
            .audioCodec('pcm_s16le')
            .audioFrequency(16000)
            .audioChannels(1)
            .format('wav')
            .on('end', () => {
                console.log('Audio conversion completed');
                resolve(outputPath);
            })
            .on('error', (err) => {
                console.error('Audio conversion error:', err);
                reject(err);
            })
            .save(outputPath);
    });
}

// Transcribe audio using Google Speech API
async function transcribeAudio(audioPath, language = 'en-US') {
    try {
        // Convert audio to WAV format if needed
        const wavPath = audioPath.replace(/\.[^/.]+$/, '.wav');
        if (!audioPath.endsWith('.wav')) {
            await convertAudio(audioPath, wavPath);
        } else {
            wavPath = audioPath;
        }

        // Read the audio file
        const audioBytes = fs.readFileSync(wavPath).toString('base64');

        // Configure the request
        const request = {
            audio: {
                content: audioBytes,
            },
            config: {
                encoding: 'LINEAR16',
                sampleRateHertz: 16000,
                languageCode: language,
                enableAutomaticPunctuation: true,
                enableWordTimeOffsets: true,
            },
        };

        // Perform the transcription
        const startTime = Date.now();
        const [response] = await speechClient.recognize(request);
        const processingTime = (Date.now() - startTime) / 1000;

        const results = response.results;
        if (results.length === 0) {
            throw new Error('No transcription results found');
        }

        const transcription = results
            .map(result => result.alternatives[0].transcript)
            .join('\n');

        const confidence = results[0].alternatives[0].confidence || 0;

        // Get word-level timestamps
        const words = results[0].alternatives[0].words || [];
        const segments = words.map(word => ({
            word: word.word,
            start: parseFloat(word.startTime.seconds || 0) + (parseFloat(word.startTime.nanos || 0) / 1e9),
            end: parseFloat(word.endTime.seconds || 0) + (parseFloat(word.endTime.nanos || 0) / 1e9),
            confidence: word.confidence || 0
        }));

        // Clean up temporary files
        if (wavPath !== audioPath && fs.existsSync(wavPath)) {
            fs.unlinkSync(wavPath);
        }

        return {
            text: transcription,
            confidence: confidence,
            segments: segments,
            processing_time: processingTime,
            language: language
        };

    } catch (error) {
        console.error('Transcription error:', error);
        throw error;
    }
}

// WebSocket server for AEAP
const wss = new WebSocket.Server({ port: PORT });

wss.on('connection', (ws) => {
    console.log('New AEAP client connected');

    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            console.log('Received AEAP message:', data.type);

            // Handle different AEAP message types
            switch (data.type) {
                case 'speech_to_text':
                    // Handle speech-to-text request
                    console.log('Speech-to-text request received');
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error parsing AEAP message:', error);
        }
    });

    ws.on('close', () => {
        console.log('AEAP client disconnected');
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

// HTTP endpoint for file uploads (for web interface)
app.post('/transcribe', upload.single('audio_file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No audio file provided' });
        }

        const language = req.body.language || 'en-US';
        const audioPath = req.file.path;

        console.log(`Transcribing audio file: ${audioPath}`);

        const result = await transcribeAudio(audioPath, language);

        // Clean up uploaded file
        fs.unlinkSync(audioPath);

        res.json({
            success: true,
            text: result.text,
            confidence: result.confidence,
            segments: result.segments,
            processing_time: result.processing_time,
            language: result.language,
            engine: 'asterisk-aeap'
        });

    } catch (error) {
        console.error('Transcription error:', error);
        res.status(500).json({ 
            error: 'Transcription failed: ' + error.message 
        });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        engine: 'asterisk-aeap',
        port: PORT,
        http_port: HTTP_PORT
    });
});

// Start servers
app.listen(HTTP_PORT, () => {
    console.log(`HTTP server listening on port ${HTTP_PORT}`);
    console.log(`WebSocket server listening on port ${PORT}`);
    console.log('Asterisk AEAP Speech-to-Text server ready');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down servers...');
    wss.close(() => {
        console.log('WebSocket server closed');
        process.exit(0);
    });
});
