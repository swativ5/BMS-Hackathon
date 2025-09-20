import mediapipe as mp

mp_pose = mp.solutions.pose

def check_head_neck(frame):
    with mp_pose.Pose(static_image_mode=False) as pose:
        results = pose.process(frame)
        if results.pose_landmarks:
            nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            neck = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            # Heuristic: head (nose) above neck (shoulder)
            return nose.y < neck.y
    return False