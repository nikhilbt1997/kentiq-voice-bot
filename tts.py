import pyttsx3
import threading

_lock = threading.Lock()
_speaking = False

def speak(text):
    global _speaking
    print(f"Bot: {text}")
    _speaking = True
    def _run():
        global _speaking
        with _lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1.0)
                engine.say(str(text))
                engine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")
            finally:
                _speaking = False
    t = threading.Thread(target=_run, daemon=True)
    t.start()
    # Do NOT join — return immediately so response goes to frontend fast

def wait_for_tts():
    import time
    global _speaking
    while _speaking:
        time.sleep(0.1)
    time.sleep(0.3)