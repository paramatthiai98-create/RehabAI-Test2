import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="RehabAI", layout="wide")

# ---------- session state ----------
defaults = {
    "running": False,
    "correct_count": 0,
    "incorrect_count": 0,
    "scores": [],
    "angles": [],
    "rep_stage": "down",
    "locked_angle": 70,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------- logic ----------
def get_risk_and_recommendation(angle_value):
    if angle_value < 55:
        return "Incorrect ❌", 45, "HIGH 🔴", "Raise your arm higher / reduce compensation"
    elif angle_value < 75:
        return "Almost Correct ⚠️", 70, "MEDIUM 🟠", "Try to improve range of motion"
    else:
        return "Correct ✅", 92, "LOW 🟢", "Good posture and movement"

def count_rep(angle_value):
    if angle_value < 55:
        st.session_state.rep_stage = "down"
    if angle_value > 75 and st.session_state.rep_stage == "down":
        st.session_state.rep_stage = "up"
        return True
    return False

# ---------- sidebar ----------
st.title("🏥 RehabAI – Real-time Recovery Intelligence System")
st.caption("AI ที่ช่วยให้การฟื้นฟูร่างกายเร็วขึ้น ปลอดภัยขึ้น และถูกต้องขึ้น แบบ real-time")

st.sidebar.header("👤 Patient Profile")
patient_name = st.sidebar.text_input("Name", "John Doe")
age = st.sidebar.slider("Age", 20, 80, 45)
condition = st.sidebar.selectbox("Condition", ["Shoulder Rehab", "Knee Rehab", "Elbow Rehab"])
session_goal = st.sidebar.slider("Target Reps", 5, 30, 10)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛 Demo Control")
angle_input = st.sidebar.slider("Simulated Angle", 30, 120, 70)

c1, c2 = st.sidebar.columns(2)
with c1:
    if st.button("▶ Start Session", use_container_width=True):
        st.session_state.running = True
        st.session_state.locked_angle = angle_input

with c2:
    if st.button("⏹ Stop Session", use_container_width=True):
        st.session_state.running = False

if st.sidebar.button("🔄 Reset Session", use_container_width=True):
    st.session_state.running = False
    st.session_state.correct_count = 0
    st.session_state.incorrect_count = 0
    st.session_state.scores = []
    st.session_state.angles = []
    st.session_state.rep_stage = "down"
    st.session_state.locked_angle = 70

# ---------- main layout ----------
left, center, right = st.columns([1.1, 2.2, 1.2])

with left:
    st.subheader("👤 Patient Info")
    st.write(f"**Name:** {patient_name}")
    st.write(f"**Age:** {age}")
    st.write(f"**Condition:** {condition}")

    total_reps = st.session_state.correct_count + st.session_state.incorrect_count
    progress = min(total_reps / session_goal, 1.0) if session_goal > 0 else 0
    st.progress(progress)

    st.subheader("📊 Session Summary")
    st.metric("Correct Reps", st.session_state.correct_count)
    st.metric("Incorrect Reps", st.session_state.incorrect_count)

    avg_score = int(np.mean(st.session_state.scores)) if len(st.session_state.scores) > 0 else 0
    max_angle = int(np.max(st.session_state.angles)) if len(st.session_state.angles) > 0 else 0

    st.metric("Average Score", avg_score)
    st.metric("Max Angle", f"{max_angle}°")

with center:
    st.subheader("📹 Live Monitoring")
    frame_placeholder = st.empty()
    chart_placeholder = st.empty()

with right:
    st.subheader("🧠 Live Clinical Metrics")
    status_box = st.empty()
    score_box = st.empty()
    risk_box = st.empty()
    angle_box = st.empty()
    rec_box = st.empty()

# ---------- display ----------
current_angle = st.session_state.locked_angle if st.session_state.running else angle_input
status, score, risk, recommendation = get_risk_and_recommendation(current_angle)

if st.session_state.running:
    rep_done = count_rep(current_angle)
    if rep_done:
        if "Correct" in status:
            st.session_state.correct_count += 1
        else:
            st.session_state.incorrect_count += 1

    if len(st.session_state.scores) < 200:
        st.session_state.scores.append(score)
    if len(st.session_state.angles) < 200:
        st.session_state.angles.append(current_angle)

frame_placeholder.markdown(
    f"""
    <div style="
        height:420px;
        border-radius:18px;
        background:#111827;
        color:white;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        text-align:center;">
        <h2>RehabAI Demo Mode</h2>
        <h1>{current_angle}°</h1>
        <p>Simulated Joint Angle</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if len(st.session_state.scores) > 0:
    df = pd.DataFrame({"Recovery Score": st.session_state.scores[-20:]})
    chart_placeholder.line_chart(df, height=220)
else:
    chart_placeholder.info("กราฟคะแนนจะแสดงเมื่อเริ่ม session")

status_box.metric("Posture Status", status if st.session_state.running else "Waiting")
score_box.metric("Recovery Score", score if st.session_state.running else 0)
risk_box.metric("Risk Level", risk if st.session_state.running else "-")
angle_box.metric("Joint Angle", f"{current_angle}°" if st.session_state.running else "0°")

if st.session_state.running:
    if "Correct" in status:
        rec_box.success(f"✅ {recommendation}")
    elif "Almost" in status:
        rec_box.warning(f"⚠️ {recommendation}")
    else:
        rec_box.error(f"🚨 {recommendation}")
else:
    rec_box.info("ระบบพร้อมใช้งาน กด Start Session เพื่อเริ่ม Demo")
