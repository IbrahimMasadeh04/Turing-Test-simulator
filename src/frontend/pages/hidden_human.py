import streamlit as st
import requests
import time

# إعدادات الصفحة
st.set_page_config(page_title="Human Room", page_icon="👤", layout="centered")

# حماية الصفحة
if st.session_state.get("role") != "human":
    st.warning("غير مصرح لك بالدخول. الرجاء تسجيل الدخول من الصفحة الرئيسية.")
    st.stop()

st.title("غرفة الإنسان السري 👤")
st.caption("أنت الطرف (أ). أثبت للمُحكّم أنك الإنسان الحقيقي!")

API_URL = "http://127.0.0.1:8000/api/chat"


def format_remaining_time(remaining_seconds: int) -> str:
    remaining_seconds = int(remaining_seconds)
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

# 1. جلب المحادثة عشان الصديق يشوف شو المُحكّم سأل
try:
    response = requests.get(f"{API_URL}/history")
    current_messages = response.json()
except requests.exceptions.ConnectionError:
    current_messages = []
    st.error("سيرفر FastAPI لا يعمل!")
    st.stop()

try:
    round_state_response = requests.get(f"{API_URL}/round/state")
    round_state = round_state_response.json()
except requests.exceptions.ConnectionError:
    st.error("سيرفر FastAPI لا يعمل!")
    st.stop()

st.metric("الوقت المتبقي", format_remaining_time(round_state["remaining_seconds"]))

# 2. عرض الرسائل
for msg in current_messages:
    if msg["role"] == "judge":
        with st.chat_message("human", avatar="⚖️"):
            st.markdown(f"**المُحكّم:** {msg['content']}")
    else:
        avatar = "🅰️" if msg["sender"] == "الطرف (أ)" else "🅱️"
        with st.chat_message("ai", avatar=avatar):
            st.markdown(f"**{msg['sender']}:** {msg['content']}")

# 3. حقل الإدخال لرد الصديق الخفي
if prompt := st.chat_input("اكتب ردك العفوي هنا..."):
    # تجهيز الرسالة كـ "الطرف (أ)"
    payload = {
        "role": "participant",
        "sender": "الطرف (أ)",
        "content": prompt
    }
    
    # إرسال الرد للـ API المخصص للإنسان
    try:
        requests.post(f"{API_URL}/human_reply", json=payload)
        st.rerun() 
    except Exception as e:
        st.error("حدث خطأ أثناء إرسال الرد.")

# 4. تحديث الصفحة تلقائياً لجلب الأسئلة الجديدة
time.sleep(1)
st.rerun()