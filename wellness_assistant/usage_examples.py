#!/usr/bin/env python3
"""
Usage Examples for Wellness Assistant
Demonstrates different ways to use the modular wellness system
"""

from wellness_assistant import WellnessApp, PostureDetector, EyeDetector, ChantDetector
import cv2
import speech_recognition as sr
import time

def example_1_simple_usage():
    """Example 1: Simple app usage"""
    print("Example 1: Simple Wellness App")
    print("-" * 30)
    
    app = WellnessApp()
    
    # Initialize and start
    if app.initialize_camera():
        app.start_session()
        
        # Get final summary
        summary = app.get_session_summary()
        if summary:
            print(f"Session completed: {summary['total_session_time']:.1f}s")
            print(f"Good posture: {summary['posture']['good_percent']:.1f}%")

def example_2_custom_breathing_interval():
    """Example 2: Custom breathing interval"""
    print("\nExample 2: Custom Breathing Interval")
    print("-" * 30)
    
    app = WellnessApp()
    
    # Set custom interval (every 30 seconds instead of 20)
    app.set_breathing_interval(30)
    
    if app.initialize_camera():
        print("Starting session with 30-second breathing intervals...")
        app.start_session()

def example_3_posture_only():
    """Example 3: Posture detection only"""
    print("\nExample 3: Posture Detection Only")
    print("-" * 30)
    
    cap = cv2.VideoCapture(0)
    posture_detector = PostureDetector()
    
    print("Starting posture-only monitoring. Press 'q' to quit.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            posture_good, warning = posture_detector.detect_posture(frame)
            
            # Display status
            color = (0, 255, 0) if posture_good else (0, 0, 255)
            status = "GOOD POSTURE" if posture_good else "BAD POSTURE"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            if warning:
                cv2.putText(frame, warning, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Show stats
            stats = posture_detector.get_stats()
            cv2.putText(frame, f"Good: {stats['good_percent']:.1f}%", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow("Posture Monitor", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()

def example_4_chant_only():
    """Example 4: Chant detection only"""
    print("\nExample 4: Chant Detection Only")
    print("-" * 30)
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    chant_detector = ChantDetector(recognizer, microphone)
    
    # Calibrate microphone
    chant_detector.calibrate_microphone()
    
    print("Starting chant-only mode. Say 'Om' when prompted.")
    
    try:
        for i in range(3):  # 3 sessions
            print(f"\nSession {i+1}/3")
            detected, duration = chant_detector.complete_breathing_session()
            
            if detected:
                print(f"✅ Success! Chanted for {duration:.1f}s")
            else:
                print(f"❌ Not detected. Duration: {duration:.1f}s")
            
            time.sleep(2)  # Wait between sessions
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    
    # Final stats
    stats = chant_detector.get_stats()
    print(f"\nFinal Stats: {stats['successful_detections']}/{stats['total_sessions']} successful")

def example_5_eye_detection_only():
    """Example 5: Eye detection only"""
    print("\nExample 5: Eye Detection Only")
    print("-" * 30)
    
    cap = cv2.VideoCapture(0)
    eye_detector = EyeDetector()
    
    print("Starting eye detection calibration (3 seconds)...")
    print("Keep your eyes open and look at the camera.")
    
    # Calibration phase
    calibration_start = time.time()
    while time.time() - calibration_start < 3:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame = cv2.flip(frame, 1)
        eye_detector.detect_eyes(frame, calibrating=True)
        
        cv2.putText(frame, "Calibrating eyes...", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow("Eye Monitor", frame)
        cv2.waitKey(1)
    
    # Set threshold
    eye_detector.set_threshold()
    calibration_info = eye_detector.get_calibration_info()
    print(f"✅ Calibration complete. Threshold: {calibration_info['threshold']:.3f}")
    
    # Main detection
    print("Eye detection active. Press 'q' to quit.")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            eyes_open, left_ear, right_ear = eye_detector.detect_eyes(frame)
            
            # Display status
            color = (0, 255, 0) if eyes_open else (0, 0, 255)
            status = "EYES OPEN" if eyes_open else "EYES CLOSED"
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Show EAR values
            if left_ear and right_ear:
                avg_ear = (left_ear + right_ear) / 2
                cv2.putText(frame, f"EAR: {avg_ear:.3f}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.imshow("Eye Monitor", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()

def example_6_component_testing():
    """Example 6: Test all components"""
    print("\nExample 6: Component Testing")
    print("-" * 30)
    
    app = WellnessApp()
    
    # Test all components
    if app.test_components():
        print("✅ All components working correctly")
    else:
        print("❌ Some components failed")

def example_7_custom_callback():
    """Example 7: Custom session callback"""
    print("\nExample 7: Custom Session Callback")
    print("-" * 30)
    
    def my_session_callback(detected, duration):
        """Custom callback for breathing sessions"""
        if detected:
            print(f"🎉 Great job! Om detected for {duration:.1f} seconds")
        else:
            print(f"💪 Keep trying! Session duration: {duration:.1f} seconds")
        
        # You could add here:
        # - Log to file
        # - Send notification
        # - Update UI
        # - Play sound
    
    app = WellnessApp()
    
    # Set custom callback
    app.breathing_thread.set_session_callback(my_session_callback)
    
    if app.initialize_camera():
        app.start_session()

if __name__ == "__main__":
    print("🧘 Wellness Assistant Usage Examples")
    print("=" * 50)
    
    examples = [
        ("Simple Usage", example_1_simple_usage),
        ("Custom Breathing Interval", example_2_custom_breathing_interval),
        ("Posture Only", example_3_posture_only),
        ("Chant Only", example_4_chant_only),
        ("Eye Detection Only", example_5_eye_detection_only),
        ("Component Testing", example_6_component_testing),
        ("Custom Callback", example_7_custom_callback)
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    try:
        choice = input("\nEnter example number (1-7) or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            print("Goodbye!")
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(examples):
            name, func = examples[choice_num - 1]
            print(f"\nRunning: {name}")
            print("=" * 50)
            func()
        else:
            print("Invalid choice. Please enter a number between 1-7.")
            
    except (ValueError, KeyboardInterrupt):
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nError running example: {e}")
    