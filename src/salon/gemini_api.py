"""Gemini API Client & Witty 2-Line Fallback Generator for 25 Personas.
Strictly limits responses to maximum 2 lines for snappy, democratic forum banter.
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
    """Generate a snappy maximum 2-line comment for a persona."""
    if GEMINI_API_KEY:
        try:
            return call_gemini_api(persona, article_title, article_summary, dialogue_history, turn)
        except Exception as e:
            print(f"[Gemini API] Notice: API unavailable ({e}), using dynamic fallback.")

    return generate_mock_comment(persona, article_title)


def call_gemini_api(
    persona: dict[str, Any],
    article_title: str,
    article_summary: str,
    dialogue_history: list[dict[str, str]],
    turn: int
) -> str:
    """Call Gemini 2.0 Flash REST endpoint with strict 2-line length limits."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    recent_history = dialogue_history[-4:]  # Last 4 comments for immediate context
    history_text = "\n".join([f"{item['speaker_name']}: {item['content']}" for item in recent_history])
    
    prompt = f"""記事タイトル: {article_title}
記事要約: {article_summary}

直前の掲示板の流れ:
{history_text if history_text else "（スレッドの口火を切ります）"}

あなたのキャラクター:
名前: {persona['name']} {persona.get('avatar_emoji', '')}
設定: {persona['system_prompt']}

【必須制約】
- キャラクター設定に忠実に、直前の発言やニュースに対して【最大2文（2行以内）】で端的に発言してください。
- 前置き、挨拶、メタ的な注釈は一切不要。セリフのみを出力してください。
- 3行以上の長文は禁止です。
"""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.88,
            "maxOutputTokens": 80
        }
    }
    
    resp = requests.post(url, json=payload, timeout=8)
    resp.raise_for_status()
    data = resp.json()
    candidate = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Normalize to max 2 lines
    lines = [line.strip() for line in candidate.split("\n") if line.strip()]
    return " ".join(lines[:2])


