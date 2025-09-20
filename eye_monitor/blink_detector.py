import mediapipe as mp

mp_face = mp.solutions.face_mesh

def detect_eyes_open(frame):
    with mp_face.FaceMesh(static_image_mode=False) as face_mesh:
        results = face_mesh.process(frame)
        # Naive: if landmarks for eyes detected, assume eyes are open
        return bool(results.multi_face_landmarks)