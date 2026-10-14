"""RSS and Media Feed Ingestion Engine.
Fetches soccer news from Yahoo! Sports, Gekisaka, Soccer King, PR Times, and YouTube.
"""
from __future__ import annotations

import hashlib
import re
import datetime
from typing import Any
import feedparser
from bs4 import BeautifulSoup

FEEDS = [
    {
        "name": "Yahoo!サッカー",
        "url": "https://news.yahoo.co.jp/rss/topics/soccer.xml",
        "type": "rss"
    },
    {
        "name": "ゲキサカ",
        "url": "https://gekisaka.jp/feed",
        "type": "rss"
    },
    {
        "name": "サッカーキング",
        "url": "https://www.soccer-king.jp/feed",
        "type": "rss"
    },
    {
        "name": "PR TIMES (Jリーグ)",
        "url": "https://prtimes.jp/topics/keywords/J%E3%83%AA%E3%83%BC%E3%82%B0.rdf",
        "type": "rss"
    },
    {
        "name": "Jリーグ公式YouTube",
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCt3nzngy957fWd3c28qWpBg",
        "type": "youtube"
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


def fetch_all_feeds(limit_per_feed: int = 10) -> list[dict[str, Any]]:
    """Fetch and parse all configured soccer feeds."""
    articles = []
    seen_titles = set()

    for feed_info in FEEDS:
        try:
            parsed = feedparser.parse(feed_info["url"])
            entries = parsed.entries[:limit_per_feed]
            for entry in entries:
                title = clean_text(getattr(entry, "title", ""))
                if not title or title in seen_titles:
                    continue
                seen_titles.add(title)

                link = getattr(entry, "link", "")
                raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                summary = clean_text(raw_summary)
                if len(summary) > 300:
                    summary = summary[:297] + "..."

                iso_date, date_prefix = parse_entry_date(entry)
                slug = generate_slug(date_prefix, title)

                # Extract thumbnail if available
                thumbnail = None
                if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
                    thumbnail = entry.media_thumbnail[0].get("url")
                elif hasattr(entry, "enclosures") and entry.enclosures:
                    for enc in entry.enclosures:
                        if enc.get("type", "").startswith("image/"):
                            thumbnail = enc.get("href")
                            break

                article = {
                    "id": slug,
                    "slug": slug,
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": feed_info["name"],
                    "feed_type": feed_info["type"],
                    "published_at": iso_date,
                    "date_prefix": date_prefix,
                    "thumbnail": thumbnail,
                }
                articles.append(article)
        except Exception as e:
            print(f"[RSS Fetcher] Warning: Failed to fetch {feed_info['name']} ({feed_info['url']}): {e}")

    # Sort descending by published_at
    articles.sort(key=lambda x: x["published_at"], reverse=True)
    return articles
