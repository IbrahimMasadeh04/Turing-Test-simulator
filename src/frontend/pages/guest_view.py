import streamlit as st
import time
import requests


st.set_page_config(page_title="Live Stream", page_icon="👁️", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stToast"] {
        background-color: #f0f4f8 !important;
        border: 1px solid #d0d8e0 !important;
    }
    [data-testid="stToast"] div {
        color: #1a1a1a !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("البث المباشر لاختبار تورنغ 🔴")
st.caption("راقب المحادثة وحاول أن تحزر: من هو الإنسان ومن هي الآلة؟")

st.divider()


def format_remaining_time(remaining_seconds: int) -> str:
    remaining_seconds = int(remaining_seconds)
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

try:
    resp = requests.get("http://127.0.0.1:8000/api/chat/history")
    current_messages = resp.json()
except Exception as e:
    current_messages = []
    st.error("السيرفر لا يعمل حاليا")

try:
    round_state_response = requests.get("http://127.0.0.1:8000/api/chat/round/state")
    round_state = round_state_response.json()
except Exception as e:
    round_state = {
        "remaining_seconds": 300,
    }

try:
    verdict_resp = requests.get("http://127.0.0.1:8000/api/chat/verdict/selection")
    judge_selection = verdict_resp.json().get("selection")
except Exception as e:
    judge_selection = None

st.metric("الوقت المتبقي", format_remaining_time(round_state["remaining_seconds"]))

if "last_seen_selection" not in st.session_state:
    st.session_state.last_seen_selection = None

if judge_selection and judge_selection != st.session_state.last_seen_selection:
    st.toast(f"👀 المُحكّم يفكّر حالياً باختيار: **{judge_selection}**", icon="🔔")
    st.session_state.last_seen_selection = judge_selection

def get_pending_participants(messages: list[dict]) -> list[str]:
    last_judge_index = -1

    for index, message in enumerate(messages):
        if message.get("role") == "judge":
            last_judge_index = index

    if last_judge_index == -1:
        return []

    pending_senders = []
    recent_messages = messages[last_judge_index + 1 :]

    for sender in ("الطرف (أ)", "الطرف (ب)"):
        has_reply = any(message.get("sender") == sender for message in recent_messages)
        if not has_reply:
            pending_senders.append(sender)

    return pending_senders

if not current_messages:
    st.info("ننتظر بدء المُحكّم بطرح السؤال الأول...")
else:
    
    for msg in current_messages:
        if msg["role"] == "judge":
            with st.chat_message("human", avatar="⚖️"):
                st.markdown(f"**المُحكّم:** {msg['content']}")
        else:
            avatar = "🅰️" if msg["sender"] == "الطرف (أ)" else "🅱️"
            
            with st.chat_message("ai", avatar=avatar):
                st.markdown(f"**{msg['sender']}:** {msg['content']}")

    pending_participants = get_pending_participants(current_messages)
    if pending_participants:
        pending_label = " و ".join(pending_participants)
        with st.chat_message("ai", avatar="⌨️"):
            st.markdown(f"**{pending_label} يكتبـ/ـان الآن...**")

time.sleep(3)
st.rerun()