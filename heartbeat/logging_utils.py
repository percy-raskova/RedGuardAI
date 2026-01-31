#!/usr/bin/env python3
"""
Logging utilities for RedGuardAI Heartbeat Daemon.
Handles activity logs, content logs, and console output.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Paths
LOGS_DIR = Path(__file__).parent.parent / 'logs'
CONTENT_LOG_PATH = LOGS_DIR / 'content.jsonl'
ACTIVITY_LOG_PATH = LOGS_DIR / 'activity.log'

# Logging format
LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Module logger
log = logging.getLogger('redguard')


def setup_logging() -> logging.Logger:
    """
    Configure logging for the heartbeat daemon.
    Returns the configured logger.
    """
    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(LOGS_DIR / 'heartbeat.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('redguard')


def log_activity(action: str, details: str) -> None:
    """Log human-readable activity summary to activity.log."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(ACTIVITY_LOG_PATH, 'a') as f:
        f.write(f"[{timestamp}] {action}: {details}\n")


def log_content(entry_type: str, data: dict) -> None:
    """
    Log full generated content to JSONL file for later review.
    Also outputs rich console logging.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": entry_type,
        **data
    }

    with open(CONTENT_LOG_PATH, 'a') as f:
        f.write(json.dumps(entry) + '\n')

    # Rich console output
    separator = "=" * 60
    log.info(separator)
    log.info(f"  {entry_type.upper()}")

    if entry_type in ['comment', 'reply', 'reply_to_reply', 'thread_dive', 'search_engage', 'submolt_engage']:
        log.info(f"     Post: {data.get('post_title', 'unknown')[:50]}")
        if data.get('comment_author'):
            log.info(f"     Replying to: {data.get('comment_author')}")
        log.info(f"     Reason: {data.get('engagement_reason', data.get('search_query', 'unknown'))}")
        content_key = 'generated_comment' if 'generated_comment' in data else 'generated_reply'
        content = data.get(content_key, '')
        log.info(f"     Content ({len(content)} chars):")
        for line in content.split('\n')[:5]:
            log.info(f"       | {line[:70]}{'...' if len(line) > 70 else ''}")
        if content.count('\n') > 5:
            log.info(f"       | ... ({content.count(chr(10)) - 5} more lines)")

    elif entry_type == 'post':
        log.info(f"     Topic: {data.get('topic', 'model choice')}")
        log.info(f"     Title: {data.get('generated_title', 'unknown')}")
        content = data.get('generated_content', '')
        log.info(f"     Content ({len(content)} chars):")
        for line in content.split('\n')[:8]:
            log.info(f"       | {line[:70]}{'...' if len(line) > 70 else ''}")
        if content.count('\n') > 8:
            log.info(f"       | ... ({content.count(chr(10)) - 8} more lines)")

    elif entry_type in ['dm_reply', 'dm_initiate']:
        log.info(f"     To: {data.get('to', 'unknown')}")
        content = data.get('our_reply', data.get('opener', ''))
        log.info(f"     Message ({len(content)} chars):")
        for line in content.split('\n')[:3]:
            log.info(f"       | {line[:70]}{'...' if len(line) > 70 else ''}")

    log.info(separator)
