"""
StudyPilot — Timetable Visualizer Component
Renders an interactive HTML timetable grid.
"""

from typing import Dict, List
import streamlit as st

WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HOURS = [f"{h:02d}:00-{(h+1)%24:02d}:00" for h in range(24)]

# Only show hours with content (non-empty or non-free) for compact view
SHOW_HOURS = list(range(5, 24))  # 5am–midnight


def _slot_class(label: str) -> str:
    if label.startswith("📘"):
        return "slot-college"
    if label.startswith("🏆"):
        return "slot-competitive"
    if label.startswith("🔁"):
        return "slot-revision"
    if label.startswith("😴"):
        return "slot-sleep"
    if label.startswith("☕") or label.startswith("🍽️"):
        return "slot-break"
    if label.startswith("🎓"):
        return "slot-college"
    if label.startswith("🏃"):
        return "slot-break"
    return "slot-free"


def render_timetable_html(grid: Dict, show_hours: List[int] = None) -> str:
    """Render full week timetable as styled HTML table."""
    hrs = show_hours or SHOW_HOURS
    hour_labels = [f"{h:02d}:00" for h in hrs]
    slot_keys   = [f"{h:02d}:00-{(h+1)%24:02d}:00" for h in hrs]

    cols = "".join(f'<th>{h}</th>' for h in hour_labels)
    header = f'<tr><th>Day</th>{cols}</tr>'

    rows = ""
    for day in WEEK:
        cells = f'<td style="font-family:\'Syne\',sans-serif;font-weight:600;color:#A09AFF;white-space:nowrap">{day[:3]}</td>'
        day_slots = grid.get(day, {})
        for sk in slot_keys:
            label = day_slots.get(sk, "")
            cls   = _slot_class(label)
            short = label[:30] + "…" if len(label) > 30 else label
            cells += f'<td><div class="{cls}" title="{label}">{short}</div></td>'
        rows += f"<tr>{cells}</tr>"

    return f"""
    <div style="overflow-x:auto;margin-top:1rem">
      <table class="tt-grid">
        <thead>{header}</thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    """


def render_daily_view(grid: Dict, day: str) -> str:
    """Render a single-day timeline card view."""
    slots = grid.get(day, {})
    cards_html = ""
    for h in range(24):
        slot_key = f"{h:02d}:00-{(h+1)%24:02d}:00"
        label = slots.get(slot_key, "")
        if not label:
            continue
        cls = _slot_class(label)
        cards_html += f"""
        <div class="{cls}" style="display:flex;align-items:center;gap:0.6rem;margin:0.3rem 0;padding:0.5rem 0.8rem;border-radius:8px">
            <span style="font-size:0.78rem;color:#6060A0;min-width:50px;font-family:'Syne',sans-serif">{h:02d}:00</span>
            <span style="font-size:0.9rem">{label}</span>
        </div>
        """

    return f"""
    <div class="glass-card">
      <h4 style="font-family:'Syne',sans-serif;color:#A09AFF;margin-bottom:0.8rem">{day}</h4>
      {cards_html or '<p style="color:#6060A0">No activities</p>'}
    </div>
    """


def subject_legend_html(subjects: List[str], color_map: Dict[str, str]) -> str:
    items = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:0.3rem;margin:0.2rem 0.4rem">'
        f'<span style="width:10px;height:10px;border-radius:3px;background:{color_map.get(s,"#6C63FF")}"></span>'
        f'<span style="font-size:0.78rem;color:#C0C0D8">{s}</span>'
        f'</span>'
        for s in subjects
    )
    return f'<div style="margin:0.5rem 0">{items}</div>'
