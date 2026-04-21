# Kentiq AI Voice Banking Assistant
## Dubai Bank — Avyukta Intellicall Assignment

---

## Project Overview
Kentiq AI Voice Bot is a voice-enabled AI banking assistant built for Dubai Bank. It accepts voice input from users, processes banking commands using NLP and speech recognition, and responds via text-to-speech. The system simulates real banking operations using dummy data and mock workflows.

---

## Tech Stack
| Component | Technology |
|-----------|-----------|
| Backend | Python 3.14, Flask |
| Speech to Text | Google Speech Recognition (SpeechRecognition library) |
| Text to Speech | pyttsx3 |
| Audio Recording | Browser WebRTC (MediaRecorder API) |
| Audio Processing | FFmpeg (webm to wav conversion) |
| Image Validation | OpenCV (cv2) |
| Frontend | HTML5, CSS3, JavaScript |
| KYC Photo Capture | OpenCV (cv2 VideoCapture) |

---

## Features Implemented

### 1. Voice Interaction
- Browser microphone access via WebRTC
- Auto silence detection — stops recording when user stops speaking
- Speech to text via Google Speech Recognition API
- Text to speech via pyttsx3

### 2. Mandatory Welcome Message
On first interaction the bot speaks exactly:
"Welcome to Kentiq AI Voice Bot from Dubai Bank Bank. How can I help you?"

### 3. Account Balance Inquiry
- Detects voice queries related to account balance
- Responds with dummy balance (15,000 AED) via voice and display
- Balance updates after each transfer

### 4. Money Transfer Workflow
- Step by step voice conversation
- Collects: beneficiary name, bank name, account number, amount
- Confirms transfer via voice
- Deducts from balance and shows remaining balance
- Declines if insufficient funds

### 5. Cheque Verification
- Voice triggered upload flow
- Validates cheque using OpenCV image analysis
- Checks aspect ratio, minimum size, horizontal lines
- Accepts valid cheque images
- Rejects invalid images with voice feedback

### 6. Voice KYC
- Browser mic records user voice
- User says full name and date of birth
- Audio saved locally as WAV file
- Photo captured via webcam and saved locally
- Completion confirmed via voice with reference number

### 7. Error Handling
- Unclear speech → "Sorry, I didn't understand. Please repeat."
- No speech detected → "No speech detected. Please try again."
- Unknown command → "I can help with balance, transfer, cheque, or KYC."
- Insufficient funds → "Transaction declined! Insufficient funds."
- Invalid cheque → "Invalid image. Does not match cheque format."

---

## Project Structure
kentiq-voice-bot/
├── app.py              — Flask backend, all routes and intent logic
├── tts.py              — Text to speech engine
├── banking.py          — Banking helper functions
├── cheque.py           — OpenCV cheque validation
├── kyc.py              — KYC helper
├── templates/
│   └── index.html      — Frontend UI with WebRTC mic
├── static/
│   └── style.css       — Styling
└── uploads/            — KYC audio and photo files saved here

---

## How to Run

### Prerequisites
```bash
pip install flask flask-cors SpeechRecognition pyttsx3 sounddevice numpy opencv-python
winget install ffmpeg
```

### Start the server
```bash
python app.py
```

### Open in browser
http://localhost:5000

---

## Test Credentials / Demo Flow
1. Click **▶ Start** — welcome message plays
2. Click **💰 Balance** — shows 15,000 AED
3. Click **💸 Transfer** — then click 🎤 and say:
   > "beneficiary name John bank name Emirates account number 1234 amount 5000"
4. Click **💰 Balance** again — shows 10,000 AED
5. Click **📄 Cheque** — upload a wide landscape image
6. Click **🪪 KYC** — speak your name and DOB after beep

---

## Evaluation Criteria Coverage
| Criteria | Implementation |
|----------|---------------|
| Functional completion (40%) | All 6 milestones complete |
| Milestone achievement (25%) | All 6 milestones achieved |
| Code quality (15%) | Clean modular structure, error handling |
| User experience (10%) | Auto silence detection, real-time chat display |
| Documentation (10%) | This README |