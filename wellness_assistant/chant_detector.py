#!/usr/bin/env python3
"""
Chant Detection Module
Handles breathing guidance and Om chant detection using speech recognition
"""
import speech_recognition as sr
import audioop
import time
from speech_engine import speak


class ChantDetector:
    """Breathing guidance and chant detection"""
    
    def __init__(self, recognizer=None, microphone=None):
        self.recognizer = recognizer or sr.Recognizer()
        self.microphone = microphone or sr.Microphone()
        
        # Chant detection settings
        self.om_keywords = ["om", "aum", "ohm", "oom", "um", "hmm"]
        self.silence_threshold = 300  # RMS threshold for silence detection
        self.max_listen_time = 15     # Maximum listening time in seconds
        
        # Statistics
        self.total_sessions = 0
        self.successful_detections = 0
        self.total_chant_duration = 0.0
    
    def calibrate_microphone(self, duration=2):
        """Calibrate microphone for ambient noise"""
        print("🔧 Calibrating microphone...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print("✅ Microphone calibration complete.")
            return True
        except Exception as e:
            print(f"❌ Microphone calibration failed: {e}")
            return False
    
    def guide_breathing(self):
        """Guide user through breathing exercise"""
        speak("Inhale...")
        time.sleep(4)
        speak("Exhale...")
        time.sleep(6)
        speak("Begin chant Om...")
    
    def detect_chant_blocking(self, max_listen=None):
        """
        Listen for Om chant with blocking behavior
        
        Args:
            max_listen: Maximum listening time (uses default if None)
            
        Returns:
            tuple: (detected: bool, duration: float)
        """
        if max_listen is None:
            max_listen = self.max_listen_time
        
        try:
            with self.microphone as source:
                print("🎙️ Listening for chant...")
                audio = self.recognizer.listen(source, phrase_time_limit=max_listen)

            # Calculate actual duration from audio data
            duration = round(
                len(audio.frame_data) / (audio.sample_rate * audio.sample_width), 2
            )

            # Check for silence using RMS
            rms = audioop.rms(audio.get_raw_data(), audio.sample_width)
            if rms < self.silence_threshold:
                print("❌ No chant detected (silence)")
                return False, duration

            # Attempt speech recognition
            detected = False
            try:
                text = self.recognizer.recognize_google(audio).lower().strip()
                print(f"Recognized text: '{text}'")
                
                # Check for Om keywords
                if any(word in text for word in self.om_keywords):
                    detected = True
                    
            except sr.UnknownValueError:
                print("⚠️ Could not understand audio")
                detected = True # Comment when you want strict detection
            except sr.RequestError as e:
                print(f"⚠️ API error: {e}")
            except Exception as e:
                print(f"⚠️ Speech recognition error: {e}")

            # Provide feedback
            if detected:
                print(f"✅ Om detected | Duration: {duration} seconds")
            else:
                print(f"⚠️ Chant detected (not recognized as Om) | Duration: {duration} seconds")

            return detected, duration
            
        except Exception as e:
            print(f"❌ Chant detection error: {e}")
            return False, 0.0
    
    def detect_chant_non_blocking(self, timeout=1.0):
        """
        Non-blocking chant detection (for real-time applications)
        
        Args:
            timeout: Maximum time to wait for audio
            
        Returns:
            tuple: (detected: bool, duration: float, listening: bool)
        """
        try:
            with self.microphone as source:
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=2)
                    
                    # Quick duration calculation
                    duration = round(
                        len(audio.frame_data) / (audio.sample_rate * audio.sample_width), 2
                    )
                    
                    # Quick RMS check
                    rms = audioop.rms(audio.get_raw_data(), audio.sample_width)
                    if rms < self.silence_threshold:
                        return False, duration, False
                    
                    # Quick recognition attempt
                    try:
                        text = self.recognizer.recognize_google(audio, show_all=False).lower().strip()
                        detected = any(word in text for word in self.om_keywords)
                        return detected, duration, False
                    except:
                        return False, duration, False
                        
                except sr.WaitTimeoutError:
                    return False, 0.0, True  # Still listening
                    
        except Exception as e:
            print(f"Non-blocking detection error: {e}")
            return False, 0.0, False
    
    def complete_breathing_session(self):
        """Complete breathing and chant session"""
        self.total_sessions += 1
        session_start = time.time()
        
        print(f"\n[{time.strftime('%H:%M:%S')}] Starting breathing & chant session #{self.total_sessions}...")
        
        # Guide breathing
        self.guide_breathing()
        
        # Detect chant
        detected, duration = self.detect_chant_blocking()
        
        # Update statistics
        if detected:
            self.successful_detections += 1
        self.total_chant_duration += duration
        
        session_duration = time.time() - session_start
        print(f"Session completed in {session_duration:.1f}s total")
        
        return detected, duration
    
    def get_stats(self):
        """Get chant detection statistics"""
        success_rate = 0
        avg_chant_duration = 0
        
        if self.total_sessions > 0:
            success_rate = (self.successful_detections / self.total_sessions) * 100
        
        if self.successful_detections > 0:
            avg_chant_duration = self.total_chant_duration / self.successful_detections
        
        return {
            'total_sessions': self.total_sessions,
            'successful_detections': self.successful_detections,
            'success_rate': success_rate,
            'total_chant_duration': self.total_chant_duration,
            'average_chant_duration': avg_chant_duration
        }
    
    def reset_stats(self):
        """Reset chant detection statistics"""
        self.total_sessions = 0
        self.successful_detections = 0
        self.total_chant_duration = 0.0
    
    def test_microphone(self):
        """Test microphone functionality"""
        print("🎤 Testing microphone...")
        try:
            with self.microphone as source:
                print("Say something...")
                audio = self.recognizer.listen(source, phrase_time_limit=3)
                text = self.recognizer.recognize_google(audio)
                print(f"✅ Microphone test successful. Heard: '{text}'")
                return True
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False