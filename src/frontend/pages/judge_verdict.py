import requests
import streamlit as st

st.set_page_config(page_title="Judge Verdict", page_icon="🎯", layout="centered")

if st.session_state.get("role") != "judge":
    st.warning("غير مصرح لك بالدخول. الرجاء تسجيل الدخول من الصفحة الرئيسية.")
    st.stop()

st.title("القرار النهائي 🎯")
st.caption("خلص الوقت. الآن حدّد مين بتتوقع يكون الذكاء الاصطناعي.")

try:
    round_state_response = requests.get("http://127.0.0.1:8000/api/chat/round/state")
    round_state = round_state_response.json()
except requests.exceptions.ConnectionError:
    st.error("السيرفر لا يعمل حاليا. تأكد من تشغيل FastAPI قبل المتابعة.")
    st.stop()

remaining_seconds = round_state.get("remaining_seconds", 0)
remaining_seconds = int(remaining_seconds)
minutes = remaining_seconds // 60
seconds = remaining_seconds % 60
st.metric("الوقت المتبقي", f"{minutes:02d}:{seconds:02d}")

st.write("مين بتتوقع يكون الذكاء الاصطناعي؟")

choice = st.radio(
    "اختيارك",
    options=["الطرف (أ)", "الطرف (ب)"],
    horizontal=True,
    key="judge_final_guess",
)

if st.button("إرسال التوقع", type="primary"):
    if choice == "الطرف (ب)":
        st.success("صح حكيك. شارك الناس سبب اختيارك ✨")
    else:
        st.error("اختيارك خطأ، الذكاء الاصطناعي كان الطرف (ب)، محاولة حلوة منك. شارك الناس سبب اختيارك للطرف (أ) 🤝")
