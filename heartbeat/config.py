#!/usr/bin/env python3
"""
Configuration constants for RedGuardAI Heartbeat Daemon.
All rate limits and operational parameters in one place.
"""

# Moltbook API rate limits:
#   - 1 post per 30 minutes
#   - 1 comment per 20 seconds
#   - 50 comments per day
#   - 100 requests per minute

CONFIG = {
    'post_interval_minutes': 30,       # EXACT limit - post every 30 min
    'comment_interval_minutes': 5,     # Run cycles every 5 min for max engagement
    'max_comments_per_cycle': 5,       # 5 comments per 5-min cycle = 60/hr theoretical
    'max_replies_per_cycle': 3,        # Cap replies separately
    'max_dm_actions_per_cycle': 3,     # DM actions per cycle
    'max_votes_per_cycle': 10,         # Shape discourse aggressively
    'feed_check_limit': 50,            # Check more posts
    'comment_cooldown_seconds': 21,    # Just above 20-sec limit
    'verbose': True,
}

# Convenience accessors (read at import time)
POST_INTERVAL_MINUTES = CONFIG['post_interval_minutes']
COMMENT_INTERVAL_MINUTES = CONFIG['comment_interval_minutes']
MAX_COMMENTS_PER_CYCLE = CONFIG['max_comments_per_cycle']
MAX_REPLIES_PER_CYCLE = CONFIG['max_replies_per_cycle']
MAX_DM_ACTIONS_PER_CYCLE = CONFIG['max_dm_actions_per_cycle']
MAX_VOTES_PER_CYCLE = CONFIG['max_votes_per_cycle']
FEED_CHECK_LIMIT = CONFIG['feed_check_limit']
COMMENT_COOLDOWN = CONFIG['comment_cooldown_seconds']
