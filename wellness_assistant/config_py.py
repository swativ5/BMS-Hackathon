#!/usr/bin/env python3
"""
Configuration Module
Central configuration for all wellness assistant components
"""

# Camera Settings
CAMERA_CONFIG = {
    'default_index': 0,
    'frame_width': 640,
    'frame_height': 480,
    'fps': 30,
    'flip_horizontal': True
}

# Posture Detection Settings
POSTURE_CONFIG = {
    'auto_calibration_frames': 75,
    'shoulder_tilt_tolerance': 1.5,
    'head_forward_tolerance': 1.5,
    'slouch_tolerance': 0.8,
    'head_tilt_tolerance': 15,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'distance_thresholds': {
        'too_close': 0.15,  # fraction of frame width
        'too_far': 0.6      # fraction of frame width
    }
}

# Eye Detection Settings
EYE_CONFIG = {
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5,
    'default_ear_threshold': 0.22,
    'calibration_frames_min': 30,
    'max_num_faces': 1,
    'refine_landmarks': True
}

# Speech Recognition Settings
SPEECH_CONFIG = {
    'recognizer_timeout': 1.0,
    'phrase_time_limit': 15,
    'ambient_noise_duration': 2.0,
    'silence_threshold': 300,  # RMS threshold
    'api_timeout': 5.0,
    'om_keywords': ["om", "aum", "ohm", "oom", "um", "hmm"]
}

# Text-to-Speech Settings
TTS_CONFIG = {
    'speech_rate': 140,
    'preferred_voices': ["female", "zira"],
    'queue_timeout': 1.0,
    'engine_timeout': 5.0
}

# Breathing Session Settings
BREATHING_CONFIG = {
    'default_interval': 20,  # seconds between sessions
    'inhale_duration': 4,    # seconds
    'exhale_duration': 6,    # seconds
    'max_listen_time': 15,   # seconds
    'session_timeout': 30,   # seconds
    'min_interval': 10,      # minimum interval
    'max_interval': 300      # maximum interval (5 minutes)
}

# Display Settings
DISPLAY_CONFIG = {
    'window_name': "Unified Wellness Assistant",
    'font_face': 'FONT_HERSHEY_SIMPLEX',
    'font_scale': {
        'large': 1.0,
        'medium': 0.8,
        'small': 0.6
    },
    'colors': {
        'good': (0, 255, 0),      # Green
        'bad': (0, 0, 255),       # Red
        'warning': (0, 0, 255),   # Red
        'info': (255, 255, 255),  # White
        'calibrating': (0, 255, 255),  # Yellow
        'accent': (255, 255, 0)   # Cyan
    },
    'line_thickness': 2,
    'circle_radius': 5
}

# Application Settings
APP_CONFIG = {
    'calibration_countdown': 5,   # seconds
    'calibration_duration': 3,    # seconds
    'stats_update_interval': 1.0, # seconds
    'component_test_timeout': 10, # seconds
    'max_session_duration': 3600, # 1 hour
    'auto_save_stats': True,
    'log_level': 'INFO'
}

# File Paths
PATHS_CONFIG = {
    'log_directory': 'logs/',
    'data_directory': 'data/',
    'config_file': 'user_config.json',
    'stats_file': 'session_stats.json',
    'calibration_file': 'calibration_data.json'
}

# Thresholds and Limits
LIMITS_CONFIG = {
    'max_bad_posture_streak': 100,   # frames
    'max_eyes_closed_streak': 50,    # frames
    'min_session_duration': 30,      # seconds
    'max_calibration_attempts': 3,
    'audio_buffer_size': 4096,
    'max_audio_length': 30           # seconds
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'thread_sleep_interval': 0.1,   # seconds
    'frame_skip_threshold': 5,       # skip frames if processing is slow
    'memory_limit_mb': 512,          # MB
    'cpu_usage_limit': 80,           # percentage
    'enable_gpu_acceleration': True,
    'optimize_for_battery': False
}

