# BMS-Hackathon

## Problem statement:
Chanting Om kara (Sound meditation)
- Real-time correction for Spinal  alignment (sitting straight)
- Real-time correction for Head/neck movements  
- Give audio alert messages in real-time whenever eyes are open 
- Guide for length of Om chanting (calculate the time in seconds for length of chant)  

## Project Overview
om_meditation_app/
│
├── main.py                # Entry point (run this to start program)
├── requirements.txt       # Dependency list for pip install
├── README.md              # Project description and instructions
│
├── posture_detection/
│   ├── pose_utils.py      # MediaPipe pose control & calculations
│   └── head_neck.py       # Head/neck alignment logic
│
├── eye_monitor/
│   ├── blink_detector.py  # Eye open/close detection
│   ├── alert.py           # Audio alert trigger
│
├── audio_analysis/
│   ├── record.py          # Record Om chant (mic input)
│   └── duration.py        # Calculate chant duration
│
├── guides/
│   ├── om_timing.py       # UI and feedback for chant timing
│   └── instructions.py    # Scripted meditation assistance
│
├── utils/
│   ├── camera.py          # Camera capture utilities
│   └── logger.py          # Logging and data recording
│
└── tests/
    └── test_all.py        # Unit tests for all modules
