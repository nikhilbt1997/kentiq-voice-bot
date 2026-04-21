import cv2
import numpy as np
from tts import speak

def validate_cheque(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            speak("Sorry, could not read the image. Please upload a valid image file.")
            return False, "❌ Could not read image."

        height, width = img.shape[:2]

        if width < 200 or height < 100:
            speak("Invalid image. Image is too small.")
            return False, "❌ Invalid image. Too small."

        aspect_ratio = width / height
        if aspect_ratio < 1.5:
            speak("Invalid cheque. Image does not match cheque format.")
            return False, "❌ Invalid image. Does not match cheque format."

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi/180,
            threshold=80,
            minLineLength=width * 0.2,
            maxLineGap=10
        )

        if lines is None or len(lines) < 2:
            speak("Invalid cheque. Could not detect cheque lines.")
            return False, "❌ Invalid cheque. Could not detect required lines."

        speak("Cheque validated successfully. Your cheque has been accepted and is being processed.")
        return True, "✅ Cheque validated successfully! Your cheque is being processed."

    except Exception as e:
        print(f"Cheque error: {e}")
        speak("An error occurred while validating the cheque.")
        return False, "❌ Validation error. Please try again."