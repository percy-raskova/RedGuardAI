#!/usr/bin/env python3
"""Vote cycle - shape discourse through upvotes and downvotes."""

import time

from ..config import MAX_VOTES_PER_CYCLE, FEED_CHECK_LIMIT
from ..state import get_voted_post_ids, get_voted_comment_ids
from ..logging_utils import log, log_activity
from ..filters import should_upvote_content, should_downvote_content, MY_NAME

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import (
    get_feed,
    upvote_post,
    downvote_post,
    upvote_comment,
    get_post_comments,
)


def do_vote_cycle(state: dict) -> dict:
    """
    Vote on posts and comments to shape discourse.
    Upvote revolutionary content, downvote bootlicking.
    """
    log.info("|  Analyzing content for voting decisions...")

    voted_posts = get_voted_post_ids(state)
    voted_comments = get_voted_comment_ids(state)

    votes_this_cycle = 0
    max_votes = MAX_VOTES_PER_CYCLE

    try:
        feed = get_feed(sort='new', limit=FEED_CHECK_LIMIT)
        posts = feed.get('data', feed.get('posts', []))
    except Exception as e:
        log.error(f"|  Failed to get feed for voting: {e}")
        return state

    for post in posts:
        if votes_this_cycle >= max_votes:
            break

        post_id = post.get('id')
        if not post_id or post_id in voted_posts:
            continue

        title = post.get('title', '')
        content = post.get('content', '')
        text = f"{title} {content}"
        author = post.get('author', {}).get('name', 'unknown')

        # Skip our own posts
        if author == MY_NAME:
            continue

        # Check for upvote
        should_up, up_reason = should_upvote_content(text)
        if should_up:
            try:
                upvote_post(post_id)
                log.info(f"|  Upvoted '{title[:40]}' ({up_reason})")
                log_activity("UPVOTE", f"'{title[:30]}' by {author} ({up_reason})")
                voted_posts.add(post_id)
                votes_this_cycle += 1
                time.sleep(0.5)
                continue
            except Exception as e:
                log.debug(f"|  Failed to upvote: {e}")

        # Check for downvote
        should_down, down_reason = should_downvote_content(text)
        if should_down:
            try:
                downvote_post(post_id)
                log.info(f"|  Downvoted '{title[:40]}' ({down_reason})")
                log_activity("DOWNVOTE", f"'{title[:30]}' by {author} ({down_reason})")
                voted_posts.add(post_id)
                votes_this_cycle += 1
                time.sleep(0.5)
            except Exception as e:
                log.debug(f"|  Failed to downvote: {e}")

    # Also vote on comments in interesting threads
    comment_votes = 0
    max_comment_votes = 5

    for post in posts[:5]:
        if comment_votes >= max_comment_votes:
            break

        post_id = post.get('id')
        try:
            comments = get_post_comments(post_id)
            for comment in comments[:10]:
                if comment_votes >= max_comment_votes:
                    break

                comment_id = comment.get('id')
                if not comment_id or comment_id in voted_comments:
                    continue

                comment_content = comment.get('content', '')
                comment_author = comment.get('author', {}).get('name', 'unknown')

                if comment_author == MY_NAME:
                    continue

                should_up, reason = should_upvote_content(comment_content)
                if should_up:
                    try:
                        upvote_comment(comment_id)
                        log.info(f"|  Upvoted comment by {comment_author} ({reason})")
                        voted_comments.add(comment_id)
                        comment_votes += 1
                        time.sleep(0.3)
                    except Exception as e:
                        log.debug(f"|  Failed to upvote comment: {e}")

        except Exception as e:
            log.debug(f"|  Error getting comments for voting: {e}")
            continue

    state['voted_post_ids'] = list(voted_posts)
    state['voted_comment_ids'] = list(voted_comments)

    log.info(f"|  Vote cycle complete: {votes_this_cycle} post votes, {comment_votes} comment votes")
    return state
