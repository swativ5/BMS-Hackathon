#!/usr/bin/env python3
"""
Posture Detection Module
Detects and monitors user posture using MediaPipe pose detection
"""
import cv2
import mediapipe as mp
import numpy as np
import time


class PostureDetector:
    """Real-time posture detection with auto-calibration"""
    
    def __init__(self):
        # Initialize MediaPipe pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Statistics tracking
        self.total_frames = 0
        self.good_posture_frames = 0
        self.bad_posture_frames = 0
        self.start_time = time.time()
        
        # Calibration settings
        self.calibrated = False
        self.calibration_data = []
        self.reference = {
            "shoulder_line": 0,
            "head_forward": 0,
            "shoulder_hip_height": 0,
            "head_tilt": 0
        }
        
        # Configuration parameters
        self.AUTO_CALIBRATION_FRAMES = 75
        self.SHOULDER_TILT_TOLERANCE = 1.5
        self.HEAD_FORWARD_TOLERANCE = 1.5
        self.SLOUCH_TOLERANCE = 0.8
        self.HEAD_TILT_TOLERANCE = 15
    
    def reset_stats(self):
        """Reset posture statistics"""
        self.total_frames = 0
        self.good_posture_frames = 0
        self.bad_posture_frames = 0
        self.start_time = time.time()
    
    def reset_calibration(self):
        """Reset calibration data"""
        self.calibrated = False
        self.calibration_data = []
        self.reference = {
            "shoulder_line": 0,
            "head_forward": 0,
            "shoulder_hip_height": 0,
            "head_tilt": 0
        }
    
    def _extract_landmarks(self, results, frame_shape):
        """Extract key pose landmarks"""
        if not results.pose_landmarks:
            return None
        
        h, w, _ = frame_shape
        lm = results.pose_landmarks.landmark
        
        landmarks = {
            'left_shoulder': (
                lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x * w,
                lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y * h
            ),
            'right_shoulder': (
                lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w,
                lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h
            ),
            'left_ear': (
                lm[self.mp_pose.PoseLandmark.LEFT_EAR].x * w,
                lm[self.mp_pose.PoseLandmark.LEFT_EAR].y * h
            ),
            'right_ear': (
                lm[self.mp_pose.PoseLandmark.RIGHT_EAR].x * w,
                lm[self.mp_pose.PoseLandmark.RIGHT_EAR].y * h
            ),
            'nose': (
                lm[self.mp_pose.PoseLandmark.NOSE].x * w,
                lm[self.mp_pose.PoseLandmark.NOSE].y * h
            ),
            'left_hip': (
                lm[self.mp_pose.PoseLandmark.LEFT_HIP].x * w,
                lm[self.mp_pose.PoseLandmark.LEFT_HIP].y * h
            ),
            'right_hip': (
                lm[self.mp_pose.PoseLandmark.RIGHT_HIP].x * w,
                lm[self.mp_pose.PoseLandmark.RIGHT_HIP].y * h
            )
        }
        
        return landmarks
    
    def _calculate_posture_metrics(self, landmarks, frame_shape):
        """Calculate posture metrics from landmarks"""
        h, w, _ = frame_shape
        
        # Shoulder tilt angle
        shoulder_tilt = np.degrees(np.arctan2(
            abs(landmarks['left_shoulder'][1] - landmarks['right_shoulder'][1]),
            abs(landmarks['left_shoulder'][0] - landmarks['right_shoulder'][0]) + 1e-6
        ))
        
        # Head forward position
        head_forward = (
            (landmarks['left_ear'][0] - landmarks['left_shoulder'][0]) + 
            (landmarks['right_ear'][0] - landmarks['right_shoulder'][0])
        ) / 2 / w
        
        # Shoulder-hip height ratio (slouching indicator)
        mid_shoulder_y = (landmarks['left_shoulder'][1] + landmarks['right_shoulder'][1]) / 2
        mid_hip_y = (landmarks['left_hip'][1] + landmarks['right_hip'][1]) / 2
        shoulder_hip_height = (mid_hip_y - mid_shoulder_y) / h
        
        # Head tilt angle
        mid_shoulder_x = (landmarks['left_shoulder'][0] + landmarks['right_shoulder'][0]) / 2
        mid_shoulder_y = (landmarks['left_shoulder'][1] + landmarks['right_shoulder'][1]) / 2
        head_tilt = np.degrees(np.arctan2(
            landmarks['nose'][0] - mid_shoulder_x,
            landmarks['nose'][1] - mid_shoulder_y + 1e-6
        ))
        
        return {
            'shoulder_tilt': shoulder_tilt,
            'head_forward': head_forward,
            'shoulder_hip_height': shoulder_hip_height,
            'head_tilt': head_tilt
        }
    
    def _check_distance_warning(self, landmarks, frame_shape):
        """Check if user is too close or far from camera"""
        h, w, _ = frame_shape
        shoulder_width = abs(landmarks['left_shoulder'][0] - landmarks['right_shoulder'][0])
        
        if shoulder_width < w * 0.15:
            return "Move closer to camera"
        elif shoulder_width > w * 0.6:
            return "Move back from camera"
        return None
    
    def _draw_landmarks(self, frame, landmarks):
        """Draw pose landmarks on frame"""
        landmark_points = [
            landmarks['left_shoulder'], landmarks['right_shoulder'],
            landmarks['left_ear'], landmarks['right_ear'],
            landmarks['left_hip'], landmarks['right_hip'],
            landmarks['nose']
        ]
        
        for point in landmark_points:
            cv2.circle(frame, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)
    
    def detect_posture(self, frame):
        """
        Detect posture in frame and return results
        
        Returns:
            tuple: (posture_good: bool, warning: str or None)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        
        posture_good = True
        warning = None
        
        landmarks = self._extract_landmarks(results, frame.shape)
        
        if landmarks:
            # Check distance from camera
            warning = self._check_distance_warning(landmarks, frame.shape)
            
            # Calculate posture metrics
            metrics = self._calculate_posture_metrics(landmarks, frame.shape)
            
            # Handle calibration
            if not self.calibrated:
                self.calibration_data.append((
                    metrics['shoulder_tilt'],
                    metrics['head_forward'],
                    metrics['shoulder_hip_height'],
                    metrics['head_tilt']
                ))
                
                if len(self.calibration_data) >= self.AUTO_CALIBRATION_FRAMES:
                    avg = np.mean(self.calibration_data, axis=0)
                    self.reference = {
                        "shoulder_line": avg[0],
                        "head_forward": max(avg[1], 0.01),
                        "shoulder_hip_height": avg[2],
                        "head_tilt": avg[3]
                    }
                    self.calibrated = True
                    self.calibration_data.clear()
                    print("✅ Posture auto-calibrated!")
            
            # Evaluate posture if calibrated
            if self.calibrated:
                if metrics['shoulder_tilt'] > self.reference["shoulder_line"] * self.SHOULDER_TILT_TOLERANCE:
                    posture_good = False
                if metrics['head_forward'] > self.reference["head_forward"] * self.HEAD_FORWARD_TOLERANCE:
                    posture_good = False
                if metrics['shoulder_hip_height'] < self.reference["shoulder_hip_height"] * self.SLOUCH_TOLERANCE:
                    posture_good = False
                if abs(metrics['head_tilt'] - self.reference["head_tilt"]) > self.HEAD_TILT_TOLERANCE:
                    posture_good = False
            
            # Draw landmarks
            self._draw_landmarks(frame, landmarks)
        
        # Update statistics
        self.total_frames += 1
        if posture_good:
            self.good_posture_frames += 1
        else:
            self.bad_posture_frames += 1
        
        return posture_good, warning
    
    def get_stats(self):
        """Get current posture statistics"""
        elapsed = time.time() - self.start_time
        if self.total_frames > 0:
            good_percent = (self.good_posture_frames / self.total_frames) * 100
            bad_percent = 100 - good_percent
        else:
            good_percent = bad_percent = 0
        
        return {
            'elapsed_time': elapsed,
            'total_frames': self.total_frames,
            'good_frames': self.good_posture_frames,
            'bad_frames': self.bad_posture_frames,
            'good_percent': good_percent,
            'bad_percent': bad_percent,
            'calibrated': self.calibrated,
            'calibration_progress': len(self.calibration_data) if not self.calibrated else self.AUTO_CALIBRATION_FRAMES
        }