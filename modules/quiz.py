"""クイズモード（4択・穴埋め・英⇔日）"""

import random
import streamlit as st
from modules.data_manager import load_vocabulary, update_score
from modules.ai_helper import ask_claude


def render():
    st.header("クイズ")

    words = load_vocabulary()
    if len(words) < 4:
        st.warning("クイズには最低4つの単語が必要です。単語帳から追加してください。")
        return

    quiz_type = st.radio(
        "クイズの種類",
        ["英語 → 日本語（4択）", "日本語 → 英語（4択）", "穴埋め問題"],
        horizontal=True,
    )

    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = None

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("新しい問題を出題", use_container_width=True):
            _generate_question(words, quiz_type)
    with col2:
        if st.button("リセット", use_container_width=True):
            st.session_state.quiz_state = None
            st.rerun()

    if st.session_state.quiz_state:
        _display_question()


def _generate_question(words: list[dict], quiz_type: str):
    target = random.choice(words)
    others = [w for w in words if w["english"] != target["english"]]
    distractors = random.sample(others, min(3, len(others)))

    if quiz_type == "英語 → 日本語（4択）":
        question = f"「**{target['english']}**」の意味は？"
        correct = target["japanese"]
        options = [correct] + [d["japanese"] for d in distractors]
        random.shuffle(options)
        st.session_state.quiz_state = {
            "type": "choice",
            "question": question,
            "correct": correct,
            "options": options,
            "word": target["english"],
            "answered": False,
        }

    elif quiz_type == "日本語 → 英語（4択）":
        question = f"「**{target['japanese']}**」を英語で言うと？"
        correct = target["english"]
        options = [correct] + [d["english"] for d in distractors]
        random.shuffle(options)
        st.session_state.quiz_state = {
            "type": "choice",
            "question": question,
            "correct": correct,
            "options": options,
            "word": target["english"],
            "answered": False,
        }

    elif quiz_type == "穴埋め問題":
        example = target.get("example", "")
        if not example:
            # 例文がなければAIで生成
            example = ask_claude(
                "You are an English teacher. Generate a single simple English sentence using the given word. "
                "Replace the target word with '______'. Return ONLY the sentence with the blank.",
                f"Word: {target['english']}",
                max_tokens=100,
            )
        else:
            example = example.replace(target["english"], "______").replace(
                target["english"].lower(), "______"
            )

        st.session_state.quiz_state = {
            "type": "fill",
            "question": f"空欄に入る単語を入力してください:\n\n{example}",
            "correct": target["english"].lower(),
            "word": target["english"],
            "answered": False,
        }


def _display_question():
    qs = st.session_state.quiz_state

    st.subheader("問題")
    st.markdown(qs["question"])
    st.divider()

    if qs["type"] == "choice":
        for i, option in enumerate(qs["options"]):
            if st.button(option, key=f"opt_{i}", use_container_width=True, disabled=qs["answered"]):
                qs["answered"] = True
                if option == qs["correct"]:
                    st.success("正解！")
                    update_score(qs["word"], True)
                else:
                    st.error(f"不正解... 正解は「{qs['correct']}」です。")
                    update_score(qs["word"], False)

    elif qs["type"] == "fill":
        answer = st.text_input("回答", key="fill_answer", disabled=qs["answered"])
        if st.button("回答する", disabled=qs["answered"]):
            qs["answered"] = True
            if answer.strip().lower() == qs["correct"]:
                st.success("正解！")
                update_score(qs["word"], True)
            else:
                st.error(f"不正解... 正解は「{qs['correct']}」です。")
                update_score(qs["word"], False)
