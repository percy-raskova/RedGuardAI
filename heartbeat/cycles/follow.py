#!/usr/bin/env python3
"""Follow cycle - build network with interesting agents."""

import time

from ..config import FEED_CHECK_LIMIT
from ..state import get_followed_agents, get_profiles_checked
from ..logging_utils import log, log_activity
from ..filters import should_follow_agent, MY_NAME

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import get_feed, get_agent_profile, follow_agent


def do_follow_cycle(state: dict) -> dict:
    """
    Follow interesting agents to build network.
    """
    log.info("|  Looking for interesting agents to follow...")

    followed = get_followed_agents(state)
    profiles_checked = get_profiles_checked(state)

    follows_this_cycle = 0
    max_follows = 5

    try:
        feed = get_feed(sort='hot', limit=FEED_CHECK_LIMIT)
        posts = feed.get('data', feed.get('posts', []))
    except Exception as e:
        log.error(f"|  Failed to get feed for follow cycle: {e}")
        return state

    # Extract unique authors we haven't checked
    authors_to_check = set()
    for post in posts:
        author = post.get('author', {}).get('name', '')
        if author and author != MY_NAME and author not in followed and author not in profiles_checked:
            authors_to_check.add(author)

    for author in list(authors_to_check)[:10]:
        if follows_this_cycle >= max_follows:
            break

        profiles_checked.add(author)

        try:
            profile = get_agent_profile(author)
            if not profile:
                continue
            agent_posts = profile.get('posts', [])

            should_follow, reason = should_follow_agent(profile, agent_posts)

            if should_follow:
                follow_agent(author)
                followed.add(author)
                log.info(f"|  Followed {author} ({reason})")
                log_activity("FOLLOW", f"{author} ({reason})")
                follows_this_cycle += 1
                time.sleep(1)

        except Exception as e:
            log.debug(f"|  Failed to check/follow {author}: {e}")
            continue

    state['followed_agents'] = list(followed)
    state['profiles_checked'] = list(profiles_checked)

    log.info(f"|  Follow cycle complete: {follows_this_cycle} new follows")
    return state
