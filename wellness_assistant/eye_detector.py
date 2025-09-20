#!/usr/bin/env python3
"""
Eye Detection Module
Detects eye state (open/closed) using MediaPipe face mesh and EAR calculation
"""
import cv2
import mediapipe as mp
import numpy as np
import time


class EyeDetector:
    """Real-time eye state detection with auto-calibration"""
    
    def __init__(self):
        # Initialize MediaPipe face mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Eye landmark indices for EAR calculation
        # These correspond to specific points around the eyes in MediaPipe's face mesh
        self.LEFT_EYE = [[33, 133], [159, 145], [158, 153]]
        self.RIGHT_EYE = [[362, 263], [386, 374], [387, 373]]
        
        # Calibration settings
        self.EAR_THRESHOLD = None
        self.lowest_ear = float("inf")
        self.highest_ear = 0.0
        self.calibrated = False
        
        # Statistics tracking
        self.total_frames = 0
        self.eyes_open_frames = 0
        self.eyes_closed_frames = 0
        self.start_time = time.time()
    
    def reset_calibration(self):
        """Reset eye calibration data"""
        self.EAR_THRESHOLD = None
        self.lowest_ear = float("inf")
        self.highest_ear = 0.0
        self.calibrated = False
    
    def reset_stats(self):
        """Reset eye statistics"""
        self.total_frames = 0
        self.eyes_open_frames = 0
        self.eyes_closed_frames = 0
        self.start_time = time.time()
    
    def set_threshold(self, threshold=None):
        """Manually set EAR threshold or auto-calculate"""
        if threshold is not None:
            self.EAR_THRESHOLD = threshold
            self.calibrated = True
        elif self.highest_ear > 0 and self.lowest_ear < float("inf"):
            self.EAR_THRESHOLD = (self.highest_ear + self.lowest_ear) / 2
            self.calibrated = True
        else:
            self.EAR_THRESHOLD = 0.22  # Default fallback
            self.calibrated = True
    
    def _calculate_ear(self, eye_landmarks, face_landmarks, frame_shape):
        """
        Calculate Eye Aspect Ratio (EAR) for given eye landmarks
        
        EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
        where p1-p6 are eye landmark points
        """
        h, w, _ = frame_shape
        
        try:
            # Get eye landmark coordinates
            points = []
            for landmark_pair in eye_landmarks:
                for landmark_idx in landmark_pair:
                    landmark = face_landmarks[landmark_idx]
                    points.append(np.array([landmark.x * w, landmark.y * h]))
            
            # Calculate EAR using the 6 points
            # Horizontal distance (eye width)
            horizontal_dist = np.linalg.norm(points[0] - points[1])
            
            # Vertical distances (eye height at two positions)
            vertical_dist1 = np.linalg.norm(points[2] - points[3])
            vertical_dist2 = np.linalg.norm(points[4] - points[5])
            
            # Calculate EAR
            if horizontal_dist > 1e-6:
                ear = (vertical_dist1 + vertical_dist2) / (2 * horizontal_dist)
                return ear
            else:
                return None
        except (IndexError, AttributeError):
            return None
    
    def detect_eyes(self, frame, calibrating=False):
        """
        Detect eye state in frame
        
        Args:
            frame: Input image frame
            calibrating: If True, collect calibration data
            
        Returns:
            tuple: (eyes_open: bool, left_ear: float, right_ear: float)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        
        eyes_open = True
        left_ear = None
        right_ear = None
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Calculate EAR for both eyes
                left_ear = self._calculate_ear(
                    self.LEFT_EYE, face_landmarks.landmark, frame.shape
                )
                right_ear = self._calculate_ear(
                    self.RIGHT_EYE, face_landmarks.landmark, frame.shape
                )
                
                if left_ear is not None and right_ear is not None:
                    avg_ear = (left_ear + right_ear) / 2
                    
                    # Update calibration values during calibration phase
                    if calibrating:
                        self.lowest_ear = min(self.lowest_ear, avg_ear)
                        self.highest_ear = max(self.highest_ear, avg_ear)
                    
                    # Determine if eyes are open (only if calibrated and not calibrating)
                    if not calibrating and self.calibrated and self.EAR_THRESHOLD:
                        eyes_open = avg_ear > self.EAR_THRESHOLD
                
                break  # Only process first face
        
        # Update statistics (only when not calibrating and face detected)
        if not calibrating and results.multi_face_landmarks:
            self.total_frames += 1
            if eyes_open:
                self.eyes_open_frames += 1
            else:
                self.eyes_closed_frames += 1
        
        return eyes_open, left_ear, right_ear
    
    def get_average_ear(self, left_ear, right_ear):
        """Calculate average EAR from left and right eyes"""
        if left_ear is not None and right_ear is not None:
            return (left_ear + right_ear) / 2
        return None
    
    def get_calibration_info(self):
        """Get current calibration information"""
        return {
            'threshold': self.EAR_THRESHOLD,
            'lowest_ear': self.lowest_ear if self.lowest_ear != float("inf") else None,
            'highest_ear': self.highest_ear if self.highest_ear > 0 else None,
            'calibrated': self.calibrated,
            'range': self.highest_ear - self.lowest_ear if (
                self.highest_ear > 0 and self.lowest_ear != float("inf")
            ) else None
        }
    
    def get_stats(self):
        """Get current eye statistics"""
        elapsed_time = time.time() - self.start_time
        
        if self.total_frames > 0:
            open_percent = (self.eyes_open_frames / self.total_frames) * 100
            closed_percent = (self.eyes_closed_frames / self.total_frames) * 100
        else:
            open_percent = closed_percent = 0
        
        return {
            'elapsed_time': elapsed_time,
            'total_frames': self.total_frames,
            'open_frames': self.eyes_open_frames,
            'closed_frames': self.eyes_closed_frames,
            'open_percent': open_percent,
            'closed_percent': closed_percent,
            'calibrated': self.calibrated
        }
    
    def draw_eye_landmarks(self, frame, results):
        """Draw eye landmarks on frame (for debugging)"""
        if not results.multi_face_landmarks:
            return
        
        h, w, _ = frame.shape
        
        for face_landmarks in results.multi_face_landmarks:
            # Draw left eye landmarks
            for landmark_pair in self.LEFT_EYE:
                for landmark_idx in landmark_pair:
                    landmark = face_landmarks.landmark[landmark_idx]
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            # Draw right eye landmarks
            for landmark_pair in self.RIGHT_EYE:
                for landmark_idx in landmark_pair:
                    landmark = face_landmarks.landmark[landmark_idx]
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)