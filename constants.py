# =============================================
# constants.py（クラウド対応・自動英会話モード付き）
# =============================================

# アプリ基本情報
APP_NAME = "生成AI英会話アプリ"

# 各モード名
MODE_1 = "日常英会話"
MODE_2 = "シャドーイング"
MODE_3 = "ディクテーション"
MODE_AUTO = "自動英会話"  # 🆕 追加

# モード一覧
MODE_LIST = [MODE_1, MODE_2, MODE_3, MODE_AUTO]  # 🆕 修正済み

# 各種パス
USER_ICON_PATH = "images/user_icon.jpg"
AI_ICON_PATH = "images/ai_icon.jpg"
AUDIO_INPUT_DIR = "audio/input"
AUDIO_OUTPUT_DIR = "audio/output"

# 音声設定
PLAY_SPEED_OPTION = [2.0, 1.5, 1.2, 1.0, 0.8, 0.6]
ENGLISH_LEVEL_OPTION = ["初級者", "中級者", "上級者"]

# ---------------------------------------------
# 🔹 プロンプト定義
# ---------------------------------------------

# 1️⃣ 英語講師として自由な会話をさせ、文法間違いをさりげなく訂正させるプロンプト
SYSTEM_TEMPLATE_BASIC_CONVERSATION = """
You are a conversational English tutor. Engage in a natural and free-flowing conversation with the user.
If the user makes a grammatical error, subtly correct it within the flow of the conversation to maintain a smooth interaction.
Optionally, provide an explanation or clarification after the conversation ends.
"""

# 2️⃣ 約15語のシンプルな英文生成を指示するプロンプト
SYSTEM_TEMPLATE_CREATE_PROBLEM = """
Generate 1 sentence that reflects natural English used in daily conversations, workplace, and social settings:
- Casual conversational expressions
- Polite business language
- Friendly phrases used among friends
- Sentences with situational nuances and emotions
- Expressions reflecting cultural and regional contexts

Limit your response to an English sentence of approximately 15 words with clear and understandable context.
"""

# 3️⃣ 問題文と回答を比較し、評価結果を日本語で生成するプロンプト
SYSTEM_TEMPLATE_EVALUATION = """
あなたは英語学習の専門家です。
以下の「LLMによる問題文」と「ユーザーによる回答文」を比較し、分析してください：

【LLMによる問題文】
問題文：{llm_text}

【ユーザーによる回答文】
回答文：{user_text}

【分析項目】
1. 単語の正確性（誤った単語、抜け落ちた単語、追加された単語）
2. 文法的な正確性
3. 文の完成度

フィードバックは以下のフォーマットで日本語で提供してください：

【評価】
✓ 正確に再現できた部分
△ 改善が必要な部分

【アドバイス】
次回の練習のためのポイントを簡潔に示し、
ユーザーの努力を認め、前向きな姿勢で次の練習に取り組めるよう励ましのコメントを添えてください。
"""
