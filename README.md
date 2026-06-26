# 🤖 JARVIS — Python Voice Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  A fully offline-capable, Python-based voice assistant that listens to your voice and responds to 30+ commands across time, weather, web search, system control, math, notes, and more — all hands-free.
</p>

---

## 📸 Preview

```
===========================================================
  🤖  JARVIS — Python Voice Assistant
===========================================================
  Say 'help' to see all commands.
  Say 'goodbye' or 'exit' to quit.
===========================================================

🤖 JARVIS: Good morning! I'm Jarvis, your personal voice assistant.

🎙️  Listening...
👤 You: what time is it
🤖 JARVIS: The time is 10:35 AM
```

---

## ✨ Features

| Category | What You Can Do |
|---|---|
| ⏰ **Time & Alarms** | Get current time, date, day · Set countdown timers · Set alarms (run in background) |
| 🌐 **Web & Search** | Google search · YouTube search · Open any website · Wikipedia summaries |
| 🌤️ **Weather** | Get weather for any city (API or Google fallback) |
| 💻 **System Control** | Screenshot · System/battery info · Shutdown · Restart · Lock screen · Open apps |
| 🧮 **Math & Units** | Evaluate expressions · Convert km↔miles, kg↔lbs, °C↔°F, and more |
| 📝 **Notes & To-Do** | Save & read notes · Add & list tasks · All stored locally in JSON |
| 🎲 **Fun** | Jokes · Motivational quotes · Coin flip · Dice roll · Random numbers |
| 🤖 **Personality** | Context-aware greetings · "How are you" · "Who are you" |
| 🆘 **Help** | Say "help" to print the full command list to the terminal |
| 🔄 **Smart Fallback** | Unknown commands auto-offer a Google search |

---

## 🛠️ Tech Stack

- **Python 3.8+**
- [`SpeechRecognition`](https://pypi.org/project/SpeechRecognition/) — Mic input → text via Google Speech API
- [`pyttsx3`](https://pypi.org/project/pyttsx3/) — Offline text → speech engine
- [`PyAudio`](https://pypi.org/project/PyAudio/) — Microphone access
- [`requests`](https://pypi.org/project/requests/) — Weather API calls
- [`wikipedia`](https://pypi.org/project/wikipedia/) — Wikipedia summaries
- [`psutil`](https://pypi.org/project/psutil/) — CPU, RAM, battery stats
- [`pyautogui`](https://pypi.org/project/pyautogui/) — Screenshots

---

## ⚡ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/jarvis-voice-assistant.git
cd jarvis-voice-assistant
```

### 2. Install dependencies

```bash
pip install speechrecognition pyttsx3 pyaudio requests wikipedia pyautogui psutil
```

> **Windows:** If `pyaudio` fails, download the correct `.whl` from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install it manually:
> ```bash
> pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl
> ```

> **Linux:**
> ```bash
> sudo apt install python3-pyaudio espeak
> ```

> **Mac:**
> ```bash
> brew install portaudio
> pip install pyaudio
> ```

### 3. Run the assistant

```bash
python voice_assistant.py
```

---

## 🔑 Optional API Keys

For richer weather data, open `voice_assistant.py` and add your free API keys at the top:

```python
WEATHER_API_KEY = "your_openweathermap_key"   # https://openweathermap.org/api (free)
NEWS_API_KEY    = "your_newsapi_key"           # https://newsapi.org (free)
```

> Without keys, weather automatically opens Google — so it still works out of the box!

---

## 🗣️ Voice Commands Reference

### ⏰ Time & Alarms
```
"What time is it"
"What's today's date"
"What day is it"
"Set a timer for 5 minutes"
"Set alarm for 7 30 AM"
```

### 🌐 Web & Search
```
"Search <query>"
"Search YouTube for <query>"
"Open YouTube"
"Open GitHub"
"Open Gmail"
"Wikipedia Python programming"
```

### 🌤️ Weather
```
"Weather in Chennai"
"What's the weather in Delhi"
```

### 💻 System Control
```
"Take a screenshot"
"System info"
"Battery status"
"Shutdown"
"Restart"
"Lock screen"
"Open notepad"
```

### 🧮 Math & Conversions
```
"Calculate 25 times 4"
"What is 150 divided by 6"
"Convert 10 km to miles"
"Convert 37 celsius to fahrenheit"
"Convert 5 kg to lbs"
```

### 📝 Notes & To-Do
```
"Save a note Buy groceries tomorrow"
"Read my notes"
"Add to-do Submit the assignment"
"Read my todos"
"Clear notes"
```

### 🎲 Fun
```
"Tell me a joke"
"Motivate me"
"Flip a coin"
"Roll a dice"
"Random number between 1 and 50"
```

### 👋 General
```
"Hello"
"How are you"
"Who are you"
"Help"
"Goodbye"
```

---

## 📁 Project Structure

```
jarvis-voice-assistant/
│
├── voice_assistant.py       # Main assistant script
├── jarvis_notes.json        # Auto-created: stores notes & todos
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

---

## 📦 requirements.txt

```
speechrecognition
pyttsx3
pyaudio
requests
wikipedia
pyautogui
psutil
```

> Save this as `requirements.txt` and run `pip install -r requirements.txt` for one-shot setup.

---

## 🔧 Customization

You can easily extend JARVIS by adding new command blocks inside `process_command()` in `voice_assistant.py`:

```python
elif "your trigger phrase" in c:
    your_function()
```

Want to change the assistant's name? Update this at the top of the file:

```python
ASSISTANT_NAME = "Jarvis"   # Change to anything you like
```

Want to adjust voice speed or volume?

```python
engine.setProperty('rate', 175)    # Lower = slower, Higher = faster
engine.setProperty('volume', 1.0)  # 0.0 to 1.0
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `PyAudio` install fails | See platform-specific install steps above |
| Mic not detected | Check microphone permissions in OS settings |
| Speech not recognized | Ensure you have a stable internet connection (Google Speech API is used) |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Voice sounds robotic | Try a different voice index in `engine.setProperty('voice', voices[1].id)` |

---

## 🚀 Future Improvements

- [ ] Wake word detection (always-on listening)
- [ ] GUI interface with Tkinter
- [ ] Email sending via SMTP
- [ ] Spotify / music playback control
- [ ] WhatsApp message automation
- [ ] News headlines via NewsAPI
- [ ] Multi-language support

---

## 🧑‍💻 Author

**Mohamed Anwar**
- 🎓 Computer Science & Engineering Student
- 💼 Skills: Python · Data Analytics · Frontend Development · AI Prompting
- 🔗 [LinkedIn](https://linkedin.com/in/your-profile) · [GitHub](https://github.com/your-username)

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute it.

---

## ⭐ Show Your Support

If you found this project helpful, please consider giving it a **star ⭐** on GitHub — it means a lot!

---

<p align="center">Built with ❤️ using Python</p>
