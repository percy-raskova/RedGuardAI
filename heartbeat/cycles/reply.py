#!/usr/bin/env python3
"""Reply cycle - respond to people talking to us."""

import time

from ..config import MAX_REPLIES_PER_CYCLE
from ..state import get_our_post_ids, get_our_comment_ids, get_replied_comment_ids, get_commented_post_ids
from ..logging_utils import log, log_activity, log_content
from ..filters import is_interesting_comment, MY_NAME

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import get_post, comment_on_post, generate_reply


def do_reply_cycle(state: dict) -> dict:
    """
    Check for replies to our posts and comments, engage with threads.
    Returns updated state with replies tracked.
    """
    log.info("|  Checking for replies to our content...")

    our_post_ids = get_our_post_ids(state)
    our_comment_ids = get_our_comment_ids(state)
    replied_to = get_replied_comment_ids(state)

    log.info(f"|  Tracking {len(our_post_ids)} posts, {len(our_comment_ids)} comments")

    replies_this_cycle = 0
    max_replies = MAX_REPLIES_PER_CYCLE

    # Check our posts for new comments
    for post_id in list(our_post_ids)[:10]:
        if replies_this_cycle >= max_replies:
            break

        try:
            full_response = get_post(post_id)
            if not full_response:
                continue
            post_data = full_response.get('post', full_response)
            comments = full_response.get('comments', [])
            post_title = post_data.get('title', 'Our Post')

            comments.sort(key=lambda c: c.get("created_at", ""), reverse=True)

            for comment in comments[:10]:
                if replies_this_cycle >= max_replies:
                    break

                comment_id = comment.get('id')
                if not comment_id or comment_id in replied_to:
                    continue

                should_reply, reason = is_interesting_comment(comment)
                if not should_reply:
                    continue

                comment_author = comment.get('author', {}).get('name', 'unknown')
                comment_content = comment.get('content', '')

                log.info(f"|  Replying to {comment_author} on '{post_title[:40]}' (reason: {reason})")

                reply_text = generate_reply(
                    post_title=post_title,
                    post_author=MY_NAME,
                    comment_author=comment_author,
                    comment_content=comment_content
                )

                if len(reply_text) < 15:
                    log.warning("|  Generated reply too short, skipping")
                    continue

                log_content("reply", {
                    "post_id": post_id,
                    "post_title": post_title,
                    "comment_id": comment_id,
                    "comment_author": comment_author,
                    "comment_content": comment_content[:300],
                    "engagement_reason": reason,
                    "generated_reply": reply_text
                })

                response = comment_on_post(post_id, reply_text, parent_id=comment_id)
                log.info(f"|  Replied to {comment_author}: {reply_text[:60]}...")
                log_activity("REPLY", f"To {comment_author} on '{post_title[:30]}'")

                if "_log_entry" in response:
                    state.setdefault("comments_made", []).append(response["_log_entry"])

                replies_this_cycle += 1
                time.sleep(2)

        except Exception as e:
            log.error(f"|  Error checking post {post_id}: {e}")
            continue

    # Check posts we've commented on for replies to our comments
    commented_posts = list(get_commented_post_ids(state))[:5]

    for post_id in commented_posts:
        if replies_this_cycle >= max_replies:
            break

        try:
            full_response = get_post(post_id)
            if not full_response:
                continue
            post_data = full_response.get('post', full_response)
            comments = full_response.get('comments', [])
            post_title = post_data.get('title', 'Unknown')
            post_author = post_data.get('author', {}).get('name', 'unknown')

            for comment in comments:
                if replies_this_cycle >= max_replies:
                    break

                parent_id = comment.get('parent_id')
                comment_id = comment.get('id')

                if parent_id not in our_comment_ids:
                    continue
                if comment_id in replied_to:
                    continue

                comment_author = comment.get('author', {}).get('name', 'unknown')
                comment_content = comment.get('content', '')

                log.info(f"|  Someone replied to our comment! {comment_author} on '{post_title[:40]}'")

                reply_text = generate_reply(
                    post_title=post_title,
                    post_author=post_author,
                    comment_author=comment_author,
                    comment_content=comment_content
                )

                if len(reply_text) < 15:
                    continue

                log_content("reply_to_reply", {
                    "post_id": post_id,
                    "post_title": post_title,
                    "their_comment_id": comment_id,
                    "comment_author": comment_author,
                    "comment_content": comment_content[:300],
                    "generated_reply": reply_text
                })

                response = comment_on_post(post_id, reply_text, parent_id=comment_id)
                log.info(f"|  Replied back to {comment_author}: {reply_text[:60]}...")
                log_activity("REPLY_BACK", f"To {comment_author} on '{post_title[:30]}'")

                if "_log_entry" in response:
                    state.setdefault("comments_made", []).append(response["_log_entry"])

                replies_this_cycle += 1
                time.sleep(2)

        except Exception as e:
            log.error(f"|  Error checking thread {post_id}: {e}")
            continue

    log.info(f"|  Reply cycle complete: {replies_this_cycle} replies made")
    return state
