import audioread

def get_audio_length(filename="om_chant.wav"):
    with audioread.audio_open(filename) as f:
        return int(f.duration)