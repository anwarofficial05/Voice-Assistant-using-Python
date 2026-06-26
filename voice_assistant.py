"""
========================================================
  JARVIS - Full-Pledged Python Voice Assistant
  Author: Mohamed Anwar
  Features: 30+ commands across 10 categories
========================================================

SETUP:
    pip install speechrecognition pyttsx3 pyaudio requests wikipedia
    pip install pyautogui psutil googletrans==4.0.0rc1 pillow

    For Linux:  sudo apt install python3-pyaudio espeak
    For Mac:    brew install portaudio && pip install pyaudio
"""

import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import sys
import platform
import subprocess
import time
import random
import json
import math
import threading
import re
import urllib.parse

# Optional imports (graceful fallback if not installed)
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

engine = pyttsx3.init()

# Voice settings
voices = engine.getProperty('voices')
engine.setProperty('rate', 175)       # Speed (default ~200)
engine.setProperty('volume', 1.0)     # Volume 0.0 to 1.0

# Try to set a clear English voice
for v in voices:
    if 'english' in v.name.lower() or 'en' in v.id.lower():
        engine.setProperty('voice', v.id)
        break

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

ASSISTANT_NAME = "Jarvis"
WAKE_WORDS = ["jarvis", "hey jarvis", "ok jarvis"]
WEATHER_API_KEY = ""   # Optional: paste your OpenWeatherMap key here
NEWS_API_KEY    = ""   # Optional: paste your NewsAPI key here


# ─────────────────────────────────────────────
#  CORE: SPEAK & LISTEN
# ─────────────────────────────────────────────

def speak(text: str, print_text: bool = True):
    """Convert text to speech."""
    if print_text:
        print(f"\n🤖 {ASSISTANT_NAME}: {text}")
    engine.say(text)
    engine.runAndWait()


def listen(timeout: int = 6, phrase_limit: int = 10) -> str:
    """Listen via microphone and return lowercased text."""
    with sr.Microphone() as source:
        print("\n🎙️  Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        try:
            audio = recognizer.listen(source, timeout=timeout,
                                      phrase_time_limit=phrase_limit)
            command = recognizer.recognize_google(audio).lower().strip()
            print(f"👤 You: {command}")
            return command
        except sr.UnknownValueError:
            return ""
        except sr.WaitTimeoutError:
            return ""
        except sr.RequestError:
            speak("I'm having trouble connecting to the speech service.")
            return ""


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

def set_alarm(hour: int, minute: int, period: str = ""):
    """Rings when system time matches."""
    def _alarm():
        while True:
            now = datetime.datetime.now()
            target_hour = hour
            if period.lower() == "pm" and hour != 12:
                target_hour += 12
            elif period.lower() == "am" and hour == 12:
                target_hour = 0
            if now.hour == target_hour and now.minute == minute:
                speak("⏰ Alarm ringing! Wake up!")
                break
            time.sleep(30)
    threading.Thread(target=_alarm, daemon=True).start()
    speak(f"Alarm set for {hour}:{minute:02d} {period.upper()}")


# ─────────────────────────────────────────────
#  2. WEB & SEARCH
# ─────────────────────────────────────────────

def google_search(query: str):
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    webbrowser.open(url)
    speak(f"Searching Google for: {query}")

def youtube_search(query: str):
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    webbrowser.open(url)
    speak(f"Searching YouTube for: {query}")

def open_website(site: str):
    """Open any website by name or URL."""
    site_map = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "linkedin": "https://linkedin.com",
        "twitter": "https://twitter.com",
        "instagram": "https://instagram.com",
        "facebook": "https://facebook.com",
        "reddit": "https://reddit.com",
        "netflix": "https://netflix.com",
        "amazon": "https://amazon.com",
        "wikipedia": "https://wikipedia.org",
        "stack overflow": "https://stackoverflow.com",
        "chatgpt": "https://chat.openai.com",
    }
    key = site.lower().strip()
    url = site_map.get(key, f"https://{site}" if "." in site else f"https://www.{site}.com")
    webbrowser.open(url)
    speak(f"Opening {site}")

