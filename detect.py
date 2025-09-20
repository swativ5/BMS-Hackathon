import sounddevice as sd
import numpy as np
import time

# === CONFIGURATION ===
CALIBRATION_DURATION = 5   # seconds to measure average amplitude
SAMPLE_RATE = 44100
CHANNELS = 1
WINDOW_DURATION = 0.2      # seconds per detection window
THRESHOLD_MULTIPLIER = 1.2 # 20% above average = exhaling

# === PHASE 1: CALIBRATION ===
print(f"🎤 Calibrating for {CALIBRATION_DURATION} seconds... Breathe normally.")
calibration = sd.rec(int(CALIBRATION_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
sd.wait()

calibration_data = calibration.flatten()
calibration_amp = np.abs(calibration_data)

calibration_avg = np.mean(calibration_amp)
threshold = calibration_avg * THRESHOLD_MULTIPLIER

print("\nCalibration complete.")
print(f" Average amplitude: {calibration_avg:.6f}")
print(f" Threshold (Exhaling > this): {threshold:.6f}\n")

# === PHASE 2: LIVE DETECTION ===
print(" Live detection started. Press Ctrl+C to stop.\n")

window_size = int(SAMPLE_RATE * WINDOW_DURATION)

try:
    while True:
        # Record a short window
        window = sd.rec(window_size, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
        sd.wait()

        # Compute average amplitude
        amp = np.abs(window.flatten())
        avg_amp = np.mean(amp)

        # Classify
        if avg_amp > threshold:
            print(f" Exhaling (avg={avg_amp:.6f})")
        else:
            print(f" Inhaling (avg={avg_amp:.6f})")

        time.sleep(0.01)  # small pause to avoid CPU overuse

except KeyboardInterrupt:
    print("\n Stopped by user.")
