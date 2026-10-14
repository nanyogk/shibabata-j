"""Intelligent Topic Router for 20+ Personas.
Analyzes article keywords and automatically selects the 3-4 most relevant personas,
preventing dialogue noise and keeping banter sharp and contextual.
"""
from __future__ import annotations

import json
from pathlib import Path
import random
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "personas.json"

TOPIC_RULES = {
    "transfer_business": {
        "keywords": ["移籍", "契約", "違約金", "年俸", "完全移籍", "期限付き", "スポンサー", "決算", "売上", "配分金", "獲得", "加入", "退団"],
        "priority_personas": ["economist-wannabe", "transfer-guru", "fantasy-manager", "young-talent-hunter"],
        "fallback_personas": ["ultras-supporter", "coach-wannabe"]
    },
    "match_tactics": {
        "keywords": ["試合", "勝利", "敗戦", "ドロー", "ゴール", "失点", "スタメン", "先発", "交代", "フォーメーション", "監督", "解任", "采配", "ハイライト", "シュート"],
        "priority_personas": ["coach-wannabe", "stats-data-geek", "ultras-supporter", "var-referee-nerd"],
        "fallback_personas": ["nostalgic-boomer", "economist-wannabe"]
    },
    "referee_var": {
        "keywords": ["var", "ファウル", "レッドカード", "イエロー", "ハンド", "誤審", "審判", "主審", "退場", "オフサイド", "pk", "ペナルティ"],
        "priority_personas": ["var-referee-nerd", "coach-wannabe", "ultras-supporter", "stats-data-geek"],
        "fallback_personas": ["nostalgic-boomer"]
    },
    "stadium_culture": {
        "keywords": ["スタグル", "グルメ", "スタジアム", "ビール", "観客", "動員", "マスコット", "新スタ", "建設", "アウェイ", "遠征", "応援", "サポーター"],
        "priority_personas": ["stadium-gourmet", "ultras-supporter", "economist-wannabe", "nostalgic-boomer"],
        "fallback_personas": ["coach-wannabe"]
    },
    "national_overseas": {
        "keywords": ["日本代表", "森保", "samurai blue", "海外", "プレミア", "ブンデス", "ラリーガ", "セリエa", "欧州", "w杯", "アジア最終予選", "u-20", "u-23"],
        "priority_personas": ["overseas-elitist", "young-talent-hunter", "nostalgic-boomer", "coach-wannabe"],
        "fallback_personas": ["ultras-supporter", "stats-data-geek"]
    },
    "j2_j3_swamp": {
        "keywords": ["j2", "j3", "jfl", "昇格", "降格", "プレーオフ", "po圏", "地域リーグ"],
        "priority_personas": ["j2-connoisseur", "young-talent-hunter", "ultras-supporter", "economist-wannabe"],
        "fallback_personas": ["coach-wannabe"]
    }
}


def load_all_personas() -> dict[str, dict[str, Any]]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {p["id"]: p for p in data.get("personas", [])}


ALL_PERSONAS = load_all_personas()


def select_personas_for_article(title: str, summary: str, turn_count: int = 4) -> list[dict[str, Any]]:
    """Determine article topic and select the best 3-4 personas."""
    text = f"{title} {summary}".lower()
    
    # Score each topic
    topic_scores = {}
    for topic, rule in TOPIC_RULES.items():
        score = sum(1 for kw in rule["keywords"] if kw.lower() in text)
        topic_scores[topic] = score

    # Find highest scoring topic (if tie or 0, fallback to match_tactics)
    best_topic = max(topic_scores, key=topic_scores.get)
    if topic_scores[best_topic] == 0:
        best_topic = "match_tactics"

    rule = TOPIC_RULES[best_topic]
    chosen_ids: list[str] = []
    
    # Pick top priorities from the matched topic
    for pid in rule["priority_personas"]:
        if pid in ALL_PERSONAS and pid not in chosen_ids:
            chosen_ids.append(pid)
        if len(chosen_ids) >= turn_count:
            break

    # If still need more, pick from fallbacks or random pool
    if len(chosen_ids) < turn_count:
        for pid in rule.get("fallback_personas", []):
            if pid in ALL_PERSONAS and pid not in chosen_ids:
                chosen_ids.append(pid)
            if len(chosen_ids) >= turn_count:
                break

    # If still not enough, grab from all available
    remaining_ids = [pid for pid in ALL_PERSONAS if pid not in chosen_ids]
    random.shuffle(remaining_ids)
    while len(chosen_ids) < turn_count and remaining_ids:
        chosen_ids.append(remaining_ids.pop())

    # Shuffle selected personas so speaker order varies
    random.shuffle(chosen_ids)
    return [ALL_PERSONAS[pid] for pid in chosen_ids[:turn_count]]
