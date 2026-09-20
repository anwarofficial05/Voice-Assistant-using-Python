"""
Quick launcher script for JARVIS Voice Assistant Web Server.
Run:
    python run_server.py
"""

import sys
import webbrowser
import threading
import time
import uvicorn

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def open_browser():
    time.sleep(1.8)
    print("\n[Web Browser] Opening JARVIS Web Dashboard: http://localhost:8000 ...")
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass

if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    print("=" * 65)
    print("  [*] JARVIS Full-Stack Voice Assistant & AI Platform")
    print("  [*] Host: http://localhost:8000")
    print("  [*] API Docs: http://localhost:8000/api/docs")
    print("=" * 65)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

