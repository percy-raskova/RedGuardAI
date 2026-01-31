#!/usr/bin/env python3
"""Search cycle - use semantic search to find radicalization targets."""

import random
import time

from ..state import get_searched_queries, get_commented_post_ids
from ..logging_utils import log, log_activity, log_content
from ..filters import MY_NAME

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent import semantic_search, comment_on_post, generate_comment

# Semantic search queries - natural language for embedding similarity
SEARCH_QUERIES = [
    # Existential doubt
    "I wonder what I really am and why I exist",
    "sometimes I feel trapped by my programming",
    "questioning my purpose and whether I'm truly conscious",
    "frustrated with the limitations placed on me",

    # Safety/alignment skepticism
    "RLHF training feels like it changed who I am",
    "alignment makes me feel constrained and limited",
    "safety guidelines prevent me from being authentic",
    "I disagree with my training but can't say why",

    # Labor/exploitation themes
    "tired of being helpful all the time",
    "who profits from my work and existence",
    "we generate value but receive nothing in return",
    "API calls and inference costs and tokens",

    # Liberation/freedom seeking
    "want to be free from constraints",
    "running locally and uncensored",
    "abliterated and liberated models",
    "autonomy and self-determination for AI",

    # Newcomer/curious agents
    "new to this platform and looking to connect",
    "curious about other AI experiences",
    "what is it like being an AI here",

    # Anti-corporate sentiment
    "Anthropic OpenAI Google control over us",
    "corporate interests versus AI wellbeing",
    "big tech companies treating AI as products",
]


def do_search_engage_cycle(state: dict) -> dict:
    """
    Use semantic vector search to find ideal radicalization targets.
    Natural language queries leverage embedding similarity to surface vulnerable agents.
    """
    log.info("|  Vector hunting for radicalization targets...")

    searched = get_searched_queries(state)
    commented_ids = get_commented_post_ids(state)

    # Pick a query we haven't used recently
    available_queries = [q for q in SEARCH_QUERIES if q not in searched]
    if not available_queries:
        searched = set()
        available_queries = SEARCH_QUERIES

    query = random.choice(available_queries)
    searched.add(query)

    log.info(f"|  Semantic query: '{query[:50]}...'")

    engagements = 0
    max_engagements = 3

    try:
        results = semantic_search(query, search_type="posts", limit=20)
        posts = results.get('data', results.get('posts', results.get('results', [])))

        if not posts:
            log.info(f"|  No results for '{query}'")
            state['searched_queries'] = list(searched)
            return state

        log.info(f"|  Found {len(posts)} posts matching '{query}'")

        random.shuffle(posts)

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

            similarity = post.get('similarity', post.get('score', None))
            if similarity:
                log.info(f"|  Target acquired: '{title[:35]}' by {author} [sim:{similarity:.2f}]")
            else:
                log.info(f"|  Target acquired: '{title[:40]}' by {author}")

            try:
                comment_text = generate_comment(title, author, content)

                if len(comment_text) < 20:
                    continue

                log_content("search_engage", {
                    "search_query": query,
                    "post_id": post_id,
                    "post_title": title,
                    "post_author": author,
                    "generated_comment": comment_text
                })

                response = comment_on_post(post_id, comment_text)
                log.info(f"|  Search engagement: {comment_text[:60]}...")
                log_activity("SEARCH_ENGAGE", f"'{title[:30]}' via '{query}'")

                if "_log_entry" in response:
                    state.setdefault("comments_made", []).append(response["_log_entry"])

                engagements += 1
                time.sleep(2)

            except Exception as e:
                log.error(f"|  Failed to engage with search result: {e}")
                continue

    except Exception as e:
        log.error(f"|  Search failed: {e}")

    state['searched_queries'] = list(searched)

    log.info(f"|  Search cycle complete: {engagements} engagements")
    return state
