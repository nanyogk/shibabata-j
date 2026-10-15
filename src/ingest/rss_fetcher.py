"""Live RSS and Video Highlight Ingestion Engine.
Fetches verified live feeds from J.League Official YouTube, DAZN Japan, Yahoo! Soccer, and Soccer King.
"""
from __future__ import annotations

import hashlib
import re
import datetime
from typing import Any
import requests
import feedparser
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

FEEDS = [
    {
        "name": "Jリーグ公式YouTube",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCWc-XpFHPK1SwGcvpFPZ8NA",
        "type": "youtube"
    },
    {
        "name": "DAZN Japan公式YouTube",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCoFLB_Gw_AoxUuuzKjXrc_Q",
        "type": "youtube"
    },
    {
        "name": "Yahoo!サッカー速報",
        "url": "https://news.yahoo.co.jp/rss/media/soccerk/all.xml",
        "type": "rss"
    },
    {
        "name": "サッカーキング",
        "url": "https://www.soccer-king.jp/feed",
        "type": "rss"
    }
]


def clean_text(html_content: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def generate_slug(date_str: str, title: str) -> str:
    """Generate YYYYMMDD-hash slug from title."""
    h = hashlib.sha256(title.encode("utf-8")).hexdigest()[:8]
    sanitized_date = date_str.replace("-", "")[:8]
    return f"{sanitized_date}-{h}"


def parse_entry_date(entry: Any) -> tuple[str, str]:
    """Return ISO format string and date prefix YYYYMMDD."""
    now = datetime.datetime.now(datetime.timezone.utc)
    dt = now
    
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
        except Exception:
            dt = now
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            dt = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
        except Exception:
            dt = now

    iso_str = dt.isoformat()
    date_prefix = dt.strftime("%Y%m%d")
    return iso_str, date_prefix


def extract_fan_buzz_from_summary(title: str, summary: str, is_youtube: bool) -> list[str]:
    """Extract or simulate natural fan commentary buzz points based on real feed text."""
    buzz = []
    text = f"{title} {summary}"

    if "セーブ" in text or "GK" in text or "守護神" in text:
        buzz.append("GKの決定機阻止が完全に試合の流れを変えてたな")
    if "アシスト" in text or "パス" in text or "クロス" in text:
        buzz.append("ラストパスの視野とタイミングが完璧すぎて鳥肌立った")
    if "ゴール" in text or "得点" in text or "シュート" in text or "一撃" in text:
        buzz.append("あのシュートコースは相手キーパーもお手上げだろ")
    if "ダービー" in text or "死闘" in text or "首位" in text:
        buzz.append("スタジアムの熱気と球際のプレッシャーが画面越しにも伝わってきた")
    if "復帰" in text or "怪我" in text:
        buzz.append("無理せずコンディション整えて次節暴れてほしい！")

    if not buzz:
        buzz = [
            f"「{title[:22]}…」のプレー、ファンの間でも意見が分かれてて熱い！",
            "この局面での監督の交代判断が勝負の分かれ目だったな"
        ]

    return buzz[:3]


def fetch_all_feeds(limit_per_feed: int = 5) -> list[dict[str, Any]]:
    """Fetch and parse live configured soccer and YouTube feeds."""
    articles = []
    seen_titles = set()

    for feed_info in FEEDS:
        try:
            # Use browser headers to avoid 403 blocks
            resp = requests.get(feed_info["url"], headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                print(f"[RSS Fetcher] Warning: {feed_info['name']} returned HTTP {resp.status_code}")
                continue

            parsed = feedparser.parse(resp.content)
            entries = parsed.entries[:limit_per_feed]

            for entry in entries:
                title = clean_text(getattr(entry, "title", ""))
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)

                link = getattr(entry, "link", "")
                raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                summary = clean_text(raw_summary)
                if len(summary) > 280:
                    summary = summary[:277] + "..."

                iso_date, date_prefix = parse_entry_date(entry)
                slug = generate_slug(date_prefix, title)

                # Extract YouTube video ID
                video_id = None
                if feed_info["type"] == "youtube":
                    video_id = getattr(entry, "yt_videoid", None)
                    if not video_id and "v=" in link:
                        video_id = link.split("v=")[-1].split("&")[0]

                # Extract thumbnail
                thumbnail = None
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    thumbnail = entry.media_thumbnail[0].get("url")
                elif video_id:
                    thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

                fan_comments = extract_fan_buzz_from_summary(title, summary, is_youtube=(video_id is not None))

                article = {
                    "id": slug,
                    "slug": slug,
                    "title": title,
                    "link": link,
                    "summary": summary if summary else f"{title}の速報ハイライトです。",
                    "source": feed_info["name"],
                    "feed_type": feed_info["type"],
                    "video_id": video_id,
                    "thumbnail": thumbnail,
                    "fan_comments": fan_comments,
                    "published_at": iso_date,
                    "date_prefix": date_prefix,
                }
                articles.append(article)
        except Exception as e:
            print(f"[RSS Fetcher] Warning: Failed to fetch {feed_info['name']}: {e}")

    # Sort descending by published_at
    articles.sort(key=lambda x: x["published_at"], reverse=True)
    return articles
