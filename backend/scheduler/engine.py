"""
StudyPilot — Scheduling Engine
Refactored from SSG.ipynb: constraint-based weekly + multi-week timetable generation.
"""

import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd

WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HOURS = [f"{h:02d}:00-{(h+1)%24:02d}:00" for h in range(24)]

# Emoji labels for slot types
EMOJI = {
    "college":     "📘",
    "competitive": "🏆",
    "revision":    "🔁",
    "break":       "☕",
    "sleep":       "😴",
    "free":        "🎮",
    "exercise":    "🏃",
    "meal":        "🍽️",
    "blocked":     "🚫",
    "college_class": "🎓",
}

SUBJECT_COLORS = [
    "#6C63FF", "#FF6584", "#43E97B", "#FA8231",
    "#00B4D8", "#EE5A24", "#A29BFE", "#FD79A8",
    "#55EFC4", "#FDCB6E", "#74B9FF", "#E17055",
]


# ─────────────────────────── Helpers ───────────────────────────

def parse_hhmm(s: Any) -> Optional[str]:
    """Normalise any time string to 'HH:MM' or None."""
    if not s:
        return None
    s = str(s).strip().lower()
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", s)
    if not m:
        return None
    hh, mm = int(m.group(1)), int(m.group(2) or 0)
    ampm = m.group(3)
    if ampm == "pm" and hh != 12:
        hh += 12
    if ampm == "am" and hh == 12:
        hh = 0
    return f"{hh%24:02d}:{mm:02d}"


def to_min(hhmm: Optional[str]) -> Optional[int]:
    if not hhmm:
        return None
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


def hour_label(h: int) -> str:
    return f"{h:02d}:00-{(h+1)%24:02d}:00"


def overlap(a1: int, a2: int, b1: int, b2: int) -> bool:
    return max(a1, b1) < min(a2, b2)


def expand_day_range(s: str) -> List[str]:
    """Expand 'Mon-Fri', 'Mon,Wed,Fri' → full day names."""
    if not s:
        return []
    short = {d[:3].lower(): d for d in WEEK}
    s = str(s).strip().replace("–", "-").replace("—", "-")

    if "," in s:
        return [short[p.strip().lower()[:3]] for p in s.split(",") if p.strip().lower()[:3] in short]

    if "-" not in s:
        k = s.strip().lower()[:3]
        return [short[k]] if k in short else []

    try:
        a, b = [x.strip().lower()[:3] for x in s.split("-", 1)]
        if a not in short or b not in short:
            return []
        si, ei = WEEK.index(short[a]), WEEK.index(short[b])
        return WEEK[si:ei+1] if si <= ei else WEEK[si:] + WEEK[:ei+1]
    except Exception:
        return []


def extract_topics(syllabus: Dict) -> List[str]:
    """Extract subject-topic pairs from a syllabus dict."""
    if not syllabus:
        return []
    try:
        df = pd.DataFrame(syllabus)
        text = " ".join(df.astype(str).values.flatten())
        rows = re.findall(r"([A-Za-z &]+)\s+([A-Za-z &()]+)\s+\d", text)
        return [f"{a.strip()} — {b.strip()}" for a, b in rows] if rows else []
    except Exception:
        return []


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(float(x))
    except Exception:
        return default


# ─────────────────────────── Core Generator ───────────────────────────

