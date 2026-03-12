"""単語帳ページ"""

import streamlit as st
from modules.data_manager import load_vocabulary, add_word, delete_word
from modules.preset_words import PRESET_CATEGORIES


def render():
    st.header("📖 単語帳")

    tab_add, tab_list, tab_preset = st.tabs(["単語を追加", "単語一覧", "重要単語集"])

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
            st.info("まだ単語が登録されていません。「単語を追加」タブまたは「重要単語集」から追加してください。")
            return

        st.write(f"登録単語数: **{len(words)}語**")

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

    with tab_preset:
        st.write("ネイティブが日常会話でよく使う重要単語・表現です。単語帳に追加して学習できます。")

        my_words = {w["english"].lower() for w in load_vocabulary()}

        category = st.selectbox("カテゴリ", list(PRESET_CATEGORIES.keys()))
        preset_list = PRESET_CATEGORIES[category]

        not_added = [w for w in preset_list if w["english"].lower() not in my_words]
        if not_added:
            if st.button(f"未登録の {len(not_added)} 語をまとめて追加", use_container_width=True, type="primary"):
                count = 0
                for w in not_added:
                    if add_word(w["english"], w["japanese"], w["example"]):
                        count += 1
                st.success(f"{count} 語を追加しました！")
                st.rerun()
        else:
            st.success("このカテゴリの単語はすべて登録済みです！")

        st.divider()

        for w in preset_list:
            already = w["english"].lower() in my_words
            col1, col2 = st.columns([4, 1])
            with col1:
                status = "  ✓" if already else ""
                st.markdown(f"**{w['english']}**{status} — {w['japanese']}")
                st.caption(f"例: {w['example']}")
            with col2:
                if already:
                    st.write("登録済み")
                else:
                    if st.button("追加", key=f"preset_{w['english']}", use_container_width=True):
                        add_word(w["english"], w["japanese"], w["example"])
                        st.rerun()