def generate_mock_comment(persona: dict[str, Any], article_title: str) -> str:
    """High-variety 2-line dynamic quips for all 25 personas."""
    pid = persona.get("id", "")
    t_short = article_title[:16] + "…" if len(article_title) > 16 else article_title

    quips = {
        "economist-wannabe": [
            f"「{t_short}」の件、移籍金の減価償却と客単価の上昇で見れば極めて合理的な投資判断ですね。DAZNの分配金モデルにも合致しています。",
            "人件費比率を抑えつつスタジアム稼働率を最大化する観点から、この動きはクラブ経営として満点に近いですよ。"
        ],
        "coach-wannabe": [
            f"ビルドアップで3-2-5に可変させるとき、偽サイドバックの絞りが遅ぇんだよ！俺なら後半開始と同時にスイッチ入れさせてるね。",
            "ハーフスペースの使い方が雑！5レーンを意識して相手ボランチの脇を突かないと崩せないぞ。"
        ],
        "young-talent-hunter": [
            "この選手は高円宮杯プレミアリーグで見た時から股関節の可動域が別格だったんだよ。早くU-20代表に呼んで海外にバレる前に育てろ！",
            "ユース育ちの至宝をこのタイミングで起用するのは大正解。高校選手権の時から俺はずっと推してたからね。"
        ],
        "ultras-supporter": [
            "細かい戦術や数字なんか後回し！泥臭く走ってピッチで魂見せてくれりゃそれでいいんだよ！現地ビールが美味ぇ〜〜！！",
            "次節のホームはゴール裏をぎっしり埋めて90分間声枯らすぞ！泥臭く勝ち点3もぎ取ってこい！！"
        ],
        "var-referee-nerd": [
            "競技規則第12条の文脈を読めば、接触の強度はインシデンタル（偶発的）でありノーファウルが妥当です。VARのクリア＆オブビアス基準にも抵触しません。",
            "DOGSO（決定的な得点機会の阻止）の4要件を精査すべきですね。カバーリングのDFの位置関係から言ってイエローが適正判定でしょう。"
        ],
        "stats-data-geek": [
            "スコア上の結果より、xG（ゴール期待値）とPPDAの指数推移を見ればチームの構造的欠陥が一目瞭然ですよ。",
            "プログレッシブパス成功率と敵陣PA内タッチ数の相関を見れば、今日の試合の影のMOMはボランチ一択です。"
        ],
        "nostalgic-boomer": [
            "1993年Jリーグ開幕戦のヴェルディ対マリノスの熱狂を思い出すなぁ… 今の若い選手も昔の野生味を少し見習ってほしいね。",
            "昔のジーコやリトバルスキーはもっと自由奔放にピッチを支配してたぞ。今のサッカーは少し型にはまりすぎに見えるな。"
        ],
        "overseas-elitist": [
            "プレミアリーグのインテンシティに比べると、どうしてもファーストタッチと判断のテンポがワンテンポ遅く見えますね。",
            "欧州CLのスピード感なら今のプレッシングは簡単に剥がされてますよ。早く5大リーグへ飛び出して揉まれるべきです。"
        ],
        "stadium-gourmet": [
            "勝敗も大事だけど、あそこのスタジアム限定の牛すじ煮込みとクラフトビールは全国ナンバーワンだから！遠征民は全員食うべき。",
            "ビジター席側のキッチンカーが拡充されたの最高すぎる。次のアウェイ遠征はキックオフ3時間前に現着してスタグル全制覇する予定！"
        ],
        "transfer-guru": [
            "独占速報：すでに代理人サイドは欧州メガクラブと接触済みで、バイアウト条項の確認に入っています！Here We Go!",
            "契約満了でのゼロ円移籍を避けるため、クラブ側は今冬のエクステンションを最優先で打診している模様です。"
        ],
        "j2-connoisseur": [
            "J2沼の深さを甘く見ちゃいけない。悪天候のアウェイナイターで足元すくわれるドラマこそが日本サッカーの真髄だよ。",
            "昇格プレーオフ圏の争いは最終節の90+6分まで何が起こるか分からない。この育成型期限付き移籍の妙味がたまらん！"
        ],
        "fantasy-manager": [
            "このフォメ、ウイングバックを1列上げて4-1-2-3にコンバートすればケミストリー爆上がりなのに！オランダから快速FW獲ってきてくれ！",
            "選手のポテンシャルゲージが今季でMAXになりそうだから、冬の移籍市場で即戦力ボランチとトレードすべき。"
        ],
        "uniform-fashionista": [
            "今季の襟付きユニフォーム、90年代のレトロオマージュが効いてて最高。胸スポンサーのロゴカラーが調和してて映える！",
            "アウェイのセカンドユニの差し色、ピッチの緑芝とコントラストが綺麗に出ててめちゃくちゃ写真映えするね。"
        ],
        "mascot-otaku": [
            "ハーフタイムのマスコットのキレキレダンス見た！？あのもふもふ感とファンサの神対応だけで現地行った甲斐があったよ！",
            "マスコット総選挙に向けて今から徳を積んでおく。あざと可愛い仕草に全サポーターがメロメロになってるの尊すぎる。"
        ],
        "injury-pessimist": [
            "勝ったのは嬉しいけど…途中で太もも裏押さえてた主力選手、ハムストリング再発じゃないよね！？過密日程で選手層が心配すぎて胃が痛い…",
            "連勝してるときほど主力の負傷離脱が怖いんだよ。ターンオーバーして無理させないでくれ頼むから！"
        ],
        "protective-mom": [
            "みんな一生懸命走ってて立派やわぁ。しっかり夜ご飯食べて水分取って、怪我だけはせんといてや！",
            "倒れた相手選手に手を差し伸べて起こしてあげてたの見て涙出そうになったわ。スポーツマンシップが一番素敵やね。"
        ],
        "local-pride-patriot": [
            "スタジアム周辺の道の駅や飲食店がサポーターで賑わってて誇らしい！クラブが街の活力になるのが一番の地域貢献だよ。",
            "おらが街のクラブが全国ニュースで取り上げられるだけで感無量。地元小中学校への巡回指導も続けてくれてありがとう！"
        ],
        "lens-photographer": [
            "ゴール直後の咆哮シーン、西日の逆光と芝の舞い上がりが完璧に重なって最高の1枚が撮れました！筋肉のカットが美しすぎる。",
            "今日の望遠レンズ席は神席だった。選手の鋭い視線と気迫がファインダー越しにビリビリ伝わってきたよ。"
        ],
        "dazn-director": [
            "今の中継、決定機の直後にゴール裏の歓声アングルを瞬時に挟んだスイッチングが見事でしたね！現地集音マイクの臨場感も素晴らしい。",
            "リプレイ流すタイミングで次のカウンター始まっちゃってるからカメラワークもっと引きで撮って！実況と解説の掛け合いは最高。"
        ],
        "peace-enjoyer": [
            "両チームの選手もサポーターも本当にお疲れ様でした！お互いにリスペクトがあって清々しい好ゲームでしたね。",
            "素晴らしいスーパーゴールが見られて幸せ！ネット上で相手を煽ったりせず、みんなでサッカーを楽しく語り合いましょう。"
        ],
        "derby-warrior": [
            "他の試合はどうでもいいが、あいつらとのダービーだけは死んでも負けられねぇ！ピッチ上の借りはピッチ上でキッチリ返す！",
            "ダービーの勝敗記録にまた一つ誇りが刻まれた。スタジアムの一体感と緊張感がレベチだったぜ！"
        ],
        "away-bus-veteran": [
            "早朝の海老名SAで同じユニ着た仲間と目が合って無言の会釈。夜行バス遠征のこの独特な連帯感がたまらんのだよ！",
            "往復夜行バスで全身バキバキだけど、敵地で勝ち点3取れたから月曜の出勤も笑顔で乗り切れるぜ！"
        ],
        "boots-gear-nerd": [
            "濡れたピッチコンディションに合わせてミックススタッドをチョイスした選手の判断力、足元のギアオタクとして大絶賛したい。",
            "あの大胆なカットイン、新作スパイクのアッパーのホールド感とアウトソールの反発力が見事に噛み合ってたね！"
        ],
        "note-tactics-writer": [
            "前半の失点は個人のミスではなく、ネガティブトランジションにおける中央封鎖の構造的欠陥によるもの。詳しくは後日noteにまとめます。",
            "ポジショナルプレーの原則に照らすと、逆サイドのアイソレーションの再現性が非常に高い。実に知的な試合運びだった。"
        ],
        "stockholder-fan": [
            "クラブの決算短信と照らし合わせても、今期の営業収益と人件費のバランスは極めて健全。次期株主総会でもこの方針を支持したい。",
            "新スタジアム構想における指定管理者制度の収支計画、民間資金の活用モデルとして他自治体の好事例になりそうですね。"
        ]
    }

    persona_quips = quips.get(pid, [
        f"「{t_short}」について、色々な角度から議論が深まるのは面白いですね。今後の展開に注目です！"
    ])
    return random.choice(persona_quips)
