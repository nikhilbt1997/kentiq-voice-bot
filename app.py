from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import os
import subprocess
import sys
from tts import speak
from banking import get_balance_amount
from cheque import validate_cheque
from kyc import start_kyc

app = Flask(__name__)
CORS(app)

CURRENT_BALANCE = 15000.00
welcome_played = False

def detect_intent(text):
    text = text.lower().strip()

    transfer_words = ["transfer", "send", "pay", "payment", "beneficiary",
                      "bank name", "account number", "amount", "remit",
                      "wire", "dispatch", "transmit"]
    if any(word in text for word in transfer_words):
        return "transfer"

    balance_words = ["balance", "how much", "funds", "money left",
                     "account balance", "check balance", "my balance",
                     "what is my", "tell me my", "show balance",
                     "how many", "remaining"]
    if any(word in text for word in balance_words):
        return "balance"

    cheque_words = ["cheque", "check", "upload", "scan", "verify cheque",
                    "validate", "chek", "chaque", "chase", "chuck"]
    if any(word in text for word in cheque_words):
        return "cheque"

    kyc_words = ["kyc", "verify", "verification", "identity", "know your",
                 "document", "id proof", "identification", "kvc",
                 "cky", "k y c"]
    if any(word in text for word in kyc_words):
        return "kyc"

    exit_words = ["bye", "exit", "quit", "goodbye", "thank you", "thanks",
                  "close", "stop", "end", "finish", "done"]
    if any(word in text for word in exit_words):
        return "exit"

    if any(word in text for word in ["ball", "bells", "ballance", "balanc"]):
        return "balance"
    if any(word in text for word in ["transf", "trans for"]):
        return "transfer"
    if any(word in text for word in ["kayo", "casey", "kc", "kayak"]):
        return "kyc"

    return "unknown"

def parse_transfer_details(text):
    import re
    text = text.lower()

    beneficiary = ""
    for pattern in [
        r"beneficiary name[:\s]+([a-zA-Z]+)",
        r"beneficiary[:\s]+([a-zA-Z]+)",
        r"rename[:\s]+([a-zA-Z]+)",
        r"recipient[:\s]+([a-zA-Z]+)",
        r"name[:\s]+([a-zA-Z]+)",
        r"send to[:\s]+([a-zA-Z]+)",
        r"transfer to[:\s]+([a-zA-Z]+)",
        r"pay to[:\s]+([a-zA-Z]+)",
    ]:
        match = re.search(pattern, text)
        if match:
            beneficiary = match.group(1).capitalize()
            break

    bank = ""
    for pattern in [
        r"bank name[:\s]+([a-zA-Z]+(?:\s[a-zA-Z]+)?)",
        r"bank[:\s]+([a-zA-Z]+(?:\s[a-zA-Z]+)?)",
        r"at bank[:\s]+([a-zA-Z]+(?:\s[a-zA-Z]+)?)",
    ]:
        match = re.search(pattern, text)
        if match:
            bank = match.group(1).title()
            break

    account = ""
    for pattern in [
        r"account number[:\s]+(\d+)",
        r"account no[:\s]+(\d+)",
        r"acc number[:\s]+(\d+)",
        r"account[:\s]+(\d+)",
    ]:
        match = re.search(pattern, text)
        if match:
            account = f"****{match.group(1)[-4:]}"
            break

    amount = ""
    for pattern in [
        r"amount[:\s]+(\d+)",
        r"(\d+)\s*aed",
        r"(\d+)\s*dirham",
        r"(\d+)\s*rupees",
        r"(\d+)\s*dollars",
    ]:
        match = re.search(pattern, text)
        if match:
            amount = match.group(1)
            break

    if not amount:
        numbers = re.findall(r'\d+', text)
        if numbers:
            amount = numbers[-1]

    return beneficiary, bank, account, amount

