import streamlit as st
import requests
import os
import sys
from datetime import datetime
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.logger import get_recent_logs

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
icon_path = os.path.join(root_dir, "screenshots", "E-Icon.png")

try:
    icon_image = Image.open(icon_path)
except Exception:
    icon_image = "🧠"

API_URL = "http://ai_os_api:8000"

st.set_page_config(
    page_title="Engram OS",
    page_icon=icon_image,
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@500&display=swap');
    
    .stApp { background-color: #F8F9FA; } /* Lighter background */
    #MainMenu, header, footer {visibility: hidden;}
    
    /* Central Title and Subtitle */
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        color: #212529;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.2rem;
        color: #6C757D;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Input Field Styling */
    .stTextInput > div > div > input {
        border: 1px solid #CED4DA;
        border-radius: 50px; /* More rounded */
        padding: 16px 24px;
        font-size: 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stTextInput > div > div > input:focus {
        border-color: #ADB5BD;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 50px;
        padding: 12px 24px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Specific styling for the primary 'Chat' button */
    button[kind="primary"] {
        background-color: #E65C5C !important; /* Red color from image */
        color: white !important;
    }
    button[kind="secondary"] {
        background-color: white !important;
        color: #212529 !important;
        border: 1px solid #CED4DA !important;
    }
    
    /* Log Item Styling */
    .log-item { padding: 10px 0; border-bottom: 1px solid #E9ECEF; font-size: 13px; }
    .log-time { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ADB5BD; margin-bottom: 2px; }
    
    /* Badge Styling */
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; display: inline-block; margin-right: 6px; }
    .badge-green { background: #D1E7DD; color: #0F5132; }
    .badge-blue { background: #CFE2FF; color: #084298; }
    .badge-red { background: #F8D7DA; color: #842029; }
    .badge-gray { background: #E9ECEF; color: #495057; }
</style>
""", unsafe_allow_html=True)

spacer_left, center_col, spacer_right = st.columns([1, 2, 1])

with center_col:
    st.markdown('<h1 class="hero-title">Engram OS</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Your Second Brain. Online.</p>', unsafe_allow_html=True)
    
    user_input = st.text_input("Input", placeholder="What is on your mind?", label_visibility="collapsed")
    st.markdown("###")

    b_spacer_l, b1, b2, b_spacer_r = st.columns([1, 2, 2, 1])
    with b1:
        save_btn = st.button("📥 Save Memory", use_container_width=True, type="secondary")
    with b2:
        chat_btn = st.button("✨ Chat with OS", type="primary", use_container_width=True)

    if save_btn and user_input:
        try:
            requests.post(f"{API_URL}/ingest", json={"text": user_input})
            st.toast("Memory saved successfully!", icon="✅")
        except:
            st.error("Could not connect to Brain.")

    if chat_btn and user_input:
        with st.spinner("Processing..."):
            try:
                res = requests.post(f"{API_URL}/chat", json={"text": user_input})
                if res.status_code == 200:
                    data = res.json()
                    st.markdown(f"""
                    <div style="background: white; padding: 20px; border-radius: 15px; margin-top: 20px; border: 1px solid #E9ECEF; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <b>Engram:</b> {data['reply']}
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("View Context"):
                        st.json(data['context_used'])
            except:
                st.error("Brain is offline.")

    st.markdown("---") 

    with st.expander("🔧 System Controls"):
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("Trigger Calendar Agent", use_container_width=True, type="secondary"):
                requests.post(f"{API_URL}/run-agents/calendar")
                st.toast("Calendar Agent Started")
        with c_b:
            if st.button("Trigger Email Agent", use_container_width=True, type="secondary"):
                requests.post(f"{API_URL}/run-agents/email")
                st.toast("Email Agent Started")

st.markdown("###") 
f_spacer_left, f_center_col, f_spacer_right = st.columns([1, 2, 1])

with f_center_col:
    f_head, f_btn = st.columns([3, 1])
    with f_head:
        st.subheader("Live Neural Activity")
    with f_btn:
        if st.button("Refresh Feed", key="refresh", type="secondary"):
            st.rerun()

    with st.container(height=400):
        logs = get_recent_logs(20)
        if not logs:
            st.info("System is quiet. No recent neural activity.")
        
        for timestamp, agent, action, details in logs:
            badge_class = "badge-gray"
            if action == "TOOL_USE": badge_class = "badge-green"
            elif action == "ERROR": badge_class = "badge-red"
            elif action == "WAKE_UP": badge_class = "badge-blue"
            
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                nice_time = dt.strftime("%H:%M")
            except:
                nice_time = timestamp

            st.markdown(f"""
            <div class="log-item">
                <div class="log-time">{nice_time} • {agent}</div>
                <div><span class="badge {badge_class}">{action}</span> <span style="color: #212529;">{details}</span></div>
            </div>
            """, unsafe_allow_html=True)