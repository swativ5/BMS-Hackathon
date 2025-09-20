# Wellness Assistant 🧘

A comprehensive wellness monitoring application that combines posture detection, eye tracking, and breathing/chanting guidance into a unified system.

## Features

- **🎯 Posture Detection**: Real-time posture monitoring with auto-calibration
- **👁️ Eye Tracking**: Open/closed eye detection using Eye Aspect Ratio (EAR)
- **🫁 Breathing Guidance**: Guided inhale/exhale cycles with Om chanting
- **🎤 Chant Recognition**: Advanced speech recognition for Om detection
- **📊 Statistics Tracking**: Comprehensive session analytics
- **🔧 Modular Design**: Easy to integrate and customize

## Installation

### Requirements
- Python 3.7+
- Camera (webcam)
- Microphone
- Audio output (speakers/headphones)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Dependencies Include:
- `opencv-python` - Computer vision and camera handling
- `mediapipe` - Pose and face landmark detection
- `numpy` - Numerical computations
- `speech-recognition` - Voice recognition
- `pyttsx3` - Text-to-speech synthesis
- `pyaudio` - Audio I/O

## File Structure

```
wellness_assistant/
├── __init__.py              # Package initialization
├── wellness_app.py          # Main application orchestrator
├── posture_detector.py      # Posture detection module
├── eye_detector.py          # Eye state detection module
├── chant_detector.py        # Breathing & chant detection
├── breathing_thread.py      # Background breathing thread
├── speech_engine.py         # Text-to-speech engine
├── usage_examples.py        # Example implementations
├── requirements.txt         # Package dependencies
```

## Module Overview

### 🏃 WellnessApp (`wellness_app.py`)
Main application class that orchestrates all components:
- Camera management
- System calibration
- Session control
- Real-time display
- Statistics tracking

### 🎯 PostureDetector (`posture_detector.py`)
Monitors user posture using MediaPipe pose detection:
- Auto-calibration for neutral posture
- Real-time posture evaluation
- Distance warnings (too close/far)
- Posture statistics

### 👁️ EyeDetector (`eye_detector.py`)
Tracks eye state using facial landmarks:
- Eye Aspect Ratio (EAR) calculation
- Open/closed eye detection
- Auto-threshold calibration
- Blink detection

### 🎤 ChantDetector (`chant_detector.py`)
Handles breathing guidance and Om detection:
- Guided breathing cycles
- Speech recognition for Om
- RMS-based silence detection
- Accurate duration measurement

### 🫁 BreathingThread (`breathing_thread.py`)
Background thread for breathing sessions:
- Non-blocking operation
- Configurable intervals
- Pause/resume functionality
- Session callbacks

### 🔊 SpeechEngine (`speech_engine.py`)
Thread-safe text-to-speech:
- Queued speech processing
- Voice customization
- Non-blocking TTS

## Controls During Session

- **Q**: Quit session
- **P**: Pause/resume breathing guidance
- **F**: Force immediate breathing session
- **R**: Reset statistics

## Configuration Options

### Posture Detection
- `AUTO_CALIBRATION_FRAMES`: Frames for auto-calibration (default: 75)
- `SHOULDER_TILT_TOLERANCE`: Shoulder tilt tolerance (default: 1.5)
- `HEAD_FORWARD_TOLERANCE`: Head forward tolerance (default: 1.5)
- `SLOUCH_TOLERANCE`: Slouching tolerance (default: 0.8)

### Eye Detection
- Auto-calibrated EAR threshold
- Supports manual threshold setting
- Configurable landmark points

### Breathing/Chanting
- `interval`: Time between sessions (default: 20s)
- `max_listen_time`: Max chant listening time (default: 15s)
- `silence_threshold`: RMS threshold for silence (default: 300)

## API Reference

### WellnessApp Methods
- `initialize_camera(camera_index=0)`: Initialize camera
- `start_session()`: Start wellness session
- `stop_session()`: Stop session
- `set_breathing_interval(interval)`: Set breathing interval
- `get_session_summary()`: Get session statistics

### PostureDetector Methods
- `detect_posture(frame)`: Detect posture in frame
- `get_stats()`: Get posture statistics
- `reset_stats()`: Reset statistics
- `reset_calibration()`: Reset calibration

### EyeDetector Methods
- `detect_eyes(frame, calibrating=False)`: Detect eye state
- `set_threshold(threshold=None)`: Set EAR threshold
- `get_calibration_info()`: Get calibration data

### ChantDetector Methods
- `complete_breathing_session()`: Full breathing session
- `detect_chant_blocking()`: Blocking chant detection
- `calibrate_microphone()`: Calibrate microphone
- `get_stats()`: Get chant statistics

## Troubleshooting

### Camera Issues
- Check camera permissions
- Try different camera indices (0, 1, 2...)
- Verify camera is not in use by other applications

### Microphone Issues
- Check microphone permissions
- Run microphone calibration
- Verify audio input device

### Performance Issues
- Lower camera resolution
- Increase detection confidence thresholds
- Close other applications using camera/microphone

### Speech Recognition Issues
- Check internet connection (Google Speech API)
- Speak clearly and close to microphone
- Reduce background noise

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review usage examples
