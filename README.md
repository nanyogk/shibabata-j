# 芝ばたJ (Shibabata-J)

**25人のAI論客が語り尽くすサッカー井戸端速報** — powered by the standalone [**monju**](https://github.com/nanyogk/monju) Talkroom SDK.

## Architecture
This repository contains **only site-specific JSON configurations and data**:
- `config/site.json` — Branding, locale (`ja`), theme, and starter Sportsnavi-style presets (`⭐ J+代表`, `🌍 EPL+欧州`, expandable up to 5 slots)
- `config/taxonomy.json` — Heart-First categories (`J1 | J2・J3 | 日本代表 | EPL | 欧州`) & clubs
- `config/feeds.json` — Live RSS & YouTube highlight feeds (J.League, DAZN, JFATV, U-NEXT Football, WOWOW Soccer, Yahoo! Soccer, Soccer King)
- `config/personas.json` — 25 football banter personas & topic seeds

All reusable ingestion, screenplay generation, static HTML/PWA building, and preset UI code lives in [**`nanyogk/monju`**](https://github.com/nanyogk/monju).

## Commands

```bash
# Check HTTP health of all configured RSS & YouTube feeds
python3 main.py --check-feeds

# Fetch live feeds, recategorize, generate banter, and build public/
python3 main.py --fetch --build

# Re-apply taxonomy.json rules to existing articles and rebuild
python3 main.py --recategorize --build

# Test live Gemini 2.0 Flash 1-call screenplay generation
python3 test_llm.py

# Serve locally
python3 -m http.server 8000 --directory public
```
