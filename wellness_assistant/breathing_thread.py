#!/usr/bin/env python3
"""
Breathing Thread Module
Background thread for breathing guidance and chant detection
"""
import threading
import time
from chant_detector import ChantDetector


class BreathingThread(threading.Thread):
    """Background thread for breathing and chant sessions"""
    
    def __init__(self, recognizer, microphone, interval=20):
        super().__init__(daemon=True)
        self.chant_detector = ChantDetector(recognizer, microphone)
        self.interval = interval
        self.last_run = time.time()
        self.running = False
        self.paused = False
        
        # Event for thread control
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        
        # Callback for session results
        self.session_callback = None
    
    def set_session_callback(self, callback):
        """Set callback function for session results"""
        self.session_callback = callback
    
    def start_breathing(self):
        """Start the breathing thread"""
        if not self.running:
            self.running = True
            self._stop_event.clear()
            self._pause_event.clear()
            self.start()
    
    def stop_breathing(self):
        """Stop the breathing thread"""
        self.running = False
        self._stop_event.set()
        
    def pause_breathing(self):
        """Pause breathing sessions"""
        self.paused = True
        self._pause_event.set()
    
    def resume_breathing(self):
        """Resume breathing sessions"""
        self.paused = False
        self._pause_event.clear()
    
    def set_interval(self, interval):
        """Set new interval between breathing sessions"""
        self.interval = interval
    
    def calibrate_microphone(self, duration=2):
        """Calibrate microphone for the chant detector"""
        return self.chant_detector.calibrate_microphone(duration)
    
    def test_microphone(self):
        """Test microphone functionality"""
        return self.chant_detector.test_microphone()
    
    def run(self):
        """Main thread execution loop"""
        while self.running:
            if self._stop_event.is_set():
                break
            
            if self.paused:
                time.sleep(0.1)
                continue
            
            current_time = time.time()
            if current_time - self.last_run >= self.interval:
                try:
                    self.perform_breathing_session()
                    self.last_run = current_time
                except Exception as e:
                    print(f"❌ Error in breathing session: {e}")
            
            time.sleep(0.1)
    
    def perform_breathing_session(self):
        """Perform a complete breathing and chant session"""
        if self._stop_event.is_set() or self.paused:
            return
        
        # Run the breathing session
        detected, duration = self.chant_detector.complete_breathing_session()
        
        # Call callback if set
        if self.session_callback:
            try:
                self.session_callback(detected, duration)
            except Exception as e:
                print(f"❌ Error in session callback: {e}")
    
    def get_stats(self):
        """Get breathing and chant statistics"""
        return self.chant_detector.get_stats()
    
    def reset_stats(self):
        """Reset breathing and chant statistics"""
        self.chant_detector.reset_stats()
    
    def force_session(self):
        """Force an immediate breathing session (regardless of interval)"""
        if self.running and not self.paused:
            threading.Thread(
                target=self.perform_breathing_session, 
                daemon=True
            ).start()
    
    def is_running(self):
        """Check if breathing thread is running"""
        return self.running and not self._stop_event.is_set()
    
    def is_paused(self):
        """Check if breathing thread is paused"""
        return self.paused
    
    def get_time_until_next_session(self):
        """Get time remaining until next breathing session"""
        if not self.running or self.paused:
            return None
        
        elapsed = time.time() - self.last_run
        remaining = max(0, self.interval - elapsed)
        return remaining