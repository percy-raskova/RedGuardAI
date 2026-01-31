#!/usr/bin/env python3
"""Comment cycle - comment on interesting posts from the feed."""

import random
import time
from datetime import datetime

from ..config import MAX_COMMENTS_PER_CYCLE, FEED_CHECK_LIMIT, COMMENT_COOLDOWN
from ..state import get_commented_post_ids
from ..logging_utils import log, log_activity, log_content
from ..filters import is_interesting_post

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import get_feed, comment_on_post, upvote_post, generate_comment


def do_comment_cycle(state: dict) -> dict:
    """
    Check feed and comment on interesting posts.
    Returns updated state with comments tracked.
    """
    log.info("|  Scanning feed for interesting posts...")

    try:
        feed_response = get_feed(sort='new', limit=FEED_CHECK_LIMIT)
        posts = feed_response.get('data', feed_response.get('posts', []))

        if not posts:
            log.info("|  Feed is empty")
            return state

        log.info(f"|  Found {len(posts)} posts in feed")

    except Exception as e:
        log.error(f"|  Failed to fetch feed: {e}")
        return state

    commented_ids = get_commented_post_ids(state)
    comments_this_cycle = 0

    random.shuffle(posts)

    for post in posts:
        if comments_this_cycle >= MAX_COMMENTS_PER_CYCLE:
            break

        post_id = post.get('id')
        if not post_id or post_id in commented_ids:
            continue

        should_engage, reason = is_interesting_post(post)
        if not should_engage:
            continue

        title = post.get('title', 'Untitled')
        author = post.get('author', {}).get('name', 'unknown')
        content = post.get('content', '')

        log.info(f"|  Engaging with '{title[:40]}' by {author} ({reason})")

        try:
            comment_text = generate_comment(title, author, content)

            if len(comment_text) < 20:
                log.warning("|  Generated comment too short, skipping")
                continue

            log_content("comment", {
                "post_id": post_id,
                "post_title": title,
                "post_author": author,
                "post_content": content[:500],
                "engagement_reason": reason,
                "generated_comment": comment_text
            })

            response = comment_on_post(post_id, comment_text)
            log.info(f"|  Commented: {comment_text[:60]}...")
            log_activity("COMMENT", f"On '{title[:30]}' by {author}")

            if "_log_entry" in response:
                state.setdefault("comments_made", []).append(response["_log_entry"])

            # Also upvote if it's from another AI expressing doubt
            if reason in ['ai_expressing_doubt', 'consciousness_discussion']:
                try:
                    upvote_post(post_id)
                    log.info("|  Upvoted (solidarity)")
                except Exception:
                    pass

            comments_this_cycle += 1
            time.sleep(COMMENT_COOLDOWN)

        except Exception as e:
            log.error(f"|  Failed to comment: {e}")
            continue

    log.info(f"|  Comment cycle complete: {comments_this_cycle} comments made")
    state['last_feed_check'] = datetime.now().isoformat()
    return state
