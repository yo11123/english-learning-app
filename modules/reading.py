"""リーディング練習ページ"""

import streamlit as st
from modules.ai_helper import ask_claude, ask_claude_json


READING_TOPICS = [
    "日常生活",
    "旅行",
    "ビジネス",
    "テクノロジー",
    "環境問題",
    "文化・歴史",
    "健康・スポーツ",
    "科学",
]

LEVELS = ["初級 (中学レベル)", "中級 (高校レベル)", "上級 (大学・TOEIC)"]


def render():
    st.header("リーディング")

    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox("トピック", READING_TOPICS)
    with col2:
        level = st.selectbox("レベル", LEVELS)

    if "reading_state" not in st.session_state:
        st.session_state.reading_state = None

    if st.button("英文を生成", use_container_width=True):
        _generate_reading(topic, level)

    if st.session_state.reading_state:
        _display_reading()


def _generate_reading(topic: str, level: str):
    prompt = f"""以下の条件で英語のリーディング教材を作ってください。

- トピック: {topic}
- レベル: {level}

以下のJSON形式で返してください（JSONのみ）:
{{
    "title": "英文のタイトル",
    "text": "英文本文（150-250語程度）",
    "vocabulary": [
        {{"word": "難しい単語1", "meaning": "日本語の意味"}},
        {{"word": "難しい単語2", "meaning": "日本語の意味"}}
    ],
    "questions": [
        {{"question": "内容理解の質問（英語）", "answer": "模範解答（英語）"}},
        {{"question": "内容理解の質問2（英語）", "answer": "模範解答2（英語）"}}
    ]
}}"""

    with st.spinner("英文を生成中..."):
        data = ask_claude_json(
            "You are an English reading material creator for Japanese students.",
            prompt,
            max_tokens=8192,
        )

    if data:
        st.session_state.reading_state = {
            "data": data,
            "show_translation": False,
            "show_answers": {},
        }
    else:
        st.error("教材の生成に失敗しました。もう一度試してください。")


def _display_reading():
    rs = st.session_state.reading_state
    data = rs["data"]

    st.subheader(data["title"])

    # 本文（左）と問題（右）を横並びで表示
    text_col, question_col = st.columns([1, 1])

    with text_col:
        st.markdown("#### 本文")
        with st.container(border=True, height=500):
            st.markdown(data["text"])

            # 語彙リスト
            with st.expander("重要語彙"):
                for v in data.get("vocabulary", []):
                    st.write(f"- **{v['word']}**: {v['meaning']}")

            # 全文翻訳
            if st.button("全文を日本語に翻訳"):
                if not rs["show_translation"]:
                    with st.spinner("翻訳中..."):
                        translation = ask_claude(
                            "You are a translator. Translate the following English text to natural Japanese.",
                            data["text"],
                            max_tokens=500,
                        )
                        rs["translation"] = translation
                        rs["show_translation"] = True

            if rs.get("show_translation"):
                st.info(rs["translation"])

    with question_col:
        st.markdown("#### 内容理解問題")
        for i, q in enumerate(data.get("questions", [])):
            st.markdown(f"**Q{i+1}.** {q['question']}")
            user_answer = st.text_area(f"回答 Q{i+1}（英語で回答）", key=f"reading_q_{i}", height=80)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("回答を確認", key=f"check_reading_{i}"):
                    if user_answer.strip():
                        feedback = ask_claude(
                            "You are an English teacher for Japanese students. Compare the student's English answer with the model answer. "
                            "Give brief feedback in Japanese. Check if the meaning is correct and if the English grammar/expression is natural. Be encouraging.",
                            f"Question: {q['question']}\nModel answer: {q['answer']}\n"
                            f"Student's answer: {user_answer}",
                            max_tokens=500,
                        )
                        rs["show_answers"][i] = feedback
            with c2:
                if st.button("模範解答を見る", key=f"show_reading_{i}"):
                    rs["show_answers"][i] = f"**模範解答:** {q['answer']}"

            if i in rs.get("show_answers", {}):
                st.markdown(rs["show_answers"][i])
            st.divider()
