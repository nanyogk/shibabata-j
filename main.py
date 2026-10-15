"""Main CLI Coordinator for 芝ばたJ (Shibabata-J).
Orchestrates RSS ingestion, topic-routed ChamberAI persona generation, static HTML building, and X posting.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.ingest.categorizer import enrich_article_with_tags


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ARTICLES_FILE = DATA_DIR / "articles.json"


def load_articles() -> list[dict[str, Any]]:
    if ARTICLES_FILE.exists():
        try:
            with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_articles(articles: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def create_sample_articles() -> list[dict[str, Any]]:
    """Generate realistic initial soccer articles including YouTube video highlights and fan buzz."""
    samples = [
        {
            "id": "20261015-jleague-highlight-kobe-hiroshima",
            "slug": "20261015-jleague-highlight-kobe-hiroshima",
            "title": "【公式ハイライト】ヴィッセル神戸 vs サンフレッチェ広島｜明治安田J1 第30節 首位攻防の死闘！",
            "link": "https://www.youtube.com/watch?v=0kF43J6_QY0",
            "video_id": "0kF43J6_QY0",
            "summary": "首位を争うヴィッセル神戸とサンフレッチェ広島の直接対決。後半89分、ペナルティエリア手前から放たれた反転ボレーシュートがネットを揺らし劇的な幕切れに。両GKの神セーブが連発した今季屈指の好ゲーム。",
            "source": "Jリーグ公式YouTube",
            "category": "j1",
            "team_tags": [
                {"slug": "vissel-kobe", "name": "ヴィッセル神戸", "short_name": "神戸", "category": "j1", "color": "#9b003f"},
                {"slug": "sanfrecce-hiroshima", "name": "サンフレッチェ広島", "short_name": "広島", "category": "j1", "color": "#51237c"}
            ],
            "fan_comments": [
                "89分の反転シュート、トラップからインパクトまで完璧すぎて変な声出たわ",
                "92分のキーパーの指先ビッグセーブえぐすぎるだろ！今季の年間最優秀セーブ候補",
                "後半ATのペナルティエリア内の接触、VAR入るかと思ったけどインシデンタルでノーファウル妥当",
                "これぞJ1の頂上決戦！両チームとも球際バチバチでスタジアムの熱気すごかった"
            ],
            "published_at": "2026-10-15T05:00:00Z",
            "date_prefix": "20261015"
        },
        {
            "id": "20261015-dazn-mitoma-assist",
            "slug": "20261015-dazn-mitoma-assist",
            "title": "【DAZN特報】三笘薫、敵地を沈黙させる圧巻2アシスト！地元メディア満点評価の全タッチ集",
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "video_id": "dQw4w9WgXcQ",
            "summary": "ブライトン三笘薫がプレミアリーグ第8節で無双の活躍。左サイドを単独で切り裂くドリブル突破と右足アウトサイドでの芸術的スルーパスで2ゴールを演出し、敵地サポーターすら脱帽させた。",
            "source": "DAZN Japan公式YouTube",
            "category": "overseas",
            "team_tags": [{"slug": "overseas-players", "name": "海外日本人選手", "short_name": "海外組", "category": "overseas", "color": "#1e293b"}],
            "fan_comments": [
                "2点目のアウトサイドパス、視野が広すぎて何回見返しても鳥肌立つ",
                "対峙したイングランド代表DFが完全に重心崩されてて草",
                "このレベルのプレー連発してるなら早くCL常連のメガクラブに移籍してほしい"
            ],
            "published_at": "2026-10-15T04:30:00Z",
            "date_prefix": "20261015"
        },
        {
            "id": "20261015-urawa-transfer",
            "slug": "20261015-urawa-transfer",
            "title": "浦和レッズ、欧州組の日本代表MFに完全移籍オファー！違約金はクラブ史上最高の約8億円規模か",
            "link": "https://news.yahoo.co.jp/soccer",
            "summary": "浦和レッズが欧州クラブで主力として活躍する日本代表MFの獲得に乗り出していることが判明した。推定移籍金は約8億円で、実現すればJリーグ史上最高クラスの大型契約となる見込み。中盤の得点力強化を目指す。",
            "source": "Yahoo!サッカー",
            "category": "j1",
            "team_tags": [{"slug": "urawa-reds", "name": "浦和レッズ", "short_name": "浦和", "category": "j1", "color": "#e60012"}],
            "fan_comments": [
                "8億円はJリーグとしては超破格だけど中盤の補強は最優先課題だから納得",
                "若手の育成枠が削られるんじゃないかって不安もあるけどタイトル獲るならこれくらい必要"
            ],
            "published_at": "2026-10-15T04:00:00Z",
            "date_prefix": "20261015"
        },
        {
            "id": "20261015-j2-playoff-race",
            "slug": "20261015-j2-playoff-race",
            "title": "大混戦のJ2昇格プレーオフ争い！残り3節で勝ち点差わずか2の中に6クラブがひしめく死闘",
            "link": "https://prtimes.jp",
            "summary": "過酷なJ2リーグは終盤戦を迎え、J1昇格プレーオフ出場権を巡る争いが過熱。毎節順位が激しく入れ替わるJ2沼の過酷さに全国のサポーターが熱狂している。",
            "source": "PR TIMES (Jリーグ)",
            "category": "j2",
            "team_tags": [],
            "fan_comments": [
                "J2は毎週末胃が痛いけど面白すぎる。全試合DAZNで見逃せない",
                "6位と11位の勝ち点差が3しかないとか狂気の世界だろ"
            ],
            "published_at": "2026-10-15T00:45:00Z",
            "date_prefix": "20261015"
        }
    ]
    return samples


def run_pipeline(fetch: bool, build: bool, tweet: bool, sample: bool, force_dialogue: bool = False) -> None:
    existing_articles = load_articles()
    articles_map = {a["slug"]: a for a in existing_articles}

    if sample and not existing_articles:
        print("[Pipeline] Seeding realistic sample articles...")
        samples = create_sample_articles()
        for s in samples:
            articles_map[s["slug"]] = s

    if fetch:
        from src.ingest.rss_fetcher import fetch_all_feeds
        print("[Pipeline] Fetching RSS feeds...")
        raw_items = fetch_all_feeds(limit_per_feed=8)
        for item in raw_items:
            slug = item["slug"]
            if slug not in articles_map:
                enriched = enrich_article_with_tags(item)
                articles_map[slug] = enriched

    # Generate ChamberAI dialogue for articles that do not have it yet (or when forced)
    new_count = 0
    from src.salon.dialogue import generate_chamber_dialogue
    for slug, article in articles_map.items():
        if force_dialogue or "dialogue" not in article or not article["dialogue"]:
            print(f"[ChamberAI] Routing topic & generating dialogue: {article['title'][:30]}...")
            dialogue, punchy_quote = generate_chamber_dialogue(article)
            article["dialogue"] = dialogue
            article["punchy_quote"] = punchy_quote
            new_count += 1

    all_articles = list(articles_map.values())
    save_articles(all_articles)
    print(f"[Pipeline] Total articles tracked: {len(all_articles)} (new dialogues: {new_count})")

    if build:
        from src.generator.build_html import build_site
        print("[Pipeline] Building static HTML site...")
        build_site(all_articles)

    if tweet and all_articles:
        from src.bot.x_publisher import publish_article_to_x
        latest = sorted(all_articles, key=lambda x: x.get("published_at", ""), reverse=True)[0]
        print(f"[Pipeline] Attempting to tweet latest article: {latest['title'][:30]}...")
        publish_article_to_x(latest)


def main():
    parser = argparse.ArgumentParser(description="芝ばたJ (Shibabata-J) Pipeline")
    parser.add_argument("--fetch", action="store_true", help="Fetch fresh news from RSS")
    parser.add_argument("--build", action="store_true", help="Build static site into public/")
    parser.add_argument("--tweet", action="store_true", help="Publish latest article to X")
    parser.add_argument("--sample", action="store_true", help="Seed sample articles for testing")
    parser.add_argument("--force-dialogue", action="store_true", help="Force regenerate ChamberAI dialogue with LLM")
    parser.add_argument("--all", action="store_true", help="Run full pipeline (Fetch -> Dialogue -> Build -> Tweet)")
    args = parser.parse_args()

    if args.all:
        run_pipeline(fetch=True, build=True, tweet=True, sample=True, force_dialogue=args.force_dialogue)
    elif args.sample:
        run_pipeline(fetch=False, build=True, tweet=False, sample=True, force_dialogue=args.force_dialogue)
    else:
        run_pipeline(
            fetch=args.fetch,
            build=args.build,
            tweet=args.tweet,
            sample=False,
            force_dialogue=args.force_dialogue
        )


if __name__ == "__main__":
    main()
