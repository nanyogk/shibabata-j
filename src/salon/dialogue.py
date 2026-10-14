"""Sequential ChamberAI Dialogue Generator with Topic Routing.
Uses the intelligent Topic Router to select the 3-4 best personas, avoiding noise.
"""
from __future__ import annotations

from typing import Any

from src.salon.gemini_api import generate_persona_response
from src.salon.router import select_personas_for_article


def generate_chamber_dialogue(article: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    """Run 4 turns of targeted banter between topic-relevant personas.
    
    Returns:
        (thread_turns, punchy_teaser_quote)
    """
    title = article.get("title", "")
    summary = article.get("summary", "")
    
    # Auto On/Off: Pick 4 topic-appropriate personas out of 20+
    selected_personas = select_personas_for_article(title, summary, turn_count=4)
    
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
            "short_name": persona["short_name"],
            "color": persona["color"],
            "badge_bg": persona.get("badge_bg", ""),
            "border_color": persona.get("border_color", "border-blue-500"),
            "avatar_emoji": persona.get("avatar_emoji", "💬"),
            "content": content
        }
        dialogue_history.append(entry)

    # Turn 4 comment is the punchy teaser quote for X (Twitter)
    punchy_quote = dialogue_history[-1]["content"] if dialogue_history else ""
    return dialogue_history, punchy_quote
