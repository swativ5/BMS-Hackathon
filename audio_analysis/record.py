import sounddevice as sd
import numpy as np
import wave

def record_om(filename="om_chant.wav", duration=10, fs=44100):
    print("Start chanting Om!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wave.write(filename, recording.tobytes())
    print("Recording saved to", filename)