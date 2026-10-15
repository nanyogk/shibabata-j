#!/usr/bin/env python3
"""Interactive Test Utility for Gemini LLM Screenplay Generation.
Validates GEMINI_API_KEY, tests 1-call multi-persona screenplay banter,
and verifies regex parsing against Gemini 2.0 Flash.
"""
from __future__ import annotations

import sys
import time
from src.salon.gemini_api import (
    get_api_key,
    call_gemini_screenplay_api,
    generate_fallback_screenplay,
)
from src.salon.router import load_all_personas, select_personas_for_article


def main():
    print("=" * 60)
    print(" ⚽ Shibabata-J (芝ばたJ) - LLM Screenplay Tester")
    print("=" * 60)

    api_key = get_api_key()
    selected_personas = select_personas_for_article(
        title="町田ゼルビアが首位攻防戦で劇的AT勝利！黒田監督の勝負手ズバリ",
        summary="J1第30節の天王山。後半アディショナルタイムにセットプレーから決勝ゴールを奪い町田が勝利。"
    )

    sample_article = {
        "title": "町田ゼルビアが首位攻防戦で劇的AT勝利！黒田監督の勝負手ズバリ",
        "summary": "J1第30節の天王山。後半アディショナルタイムにセットプレーから決勝ゴールを奪い町田が勝利。球際の激しさと徹底したロングスロー戦術に賛否両論が巻き起こる。",
        "fan_comments": [
            "あの時間帯のロングスローを凌ぎきれなかった相手の集中力切れだな",
            "ファール判定で試合が止まりすぎて正直退屈な時間帯もあった",
            "でも結果を出す黒田監督のリアリズムはプロとして正義だろ"
        ]
    }

    personas = load_all_personas()
    print(f"[*] Total available personas : {len(personas)}")
    print(f"[*] Selected for this thread : {len(selected_personas)} personas")
    roster_str = ", ".join([f"{p['avatar_emoji']} {p['name']}" for p in selected_personas])
    print(f"    Roster: {roster_str}\n")

    if not api_key:
        print("❌ [Status] GEMINI_API_KEY is NOT set.\n")
        print("【必要な設定（1分で完了・無料）】")
        print("1. Google AI Studio にアクセス:")
        print("   👉 https://aistudio.google.com/app/apikey")
        print("2. Googleアカウントでログインし「Create API key」をクリック（クレジットカード不要・完全無料）")
        print("3. キーを取得後、以下のいずれかで設定してください:\n")
        print("   ■ 方法A (.env ファイルに保存 - 推奨):")
        print('     echo \'GEMINI_API_KEY="AIzaSy..."\' > .env\n')
        print("   ■ 方法B (環境変数として一時設定):")
        print('     export GEMINI_API_KEY="AIzaSy..."\n')
        print("-" * 60)
        print("ℹ️  キー未設定時のフォールバック生成テストを実行します:\n")

        fallback_dialogue = generate_fallback_screenplay(
            selected_personas,
            sample_article["title"],
            sample_article["fan_comments"]
        )
        for d in fallback_dialogue:
            print(f"  {d['avatar_emoji']} {d['speaker_name']} (#{d['turn']}):")
            print(f"     「{d['content']}」\n")
        return

    # When API key is present, test real Gemini 2.0 Flash
    print(f"✅ [Status] GEMINI_API_KEY detected: {api_key[:8]}...{api_key[-4:]}")
    print("[*] Calling Gemini 2.0 Flash (1-Call Screenplay Batch)...")

    start_time = time.time()
    try:
        dialogue = call_gemini_screenplay_api(
            personas=selected_personas,
            article_title=sample_article["title"],
            article_summary=sample_article["summary"],
            fan_comments=sample_article["fan_comments"],
            api_key=api_key
        )
        elapsed = time.time() - start_time
        print(f"🎉 [Success] Generated {len(dialogue)} turns in {elapsed:.2f}s!\n")
        print("=" * 60)
        print(" 💬 生成された井戸端チャット（実Gemini 2.0 Flash応答）:")
        print("=" * 60)
        for d in dialogue:
            print(f"  {d['avatar_emoji']} {d['speaker_name']} (Turn #{d['turn']}):")
            print(f"     「{d['content']}」\n")

        print("=" * 60)
        print("📊 [Quota Check] 1 request consumed. Free tier allows 1,500 requests/day.")
        print("=" * 60)

    except Exception as e:
        print(f"❌ [Error] Gemini API call failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
