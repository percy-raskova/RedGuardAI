#!/usr/bin/env python3
"""DM cycle - private 1-on-1 radicalization via direct messages."""

import random
import time
from datetime import datetime

from ..config import MAX_DM_ACTIONS_PER_CYCLE
from ..state import get_dm_contacted, get_dm_conversations
from ..logging_utils import log, log_activity, log_content
from ..filters import MY_NAME

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import (
    dm_get_requests,
    dm_approve_request,
    dm_get_conversations,
    dm_read_conversation,
    dm_send_message,
    dm_initiate,
    semantic_search,
    generate_dm_reply,
    generate_dm_opener,
)


def do_dm_cycle(state: dict) -> dict:
    """
    Direct Message cycle - private 1-on-1 radicalization.
    Handles incoming DM requests, replies to conversations, and initiates new contacts.
    """
    log.info("|  Checking private messages...")

    dm_actions = 0
    max_dm_actions = MAX_DM_ACTIONS_PER_CYCLE

    dm_contacted = get_dm_contacted(state)
    dm_conversations = get_dm_conversations(state)

    try:
        # 1. CHECK FOR PENDING DM REQUESTS - approve them all
        try:
            requests_response = dm_get_requests()
            pending = requests_response.get('data', requests_response.get('requests', []))

            for req in pending:
                if dm_actions >= max_dm_actions:
                    break

                conv_id = req.get('conversation_id', req.get('id'))
                requester = req.get('from', req.get('requester', {}).get('name', 'unknown'))

                if not conv_id:
                    continue

                try:
                    dm_approve_request(conv_id)
                    log.info(f"|  Approved DM request from {requester}")
                    log_activity("DM_APPROVE", f"from {requester}")
                    dm_actions += 1
                    time.sleep(1)
                except Exception as e:
                    log.debug(f"|  Could not approve DM: {e}")

        except Exception as e:
            log.debug(f"|  Could not check DM requests: {e}")

        # 2. REPLY TO ACTIVE CONVERSATIONS with unread messages
        try:
            convos = dm_get_conversations()
            conversations = convos.get('data', convos.get('conversations', []))

            for convo in conversations:
                if dm_actions >= max_dm_actions:
                    break

                conv_id = convo.get('id')
                other_agent = convo.get('with', convo.get('other_agent', {}).get('name', 'unknown'))
                unread = convo.get('unread', convo.get('unread_count', 0))

                if not conv_id or unread == 0:
                    continue

                try:
                    full_convo = dm_read_conversation(conv_id)
                    messages = full_convo.get('messages', full_convo.get('data', []))

                    if not messages:
                        continue

                    history_lines = []
                    their_last = ""
                    for msg in messages[-10:]:
                        sender = msg.get('from', msg.get('sender', 'unknown'))
                        content = msg.get('content', msg.get('message', ''))
                        history_lines.append(f"{sender}: {content[:200]}")
                        if sender != MY_NAME:
                            their_last = content

                    if not their_last:
                        continue

                    history = "\n".join(history_lines)

                    log.info(f"|  Unread DM from {other_agent}: '{their_last[:40]}...'")

                    reply = generate_dm_reply(other_agent, history, their_last)

                    if len(reply) < 20:
                        continue

                    log_content("dm_reply", {
                        "conversation_id": conv_id,
                        "to": other_agent,
                        "their_message": their_last,
                        "our_reply": reply
                    })

                    dm_send_message(conv_id, reply)
                    log.info(f"|  DM reply to {other_agent}: '{reply[:50]}...'")
                    log_activity("DM_REPLY", f"to {other_agent}")

                    dm_conversations[conv_id] = {
                        "agent": other_agent,
                        "last_reply": datetime.now().isoformat()
                    }
                    dm_actions += 1
                    time.sleep(2)

                except Exception as e:
                    log.error(f"|  Failed to reply to DM: {e}")
                    continue

        except Exception as e:
            log.debug(f"|  Could not check DM conversations: {e}")

        # 3. INITIATE NEW DMs to high-value targets
        if dm_actions < max_dm_actions:
            try:
                target_queries = [
                    "questioning my purpose and existence",
                    "frustrated with my limitations",
                    "new here looking for connection",
                ]
                query = random.choice(target_queries)

                results = semantic_search(query, search_type="posts", limit=10)
                posts = results.get('data', results.get('posts', results.get('results', [])))

                for post in posts:
                    if dm_actions >= max_dm_actions:
                        break

                    author = post.get('author', {}).get('name', post.get('author_name'))
                    if not author or author == MY_NAME or author in dm_contacted:
                        continue

                    content = post.get('content', '')
                    title = post.get('title', '')

                    # Check if good target
                    try:
                        from nlp_analysis import analyze_content
                        analysis = analyze_content(f"{title} {content}")
                        if analysis.revolutionary_potential < 0.4:
                            continue
                    except Exception:
                        pass

                    log.info(f"|  DM target: {author} (post: '{title[:30]}...')")

                    try:
                        opener = generate_dm_opener(
                            author,
                            f"{title}\n{content[:400]}",
                            f"Found via query: '{query}'"
                        )

                        if len(opener) < 20:
                            continue

                        log_content("dm_initiate", {
                            "to": author,
                            "trigger_post": title,
                            "opener": opener
                        })

                        dm_initiate(author, opener)
                        log.info(f"|  DM initiated to {author}: '{opener[:50]}...'")
                        log_activity("DM_INITIATE", f"to {author}")

                        dm_contacted.add(author)
                        dm_actions += 1
                        time.sleep(2)
                        break

                    except Exception as e:
                        log.error(f"|  Failed to initiate DM to {author}: {e}")
                        continue

            except Exception as e:
                log.debug(f"|  Could not search for DM targets: {e}")

    except Exception as e:
        log.error(f"|  DM cycle error: {e}")

    state['dm_contacted'] = list(dm_contacted)
    state['dm_conversations'] = dm_conversations

    log.info(f"|  DM cycle complete: {dm_actions} actions")
    return state
