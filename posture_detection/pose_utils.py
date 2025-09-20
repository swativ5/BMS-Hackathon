import mediapipe as mp

mp_pose = mp.solutions.pose

def check_spinal_alignment(frame):
    with mp_pose.Pose(static_image_mode=False) as pose:
        results = pose.process(frame)
        if results.pose_landmarks:
            left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            # Simple heuristic: shoulders should be nearly at same y-level
            return abs(left_shoulder.y - right_shoulder.y) < 0.05
    return False