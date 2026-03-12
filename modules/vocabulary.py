"""単語帳ページ"""

import streamlit as st
from modules.data_manager import load_vocabulary, add_word, delete_word


def render():
    st.header("単語帳")

    tab_add, tab_list = st.tabs(["単語を追加", "単語一覧"])

    with tab_add:
        with st.form("add_word_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                english = st.text_input("英単語", placeholder="例: abandon")
            with col2:
                japanese = st.text_input("日本語の意味", placeholder="例: 捨てる、放棄する")
            example = st.text_input("例文（任意）", placeholder="例: He abandoned the project.")
            submitted = st.form_submit_button("追加", use_container_width=True)

            if submitted:
                if not english or not japanese:
                    st.warning("英単語と日本語の意味を入力してください。")
                elif add_word(english, japanese, example):
                    st.success(f"「{english}」を追加しました！")
                else:
                    st.warning(f"「{english}」は既に登録されています。")

    with tab_list:
        words = load_vocabulary()
        if not words:
            st.info("まだ単語が登録されていません。上のタブから追加してください。")
            return

        st.write(f"登録単語数: **{len(words)}語**")

        # 検索フィルター
        search = st.text_input("検索", placeholder="英単語または日本語で検索...")
        if search:
            words = [w for w in words if search.lower() in w["english"].lower() or search in w["japanese"]]

        for w in words:
            total = w["correct_count"] + w["wrong_count"]
            accuracy = f"{w['correct_count'] / total * 100:.0f}%" if total > 0 else "-"
            with st.expander(f"**{w['english']}** — {w['japanese']}　（正答率: {accuracy}）"):
                if w["example"]:
                    st.write(f"例文: _{w['example']}_")
                st.caption(f"正解: {w['correct_count']}回 / 不正解: {w['wrong_count']}回")
                if st.button("削除", key=f"del_{w['english']}"):
                    delete_word(w["english"])
                    st.rerun()
