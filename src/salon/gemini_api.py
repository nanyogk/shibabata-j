"""Gemini API Client for ChamberAI persona generation.
Uses GEMINI_API_KEY if present, with graceful mock fallback for offline or zero-cost builds.
"""
from __future__ import annotations

import os
import random
from typing import Any
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def generate_persona_response(
    persona: dict[str, Any],
    article_title: str,
    article_summary: str,
    dialogue_history: list[dict[str, str]],
    turn: int
) -> str:
    """Generate a single comment for a persona."""
    if GEMINI_API_KEY:
        try:
            return call_gemini_api(persona, article_title, article_summary, dialogue_history, turn)
        except Exception as e:
            print(f"[Gemini API] Warning: API call failed ({e}). Falling back to rule-based generator.")

    # Graceful fallback generator based on persona catchphrases and keywords
    return generate_mock_comment(persona, article_title, turn)


def call_gemini_api(
    persona: dict[str, Any],
    article_title: str,
    article_summary: str,
    dialogue_history: list[dict[str, str]],
    turn: int
) -> str:
    """Call Gemini 2.0 Flash REST endpoint directly."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    history_text = "\n".join([f"{item['speaker_name']}: {item['content']}" for item in dialogue_history])
    
    prompt = f"""記事タイトル: {article_title}
記事要約: {article_summary}

これまでの会話の流れ:
{history_text if history_text else "（あなたが口火を切ります）"}

あなたのキャラクター設定:
{persona['system_prompt']}

指示:
- キャラクター設定に忠実に、記事や前の発言に対して1〜2文でテンポよく発言してください。
- 前置きや「承知しました」「私のコメント:」などのメタな説明は一切含めず、セリフのみを出力してください。
- ターン {turn} / 4
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 150
        }
    }
    
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    candidate = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    return candidate


def generate_mock_comment(persona: dict[str, Any], article_title: str, turn: int) -> str:
    """Rule-based witty fallback so static build always succeeds even with no internet/API key."""
    catchphrases = persona.get("catchphrases", ["興味深いニュースですね。"])
    catchphrase = random.choice(catchphrases)
    
    p_id = persona["id"]
    if p_id == "economist-wannabe":
        snippets = [
            f"「{article_title[:15]}…」の件、クラブの営業収益とスポンサーへの露出ROIで見れば、極めて妥当な投資判断と言えますね。",
            f"この動きは人件費比率を抑えつつ減価償却費を平準化する賢いアプローチ。客単価の上昇にも直結しますよ。",
            f"経営陣がどれだけDAZNの理念強化配分金を織り込んで予算編成したかが見どころです。"
        ]
    elif p_id == "coach-wannabe":
        snippets = [
            f"ビルドアップで3-2-5に可変するとき、相手のプレッシングトリガーをどう外すかが全てだろ！",
            f"戦術的に見れば5レーンの幅の取り方が甘い。俺なら後半開始から偽サイドバックをインサイドに絞らせるね。",
            f"記事読んだけど、監督の交代カードの切るタイミングが15分遅ぇんだよ！もっと前線からスイッチ入れろ！"
        ]
    elif p_id == "young-talent-hunter":
        snippets = [
            f"この選手、高円宮杯プレミアリーグで見た時から股関節の可動域とファーストタッチが別格だったんだよ。",
            f"ユース育ちの至宝をここで実戦投入しない手はない。欧州スカウトに見つかる前に早く代表に呼んでほしいね。",
            f"高校選手権の時から注目してたけど、フィジカルコンタクトの耐性がJのトップレベルに達してきた証拠だな。"
        ]
    else:  # ultras-supporter
        snippets = [
            f"細かい戦術や数字なんか後回し！ピッチで魂見せて走り切ってくれりゃそれでいいんだよ！",
            f"次節のホームはゴール裏をぎっしり埋めて声枯らすぞ！勝った後のスタジアムビールが一番美味ぇんだから！",
            f"泥臭く足止めるな！どんな形でも泥臭く勝ち点3もぎ取ってこい！！"
        ]
    
    snippet = random.choice(snippets)
    if turn == 1:
        return f"{snippet} {catchphrase}"
    elif turn == 4:
        return f"{catchphrase} 要するに、{snippet}"
    return f"{catchphrase} {snippet}"
