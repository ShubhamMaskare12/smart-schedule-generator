"""
StudyPilot — Main Entry Point
Premium AI-powered study scheduler SaaS
"""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

from database.models import init_db
from assets.styles.theme import inject_css, kpi

# ── Page config (must be first Streamlit call) ──
st.set_page_config(
    page_title="StudyPilot — AI Study Scheduler",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init DB ──
init_db()

# ── CSS ──
inject_css()

# ── Session state defaults ──
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "timetable_grids" not in st.session_state:
    st.session_state.timetable_grids = []
if "timetable_config" not in st.session_state:
    st.session_state.timetable_config = {}

# ── Sidebar ──
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🎓 StudyPilot</div>', unsafe_allow_html=True)

    if st.session_state.user:
        uname = st.session_state.user.get("username", "User")
        st.markdown(f'<p style="color:#9090B0;font-size:0.85rem">👋 Hello, <b style="color:#A09AFF">{uname}</b></p>', unsafe_allow_html=True)
        st.markdown("---")

    nav_items = [
        ("🏠", "Home",       "home"),
        ("⚡", "Generator",  "generator"),
        ("📅", "Timetable",  "timetable"),
        ("📊", "Dashboard",  "dashboard"),
        ("⏱️", "Focus Mode", "focus"),
        ("⚙️", "Settings",   "settings"),
    ]

    for icon, label, key in nav_items:
        active = st.session_state.page == key
        style = "color:#A09AFF;font-weight:700" if active else "color:#7070A0"
        if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")
    if st.session_state.user:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()
    else:
        if st.button("🔑 Login / Sign Up", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()

    st.markdown('<p style="font-size:0.7rem;color:#3A3A5A;margin-top:2rem">StudyPilot v1.0 · Built with ❤️</p>', unsafe_allow_html=True)


# ── Route pages ──
page = st.session_state.page

if page == "home":
    # ── Landing Page ──
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem 2rem">
        <div class="hero-title">Study Smarter.<br>Score Higher.</div>
        <p class="hero-sub" style="margin:1rem auto">
            StudyPilot generates AI-powered weekly timetables that balance your college schedule,
            competitive exam prep, and personal life — automatically.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature badges
    badges = ["📘 College Sync", "🏆 Exam Prep", "📊 Analytics", "⏱️ Pomodoro", "📁 Export PDF/Excel", "🔥 Streak Tracker"]
    st.markdown(
        '<div style="text-align:center;margin-bottom:2rem">' +
        "".join(f'<span class="feature-badge">{b}</span>' for b in badges) +
        "</div>",
        unsafe_allow_html=True
    )

    # CTA
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Generate My Timetable — Free", use_container_width=True, type="primary"):
            st.session_state.page = "generator"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # How it works
    st.markdown('<h2 style="text-align:center;font-family:Syne,sans-serif;margin-bottom:1.5rem">How It Works</h2>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("01", "📝 Tell Us About You", "Your subjects, goals, sleep schedule, and college timings."),
        ("02", "🧠 AI Schedules It",   "Our engine builds a conflict-free timetable in seconds."),
        ("03", "📅 View & Adjust",     "See your week at a glance, daily or weekly view."),
        ("04", "📤 Export Anywhere",   "Download as Excel, CSV, or share the link."),
    ]
    for col, (num, title, desc) in zip([c1,c2,c3,c4], steps):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center">
                <div style="font-family:'Syne',sans-serif;font-size:2rem;color:rgba(108,99,255,0.5);margin-bottom:0.5rem">{num}</div>
                <div style="font-weight:600;color:#E8E8F0;margin-bottom:0.4rem">{title}</div>
                <div style="font-size:0.82rem;color:#7070A0">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Stats
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center;font-family:Syne,sans-serif;margin-bottom:1.5rem">Why StudyPilot?</h2>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, (val, label) in zip([s1,s2,s3,s4], [
        ("10K+", "Timetables Generated"),
        ("94%",  "Users Hit Study Goals"),
        ("3×",   "Productivity Boost"),
        ("0",    "Conflicts Scheduled"),
    ]):
        with col:
            st.markdown(kpi(val, label), unsafe_allow_html=True)

elif page == "auth":
    from pages.auth_page import render_auth
    render_auth()

elif page == "generator":
    from pages.generator_page import render_generator
    render_generator()

elif page == "timetable":
    from pages.timetable_page import render_timetable
    render_timetable()

elif page == "dashboard":
    from pages.dashboard_page import render_dashboard
    render_dashboard()

elif page == "focus":
    from pages.focus_page import render_focus
    render_focus()

elif page == "settings":
    from pages.settings_page import render_settings
    render_settings()
