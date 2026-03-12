"""Gemini API を使った共通ヘルパー"""

import json
import re
import streamlit as st
import google.generativeai as genai
def _configure_client():
    """Gemini クライアントを設定"""
    api_key = st.session_state.get("api_key", "") or st.secrets.get("GEMINI_API_KEY", "")
    if not api_key or api_key == "your-api-key-here":
        st.error("APIキーが設定されていません。管理者に連絡してください。")
        st.stop()
    genai.configure(api_key=api_key)


def _extract_json(text: str) -> str:
    """応答テキストからJSON部分を抽出する"""
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", text)
    cleaned = re.sub(r"\n?```", "", cleaned)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return match.group(0)
    return cleaned.strip()


def _call_gemini(system_prompt: str, user_message: str, max_tokens: int = 8192) -> str:
    """Gemini API を呼び出して生テキストを返す"""
    _configure_client()
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt,
        )
        response = model.generate_content(
            user_message,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens),
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "401" in error_msg:
            st.error("APIキーが無効です。正しいキーをサイドバーから入力し直してください。")
        else:
            st.error(f"API エラーが発生しました: {error_msg}")
        st.stop()


def ask_claude(system_prompt: str, user_message: str, max_tokens: int = 8192) -> str:
    """Gemini にメッセージを送って応答を得る（テキスト返却）"""
    text = _call_gemini(system_prompt, user_message, max_tokens)
    if "{" in text:
        return _extract_json(text)
    return text.strip()


def ask_claude_json(system_prompt: str, user_message: str, max_tokens: int = 8192) -> dict | None:
    """Gemini にJSON応答を要求して辞書を返す"""
    enhanced_prompt = system_prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanation, no code blocks."
    text = _call_gemini(enhanced_prompt, user_message, max_tokens)
    json_str = _extract_json(text)
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        st.error(f"JSONパースに失敗しました。AI応答:\n```\n{text[:500]}\n```")
        return None


def ask_claude_conversation(system_prompt: str, messages: list[dict], max_tokens: int = 8192) -> str:
    """会話履歴付きでGemini にメッセージを送る"""
    _configure_client()
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt,
        )
        gemini_history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=gemini_history)
        last_message = messages[-1]["content"] if messages else ""
        response = chat.send_message(
            last_message,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_tokens),
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "401" in error_msg:
            st.error("APIキーが無効です。正しいキーをサイドバーから入力し直してください。")
        else:
            st.error(f"API エラーが発生しました: {error_msg}")
        st.stop()
