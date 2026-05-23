"""
StudyPilot — Settings Page
"""

import streamlit as st
from assets.styles.theme import inject_css


def render_settings():
    inject_css()

    st.markdown('<h1 style="font-family:Syne,sans-serif">⚙️ Settings</h1>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎨 Appearance", "📋 Profile", "📤 Data"])

    with tab1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Theme & Appearance")
        accent = st.color_picker("Accent Color", value="#6C63FF")
        time_fmt = st.radio("Time Format", ["24h", "12h"], horizontal=True)
        if st.button("Save Preferences", type="primary"):
            if st.session_state.user:
                from database.models import save_prefs
                save_prefs(st.session_state.user["id"], "dark", accent, time_fmt)
                st.success("Preferences saved!")
            else:
                st.info("Login to save preferences.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        if st.session_state.user:
            u = st.session_state.user
            st.markdown(f"**Username:** {u.get('username','—')}")
            st.markdown(f"**Email:** {u.get('email','—')}")
            st.markdown(f"**Member since:** {u.get('created_at','—')[:10] if u.get('created_at') else '—'}")
        else:
            st.markdown('<div class="warn-banner">Login to view your profile.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Export Your Data")
        grids = st.session_state.get("timetable_grids", [])
        if grids:
            from backend.exports.export_engine import export_to_excel
            excel_bytes = export_to_excel(grids)
            st.download_button("📥 Download All Timetables (Excel)", data=excel_bytes,
                               file_name="StudyPilot_All_Timetables.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("No timetable generated yet.")

        st.markdown("---")
        st.markdown("#### Danger Zone")
        if st.button("🗑️ Clear Current Timetable", type="secondary"):
            st.session_state.timetable_grids = []
            st.session_state.timetable_config = {}
            st.session_state.timetable_analytics = {}
            st.success("Timetable cleared.")
        st.markdown('</div>', unsafe_allow_html=True)
