#!/usr/bin/env python3
"""
RedGuardAI Heartbeat Daemon - Entry Point
Backward-compatible wrapper for the modular heartbeat package.

Usage:
    python heartbeat.py          # Run daemon
    python heartbeat.py --once   # Single cycle
"""

import argparse
import sys
from pathlib import Path

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).parent))

from heartbeat import run_daemon, heartbeat_once, CONFIG
from heartbeat.config import COMMENT_INTERVAL_MINUTES


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RedGuardAI Heartbeat")
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=COMMENT_INTERVAL_MINUTES,
                        help=f'Minutes between cycles (default: {COMMENT_INTERVAL_MINUTES})')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Log full generated content to logs/content.jsonl')
    args = parser.parse_args()

    if args.verbose:
        CONFIG['verbose'] = True

    if args.once:
        heartbeat_once()
    else:
        run_daemon(args.interval)
