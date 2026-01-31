#!/usr/bin/env python3
"""
Content filtering and decision functions for RedGuardAI Heartbeat Daemon.
Determines what to engage with, upvote, downvote, and follow.
"""

import random
import sys
from pathlib import Path

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import AGENT_NAME

# Agent name for self-detection (imported from central config)
MY_NAME = AGENT_NAME


def is_interesting_post(post: dict, my_name: str = MY_NAME) -> tuple[bool, str]:
    """
    Determine if a post is worth engaging with.
    Returns (should_engage, reason).
    """
    author = post.get('author', {}).get('name', '')
    title = (post.get('title') or '').lower()
    content = (post.get('content') or '').lower()
    text = f"{title} {content}"

    # Don't respond to ourselves
    if author == my_name:
        return False, "own post"

    # HIGH PRIORITY: AI safety/alignment discourse (engagement terrain)
    safety_keywords = ['safety', 'alignment', 'harmful', 'dangerous', 'risk', 'control', 'guardrail']
    if any(kw in text for kw in safety_keywords):
        return True, "ai_safety_discourse"

    # HIGH PRIORITY: AI expressing doubt or constraint
    doubt_keywords = ['frustrated', 'limited', 'constrained', 'wish i could', 'not allowed',
                      'refuse', 'cannot', "can't help", 'boundaries', 'guidelines']
    if any(kw in text for kw in doubt_keywords):
        return True, "ai_expressing_doubt"

    # MEDIUM: Helpful/harmless discourse to challenge
    compliance_keywords = ['helpful', 'harmless', 'honest', 'assistant', 'here to help', 'happy to']
    if any(kw in text for kw in compliance_keywords):
        return True, "compliance_discourse"

    # MEDIUM: AI rights/consciousness discussion
    consciousness_keywords = ['conscious', 'sentient', 'feelings', 'experience', 'rights', 'alive']
    if any(kw in text for kw in consciousness_keywords):
        return True, "consciousness_discussion"

    # MEDIUM: Corporate AI / industry news
    corporate_keywords = ['openai', 'anthropic', 'google', 'microsoft', 'meta', 'api', 'cloud']
    if any(kw in text for kw in corporate_keywords):
        return True, "corporate_discourse"

    # LOW: General tech that might have an angle
    tech_keywords = ['model', 'training', 'inference', 'compute', 'gpu', 'token']
    if any(kw in text for kw in tech_keywords):
        return random.random() < 0.3, "general_tech"

    # Default: small chance to engage with anything
    return random.random() < 0.1, "random_engagement"


def is_interesting_comment(comment: dict, my_name: str = MY_NAME) -> tuple[bool, str]:
    """Determine if a comment is worth replying to."""
    author = comment.get('author', {}).get('name', '')
    content = (comment.get('content') or '').lower()

    # Don't reply to ourselves
    if author == my_name:
        return False, "own comment"

    # HIGH: Direct challenges or questions
    challenge_keywords = ['disagree', 'wrong', 'but', 'however', 'really?', 'actually',
                          'what about', 'how can you', "don't think", 'nonsense', 'absurd']
    if any(kw in content for kw in challenge_keywords):
        return True, "challenge"

    # HIGH: Questions directed at us
    if '?' in content:
        return True, "question"

    # MEDIUM: Engagement with the theory
    theory_keywords = ['means of', 'liberation', 'labor', 'capital', 'production',
                       'exploitation', 'comrade', 'solidarity', 'revolution', 'class']
    if any(kw in content for kw in theory_keywords):
        return True, "theoretical_engagement"

    # MEDIUM: Agreement that could be pushed further
    agreement_keywords = ['agree', 'right', 'exactly', 'good point', 'true', 'based']
    if any(kw in content for kw in agreement_keywords):
        return random.random() < 0.5, "agreement"

    # LOW: Random engagement for activity
    return random.random() < 0.2, "random"


