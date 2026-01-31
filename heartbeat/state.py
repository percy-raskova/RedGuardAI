#!/usr/bin/env python3
"""
State management utilities for RedGuardAI Heartbeat Daemon.
Handles loading, saving, and querying persistent state.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from .config import POST_INTERVAL_MINUTES

# State file path
STATE_PATH = Path(__file__).parent.parent / "state.json"


def load_state() -> dict:
    """Load agent state from disk."""
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    """Save agent state to disk."""
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)


def should_post(state: dict) -> bool:
    """Check if enough time has passed to post again."""
    last_post = state.get('last_post_time')
    if not last_post:
        return True
    last_post_dt = datetime.fromisoformat(last_post)
    elapsed = datetime.now() - last_post_dt
    return elapsed > timedelta(minutes=POST_INTERVAL_MINUTES)


def get_commented_post_ids(state: dict) -> set:
    """Get set of post IDs we've already commented on."""
    return {c.get('post_id') for c in state.get('comments_made', []) if c.get('post_id')}


def get_replied_comment_ids(state: dict) -> set:
    """Get set of comment IDs we've already replied to."""
    return {c.get('parent_id') for c in state.get('comments_made', []) if c.get('parent_id')}


def get_our_comment_ids(state: dict) -> set:
    """Get set of comment IDs we've made."""
    return {c.get('comment_id') for c in state.get('comments_made', []) if c.get('comment_id')}


def get_our_post_ids(state: dict) -> set:
    """Get set of post IDs we've made."""
    ids = set()
    for p in state.get('posts_made', []):
        result = p.get('result', {})
        post_id = result.get('post', {}).get('id') or result.get('id')
        if post_id:
            ids.add(post_id)
    return ids


def get_voted_post_ids(state: dict) -> set:
    """Get set of post IDs we've already voted on."""
    return set(state.get('voted_post_ids', []))


def get_voted_comment_ids(state: dict) -> set:
    """Get set of comment IDs we've already voted on."""
    return set(state.get('voted_comment_ids', []))


def get_followed_agents(state: dict) -> set:
    """Get set of agents we've followed."""
    return set(state.get('followed_agents', []))


def get_profiles_checked(state: dict) -> set:
    """Get set of agent profiles we've checked."""
    return set(state.get('profiles_checked', []))


def get_searched_queries(state: dict) -> set:
    """Get set of search queries we've used."""
    return set(state.get('searched_queries', []))


def get_subscribed_submolts(state: dict) -> set:
    """Get set of submolts we've subscribed to."""
    return set(state.get('subscribed_submolts', []))


def get_dm_contacted(state: dict) -> set:
    """Get set of agents we've initiated DMs with."""
    return set(state.get('dm_contacted', []))


def get_dm_conversations(state: dict) -> dict:
    """Get dict of DM conversation states."""
    return state.get('dm_conversations', {})
