# 🤖 JARVIS — Full-Stack Real-Time Voice Assistant & AI Platform

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Web Speech API](https://img.shields.io/badge/Web_Speech_API-HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **JARVIS** is an industry-grade, full-stack voice assistant and productivity platform inspired by Iron Man's Stark Industries AI. Engineered with an asynchronous **Python (FastAPI)** backend and a futuristic cybernetic HUD web frontend utilizing HTML5 **Web Speech API** and **Web Audio API** canvas visualizer.

---

## 🌟 Key Highlights & Engineering Features

- 🎙️ **Dual-Engine Speech Architecture**: Instantaneous speech-to-text and voice synthesis in any browser via the Web Speech API with automatic fallback to server-side NLP routing.
- 🌊 **Real-Time Soundwave Visualizer**: HTML5 Canvas audio frequency analyzer powered by Web Audio API `AnalyserNode`, responding dynamically to vocal input.
- ⚡ **Asynchronous Microservices Backend**: Powered by FastAPI & Uvicorn with sub-200ms intent dispatch latency.
- 🛠️ **50+ Spoken Commands Across 12 Categories**:
  - **AI & Tech Knowledge**: Deep technical explainers for Quantum Computing, Microservices, Docker, REST APIs, Big O, and Recursion.
  - **Developer Tools**: Algorithmic code generation (Binary Search, QuickSort, Debounce), cryptographic password generation, UUID v4 generator, Git cheatsheet, and Regex helpers.
  - **Productivity & Health**: Integrated Pomodoro focus cycles, guided 4-7-8 breathing circle animation, posture reminders, and hydration alerts.
  - **Finance & Crypto**: Real-time cryptocurrency price tracker (Bitcoin, Ethereum, Solana) powered by CoinGecko API and currency conversion.
  - **System Telemetry**: Live CPU, RAM, and disk utilization HUD gauges streaming via `psutil`.
  - **Audio & Ambience**: Ambient soundscapes (lofi chill beats, heavy rain, coffee shop background noise).
  - **Notes & Tasks**: Persistent JSON task checklist with one-click Markdown export.
  - **Fallback Keyboard & Chip Mode**: 100% interactive even without a microphone or in noisy environments.
- 💼 **Portfolio & Resume Ready**: Dedicated "Resume Showcase" modal containing ready-to-copy bullet points, metrics, and architecture diagrams for technical interviews.

---

## 🏗️ System Architecture

```text
+-------------------------------------------------------------+
|                  BROWSER CLIENT LAYER                      |
|  - Web Speech API (webkitSpeechRecognition & Synthesis)     |
|  - Web Audio API (AnalyserNode -> HTML5 Canvas Visualizer)  |
|  - Iron Man / HUD Cyberpunk Glassmorphism Interface         |
+------------------------------+------------------------------+
                               |
               REST / WebSocket | JSON (sub-200ms latency)
                               v
+-------------------------------------------------------------+
|                  FASTAPI ASYNC BACKEND                      |
|  - Intent Classifier & Keyword Dispatcher (assistant.py)   |
|  - 12 Categorized Handlers (AI, Dev, Telemetry, Finance...) |
|  - Hardware Telemetry Monitor (psutil)                      |
|  - Persistent Notes & Task Engine (JSON storage)            |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|               EXTERNAL APIS & SYSTEM TOOLS                  |
|  - CoinGecko Real-time API  |  Wikipedia Knowledge Base     |
|  - OpenWeatherMap API       |  Local OS Automation (psutil) |
+-------------------------------------------------------------+
```

---

## 📂 Project Structure

```text
Voice-Assistant-using-Python/
├── backend/
│   ├── assistant.py          # Core Jarvis brain, intent dispatcher & 50+ commands
│   ├── main.py               # FastAPI server, REST routes & static file mounting
│   ├── requirements.txt      # Backend dependencies
│   └── test_assistant.py     # Automated intent testing script
├── frontend/
│   ├── index.html            # Futuristic Iron Man HUD dashboard
│   ├── css/
│   │   └── style.css         # Cyberpunk glassmorphism styling & animations
│   └── js/
│       └── app.js            # Web Speech API, canvas visualizer & API controller
├── jarvis_desktop.py         # Standalone desktop CLI voice assistant
├── resume_bullet_points.md   # Ready-to-use resume bullet points & interview guide
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start Guide

### Option 1: Run Full-Stack Web Application (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anwarofficial05/Voice-Assistant-using-Python.git
   cd Voice-Assistant-using-Python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Start the FastAPI Server:**
   ```bash
   python -m uvicorn backend.main:app --reload --port 8000
   ```

4. **Open your browser:**
   Navigate to [http://localhost:8000](http://localhost:8000). Click **"INITIATE VOICE"** (or press `Spacebar`) and start speaking!
   Interactive API docs are available at [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

---

### Option 2: Run Standalone Desktop CLI Assistant

If you want to use the local microphone script directly in terminal:
```bash
python jarvis_desktop.py
```

---

### Option 3: Instant Browser Preview (Zero Installation)

You can directly open `frontend/index.html` in Chrome, Edge, or Safari! The built-in client fallback engine executes the commands directly in your browser without requiring a running Python server.

---

## 🗣️ Spoken Command Examples

| Category | Voice Command Example |
| :--- | :--- |
| **AI & Tech** | *"Explain Quantum Computing"*, *"Explain Microservices"* |
| **Developer** | *"Generate code for Binary Search"*, *"Generate secure password"*, *"Git undo commit"* |
| **Productivity** | *"Start Pomodoro"*, *"Guided breathing"*, *"Posture check"*, *"Set timer for 5 minutes"* |
| **Finance** | *"Price of Bitcoin"*, *"Price of Solana"*, *"Convert 100 USD to EUR"* |
| **System** | *"System telemetry"*, *"Network ping status"*, *"System info"* |
| **Notes & Tasks** | *"Save note review portfolio"*, *"Read notes"*, *"Add todo submit application"* |
| **Media & Fun** | *"Play lofi chill beats"*, *"Tell me a developer joke"*, *"Flip a coin"* |
| **Math** | *"What is 45 times 8"*, *"Convert 10 km to miles"*, *"Convert 100 celsius to fahrenheit"* |

---

## 📄 Adding to Your Resume

Check out [`resume_bullet_points.md`](resume_bullet_points.md) for pre-written bullet points and interview talking points tailored for Software Engineer, Full-Stack, and Python Developer roles.

---

## 👨‍💻 Author

**Mohamed Anwar**  
- GitHub: [@anwarofficial05](https://github.com/anwarofficial05)
- Project: [Voice-Assistant-using-Python](https://github.com/anwarofficial05/Voice-Assistant-using-Python)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE). Feel free to star ⭐️ the repository and contribute!
