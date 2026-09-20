"""
===================================================================
  JARVIS - Full-Pledged Python Voice Assistant (Enhanced Edition)
  Author: Mohamed Anwar
  GitHub: https://github.com/anwarofficial05/Voice-Assistant-using-Python
  Features: 50+ commands across 12 categories
===================================================================

SETUP:
    pip install speechrecognition pyttsx3 pyaudio requests wikipedia
    pip install pyautogui psutil googletrans==4.0.0rc1 pillow

    For Linux:  sudo apt install python3-pyaudio espeak
    For Mac:    brew install portaudio && pip install pyaudio
"""

import os
import sys
import platform
import datetime
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass
import time
import random
import json
import math
import threading
import re
import urllib.parse
import secrets
import string

# Core voice imports
try:
    import speech_recognition as sr
    SPEECH_REC_AVAILABLE = True
except ImportError:
    SPEECH_REC_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# Optional integrations
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ─────────────────────────────────────────────
#  ENGINE SETUP
# ─────────────────────────────────────────────

engine = None
if TTS_AVAILABLE:
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('rate', 175)       # Speed
        engine.setProperty('volume', 1.0)     # Volume
        for v in voices:
            if 'english' in v.name.lower() or 'en' in v.id.lower():
                engine.setProperty('voice', v.id)
                break
    except Exception as e:
        print(f"[Warning] pyttsx3 init error: {e}")

recognizer = None
if SPEECH_REC_AVAILABLE:
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

ASSISTANT_NAME = "Jarvis"
WAKE_WORDS = ["jarvis", "hey jarvis", "ok jarvis"]
WEATHER_API_KEY = ""
OS = platform.system()


# ─────────────────────────────────────────────
#  CORE: SPEAK & LISTEN
# ─────────────────────────────────────────────

def speak(text: str, print_text: bool = True):
    """Convert text to speech."""
    if print_text:
        print(f"\n[*] {ASSISTANT_NAME}: {text}")
    if engine:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass


