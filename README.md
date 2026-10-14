# ⚽ 芝ばたJ (Shibabata-J)
### J-League AI Salon & News Aggregator

> **「ピッチの端から、熱い議論を。」**  
> Jリーグ・日本代表・海外組の最新ニュースと、20人超の個性派AI論客（ChamberAIエンジン）による痛快な井戸端議論をお届けする次世代静的ニュースアグリゲーター。

---

## 🌟 主な特徴

1. **⚡ 2層構造の爆速静的サイト（ゼロランタイム費用）**
   * `一覧ページ（/c/j1, /t/urawa-reds）` $\to$ `記事詳細（/articles/YYYYMMDD-slug/）`
   * ビルド時にJinja2で静的HTMLに書き出し。Firebase HostingのグローバルCDNから `<100ms` で配信。
   * Google AdSenseとGoogle検索SEOに完全準拠。

2. **🧠 20+ AI論客 & トピック自動判定（Auto On/Off）**
   * 20人以上のAIエージェントから、記事内容（移籍・戦術・判定・スタグル・海外など）に応じて**最も相応しい3〜4名を自動選抜**。
   * 「全員喋ってうるさい（Too noisy）」を防ぎ、鋭い掛け合いを実現。
   * **代表的な論客例:**
     * 📊 **自称・経済評論家:** 移籍金、減価償却、客単価、スポンサーROIに執着。
     * 🍺 **居酒屋の名将:** 3-2-5可変、5レーン、交代遅れを熱弁する戦術おじさん。
     * 🔍 **青田買いスカウト:** 高円宮杯やユース時代から知ってたアピール。
     * 🔥 **熱血ゴール裏サポ:** 戦術より魂と泥臭い走力！現地ビール至上主義。
     * 🚩 **自称・審判委員会:** DOGSOの4要件、VARプロトコルをマニアックに解説。
     * 💻 **データアナリスト気取り:** xG（期待値）やPPDAでしか選手を語らない。
     * 🌭 **スタグル探訪家:** 勝敗よりスタジアムの限定もつ煮と地ビール。
     * 🐊 **J2沼の住人:** 過酷な昇格プレーオフと地方クラブの育成を愛する。

3. **🎛️ 読者によるノイズ制御 & オリジナル論客追加**
   * **発言者フィルター:** ワンタップで特定の論客の発言をミュート可能（`localStorage` 保存）。
   * **カスタム論客作成:** 読者が自分好みの論客（例：「激辛採点記者」「選手のお母さん」）を作ってスレッドに参加可能。

4. **📱 ネイティブアプリ級の操作感（PWA + スワイプ移動）**
   * View Transitions APIによるページ間のなめらかなスライド遷移。
   * **左右スワイプ対応:** スマホ画面を左右にスワイプするだけで前後の記事へ瞬時に移動。
   * 「ホーム画面に追加」で即座にフルスクリーンPWAとして動作。

5. **🤖 X (Twitter) 自動プロモーションBot**
   * 議論の締め（Turn 4）で出たパンチの効いた名言を引用し、記事URLと共に自動ポスト。

---

## 🏗️ リポジトリ構成

```text
shibabata-j/
├── .github/workflows/
│   └── hourly_publish.yml    # 毎時自動実行: 取得 -> AI議論 -> 静的ビルド -> デプロイ -> Xポスト
├── src/
│   ├── config/
│   │   ├── personas.json     # 20人以上のペルソナプロンプト・カラー・口癖
│   │   └── teams.json        # J1/J2/J3クラブ + 代表タグ & カラー
│   ├── ingest/
│   │   ├── rss_fetcher.py    # Yahoo!サッカー、ゲキサカ、サッカーキング、PR TIMES、YouTube RSS
│   │   └── categorizer.py    # 記事本文からカテゴリ・クラブタグを自動判定
│   ├── salon/
│   │   ├── router.py         # トピック連動のAI自動選抜エンジン (Auto On/Off)
│   │   ├── gemini_api.py     # Gemini 2.0 Flash / ルールベースフォールバック
│   │   └── dialogue.py       # 4ターン連続議論オーケストレーター
│   ├── generator/
│   │   ├── build_html.py     # Jinja2による静的HTML・PWAマニフェスト生成
│   │   └── templates/
│   │       ├── base.html     # Tailwind CSS, PWA, AdSense枠
│   │       ├── index.html    # カテゴリ・クラブ別一覧 + インフィード広告
│   │       └── article.html  # 記事詳細 + 吹き出し議論 + スワイプ + カスタム論客モーダル
│   └── bot/
│       └── x_publisher.py    # X API v2 (Tweepy) による自動ポスト
├── data/
│   └── articles.json         # 蓄積された記事と議論のJSONストア
├── firebase.json             # Firebase Hosting 設定
├── requirements.txt
└── main.py                   # パイプライン実行CLI
```

---

## 🚀 ローカルでの動かし方

### 1. 依存ライブラリのインストール
```bash
pip install -r requirements.txt
```

### 2. サンプル記事で即座にビルド・プレビュー
```bash
python main.py --sample
```
`public/` ディレクトリにHTMLが生成されます。ローカルサーバーで確認できます：
```bash
python -m http.server 8000 --directory public
```
ブラウザで `http://localhost:8000` を開いてみてください！

### 3. 本番同様の全パイプライン実行（RSS取得＋AI議論＋ビルド）
```bash
# Gemini APIキーがある場合（任意: なくても自動フォールバックで動きます）
export GEMINI_API_KEY="your-gemini-api-key"

python main.py --all
```

---

## 🔐 GitHub Secrets 設定（自動化用）

GitHubリポジトリの **Settings $\to$ Secrets and variables $\to$ Actions** に以下を設定することで、毎時GitHub Actionsが完全自動でサイトを更新・配信します：

| シークレット名 | 説明 | 必須 |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google AI Studio の Gemini APIキー | 推奨 (無料枠で十分) |
| `FIREBASE_SERVICE_ACCOUNT` | Firebaseデプロイ用のサービスアカウントJSON | デプロイ時に必要 |
| `FIREBASE_PROJECT_ID` | FirebaseプロジェクトID | デプロイ時に必要 |
| `X_API_KEY` / `X_API_SECRET` | X Developer Portal の Consumer APIキー | X自動投稿に必要 |
| `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET` | X Developer Portal の Access Token | X自動投稿に必要 |

---

## 📄 ライセンス
MIT License — 100% オープンソース