class SchedulingEngine:
    """
    Generates a single-week timetable grid respecting all constraints.
    Returns a dict: {day: {hour_slot: label}}
    """

    def __init__(self, config: Dict):
        self.cfg = config
        self._parse_config()

    def _parse_config(self):
        c = self.cfg
        self.sleep_hours    = safe_float(c.get("sleep_hours_per_day"), 6)
        self.wake_time      = parse_hhmm(c.get("wake_time") or "05:00") or "05:00"
        self.max_study      = safe_int(c.get("max_daily_study_hours"), 6)
        self.weekly_free    = safe_float(c.get("weekly_free_hours"), 4)
        self.college_study  = safe_int(c.get("college_study_hours"), 3)
        self.comp_study     = safe_int(c.get("competitive_study_hours"), 3)
        self.college_hours  = c.get("college_hours", {})   # {day: [{start,end}]}
        self.blocked_slots  = c.get("blocked_slots", [])   # [{day, start, end}]
        self.weak_subjects  = c.get("weak_subjects", "")
        self.college_topics = c.get("college_topics", [])
        self.comp_topics    = c.get("competitive_topics", [])

        wake_min = to_min(self.wake_time) or 300
        sleep_min = int(self.sleep_hours * 60)
        self.sleep_start_min = (wake_min - sleep_min) % 1440
        self.sleep_end_min   = wake_min

    # ── blocked-slot check ──
    def _is_blocked(self, day: str, h: int) -> bool:
        slot_start, slot_end = h * 60, (h + 1) * 60
        # sleep
        ss, se = self.sleep_start_min, self.sleep_end_min
        if ss < se:
            if overlap(slot_start, slot_end, ss, se):
                return True
        else:  # wraps midnight
            if overlap(slot_start, slot_end, ss, 1440) or overlap(slot_start, slot_end, 0, se):
                return True
        # college classes
        for cls in self.college_hours.get(day, []):
            cs = to_min(parse_hhmm(cls.get("start", "")))
            ce = to_min(parse_hhmm(cls.get("end", "")))
            if cs is not None and ce is not None and overlap(slot_start, slot_end, cs, ce):
                return True
        # custom blocked
        for b in self.blocked_slots:
            if b.get("day", "").lower() == day.lower() or b.get("day", "") == "All":
                bs = to_min(parse_hhmm(b.get("start", "")))
                be = to_min(parse_hhmm(b.get("end", "")))
                if bs is not None and be is not None and overlap(slot_start, slot_end, bs, be):
                    return True
        return False

    def _is_sleep(self, h: int) -> bool:
        slot_start, slot_end = h * 60, (h + 1) * 60
        ss, se = self.sleep_start_min, self.sleep_end_min
        if ss < se:
            return overlap(slot_start, slot_end, ss, se)
        return overlap(slot_start, slot_end, ss, 1440) or overlap(slot_start, slot_end, 0, se)

    def _is_college_class(self, day: str, h: int) -> bool:
        slot_start, slot_end = h * 60, (h + 1) * 60
        for cls in self.college_hours.get(day, []):
            cs = to_min(parse_hhmm(cls.get("start", "")))
            ce = to_min(parse_hhmm(cls.get("end", "")))
            if cs is not None and ce is not None and overlap(slot_start, slot_end, cs, ce):
                return True
        return False

    # ── main build ──
    def generate_week(self, week_num: int = 1) -> Dict[str, Dict[str, str]]:
        """Return {day: {slot_label: content_label}} for one week."""
        random.seed(week_num * 42)

        college_topics = list(self.college_topics) or [
            "Mathematics — Calculus", "Physics — Mechanics", "CS — Data Structures"
        ]
        comp_topics = list(self.comp_topics) or [
            "Quant — Arithmetic", "Verbal — Reading Comprehension", "DILR — Puzzles"
        ]

        # Shuffle for variety each week
        random.shuffle(college_topics)
        random.shuffle(comp_topics)

        grid: Dict[str, Dict[str, str]] = {}

        for day in WEEK:
            grid[day] = {}
            study_count = 0
            topic_pool_col  = list(college_topics)
            topic_pool_comp = list(comp_topics)

            for h in range(24):
                slot = hour_label(h)

                if self._is_sleep(h):
                    grid[day][slot] = EMOJI["sleep"] + " Sleep"
                    continue

                if self._is_college_class(day, h):
                    grid[day][slot] = EMOJI["college_class"] + " College Class"
                    continue

                # Skip meal slots (07-08, 13-14, 19-20)
                if h in (7, 13, 19):
                    grid[day][slot] = EMOJI["meal"] + " Meal / Break"
                    continue

                # Exercise morning slot
                if h == (to_min(self.wake_time) or 300) // 60:
                    grid[day][slot] = EMOJI["exercise"] + " Morning Routine"
                    continue

                if self._is_blocked(day, h):
                    grid[day][slot] = EMOJI["blocked"] + " Blocked"
                    continue

                if study_count >= self.max_study:
                    grid[day][slot] = EMOJI["free"] + " Free / Leisure"
                    continue

                # Assign study slots
                # break every 2 study hours
                if study_count > 0 and study_count % 2 == 0:
                    grid[day][slot] = EMOJI["break"] + " Short Break"
                    continue

                # college vs competitive quota
                col_done  = sum(1 for v in grid[day].values() if v.startswith(EMOJI["college"]))
                comp_done = sum(1 for v in grid[day].values() if v.startswith(EMOJI["competitive"]))

                if col_done < self.college_study and topic_pool_col:
                    topic = topic_pool_col.pop(0) if topic_pool_col else random.choice(college_topics)
                    grid[day][slot] = f"{EMOJI['college']} {topic}"
                    study_count += 1
                elif comp_done < self.comp_study and topic_pool_comp:
                    topic = topic_pool_comp.pop(0) if topic_pool_comp else random.choice(comp_topics)
                    grid[day][slot] = f"{EMOJI['competitive']} {topic}"
                    study_count += 1
                elif study_count < self.max_study:
                    # revision
                    all_topics = college_topics + comp_topics
                    topic = random.choice(all_topics) if all_topics else "General Review"
                    grid[day][slot] = f"{EMOJI['revision']} Revision: {topic}"
                    study_count += 1
                else:
                    grid[day][slot] = EMOJI["free"] + " Free / Leisure"

        return grid


