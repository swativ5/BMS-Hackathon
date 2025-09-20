#!/usr/bin/env python3
"""
Real Eye Detection Test Script (Auto-Calibrated)
Uses OpenCV and MediaPipe to detect open/closed eyes from laptop camera
"""

import cv2
import mediapipe as mp
import numpy as np
import time

class EyeDetector:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Eye landmark indices for EAR (MediaPipe FaceMesh 468 landmarks)
        self.LEFT_EYE = [
            [33, 133],   # Horizontal (corners)
            [159, 145],  # Vertical upper-lower
            [158, 153],  # Vertical upper-lower (side)
        ]

        self.RIGHT_EYE = [
            [362, 263],  # Horizontal (corners)
            [386, 374],  # Vertical upper-lower
            [387, 373],  # Vertical upper-lower (side)
        ]

        # Threshold for detecting closed eyes (will be calibrated)
        self.EAR_THRESHOLD = None  
        self.CLOSED_EYE_FRAME_THRESHOLD = 2

        # Stats
        self.total_frames = 0
        self.eyes_open_frames = 0
        self.eyes_closed_frames = 0
        self.start_time = time.time()

        # Track EAR extremes
        self.lowest_ear = float("inf")
        self.highest_ear = 0.0
        self.lowest_left_ear = float("inf")
        self.lowest_right_ear = float("inf")

    def calculate_ear(self, eye_points, landmarks, frame_shape):
        """Calculate Eye Aspect Ratio using pixel coords"""
        h, w, _ = frame_shape
        try:
            p1 = np.array([landmarks[eye_points[0][0]].x * w,
                           landmarks[eye_points[0][0]].y * h])
            p4 = np.array([landmarks[eye_points[0][1]].x * w,
                           landmarks[eye_points[0][1]].y * h])

            p2 = np.array([landmarks[eye_points[1][0]].x * w,
                           landmarks[eye_points[1][0]].y * h])
            p6 = np.array([landmarks[eye_points[1][1]].x * w,
                           landmarks[eye_points[1][1]].y * h])

            p3 = np.array([landmarks[eye_points[2][0]].x * w,
                           landmarks[eye_points[2][0]].y * h])
            p5 = np.array([landmarks[eye_points[2][1]].x * w,
                           landmarks[eye_points[2][1]].y * h])

            # Compute distances
            v1 = np.linalg.norm(p2 - p6)
            v2 = np.linalg.norm(p3 - p5)
            hdist = np.linalg.norm(p1 - p4)

            if hdist > 1e-6:
                ear = (v1 + v2) / (2.0 * hdist)
                return ear
            return None

        except Exception:
            return None

    def detect_eyes(self, frame, calibrating=False):
        """Detect if eyes are open or closed"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        left_ear, right_ear = None, None
        eyes_open = True

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                left_ear = self.calculate_ear(self.LEFT_EYE, face_landmarks.landmark, frame.shape)
                right_ear = self.calculate_ear(self.RIGHT_EYE, face_landmarks.landmark, frame.shape)

                if left_ear is not None and right_ear is not None:
                    avg_ear = (left_ear + right_ear) / 2.0

                    # Update EAR extremes
                    self.lowest_ear = min(self.lowest_ear, avg_ear)
                    self.highest_ear = max(self.highest_ear, avg_ear)
                    self.lowest_left_ear = min(self.lowest_left_ear, left_ear)
                    self.lowest_right_ear = min(self.lowest_right_ear, right_ear)

                    # During calibration, we don't decide open/closed yet
                    if not calibrating and self.EAR_THRESHOLD is not None:
                        eyes_open = avg_ear > self.EAR_THRESHOLD

        # Update counters only after calibration
        if not calibrating and self.EAR_THRESHOLD is not None:
            self.total_frames += 1
            if eyes_open:
                self.eyes_open_frames += 1
            else:
                self.eyes_closed_frames += 1

        return eyes_open, left_ear, right_ear

    def get_statistics(self):
        elapsed_time = time.time() - self.start_time
        open_percentage = (self.eyes_open_frames / max(self.total_frames, 1)) * 100
        closed_percentage = (self.eyes_closed_frames / max(self.total_frames, 1)) * 100
        return {
            'elapsed_time': elapsed_time,
            'total_frames': self.total_frames,
            'eyes_open_frames': self.eyes_open_frames,
            'eyes_closed_frames': self.eyes_closed_frames,
            'open_percentage': open_percentage,
            'closed_percentage': closed_percentage,
            'lowest_ear': self.lowest_ear if self.lowest_ear != float("inf") else None,
            'highest_ear': self.highest_ear,
            'lowest_left_ear': self.lowest_left_ear if self.lowest_left_ear != float("inf") else None,
            'lowest_right_ear': self.lowest_right_ear if self.lowest_right_ear != float("inf") else None,
            'ear_threshold': self.EAR_THRESHOLD
        }

def main():
    print("Eye Detection Test Script")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    eye_detector = EyeDetector()

    # --- Calibration phase ---
    print("Calibration for 5 seconds... Please keep eyes open, then blink once or twice.")
    calibration_start = time.time()
    while time.time() - calibration_start < 5:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        eye_detector.detect_eyes(frame, calibrating=True)

        cv2.putText(frame, "Calibrating... Keep eyes open & blink", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.imshow('Eye Detection Test', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    # Set dynamic threshold
    if eye_detector.highest_ear > 0 and eye_detector.lowest_ear < float("inf"):
        eye_detector.EAR_THRESHOLD = (eye_detector.highest_ear + eye_detector.lowest_ear) / 2
    else:
        eye_detector.EAR_THRESHOLD = 0.22  # fallback

    print(f"Calibration complete. EAR Threshold set to {eye_detector.EAR_THRESHOLD:.3f}")
    print("Eye detection started!")

    # --- Detection phase ---
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)

            eyes_open, left_ear, right_ear = eye_detector.detect_eyes(frame)

            status_text = "EYES OPEN" if eyes_open else "EYES CLOSED"
            status_color = (0, 255, 0) if eyes_open else (0, 0, 255)
            cv2.putText(frame, status_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)

            if left_ear is not None and right_ear is not None:
                avg_ear = (left_ear + right_ear) / 2.0
                cv2.putText(frame, f"Left EAR: {left_ear:.3f}", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, f"Right EAR: {right_ear:.3f}", (10, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, f"Avg EAR: {avg_ear:.3f} (Threshold: {eye_detector.EAR_THRESHOLD:.3f})",
                            (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

            stats = eye_detector.get_statistics()
            cv2.putText(frame, f"Open: {stats['open_percentage']:.1f}% | Closed: {stats['closed_percentage']:.1f}%",
                        (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            if stats['lowest_ear'] is not None:
                cv2.putText(frame, f"Lowest EAR: {stats['lowest_ear']:.3f} | Highest: {stats['highest_ear']:.3f}",
                            (10, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            cv2.imshow('Eye Detection Test', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                print("\nCurrent Statistics:")
                print(eye_detector.get_statistics())

    finally:
        stats = eye_detector.get_statistics()
        print("\nFinal Statistics:")
        print(stats)
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