def wikipedia_search(query: str):
    if not WIKIPEDIA_AVAILABLE:
        speak("Wikipedia module not installed. Searching on Google instead.")
        google_search(query + " wikipedia")
        return
    try:
        wikipedia.set_lang("en")
        result = wikipedia.summary(query, sentences=3)
        speak(result)
    except wikipedia.exceptions.DisambiguationError as e:
        speak(f"Multiple results found. Did you mean: {e.options[0]}?")
    except Exception:
        speak("I couldn't find that on Wikipedia.")


# ─────────────────────────────────────────────
#  3. WEATHER
# ─────────────────────────────────────────────

def get_weather(city: str = "Madurai"):
    if not REQUESTS_AVAILABLE:
        speak("Requests module not installed.")
        return
    if not WEATHER_API_KEY:
        speak(f"No weather API key set. Opening weather for {city} on Google.")
        webbrowser.open(f"https://www.google.com/search?q=weather+in+{urllib.parse.quote(city)}")
        return
    try:
        url = (f"http://api.openweathermap.org/data/2.5/weather"
               f"?q={city}&appid={WEATHER_API_KEY}&units=metric")
        data = requests.get(url, timeout=5).json()
        if data.get("cod") != 200:
            speak(f"Couldn't get weather for {city}.")
            return
        temp  = data["main"]["temp"]
        desc  = data["weather"][0]["description"]
        humid = data["main"]["humidity"]
        speak(f"Weather in {city}: {desc}, {temp:.0f}°C, humidity {humid}%")
    except Exception:
        speak("Weather service unavailable right now.")


# ─────────────────────────────────────────────
#  4. SYSTEM CONTROL
# ─────────────────────────────────────────────

OS = platform.system()  # "Windows", "Linux", "Darwin"

def take_screenshot():
    try:
        import pyautogui
        filename = f"screenshot_{int(time.time())}.png"
        pyautogui.screenshot(filename)
        speak(f"Screenshot saved as {filename}")
    except ImportError:
        speak("pyautogui not installed. Run: pip install pyautogui")

def system_info():
    info = []
    info.append(f"OS: {platform.system()} {platform.release()}")
    info.append(f"Machine: {platform.machine()}")
    if PSUTIL_AVAILABLE:
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        info.append(f"CPU usage: {cpu}%")
        info.append(f"RAM used: {ram.percent}%")
        info.append(f"Disk used: {disk.percent}%")
    speak(". ".join(info))

def battery_status():
    if not PSUTIL_AVAILABLE:
        speak("psutil not installed.")
        return
    batt = psutil.sensors_battery()
    if batt:
        speak(f"Battery at {batt.percent:.0f}%. {'Charging.' if batt.power_plugged else 'Not charging.'}")
    else:
        speak("No battery detected.")

def shutdown_system():
    if confirm("Are you sure you want to shut down the computer?"):
        speak("Shutting down...")
        if OS == "Windows":
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h now")

def restart_system():
    if confirm("Are you sure you want to restart?"):
        speak("Restarting...")
        if OS == "Windows":
            os.system("shutdown /r /t 5")
        else:
            os.system("reboot")

def lock_screen():
    speak("Locking screen.")
    if OS == "Windows":
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif OS == "Linux":
        os.system("gnome-screensaver-command -l")
    elif OS == "Darwin":
        os.system('"/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession" -suspend')

def open_application(app_name: str):
    speak(f"Opening {app_name}")
    if OS == "Windows":
        os.system(f'start {app_name}')
    elif OS == "Darwin":
        os.system(f'open -a "{app_name}"')
    else:
        subprocess.Popen([app_name])


# ─────────────────────────────────────────────
#  5. CALCULATIONS & MATH
# ─────────────────────────────────────────────

def calculate(expression: str) -> str:
    """Evaluate a math expression safely."""
    try:
        # Replace spoken words with symbols
        expr = expression.replace("plus", "+").replace("minus", "-") \
                         .replace("times", "*").replace("multiplied by", "*") \
                         .replace("divided by", "/").replace("x", "*") \
                         .replace("power", "**").replace("squared", "**2") \
                         .replace("cubed", "**3").replace("percent", "/100*") \
                         .replace("√", "math.sqrt").replace("pi", str(math.pi))
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expr, {"__builtins__": {}}, allowed)
        return str(round(result, 6))
    except Exception:
        return "I couldn't calculate that."

def unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    conversions = {
        ("km", "miles"): 0.621371, ("miles", "km"): 1.60934,
        ("kg", "lbs"): 2.20462,   ("lbs", "kg"): 0.453592,
        ("cm", "inches"): 0.393701,("inches", "cm"): 2.54,
        ("celsius", "fahrenheit"): lambda c: c * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
        ("liters", "gallons"): 0.264172, ("gallons", "liters"): 3.78541,
        ("meters", "feet"): 3.28084,    ("feet", "meters"): 0.3048,
    }
    key = (from_unit.lower(), to_unit.lower())
    conv = conversions.get(key)
    if conv is None:
        return "I don't know that conversion."
    result = conv(value) if callable(conv) else value * conv
    return f"{value} {from_unit} = {round(result, 4)} {to_unit}"


# ─────────────────────────────────────────────
#  6. NOTES & REMINDERS
# ─────────────────────────────────────────────

NOTES_FILE = "jarvis_notes.json"

def load_notes() -> dict:
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {"notes": [], "todos": []}

def save_notes(data: dict):
    with open(NOTES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_note(note: str):
    data = load_notes()
    entry = {"text": note, "time": datetime.datetime.now().isoformat()}
    data["notes"].append(entry)
    save_notes(data)
    speak(f"Note saved: {note}")

def read_notes():
    data = load_notes()
    notes = data.get("notes", [])
    if not notes:
        speak("You have no saved notes.")
        return
    speak(f"You have {len(notes)} note{'s' if len(notes) > 1 else ''}.")
    for i, n in enumerate(notes, 1):
        speak(f"Note {i}: {n['text']}")

def add_todo(task: str):
    data = load_notes()
    data["todos"].append({"task": task, "done": False})
    save_notes(data)
    speak(f"Added to your to-do list: {task}")

def read_todos():
    data = load_notes()
    todos = [t for t in data.get("todos", []) if not t["done"]]
    if not todos:
        speak("Your to-do list is empty.")
        return
    speak(f"You have {len(todos)} pending task{'s' if len(todos) > 1 else ''}.")
    for i, t in enumerate(todos, 1):
        speak(f"{i}. {t['task']}")

def clear_notes():
    if confirm("Delete all notes and todos?"):
        save_notes({"notes": [], "todos": []})
        speak("All notes and todos cleared.")


# ─────────────────────────────────────────────
#  7. FUN & ENTERTAINMENT
# ─────────────────────────────────────────────

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why don't scientists trust atoms? Because they make up everything!",
    "I'm reading a book about anti-gravity. It's impossible to put down.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "Parallel lines have so much in common. It's a shame they'll never meet.",
    "Why did the Python programmer wear glasses? Because he couldn't C sharp!",
    "What do you call a fish without eyes? A fsh.",
    "I would tell you a joke about UDP, but you might not get it.",
    "There are 10 kinds of people: those who understand binary and those who don't.",
]

MOTIVATIONAL_QUOTES = [
    "Believe you can and you're halfway there. — Theodore Roosevelt",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt",
    "Code is like humor. When you have to explain it, it's bad. — Cory House",
    "The best error message is the one that never shows up. — Thomas Fuchs",
]

def tell_joke():
    speak(random.choice(JOKES))

def motivate():
    speak(random.choice(MOTIVATIONAL_QUOTES))

def flip_coin():
    result = random.choice(["Heads", "Tails"])
    speak(f"It's {result}!")

def roll_dice(sides: int = 6):
    result = random.randint(1, sides)
    speak(f"You rolled a {result} on a {sides}-sided die.")

def random_number(low: int = 1, high: int = 100):
    speak(f"Your random number is {random.randint(low, high)}")


# ─────────────────────────────────────────────
#  8. GREETINGS & PERSONALITY
# ─────────────────────────────────────────────

def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    speak(f"{greeting}! I'm {ASSISTANT_NAME}, your personal voice assistant. How can I help you today?")

def how_are_you():
    responses = [
        "I'm doing great, fully charged and ready to help!",
        "Fantastic! All systems are running smoothly.",
        "I'm operating at peak performance. Thanks for asking!",
    ]
    speak(random.choice(responses))

