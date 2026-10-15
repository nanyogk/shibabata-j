"""Sequential Democratic Dialogue Generator using 1-Call Screenplay Batching.
Passes selected 5 to 8 personas, video highlights, and fan comments in 1 single call.
"""
from __future__ import annotations

import random
from typing import Any

from src.salon.gemini_api import generate_thread_screenplay
from src.salon.router import select_personas_for_article


def generate_chamber_dialogue(article: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    """Run a lively, democratic discussion of 5 to 8 turns in ONE single API call.
    
    Returns:
        (thread_turns, punchy_teaser_quote)
    """
    title = article.get("title", "")
    summary = article.get("summary", "")
    fan_comments = article.get("fan_comments", [])
    
    # 1. Randomly pick 5 to 8 personas in organic randomized speaking order
    selected_personas = select_personas_for_article(title, summary, min_count=5, max_count=8)
    
    # 2. 1-Call Batch Screenplay Generation!
    dialogue_history = generate_thread_screenplay(
        personas=selected_personas,
        article_title=title,
        article_summary=summary,
        fan_comments=fan_comments
    )

    # 3. Pick an entertaining comment from the latter half of the thread as the teaser quote
    candidates = dialogue_history[-3:] if len(dialogue_history) >= 3 else dialogue_history
    chosen_teaser = random.choice(candidates)["content"] if candidates else ""
    return dialogue_history, chosen_teaser
