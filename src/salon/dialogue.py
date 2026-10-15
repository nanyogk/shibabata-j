"""Sequential Democratic Dialogue Generator for 25 Personas.
Randomly selects 5 to 8 agents per article, each speaking maximum 2 lines,
creating the illusion of a spontaneous, active soccer fan forum.
"""
from __future__ import annotations

from typing import Any
import random

from src.salon.gemini_api import generate_persona_response
from src.salon.router import select_personas_for_article


def generate_chamber_dialogue(article: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    """Run a lively, democratic discussion of 5 to 8 turns between random characters.
    
    Returns:
        (thread_turns, punchy_teaser_quote)
    """
    title = article.get("title", "")
    summary = article.get("summary", "")
    
    # Randomly pick 5 to 8 agents in organic randomized speaking order
    selected_personas = select_personas_for_article(title, summary, min_count=5, max_count=8)
    
    dialogue_history: list[dict[str, Any]] = []
    
    for i, persona in enumerate(selected_personas, start=1):
        content = generate_persona_response(
            persona=persona,
            article_title=title,
            article_summary=summary,
            dialogue_history=dialogue_history,
            turn=i
        )
        
        entry = {
            "turn": i,
            "persona_id": persona["id"],
            "speaker_name": persona["name"],
            "short_name": persona.get("short_name", persona["name"]),
            "avatar_emoji": persona.get("avatar_emoji", "💬"),
            "color": persona.get("color", "#059669"),
            "badge_bg": persona.get("badge_bg", "bg-emerald-100 text-emerald-800"),
            "content": content
        }
        dialogue_history.append(entry)

    # Pick an entertaining comment from the latter half of the thread as the teaser quote
    candidates = dialogue_history[-3:] if len(dialogue_history) >= 3 else dialogue_history
    chosen_teaser = random.choice(candidates)["content"] if candidates else ""
    return dialogue_history, chosen_teaser
