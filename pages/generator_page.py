"""
StudyPilot — Timetable Generator Page
Multi-step wizard to collect inputs and run the scheduling engine.
"""

import streamlit as st
from assets.styles.theme import inject_css, step_wizard_html
from backend.scheduler.engine import (
    generate_multi_week, compute_analytics,
    extract_topics, WEEK
)

STEPS = ["Personal", "Academic", "Schedule", "Preferences", "Generate"]


def render_generator():
    inject_css()

    st.markdown('<h1 style="font-family:Syne,sans-serif">⚡ Timetable Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7070A0;margin-bottom:1.5rem">Build your personalised AI study schedule in 5 steps.</p>', unsafe_allow_html=True)

    # ── Wizard state ──
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 0
    if "wizard_data" not in st.session_state:
        st.session_state.wizard_data = {}

    step = st.session_state.wizard_step
    data = st.session_state.wizard_data

    # Progress bar
    st.progress((step) / (len(STEPS) - 1) if step < len(STEPS) - 1 else 1.0)
    st.markdown(step_wizard_html(STEPS, step), unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # STEP 0 — Personal
    # ──────────────────────────────────────────────────
    if step == 0:
        st.markdown("### 👤 Tell us about yourself")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            data["name"] = st.text_input("Your Name", value=data.get("name", ""), placeholder="Alex Kumar")
            data["exam_target"] = st.selectbox("Competitive Exam (if any)", [
                "None", "JEE", "NEET", "CAT", "UPSC", "GATE", "GRE", "GMAT", "Other"
            ], index=["None","JEE","NEET","CAT","UPSC","GATE","GRE","GMAT","Other"].index(data.get("exam_target","None")))
        with col2:
            data["semester"] = st.selectbox("Current Semester / Year", [
                "1st Year", "2nd Year", "3rd Year", "4th Year", "Postgraduate"
            ])
            data["stream"] = st.selectbox("Stream", [
                "Engineering", "Medical", "Commerce", "Arts", "Science", "Management", "Other"
            ])

        st.markdown('</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # STEP 1 — Academic
    # ──────────────────────────────────────────────────
    elif step == 1:
        st.markdown("### 📚 Your Subjects")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.markdown('<div class="info-banner">💡 Enter subjects separated by commas. Add difficulty level after each (Easy/Medium/Hard).</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**College Subjects**")
            college_subj_raw = st.text_area(
                "College subjects (one per line: Subject, difficulty)",
                value=data.get("college_subjects_raw", "Mathematics, Hard\nPhysics, Medium\nCS, Easy\nChemistry, Medium"),
                height=150
            )
            data["college_subjects_raw"] = college_subj_raw
            data["college_study_hours"]  = st.slider("Daily college study hours", 1, 8, data.get("college_study_hours", 3))

        with col2:
            if data.get("exam_target", "None") != "None":
                st.markdown(f"**{data['exam_target']} Subjects**")
                comp_subj_raw = st.text_area(
                    "Competitive subjects (one per line: Subject, difficulty)",
                    value=data.get("comp_subjects_raw", "Quantitative Aptitude, Hard\nVerbal Ability, Medium\nDILR, Hard"),
                    height=150
                )
                data["comp_subjects_raw"]      = comp_subj_raw
                data["competitive_study_hours"] = st.slider("Daily exam study hours", 1, 6, data.get("competitive_study_hours", 3))
            else:
                st.markdown("**Weak Subjects (for extra focus)**")
                data["weak_subjects"] = st.text_input("Weak subjects (comma-separated)", value=data.get("weak_subjects", ""))

        st.markdown('</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # STEP 2 — Schedule Constraints
    # ──────────────────────────────────────────────────
    elif step == 2:
        st.markdown("### 🗓️ Your Schedule Constraints")

        with st.expander("⏰ Sleep & Wake Times", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                data["wake_time"]           = st.text_input("Wake time (e.g. 06:00)", value=data.get("wake_time", "06:00"))
            with col2:
                data["sleep_hours_per_day"] = st.slider("Hours of sleep", 4, 10, data.get("sleep_hours_per_day", 7))
            with col3:
                data["max_daily_study_hours"] = st.slider("Max study hours/day", 2, 12, data.get("max_daily_study_hours", 6))

        with st.expander("🏫 College Class Timings", expanded=True):
            st.markdown('<div class="info-banner">Enter your fixed college hours for each day.</div>', unsafe_allow_html=True)
            college_hours: dict = data.get("college_hours", {})

            for day in WEEK:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    start = st.text_input(f"{day[:3]} start", value=college_hours.get(day, [{}])[0].get("start", ""), key=f"cs_{day}", placeholder="09:00")
                with col2:
                    end = st.text_input(f"{day[:3]} end", value=college_hours.get(day, [{}])[0].get("end", ""), key=f"ce_{day}", placeholder="17:00")
                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.checkbox("Off", key=f"coff_{day}"):
                        college_hours[day] = []
                        continue
                if start and end:
                    college_hours[day] = [{"start": start, "end": end}]

            data["college_hours"] = college_hours

        with st.expander("🚫 Blocked Slots (optional)"):
            blocked_raw = st.text_area(
                "Blocked times (format: Day, HH:MM-HH:MM per line)",
                value=data.get("blocked_raw", ""),
                placeholder="Sunday, 10:00-12:00\nSaturday, 14:00-16:00",
                height=100
            )
            data["blocked_raw"] = blocked_raw
            # parse to list
            blocked_slots = []
            for line in blocked_raw.strip().split("\n"):
                line = line.strip()
                if "," in line and "-" in line:
                    parts = line.split(",", 1)
                    day_p = parts[0].strip()
                    times = parts[1].strip().split("-")
                    if len(times) == 2:
                        blocked_slots.append({"day": day_p, "start": times[0].strip(), "end": times[1].strip()})
            data["blocked_slots"] = blocked_slots

        data["weekly_free_hours"] = st.slider("Weekly free / leisure hours", 2, 20, data.get("weekly_free_hours", 6))

    # ──────────────────────────────────────────────────
    # STEP 3 — Preferences
    # ──────────────────────────────────────────────────
    elif step == 3:
        st.markdown("### 🎨 Study Preferences")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            data["productivity_peak"] = st.selectbox("When are you most productive?", [
                "Early Morning (5-8 AM)", "Morning (8-11 AM)", "Afternoon (12-3 PM)",
                "Evening (4-7 PM)", "Night (8-11 PM)", "Late Night (11PM+)"
            ])
            data["study_style"] = st.selectbox("Study style", [
                "Deep Focus (long sessions)", "Spaced (short bursts)", "Mixed"
            ])
        with col2:
            data["break_freq"] = st.selectbox("Break frequency", [
                "Every 25 min (Pomodoro)", "Every 45 min", "Every 1 hour", "Every 2 hours"
            ])
            data["n_weeks"] = st.slider("Weeks to generate", 1, 12, data.get("n_weeks", 4))

        data["include_exercise"] = st.checkbox("Include exercise/morning routine slot", value=data.get("include_exercise", True))
        data["revision_sessions"] = st.checkbox("Include weekly revision sessions", value=data.get("revision_sessions", True))

        st.markdown('</div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # STEP 4 — Generate
    # ──────────────────────────────────────────────────
    elif step == 4:
        st.markdown("### 🚀 Review & Generate")

        # Summary
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**Your Configuration Summary**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Name:** {data.get('name','—')}")
            st.markdown(f"**Exam:** {data.get('exam_target','None')}")
            st.markdown(f"**Wake:** {data.get('wake_time','06:00')}")
        with col2:
            st.markdown(f"**Sleep:** {data.get('sleep_hours_per_day',7)}h")
            st.markdown(f"**Max study/day:** {data.get('max_daily_study_hours',6)}h")
            st.markdown(f"**Weeks:** {data.get('n_weeks',4)}")
        with col3:
            st.markdown(f"**College study:** {data.get('college_study_hours',3)}h/day")
            st.markdown(f"**Exam study:** {data.get('competitive_study_hours',3)}h/day")
            st.markdown(f"**Style:** {data.get('study_style','Mixed')}")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("⚡ Generate Timetable Now!", use_container_width=True, type="primary"):
            with st.spinner("🧠 Generating your personalised timetable…"):
                # Parse topics from raw subjects
                college_topics = _parse_subjects(data.get("college_subjects_raw", ""))
                comp_topics    = _parse_subjects(data.get("comp_subjects_raw", ""))

                config = {
                    "sleep_hours_per_day":    data.get("sleep_hours_per_day", 7),
                    "wake_time":              data.get("wake_time", "06:00"),
                    "max_daily_study_hours":  data.get("max_daily_study_hours", 6),
                    "weekly_free_hours":      data.get("weekly_free_hours", 6),
                    "college_study_hours":    data.get("college_study_hours", 3),
                    "competitive_study_hours":data.get("competitive_study_hours", 3),
                    "college_hours":          data.get("college_hours", {}),
                    "blocked_slots":          data.get("blocked_slots", []),
                    "weak_subjects":          data.get("weak_subjects", ""),
                    "college_topics":         college_topics,
                    "competitive_topics":     comp_topics,
                }

                n_weeks = data.get("n_weeks", 4)
                grids   = generate_multi_week(config, n_weeks)
                analytics = compute_analytics(grids)

                st.session_state.timetable_grids   = grids
                st.session_state.timetable_config  = config
                st.session_state.timetable_analytics = analytics

                # Persist for logged-in users
                if st.session_state.user:
                    from database.models import save_timetable
                    grid_serializable = {
                        str(i): grids[i] for i in range(len(grids))
                    }
                    save_timetable(
                        user_id=st.session_state.user["id"],
                        name=f"{data.get('name','')} — {n_weeks}wk",
                        config=config,
                        grid=grid_serializable,
                        weeks=n_weeks
                    )

            st.success("✅ Timetable generated successfully!")
            st.markdown('<div class="info-banner">📅 Head to the <b>Timetable</b> tab to view your schedule.</div>', unsafe_allow_html=True)
            if st.button("View Timetable →", type="primary"):
                st.session_state.page = "timetable"
                st.rerun()

    # ── Navigation buttons ──
    st.markdown("<br>", unsafe_allow_html=True)
    col_back, col_space, col_next = st.columns([1, 3, 1])
    with col_back:
        if step > 0 and st.button("← Back"):
            st.session_state.wizard_step -= 1
            st.session_state.wizard_data = data
            st.rerun()
    with col_next:
        if step < len(STEPS) - 1:
            if st.button("Next →", type="primary"):
                st.session_state.wizard_step += 1
                st.session_state.wizard_data = data
                st.rerun()


def _parse_subjects(raw: str) -> list:
    """Parse 'Subject, Difficulty' lines → topic list."""
    topics = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        subj = parts[0]
        diff = parts[1] if len(parts) > 1 else ""
        topics.append(f"{subj} ({diff})" if diff else subj)
    return topics