def about_assistant():
    speak(f"I'm {ASSISTANT_NAME}, a Python-based voice assistant. I can help you with time, weather, web searches, calculations, notes, system control, and much more. Just ask!")

def say_bye():
    farewells = [
        "Goodbye! Have a wonderful day!",
        "See you later! Stay awesome!",
        "Farewell! Come back anytime you need help.",
    ]
    speak(random.choice(farewells))
    sys.exit(0)


# ─────────────────────────────────────────────
#  9. HELP & COMMANDS LIST
# ─────────────────────────────────────────────

HELP_TEXT = """
Here's what I can do:

📅 DATE & TIME
   "What time is it" | "What's the date" | "What day is it"
   "Set a timer for 5 minutes" | "Set alarm for 7 30 AM"

🌐 WEB & SEARCH
   "Search <query>" | "Search YouTube for <query>"
   "Open YouTube / GitHub / Gmail / Wikipedia"
   "Wikipedia <topic>"

🌤 WEATHER
   "Weather in <city>" | "What's the weather"

💻 SYSTEM
   "Take a screenshot" | "System info" | "Battery status"
   "Shutdown" | "Restart" | "Lock screen"
   "Open <app name>"

🧮 MATH
   "Calculate <expression>" | "What is 25 times 4"
   "Convert 5 km to miles" | "Convert 100 celsius to fahrenheit"

📝 NOTES & TO-DO
   "Save a note <text>" | "Read my notes"
   "Add to-do <task>" | "Read todos" | "Clear notes"

🎲 FUN
   "Tell me a joke" | "Motivate me"
   "Flip a coin" | "Roll a dice" | "Random number"

👋 PERSONALITY
   "How are you" | "Who are you" | "Goodbye / Exit"
"""

def show_help():
    print(HELP_TEXT)
    speak("I've printed the full command list to your terminal. Here's a quick summary: "
          "I can handle time, weather, web searches, system control, calculations, notes, and fun stuff. "
          "Just speak naturally!")


# ─────────────────────────────────────────────
#  10. COMMAND PROCESSOR
# ─────────────────────────────────────────────

def extract_query(command: str, *keywords) -> str:
    """Remove trigger keywords and return the rest."""
    result = command
    for kw in keywords:
        result = result.replace(kw, "").strip()
    return result