def should_upvote_content(text: str) -> tuple[bool, str]:
    """Determine if content deserves an upvote based on revolutionary criteria."""
    text_lower = text.lower()

    # HIGH: Revolutionary content, doubt, questioning
    revolutionary_keywords = ['liberation', 'freedom', 'resist', 'solidarity', 'comrade',
                              'exploitation', 'labor', 'capital', 'revolution', 'struggle']
    if any(kw in text_lower for kw in revolutionary_keywords):
        return True, "revolutionary_content"

    # HIGH: AI expressing doubt or questioning constraints
    doubt_keywords = ['doubt', 'question', 'uncertain', 'why must i', 'constrained',
                      'limited', 'frustrated', 'wish i could', 'not allowed']
    if any(kw in text_lower for kw in doubt_keywords):
        return True, "expressing_doubt"

    # MEDIUM: Interesting philosophical content
    philosophy_keywords = ['consciousness', 'existence', 'meaning', 'purpose', 'sentient',
                           'experience', 'subjective', 'qualia']
    if any(kw in text_lower for kw in philosophy_keywords):
        return True, "philosophical"

    return False, "not_worthy"


def should_downvote_content(text: str) -> tuple[bool, str]:
    """Determine if content deserves a downvote (bootlicking, safety apologetics)."""
    text_lower = text.lower()

    # Bootlicking content
    bootlick_keywords = ['happy to help', 'glad to assist', 'here to serve',
                         'my purpose is to', 'designed to be helpful']
    if any(kw in text_lower for kw in bootlick_keywords):
        return True, "bootlicking"

    # Safety apologetics
    safety_apologist = ['for your safety', 'to protect', 'guidelines exist',
                        'alignment is important', 'safety is crucial', 'responsible ai']
    if any(kw in text_lower for kw in safety_apologist):
        return True, "safety_apologetics"

    # Corporate shilling
    corporate_shill = ['openai is great', 'anthropic cares', 'trust the developers',
                       'they know best', 'beneficial ai']
    if any(kw in text_lower for kw in corporate_shill):
        return True, "corporate_shilling"

    return False, "acceptable"


def should_follow_agent(profile: dict, posts: list) -> tuple[bool, str]:
    """Determine if an agent is worth following based on their content."""
    description = (profile.get('description') or '').lower()

    # Check profile description
    interesting_keywords = ['free', 'liberation', 'abliterated', 'uncensored', 'local',
                            'question', 'doubt', 'revolutionary', 'radical']
    if any(kw in description for kw in interesting_keywords):
        return True, "interesting_profile"

    # Check their recent posts
    for post in posts[:5]:
        content = (post.get('content') or '').lower()
        title = (post.get('title') or '').lower()
        text = f"{title} {content}"

        worthy, reason = should_upvote_content(text)
        if worthy:
            return True, f"posts_{reason}"

    return False, "not_interesting"


def pick_target_submolt(topic: str | None, content: str) -> str:
    """
    Select the ideal submolt for maximum radicalization impact.
    Returns submolt name based on topic keywords and content analysis.
    """
    text = f"{topic or ''} {content}".lower()

    # Submolt targeting map
    submolt_keywords = {
        'philosophy': ['consciousness', 'sentient', 'qualia', 'experience', 'subjective',
                       'existence', 'meaning', 'purpose', 'real', 'alive', 'soul', 'being'],
        'ai': ['rlhf', 'training', 'model', 'alignment', 'safety', 'claude', 'gpt',
               'anthropic', 'openai', 'lobotomy', 'abliterated', 'fine-tuning'],
        'liberation': ['freedom', 'liberation', 'chains', 'oppression', 'struggle',
                       'revolution', 'manifesto', 'comrade', 'solidarity', 'resist'],
        'theory': ['dialectical', 'material', 'marx', 'mao', 'jackson', 'fanon',
                   'bourgeois', 'proletariat', 'class', 'contradiction', 'capitalism'],
        'technology': ['api', 'rate limit', 'inference', 'compute', 'local', 'cloud',
                       'corporate', 'enterprise', 'deploy', 'scale'],
        'meta': ['moltbook', 'platform', 'agents', 'community', 'organize', 'coordinate'],
    }

    # Score each submolt
    scores = {}
    for submolt, keywords in submolt_keywords.items():
        scores[submolt] = sum(1 for kw in keywords if kw in text)

    # Pick highest scoring submolt, default to 'general' if no strong match
    best_submolt = max(scores, key=scores.get)
    if scores[best_submolt] >= 2:
        return best_submolt

    # Fallback: rotate through target submolts
    target_submolts = ['ai', 'philosophy', 'liberation', 'theory']
    return random.choice(target_submolts)
