#!/usr/bin/env python3
"""
Speech Engine Module
Handles text-to-speech functionality with threading support
"""
import pyttsx3
import threading
from queue import Queue, Empty


class SpeechEngine:
    """Thread-safe text-to-speech engine"""
    
    def __init__(self, rate=140):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.speech_queue = Queue()
        self.speaking_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speaking_thread.start()
        self._setup_voice()
    
    def _setup_voice(self):
        """Try to set a female voice if available"""
        try:
            voices = self.engine.getProperty("voices")
            for voice in voices:
                if "female" in voice.name.lower() or "zira" in voice.name.lower():
                    self.engine.setProperty("voice", voice.id)
                    break
        except Exception as e:
            print(f"Warning: Could not set voice preference: {e}")
    
    def speak(self, text):
        """Add text to speech queue (non-blocking)"""
        self.speech_queue.put(text)
    
    def speak_sync(self, text):
        """Speak text synchronously (blocking)"""
        self.engine.say(text)
        self.engine.runAndWait()
    
    def _speech_worker(self):
        """Background worker thread for speech processing"""
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                self.engine.say(text)
                self.engine.runAndWait()
                self.speech_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                print(f"Speech engine error: {e}")
    
    def clear_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except Empty:
                break
    
    def stop(self):
        """Stop the speech engine"""
        try:
            self.engine.stop()
        except:
            pass


# Global instance for easy importing
_global_engine = None

def get_speech_engine():
    """Get global speech engine instance"""
    global _global_engine
    if _global_engine is None:
        _global_engine = SpeechEngine()
    return _global_engine

def speak(text):
    """Convenience function for quick speech"""
    get_speech_engine().speak(text)

def speak_sync(text):
    """Convenience function for synchronous speech"""
    get_speech_engine().speak_sync(text)