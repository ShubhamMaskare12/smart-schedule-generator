"""
StudyPilot — Timetable View Page
Renders weekly/daily timetable views with export options.
"""

import streamlit as st
import pandas as pd

from assets.styles.theme import inject_css
from components.timetable_view import render_timetable_html, render_daily_view, subject_legend_html
from backend.scheduler.engine import WEEK, HOURS, get_subject_color_map
from backend.exports.export_engine import export_to_excel, export_to_csv


def render_timetable():
    inject_css()

    st.markdown('<h1 style="font-family:Syne,sans-serif">📅 Your Timetable</h1>', unsafe_allow_html=True)

    grids = st.session_state.get("timetable_grids", [])

    if not grids:
        st.markdown('<div class="warn-banner">⚠️ No timetable generated yet. Head to the <b>Generator</b> to create one.</div>', unsafe_allow_html=True)
        if st.button("⚡ Go to Generator", type="primary"):
            st.session_state.page = "generator"
            st.rerun()
        return

    n_weeks = len(grids)

    # Controls row
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        selected_week = st.selectbox("Select Week", [f"Week {i+1}" for i in range(n_weeks)]) or "Week 1"
        week_idx = int(selected_week.split()[1]) - 1
    with col2:
        view_mode = st.radio("View", ["Weekly", "Daily"], horizontal=True)
    with col3:
        pass  # export buttons below

    grid = grids[week_idx]

    # Export buttons
    ex_col1, ex_col2, ex_col3, _ = st.columns([1, 1, 1, 3])
    with ex_col1:
        excel_bytes = export_to_excel(grids, name="StudyPilot_Timetable")
        st.download_button(
            "📥 Excel (All Weeks)",
            data=excel_bytes,
            file_name="StudyPilot_Timetable.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with ex_col2:
        csv_bytes = export_to_csv(grid)
        st.download_button(
            "📄 CSV (This Week)",
            data=csv_bytes,
            file_name=f"Week{week_idx+1}_Timetable.csv",
            mime="text/csv",
            use_container_width=True
        )
    with ex_col3:
        if st.button("🖨️ Print View", use_container_width=True):
            st.info("Tip: Use Ctrl+P / Cmd+P to print this page.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Subject legend
    all_subjects = set()
    for day, slots in grid.items():
        for label in slots.values():
            if " " in label:
                subj = label.split(" ", 1)[1].split("—")[0].split("(")[0].strip()
                if subj and not subj.startswith("Sleep") and not subj.startswith("Meal") and not subj.startswith("Free"):
                    all_subjects.add(subj)
    color_map = get_subject_color_map(list(all_subjects))
    if all_subjects:
        st.markdown("**Subject Legend:**")
        st.markdown(subject_legend_html(sorted(all_subjects), color_map), unsafe_allow_html=True)

    # Render chosen view
    if view_mode == "Weekly":
        show_hrs = list(range(5, 23))  # 5am - 11pm compact
        html = render_timetable_html(grid, show_hours=show_hrs)
        st.markdown(html, unsafe_allow_html=True)

    else:  # Daily
        day_choice = st.selectbox("Select Day", WEEK)
        html = render_daily_view(grid, day_choice)
        st.markdown(html, unsafe_allow_html=True)

    # Multi-week summary cards
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3 style="font-family:Syne,sans-serif">All Weeks Overview</h3>', unsafe_allow_html=True)

    week_cols = st.columns(min(n_weeks, 4))
    for i, (g, wc) in enumerate(zip(grids[:4], week_cols)):
        study_count = sum(
            1 for day in g.values()
            for label in day.values()
            if any(label.startswith(e) for e in ["📘", "🏆", "🔁"])
        )
        with wc:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{study_count}h</div>
                <div class="kpi-label">Week {i+1} Study</div>
            </div>
            """, unsafe_allow_html=True)
