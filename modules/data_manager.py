"""単語帳データの管理モジュール（セッションベース）"""

import streamlit as st
from datetime import datetime


def _get_vocab() -> list[dict]:
    """セッションから単語リストを取得"""
    if "vocabulary" not in st.session_state:
        st.session_state.vocabulary = []
    return st.session_state.vocabulary


def load_vocabulary() -> list[dict]:
    """単語リストを読み込む"""
    return _get_vocab()


def save_vocabulary(words: list[dict]):
    """単語リストを保存する"""
    st.session_state.vocabulary = words


def add_word(english: str, japanese: str, example: str = "") -> bool:
    """単語を追加する。重複があればFalseを返す"""
    words = _get_vocab()
    if any(w["english"].lower() == english.lower() for w in words):
        return False
    words.append({
        "english": english.strip(),
        "japanese": japanese.strip(),
        "example": example.strip(),
        "added_at": datetime.now().isoformat(),
        "correct_count": 0,
        "wrong_count": 0,
    })
    st.session_state.vocabulary = words
    return True


def delete_word(english: str):
    """単語を削除する"""
    words = _get_vocab()
    words = [w for w in words if w["english"].lower() != english.lower()]
    st.session_state.vocabulary = words


def update_score(english: str, correct: bool):
    """正解/不正解を記録する"""
    words = _get_vocab()
    for w in words:
        if w["english"].lower() == english.lower():
            if correct:
                w["correct_count"] += 1
            else:
                w["wrong_count"] += 1
            break
    st.session_state.vocabulary = words