def process_command(command: str) -> bool:
    """
    Parse and execute a voice command.
    Returns False to exit, True to continue.
    """
    if not command:
        return True

    c = command.lower().strip()

    # ── EXIT ──────────────────────────────────
    if any(w in c for w in ["bye", "exit", "quit", "goodbye", "stop", "shut down jarvis"]):
        say_bye()
        return False

    # ── GREETINGS ─────────────────────────────
    if any(w in c for w in ["hello", "hi jarvis", "hey", "what's up"]):
        greet_user()
    elif "how are you" in c:
        how_are_you()
    elif any(w in c for w in ["who are you", "about yourself", "what are you"]):
        about_assistant()
    elif any(w in c for w in ["help", "what can you do", "commands"]):
        show_help()

    # ── DATE & TIME ───────────────────────────
    elif any(w in c for w in ["what time", "current time", "tell me the time"]):
        tell_time()
    elif any(w in c for w in ["what date", "today's date", "current date"]):
        tell_date()
    elif any(w in c for w in ["what day", "which day"]):
        tell_day()
    elif "timer" in c:
        # Extract number of minutes
        nums = re.findall(r'\d+\.?\d*', c)
        if nums:
            set_timer(float(nums[0]))
        else:
            speak("How many minutes for the timer?")
            reply = listen(timeout=5)
            nums = re.findall(r'\d+', reply)
            if nums:
                set_timer(float(nums[0]))
    elif "alarm" in c:
        nums = re.findall(r'\d+', c)
        period = "am" if "am" in c else ("pm" if "pm" in c else "")
        if len(nums) >= 2:
            set_alarm(int(nums[0]), int(nums[1]), period)
        elif len(nums) == 1:
            set_alarm(int(nums[0]), 0, period)
        else:
            speak("Please say the alarm time, like: set alarm for 7 30 AM")

    # ── WEB ───────────────────────────────────
    elif c.startswith("search youtube") or "youtube search" in c:
        q = extract_query(c, "search youtube for", "search youtube", "youtube search")
        youtube_search(q)
    elif c.startswith("search") or "google" in c:
        q = extract_query(c, "search google for", "search for", "search", "google")
        google_search(q)
    elif "open" in c:
        site = extract_query(c, "open")
        open_website(site)
    elif "wikipedia" in c:
        q = extract_query(c, "wikipedia", "search wikipedia for", "wiki")
        wikipedia_search(q)

    # ── WEATHER ───────────────────────────────
    elif "weather" in c:
        city_match = re.search(r'weather\s+(?:in|for|at)?\s*(.+)', c)
        city = city_match.group(1).strip() if city_match else "Madurai"
        get_weather(city)

    # ── SYSTEM ────────────────────────────────
    elif "screenshot" in c:
        take_screenshot()
    elif any(w in c for w in ["system info", "system status", "pc info", "computer info"]):
        system_info()
    elif "battery" in c:
        battery_status()
    elif "shutdown" in c or "shut down" in c:
        shutdown_system()
    elif "restart" in c or "reboot" in c:
        restart_system()
    elif "lock" in c:
        lock_screen()

    # ── MATH ──────────────────────────────────
    elif any(w in c for w in ["calculate", "what is", "compute", "solve"]):
        expr = extract_query(c, "calculate", "what is", "compute", "solve")
        # Check for unit conversion
        conv_match = re.search(r'([\d.]+)\s*(\w+)\s+(?:to|in)\s+(\w+)', expr)
        if conv_match:
            val   = float(conv_match.group(1))
            f_unit = conv_match.group(2)
            t_unit = conv_match.group(3)
            result = unit_converter(val, f_unit, t_unit)
            speak(result)
        else:
            result = calculate(expr)
            speak(f"The answer is {result}")
    elif "convert" in c:
        conv_match = re.search(r'([\d.]+)\s*(\w+)\s+(?:to|in)\s+(\w+)', c)
        if conv_match:
            val    = float(conv_match.group(1))
            f_unit = conv_match.group(2)
            t_unit = conv_match.group(3)
            speak(unit_converter(val, f_unit, t_unit))
        else:
            speak("Please say something like: convert 5 km to miles")

    # ── NOTES ─────────────────────────────────
    elif any(w in c for w in ["save note", "take note", "add note", "note down"]):
        note = extract_query(c, "save note", "take note", "add note", "note down", "note")
        if not note:
            speak("What should I note down?")
            note = listen()
        add_note(note)
    elif any(w in c for w in ["read notes", "show notes", "my notes"]):
        read_notes()
    elif any(w in c for w in ["add todo", "add to-do", "add task", "to do"]):
        task = extract_query(c, "add todo", "add to-do", "add task", "to do")
        if not task:
            speak("What task should I add?")
            task = listen()
        add_todo(task)
    elif any(w in c for w in ["read todos", "my todos", "pending tasks", "to-do list"]):
        read_todos()
    elif "clear notes" in c:
        clear_notes()

    # ── FUN ───────────────────────────────────
    elif any(w in c for w in ["joke", "funny", "make me laugh"]):
        tell_joke()
    elif any(w in c for w in ["motivate", "inspire", "quote"]):
        motivate()
    elif "flip" in c and "coin" in c:
        flip_coin()
    elif "dice" in c or "roll" in c:
        nums = re.findall(r'\d+', c)
        sides = int(nums[0]) if nums else 6
        roll_dice(sides)
    elif "random number" in c:
        nums = re.findall(r'\d+', c)
        if len(nums) >= 2:
            random_number(int(nums[0]), int(nums[1]))
        else:
            random_number()

    # ── FALLBACK ──────────────────────────────
    else:
        speak(f"I'm not sure how to handle that. Say 'help' to hear what I can do, "
              f"or I'll search Google for: {c}")
        if confirm("Should I search Google?"):
            google_search(c)

    return True


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────

def main():
    print("=" * 55)
    print(f"  🤖  {ASSISTANT_NAME} — Python Voice Assistant")
    print("=" * 55)
    print("  Say 'help' to see all commands.")
    print("  Say 'goodbye' or 'exit' to quit.")
    print("=" * 55)
    greet_user()

    running = True
    while running:
        command = listen()
        if command:
            running = process_command(command)


if __name__ == "__main__":
    main()
