"""X (Twitter) Outgoing Promotion Bot for 芝ばたJ.
Posts top news headlines with the punchy ChamberAI agent quote and link.
Uses X API v2 Free Tier via Tweepy.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATE_FILE = BASE_DIR / "state" / "tweeted.json"

X_API_KEY = os.getenv("X_API_KEY", "")
X_API_SECRET = os.getenv("X_API_SECRET", "")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN", "")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET", "")
BASE_URL = os.getenv("SITE_BASE_URL", "https://shibabata-j.web.app")


def load_tweeted_slugs() -> set[str]:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_tweeted_slugs(slugs: set[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(slugs), f, ensure_ascii=False, indent=2)


def format_tweet(article: dict[str, Any]) -> str:
    """Format tweet text within 280 character limit."""
    title = article.get("title", "")
    quote = article.get("punchy_quote", "")
    slug = article.get("slug", "")
    article_url = f"{BASE_URL}/articles/{slug}/"

    # Truncate title if needed
    if len(title) > 50:
        title = title[:47] + "…"

    # Truncate quote if needed
    if len(quote) > 70:
        quote = quote[:67] + "…"

    tags = "#芝ばたJ #Jリーグ"
    tweet = f"【話題の速報】{title}\n\n💬 AI論客の一言:\n「{quote}」\n\n👇 議論の続きを読む\n{article_url}\n\n{tags}"
    return tweet


def publish_article_to_x(article: dict[str, Any]) -> bool:
    """Post an article to X."""
    slug = article.get("slug", "")
    tweeted_slugs = load_tweeted_slugs()
    
    if slug in tweeted_slugs:
        print(f"[X Bot] Article {slug} already tweeted. Skipping.")
        return False

    tweet_text = format_tweet(article)

    # Check for X API credentials
    if not (X_API_KEY and X_API_SECRET and X_ACCESS_TOKEN and X_ACCESS_TOKEN_SECRET):
        print("[X Bot] (Dry Run - No X API keys found) Would post tweet:")
        print("--------------------------------------------------")
        print(tweet_text)
        print("--------------------------------------------------")
        tweeted_slugs.add(slug)
        save_tweeted_slugs(tweeted_slugs)
        return True

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=X_API_KEY,
            consumer_secret=X_API_SECRET,
            access_token=X_ACCESS_TOKEN,
            access_token_secret=X_ACCESS_TOKEN_SECRET
        )
        response = client.create_tweet(text=tweet_text)
        print(f"[X Bot] Successfully tweeted article {slug} (Tweet ID: {response.data.get('id')})")
        tweeted_slugs.add(slug)
        save_tweeted_slugs(tweeted_slugs)
        return True
    except Exception as e:
        print(f"[X Bot] Error posting to X: {e}")
        return False
