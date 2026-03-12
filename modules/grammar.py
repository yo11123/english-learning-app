"""文法練習ページ（AIが問題を生成）"""

import streamlit as st
from modules.ai_helper import ask_claude, ask_claude_json


GRAMMAR_TOPICS = [
    "現在形と現在進行形",
    "過去形と現在完了形",
    "未来表現 (will / be going to)",
    "受動態",
    "関係代名詞",
    "仮定法",
    "比較級と最上級",
    "前置詞",
    "冠詞 (a/an/the)",
    "不定詞と動名詞",
]

LEVELS = ["初級", "中級", "上級"]


def render():
    st.header("文法練習")

    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox("トピック", GRAMMAR_TOPICS)
    with col2:
        level = st.selectbox("レベル", LEVELS)

    problem_type = st.radio("問題タイプ", ["並べ替え問題", "英作文問題"], horizontal=True)

    if "grammar_state" not in st.session_state:
        st.session_state.grammar_state = None

    if st.button("問題を生成", use_container_width=True):
        _generate_grammar_question(topic, level, problem_type)

    if st.session_state.grammar_state:
        _display_grammar_question()


def _generate_grammar_question(topic: str, level: str, problem_type: str):
    if problem_type == "並べ替え問題":
        prompt = f"""以下の条件で英語の並べ替え問題を1問作ってください。
- 文法トピック: {topic}
- レベル: {level}

重要なルール:
- wordsには、answerの英文を構成する全ての単語をシャッフルして入れること
- 同じ単語が2回以上使われる場合は、その回数分だけwordsに含めること（例: "the"が2回必要なら"the"を2つ入れる）
- カンマやピリオドなどの記号はwordsに含めないこと
- wordsの単語を全て使うとanswerの英文が完成するようにすること

以下のJSON形式で返してください（JSONのみ、他のテキストは不要）:
{{
    "japanese": "日本語の文",
    "words": ["シャッフルされた", "英単語", "の", "配列"],
    "answer": "正しい英文（カンマやピリオド付き）",
    "hint": "文構造のヒント（例: 'S + usually + V + O（習慣）, but + S + be + V-ing + O（今の動作）' のように記号で骨組みを示し、各パートの役割を短い日本語で補足する。文法トピック自体の説明はしないこと）"
}}"""
    else:
        prompt = f"""以下の条件で英作文問題を1問作ってください。
- 文法トピック: {topic}
- レベル: {level}

以下のJSON形式で返してください（JSONのみ、他のテキストは不要）:
{{
    "japanese": "日本語の文（これを英訳させる）",
    "answer": "模範解答の英文",
    "hint": "文構造のヒント（例: 'S + have + p.p. + O（経験）+ since + 時点' のように記号で骨組みを示し、各パートの役割を短い日本語で補足する。キーとなる単語も含める。文法トピック自体の説明はしないこと）"
}}"""

    with st.spinner("問題を生成中..."):
        max_retries = 3
        data = None
        for attempt in range(max_retries):
            data = ask_claude_json(
                "You are an English grammar teacher for Japanese students.",
                prompt,
                max_tokens=1024,
            )
            if data and problem_type == "並べ替え問題":
                data = _validate_and_fix_words(data)
            if data:
                break

    if data:
        import time
        st.session_state.grammar_state = {
            "type": problem_type,
            "data": data,
            "answered": False,
            "key_id": int(time.time() * 1000),
            "selected_words": [],  # 並べ替え用：選択済み単語のインデックス
        }
    else:
        st.error("問題の生成に失敗しました。もう一度試してください。")


def _validate_and_fix_words(data: dict) -> dict | None:
    """模範解答の全単語が語群に含まれているか検証し、不足があれば修正する"""
    import re as _re

    if "answer" not in data or "words" not in data:
        return None

    # 模範解答から句読点を除去して単語リストを作成
    answer_text = _re.sub(r"[.,!?;:\"']+", "", data["answer"])
    answer_words = answer_text.strip().lower().split()

    # 語群を小文字化してカウント
    word_pool = [w.lower() for w in data["words"]]
    pool_counts: dict[str, int] = {}
    for w in word_pool:
        pool_counts[w] = pool_counts.get(w, 0) + 1

    answer_counts: dict[str, int] = {}
    for w in answer_words:
        answer_counts[w] = answer_counts.get(w, 0) + 1

    # 不足している単語を追加
    fixed = False
    for word, need in answer_counts.items():
        have = pool_counts.get(word, 0)
        if have < need:
            # 元の大文字小文字を保持して追加
            # 模範解答から元の表記を探す
            original_words = data["answer"].replace(",", "").replace(".", "").replace("!", "").replace("?", "").split()
            original = word  # fallback
            for ow in original_words:
                if ow.lower() == word:
                    original = ow
                    break
            for _ in range(need - have):
                data["words"].append(original)
            fixed = True

    # 語群に余分な単語がないかもチェック
    pool_counts2: dict[str, int] = {}
    for w in [w.lower() for w in data["words"]]:
        pool_counts2[w] = pool_counts2.get(w, 0) + 1

    for word, have in pool_counts2.items():
        need = answer_counts.get(word, 0)
        if have > need:
            # 余分な単語を削除
            to_remove = have - need
            new_words = []
            removed = 0
            for w in reversed(data["words"]):
                if w.lower() == word and removed < to_remove:
                    removed += 1
                else:
                    new_words.append(w)
            data["words"] = list(reversed(new_words))
            fixed = True

    # シャッフルし直す
    if fixed:
        import random
        random.shuffle(data["words"])

    return data


