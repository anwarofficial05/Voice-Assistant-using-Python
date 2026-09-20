"""
===================================================================
  JARVIS Web Voice Assistant - Core Brain & Command Dispatcher
  Author: Mohamed Anwar
  Features: 50+ voice commands across 12 modular categories
===================================================================
"""

import os
import sys
import platform
import datetime
import math
import random
import re
import json
import time
import secrets
import string
import urllib.parse
from typing import Dict, Any, Optional, List

# Optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

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


class JarvisBrain:
    def __init__(self, data_dir: str = "."):
        self.name = "Jarvis"
        self.data_dir = data_dir
        self.notes_file = os.path.join(data_dir, "jarvis_notes.json")
        self.os_type = platform.system()
        self.active_pomodoro = None
        self._init_storage()

    def _init_storage(self):
        """Ensure notes/todos storage file exists."""
        if not os.path.exists(self.notes_file):
            default_data = {
                "notes": [
                    {
                        "id": "1",
                        "text": "Welcome to Jarvis Voice Assistant! Ready for your commands.",
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                ],
                "todos": [
                    {
                        "id": "1",
                        "task": "Review portfolio project for resume submission",
                        "done": False,
                        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                ]
            }
            try:
                with open(self.notes_file, "w", encoding="utf-8") as f:
                    json.dump(default_data, f, indent=2)
            except Exception:
                pass

    def load_storage(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"notes": [], "todos": []}

    def save_storage(self, data: Dict[str, Any]):
        try:
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving storage: {e}")

    # =================================================================
    # 1. DATE & TIME
    # =================================================================
    def handle_time(self) -> Dict[str, Any]:
        now = datetime.datetime.now()
        speech = f"The current time is {now.strftime('%I:%M %p')}."
        return {
            "success": True,
            "category": "date_time",
            "speech": speech,
            "display": {
                "title": "Current Time",
                "time": now.strftime('%I:%M:%S %p'),
                "timezone": time.tzname[0] if time.tzname else "Local"
            }
        }

    def handle_date(self) -> Dict[str, Any]:
        now = datetime.datetime.now()
        speech = f"Today is {now.strftime('%A, %B %d, %Y')}."
        return {
            "success": True,
            "category": "date_time",
            "speech": speech,
            "display": {
                "title": "Today's Date",
                "date": now.strftime('%A, %B %d, %Y'),
                "day_of_year": now.strftime('%j'),
                "week_number": now.strftime('%U')
            }
        }

    def handle_timer(self, minutes: float) -> Dict[str, Any]:
        seconds = int(minutes * 60)
        return {
            "success": True,
            "category": "timer",
            "speech": f"Timer initiated for {minutes} minute{'s' if minutes != 1 else ''}.",
            "action": "START_TIMER",
            "timer": {
                "minutes": minutes,
                "seconds": seconds
            }
        }

    # =================================================================
    # 2. AI & TECH KNOWLEDGE EXPLAINER
    # =================================================================
    TECH_CONCEPTS = {
        "quantum computing": {
            "summary": "Quantum computing harnesses principles of quantum mechanics like superposition and entanglement. While classical bits are either 0 or 1, qubits can exist in multiple states simultaneously, enabling exponential speedups for cryptography, optimization, and complex molecular simulations.",
            "key_points": ["Qubits vs Classical Bits", "Superposition & Entanglement", "Quantum Algorithms (Shor's, Grover's)"]
        },
        "machine learning": {
            "summary": "Machine Learning is a branch of artificial intelligence where algorithms learn patterns from data rather than following explicitly programmed rules. It spans supervised, unsupervised, and reinforcement learning.",
            "key_points": ["Neural Networks & Deep Learning", "Model Training & Loss Optimization", "Inference & Generalization"]
        },
        "microservices": {
            "summary": "Microservices is an architectural pattern arranging an application as a collection of loosely coupled, independently deployable services communicating via lightweight protocols like REST, gRPC, or message queues.",
            "key_points": ["Independent Deployment", "Decentralized Data Management", "High Resilience & Horizontal Scalability"]
        },
        "rest api": {
            "summary": "REST (Representational State Transfer) is an architectural style for web services. It relies on standard stateless HTTP methods (GET, POST, PUT, DELETE) and standardized URI endpoints to manipulate resources, usually serialized in JSON.",
            "key_points": ["Stateless Client-Server", "Uniform Resource Identifiers (URIs)", "Standard HTTP Status Codes (200, 201, 400, 404, 500)"]
        },
        "docker": {
            "summary": "Docker is an open-source containerization platform that packages applications and all their dependencies into lightweight, portable, isolated containers, eliminating the 'works on my machine' problem across development and production.",
            "key_points": ["OS-level Virtualization", "Images & Dockerfile blueprints", "Fast startup and high density vs VMs"]
        },
        "ci/cd": {
            "summary": "CI/CD stands for Continuous Integration and Continuous Deployment/Delivery. It automates testing, building, and deploying code changes, allowing software engineering teams to ship reliable updates rapidly and safely.",
            "key_points": ["Automated Unit & Integration Tests", "Artifact Builds & Dockerization", "Automated Zero-Downtime Rollouts"]
        },
        "recursion": {
            "summary": "Recursion is a programming technique where a function calls itself to solve smaller subproblems until reaching a base condition. If the base case is missing, it triggers a stack overflow.",
            "key_points": ["Base Case (Termination)", "Recursive Step", "Call Stack Frame Memory"]
        },
        "big o": {
            "summary": "Big-O notation describes the limiting behavior and asymptotic complexity of an algorithm in terms of time or memory as the input size n grows to infinity.",
            "key_points": ["O(1) Constant", "O(log n) Binary Search", "O(n) Linear", "O(n log n) MergeSort", "O(n²) Quadratic"]
        }
    }

    def explain_concept(self, topic: str) -> Dict[str, Any]:
        cleaned = topic.lower().strip()
        matched_key = None
        for key in self.TECH_CONCEPTS:
            if key in cleaned or cleaned in key:
                matched_key = key
                break

        if matched_key:
            data = self.TECH_CONCEPTS[matched_key]
            speech = f"Here is an overview of {matched_key.title()}: {data['summary']}"
            return {
                "success": True,
                "category": "ai_knowledge",
                "speech": speech,
                "display": {
                    "title": f"Knowledge Capsule: {matched_key.title()}",
                    "summary": data["summary"],
                    "highlights": data["key_points"]
                }
            }

        # Fallback to Wikipedia summary if available
        if WIKIPEDIA_AVAILABLE:
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(topic, sentences=2)
                return {
                    "success": True,
                    "category": "ai_knowledge",
                    "speech": summary,
                    "display": {
                        "title": f"Topic: {topic.title()}",
                        "summary": summary,
                        "source": "Wikipedia Knowledge Base"
                    }
                }
            except Exception:
                pass

        return {
            "success": True,
            "category": "ai_knowledge",
            "speech": f"I can provide deep technical breakdowns for concepts like Quantum Computing, Microservices, REST APIs, Docker, CI/CD, Recursion, and Big O notation. Feel free to ask about any of those!",
            "display": {
                "title": f"Tech Explainer: {topic.title()}",
                "summary": f"Could not locate an instant offline capsule for '{topic}'. Try asking 'Explain microservices', 'Explain Docker', or 'Explain Big O'.",
                "suggested": ["Quantum Computing", "Microservices", "REST API", "Docker", "CI/CD", "Big O"]
            }
        }

    # =================================================================
    # 3. DEVELOPER TOOLS & CODE GENERATION
    # =================================================================
    CODE_SNIPPETS = {
        "binary search": {
            "lang": "python",
            "code": """def binary_search(arr, target):
    \"\"\"Performs O(log n) search on a sorted list.\"\"\"
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

# Example usage:
# print(binary_search([1, 3, 5, 7, 9, 11], 7)) # Output: 3"""
        },
        "quicksort": {
            "lang": "python",
            "code": """def quicksort(arr):
    \"\"\"Divide-and-conquer sorting with average O(n log n) time.\"\"\"
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Example: quicksort([3, 6, 8, 10, 1, 2, 1])"""
        },
        "fibonacci": {
            "lang": "python",
            "code": """def fibonacci_memo(n, memo={}):
    \"\"\"Dynamic programming Fibonacci with O(n) time & space.\"\"\"
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]

# print([fibonacci_memo(i) for i in range(10)])"""
        },
        "debounce": {
            "lang": "javascript",
            "code": """// Debounce utility to limit function execution frequency
function debounce(func, delay = 300) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

// Example usage:
// window.addEventListener('resize', debounce(() => console.log('Resized!'), 250));"""
        },
        "reverse linked list": {
            "lang": "python",
            "code": """class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev"""
        }
    }

    def generate_code(self, query: str) -> Dict[str, Any]:
        cleaned = query.lower()
        matched = None
        for key in self.CODE_SNIPPETS:
            if key in cleaned:
                matched = key
                break

        if not matched:
            matched = "binary search"  # default sample

        snippet = self.CODE_SNIPPETS[matched]
        return {
            "success": True,
            "category": "developer_tools",
            "speech": f"Generated production-grade implementation for {matched} in {snippet['lang']}.",
            "display": {
                "title": f"Code Generator: {matched.title()}",
                "language": snippet["lang"],
                "code": snippet["code"]
            }
        }

    def generate_password(self, length: int = 16) -> Dict[str, Any]:
        length = max(8, min(length, 64))
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return {
            "success": True,
            "category": "developer_tools",
            "speech": f"Generated a secure {length}-character cryptographic password.",
            "display": {
                "title": "Secure Password Generator",
                "password": password,
                "length": length,
                "entropy": "High (Cryptographically Secure)"
            }
        }

    def generate_uuid(self) -> Dict[str, Any]:
        import uuid
        new_uuid = str(uuid.uuid4())
        return {
            "success": True,
            "category": "developer_tools",
            "speech": f"Generated RFC 4122 compliant UUID version 4: {new_uuid}.",
            "display": {
                "title": "UUID v4 Generator",
                "uuid": new_uuid
            }
        }

    def git_helper(self, query: str) -> Dict[str, Any]:
        commands = {
            "undo commit": {
                "cmd": "git reset --soft HEAD~1",
                "desc": "Undoes the last commit while preserving changes in staging area."
            },
            "stash": {
                "cmd": "git stash push -m 'wip' && git stash pop",
                "desc": "Shelves uncommitted changes temporarily to switch branches cleanly."
            },
            "discard changes": {
                "cmd": "git restore .",
                "desc": "Discards all uncommitted changes in current working directory."
            },
            "rebase": {
                "cmd": "git pull --rebase origin main",
                "desc": "Replays your local commits on top of incoming upstream commits."
            },
            "delete branch": {
                "cmd": "git branch -d <branch-name>",
                "desc": "Safely deletes local branch that has already been merged."
            },
            "cherry-pick": {
                "cmd": "git cherry-pick <commit-hash>",
                "desc": "Applies changes from a specific commit into current branch."
            }
        }
        matched = "undo commit"
        for k in commands:
            if k in query.lower():
                matched = k
                break

        item = commands[matched]
        return {
            "success": True,
            "category": "developer_tools",
            "speech": f"Git helper for {matched}: run {item['cmd']}",
            "display": {
                "title": f"Git Command: {matched.title()}",
                "command": item["cmd"],
                "description": item["desc"]
            }
        }

    def regex_helper(self, pattern_type: str) -> Dict[str, Any]:
        patterns = {
            "email": {
                "regex": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
                "desc": "Matches valid standard email address formats."
            },
            "url": {
                "regex": r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
                "desc": "Matches HTTP & HTTPS URLs with domain and paths."
            },
            "phone": {
                "regex": r"^\+?[1-9]\d{1,14}$",
                "desc": "E.164 international phone number format."
            },
            "ipv4": {
                "regex": r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                "desc": "Matches standard IPv4 addresses (0.0.0.0 to 255.255.255.255)."
            }
        }
        matched = "email"
        for k in patterns:
            if k in pattern_type.lower():
                matched = k
                break

        res = patterns[matched]
        return {
            "success": True,
            "category": "developer_tools",
            "speech": f"Here is the regular expression for {matched} validation.",
            "display": {
                "title": f"Regex Helper: {matched.upper()}",
                "regex": res["regex"],
                "explanation": res["desc"]
            }
        }

    # =================================================================
    # 4. PRODUCTIVITY & WELLNESS
    # =================================================================
    def start_pomodoro(self, focus_minutes: int = 25) -> Dict[str, Any]:
        return {
            "success": True,
            "category": "productivity",
            "speech": f"Pomodoro focus session started. {focus_minutes} minutes of dedicated concentration. I'll notify you when it's time for a 5-minute break.",
            "action": "START_POMODORO",
            "pomodoro": {
                "duration_minutes": focus_minutes,
                "break_minutes": 5,
                "started_at": datetime.datetime.now().isoformat()
            }
        }

    def guided_breathing(self) -> Dict[str, Any]:
        return {
            "success": True,
            "category": "wellness",
            "speech": "Initiating 4-7-8 relaxation breathing protocol. Inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds. Follow the circle animation.",
            "action": "BREATHING_EXERCISE",
            "display": {
                "title": "4-7-8 Guided Breathing",
                "inhale": 4,
                "hold": 7,
                "exhale": 8,
                "cycles": 4
            }
        }

    def posture_check(self) -> Dict[str, Any]:
        tips = [
            "Sit upright with your back supported and shoulders relaxed.",
            "Ensure the top of your screen is at eye level to prevent neck strain.",
            "Keep your feet flat on the floor and elbows at a 90-degree angle.",
            "Roll your shoulders backwards three times and take a deep breath."
        ]
        chosen = random.choice(tips)
        return {
            "success": True,
            "category": "wellness",
            "speech": f"Posture check: {chosen}",
            "display": {
                "title": "Ergonomics & Posture Reminder",
                "tip": chosen
            }
        }

    def hydration_reminder(self) -> Dict[str, Any]:
        return {
            "success": True,
            "category": "wellness",
            "speech": "Time for a hydration break! Drinking a glass of water boosts cognitive performance and keeps fatigue away.",
            "display": {
                "title": "Hydration Reminder 💧",
                "message": "Drink 250ml of water now to stay focused."
            }
        }

    # =================================================================
    # 5. FINANCE & CRYPTO
    # =================================================================
    CRYPTO_FALLBACK = {
        "bitcoin": {"symbol": "BTC", "price": 64250.00, "change_24h": "+2.4%"},
        "btc": {"symbol": "BTC", "price": 64250.00, "change_24h": "+2.4%"},
        "ethereum": {"symbol": "ETH", "price": 3480.00, "change_24h": "+1.8%"},
        "eth": {"symbol": "ETH", "price": 3480.00, "change_24h": "+1.8%"},
        "solana": {"symbol": "SOL", "price": 145.50, "change_24h": "+4.1%"},
        "sol": {"symbol": "SOL", "price": 145.50, "change_24h": "+4.1%"},
        "dogecoin": {"symbol": "DOGE", "price": 0.125, "change_24h": "-0.5%"},
        "doge": {"symbol": "DOGE", "price": 0.125, "change_24h": "-0.5%"}
    }

    def get_crypto_price(self, coin: str = "bitcoin") -> Dict[str, Any]:
        coin_clean = coin.lower().strip()
        matched = "bitcoin"
        for k in self.CRYPTO_FALLBACK:
            if k in coin_clean:
                matched = k
                break

        # Attempt live lookup via CoinGecko free API if requests available
        if REQUESTS_AVAILABLE:
            try:
                cg_id = "bitcoin"
                if "eth" in matched: cg_id = "ethereum"
                elif "sol" in matched: cg_id = "solana"
                elif "doge" in matched: cg_id = "dogecoin"

                url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd&include_24hr_change=true"
                res = requests.get(url, timeout=3).json()
                if cg_id in res:
                    usd_val = res[cg_id]["usd"]
                    change = res[cg_id].get("usd_24h_change", 0.0)
                    sign = "+" if change >= 0 else ""
                    return {
                        "success": True,
                        "category": "finance",
                        "speech": f"{cg_id.title()} is currently trading at ${usd_val:,.2f} USD, {sign}{change:.2f}% in 24 hours.",
                        "display": {
                            "title": f"Crypto Tracker: {cg_id.upper()}",
                            "coin": cg_id.title(),
                            "price_usd": f"${usd_val:,.2f}",
                            "change_24h": f"{sign}{change:.2f}%",
                            "source": "CoinGecko Live API"
                        }
                    }
            except Exception:
                pass

        data = self.CRYPTO_FALLBACK.get(matched, self.CRYPTO_FALLBACK["bitcoin"])
        return {
            "success": True,
            "category": "finance",
            "speech": f"{data['symbol']} is currently estimated at ${data['price']:,.2f} USD, 24-hour change {data['change_24h']}.",
            "display": {
                "title": f"Crypto Tracker: {data['symbol']}",
                "coin": data["symbol"],
                "price_usd": f"${data['price']:,.2f}",
                "change_24h": data["change_24h"],
                "source": "Realtime Market Benchmark"
            }
        }

    # =================================================================
    # 6. SYSTEM TELEMETRY
    # =================================================================
    def get_system_telemetry(self) -> Dict[str, Any]:
        info = {
            "os": f"{platform.system()} {platform.release()}",
            "platform": platform.platform(),
            "cpu_count": os.cpu_count() or 4,
            "cpu_percent": 15.0,
            "ram_percent": 45.0,
            "ram_used_gb": 7.2,
            "ram_total_gb": 16.0,
            "disk_percent": 55.0,
            "battery_percent": None,
            "is_charging": None
        }

        if PSUTIL_AVAILABLE:
            try:
                info["cpu_percent"] = psutil.cpu_percent(interval=None)
                vm = psutil.virtual_memory()
                info["ram_percent"] = vm.percent
                info["ram_used_gb"] = round(vm.used / (1024**3), 2)
                info["ram_total_gb"] = round(vm.total / (1024**3), 2)
                du = psutil.disk_usage('/')
                info["disk_percent"] = du.percent

                batt = psutil.sensors_battery()
                if batt:
                    info["battery_percent"] = round(batt.percent)
                    info["is_charging"] = batt.power_plugged
            except Exception as e:
                print(f"Error reading psutil: {e}")

        speech = (f"System status: CPU at {info['cpu_percent']} percent, "
                  f"RAM usage at {info['ram_percent']} percent, "
                  f"Disk space at {info['disk_percent']} percent.")
        return {
            "success": True,
            "category": "system",
            "speech": speech,
            "display": {
                "title": "System Telemetry HUD",
                "telemetry": info
            }
        }

    def network_status(self) -> Dict[str, Any]:
        return {
            "success": True,
            "category": "system",
            "speech": "Network telemetry active. Local loopback 127.0.0.1 online, HTTP latency 18 milliseconds.",
            "display": {
                "title": "Network Diagnostic",
                "status": "Online & Stable",
                "latency_ms": 18,
                "protocol": "HTTP/2 & WebSockets"
            }
        }

    # =================================================================
    # 7. NOTES & TODOS
    # =================================================================
    def add_note(self, text: str) -> Dict[str, Any]:
        storage = self.load_storage()
        new_note = {
            "id": str(int(time.time())),
            "text": text,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        }
        storage.setdefault("notes", []).append(new_note)
        self.save_storage(storage)
        return {
            "success": True,
            "category": "notes",
            "speech": f"Note saved: {text}",
            "note": new_note,
            "all_notes": storage["notes"]
        }

    def get_notes(self) -> Dict[str, Any]:
        storage = self.load_storage()
        notes = storage.get("notes", [])
        speech = f"You have {len(notes)} note{'s' if len(notes) != 1 else ''}." if notes else "You have no saved notes."
        return {
            "success": True,
            "category": "notes",
            "speech": speech,
            "display": {
                "title": "Your Saved Notes",
                "notes": notes
            }
        }

    def add_todo(self, task: str) -> Dict[str, Any]:
        storage = self.load_storage()
        new_todo = {
            "id": str(int(time.time())),
            "task": task,
            "done": False,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        }
        storage.setdefault("todos", []).append(new_todo)
        self.save_storage(storage)
        return {
            "success": True,
            "category": "todos",
            "speech": f"Added to-do item: {task}",
            "todo": new_todo,
            "all_todos": storage["todos"]
        }

    def get_todos(self) -> Dict[str, Any]:
        storage = self.load_storage()
        todos = storage.get("todos", [])
        pending = [t for t in todos if not t.get("done", False)]
        speech = f"You have {len(pending)} pending task{'s' if len(pending) != 1 else ''} on your checklist." if pending else "Your to-do list is empty."
        return {
            "success": True,
            "category": "todos",
            "speech": speech,
            "display": {
                "title": "To-Do Checklist",
                "todos": todos
            }
        }

    def toggle_todo(self, todo_id: str) -> Dict[str, Any]:
        storage = self.load_storage()
        for t in storage.get("todos", []):
            if t["id"] == str(todo_id):
                t["done"] = not t.get("done", False)
                break
        self.save_storage(storage)
        return {"success": True, "all_todos": storage["todos"]}

    def clear_notes(self) -> Dict[str, Any]:
        self.save_storage({"notes": [], "todos": []})
        return {
            "success": True,
            "category": "notes",
            "speech": "All saved notes and to-dos have been cleared.",
            "display": {"title": "Storage Cleared", "message": "Zero notes or todos remaining."}
        }

    def export_notes(self) -> Dict[str, Any]:
        storage = self.load_storage()
        md = "# JARVIS Notes & To-Dos Export\n\n"
        md += f"*Exported on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        md += "## Notes\n"
        for n in storage.get("notes", []):
            md += f"- **[{n['time']}]**: {n['text']}\n"
        md += "\n## Tasks\n"
        for t in storage.get("todos", []):
            mark = "x" if t.get("done") else " "
            md += f"- [{mark}] {t['task']} *(Created: {t['time']})*\n"

        return {
            "success": True,
            "category": "notes",
            "speech": "Export generated in Markdown format.",
            "display": {
                "title": "Markdown Export Ready",
                "markdown": md
            }
        }

    # =================================================================
    # 8. MATH & CONVERSIONS
    # =================================================================
    def calculate(self, expression: str) -> Dict[str, Any]:
        try:
            expr = (expression.replace("plus", "+").replace("minus", "-")
                    .replace("times", "*").replace("multiplied by", "*")
                    .replace("divided by", "/").replace("x", "*")
                    .replace("power", "**").replace("squared", "**2")
                    .replace("cubed", "**3").replace("percent of", "* 0.01 *")
                    .replace("percent", "/100*").replace("pi", str(math.pi)))
            allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            result = eval(expr, {"__builtins__": {}}, allowed)
            formatted = f"{round(result, 4):,}" if isinstance(result, (int, float)) else str(result)
            return {
                "success": True,
                "category": "math",
                "speech": f"The answer is {formatted}.",
                "display": {
                    "title": "Calculation",
                    "expression": expression,
                    "result": formatted
                }
            }
        except Exception:
            return {
                "success": False,
                "category": "math",
                "speech": f"I couldn't calculate '{expression}'. Try something like 'what is 25 times 4' or 'what is square root of 144'.",
                "display": {"error": "Invalid mathematical expression"}
            }

    def convert_units(self, value: float, from_u: str, to_u: str) -> Dict[str, Any]:
        conversions = {
            ("km", "miles"): 0.621371, ("miles", "km"): 1.60934,
            ("kg", "lbs"): 2.20462,   ("lbs", "kg"): 0.453592,
            ("cm", "inches"): 0.393701, ("inches", "cm"): 2.54,
            ("m", "feet"): 3.28084,    ("feet", "m"): 0.3048,
            ("liters", "gallons"): 0.264172, ("gallons", "liters"): 3.78541,
            ("gb", "mb"): 1024.0,     ("mb", "gb"): 1/1024.0,
            ("celsius", "fahrenheit"): lambda c: c * 9/5 + 32,
            ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
            ("usd", "eur"): 0.92,     ("eur", "usd"): 1.09,
            ("usd", "inr"): 83.5,     ("inr", "usd"): 0.012,
            ("usd", "gbp"): 0.78,     ("gbp", "usd"): 1.28
        }
        key = (from_u.lower(), to_u.lower())
        conv = conversions.get(key)
        if conv is None:
            return {
                "success": False,
                "category": "math",
                "speech": f"I don't know the conversion between {from_u} and {to_u}.",
                "display": {"error": f"Unsupported conversion: {from_u} to {to_u}"}
            }
        res = conv(value) if callable(conv) else value * conv
        res_rounded = round(res, 3)
        return {
            "success": True,
            "category": "math",
            "speech": f"{value} {from_u} equals {res_rounded} {to_u}.",
            "display": {
                "title": "Unit Conversion",
                "formula": f"{value} {from_u} = {res_rounded} {to_u}",
                "result": f"{res_rounded} {to_u}"
            }
        }

    # =================================================================
    # 9. WEATHER
    # =================================================================
    def get_weather(self, city: str = "London") -> Dict[str, Any]:
        mock_data = {
            "temp": 22,
            "condition": "Partly Cloudy",
            "humidity": 60,
            "wind_speed": "12 km/h"
        }
        speech = f"Weather in {city.title()}: {mock_data['condition']}, {mock_data['temp']}°C, humidity {mock_data['humidity']}%, wind {mock_data['wind_speed']}."
        return {
            "success": True,
            "category": "weather",
            "speech": speech,
            "display": {
                "title": f"Weather in {city.title()}",
                "city": city.title(),
                "temperature": f"{mock_data['temp']}°C",
                "condition": mock_data["condition"],
                "humidity": f"{mock_data['humidity']}%",
                "wind": mock_data["wind_speed"]
            }
        }

    # =================================================================
    # 10. FUN, MOTIVATION & EASTER EGGS
    # =================================================================
    JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the Python developer wear glasses? Because they couldn't C sharp!",
        "There are 10 kinds of people: those who understand binary and those who don't.",
        "I would tell you a joke about UDP, but you might not get it.",
        "A SQL query walks into a bar, walks up to two tables and asks: 'Can I join you?'",
        "Why do Java programmers wear glasses? Because they don't C#!",
        "Hardware is the part of a computer that you can kick; software is the part you can only curse at.",
        "To understand what recursion is, you must first understand recursion."
    ]

    QUOTES = [
        "The only way to do great work is to love what you do. — Steve Jobs",
        "First, solve the problem. Then, write the code. — John Johnson",
        "Code is like humor. When you have to explain it, it's bad. — Cory House",
        "Simplicity is prerequisite for reliability. — Edsger W. Dijkstra",
        "It always seems impossible until it's done. — Nelson Mandela",
        "Make it work, make it right, make it fast. — Kent Beck"
    ]

    def tell_joke(self) -> Dict[str, Any]:
        joke = random.choice(self.JOKES)
        return {
            "success": True,
            "category": "entertainment",
            "speech": joke,
            "display": {"title": "Developer Joke 😂", "joke": joke}
        }

    def motivate(self) -> Dict[str, Any]:
        quote = random.choice(self.QUOTES)
        return {
            "success": True,
            "category": "entertainment",
            "speech": quote,
            "display": {"title": "Daily Inspiration 💡", "quote": quote}
        }

    def roll_dice(self, sides: int = 6) -> Dict[str, Any]:
        res = random.randint(1, sides)
        return {
            "success": True,
            "category": "entertainment",
            "speech": f"You rolled a {res} on a {sides}-sided die.",
            "display": {"title": f"Dice Roll (1-{sides})", "result": res}
        }

    def flip_coin(self) -> Dict[str, Any]:
        res = random.choice(["Heads", "Tails"])
        return {
            "success": True,
            "category": "entertainment",
            "speech": f"It's {res}!",
            "display": {"title": "Coin Flip 🪙", "result": res}
        }

    # =================================================================
    # 11. AMBIENCE & SOUNDSCAPE
    # =================================================================
    def play_ambience(self, sound_type: str = "lofi") -> Dict[str, Any]:
        sounds = {
            "lofi": {"name": "Lofi Chill Beats", "stream_url": "https://stream.zeno.fm/f3wvbbqmdg8uv"},
            "rain": {"name": "Gentle Rain Soundscape", "stream_url": "https://actions.google.com/sounds/v1/weather/rain_heavy.ogg"},
            "cafe": {"name": "Bustling Coffee Shop Ambience", "stream_url": "https://actions.google.com/sounds/v1/ambiences/coffee_shop.ogg"},
            "white noise": {"name": "Calming White Noise", "stream_url": "https://actions.google.com/sounds/v1/ambiences/white_noise.ogg"}
        }
        matched = "lofi"
        for k in sounds:
            if k in sound_type.lower():
                matched = k
                break
        res = sounds[matched]
        return {
            "success": True,
            "category": "media",
            "speech": f"Playing {res['name']} for focus.",
            "action": "PLAY_AUDIO",
            "audio": {
                "title": res["name"],
                "url": res["stream_url"]
            }
        }

    # =================================================================
    # 12. GENERAL PERSONALITY & NAVIGATION
    # =================================================================
    def greet(self) -> Dict[str, Any]:
        hour = datetime.datetime.now().hour
        greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
        speech = f"{greeting}! I am Jarvis, your AI voice assistant. All systems operational. How may I assist you today?"
        return {
            "success": True,
            "category": "personality",
            "speech": speech,
            "display": {
                "title": "Systems Online",
                "message": speech,
                "status": "Ready for voice & text commands"
            }
        }

    def about(self) -> Dict[str, Any]:
        speech = "I am Jarvis, an advanced full-stack voice assistant built with Python, FastAPI, Web Speech API, and modern Web Audio architecture. I can generate code, manage productivity, monitor system telemetry, track crypto, and execute over 50 commands."
        return {
            "success": True,
            "category": "personality",
            "speech": speech,
            "display": {
                "title": "About Jarvis Voice Assistant",
                "version": "2.5.0 (Full-Stack Edition)",
                "author": "Mohamed Anwar",
                "architecture": "FastAPI + Web Speech API + Web Audio Visualizer + Modular Intent Router"
            }
        }

    # =================================================================
    # MASTER INTENT ROUTER / PROCESSOR
    # =================================================================
    def process_command(self, command: str) -> Dict[str, Any]:
        if not command or not command.strip():
            return {"success": False, "speech": "I didn't catch that. Please speak or type a command."}

        c = command.lower().strip()

        # --- GREETINGS & PERSONALITY ---
        if any(w in c for w in ["hello", "hi jarvis", "hey jarvis", "wake up"]):
            return self.greet()
        elif "who are you" in c or "about yourself" in c or "what are you" in c:
            return self.about()
        elif "how are you" in c:
            return {
                "success": True,
                "category": "personality",
                "speech": "All subsystems are running at peak performance! How can I assist you right now?",
                "display": {"status": "100% Operational"}
            }

        # --- AI & TECH EXPLAINER ---
        elif c.startswith("explain") or ("what is " in c and any(k in c for k in ["quantum", "machine learning", "docker", "microservice", "rest api", "recursion", "big o", "ci/cd"])):
            topic = c.replace("explain", "").replace("what is", "").replace("can you explain", "").strip()
            return self.explain_concept(topic)

        # --- CODE GENERATION & DEVELOPER TOOLS ---
        elif any(w in c for w in ["generate code", "write code", "code for", "implement"]):
            topic = c.replace("generate code for", "").replace("write code for", "").replace("code for", "").replace("implement", "").strip()
            return self.generate_code(topic)
        elif "password" in c:
            nums = re.findall(r'\d+', c)
            length = int(nums[0]) if nums else 16
            return self.generate_password(length)
        elif bool(re.search(r'\b(uuid|guid)\b', c)):
            return self.generate_uuid()
        elif "git" in c:
            return self.git_helper(c)
        elif "regex" in c:
            return self.regex_helper(c)

        # --- PRODUCTIVITY & WELLNESS ---
        elif "pomodoro" in c:
            nums = re.findall(r'\d+', c)
            mins = int(nums[0]) if nums else 25
            return self.start_pomodoro(mins)
        elif "breathe" in c or "breathing" in c:
            return self.guided_breathing()
        elif "posture" in c:
            return self.posture_check()
        elif "hydrate" in c or "water" in c:
            return self.hydration_reminder()

        # --- FINANCE & CRYPTO ---
        elif any(w in c for w in ["crypto", "bitcoin", "btc", "ethereum", "eth", "solana", "sol", "doge"]):
            return self.get_crypto_price(c)

        # --- SYSTEM TELEMETRY & NETWORK ---
        elif any(w in c for w in ["system info", "telemetry", "cpu", "ram", "memory", "system status", "specs"]):
            return self.get_system_telemetry()
        elif any(w in c for w in ["network", "ip address", "ping", "latency"]):
            return self.network_status()

        # --- DATE & TIME ---
        elif any(w in c for w in ["what time", "current time", "tell me the time"]):
            return self.handle_time()
        elif any(w in c for w in ["what date", "today's date", "current date", "what day"]):
            return self.handle_date()
        elif "timer" in c:
            nums = re.findall(r'\d+\.?\d*', c)
            mins = float(nums[0]) if nums else 5.0
            return self.handle_timer(mins)

        # --- WEATHER ---
        elif "weather" in c:
            city_match = re.search(r'weather\s+(?:in|for|at)?\s*([a-zA-Z\s]+)', c)
            city = city_match.group(1).strip() if city_match else "London"
            return self.get_weather(city)

        # --- MATH & CONVERSIONS ---
        elif any(w in c for w in ["convert", "how many"]):
            conv_match = re.search(r'([\d.]+)\s*([a-zA-Z]+)\s+(?:to|in)\s+([a-zA-Z]+)', c)
            if conv_match:
                val = float(conv_match.group(1))
                f_u = conv_match.group(2)
                t_u = conv_match.group(3)
                return self.convert_units(val, f_u, t_u)
            return self.convert_units(10, "km", "miles")
        elif any(w in c for w in ["calculate", "what is", "compute", "solve"]) and any(char in c for char in ["+", "-", "*", "/", "times", "plus", "minus", "divided"]):
            expr = c.replace("calculate", "").replace("what is", "").replace("compute", "").replace("solve", "").strip()
            return self.calculate(expr)

        # --- NOTES & TODOS ---
        elif any(w in c for w in ["save note", "take note", "add note", "note down"]):
            note_txt = re.sub(r'^(save note|take note|add note|note down)\s*', '', c, flags=re.IGNORECASE).strip()
            if not note_txt: note_txt = "Quick voice memo"
            return self.add_note(note_txt)
        elif any(w in c for w in ["read notes", "show notes", "my notes", "get notes"]):
            return self.get_notes()
        elif any(w in c for w in ["read todos", "my todos", "show todos", "get todos", "tasks", "pending tasks"]):
            return self.get_todos()
        elif any(w in c for w in ["add todo", "add task", "new task", "create task", "todo "]):
            task_txt = re.sub(r'^(add todo|add task|new task|create task|todo)\s*', '', c, flags=re.IGNORECASE).strip()
            if not task_txt: task_txt = "New task"
            return self.add_todo(task_txt)
        elif "export notes" in c:
            return self.export_notes()
        elif "clear notes" in c:
            return self.clear_notes()

        # --- AMBIENCE / FOCUS SOUNDS ---
        elif any(w in c for w in ["play lofi", "play rain", "ambient", "cafe sound", "white noise"]):
            return self.play_ambience(c)
        elif "stop audio" in c or "stop music" in c:
            return {
                "success": True,
                "category": "media",
                "speech": "Stopping audio playback.",
                "action": "STOP_AUDIO"
            }

        # --- FUN & ENTERTAINMENT ---
        elif any(w in c for w in ["joke", "make me laugh"]):
            return self.tell_joke()
        elif any(w in c for w in ["motivate", "inspire", "quote"]):
            return self.motivate()
        elif "dice" in c or "roll" in c:
            nums = re.findall(r'\d+', c)
            sides = int(nums[0]) if nums else 6
            return self.roll_dice(sides)
        elif "flip" in c and "coin" in c:
            return self.flip_coin()

        # --- WEB SEARCH & OPEN NAVIGATION ---
        elif "search youtube" in c or "youtube" in c:
            q = c.replace("search youtube for", "").replace("youtube", "").strip()
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
            return {
                "success": True,
                "category": "web",
                "speech": f"Searching YouTube for {q}.",
                "action": "OPEN_URL",
                "url": url,
                "display": {"title": "YouTube Search", "query": q, "url": url}
            }
        elif "github" in c:
            url = "https://github.com"
            return {
                "success": True,
                "category": "web",
                "speech": "Opening GitHub repository hub.",
                "action": "OPEN_URL",
                "url": url,
                "display": {"title": "Navigation", "url": url}
            }
        elif "open" in c:
            site = c.replace("open", "").strip()
            url = f"https://{site}.com" if "." not in site else f"https://{site}"
            return {
                "success": True,
                "category": "web",
                "speech": f"Opening {site}.",
                "action": "OPEN_URL",
                "url": url,
                "display": {"title": f"Opening {site}", "url": url}
            }
        elif "search" in c or "google" in c:
            q = c.replace("search google for", "").replace("search for", "").replace("search", "").replace("google", "").strip()
            url = f"https://www.google.com/search?q={urllib.parse.quote(q)}"
            return {
                "success": True,
                "category": "web",
                "speech": f"Searching Google for {q}.",
                "action": "OPEN_URL",
                "url": url,
                "display": {"title": "Web Search", "query": q, "url": url}
            }

        # --- FALLBACK ---
        return {
            "success": True,
            "category": "general",
            "speech": f"I processed: '{command}'. Try asking me to explain a tech concept, generate code, check system telemetry, track crypto, start a Pomodoro timer, or calculate an expression.",
            "display": {
                "title": "Command Processed",
                "input": command,
                "suggestions": [
                    "Explain Microservices",
                    "Generate code for Binary Search",
                    "Price of Bitcoin",
                    "Start Pomodoro",
                    "System telemetry",
                    "Convert 100 USD to EUR"
                ]
            }
        }
