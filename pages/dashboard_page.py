"""
StudyPilot — Dashboard & Analytics Page
Visualises study patterns, subject distribution, productivity score.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from assets.styles.theme import inject_css, kpi
from backend.scheduler.engine import compute_analytics, WEEK


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#C0C0D8"),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(showgrid=False, zeroline=False, color="#6060A0"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, color="#6060A0"),
)


def render_dashboard():
    inject_css()

    st.markdown('<h1 style="font-family:Syne,sans-serif">📊 Analytics Dashboard</h1>', unsafe_allow_html=True)

    grids     = st.session_state.get("timetable_grids", [])
    analytics = st.session_state.get("timetable_analytics", {})

    if not grids:
        st.markdown('<div class="warn-banner">⚠️ Generate a timetable first to see analytics.</div>', unsafe_allow_html=True)
        if st.button("⚡ Go to Generator", type="primary"):
            st.session_state.page = "generator"
            st.rerun()
        return

    if not analytics:
        analytics = compute_analytics(grids)

    # ── KPI Row ──
    st.markdown("### Key Metrics")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(kpi(f"{analytics.get('total_study_hours', 0)}h", "Total Study Hours"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi(f"{analytics.get('weekly_avg', 0)}h", "Weekly Average"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi(f"{analytics.get('productivity_score', 0)}%", "Productivity Score"), unsafe_allow_html=True)
    with k4:
        n_subjects = len(analytics.get("subject_hours", {}))
        st.markdown(kpi(str(n_subjects), "Subjects Covered"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row 1 ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Weekly Study Trend")
        weekly = analytics.get("weekly_study", [])
        if weekly:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[f"Week {i+1}" for i in range(len(weekly))],
                y=weekly,
                mode="lines+markers",
                line=dict(color="#6C63FF", width=3),
                marker=dict(size=8, color="#43E97B"),
                fill="tozeroy",
                fillcolor="rgba(108,99,255,0.08)"
            ))
            fig.update_layout(**PLOTLY_LAYOUT, height=260)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Subject Distribution")
        subj_hours = analytics.get("subject_hours", {})
        if subj_hours:
            labels = list(subj_hours.keys())
            values = list(subj_hours.values())
            colors = ["#6C63FF","#43E97B","#FA8231","#FF6584","#00B4D8","#A29BFE","#FD79A8","#FDCB6E"]
            fig2 = go.Figure(go.Pie(
                labels=labels, values=values,
                hole=0.52,
                marker=dict(colors=colors[:len(labels)]),
                textfont=dict(color="#E8E8F0"),
            ))
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#C0C0D8"),
                margin=dict(l=10,r=10,t=10,b=10),
                showlegend=True,
                legend=dict(font=dict(color="#C0C0D8")),
                height=260
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No subject data available.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Charts row 2 ──
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Daily Study Pattern (Avg Across Weeks)")
        daily = analytics.get("daily_breakdown", {})
        if daily:
            days = WEEK
            vals = [daily.get(d, 0) / max(len(grids), 1) for d in days]
            fig3 = go.Figure(go.Bar(
                x=days, y=vals,
                marker=dict(
                    color=vals,
                    colorscale=[[0, "#3A3A7A"], [1, "#6C63FF"]],
                    line=dict(color="rgba(0,0,0,0)")
                ),
            ))
            fig3.update_layout(**PLOTLY_LAYOUT, height=260)
            st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Productivity Score Gauge")
        score = analytics.get("productivity_score", 0)
        fig4 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            number=dict(suffix="%", font=dict(color="#A09AFF", size=32, family="Syne")),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor="#6060A0"),
                bar=dict(color="#6C63FF"),
                bgcolor="rgba(255,255,255,0.05)",
                bordercolor="rgba(0,0,0,0)",
                steps=[
                    dict(range=[0, 40], color="rgba(255,100,100,0.1)"),
                    dict(range=[40, 70], color="rgba(255,200,50,0.1)"),
                    dict(range=[70, 100], color="rgba(67,233,123,0.1)"),
                ],
                threshold=dict(line=dict(color="#43E97B", width=3), thickness=0.75, value=score)
            )
        ))
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#C0C0D8", family="DM Sans"),
            margin=dict(l=20,r=20,t=20,b=10),
            height=260
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Study Activity Heatmap ──
    st.markdown("#### Study Activity Heatmap")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    heatmap_data = _build_heatmap(grids)
    if not heatmap_data.empty:
        fig5 = px.imshow(
            heatmap_data,
            color_continuous_scale=[[0, "#12122A"], [0.5, "#3A3A7A"], [1, "#6C63FF"]],
            aspect="auto",
            labels=dict(x="Hour", y="Day", color="Study hrs")
        )
        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#C0C0D8", family="DM Sans"),
            margin=dict(l=10,r=10,t=20,b=10),
            height=280,
            coloraxis_colorbar=dict(tickfont=dict(color="#C0C0D8"))
        )
        st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Smart Insights ──
    st.markdown("### 🧠 Smart Insights")
    insights = _generate_insights(analytics)
    i_cols = st.columns(3)
    for i, insight in enumerate(insights):
        with i_cols[i % 3]:
            st.markdown(f'<div class="glass-card"><p style="margin:0">{insight}</p></div>', unsafe_allow_html=True)


def _build_heatmap(grids):
    """Build day × hour study frequency matrix."""
    hours = list(range(5, 23))
    days  = WEEK
    mat   = {d: {h: 0 for h in hours} for d in days}

    for grid in grids:
        for day in days:
            for h in hours:
                slot = f"{h:02d}:00-{(h+1)%24:02d}:00"
                label = grid.get(day, {}).get(slot, "")
                if any(label.startswith(e) for e in ["📘", "🏆", "🔁"]):
                    mat[day][h] += 1

    rows = []
    for day in days:
        rows.append([mat[day][h] for h in hours])
    return pd.DataFrame(rows, index=days, columns=[f"{h:02d}:00" for h in hours])


def _generate_insights(analytics: dict) -> list:
    insights = []
    total = analytics.get("total_study_hours", 0)
    score = analytics.get("productivity_score", 0)
    weekly_avg = analytics.get("weekly_avg", 0)
    subj_hours = analytics.get("subject_hours", {})

    if total > 0:
        insights.append(f"📚 You've scheduled **{total} study hours** in total. Keep up the momentum!")

    if score >= 80:
        insights.append("🚀 **Excellent productivity score!** Your schedule is well-balanced.")
    elif score >= 50:
        insights.append("⚡ **Good balance.** Consider adding 1-2 more focused study hours daily.")
    else:
        insights.append("⚠️ **Low productivity score.** Try increasing daily study hours or reducing blocked slots.")

    if subj_hours:
        most = max(subj_hours, key=subj_hours.get)
        least = min(subj_hours, key=subj_hours.get)
        insights.append(f"📈 **{most}** is your most studied subject. Consider giving more time to **{least}**.")

    if weekly_avg < 10:
        insights.append("💡 **Tip:** Aim for at least 10 study hours per week for consistent progress.")

    if len(insights) < 3:
        insights.append("🔁 **Revision tip:** Schedule at least 1 revision session per subject every week.")

    return insights[:6]
