import time

import requests
import streamlit as st

st.set_page_config(page_title="Judge Room", page_icon="⚖️", layout="centered")

if st.session_state.get("role") != "judge":
    st.warning("غير مصرح لك بالدخول. الرجاء تسجيل الدخول من الصفحة الرئيسية.")
    st.stop()


@st.dialog("تحديد جنس المُحكّم")
def choose_judge_gender() -> None:
    
    st.write("قبل ما تتابع، حدّد إذا كنتَ ذكرًا أو أنثى.")

    gender = st.radio(
        "جنس المُحكّم",
        options=["ذكر", "أنثى"],
        horizontal=True,
        key="judge_gender_choice",
    )

    if st.button("تأكيد", type="primary"):
        st.session_state.judge_gender = gender
        st.rerun()


if not st.session_state.get("judge_gender"):
    choose_judge_gender()
    st.stop()

st.title("غرفة المُحكّم ⚖️")
st.caption("أنت الآن تدير اختبار تورنغ. اطرح أسئلتك بذكاء لكشف الآلة!")

API_URL = "http://127.0.0.1:8000/api/chat"


def format_remaining_time(remaining_seconds: int) -> str:
    remaining_seconds = int(remaining_seconds)
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

try:
    requests.post(f"{API_URL}/round/start")
except requests.exceptions.ConnectionError:
    st.error("السيرفر لا يعمل حاليا. تأكد من تشغيل FastAPI قبل المتابعة.")
    st.stop()

try: 
    resp = requests.get(f"{API_URL}/history")
    current_messages = resp.json()
except requests.exceptions.ConnectionError:
    st.error("السيرفر لا يعمل حاليا. تأكد من تشغيل FastAPI قبل المتابعة.")
    st.stop()

try:
    round_state_response = requests.get(f"{API_URL}/round/state")
    round_state = round_state_response.json()
except requests.exceptions.ConnectionError:
    st.error("السيرفر لا يعمل حاليا. تأكد من تشغيل FastAPI قبل المتابعة.")
    st.stop()

st.metric("الوقت المتبقي", format_remaining_time(round_state["remaining_seconds"]))

if round_state["expired"]:
    st.info("انتهى الوقت. سيتم تحويلك الآن إلى صفحة التوقع النهائي.")
    st.switch_page("pages/judge_verdict.py")
    st.stop()


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


for msg in current_messages :
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

if prompt := st.chat_input("اكتب سؤالك هنا..."):
    
    payload = {
        "role": "judge",
        "sender": "المُحكّم",
        "content": prompt,
        "judge_gender": st.session_state.get("judge_gender")
    }

    with st.chat_message("human", avatar="⚖️"):
        st.markdown(f"**المُحكّم:** {prompt}")
    
    try:
        requests.post(f"{API_URL}/judge_ask", json=payload)
        st.rerun() 
    except Exception as e:
        st.error("حدث خطأ أثناء إرسال السؤال. تأكد من تشغيل السيرفر وحاول مرة أخرى.")

time.sleep(1)
st.rerun()
