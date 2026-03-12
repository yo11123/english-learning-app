"""日本語→ネイティブ英語 パラフレーズ翻訳ページ"""

import streamlit as st
from modules.ai_helper import ask_claude_json


STYLES = {
    "カジュアル（日常会話）": "casual, everyday spoken English that a native speaker would use with friends",
    "丁寧（ビジネス・フォーマル）": "polite, professional English suitable for business emails and formal situations",
    "自然（ニュートラル）": "natural, neutral English that sounds native but is neither too casual nor too formal",
    "スラング多め（若者言葉）": "trendy, colloquial English with common slang that young native speakers use",
    "アカデミック（学術的）": "academic, sophisticated English suitable for essays and scholarly writing",
}


def _translate(japanese_text: str, style: str):
    """日本語をネイティブ英語にパラフレーズ翻訳"""
    system_prompt = f"""You are a bilingual translation expert who specializes in producing natural, native-sounding English.

Your task: translate the given Japanese text into English that a native speaker would actually say/write.
Style: {STYLES[style]}

IMPORTANT RULES:
- Do NOT produce literal/word-for-word translations
- Use natural English phrasing, idioms, and collocations
- Provide multiple paraphrase variations so the user can learn different ways to express the same idea

Return JSON:
{{
    "main": "最も自然な英訳",
    "variations": [
        {{"english": "別の言い方1", "note": "この表現のニュアンス（日本語で）"}},
        {{"english": "別の言い方2", "note": "この表現のニュアンス（日本語で）"}},
        {{"english": "別の言い方3", "note": "この表現のニュアンス（日本語で）"}}
    ],
    "vocabulary": [
        {{"word": "key phrase", "meaning": "意味・使い方の説明（日本語）"}}
    ],
    "literal_vs_natural": "直訳だとこうなるが、ネイティブはこう言う、という比較説明（日本語で）"
}}

Provide 2-4 variations. vocabulary should include 2-4 useful phrases/idioms from your translations."""

    return ask_claude_json(system_prompt, f"Translate this Japanese text:\n{japanese_text}")


def render():
    st.header("🔄 ネイティブ英語翻訳")
    st.write("日本語を入力すると、ネイティブが実際に使う自然な英語に翻訳します。")

    style = st.selectbox("文体スタイル", list(STYLES.keys()))

    japanese_input = st.text_area(
        "日本語を入力",
        height=120,
        placeholder="例: 昨日友達と久しぶりに会って、めっちゃ楽しかった！",
    )

    if st.button("翻訳する", use_container_width=True, type="primary", disabled=not japanese_input):
        with st.spinner("翻訳中..."):
            result = _translate(japanese_input, style)
        if result:
            st.session_state.translate_result = result

    result = st.session_state.get("translate_result")
    if not result:
        return

    # メイン翻訳
    st.subheader("メイン翻訳")
    st.markdown(
        f"""<div style="background-color: #1a1a2e; padding: 1.2rem; border-radius: 8px;
        border-left: 4px solid #4da6ff; font-size: 1.15rem; line-height: 1.8;">
        {result['main']}</div>""",
        unsafe_allow_html=True,
    )

    # バリエーション
    if result.get("variations"):
        st.subheader("別の言い方")
        for i, v in enumerate(result["variations"], 1):
            st.markdown(
                f"""<div style="background-color: #1e1e2e; padding: 0.8rem; border-radius: 6px;
                margin-bottom: 0.5rem; border-left: 3px solid #7c4dff;">
                <strong>{i}.</strong> {v['english']}<br>
                <span style="color: #aaa; font-size: 0.9rem;">💡 {v['note']}</span></div>""",
                unsafe_allow_html=True,
            )

    # 直訳 vs 自然な表現
    if result.get("literal_vs_natural"):
        with st.expander("📖 直訳 vs ネイティブ表現"):
            st.write(result["literal_vs_natural"])

    # 重要表現
    if result.get("vocabulary"):
        with st.expander("📝 覚えておきたい表現"):
            for v in result["vocabulary"]:
                st.write(f"- **{v['word']}**: {v['meaning']}")
