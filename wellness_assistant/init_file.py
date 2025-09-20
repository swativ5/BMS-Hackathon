#!/usr/bin/env python3
"""
Wellness Assistant Package
A comprehensive wellness application with posture monitoring, 
eye detection, and breathing/chant guidance.
"""

from wellness_app import WellnessApp
from posture_detector import PostureDetector
from eye_detector import EyeDetector
from chant_detector import ChantDetector
from breathing_thread import BreathingThread
from speech_engine import SpeechEngine, get_speech_engine, speak, speak_sync

__version__ = "1.0.0"
__author__ = "Wellness Team"
__email__ = "wellness@example.com"

__all__ = [
    'WellnessApp',
    'PostureDetector', 
    'EyeDetector',
    'ChantDetector',
    'BreathingThread',
    'SpeechEngine',
    'get_speech_engine',
    'speak',
    'speak_sync'
]

# Package metadata
PACKAGE_INFO = {
    'name': 'wellness-assistant',
    'version': __version__,
    'description': 'Comprehensive wellness monitoring with posture, eye, and breathing detection',
    'author': __author__,
    'email': __email__,
    'requires': [
        'opencv-python>=4.5.0',
        'mediapipe>=0.8.0',
        'numpy>=1.19.0',
        'speech-recognition>=3.8.0',
        'pyttsx3>=2.90',
        'pyaudio>=0.2.11'
    ],
    'python_requires': '>=3.7'
}