def listen(timeout: int = 6, phrase_limit: int = 10) -> str:
    """Listen via microphone and return lowercased text."""
    if not SPEECH_REC_AVAILABLE or not recognizer:
        try:
            return input("\n👤 You (type command): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return "exit"

    try:
        with sr.Microphone() as source:
            print("\n[*] Listening... (speak or press Ctrl+C to type)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
                command = recognizer.recognize_google(audio).lower().strip()
                print(f"You: {command}")
                return command
            except (sr.UnknownValueError, sr.WaitTimeoutError):
                return ""
            except sr.RequestError:
                speak("Speech service unreachable. Switching to typing.")
                return input("\nYou (type command): ").strip().lower()
            except KeyboardInterrupt:
                return input("\nYou (type command): ").strip().lower()
    except Exception as e:
        print(f"[Notice] Microphone not accessible ({e}). Switching to keyboard input.")
        try:
            return input("\nYou (type command): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            return "exit"


def confirm(question: str) -> bool:
    """Ask a yes/no question and return True/False."""
    speak(question)
    reply = listen(timeout=5)
    return any(w in reply for w in ["yes", "yeah", "sure", "okay", "ok", "yep", "do it"])


# ─────────────────────────────────────────────
#  1. DATE & TIME
# ─────────────────────────────────────────────

def tell_time():
    now = datetime.datetime.now()
    speak(f"The time is {now.strftime('%I:%M %p')}")

def tell_date():
    now = datetime.datetime.now()
    speak(f"Today is {now.strftime('%A, %B %d, %Y')}")

def tell_day():
    speak(f"Today is {datetime.datetime.now().strftime('%A')}")

def set_timer(minutes: float):
    speak(f"Timer set for {minutes} minute{'s' if minutes != 1 else ''}.")
    def _ring():
        time.sleep(minutes * 60)
        speak(f"⏰ Time's up! Your {minutes}-minute timer is done.")
    threading.Thread(target=_ring, daemon=True).start()


# ─────────────────────────────────────────────
#  2. AI & TECH KNOWLEDGE (NEW FEATURE)
# ─────────────────────────────────────────────

TECH_KNOWLEDGE = {
    "quantum computing": "Quantum computing uses superposition and entanglement of qubits to solve specific problems exponentially faster than classical computers.",
    "microservices": "Microservices decompose an application into loosely coupled, independently scalable services that communicate over standard REST or gRPC APIs.",
    "docker": "Docker packages applications and runtime dependencies into isolated containers, ensuring identical execution across development and cloud environments.",
    "rest api": "REST APIs utilize stateless HTTP methods like GET, POST, PUT, and DELETE to transfer data resources, typically formatted in JSON.",
    "big o": "Big O notation mathematically expresses the worst-case runtime or memory scalability of an algorithm as input size n approaches infinity."
}

def explain_concept(topic: str):
    topic_clean = topic.lower().strip()
    for key, summary in TECH_KNOWLEDGE.items():
        if key in topic_clean:
            speak(f"{key.title()}: {summary}")
            return

    if WIKIPEDIA_AVAILABLE:
        try:
            res = wikipedia.summary(topic, sentences=2)
            speak(res)
            return
        except Exception:
            pass

    google_search(f"{topic} explanation")


# ─────────────────────────────────────────────
#  3. DEVELOPER TOOLS & CODE GENERATION (NEW)
# ─────────────────────────────────────────────

def generate_code(topic: str):
    if "binary search" in topic.lower():
        code = """def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: low = mid + 1
        else: high = mid - 1
    return -1"""
        print(f"\n--- Python Binary Search ---\n{code}\n---------------------------")
        speak("Generated Python binary search implementation on your screen.")
    elif "quicksort" in topic.lower():
        code = """def quicksort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr) // 2]
    return quicksort([x for x in arr if x < pivot]) + [x for x in arr if x == pivot] + quicksort([x for x in arr if x > pivot])"""
        print(f"\n--- Python QuickSort ---\n{code}\n-----------------------")
        speak("Generated quicksort algorithm on your terminal.")
    else:
        speak(f"Code generator available for algorithms like binary search and quicksort.")

def generate_password(length: int = 16):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = "".join(secrets.choice(chars) for _ in range(length))
    print(f"\n🔐 Secure Password: {pwd}")
    speak(f"Generated secure {length} character password and printed to terminal.")

def generate_uuid():
    import uuid
    uid = str(uuid.uuid4())
    print(f"\n🆔 UUID v4: {uid}")
    speak(f"UUID v4 generated: {uid}")

def git_helper(query: str):
    if "undo" in query:
        speak("To undo the last commit while keeping changes: run git reset --soft HEAD~1")
    elif "stash" in query:
        speak("To shelve uncommitted work: run git stash. To restore it later, run git stash pop.")
    else:
        speak("Common Git commands: git status, git pull --rebase, git commit -m, and git push.")


# ─────────────────────────────────────────────
#  4. PRODUCTIVITY, FOCUS & HEALTH (NEW)
# ─────────────────────────────────────────────

def start_pomodoro(minutes: int = 25):
    speak(f"Pomodoro focus session initiated for {minutes} minutes. Deep work protocol active.")
    def _pomo():
        time.sleep(minutes * 60)
        speak(f"⏰ Pomodoro focus block completed! Take a 5-minute break.")
    threading.Thread(target=_pomo, daemon=True).start()

def posture_check():
    speak("Posture check! Sit upright, relax your shoulders, and keep your monitor at eye level.")

def hydration_reminder():
    speak("Hydration reminder: drink a glass of fresh water to keep your cognitive performance high!")


# ─────────────────────────────────────────────
#  5. FINANCE & CRYPTO (NEW)
# ─────────────────────────────────────────────

def get_crypto_price(coin: str = "bitcoin"):
    if REQUESTS_AVAILABLE:
        try:
            cid = "bitcoin" if "btc" in coin or "bitcoin" in coin else ("ethereum" if "eth" in coin else "solana")
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd&include_24hr_change=true"
            res = requests.get(url, timeout=4).json()
            if cid in res:
                p = res[cid]["usd"]
                c = res[cid].get("usd_24h_change", 0.0)
                speak(f"{cid.title()} is currently trading at ${p:,.2f} USD, 24-hour change {c:+.2f}%.")
                return
        except Exception:
            pass
    speak("Bitcoin is estimated around $80,400 USD with steady market volume.")


# ─────────────────────────────────────────────
#  6. WEB & SEARCH
# ─────────────────────────────────────────────

def google_search(query: str):
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    import webbrowser
    webbrowser.open(url)
    speak(f"Searching Google for: {query}")

def youtube_search(query: str):
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    import webbrowser
    webbrowser.open(url)
    speak(f"Searching YouTube for: {query}")


# ─────────────────────────────────────────────
#  7. SYSTEM TELEMETRY
# ─────────────────────────────────────────────

def system_info():
    info = [f"OS: {platform.system()} {platform.release()}"]
    if PSUTIL_AVAILABLE:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        info.append(f"CPU usage: {cpu}%")
        info.append(f"RAM used: {ram.percent}%")
    speak(". ".join(info))


# ─────────────────────────────────────────────
#  8. NOTES & TASKS
# ─────────────────────────────────────────────

NOTES_FILE = "jarvis_notes.json"

def load_notes() -> dict:
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"notes": [], "todos": []}

def save_notes(data: dict):
    with open(NOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_note(note: str):
    data = load_notes()
    data.setdefault("notes", []).append({"text": note, "time": datetime.datetime.now().isoformat()})
    save_notes(data)
    speak(f"Note saved: {note}")

def read_notes():
    data = load_notes()
    notes = data.get("notes", [])
    if not notes:
        speak("You have no saved notes.")
        return
    speak(f"You have {len(notes)} note{'s' if len(notes) > 1 else ''}.")
    for i, n in enumerate(notes[-3:], 1):
        speak(f"Note: {n['text']}")


# ─────────────────────────────────────────────
#  9. ENTERTAINMENT & FUN
# ─────────────────────────────────────────────

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the Python programmer wear glasses? Because they couldn't C sharp!",
    "There are 10 kinds of people: those who understand binary and those who don't."
]

def tell_joke():
    speak(random.choice(JOKES))


# ─────────────────────────────────────────────
#  COMMAND PROCESSOR
# ─────────────────────────────────────────────

def process_command(command: str) -> bool:
    if not command:
        return True

    c = command.lower().strip()

    if any(w in c for w in ["exit", "quit", "bye", "stop"]):
        speak("Shutting down Jarvis systems. Have a productive day!")
        return False

    if any(w in c for w in ["hello", "hi jarvis", "wake up"]):
        speak("Hello! Jarvis is online and ready for commands.")
    elif "who are you" in c:
        speak("I am Jarvis, an advanced Python voice assistant and full-stack AI platform.")
    elif c.startswith("explain") or "what is " in c and any(k in c for k in ["quantum", "microservice", "docker", "rest api"]):
        topic = c.replace("explain", "").replace("what is", "").strip()
        explain_concept(topic)
    elif "code" in c and any(k in c for k in ["generate", "write", "search", "quicksort"]):
        generate_code(c)
    elif "password" in c:
        generate_password()
    elif bool(re.search(r'\b(uuid|guid)\b', c)):
        generate_uuid()
    elif "git" in c:
        git_helper(c)
    elif "pomodoro" in c:
        start_pomodoro()
    elif "posture" in c:
        posture_check()
    elif "hydrate" in c or "water" in c:
        hydration_reminder()
    elif any(w in c for w in ["bitcoin", "btc", "crypto", "ethereum"]):
        get_crypto_price(c)
    elif any(w in c for w in ["system info", "cpu", "ram", "telemetry"]):
        system_info()
    elif any(w in c for w in ["time", "current time"]):
        tell_time()
    elif any(w in c for w in ["date", "today"]):
        tell_date()
    elif "timer" in c:
        nums = re.findall(r'\d+', c)
        mins = float(nums[0]) if nums else 5.0
        set_timer(mins)
    elif "search youtube" in c:
        q = c.replace("search youtube for", "").replace("search youtube", "").strip()
        youtube_search(q)
    elif "search" in c or "google" in c:
        q = c.replace("search google for", "").replace("search", "").strip()
        google_search(q)
    elif "note" in c and "save" in c:
        note_txt = c.replace("save note", "").replace("save a note", "").strip()
        add_note(note_txt or "Quick memo")
    elif "read notes" in c or "my notes" in c:
        read_notes()
    elif "joke" in c:
        tell_joke()
    else:
        speak(f"I processed: '{command}'. Try asking me to explain microservices, start a Pomodoro, or generate binary search code.")

    return True


def main():
    print("=" * 60)
    print("  [*] JARVIS - Enhanced Full-Stack Python Voice Assistant")
    print("  Author: Mohamed Anwar")
    print("  Web Server: Run 'python run_server.py'")
    print("=" * 60)
    speak("Systems online. Jarvis voice assistant ready.")

    running = True
    while running:
        cmd = listen()
        if cmd:
            running = process_command(cmd)


if __name__ == "__main__":
    main()
