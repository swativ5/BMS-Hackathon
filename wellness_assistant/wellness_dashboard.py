import streamlit as st
import cv2
import numpy as np
import time
from posture_detector import PostureDetector
from eye_detector import EyeDetector


# Pink theme CSS styling
st.markdown("""
<style>
    .main {
        background-color: #fff0f6;
    }
    .stButton>button {
        background-color: #d6336c !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 0.5em 1.5em !important;
        font-size: 1em !important;
    }
    .stButton>button:hover {
        background-color: #a72653 !important;
    }
    .stSidebar {
        background-color: #ffe6f0;
    }
    .big-title {
        font-size: 2.8em;
        font-weight: 900;
        color: #b83265;
        margin-bottom: 0.2em;
    }
    .info-card {
        background: #ffd6e8;
        border-radius: 14px;
        padding: 1.5em;
        margin-bottom: 1em;
        color: #7a2a53;
        font-weight: 600;
        font-size: 1.1em;
    }
    .status-good {
        color: #2f7748;
        font-weight: 700;
    }
    .status-bad {
        color: #b83265;
        font-weight: 700;
    }
    .status-warning {
        color: #d98575;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# Page config and app title
st.set_page_config(page_title="Wellness Assistant", layout="wide")
st.markdown('<div class="big-title">🧘 Wellness Assistant Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    """<div class="info-card">
        Welcome! Start by calibrating your posture, then monitor your posture and eye states live.<br>
        Ensure good lighting and position yourself facing the camera for the best results.
    </div>""", unsafe_allow_html=True
)


# Sidebar controls for app
with st.sidebar:
    st.header("🛠️ Controls")
    calibrate_btn = st.button("🔧 Calibrate Posture")
    start_btn = st.button("▶️ Start Monitoring")
    stop_btn = st.button("■ Stop Monitoring")
    st.markdown("---")
    show_posture = st.checkbox("Show Posture Detection", True)
    show_eyes = st.checkbox("Show Eye Detection", True)
    st.markdown("---")
    st.info("Tip: Full frontal face and even lighting improve accuracy.")


# Initialize detector instances using session state 
if "posture_detector" not in st.session_state:
    st.session_state.posture_detector = PostureDetector()
if "eye_detector" not in st.session_state:
    st.session_state.eye_detector = EyeDetector()


# Initialize states
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False
if "calibrating" not in st.session_state:
    st.session_state.calibrating = False


# Placeholders for video and text status
frame_placeholder = st.empty()
status_placeholder = st.empty()
feedback_placeholder = st.empty()


# Handle control button clicks
if calibrate_btn:
    st.session_state.calibrating = True
    st.session_state.monitoring = False
    st.session_state.posture_detector.calibrated = False
    st.session_state.posture_detector.calibration_data = []
    st.success("Calibration started: Hold a neutral posture and remain centered.")


if start_btn:
    if not st.session_state.posture_detector.calibrated:
        st.warning("Calibration required before monitoring.")
    else:
        st.session_state.monitoring = True
        st.session_state.calibrating = False
        st.success("Monitoring started.")


if stop_btn:
    st.session_state.monitoring = False
    st.session_state.calibrating = False
    st.info("Monitoring stopped.")


def process_frame(frame):
    # Fallback to black frame if invalid frame
    if frame is None or isinstance(frame, bool):
        return np.zeros((480, 640, 3), dtype=np.uint8), "No frame", "", ""

    frame = cv2.flip(frame, 1)
    posture_status = ""
    posture_warning = ""
    eye_status = ""

    if st.session_state.calibrating:
        output = st.session_state.posture_detector.detect_posture(frame)
        if isinstance(output, tuple):
            frame = output[0]
            posture_status = output[-1] if len(output) > 1 else "Calibrating..."
        else:
            posture_status = "Calibrating..."
        cv2.putText(frame, "Calibrating... Hold neutral posture", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 150, 150), 2)
        return frame, posture_status, posture_warning, eye_status

    if st.session_state.monitoring:
        if show_posture:
            output = st.session_state.posture_detector.detect_posture(frame)
            if isinstance(output, tuple) and len(output) >= 4:
                frame, posture_good, warning, status = output
                posture_status = status
                posture_warning = warning or ""
            else:
                posture_status = "Detecting posture..."
        if show_eyes:
            frame, eyes_open = st.session_state.eye_detector.detect_eyes(frame)
            if eyes_open is not None:
                eye_status = "Eyes Open" if eyes_open else "Eyes Closed"
            else:
                eye_status = ""
    else:
        posture_status = "Idle - Please start monitoring."

    return frame, posture_status, posture_warning, eye_status


def webcam_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        status_placeholder.error("Cannot open webcam.")
        return

    try:
        while st.session_state.calibrating or st.session_state.monitoring:
            ret, frame = cap.read()
            if not ret or frame is None:
                status_placeholder.error("No valid frame received from webcam.")
                break

            proc_frame, pst_status, pst_warn, eyes_stat = process_frame(frame)

            # Safety checks on proc_frame
            if proc_frame is None or not isinstance(proc_frame, np.ndarray):
                status_placeholder.error("Invalid frame format returned by detection")
                break

            if proc_frame.dtype != np.uint8:
                proc_frame = np.clip(proc_frame, 0, 255).astype(np.uint8)

            proc_frame_rgb = cv2.cvtColor(proc_frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(proc_frame_rgb, channels="RGB", use_column_width=True)

            pst_color = (
                "status-good" if "Good" in pst_status else
                "status-warning" if "Calibrating" in pst_status or pst_warn else
                "status-bad"
            )

            status_html = f'<span class="{pst_color}">Posture: {pst_status}</span>'
            if pst_warn:
                status_html = f'<span class="status-warning">⚠️ {pst_warn}</span> | ' + status_html
            if eyes_stat:
                eye_color = "status-good" if eyes_stat == "Eyes Open" else "status-bad"
                status_html += f' | <span class="{eye_color}">Eye State: {eyes_stat}</span>'

            status_placeholder.markdown(f"<div style='font-size:1.2em'>{status_html}</div>", unsafe_allow_html=True)

            if pst_warn or eyes_stat == "Eyes Closed":
                feedback_placeholder.markdown(f"""
                <div class="info-card" style="background:#f8d7da; color:#842029;">
                    <b>⚠️ Attention:</b> {pst_warn or ''} {'Please open your eyes.' if eyes_stat == 'Eyes Closed' else ''}
                </div>
                """, unsafe_allow_html=True)
            elif "Good" in pst_status and eyes_stat == "Eyes Open":
                feedback_placeholder.markdown(f"""
                <div class="info-card" style="background:#d1e7dd; color:#0f5132;">
                    <b>✅ Great posture and alert!</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                feedback_placeholder.empty()

            time.sleep(0.05)  # ~20 FPS

    finally:
        cap.release()


# Run webcam loop if monitoring or calibrating active
if st.session_state.calibrating or st.session_state.monitoring:
    webcam_loop()
else:
    frame_placeholder.image(np.zeros((480, 640, 3), np.uint8), channels="RGB")
    status_placeholder.markdown(
        "<div style='color:#6c757d; font-size:1.1em;'>Click <b>Calibrate Posture</b> or <b>Start Monitoring</b> to begin.</div>",
        unsafe_allow_html=True,
    )
    feedback_placeholder.empty()


st.markdown("""
<hr>
<div style="text-align:center; color:#b83265; font-weight:bold; font-size:0.9em; margin-top:1em;">
    Wellness Assistant &copy; 2025 | Built with ❤️ using Streamlit, OpenCV, MediaPipe
</div>
""", unsafe_allow_html=True)