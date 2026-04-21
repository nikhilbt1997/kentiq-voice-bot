import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

voices = engine.getProperty('voices')
for voice in voices:
    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

def speak(text):
    print(f"Bot: {text}")
    engine.say(text)
    engine.runAndWait()

def listen(timeout=6, phrase_limit=8):
    """Record audio using sounddevice and recognize using SpeechRecognition"""
    try:
        sample_rate = 16000
        duration = phrase_limit

        print("Recording...")
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        print("Recording done.")

        # Save to temp wav file
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        with wave.open(tmp.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())

        # Recognize using Google
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp.name) as source:
            audio = recognizer.record(source)

        os.unlink(tmp.name)
        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        return text.lower()

    except sr.UnknownValueError:
        return "unclear"
    except sr.RequestError:
        return "error"
    except Exception as e:
        print(f"Listen error: {e}")
        return "error"

def welcome():
    speak("Welcome to Kentiq AI Voice Bot from Dubai Bank Bank. How can I help you?")