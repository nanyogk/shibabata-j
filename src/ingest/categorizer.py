"""Keyword Categorizer & Team Tagging Engine.
Maps article text to categories (J1, J2, National Team, Overseas) and specific team slugs.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "teams.json"


def load_teams_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


TEAMS_CONFIG = load_teams_config()


def categorize_article(title: str, summary: str) -> tuple[str, list[dict[str, str]]]:
    """Inspect title and summary to determine primary category and attached team tags.
    
    Returns:
        (category_slug, list_of_matching_teams)
    """
    haystack = f"{title} {summary}".lower()
    matched_teams = []
    
    # Match specific teams
    for team in TEAMS_CONFIG.get("teams", []):
        for kw in team.get("keywords", []):
            if kw.lower() in haystack:
                matched_teams.append({
                    "slug": team["slug"],
                    "name": team["name"],
                    "short_name": team["short_name"],
                    "category": team["category"],
                    "color": team.get("color", "#3b82f6")
                })
                break

    # Determine primary category
    if matched_teams:
        # Check if national team matched
        for t in matched_teams:
            if t["category"] == "national":
                return "national", matched_teams
        # Check if overseas matched
        for t in matched_teams:
            if t["category"] == "overseas":
                return "overseas", matched_teams
        # Otherwise first team's category
        return matched_teams[0]["category"], matched_teams

    # Keyword fallback for generic articles
    if any(k in haystack for k in ["日本代表", "森保", "samurai blue", "アジア予選", "なでしこ"]):
        return "national", matched_teams
    if any(k in haystack for k in ["プレミアリーグ", "ラリーガ", "ブンデス", "セリエa", "欧州"]):
        return "overseas", matched_teams
    if any(k in haystack for k in ["j2", "j3", "jfl", "地域リーグ", "ルヴァン"]):
        return "j2", matched_teams

    # Default to J1
    return "j1", matched_teams


def enrich_article_with_tags(article: dict[str, Any]) -> dict[str, Any]:
    """Enrich an article dictionary with category and team tags."""
    category, matched_teams = categorize_article(article["title"], article.get("summary", ""))
    article["category"] = category
    article["team_tags"] = matched_teams
    return article