# ─────────────────────────── Multi-week ───────────────────────────

def generate_multi_week(config: Dict, n_weeks: int) -> List[Dict]:
    """Generate n_weeks of timetable grids."""
    engine = SchedulingEngine(config)
    return [engine.generate_week(week_num=w + 1) for w in range(n_weeks)]


# ─────────────────────────── Analytics ───────────────────────────

def compute_analytics(grids: List[Dict]) -> Dict:
    """Aggregate study metrics from multi-week grids."""
    subject_hours: Dict[str, float] = {}
    weekly_study: List[float] = []
    daily_breakdown: Dict[str, float] = {d: 0 for d in WEEK}

    for grid in grids:
        week_total = 0
        for day, slots in grid.items():
            for slot, label in slots.items():
                is_study = any(label.startswith(e) for e in [
                    EMOJI["college"], EMOJI["competitive"], EMOJI["revision"]
                ])
                if is_study:
                    week_total += 1
                    daily_breakdown[day] = daily_breakdown.get(day, 0) + 1
                    # extract subject
                    subj = label.split(" ", 1)[1].split("—")[0].strip() if " " in label else "General"
                    subject_hours[subj] = subject_hours.get(subj, 0) + 1
        weekly_study.append(week_total)

    total_study = sum(weekly_study)
    total_days = len(grids) * 7 or 1

    return {
        "total_study_hours":  total_study,
        "weekly_avg":         round(sum(weekly_study) / len(weekly_study), 1) if weekly_study else 0,
        "weekly_study":       weekly_study,
        "subject_hours":      subject_hours,
        "daily_breakdown":    daily_breakdown,
        "productivity_score": min(100, int((total_study / (total_days * 6)) * 100)),
    }


def grid_to_dataframe(grid: Dict) -> pd.DataFrame:
    """Convert grid dict → tidy DataFrame."""
    rows = []
    for day, slots in grid.items():
        for slot, label in slots.items():
            rows.append({"Day": day, "Slot": slot, "Activity": label})
    return pd.DataFrame(rows)


def get_subject_color_map(subjects: List[str]) -> Dict[str, str]:
    return {s: SUBJECT_COLORS[i % len(SUBJECT_COLORS)] for i, s in enumerate(subjects)}
