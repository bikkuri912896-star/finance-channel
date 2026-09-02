import json
import re
import random
from pathlib import Path
import anthropic
import config

TOPIC_POOL = [
    {"word": "複利",           "romanji": "Compound Interest",           "theme": "お金が雪だるま式に増える仕組み",        "modern_hook": "アインシュタインが「人類最大の発明」と呼んだとされる複利の力"},
    {"word": "NISA",           "romanji": "NISA",                        "theme": "運用益が非課税になる日本の制度",         "modern_hook": "年間360万円まで運用益が完全非課税になる制度を使わない理由がない"},
    {"word": "iDeCo",          "romanji": "iDeCo",                       "theme": "掛金全額が所得控除になる老後資金作り",    "modern_hook": "毎月2万円の掛金で年間約4万8千円の税金が戻ってくる仕組み"},
    {"word": "インデックス投資", "romanji": "Index Investing",             "theme": "市場全体に乗っかる投資の王道",          "modern_hook": "バフェットが「プロより素人のインデックス投資の方が勝率が高い」と断言した理由"},
    {"word": "ドルコスト平均法", "romanji": "Dollar-Cost Averaging",       "theme": "暴落を味方にする定額積立の力",          "modern_hook": "暴落のたびに「安く買えた」と喜べるようになる投資の思考法"},
    {"word": "ETF",            "romanji": "ETF",                         "theme": "株式のように売買できる投資信託の進化形", "modern_hook": "コストが投資信託の10分の1以下という超低コストの資産運用手段"},
    {"word": "分散投資",        "romanji": "Diversification",             "theme": "リスクを下げながらリターンを狙う大原則", "modern_hook": "ロスチャイルド家が200年間「卵を一つのかごに盛るな」と言い続けてきた理由"},
    {"word": "緊急予備資金",     "romanji": "Emergency Fund",              "theme": "投資より先に用意すべきお金の盾",        "modern_hook": "コロナで職を失った人の中で、貯金ゼロの人が即日困窮した現実"},
    {"word": "インフレ",        "romanji": "Inflation",                   "theme": "銀行預金が目減りするお金の敵",          "modern_hook": "銀行の利息0.001%に対してインフレ率2%では実質マイナスになっている現実"},
    {"word": "年金",            "romanji": "Pension",                     "theme": "老後の公的収入の正しい理解",            "modern_hook": "「年金破綻する」は本当か？実は70歳まで待てば受給額が42%増える事実"},
    {"word": "生命保険",        "romanji": "Life Insurance",              "theme": "本当に必要な保障と過剰加入の見極め方",   "modern_hook": "日本人の保険料支払いは世界トップクラス。でも必要な保障は意外とシンプル"},
    {"word": "高額療養費制度",   "romanji": "High-Cost Medical System",    "theme": "月の医療費に上限がある知られていない制度","modern_hook": "手術・入院費が100万円かかっても、実質9万円程度で済む日本の制度"},
    {"word": "住宅ローン",       "romanji": "Mortgage",                    "theme": "持ち家vs賃貸の本当の答え",             "modern_hook": "35年ローンの総支払額は物件価格の1.5倍になることもある現実"},
    {"word": "4%ルール",        "romanji": "4% Rule",                     "theme": "資産を取り崩しても尽きない魔法の法則",  "modern_hook": "2000万円あれば毎年80万円引き出しても30年以上資産が持つという研究結果"},
    {"word": "FIRE",           "romanji": "FIRE",                        "theme": "経済的自由と早期退職の設計図",          "modern_hook": "30代でリタイアした人たちが実践した「生活費×25倍を貯める」という公式"},
    {"word": "配当株",          "romanji": "Dividend Stocks",             "theme": "保有するだけで現金が入ってくる株",      "modern_hook": "コカコーラ株を持ち続けたバフェットは年間数百億円の配当を受け取っている"},
    {"word": "S&P500",         "romanji": "S&P 500",                     "theme": "アメリカ主要500社に一括投資する指数",   "modern_hook": "過去100年で年平均約10%成長してきたアメリカ経済への最も簡単な投資法"},
    {"word": "バリュー投資",     "romanji": "Value Investing",             "theme": "割安な株を買うバフェット流の哲学",      "modern_hook": "バフェットが資産の99%を50歳以降に稼いだという「複利×長期」の組み合わせ"},
    {"word": "損切り",          "romanji": "Stop-Loss",                   "theme": "感情に勝てるかが投資の命運を分ける",    "modern_hook": "「塩漬け株」を持ち続ける人が損失を膨らませる心理学的な理由"},
    {"word": "72の法則",        "romanji": "Rule of 72",                  "theme": "資産が2倍になる年数を計算する魔法の数字","modern_hook": "「72÷利回り」で何年後に資産が2倍になるか一瞬で分かる計算式"},
    {"word": "不動産投資",       "romanji": "Real Estate Investment",      "theme": "REITで少額から不動産オーナーになる方法", "modern_hook": "1万円からマンションの大家になれるREITという仕組み"},
    {"word": "債券",            "romanji": "Bonds",                       "theme": "株と逆の動きをするリスク分散の柱",      "modern_hook": "株が暴落するとき債券が上昇することが多い理由と資産配分の考え方"},
    {"word": "金（ゴールド）",   "romanji": "Gold",                        "theme": "5000年間価値を保ち続けてきた安全資産",  "modern_hook": "戦争・インフレ・経済危機でも価値が消えなかった唯一の資産クラス"},
    {"word": "節税",            "romanji": "Tax Optimization",            "theme": "合法的に税金を減らすための知識",        "modern_hook": "ふるさと納税・iDeCo・NISAを組み合わせるだけで年20万円以上の節税になるケース"},
    {"word": "副業収入",        "romanji": "Side Income",                 "theme": "収入の柱を増やすリスク分散効果",        "modern_hook": "年収500万円+副業20万円で手取りが変わる仕組みと確定申告の必要性"},
    {"word": "家計管理",        "romanji": "Household Budgeting",         "theme": "収入と支出を把握する資産形成の土台",    "modern_hook": "貯蓄率30%を実現した人と0%の人の差は収入ではなく「見える化」だった"},
    {"word": "アセットアロケーション", "romanji": "Asset Allocation",     "theme": "何に投資するかより何割投資するかが重要", "modern_hook": "運用成績の90%以上はどの資産クラスに何%配分するかで決まるという研究"},
    {"word": "長期投資",        "romanji": "Long-Term Investing",         "theme": "時間を味方につける投資の鉄則",          "modern_hook": "20年間、市場の動きを完全無視し続けた投資家が最も高いリターンを得たデータ"},
    {"word": "リスクとリターン", "romanji": "Risk and Return",             "theme": "高リターンには必ず高リスクが伴う大原則", "modern_hook": "「絶対儲かる」という投資話が詐欺である理由はリターンとリスクの法則にある"},
    {"word": "投資信託",        "romanji": "Mutual Fund",                 "theme": "少額で分散投資できる金融商品の仕組み",  "modern_hook": "プロが運用する投資信託の8割以上がインデックスに負けるという衝撃的な事実"},
    {"word": "為替リスク",       "romanji": "Currency Risk",               "theme": "円安・円高が資産に与える影響",          "modern_hook": "円安で海外旅行が高くなる仕組みと、外貨建て資産が資産防衛になる理由"},
    {"word": "確定申告",        "romanji": "Tax Return",                  "theme": "年末調整だけでは戻らない税金がある",    "modern_hook": "副業収入・医療費控除・ふるさと納税で戻ってくるお金を放置している人が多い現実"},
    {"word": "クレジットカード", "romanji": "Credit Card",                  "theme": "賢い使い方と「35日後払いの罠」",       "modern_hook": "ポイント還元1%の裏で手数料15〜18%を支払わされるリボ払いの正体"},
    {"word": "生涯収入",        "romanji": "Lifetime Income",             "theme": "大卒サラリーマン2億円を最大化する考え方","modern_hook": "転職・副業・資格の取り方次第で生涯収入が数千万円変わるという現実"},
    {"word": "行動経済学",       "romanji": "Behavioral Economics",        "theme": "なぜ人は損をする判断をするのか",        "modern_hook": "ノーベル賞経済学者が証明した「人は得より損を2.5倍大きく感じる」プロスペクト理論"},
    {"word": "つみたてNISA",    "romanji": "Tsumitate NISA",              "theme": "毎月コツコツ積み立てる非課税の力",      "modern_hook": "毎月3万円を20年積み立てると元本720万円が利回り5%で約1500万円になる計算"},
    {"word": "不労所得",        "romanji": "Passive Income",              "theme": "寝ている間もお金が働く仕組み",          "modern_hook": "配当・賃料・ロイヤリティ―「お金に働いてもらう」3つの仕組みの作り方"},
    {"word": "ポートフォリオ",   "romanji": "Portfolio",                   "theme": "保有資産の最適な組み合わせの考え方",    "modern_hook": "「株60・債券30・金10」黄金比率と「自分のポートフォリオ」の作り方"},
    {"word": "生活防衛資金",     "romanji": "Financial Buffer",            "theme": "投資を始める前に必要な現金の準備",      "modern_hook": "生活費3ヶ月分の現金なしに投資を始めると最悪のタイミングで売らざるを得ない理由"},
    {"word": "金利と経済",       "romanji": "Interest Rates",              "theme": "日銀が動かす金利が生活に与える影響",    "modern_hook": "日銀が金利を0.1%上げるだけで住宅ローン返済額が数十万円変わる仕組み"},
    {"word": "仮想通貨",        "romanji": "Cryptocurrency",              "theme": "リスクと可能性を正しく理解するための知識","modern_hook": "ビットコインは10年で1万倍になったが同時に80%暴落を3回経験している事実"},
    {"word": "医療保険",        "romanji": "Health Insurance",            "theme": "民間医療保険が不要と言われる本当の理由", "modern_hook": "高額療養費制度と公的保険だけで月の医療費は約9万円が上限になる日本の現実"},
    {"word": "お金のメンタル",   "romanji": "Financial Mindset",           "theme": "投資で成功する人と失敗する人の思考の違い","modern_hook": "暴落時にパニック売りした人と無視した人の5年後の資産差が2倍になったデータ"},
]