def process_intent(intent, text=""):
    global CURRENT_BALANCE

    if intent == "balance":
        msg = f"Your current account balance is {CURRENT_BALANCE:,.2f} AED. Account number ending in 1234."
        speak(msg)
        return msg

    elif intent == "transfer":
        if any(word in text for word in ["beneficiary", "rename", "recipient", "bank name", "account number", "amount", "send to", "transfer to", "pay to"]):
            beneficiary, bank, account, amount_str = parse_transfer_details(text)
            try:
                transfer_amount = float(amount_str)
                if transfer_amount > CURRENT_BALANCE:
                    msg = (f"Transaction declined! Insufficient funds. "
                           f"You tried to transfer {transfer_amount:,.2f} AED "
                           f"but your balance is only {CURRENT_BALANCE:,.2f} AED.")
                    speak(msg)
                    return msg
                if transfer_amount <= 0:
                    msg = "Invalid amount. Please enter a valid amount greater than zero."
                    speak(msg)
                    return msg
                CURRENT_BALANCE -= transfer_amount
                msg = (f"Transfer confirmed! {transfer_amount:,.2f} AED sent to {beneficiary} "
                       f"at {bank}, account {account}. "
                       f"Reference TXN{abs(hash(beneficiary)) % 100000:05d}. "
                       f"Remaining balance is {CURRENT_BALANCE:,.2f} AED.")
                speak(msg)
                return msg
            except:
                msg = "Sorry, could not process the transfer. Please try again."
                speak(msg)
                return msg
        else:
            msg = "Starting money transfer. Please say: beneficiary name, bank name, account number and amount."
            speak(msg)
            return "Starting money transfer. Please use 🎤 Speak and say: beneficiary name, bank name, account number and amount."

    elif intent == "cheque":
        msg = "Please upload your cheque image using the upload button."
        speak(msg)
        return msg

    elif intent == "kyc":
        return "kyc_start"

    elif intent == "exit":
        msg = "Thank you for using Kentiq AI Voice Bot. Goodbye!"
        speak(msg)
        return msg

    else:
        msg = "I can help with balance, transfer, cheque verification, or KYC. What would you like?"
        speak(msg)
        return msg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
    global CURRENT_BALANCE, welcome_played
    CURRENT_BALANCE = 15000.00
    welcome_played = False
    return jsonify({"message": "Reset successful", "balance": CURRENT_BALANCE})

@app.route('/start', methods=['POST'])
def start():
    global welcome_played, CURRENT_BALANCE
    CURRENT_BALANCE = 15000.00
    welcome_played = False
    msg = "Welcome to Kentiq AI Voice Bot from Dubai Bank Bank. How can I help you?"
    speak(msg)
    return jsonify({"message": msg, "status": "ready"})

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    text = data.get('text', '').lower()
    intent = detect_intent(text)
    response = process_intent(intent, text)
    return jsonify({"text": text, "response": response, "intent": intent})

@app.route('/kyc_instruction', methods=['POST'])
def kyc_instruction():
    from tts import wait_for_tts
    import numpy as np
    import sounddevice as sd
    speak("Please say your full name and date of birth after the beep.")
    wait_for_tts()
    sample_rate = 44100
    t = np.linspace(0, 0.3, int(sample_rate * 0.3))
    beep = (np.sin(2 * np.pi * 880 * t) * 32767).astype(np.int16)
    sd.play(beep, sample_rate)
    sd.wait()
    return jsonify({"message": "Please say your full name and date of birth after the beep."})

