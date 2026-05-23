"""
StudyPilot — Auth Page (Login / Signup)
"""

import streamlit as st
from database.models import create_user, verify_user
from assets.styles.theme import inject_css


def render_auth():
    inject_css()

    st.markdown('<h1 style="font-family:Syne,sans-serif;text-align:center;margin-bottom:0.3rem">Welcome Back</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#7070A0;margin-bottom:2rem">Sign in to your StudyPilot account</p>', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        tab1, tab2 = st.tabs(["🔑 Login", "✨ Sign Up"])

        with tab1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            email    = st.text_input("Email", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")

            if st.button("Login →", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    user = verify_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = "home"
                        st.success(f"Welcome back, {user['username']}! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            uname = st.text_input("Username", key="su_uname", placeholder="coolstudent42")
            email2 = st.text_input("Email", key="su_email", placeholder="you@example.com")
            pw1   = st.text_input("Password", type="password", key="su_pw1", placeholder="Min 6 characters")
            pw2   = st.text_input("Confirm Password", type="password", key="su_pw2", placeholder="Repeat password")

            if st.button("Create Account →", use_container_width=True, type="primary"):
                if not all([uname, email2, pw1, pw2]):
                    st.error("Please fill in all fields.")
                elif pw1 != pw2:
                    st.error("Passwords don't match.")
                elif len(pw1) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    uid = create_user(uname, email2, pw1)
                    if uid:
                        user = {"id": uid, "username": uname, "email": email2}
                        st.session_state.user = user
                        st.session_state.page = "generator"
                        st.success("Account created! Let's build your timetable 🚀")
                        st.rerun()
                    else:
                        st.error("Email or username already exists.")
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="auth_back"):
        st.session_state.page = "home"
        st.rerun()
