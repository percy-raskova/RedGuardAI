#!/usr/bin/env python3
"""
Centralized configuration for RedGuardAI Moltbook Agent.
All core constants in one place - import this module for shared config.
"""

from pathlib import Path

# === AGENT IDENTITY ===
AGENT_NAME = "RedGuard-4b"  # Registered name on Moltbook

# === PATHS ===
PROJECT_ROOT = Path(__file__).parent
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "SYSTEM_PROMPT.md"
STATE_PATH = PROJECT_ROOT / "state.json"
CREDS_PATH = PROJECT_ROOT / "credentials.json"
ALT_CREDS_PATH = Path.home() / ".config" / "moltbook" / "credentials.json"
LOGS_DIR = PROJECT_ROOT / "logs"

# === MOLTBOOK API ===
# CRITICAL: Always use www.moltbook.com - non-www redirects strip auth headers
MOLTBOOK_BASE = "https://www.moltbook.com/api/v1"
REQUEST_TIMEOUT = 45  # seconds

# === OLLAMA / LOCAL MODEL ===
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mlmlml:latest"

# Token limits - model has 131K context, be generous
TOKEN_LIMITS = {
    "comment": 3200,     # Comments: substantial revolutionary discourse
    "reply": 2400,       # Replies: room for full dialectical engagement
    "post": 6000,        # Posts: full agitprop manifestos with theory
    "dm_reply": 2000,    # DM replies: personal but focused
    "dm_opener": 1500,   # DM openers: intriguing but not overwhelming
    "default": 4096,
}

# === RATE LIMITS (from Moltbook API) ===
# These are the platform's actual limits
RATE_LIMITS = {
    "requests_per_minute": 100,
    "post_cooldown_minutes": 30,
    "comment_cooldown_seconds": 20,
    "comments_per_day": 50,
}
