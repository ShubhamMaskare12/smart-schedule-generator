"""
StudyPilot — Global CSS & Styling
Inject premium dark-theme styles into Streamlit.
"""

GLOBAL_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0F0F1A !important;
    font-family: 'DM Sans', sans-serif;
    color: #E8E8F0;
}

h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    color: #E8E8F0 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12122A 0%, #1A1A3E 100%) !important;
    border-right: 1px solid rgba(108,99,255,0.2);
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #C0C0D8 !important;
}

/* ── Cards / Glass ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(108,99,255,0.18);
    border-radius: 16px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.glass-card:hover {
    border-color: rgba(108,99,255,0.5);
    box-shadow: 0 0 24px rgba(108,99,255,0.12);
}

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, rgba(108,99,255,0.15) 0%, rgba(67,233,123,0.08) 100%);
    border: 1px solid rgba(108,99,255,0.25);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #43E97B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.kpi-label {
    font-size: 0.82rem;
    color: #9090B0;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* ── Gradient CTA button ── */
.cta-btn {
    display: inline-block;
    padding: 0.75rem 2rem;
    background: linear-gradient(135deg, #6C63FF, #43E97B);
    border-radius: 50px;
    color: #fff !important;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    text-decoration: none;
    box-shadow: 0 4px 20px rgba(108,99,255,0.35);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    cursor: pointer;
    border: none;
}
.cta-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(108,99,255,0.5);
}

/* ── Step wizard progress ── */
.wizard-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1.8rem;
}
.step-dot {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem;
    font-family: 'Syne', sans-serif;
    flex-shrink: 0;
}
.step-dot.active   { background: #6C63FF; color: #fff; box-shadow: 0 0 12px rgba(108,99,255,0.6); }
.step-dot.done     { background: #43E97B; color: #0F0F1A; }
.step-dot.inactive { background: rgba(255,255,255,0.08); color: #6060A0; border: 1px solid rgba(255,255,255,0.1); }
.step-line { flex: 1; height: 2px; background: rgba(255,255,255,0.08); }
.step-line.done { background: linear-gradient(90deg, #43E97B, rgba(108,99,255,0.4)); }

/* ── Timetable grid ── */
.tt-grid { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.tt-grid th {
    background: rgba(108,99,255,0.2);
    color: #C0B8FF;
    padding: 6px 10px;
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    border: 1px solid rgba(255,255,255,0.06);
}
.tt-grid td {
    padding: 5px 8px;
    border: 1px solid rgba(255,255,255,0.05);
    vertical-align: top;
    min-width: 80px;
}
.slot-college     { background: rgba(108,99,255,0.18); border-left: 3px solid #6C63FF; border-radius: 4px; padding: 3px 6px; }
.slot-competitive { background: rgba(255,215,0,0.12); border-left: 3px solid #FFD700; border-radius: 4px; padding: 3px 6px; }
.slot-revision    { background: rgba(67,233,123,0.12); border-left: 3px solid #43E97B; border-radius: 4px; padding: 3px 6px; }
.slot-sleep       { background: rgba(100,120,200,0.1); color: #7080B0; font-size: 0.72rem; }
.slot-break       { background: rgba(255,200,100,0.08); color: #C0A060; }
.slot-free        { color: #6060A0; font-size: 0.72rem; }

/* ── Form styling ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb],
[data-testid="stMultiSelect"] div[data-baseweb],
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(108,99,255,0.2) !important;
    border-radius: 10px !important;
    color: #E8E8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #6C63FF !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.2) !important;
}

/* ── Streamlit metric ── */
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.8rem !important;
    color: #A09AFF !important;
}
[data-testid="stMetricLabel"] {
    color: #7070A0 !important;
    font-size: 0.78rem !important;
}

/* ── Progress bar ── */
.stProgress > div > div { background: linear-gradient(90deg, #6C63FF, #43E97B) !important; border-radius: 50px !important; }

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid rgba(108,99,255,0.2); }
[data-testid="stTabs"] [role="tab"] { color: #7070A0; font-family: 'Syne', sans-serif; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #A09AFF; border-bottom: 2px solid #6C63FF; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #12122A; }
::-webkit-scrollbar-thumb { background: #3A3A7A; border-radius: 10px; }

/* ── Hero ── */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 800;
    line-height: 1.15;
    background: linear-gradient(135deg, #6C63FF 0%, #43E97B 60%, #FA8231 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.15rem;
    color: #9090B0;
    max-width: 540px;
    line-height: 1.6;
    margin-top: 1rem;
}

/* ── Feature badge ── */
.feature-badge {
    display: inline-block;
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 50px;
    padding: 0.25rem 0.85rem;
    font-size: 0.78rem;
    color: #A09AFF;
    letter-spacing: 0.05em;
    margin: 0.2rem;
}

/* ── Alert / info ── */
.info-banner {
    background: rgba(67,233,123,0.08);
    border: 1px solid rgba(67,233,123,0.25);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #80E8A0;
    font-size: 0.88rem;
}
.warn-banner {
    background: rgba(250,130,49,0.08);
    border: 1px solid rgba(250,130,49,0.3);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    color: #FA8231;
    font-size: 0.88rem;
}

/* ── Sidebar logo ── */
.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6C63FF, #43E97B);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    padding: 0.5rem 0 1.2rem;
    border-bottom: 1px solid rgba(108,99,255,0.15);
    margin-bottom: 1rem;
}

/* ── Pomodoro timer ── */
.pomodoro-ring {
    width: 160px; height: 160px;
    border-radius: 50%;
    border: 6px solid rgba(108,99,255,0.2);
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1rem;
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #A09AFF;
    position: relative;
}
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def card(content: str, extra_class: str = "") -> str:
    return f'<div class="glass-card {extra_class}">{content}</div>'


def kpi(value: str, label: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """


def step_wizard_html(steps: list, current: int) -> str:
    parts = []
    for i, name in enumerate(steps):
        if i < current:
            cls = "done"
            icon = "✓"
        elif i == current:
            cls = "active"
            icon = str(i + 1)
        else:
            cls = "inactive"
            icon = str(i + 1)
        parts.append(f'<div class="step-dot {cls}">{icon}</div>')
        parts.append(f'<span style="font-size:0.78rem;color:#7070A0">{name}</span>')
        if i < len(steps) - 1:
            line_cls = "done" if i < current else ""
            parts.append(f'<div class="step-line {line_cls}"></div>')
    return f'<div class="wizard-step">{"".join(parts)}</div>'
