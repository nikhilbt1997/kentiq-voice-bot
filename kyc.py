import sounddevice as sd
import numpy as np
import wave
import os
import cv2
from tts import speak
from datetime import datetime

def start_kyc():
    try:
        speak("Starting KYC verification. Please follow the instructions.")

        # Step 1 - Record audio
        speak("I will now record a short audio clip for verification. Please say your full name and date of birth.")
        speak("Recording starts now. Go ahead.")

        sample_rate = 44100
        duration = 6
        print("Recording KYC audio...")

        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        print("Audio recording done.")

        # Save audio
        os.makedirs('uploads', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"uploads/kyc_audio_{timestamp}.wav"

        with wave.open(audio_filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(recording.tobytes())

        print(f"Audio saved: {audio_filename}")
        speak("Audio recorded and saved successfully.")

        # Step 2 - Capture photo
        speak("Now I will capture your photo for identity verification. Please look at the camera.")

        import time
        time.sleep(1)

        cap = cv2.VideoCapture(0)
        photo_saved = False

        if cap.isOpened():
            # Warm up camera
            for _ in range(5):
                cap.read()

            ret, frame = cap.read()
            if ret:
                photo_filename = f"uploads/kyc_photo_{timestamp}.jpg"
                cv2.imwrite(photo_filename, frame)
                print(f"Photo saved: {photo_filename}")
                photo_saved = True
                speak("Photo captured and saved successfully.")
            else:
                speak("Could not capture photo. Please ensure camera is connected.")
            cap.release()
        else:
            speak("Camera not available. Proceeding with audio verification only.")

        # Step 3 - Confirm completion
        ref = abs(hash(timestamp)) % 100000
        if photo_saved:
            speak(f"KYC completed successfully. Both audio and photo have been recorded and saved locally. "
                  f"Your verification reference number is K Y C {ref:05d}. Thank you.")
        else:
            speak(f"KYC partially completed. Audio has been recorded and saved. "
                  f"Your verification reference number is K Y C {ref:05d}. Thank you.")

        print(f"KYC complete. Reference: KYC{ref:05d}")

    except Exception as e:
        print(f"KYC error: {e}")
        speak("An error occurred during KYC verification. Please try again.")