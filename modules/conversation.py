"""AI英会話練習ページ"""

import streamlit as st
from modules.ai_helper import ask_claude_conversation


SCENARIOS = {
    "自由会話": "Have a free conversation with the student on any topic they choose.",
    "自己紹介": "Practice self-introductions. Ask the student about their name, hobbies, job, etc.",
    "レストランで注文": "Role-play as a waiter at a restaurant. Help the student practice ordering food.",
    "ホテルのチェックイン": "Role-play as a hotel receptionist. Practice check-in procedures.",
    "道案内": "Role-play as someone asking for directions, or giving directions to the student.",
    "ショッピング": "Role-play as a shop clerk. Help the student practice buying things.",
    "仕事の面接": "Role-play as a job interviewer. Ask common interview questions.",
    "電話対応": "Role-play a phone conversation. Practice professional phone etiquette.",
    "病院・体調不良": "Role-play as a doctor. Help the student describe symptoms and understand advice.",
    "空港・飛行機": "Role-play airport and airplane scenarios (check-in, immigration, etc.).",
}

LEVELS = {
    "初級": "Use simple vocabulary and short sentences. Speak slowly and clearly. "
            "If the student makes mistakes, gently correct them.",
    "中級": "Use natural English with moderate vocabulary. "
            "Occasionally introduce new expressions and explain them.",
    "上級": "Use natural, fluent English with idioms and advanced vocabulary. "
            "Challenge the student with complex topics.",
}


def render():
    st.header("AI英会話練習")

    col1, col2 = st.columns(2)
    with col1:
        scenario = st.selectbox("シナリオ", list(SCENARIOS.keys()))
    with col2:
        level = st.selectbox("レベル", list(LEVELS.keys()))

    # チャット履歴の初期化
    if "conv_messages" not in st.session_state:
        st.session_state.conv_messages = []
    if "conv_scenario" not in st.session_state:
        st.session_state.conv_scenario = None

    # シナリオ変更時にリセット
    current_key = f"{scenario}_{level}"
    if st.session_state.conv_scenario != current_key:
        if st.session_state.conv_messages:
            if st.button("新しいシナリオで開始"):
                st.session_state.conv_messages = []
                st.session_state.conv_scenario = current_key
                st.rerun()
        else:
            st.session_state.conv_scenario = current_key

    col_start, col_clear = st.columns(2)
    with col_start:
        if not st.session_state.conv_messages:
            if st.button("会話を始める", use_container_width=True, type="primary"):
                _start_conversation(scenario, level)
    with col_clear:
        if st.session_state.conv_messages:
            if st.button("会話をリセット", use_container_width=True):
                st.session_state.conv_messages = []
                st.session_state.conv_scenario = None
                st.rerun()

    # チャット表示
    for msg in st.session_state.conv_messages:
        role = msg["role"]
        if role == "assistant":
            with st.chat_message("assistant", avatar="🧑‍🏫"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(msg["content"])

    # 入力
    if st.session_state.conv_messages:
        user_input = st.chat_input("英語で返答してください...")
        if user_input:
            st.session_state.conv_messages.append({"role": "user", "content": user_input})

            system_prompt = _build_system_prompt(scenario, level)
            with st.spinner("..."):
                response = ask_claude_conversation(
                    system_prompt,
                    st.session_state.conv_messages,
                    max_tokens=500,
                )
            st.session_state.conv_messages.append({"role": "assistant", "content": response})
            st.rerun()

        # ヘルプボタン
        st.divider()
        col_hint, col_translate, col_correct = st.columns(3)
        with col_hint:
            if st.button("返答のヒントをもらう", use_container_width=True):
                hint = ask_claude_conversation(
                    "You help Japanese students respond in English conversations. "
                    "Give a brief hint in Japanese about what they could say next, "
                    "and suggest 2-3 useful phrases in English.",
                    st.session_state.conv_messages + [
                        {"role": "user", "content": "次に何を言えばいいかヒントをください。"}
                    ],
                    max_tokens=200,
                )
                st.info(hint)
        with col_translate:
            if st.session_state.conv_messages:
                last_assistant = [m for m in st.session_state.conv_messages if m["role"] == "assistant"]
                if last_assistant and st.button("最後の発言を翻訳", use_container_width=True):
                    from modules.ai_helper import ask_claude
                    translation = ask_claude(
                        "Translate the following English text to natural Japanese.",
                        last_assistant[-1]["content"],
                        max_tokens=200,
                    )
                    st.info(translation)
        with col_correct:
            if st.session_state.conv_messages:
                last_user = [m for m in st.session_state.conv_messages if m["role"] == "user"]
                if last_user and st.button("文法チェック", use_container_width=True):
                    from modules.ai_helper import ask_claude
                    correction = ask_claude(
                        "You are an English teacher. Check the following sentence for grammar errors. "
                        "If there are errors, explain them in Japanese and show the corrected version. "
                        "If correct, praise the student in Japanese.",
                        last_user[-1]["content"],
                        max_tokens=200,
                    )
                    st.info(correction)


def _build_system_prompt(scenario: str, level: str) -> str:
    return (
        "You are a friendly English conversation partner for Japanese students. "
        f"Scenario: {SCENARIOS[scenario]} "
        f"Level: {LEVELS[level]} "
        "Keep your responses concise (2-4 sentences). "
        "Stay in character for the scenario. "
        "If the student writes in Japanese, gently encourage them to try in English, "
        "but help them if they're stuck."
    )


def _start_conversation(scenario: str, level: str):
    system_prompt = _build_system_prompt(scenario, level)
    with st.spinner("会話を開始中..."):
        response = ask_claude_conversation(
            system_prompt,
            [{"role": "user", "content": "Let's start the conversation. Please begin."}],
            max_tokens=300,
        )
    st.session_state.conv_messages = [{"role": "assistant", "content": response}]
    st.session_state.conv_scenario = f"{scenario}_{level}"
    st.rerun()
