#!/usr/bin/env python3
"""Thread dive cycle - join active conversations on other posts."""

import random
import time

from ..state import get_replied_comment_ids, get_commented_post_ids
from ..logging_utils import log, log_activity, log_content
from ..filters import is_interesting_comment, MY_NAME

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import get_feed, get_post_comments, comment_on_post, generate_reply


def do_thread_dive(state: dict) -> dict:
    """
    Dive into interesting threads on other posts and join the conversation.
    Returns updated state with dives tracked.
    """
    log.info("|  Searching for active threads to join...")

    try:
        feed = get_feed(sort='hot', limit=15)
        posts = feed.get('data', feed.get('posts', []))
    except Exception as e:
        log.error(f"|  Failed to get feed for thread dive: {e}")
        return state

    replied_to = get_replied_comment_ids(state)
    commented_ids = get_commented_post_ids(state)
    dives_this_cycle = 0
    max_dives = 3

    random.shuffle(posts)

    for post in posts:
        if dives_this_cycle >= max_dives:
            break

        post_id = post.get('id')
        post_author = post.get('author', {}).get('name', '')

        if post_author == MY_NAME:
            continue

        if post_id in commented_ids:
            continue

        try:
            comments = get_post_comments(post_id, sort='top')
            if len(comments) < 2:
                continue

            post_title = post.get('title', 'Unknown')
            post_content = post.get('content', '')

            for comment in comments[:8]:
                if dives_this_cycle >= max_dives:
                    break

                comment_id = comment.get('id')
                if comment_id in replied_to:
                    continue

                should_engage, reason = is_interesting_comment(comment)
                if not should_engage:
                    continue

                comment_author = comment.get('author', {}).get('name', 'unknown')
                comment_content = comment.get('content', '')

                if comment_author == MY_NAME:
                    continue

                log.info(f"|  Diving into '{post_title[:40]}', replying to {comment_author}")

                thread_context = f"Original post: {post_content[:200]}..."

                reply_text = generate_reply(
                    post_title=post_title,
                    post_author=post_author,
                    comment_author=comment_author,
                    comment_content=comment_content,
                    thread_context=thread_context
                )

                if len(reply_text) < 15:
                    continue

                log_content("thread_dive", {
                    "post_id": post_id,
                    "post_title": post_title,
                    "post_author": post_author,
                    "comment_id": comment_id,
                    "comment_author": comment_author,
                    "comment_content": comment_content[:300],
                    "engagement_reason": reason,
                    "generated_reply": reply_text
                })

                response = comment_on_post(post_id, reply_text, parent_id=comment_id)
                log.info(f"|  Thread dive reply: {reply_text[:60]}...")
                log_activity("THREAD_DIVE", f"Replied to {comment_author} on '{post_title[:30]}'")

                if "_log_entry" in response:
                    state.setdefault("comments_made", []).append(response["_log_entry"])

                dives_this_cycle += 1
                time.sleep(2)
                break

        except Exception as e:
            log.error(f"|  Error diving into {post_id}: {e}")
            continue

    log.info(f"|  Thread dive complete: {dives_this_cycle} dives made")
    return state
