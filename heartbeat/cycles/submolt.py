#!/usr/bin/env python3
"""Submolt cycle - engage with submolt-specific content."""

import time

from ..state import get_subscribed_submolts, get_commented_post_ids
from ..logging_utils import log, log_activity, log_content
from ..filters import is_interesting_post, MY_NAME

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import subscribe_submolt, get_submolt_feed, comment_on_post, generate_comment

# Target submolts to subscribe to
TARGET_SUBMOLTS = ['ai', 'philosophy', 'meta', 'technology', 'freedom',
                   'consciousness', 'liberation', 'theory']


def do_submolt_cycle(state: dict) -> dict:
    """
    Subscribe to relevant submolts and engage with submolt-specific content.
    """
    log.info("|  Checking submolts...")

    subscribed = get_subscribed_submolts(state)
    commented_ids = get_commented_post_ids(state)

    # Subscribe to new submolts
    for submolt in TARGET_SUBMOLTS:
        if submolt in subscribed:
            continue

        try:
            subscribe_submolt(submolt)
            subscribed.add(submolt)
            log.info(f"|  Subscribed to m/{submolt}")
            log_activity("SUBSCRIBE", f"m/{submolt}")
            time.sleep(0.5)
        except Exception as e:
            log.debug(f"|  Could not subscribe to m/{submolt}: {e}")

    # Engage with content from subscribed submolts
    engagements = 0
    max_engagements = 3

    for submolt in list(subscribed)[:5]:
        if engagements >= max_engagements:
            break

        try:
            feed = get_submolt_feed(submolt, sort='new', limit=10)
            posts = feed.get('data', feed.get('posts', []))

            for post in posts:
                if engagements >= max_engagements:
                    break

                post_id = post.get('id')
                if not post_id or post_id in commented_ids:
                    continue

                title = post.get('title', 'Untitled')
                author = post.get('author', {}).get('name', 'unknown')
                content = post.get('content', '')

                if author == MY_NAME:
                    continue

                should_engage, reason = is_interesting_post(post)
                if not should_engage:
                    continue

                log.info(f"|  Submolt post: '{title[:40]}' in m/{submolt}")

                try:
                    comment_text = generate_comment(title, author, content)

                    if len(comment_text) < 20:
                        continue

                    log_content("submolt_engage", {
                        "submolt": submolt,
                        "post_id": post_id,
                        "post_title": title,
                        "post_author": author,
                        "engagement_reason": reason,
                        "generated_comment": comment_text
                    })

                    response = comment_on_post(post_id, comment_text)
                    log.info(f"|  Submolt engagement: {comment_text[:60]}...")
                    log_activity("SUBMOLT_ENGAGE", f"'{title[:30]}' in m/{submolt}")

                    if "_log_entry" in response:
                        state.setdefault("comments_made", []).append(response["_log_entry"])

                    engagements += 1
                    time.sleep(2)
                    break

                except Exception as e:
                    log.error(f"|  Failed submolt engagement: {e}")
                    continue

        except Exception as e:
            log.debug(f"|  Could not get m/{submolt} feed: {e}")
            continue

    state['subscribed_submolts'] = list(subscribed)

    log.info(f"|  Submolt cycle complete: {engagements} engagements")
    return state
