import streamlit as st
import cv2
import numpy as np
from posture_detector import PostureDetector
from eye_detector import EyeDetector

st.set_page_config(page_title="Wellness Dashboard", layout="wide")
st.title("🧘 Wellness Assistant Dashboard")

st.markdown(
    """
    Real-time posture and eye detection UI based on your existing modules.
    Calibrate first, then start monitoring.
    """
)

# Sidebar controls
with st.sidebar:
    st.header("Control Panel")
    calibrate = st.button("Calibrate Posture")
    start = st.button("Start Monitoring")
    stop = st.button("Stop Monitoring")
    show_posture = st.checkbox("Show Posture Detection", value=True)
    show_eyes = st.checkbox("Show Eye Detection", value=True)

# Initialize detectors in session state to persist between reruns
if "posture_detector" not in st.session_state:
    st.session_state.posture_detector = PostureDetector()
if "eye_detector" not in st.session_state:
    st.session_state.eye_detector = EyeDetector()

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False
if "calibrating" not in st.session_state:
    st.session_state.calibrating = False

# Use OpenCV webcam capture
cap = cv2.VideoCapture(0)

frame_disp = st.empty()
status_disp = st.empty()

if calibrate:
    st.session_state.calibrating = True
    st.session_state.monitoring = False
    st.session_state.posture_detector.calibrated = False
    st.session_state.posture_detector.calibration_data = []
    st.success("Calibration started. Hold neutral posture and stay centered.")

if start:
    if not st.session_state.posture_detector.calibrated:
        st.warning("Please calibrate before starting monitoring.")
    else:
        st.session_state.monitoring = True
        st.session_state.calibrating = False
        st.success("Monitoring started.")

if stop:
    st.session_state.monitoring = False
    st.info("Monitoring stopped.")

def run_frame_processing(frame):
    if frame is None:
        # Return a blank frame if input is None, to avoid errors
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        return blank, "No Frame", "", ""

    frame = cv2.flip(frame, 1)
    posture_status = ""
    posture_warning = ""
    eyes_status = ""

    if st.session_state.calibrating:
        output = st.session_state.posture_detector.detect_posture(frame)
        if isinstance(output, tuple):
            frame = output[0]
            posture_status = output[-1] if len(output) > 1 else "Calibrating..."
        else:
            posture_status = "Calibrating..."
        cv2.putText(frame, "Calibrating... Please hold neutral posture", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        return frame, posture_status, posture_warning, eyes_status

    if st.session_state.monitoring:
        if show_posture:
            output = st.session_state.posture_detector.detect_posture(frame)
            if isinstance(output, tuple) and len(output) >= 4:
                frame, posture_good, warning, status = output
                posture_status = status
                posture_warning = warning if warning else ""
            else:
                posture_status = "Detecting posture..."
        if show_eyes:
            frame, eyes_open = st.session_state.eye_detector.detect_eyes(frame)
            if eyes_open is not None:
                eyes_status = "Eyes Open" if eyes_open else "Eyes Closed"
            else:
                eyes_status = ""

    else:
        posture_status = "Idle - Start monitoring"

    return frame, posture_status, posture_warning, eyes_status

if cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        st.error("Cannot access webcam")
    else:
        proc_frame, pst_status, pst_warning, eye_status = run_frame_processing(frame)
        if proc_frame is None:
            st.error("No frame to display")
        else:
            proc_frame_rgb = cv2.cvtColor(proc_frame, cv2.COLOR_BGR2RGB)
            frame_disp.image(proc_frame_rgb, channels="RGB")

            status_text = f"**Posture:** {pst_status}"
            if pst_warning != "":
                status_text += f" | ⚠️ Warning: {pst_warning}"
            if eye_status != "":
                status_text += f" | **Eye State:** {eye_status}"

            status_disp.markdown(status_text)
else:
    st.error("Webcam not detected")

# Optional: cleanup, release camera
# cap.release()

# Basic UI styling
st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .css-1d391kg {
            color: #0b3954;
        }
    </style>
""", unsafe_allow_html=True)