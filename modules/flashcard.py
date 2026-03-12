"""フラッシュカードページ"""

import random
import streamlit as st
from modules.data_manager import load_vocabulary, update_score


def render():
    st.header("フラッシュカード")

    words = load_vocabulary()
    if not words:
        st.warning("単語が登録されていません。まず単語帳から追加してください。")
        return

    # 設定
    mode = st.radio("表示モード", ["英語 → 日本語", "日本語 → 英語"], horizontal=True)
    order = st.radio("順番", ["ランダム", "登録順", "苦手な順"], horizontal=True)

    # 並べ替え
    if order == "ランダム":
        if "flash_shuffled" not in st.session_state or st.session_state.get("flash_order") != "ランダム":
            st.session_state.flash_shuffled = random.sample(words, len(words))
            st.session_state.flash_order = "ランダム"
        words = st.session_state.flash_shuffled
    elif order == "苦手な順":
        words = sorted(words, key=lambda w: _accuracy(w))
        st.session_state.flash_order = "苦手な順"
    else:
        st.session_state.flash_order = "登録順"

    # インデックス管理
    if "flash_index" not in st.session_state:
        st.session_state.flash_index = 0
    if "flash_revealed" not in st.session_state:
        st.session_state.flash_revealed = False

    idx = st.session_state.flash_index
    if idx >= len(words):
        st.session_state.flash_index = 0
        idx = 0

    # 進捗バー
    st.progress((idx + 1) / len(words), text=f"{idx + 1} / {len(words)}")

    word = words[idx]
    front = word["english"] if mode == "英語 → 日本語" else word["japanese"]
    back = word["japanese"] if mode == "英語 → 日本語" else word["english"]

    # カード表示
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            color: white;
            min-height: 200px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <h1 style="margin: 0; font-size: 2.5em;">{front}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # めくるボタン
    if not st.session_state.flash_revealed:
        if st.button("カードをめくる", use_container_width=True, type="primary"):
            st.session_state.flash_revealed = True
            st.rerun()
    else:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 16px;
                padding: 30px;
                text-align: center;
                color: white;
                margin: 0 0 20px 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                <h2 style="margin: 0;">{back}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if word.get("example"):
            st.caption(f"例文: {word['example']}")

        # 正解/不正解ボタン
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("覚えてた", use_container_width=True, type="primary"):
                update_score(word["english"], True)
                _next_card(len(words))
        with col2:
            if st.button("あやしい", use_container_width=True):
                _next_card(len(words))
        with col3:
            if st.button("覚えてなかった", use_container_width=True):
                update_score(word["english"], False)
                _next_card(len(words))

    # ナビゲーション
    st.divider()
    nav1, nav2, nav3 = st.columns([1, 1, 1])
    with nav1:
        if st.button("← 前", use_container_width=True, disabled=idx == 0):
            st.session_state.flash_index = idx - 1
            st.session_state.flash_revealed = False
            st.rerun()
    with nav2:
        if st.button("シャッフル", use_container_width=True):
            st.session_state.flash_shuffled = random.sample(load_vocabulary(), len(load_vocabulary()))
            st.session_state.flash_index = 0
            st.session_state.flash_revealed = False
            st.rerun()
    with nav3:
        if st.button("次 →", use_container_width=True, disabled=idx >= len(words) - 1):
            st.session_state.flash_index = idx + 1
            st.session_state.flash_revealed = False
            st.rerun()


def _next_card(total: int):
    st.session_state.flash_index = min(st.session_state.flash_index + 1, total - 1)
    st.session_state.flash_revealed = False
    st.rerun()


def _accuracy(word: dict) -> float:
    total = word["correct_count"] + word["wrong_count"]
    if total == 0:
        return 0.5
    return word["correct_count"] / total
