"""Democratic Persona Selector for 25+ Characters.
Randomly selects 5 to 8 characters per article in randomized speaking order,
mimicking an organic, diverse, lively comment forum discussion.
"""
from __future__ import annotations

import json
from pathlib import Path
import random
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "personas.json"

# Topic affinities provide a gentle anchor, while remaining slots are drawn democratically
TOPIC_SEEDS = {
    "transfer": {
        "keywords": ["移籍", "契約", "違約金", "年俸", "加入", "退団", "オファー", "交渉", "獲得"],
        "candidates": ["economist-wannabe", "transfer-guru", "fantasy-manager", "young-talent-hunter", "stockholder-fan", "injury-pessimist"]
    },
    "match": {
        "keywords": ["試合", "ゴール", "勝利", "敗戦", "ドロー", "スタメン", "先発", "交代", "ハイライト", "采配", "シュート"],
        "candidates": ["coach-wannabe", "stats-data-geek", "ultras-supporter", "note-tactics-writer", "dazn-director", "lens-photographer", "boots-gear-nerd"]
    },
    "referee": {
        "keywords": ["var", "判定", "ファウル", "退場", "レッド", "イエロー", "ハンド", "誤審", "pk", "主審"],
        "candidates": ["var-referee-nerd", "coach-wannabe", "ultras-supporter", "stats-data-geek", "peace-enjoyer"]
    },
    "culture": {
        "keywords": ["スタグル", "グルメ", "スタジアム", "ビール", "マスコット", "動員", "遠征", "新スタ", "建設", "アウェイ"],
        "candidates": ["stadium-gourmet", "mascot-otaku", "away-bus-veteran", "local-pride-patriot", "protective-mom", "uniform-fashionista"]
    },
    "national_overseas": {
        "keywords": ["日本代表", "森保", "海外", "プレミア", "欧州", "w杯", "アジア最終予選", "三笘", "久保"],
        "candidates": ["overseas-elitist", "young-talent-hunter", "nostalgic-boomer", "coach-wannabe", "peace-enjoyer"]
    },
    "derby_j2": {
        "keywords": ["ダービー", "ライバル", "j2", "j3", "昇格", "降格", "プレーオフ"],
        "candidates": ["derby-warrior", "j2-connoisseur", "ultras-supporter", "local-pride-patriot"]
    }
}


def load_all_personas() -> dict[str, dict[str, Any]]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {p["id"]: p for p in data.get("personas", [])}


ALL_PERSONAS = load_all_personas()


def select_personas_for_article(title: str, summary: str, min_count: int = 5, max_count: int = 8) -> list[dict[str, Any]]:
    """Select 5 to 8 characters in random order to create a democratic discussion forum feel."""
    text = f"{title} {summary}".lower()
    target_count = random.randint(min_count, max_count)
    
    # 1. Check if any topic matches keywords to seed 2-3 contextual agents
    seeded_ids: list[str] = []
    for topic, data in TOPIC_SEEDS.items():
        if any(kw in text for kw in data["keywords"]):
            available = [cid for cid in data["candidates"] if cid in ALL_PERSONAS and cid not in seeded_ids]
            if available:
                seeded_ids.extend(random.sample(available, min(len(available), 2)))
        if len(seeded_ids) >= 3:
            break

    # 2. Fill the rest democratically from the entire remaining pool of 25 personas
    all_available_ids = [pid for pid in ALL_PERSONAS if pid not in seeded_ids]
    random.shuffle(all_available_ids)

    chosen_ids = list(seeded_ids)
    needed = target_count - len(chosen_ids)
    if needed > 0:
        chosen_ids.extend(all_available_ids[:needed])

    # 3. Randomize the speaking order completely so the flow is spontaneous and democratic
    random.shuffle(chosen_ids)
    
    return [ALL_PERSONAS[pid] for pid in chosen_ids]
