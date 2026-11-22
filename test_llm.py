#!/usr/bin/env python3
"""Interactive LLM Screenplay Tester for 芝ばたJ (powered by monju SDK)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent
SIBLING_MONJU = SITE_ROOT.parent / "monju"
if SIBLING_MONJU.exists() and str(SIBLING_MONJU) not in sys.path:
    sys.path.insert(0, str(SIBLING_MONJU))

from monju.salon.router import select_personas_for_article  # noqa: E402
from monju.salon.screenplay import (  # noqa: E402
    call_gemini_screenplay_api,
    generate_fallback_screenplay,
    get_api_key,
)
from monju.site_loader import load_site  # noqa: E402


def main() -> None:
    ctx = load_site(SITE_ROOT)
    print("=" * 60)
    print(f" {ctx.site.get('logo_emoji', '⚽')} {ctx.site.get('brand_name')} — monju LLM Screenplay Tester")
    print("=" * 60)

    sample = {
        "title": "町田ゼルビアが首位攻防戦で劇的AT勝利！黒田監督の勝負手ズバリ",
        "summary": "J1第30節の天王山。後半アディショナルタイムにセットプレーから決勝ゴールを奪い町田が勝利。",
        "fan_comments": [
            "あの時間帯のロングスローを凌ぎきれなかった相手の集中力切れだな",
            "でも結果を出す黒田監督のリアリズムはプロとして正義だろ",
        ],
    }

    selected = select_personas_for_article(ctx, sample["title"], sample["summary"])
    print(f"[*] Total personas : {len(ctx.personas)}")
    print(f"[*] Selected cast  : {len(selected)} -> " + ", ".join(f"{p['avatar_emoji']} {p['short_name']}" for p in selected))
    print()

    api_key = get_api_key(ctx.site_dir)
    if not api_key:
        print("❌ [Status] GEMINI_API_KEY is NOT set.")
        print("   Get a free key at https://aistudio.google.com/app/apikey")
        print("   Then run: echo 'GEMINI_API_KEY=\"AIzaSy...\"' > .env\n")
        print("ℹ️  Running fallback screenplay preview:\n")
        for turn in generate_fallback_screenplay(ctx, selected, sample["title"], sample["fan_comments"]):
            print(f"  {turn['avatar_emoji']} {turn['speaker_name']} (#{turn['turn']}): 「{turn['content']}」")
        return

    print(f"✅ [Status] GEMINI_API_KEY detected: {api_key[:8]}...{api_key[-4:]}")
    t0 = time.time()
    dialogue = call_gemini_screenplay_api(ctx, selected, sample["title"], sample["summary"], sample["fan_comments"], api_key)
    print(f"🎉 [Success] Generated {len(dialogue)} turns in {time.time() - t0:.2f}s!\n")
    for turn in dialogue:
        print(f"  {turn['avatar_emoji']} {turn['speaker_name']} (#{turn['turn']}): 「{turn['content']}」")


if __name__ == "__main__":
    main()
