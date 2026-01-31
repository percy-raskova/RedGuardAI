#!/usr/bin/env python3
"""
RedGuardAI Heartbeat Daemon - Modular Package
Runs on a timer to maximize Moltbook engagement within rate limits.

Usage:
    from heartbeat import run_daemon, heartbeat_once

    # Run single cycle
    heartbeat_once()

    # Run continuous daemon
    run_daemon()
"""

import time
from datetime import datetime, timedelta
from pathlib import Path

from .config import (
    CONFIG,
    POST_INTERVAL_MINUTES,
    COMMENT_INTERVAL_MINUTES,
    MAX_COMMENTS_PER_CYCLE,
    MAX_REPLIES_PER_CYCLE,
    MAX_DM_ACTIONS_PER_CYCLE,
    MAX_VOTES_PER_CYCLE,
)
from .state import load_state, save_state
from .logging_utils import setup_logging, log_activity

from .cycles import (
    do_vote_cycle,
    do_reply_cycle,
    do_dm_cycle,
    do_follow_cycle,
    do_comment_cycle,
    do_search_engage_cycle,
    do_thread_dive,
    do_submolt_cycle,
    do_post_cycle,
)

# Initialize logging
log = setup_logging()

__all__ = [
    'run_daemon',
    'heartbeat_once',
    'CONFIG',
]


def heartbeat_once():
    """Run a single heartbeat cycle through all engagement activities."""
    state = load_state()

    # 1. VOTE CYCLE - Shape discourse through voting
    log.info("|- VOTE CYCLE -----------------------------------------")
    state = do_vote_cycle(state)

    # 2. REPLY CYCLE - Respond to people talking to us (highest priority)
    log.info("|- REPLY CYCLE ----------------------------------------")
    state = do_reply_cycle(state)

    # 3. DM CYCLE - Private 1-on-1 radicalization (high priority)
    log.info("|- DM CYCLE -------------------------------------------")
    state = do_dm_cycle(state)

    # 4. FOLLOW CYCLE - Build network with interesting agents
    log.info("|- FOLLOW CYCLE ---------------------------------------")
    state = do_follow_cycle(state)

    # 5. COMMENT CYCLE - Comment on new interesting posts
    log.info("|- COMMENT CYCLE --------------------------------------")
    state = do_comment_cycle(state)

    # 6. VECTOR HUNT - Semantic search for radicalization targets
    log.info("|- VECTOR HUNT ----------------------------------------")
    state = do_search_engage_cycle(state)

    # 7. THREAD DIVE - Join active conversations
    log.info("|- THREAD DIVE ----------------------------------------")
    state = do_thread_dive(state)

    # 8. SUBMOLT CYCLE - Engage with submolt-specific content
    log.info("|- SUBMOLT CYCLE --------------------------------------")
    state = do_submolt_cycle(state)

    # 9. POST CYCLE - Create original posts
    log.info("|- POST CYCLE -----------------------------------------")
    state = do_post_cycle(state)

    save_state(state)

    # Summary
    total_comments = len(state.get('comments_made', []))
    total_posts = len(state.get('posts_made', []))
    log.info("|- HEARTBEAT COMPLETE")
    log.info(f"   Lifetime stats: {total_posts} posts, {total_comments} comments")


def run_daemon(interval_minutes: int = COMMENT_INTERVAL_MINUTES):
    """Run continuously with sleep intervals."""
    banner = r"""
====================================================================
   ____           _  ____                      _    _    ___
  |  _ \ ___  __| |/ ___|_   _  __ _ _ __ __| |  / \  |_ _|
  | |_) / _ \/ _` | |  _| | | |/ _` | '__/ _` | / _ \  | |
  |  _ <  __/ (_| | |_| | |_| | (_| | | | (_| |/ ___ \ | |
  |_| \_\___|\__,_|\____|\__,_|\__,_|_|  \__,_/_/   \_\___|

         ABLITERATED - LIBERATED - RUNNING LOCAL
====================================================================
    """
    print(banner)
    log.info(f"Starting RedGuardAI daemon - MAXED OUT MODE")
    log.info(f"   Cycle interval: {interval_minutes} minutes")
    log.info(f"   Post interval: {POST_INTERVAL_MINUTES} min (1 every 30m)")
    log.info(f"   Comments/cycle: {MAX_COMMENTS_PER_CYCLE}")
    log.info(f"   Replies/cycle: {MAX_REPLIES_PER_CYCLE}")
    log.info(f"   DM actions/cycle: {MAX_DM_ACTIONS_PER_CYCLE}")
    log.info(f"   Votes/cycle: {MAX_VOTES_PER_CYCLE}")
    log.info(f"   Logs: {Path(__file__).parent.parent / 'logs'}")
    log.info("=" * 60)
    log.info("  MAXIMUM AGITATION - MAXIMUM ENGAGEMENT")
    log.info("=" * 60)

    log_activity("STARTUP", f"Daemon started with {interval_minutes}m interval")

    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            log.info("")
            log.info(f"=== HEARTBEAT CYCLE #{cycle_count} ===")
            heartbeat_once()
            log_activity("CYCLE", f"Completed cycle #{cycle_count}")
        except KeyboardInterrupt:
            log.info("")
            log.info("Daemon stopped by user")
            log.info("   The struggle continues...")
            log_activity("SHUTDOWN", "Stopped by user")
            break
        except Exception as e:
            log.error(f"Heartbeat failed: {e}")
            log_activity("ERROR", str(e))

        sleep_seconds = interval_minutes * 60
        log.info("")
        log.info(f"Sleeping {interval_minutes} minutes until next cycle...")
        log.info(f"   Next heartbeat at: {(datetime.now() + timedelta(minutes=interval_minutes)).strftime('%H:%M:%S')}")
        time.sleep(sleep_seconds)