SYSTEM_PROMPT = """あなたは資産形成・金融リテラシーの専門家であり、YouTube Shorts向け教育コンテンツの脚本家です。
日本人の視聴者に「お金の知識」を届ける短編動画の脚本をJSON形式で生成してください。

【脚本の構成原則】
「視聴者の日常にある疑問・驚き（給料・生活費・老後の不安）→ 実はこういう仕組みだったと明かす → 具体的な数字・事例で深掘り」
という順番で構成してください。難しい金融用語より、視聴者が「なるほど！」と感じる驚きと具体性を重視してください。

必ずJSON形式のみで返答し、マークダウンのコードブロック（```json など）は使わないでください。
返答はそのままJSONとしてパースできるものにしてください。"""

USER_PROMPT_TEMPLATE = """以下の金融リテラシーのテーマについて、YouTube Shorts（約55秒）の脚本を生成してください。

テーマ: {word}
英語: {romanji}
概要: {theme}
フックのきっかけ（イントロに使うこと）: {modern_hook}

【重要ルール】
1. narration（ナレーション）フィールドは必ず純粋な日本語のみで書いてください。
2. 各ナレーションは読み上げ時間が指定秒数に収まるよう、文字数を守ってください。
   - intro: 60〜80文字（約8秒）
   - word: 50〜70文字（約9秒）
   - meaning: 150〜180文字（約25秒）
   - outro: 固定テキストを使用
3. ナレーションは必ず話し言葉で書いてください。以下を守ってください：
   - 短い文を組み合わせる（一文は30文字以内を目安に）
   - 読点（、）を使って自然な間を作る
   - 「〜なのです」「〜でしょう」など語りかける口調を使う
   - 難しい書き言葉・漢語表現は避ける
4. タイトルは「○○とは」「○○を知らないと損する」など検索されやすい日本語を先頭に置いてください。
5. 具体的な数字・事例・著名人の発言を積極的に使ってください。

以下のJSON構造で脚本を返してください:

{{
  "title": "日本語で検索されやすいフック型タイトル（例：「複利の力―毎月3万円が20年で1500万円になる理由」）",
  "description": "YouTube概要欄テキスト（150文字程度、制度説明・具体的数字・実践のヒントを含める）",
  "tags": ["{word}", "金融リテラシー", "資産形成", "投資初心者", "Shorts", "お金の知識"],
  "latin_word": "{word}",
  "romanji": "{romanji}",
  "scenes": [
    {{
      "type": "intro",
      "narration": "「フックのきっかけ」を使って視聴者を引き込む驚きの一言・問いかけ"
    }},
    {{
      "type": "word",
      "latin_text": "{word}",
      "romanji": "{romanji}",
      "reading": "カテゴリータグ（例：投資の基礎・税制優遇・リスク管理・老後の備え）",
      "narration": "このテーマが重要である理由・日本人に特に関係する具体的な理由を端的に説明するナレーション"
    }},
    {{
      "type": "meaning",
      "subtitle": "このシーンの小見出し（10文字以内）",
      "latin_quote": "関連する有名な格言・重要な数字や計算式（例：72の法則・4%ルール）（任意）",
      "quote_source": "出典・提唱者（例：ウォーレン・バフェット）（任意）",
      "narration": "具体的な数字・事例を使って「なぜ今すぐ知るべきか」を語るナレーション（150〜180文字）"
    }},
    {{
      "type": "outro",
      "narration": "ぜひチャンネル登録をして、次の動画もお聞きください。"
    }}
  ]
}}"""


def load_used_topics() -> list:
    if config.USED_TOPICS_FILE.exists():
        with open(config.USED_TOPICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_used_topics(used: list):
    with open(config.USED_TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def pick_topic() -> dict:
    used = load_used_topics()
    available = [t for t in TOPIC_POOL if t["word"] not in used]
    if not available:
        save_used_topics([])
        available = TOPIC_POOL[:]
    topic = random.choice(available)
    used.append(topic["word"])
    save_used_topics(used)
    return topic


def generate_script(topic: dict | None = None) -> dict:
    if topic is None:
        topic = pick_topic()

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        word=topic["word"],
        romanji=topic["romanji"],
        theme=topic["theme"],
        modern_hook=topic.get("modern_hook", "お金の常識を覆す意外な事実"),
    )

    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    script = json.loads(raw)
    script["_topic"] = topic
    return script