def _display_grammar_question():
    gs = st.session_state.grammar_state
    data = gs["data"]
    kid = gs.get("key_id", 0)

    st.subheader("問題")
    st.markdown(f"**日本語:** {data['japanese']}")
    st.divider()

    if gs["type"] == "並べ替え問題":
        # ヒントボタン
        if "hint" in data and not gs["answered"]:
            if st.button("ヒントを見る", key=f"hint_{kid}"):
                st.info(f"ヒント: {data['hint']}")

        st.write("単語をクリックして並べ替えてください:")
        selected = gs.get("selected_words", [])
        words = data["words"]

        # 語群を表示（使用済みは半透明）
        cols = st.columns(min(len(words), 6))
        for i, word in enumerate(words):
            col = cols[i % len(cols)]
            used = i in selected
            with col:
                if used:
                    st.markdown(
                        f'<div style="padding:8px;border-radius:8px;text-align:center;'
                        f'background:#e0e0e0;color:#aaa;margin:4px 0;">'
                        f'<s>{word}</s></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    if not gs["answered"] and st.button(word, key=f"word_{kid}_{i}", use_container_width=True):
                        selected.append(i)
                        gs["selected_words"] = selected
                        st.rerun()

        # 選択済みの単語を回答欄として表示
        if selected:
            answer_words = [words[i] for i in selected]
            st.markdown("**あなたの回答:**")
            st.info(" ".join(answer_words))

            # 最後の単語を取り消すボタン
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                if not gs["answered"] and st.button("最後の単語を取り消す", key=f"undo_{kid}", use_container_width=True):
                    selected.pop()
                    gs["selected_words"] = selected
                    st.rerun()
            with c2:
                if not gs["answered"] and st.button("全てクリア", key=f"clear_{kid}", use_container_width=True):
                    gs["selected_words"] = []
                    st.rerun()
            with c3:
                if not gs["answered"] and len(selected) == len(words):
                    if st.button("回答する", key=f"grammar_submit_{kid}", use_container_width=True, type="primary"):
                        gs["answered"] = True
                        answer = " ".join(answer_words)
                        _check_answer(answer, data["answer"])
        else:
            st.caption("上の単語をクリックして文を作ってください。")

    else:  # 英作文
        if "hint" in data:
            st.info(f"ヒント: {data['hint']}")
        answer = st.text_area("英文を入力", key=f"grammar_answer_{kid}", disabled=gs["answered"])
        if st.button("回答する", key=f"grammar_submit_{kid}", disabled=gs["answered"]):
            gs["answered"] = True
            _check_composition(answer, data)


def _normalize(text: str) -> str:
    """比較用に句読点を除去して小文字化"""
    import re as _re
    return _re.sub(r"[.,!?;:\"']+", "", text).strip().lower()


def _check_answer(user_answer: str, correct: str):
    if _normalize(user_answer) == _normalize(correct):
        st.success(f"正解！ ✓\n\n**模範解答:** {correct}")
    else:
        st.error(f"不正解...\n\n**あなたの回答:** {user_answer}\n\n**模範解答:** {correct}")


def _check_composition(user_answer: str, data: dict):
    if not user_answer.strip():
        st.warning("回答を入力してください。")
        return

    feedback = ask_claude(
        "You are an English teacher for Japanese students. Evaluate the student's English translation. "
        "Respond in Japanese. Be encouraging but point out errors.",
        f"日本語原文: {data['japanese']}\n模範解答: {data['answer']}\n生徒の回答: {user_answer}\n\n"
        "評価してください（正しいか、文法的に問題はないか、より自然な表現はあるか）。",
        max_tokens=1024,
    )
    st.markdown(f"**模範解答:** {data['answer']}")
    st.divider()
    st.markdown(f"**AI講師の評価:**\n\n{feedback}")
