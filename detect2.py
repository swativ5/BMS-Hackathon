import sounddevice as sd
import numpy as np
import time

# === CONFIGURATION ===
CALIBRATION_DURATION = 5
SAMPLE_RATE = 44100
CHANNELS = 1
WINDOW_DURATION = 0.1
THRESHOLD_MULTIPLIER = 1.2
EXPECTED_CYCLES = 10

# Expected pattern: I,I,I,I,E,E,I(1s),E(2s)
EXPECTED_SEQUENCE = [
    ("I", None), ("I", None), ("I", None), ("I", None), 
    ("E", None), ("E", None),
    ("I", 1.0), ("E", 2.0)
]

# === PHASE 1: CALIBRATION ===
print(f"🎤 Calibrating for {CALIBRATION_DURATION} seconds... Breathe normally.")
calibration = sd.rec(int(CALIBRATION_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
sd.wait()

calibration_data = calibration.flatten()
calibration_amp = np.abs(calibration_data)
calibration_avg = np.mean(calibration_amp)
threshold = calibration_avg * THRESHOLD_MULTIPLIER

print("\n✅ Calibration complete.")
print(f"📊 Average amplitude: {calibration_avg:.6f}")
print(f"📊 Threshold: {threshold:.6f}\n")

# === PHASE 2: PATTERN DETECTION ===
print(f"🔴 Live detection started. Target: {EXPECTED_CYCLES} cycles.")
print("Press Ctrl+C to stop early.\n")

window_size = int(SAMPLE_RATE * WINDOW_DURATION)

detected_sequence = []
cycle_count = 0
start_time = None
current_state = None
state_start_time = None

def classify_window(avg_amp):
    return "E" if avg_amp > threshold else "I"

try:
    while cycle_count < EXPECTED_CYCLES:
        window = sd.rec(window_size, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
        sd.wait()
        amp = np.abs(window.flatten())
        avg_amp = np.mean(amp)
        state = classify_window(avg_amp)

        now = time.time()
        if current_state != state:
            # state change detected
            if current_state is not None:
                duration = now - state_start_time
                detected_sequence.append((current_state, duration))

                # Check if we've collected a full cycle
                if len(detected_sequence) >= len(EXPECTED_SEQUENCE):
                    cycle = detected_sequence[:len(EXPECTED_SEQUENCE)]
                    detected_sequence = detected_sequence[len(EXPECTED_SEQUENCE):]
                    cycle_count += 1

                    # Evaluate accuracy
                    correct_steps = 0
                    for (det, dur), (exp, exp_dur) in zip(cycle, EXPECTED_SEQUENCE):
                        if det == exp:
                            if exp_dur is None:
                                correct_steps += 1
                            else:
                                # Check duration tolerance (±20%)
                                if abs(dur - exp_dur) <= exp_dur * 0.2:
                                    correct_steps += 1
                    accuracy = (correct_steps / len(EXPECTED_SEQUENCE)) * 100
                    print(f"Cycle {cycle_count}/{EXPECTED_CYCLES}: Accuracy = {accuracy:.1f}%")

            # update current state
            current_state = state
            state_start_time = now

except KeyboardInterrupt:
    print("\n🛑 Stopped early by user.")

print("\n Done.")