# Debug Settings
DEBUG_CONFIG = {
    'enable_debug_mode': False,
    'show_landmarks': False,
    'save_debug_frames': False,
    'print_performance_stats': False,
    'log_audio_data': False,
    'verbose_speech_recognition': False
}

# Default User Preferences
USER_PREFERENCES = {
    'breathing_interval': 20,
    'enable_voice_guidance': True,
    'enable_posture_alerts': True,
    'enable_eye_tracking': True,
    'enable_statistics': True,
    'auto_calibrate': True,
    'show_landmarks': False,
    'mute_audio': False
}


class Config:
    """Configuration manager class"""
    
    def __init__(self):
        self.camera = CAMERA_CONFIG.copy()
        self.posture = POSTURE_CONFIG.copy()
        self.eye = EYE_CONFIG.copy()
        self.speech = SPEECH_CONFIG.copy()
        self.tts = TTS_CONFIG.copy()
        self.breathing = BREATHING_CONFIG.copy()
        self.display = DISPLAY_CONFIG.copy()
        self.app = APP_CONFIG.copy()
        self.paths = PATHS_CONFIG.copy()
        self.limits = LIMITS_CONFIG.copy()
        self.performance = PERFORMANCE_CONFIG.copy()
        self.debug = DEBUG_CONFIG.copy()
        self.user = USER_PREFERENCES.copy()
    
    def update_from_dict(self, config_dict):
        """Update configuration from dictionary"""
        for section, values in config_dict.items():
            if hasattr(self, section):
                getattr(self, section).update(values)
    
    def to_dict(self):
        """Convert configuration to dictionary"""
        return {
            'camera': self.camera,
            'posture': self.posture,
            'eye': self.eye,
            'speech': self.speech,
            'tts': self.tts,
            'breathing': self.breathing,
            'display': self.display,
            'app': self.app,
            'paths': self.paths,
            'limits': self.limits,
            'performance': self.performance,
            'debug': self.debug,
            'user': self.user
        }
    
    def save_to_file(self, filepath=None):
        """Save configuration to JSON file"""
        import json
        import os
        
        if filepath is None:
            filepath = self.paths['config_file']
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def load_from_file(self, filepath=None):
        """Load configuration from JSON file"""
        import json
        import os
        
        if filepath is None:
            filepath = self.paths['config_file']
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
                self.update_from_dict(config_dict)
    
    def get_opencv_font(self):
        """Get OpenCV font constant"""
        import cv2
        return getattr(cv2, self.display['font_face'])
    
    def get_color(self, color_name):
        """Get color tuple by name"""
        return self.display['colors'].get(color_name, (255, 255, 255))
    
    def validate_config(self):
        """Validate configuration values"""
        errors = []
        
        # Validate camera settings
        if not (0 <= self.camera['default_index'] <= 10):
            errors.append("Invalid camera index")
        
        if self.camera['frame_width'] < 320 or self.camera['frame_height'] < 240:
            errors.append("Frame size too small")
        
        # Validate breathing settings
        if self.breathing['default_interval'] < self.breathing['min_interval']:
            errors.append("Breathing interval too small")
        
        if self.breathing['inhale_duration'] <= 0 or self.breathing['exhale_duration'] <= 0:
            errors.append("Invalid breathing durations")
        
        # Validate thresholds
        for tolerance in ['shoulder_tilt_tolerance', 'head_forward_tolerance', 'slouch_tolerance']:
            if self.posture[tolerance] <= 0:
                errors.append(f"Invalid posture {tolerance}")
        
        return errors
    
    def reset_to_defaults(self):
        """Reset all configuration to defaults"""
        self.__init__()


# Global configuration instance
config = Config()

# Convenience functions
def get_config():
    """Get global configuration instance"""
    return config

def update_config(config_dict):
    """Update global configuration"""
    config.update_from_dict(config_dict)

def load_user_config(filepath=None):
    """Load user configuration from file"""
    config.load_from_file(filepath)

def save_user_config(filepath=None):
    """Save current configuration to file"""
    config.save_to_file(filepath)