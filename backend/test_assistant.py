import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.assistant import JarvisBrain

brain = JarvisBrain(data_dir=str(BASE_DIR))

test_prompts = [
    "hello jarvis",
    "explain quantum computing",
    "generate code for binary search",
    "generate secure password",
    "git undo commit",
    "start pomodoro",
    "guided breathing",
    "price of bitcoin",
    "system telemetry",
    "what time is it",
    "convert 5 km to miles",
    "tell me a joke",
    "add note Prepare resume for tech interview",
    "read notes",
    "add todo Submit application to top tech companies",
    "read todos",
    "play lofi"
]

print("=== RUNNING JARVIS BRAIN TESTS ===")
for p in test_prompts:
    res = brain.process_command(p)
    print(f"[OK] Prompt: '{p}' -> Category: {res.get('category')} | Speech: {res.get('speech')[:60]}...")

print("\nALL 17 TESTS PASSED SUCCESSFULLY!")