@app.route('/kyc_start', methods=['POST'])
def kyc_start():
    import wave
    import cv2
    import time
    import speech_recognition as sr
    from datetime import datetime
    from tts import wait_for_tts

    try:
        if 'audio' not in request.files:
            return jsonify({"status": "error", "message": "No audio received."})

        audio_file = request.files['audio']
        os.makedirs('uploads', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        tmp_webm = f"uploads/kyc_temp_{timestamp}.webm"
        audio_file.save(tmp_webm)

        audio_filename = f"uploads/kyc_audio_{timestamp}.wav"
        result = subprocess.run([
            'ffmpeg', '-i', tmp_webm,
            '-ar', '16000', '-ac', '1',
            '-y', audio_filename
        ], capture_output=True, timeout=15)

        try:
            os.unlink(tmp_webm)
        except:
            pass

        if result.returncode != 0:
            return jsonify({"status": "error", "message": "Audio conversion failed."})

        speak("Thank you. Processing your details.")
        wait_for_tts()

        spoken_text = ""
        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_filename) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.record(source)
            spoken_text = recognizer.recognize_google(audio)
            print(f"KYC spoken: {spoken_text}")
            speak(f"I heard: {spoken_text}. Details recorded.")
            wait_for_tts()
        except sr.UnknownValueError:
            spoken_text = "Audio saved — could not transcribe clearly"
            speak("Audio saved. Could not transcribe clearly.")
            wait_for_tts()
        except Exception as e:
            print(f"Recognition error: {e}")
            spoken_text = "Audio saved"
            speak("Audio saved successfully.")
            wait_for_tts()

        speak("Please look at the camera.")
        wait_for_tts()
        time.sleep(1)

        cap = cv2.VideoCapture(0)
        photo_saved = False

        if cap.isOpened():
            for _ in range(5):
                cap.read()
            ret, frame = cap.read()
            if ret:
                photo_filename = f"uploads/kyc_photo_{timestamp}.jpg"
                cv2.imwrite(photo_filename, frame)
                photo_saved = True
                speak("Photo captured.")
                wait_for_tts()
            cap.release()
        else:
            speak("Camera not available.")
            wait_for_tts()

        ref = abs(hash(timestamp)) % 100000
        speak(f"K Y C completed. Reference K Y C {ref:05d}. Thank you.")
        wait_for_tts()

        return jsonify({
            "status": "complete",
            "message": f"KYC completed! Reference: KYC{ref:05d}",
            "spoken_text": spoken_text,
            "audio_saved": True,
            "photo_saved": photo_saved,
            "reference": f"KYC{ref:05d}",
            "timestamp": timestamp
        })

    except Exception as e:
        print(f"KYC error: {e}")
        speak("KYC error. Please try again.")
        return jsonify({"status": "error", "message": f"KYC error: {str(e)}"})

@app.route('/speech', methods=['POST'])
def speech_route():
    import tempfile
    import speech_recognition as sr

    tmp_path = None
    wav_path = None
    try:
        if 'audio' not in request.files:
            return jsonify({"text": "", "response": "No audio received.", "intent": "error"})

        audio_file = request.files['audio']
        tmp = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        tmp_path = tmp.name
        tmp.close()
        audio_file.save(tmp_path)

        wav_path = tmp_path.replace('.webm', '.wav')
        result = subprocess.run([
            'ffmpeg', '-i', tmp_path,
            '-ar', '16000', '-ac', '1',
            '-y', wav_path
        ], capture_output=True, timeout=15)

        if result.returncode != 0:
            return jsonify({"text": "", "response": "Audio conversion failed.", "intent": "error"})

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        print(f"Recognized: {text}")
        intent = detect_intent(text.lower())
        response = process_intent(intent, text.lower())

        if response == "kyc_start":
            return jsonify({"text": text, "response": "kyc_start", "intent": "kyc", "status": "success"})

        return jsonify({"text": text, "response": response, "intent": intent, "status": "success"})

    except sr.UnknownValueError:
        speak("Sorry, I didn't understand. Please repeat.")
        return jsonify({"text": "", "response": "Sorry, I didn't understand. Please repeat.", "intent": "error"})
    except sr.RequestError:
        return jsonify({"text": "", "response": "Speech service error. Please try again.", "intent": "error"})
    except Exception as e:
        print(f"Speech error: {e}")
        return jsonify({"text": "", "response": f"Error: {str(e)}", "intent": "error"})
    finally:
        for p in [tmp_path, wav_path]:
            if p and os.path.exists(p):
                try:
                    os.unlink(p)
                except:
                    pass

@app.route('/upload_cheque', methods=['POST'])
def upload_cheque():
    if 'file' not in request.files:
        return jsonify({"message": "❌ No file uploaded.", "valid": False})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "❌ No file selected.", "valid": False})
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)
    valid, message = validate_cheque(filepath)
    return jsonify({"message": message, "valid": valid})

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    print(f"Starting Kentiq AI Voice Bot... Balance: {CURRENT_BALANCE} AED")
    app.run(debug=False, port=5000)