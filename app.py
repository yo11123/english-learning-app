"""英語学習アプリ - メインエントリーポイント"""

import streamlit as st

st.set_page_config(
    page_title="英語学習アプリ",
    page_icon="📚",
    layout="wide",
)

# ── APIキーをsecretsから読み込み ──
if "api_key" not in st.session_state:
    st.session_state.api_key = st.secrets.get("GEMINI_API_KEY", "")

# ページ管理
PAGES = [
    "🏠 ホーム",
    "📖 単語帳",
    "❓ クイズ",
    "📝 文法練習",
    "📰 リーディング",
    "🃏 フラッシュカード",
    "💬 AI英会話",
    "🔄 ネイティブ英語翻訳",
]

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 ホーム"


def go_to(page_name: str):
    st.session_state.current_page = page_name


# サイドバー
st.sidebar.title("📚 英語学習アプリ")
st.sidebar.divider()

for p in PAGES:
    if st.sidebar.button(
        p,
        key=f"nav_{p}",
        use_container_width=True,
        type="primary" if st.session_state.current_page == p else "secondary",
    ):
        go_to(p)
        st.rerun()

st.sidebar.divider()
st.sidebar.caption("Powered by Gemini AI")

# ページルーティング
page = st.session_state.current_page

if page == "🏠 ホーム":
    st.title("📚 英語学習アプリ")
    st.write("英語力を楽しく伸ばすための総合学習アプリです。")

    # クリックで各ページに飛べるカード
    MENU_ITEMS = [
        ("📖 単語帳", "英単語を登録して管理。正答率も自動記録されます。"),
        ("❓ クイズ", "4択・穴埋めで単語力をテスト。英→日、日→英の両方に対応。"),
        ("📝 文法練習", "AIが文法問題を自動生成。並べ替え・英作文に挑戦。"),
        ("📰 リーディング", "レベル別の英文読解。語彙リスト・内容理解問題付き。"),
        ("🃏 フラッシュカード", "登録した単語をカード形式で暗記。苦手順の表示も可能。"),
        ("💬 AI英会話", "10種類のシナリオでAIと英会話練習。ヒント・翻訳・文法チェック付き。"),
        ("🔄 ネイティブ英語翻訳", "日本語を入力→ネイティブが使う自然な英語に翻訳。複数の言い回しも提案。"),
    ]

    cols = st.columns(3)
    for i, (name, desc) in enumerate(MENU_ITEMS):
        with cols[i % 3]:
            with st.container(border=True):
                st.subheader(name)
                st.caption(desc)
                if st.button("開く", key=f"home_{name}", use_container_width=True):
                    go_to(name)
                    st.rerun()

    # 単語帳の統計
    from modules.data_manager import load_vocabulary
    words = load_vocabulary()
    if words:
        st.divider()
        st.subheader("学習状況")
        total = len(words)
        answered = [w for w in words if w["correct_count"] + w["wrong_count"] > 0]
        correct_total = sum(w["correct_count"] for w in words)
        wrong_total = sum(w["wrong_count"] for w in words)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("登録単語数", f"{total}語")
        m2.metric("学習済み", f"{len(answered)}語")
        m3.metric("総正解数", f"{correct_total}回")
        m4.metric("総正答率", f"{correct_total / (correct_total + wrong_total) * 100:.0f}%" if correct_total + wrong_total > 0 else "-")

elif page == "📖 単語帳":
    from modules.vocabulary import render
    render()

elif page == "❓ クイズ":
    from modules.quiz import render
    render()

elif page == "📝 文法練習":
    from modules.grammar import render
    render()

elif page == "📰 リーディング":
    from modules.reading import render
    render()

elif page == "🃏 フラッシュカード":
    from modules.flashcard import render
    render()

elif page == "💬 AI英会話":
    from modules.conversation import render
    render()

elif page == "🔄 ネイティブ英語翻訳":
    from modules.translation import render
    render()
