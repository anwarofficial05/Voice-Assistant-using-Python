"""
===================================================================
  JARVIS Web Voice Assistant - FastAPI Application Server
  Author: Mohamed Anwar
  Endpoints: REST API, Telemetry stream, Static Frontend Mount
===================================================================
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from backend.assistant import JarvisBrain

app = FastAPI(
    title="JARVIS Voice Assistant API",
    description="Full-Stack Real-Time Voice Assistant & Command Execution Engine",
    version="2.5.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Setup for unrestricted web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Assistant Brain
brain = JarvisBrain(data_dir=str(BASE_DIR))


class CommandPayload(BaseModel):
    command: str
    client_timestamp: Optional[str] = None


class NotePayload(BaseModel):
    text: str


class TodoPayload(BaseModel):
    task: str


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "assistant": "JARVIS",
        "version": "2.5.0",
        "os": brain.os_type
    }


@app.post("/api/command")
def execute_command(payload: CommandPayload):
    """Processes user voice or text input and routes to appropriate intent handler."""
    cmd = payload.command.strip()
    if not cmd:
        raise HTTPException(status_code=400, detail="Command cannot be empty")

    result = brain.process_command(cmd)
    return result


@app.get("/api/telemetry")
def get_telemetry():
    """Returns live hardware and system telemetry metrics."""
    return brain.get_system_telemetry()


@app.get("/api/notes")
def get_notes():
    """Retrieves all saved user notes."""
    return brain.get_notes()


@app.post("/api/notes")
def add_note(payload: NotePayload):
    """Saves a new note."""
    return brain.add_note(payload.text)


@app.get("/api/todos")
def get_todos():
    """Retrieves all checklist tasks."""
    return brain.get_todos()


@app.post("/api/todos")
def add_todo(payload: TodoPayload):
    """Adds a new checklist task."""
    return brain.add_todo(payload.task)


@app.post("/api/todos/{todo_id}/toggle")
def toggle_todo(todo_id: str):
    """Toggles completed state for a task."""
    return brain.toggle_todo(todo_id)


@app.delete("/api/clear")
def clear_all():
    """Clears all saved notes and to-dos."""
    return brain.clear_notes()


@app.get("/api/export")
def export_notes():
    """Exports notes and tasks as formatted markdown."""
    return brain.export_notes()


@app.get("/api/crypto/{coin}")
def crypto_price(coin: str):
    """Returns current market pricing for requested crypto asset."""
    return brain.get_crypto_price(coin)


@app.get("/api/quick-actions")
def get_quick_actions():
    """Provides categorized quick-test prompts for instant evaluation."""
    return {
        "categories": [
            {
                "name": "AI & Tech Knowledge",
                "prompts": [
                    "Explain Quantum Computing",
                    "Explain Microservices",
                    "Explain Docker containerization",
                    "Explain Big O notation"
                ]
            },
            {
                "name": "Developer Tools",
                "prompts": [
                    "Generate code for Binary Search",
                    "Generate code for Quicksort",
                    "Generate secure password",
                    "Git undo commit",
                    "Regex for email"
                ]
            },
            {
                "name": "Productivity & Health",
                "prompts": [
                    "Start Pomodoro",
                    "Guided breathing",
                    "Posture check",
                    "Hydration reminder"
                ]
            },
            {
                "name": "Finance & Markets",
                "prompts": [
                    "Price of Bitcoin",
                    "Price of Ethereum",
                    "Convert 100 USD to EUR"
                ]
            },
            {
                "name": "System & Media",
                "prompts": [
                    "System telemetry",
                    "Network ping status",
                    "Play lofi chill beats",
                    "Tell me a developer joke"
                ]
            }
        ]
    }


# Mount Frontend Static Assets
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_frontend_root():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "Frontend index.html not found, but API is live!"}


if __name__ == "__main__":
    import uvicorn
    print("[*] Initializing JARVIS Voice Assistant Server at http://localhost:8000 ...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
