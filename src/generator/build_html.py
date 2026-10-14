"""Static Site HTML Builder for 芝ばたJ (Shibabata-J).
Uses Jinja2 to render static pages for Top, Categories, Team Tags, and Article Details.
Generates PWA manifest and service worker into public/.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "src" / "generator" / "templates"
PUBLIC_DIR = BASE_DIR / "public"
CONFIG_DIR = BASE_DIR / "src" / "config"


def load_teams_config() -> dict[str, Any]:
    with open(CONFIG_DIR / "teams.json", "r", encoding="utf-8") as f:
        return json.load(f)


def build_site(articles: list[dict[str, Any]]) -> None:
    """Build all static pages into public/."""
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    teams_config = load_teams_config()
    all_teams = teams_config.get("teams", [])
    categories = teams_config.get("categories", [])

    # Sort articles descending
    sorted_articles = sorted(articles, key=lambda x: x.get("published_at", ""), reverse=True)

    # 1. Render Top Page (public/index.html)
    top_template = env.get_template("index.html")
    top_html = top_template.render(
        articles=sorted_articles,
        all_teams=all_teams,
        current_category=None,
        current_team=None
    )
    with open(PUBLIC_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(top_html)
    print(f"[Build] Rendered Top page ({len(sorted_articles)} articles)")

    # 2. Render Category Pages (public/c/<category>/index.html)
    for cat in categories:
        cat_slug = cat["slug"]
        cat_dir = PUBLIC_DIR / "c" / cat_slug
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        filtered = [a for a in sorted_articles if a.get("category") == cat_slug]
        cat_html = top_template.render(
            articles=filtered,
            all_teams=all_teams,
            current_category=cat_slug,
            current_category_name=cat["name"],
            current_team=None
        )
        with open(cat_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(cat_html)
        print(f"[Build] Rendered Category: /c/{cat_slug}/ ({len(filtered)} articles)")

    # 3. Render Team Pages (public/t/<team>/index.html)
    for team in all_teams:
        team_slug = team["slug"]
        team_dir = PUBLIC_DIR / "t" / team_slug
        team_dir.mkdir(parents=True, exist_ok=True)
        
        filtered = [
            a for a in sorted_articles 
            if any(t.get("slug") == team_slug for t in a.get("team_tags", []))
        ]
        team_html = top_template.render(
            articles=filtered,
            all_teams=all_teams,
            current_category=None,
            current_team=team_slug,
            current_team_name=team["name"]
        )
        with open(team_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(team_html)

    # 4. Render Article Detail Pages (public/articles/<slug>/index.html)
    article_template = env.get_template("article.html")
    for i, article in enumerate(sorted_articles):
        slug = article["slug"]
        art_dir = PUBLIC_DIR / "articles" / slug
        art_dir.mkdir(parents=True, exist_ok=True)

        prev_article = sorted_articles[i - 1] if i > 0 else None
        next_article = sorted_articles[i + 1] if i < len(sorted_articles) - 1 else None

        art_html = article_template.render(
            article=article,
            dialogue=article.get("dialogue", []),
            punchy_quote=article.get("punchy_quote", ""),
            prev_article=prev_article,
            next_article=next_article
        )
        with open(art_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(art_html)

    print(f"[Build] Rendered {len(sorted_articles)} individual article pages")

    # 5. Generate PWA manifest.json
    manifest = {
        "name": "芝ばたJ - JリーグAIサロン",
        "short_name": "芝ばたJ",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#10b981",
        "description": "ピッチサイドの井戸端会議。20人のAI論客が語り尽くすJリーグ速報",
        "icons": [
            {
                "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>",
                "sizes": "192x192 512x512",
                "type": "image/svg+xml",
                "purpose": "any maskable"
            }
        ]
    }
    with open(PUBLIC_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 6. Generate lightweight Service Worker (public/sw.js)
    sw_code = """// 芝ばたJ Service Worker
const CACHE_NAME = 'shibabata-j-v1';
self.addEventListener('install', (e) => {
  self.skipWaiting();
});
self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim());
});
self.addEventListener('fetch', (e) => {
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
"""
    with open(PUBLIC_DIR / "sw.js", "w", encoding="utf-8") as f:
        f.write(sw_code)

    print("[Build] Generated PWA manifest.json and sw.js")
