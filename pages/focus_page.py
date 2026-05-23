"""
StudyPilot — Focus Mode Page
Pomodoro timer + session logger.
"""

import streamlit as st
from datetime import datetime
from assets.styles.theme import inject_css


def render_focus():
    inject_css()

    st.markdown('<h1 style="font-family:Syne,sans-serif">⏱️ Focus Mode</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#7070A0">Deep work sessions with built-in Pomodoro timer.</p>', unsafe_allow_html=True)

    # Streak display
    if st.session_state.user:
        from database.models import get_streak
        streak = get_streak(st.session_state.user["id"])
        s1, s2, _, _ = st.columns(4)
        with s1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">🔥 {streak.get('current', 0)}</div>
                <div class="kpi-label">Day Streak</div>
            </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">🏆 {streak.get('best', 0)}</div>
                <div class="kpi-label">Best Streak</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Pomodoro timer (interactive HTML)
    st.markdown("### 🍅 Pomodoro Timer")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.components.v1.html(_pomodoro_html(), height=420, scrolling=False)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📝 Log a Study Session")

        grids = st.session_state.get("timetable_grids", [])
        subjects = _extract_subjects(grids)

        subject = st.selectbox("Subject", subjects or ["Mathematics", "Physics", "CS", "Other"])
        duration = st.slider("Duration (minutes)", 15, 180, 60, step=15)
        notes    = st.text_area("Session notes (optional)", placeholder="What did you study?", height=80)

        if st.button("✅ Log Session", use_container_width=True, type="primary"):
            if st.session_state.user:
                from database.models import log_session
                log_session(
                    user_id=st.session_state.user["id"],
                    subject=subject,
                    duration_min=duration,
                    notes=notes
                )
                st.success(f"Session logged: {duration}min of {subject} 🎯")
                st.balloons()
            else:
                st.info("Login to save sessions and track streaks!")

        st.markdown('</div>', unsafe_allow_html=True)

    # Session history
    if st.session_state.user:
        st.markdown("### 📋 Recent Sessions")
        from database.models import get_sessions
        sessions = get_sessions(st.session_state.user["id"], limit=10)
        if sessions:
            import pandas as pd
            df = pd.DataFrame(sessions)[["date", "subject", "duration_min", "notes"]]
            df.columns = ["Date", "Subject", "Duration (min)", "Notes"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="info-banner">No sessions logged yet. Start your first one above!</div>', unsafe_allow_html=True)

    # Motivational quote
    quotes = [
        "The secret of getting ahead is getting started. — Mark Twain",
        "Study hard what interests you the most in the most undisciplined way. — Richard Feynman",
        "An investment in knowledge pays the best interest. — Benjamin Franklin",
        "The beautiful thing about learning is that nobody can take it away from you. — B.B. King",
        "Success is the sum of small efforts repeated day in and day out. — Robert Collier",
    ]
    import random
    q = random.choice(quotes)
    st.markdown(f'<div class="glass-card" style="text-align:center;color:#9090B0;font-style:italic">&ldquo;{q}&rdquo;</div>', unsafe_allow_html=True)


def _extract_subjects(grids):
    subjects = set()
    for grid in grids:
        for day_slots in grid.values():
            for label in day_slots.values():
                if any(label.startswith(e) for e in ["📘", "🏆", "🔁"]) and " " in label:
                    subj = label.split(" ", 1)[1].split("—")[0].split("(")[0].strip()
                    if subj:
                        subjects.add(subj)
    return sorted(subjects)


def _pomodoro_html() -> str:
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: transparent; font-family: 'DM Sans', sans-serif; color: #E8E8F0; }
      .container { display: flex; flex-direction: column; align-items: center; padding: 1rem; }
      .mode-btns { display: flex; gap: 0.5rem; margin-bottom: 1.2rem; }
      .mode-btn {
        padding: 0.4rem 1rem; border-radius: 50px; border: 1px solid rgba(108,99,255,0.3);
        background: rgba(255,255,255,0.05); color: #A09AFF; cursor: pointer;
        font-family: 'DM Sans'; font-size: 0.8rem; transition: all 0.2s;
      }
      .mode-btn.active { background: #6C63FF; color: #fff; border-color: #6C63FF; }
      .ring-wrap {
        position: relative; width: 180px; height: 180px; margin: 0.5rem auto;
      }
      canvas { position: absolute; top:0; left:0; }
      .timer-text {
        position: absolute; top:50%; left:50%; transform: translate(-50%,-50%);
        font-family: 'Syne', sans-serif; font-size: 2.6rem; font-weight: 800;
        color: #A09AFF; text-align: center; line-height: 1;
      }
      .phase-label { font-size: 0.75rem; color: #6060A0; margin-top: 4px; display: block; }
      .controls { display: flex; gap: 0.6rem; margin-top: 1rem; }
      .btn {
        padding: 0.55rem 1.4rem; border-radius: 50px;
        border: none; cursor: pointer; font-family: 'DM Sans'; font-weight: 600; font-size: 0.9rem;
        transition: all 0.15s;
      }
      .btn-start { background: linear-gradient(135deg, #6C63FF, #43E97B); color: #fff; }
      .btn-reset { background: rgba(255,255,255,0.08); color: #A09AFF; }
      .session-count { margin-top: 0.8rem; font-size: 0.8rem; color: #6060A0; }
      .dots { display: flex; gap: 4px; margin-top: 0.4rem; justify-content: center; }
      .dot { width:10px;height:10px;border-radius:50%;background:rgba(108,99,255,0.2); }
      .dot.done { background:#6C63FF; }
    </style>
    </head>
    <body>
    <div class="container">
      <div class="mode-btns">
        <button class="mode-btn active" onclick="setMode('pomodoro',25)">🍅 Focus</button>
        <button class="mode-btn" onclick="setMode('short',5)">☕ Short</button>
        <button class="mode-btn" onclick="setMode('long',15)">🛌 Long</button>
      </div>

      <div class="ring-wrap">
        <canvas id="ring" width="180" height="180"></canvas>
        <div class="timer-text">
          <span id="display">25:00</span>
          <span class="phase-label" id="phase">Focus Session</span>
        </div>
      </div>

      <div class="controls">
        <button class="btn btn-start" id="startBtn" onclick="toggleTimer()">▶ Start</button>
        <button class="btn btn-reset" onclick="resetTimer()">↺ Reset</button>
      </div>

      <p class="session-count">Sessions completed: <b id="sessCount">0</b></p>
      <div class="dots" id="dots">
        <div class="dot" id="d0"></div>
        <div class="dot" id="d1"></div>
        <div class="dot" id="d2"></div>
        <div class="dot" id="d3"></div>
      </div>
    </div>

    <script>
    let totalSecs = 25*60, remaining = 25*60, interval = null, running = false, sessCount = 0;
    const canvas = document.getElementById('ring');
    const ctx = canvas.getContext('2d');
    const cx = 90, cy = 90, r = 76;

    function drawRing(frac) {
      ctx.clearRect(0, 0, 180, 180);
      // Track
      ctx.beginPath(); ctx.arc(cx,cy,r,0,2*Math.PI);
      ctx.strokeStyle='rgba(108,99,255,0.15)'; ctx.lineWidth=10; ctx.stroke();
      // Progress
      if (frac > 0) {
        const grad = ctx.createLinearGradient(0,0,180,180);
        grad.addColorStop(0,'#6C63FF'); grad.addColorStop(1,'#43E97B');
        ctx.beginPath(); ctx.arc(cx,cy,r,-Math.PI/2,-Math.PI/2+2*Math.PI*frac);
        ctx.strokeStyle=grad; ctx.lineWidth=10; ctx.lineCap='round'; ctx.stroke();
      }
    }

    function fmt(s) {
      return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');
    }

    function tick() {
      if (remaining <= 0) {
        clearInterval(interval); running = false;
        document.getElementById('startBtn').textContent = '▶ Start';
        sessCount++; document.getElementById('sessCount').textContent = sessCount;
        for(let i=0;i<4;i++) {
          document.getElementById('d'+i).classList.toggle('done', i < sessCount % 4);
        }
        return;
      }
      remaining--;
      document.getElementById('display').textContent = fmt(remaining);
      drawRing(remaining / totalSecs);
    }

    function toggleTimer() {
      if (running) {
        clearInterval(interval); running = false;
        document.getElementById('startBtn').textContent = '▶ Resume';
      } else {
        interval = setInterval(tick, 1000); running = true;
        document.getElementById('startBtn').textContent = '⏸ Pause';
      }
    }

    function resetTimer() {
      clearInterval(interval); running = false; remaining = totalSecs;
      document.getElementById('display').textContent = fmt(remaining);
      document.getElementById('startBtn').textContent = '▶ Start';
      drawRing(1);
    }

    function setMode(mode, mins) {
      document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
      const labels = {pomodoro:'Focus Session', short:'Short Break', long:'Long Break'};
      document.getElementById('phase').textContent = labels[mode];
      totalSecs = mins * 60; resetTimer();
    }

    drawRing(1);
    </script>
    </body>
    </html>
    """
