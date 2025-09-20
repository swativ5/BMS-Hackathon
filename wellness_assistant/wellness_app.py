#!/usr/bin/env python3
"""
Main Wellness Application
Orchestrates all components for the unified wellness assistant
"""
import cv2
import time
import speech_recognition as sr
from posture_detector import PostureDetector
from eye_detector import EyeDetector
from breathing_thread import BreathingThread
from speech_engine import get_speech_engine


class WellnessApp:
    """Main application class for the wellness assistant"""
    
    def __init__(self):
        # Initialize camera
        self.cap = None
        self.camera_initialized = False
        
        # Initialize detectors
        self.posture_detector = PostureDetector()
        self.eye_detector = EyeDetector()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize breathing thread
        self.breathing_thread = BreathingThread(
            self.recognizer, 
            self.microphone, 
            interval=20
        )
        self.breathing_thread.set_session_callback(self.on_breathing_session_complete)
        
        # Initialize speech engine
        self.speech_engine = get_speech_engine()
        
        # Application state
        self.running = False
        self.session_start_time = None
        self.calibration_complete = False
        
        # Display settings
        self.frame_width = 640
        self.frame_height = 480
        self.window_name = "Unified Wellness Assistant"
    
    def initialize_camera(self, camera_index=0):
        """Initialize camera with specified settings"""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise Exception(f"Cannot open camera {camera_index}")
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            
            # Test camera
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Cannot read from camera")
            
            self.camera_initialized = True
            print("Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return False
    
    def calibrate_system(self):
        """Calibrate microphone, posture, and eye detection"""
        print("\n🔧 System Calibration")
        print("=" * 50)
        
        # Calibrate microphone
        if not self.breathing_thread.calibrate_microphone(duration=2):
            print("Microphone calibration failed, continuing anyway...")
        
        # Initial countdown
        print("⏳ Position yourself in camera frame. Calibration starting in 5 seconds...")
        countdown_start = time.time()
        
        while time.time() - countdown_start < 5:
            if not self._process_frame_during_setup("Setting up & calibrating..."):
                return False
        
        # Eye and posture calibration
        print("Calibrating posture & eyes. Keep neutral pose with eyes open...")
        calibration_start = time.time()
        
        while time.time() - calibration_start < 3:
            ret, frame = self.cap.read()
            if not ret:
                print("Camera read failed during calibration")
                return False
            
            frame = cv2.flip(frame, 1)
            
            # Collect calibration data
            self.eye_detector.detect_eyes(frame, calibrating=True)
            self.posture_detector.detect_posture(frame)
            
            # Display calibration status
            cv2.putText(frame, "Calibrating posture & eyes...",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            cv2.imshow(self.window_name, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return False
        
        # Finalize eye calibration
        self.eye_detector.set_threshold()
        
        calibration_info = self.eye_detector.get_calibration_info()
        print(f"Eye EAR threshold set to {calibration_info['threshold']:.3f}")

        self.calibration_complete = True
        print("System calibration complete!\n")
        return True
    
    def _process_frame_during_setup(self, message):
        """Process frame during setup/calibration"""
        ret, frame = self.cap.read()
        if not ret:
            return False
        
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.imshow(self.window_name, frame)
        
        return cv2.waitKey(1) & 0xFF != ord('q')
    
    def on_breathing_session_complete(self, detected, duration):
        """Callback for when a breathing session completes"""
        # This can be overridden or connected to UI updates
        stats = self.breathing_thread.get_stats()
        print(f"\nSession Stats: {stats['successful_detections']}/{stats['total_sessions']} "
              f"successful ({stats['success_rate']:.1f}%)")
    
    def start_session(self):
        """Start the wellness session"""
        if not self.camera_initialized:
            print("Camera not initialized")
            return False
        
        if not self.calibration_complete:
            if not self.calibrate_system():
                return False
        
        # Start breathing thread
        self.breathing_thread.start_breathing()
        
        # Start main session
        self.running = True
        self.session_start_time = time.time()
        print("Session started! Press 'q' to quit.\n")
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            print("\nSession interrupted by user")
        finally:
            self.stop_session()
        
        return True
    
    def _main_loop(self):
        """Main application loop"""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Camera read failed")
                break
            
            frame = cv2.flip(frame, 1)
            
            # Posture detection
            posture_good, warning = self.posture_detector.detect_posture(frame)
            self._draw_posture_status(frame, posture_good, warning)
            
            # Eye detection
            eyes_open, left_ear, right_ear = self.eye_detector.detect_eyes(frame)
            self._draw_eye_status(frame, eyes_open, left_ear, right_ear)
            
            # Statistics
            self._draw_statistics(frame)
            
            # Display frame
            cv2.imshow(self.window_name, frame)
            
            # Handle key input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                self._toggle_breathing_pause()
            elif key == ord('f'):
                self.breathing_thread.force_session()
            elif key == ord('r'):
                self._reset_stats()
    
    def _draw_posture_status(self, frame, posture_good, warning):
        """Draw posture status on frame"""
        posture_stats = self.posture_detector.get_stats()
        
        if not posture_stats['calibrated']:
            status_text = f"CALIBRATING... {posture_stats['calibration_progress']}/{self.posture_detector.AUTO_CALIBRATION_FRAMES}"
            status_color = (0, 255, 255)
        else:
            status_text = "GOOD POSTURE" if posture_good else "BAD POSTURE"
            status_color = (0, 255, 0) if posture_good else (0, 0, 255)
        
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        
        if warning:
            cv2.putText(frame, warning, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    def _draw_eye_status(self, frame, eyes_open, left_ear, right_ear):
        """Draw eye status on frame"""
        eye_text = "EYES OPEN" if eyes_open else "EYES CLOSED"
        eye_color = (0, 255, 0) if eyes_open else (0, 0, 255)
        cv2.putText(frame, eye_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, eye_color, 2)
        
        # Display EAR values
        if left_ear and right_ear:
            avg_ear = (left_ear + right_ear) / 2
            calibration_info = self.eye_detector.get_calibration_info()
            threshold = calibration_info['threshold']
            cv2.putText(frame, f"Avg EAR: {avg_ear:.3f} (Threshold: {threshold:.3f})",
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
    
    def _draw_statistics(self, frame):
        """Draw session statistics on frame"""
        # Posture statistics
        posture_stats = self.posture_detector.get_stats()
        cv2.putText(frame, f"Posture - Good: {posture_stats['good_percent']:.1f}% | Bad: {posture_stats['bad_percent']:.1f}%",
                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Eye statistics
        eye_stats = self.eye_detector.get_stats()
        if eye_stats['total_frames'] > 0:
            cv2.putText(frame, f"Eyes - Open: {eye_stats['open_percent']:.1f}% | Closed: {eye_stats['closed_percent']:.1f}%",
                       (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Session time
        elapsed = time.time() - self.session_start_time if self.session_start_time else 0
        cv2.putText(frame, f"Session time: {elapsed:.0f}s",
                   (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Breathing statistics
        breathing_stats = self.breathing_thread.get_stats()
        cv2.putText(frame, f"Chants: {breathing_stats['successful_detections']}/{breathing_stats['total_sessions']}",
                   (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Controls help
        cv2.putText(frame, "Q:Quit P:Pause F:Force R:Reset",
                   (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def _toggle_breathing_pause(self):
        """Toggle breathing thread pause state"""
        if self.breathing_thread.is_paused():
            self.breathing_thread.resume_breathing()
            print("Breathing sessions resumed")
        else:
            self.breathing_thread.pause_breathing()
            print("Breathing sessions paused")

    def _reset_stats(self):
        """Reset all statistics"""
        self.posture_detector.reset_stats()
        self.eye_detector.reset_stats()
        self.breathing_thread.reset_stats()
        print("Statistics reset")

    def stop_session(self):
        """Stop the wellness session"""
        self.running = False
        
        if self.breathing_thread.is_running():
            self.breathing_thread.stop_breathing()
        
        self._cleanup()
        print("Session ended successfully")
    
    def _cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def get_session_summary(self):
        """Get comprehensive session summary"""
        if not self.session_start_time:
            return None
        
        total_time = time.time() - self.session_start_time
        posture_stats = self.posture_detector.get_stats()
        eye_stats = self.eye_detector.get_stats()
        breathing_stats = self.breathing_thread.get_stats()
        
        return {
            'total_session_time': total_time,
            'posture': posture_stats,
            'eyes': eye_stats,
            'breathing': breathing_stats,
            'calibration_complete': self.calibration_complete
        }
    
    def set_breathing_interval(self, interval):
        """Set interval between breathing sessions"""
        self.breathing_thread.set_interval(interval)
        print(f"Breathing interval set to {interval} seconds")
    
    def test_components(self):
        """Test all system components"""
        print("\nComponent Testing")
        print("=" * 50)
        
        # Test camera
        if self.initialize_camera():
            print("Camera test passed")
        else:
            print("Camera test failed")
            return False
        
        # Test microphone
        if self.breathing_thread.test_microphone():
            print("Microphone test passed")
        else:
            print("Microphone test failed")

        # Test speech engine
        try:
            self.speech_engine.speak_sync("Testing speech engine")
            print("Speech engine test passed")
        except Exception as e:
            print(f"Speech engine test failed: {e}")

        self._cleanup()
        return True


def main():
    """Main function to run the wellness app"""
    print("Unified Wellness Assistant")
    print("=" * 50)
    
    app = WellnessApp()
    
    # Test components first
    if not app.test_components():
        print("\nComponent tests failed. Please check your setup.")
        return
    
    # Initialize camera for main session
    if not app.initialize_camera():
        print("\nFailed to initialize camera for session")
        return
    
    # Start session
    app.start_session()
    
    # Show session summary
    summary = app.get_session_summary()
    if summary:
        print("\nSession Summary")
        print("=" * 30)
        print(f"Total time: {summary['total_session_time']:.1f}s")
        print(f"Good posture: {summary['posture']['good_percent']:.1f}%")
        print(f"Eyes open: {summary['eyes']['open_percent']:.1f}%")
        print(f"Chant success rate: {summary['breathing']['success_rate']:.1f}%")


if __name__ == "__main__":
    main()