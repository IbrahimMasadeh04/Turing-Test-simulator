import streamlit as st

st.set_page_config(page_title="Turing Test Simulator", page_icon="🤖", layout="centered")

st.title("اختبار تورنغ - من هو الإنسان؟ 🤖👤")
st.write("أهلاً بك في محاكاة اختبار تورنغ المباشرة.")

if "role" not in st.session_state:
    st.session_state.role = None

st.divider()

st.subheader("دخول المُحكّم ⚖️")

judge_code = st.text_input("أدخل كود الدخول الخاص بك:", type="password")

if st.button("دخول كمُحكّم", type="primary"):

    if judge_code == "shoman2026": 
        st.session_state.role = "judge"
        st.success("تم التحقق! جاري توجيهك لغرفة التحكم...")
        
        st.switch_page("pages/judge_chat.py")
    elif judge_code == "":
        st.warning("الرجاء إدخال الكود أولاً.")
    else:
        st.error("الكود غير صحيح، حاول مرة أخرى.")

st.divider()

st.subheader("دخول الزوار 👁️")
st.write("ادخل كزائر لمشاهدة المحادثة المباشرة بين المُحكّم والأطراف المخفية على الشاشة الكبيرة.")


if st.button("متابعة كزائر", type="secondary"):
    st.session_state.role = "guest"
    st.switch_page("pages/guest_view.py")

st.subheader("دخول الشخص للرد على المحكم 👤")
human_code = st.text_input("أدخل كود الصديق:", type="password", key="human_pass")

if st.button("دخول كإنسان حقيقي", type="primary", key="human_btn"):
    if human_code == "human2026": 
        st.session_state.role = "human"
        st.success("تم التحقق! جاري توجيهك لغرفة التخفي...")
        st.switch_page("pages/hidden_human.py")
    elif human_code == "":
        st.warning("الرجاء إدخال الكود أولاً.")
    else:
        st.error("الكود غير صحيح.")