# 🎓 StudyPilot — AI-Powered Study Scheduler

> Transform your chaotic schedule into an intelligent, conflict-free study timetable.

![StudyPilot Banner](assets/images/banner.png)

---

## ✨ Features

| Feature | Description |
|---|---|
| ⚡ AI Timetable Generator | Constraint-based scheduling respecting sleep, college, and blocked slots |
| 📅 Multi-Week Planning | Generate 1–12 weeks in one click |
| 📊 Analytics Dashboard | Heatmaps, subject distribution, productivity score |
| ⏱️ Focus Mode | Built-in Pomodoro timer + session logging |
| 📥 Export | Excel (all weeks) + CSV downloads |
| 🔐 Auth System | Lightweight SQLite-backed login/signup |
| 🔥 Streak Tracker | Daily study streaks persisted to DB |
| 🎨 Premium UI | Dark glassmorphism theme, Plotly charts |

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone the repo
git clone https://github.com/your-username/studypilot.git
cd studypilot

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

App opens at **http://localhost:8501**

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New App"** → select your repo → set main file: `app.py`
4. Click **Deploy** — done in ~2 minutes

---

## 🐳 Deploy with Docker

```bash
docker build -t studypilot .
docker run -p 8501:8501 studypilot
```

---

## 🟣 Deploy to Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set **Start Command:** `streamlit run app.py --server.port $PORT --server.headless true`
4. Set **Build Command:** `pip install -r requirements.txt`

---

## 🤗 Deploy to HuggingFace Spaces

1. Create a Space with **Streamlit** SDK
2. Upload all files
3. The app will auto-deploy

---

## 📁 Project Structure

```
studypilot/
├── app.py                      # Entry point & landing page
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml             # Theme config
│
├── pages/
│   ├── auth_page.py            # Login / Signup
│   ├── generator_page.py       # 5-step wizard
│   ├── timetable_page.py       # Timetable viewer
│   ├── dashboard_page.py       # Analytics
│   ├── focus_page.py           # Pomodoro + session log
│   └── settings_page.py
│
├── backend/
│   ├── scheduler/
│   │   └── engine.py           # Core scheduling logic
│   └── exports/
│       └── export_engine.py    # Excel / CSV export
│
├── components/
│   └── timetable_view.py       # HTML timetable renderer
│
├── database/
│   └── models.py               # SQLite ORM
│
└── assets/
    └── styles/
        └── theme.py            # CSS injection + helpers
```

---

## 🧠 How the Scheduling Engine Works

1. **Input parsing** — wake time, sleep hours, college class slots, blocked periods
2. **Constraint modeling** — marks unavailable slots (sleep/meals/college/blocked)
3. **Slot assignment** — fills remaining slots with college study → competitive → revision → free
4. **Workload balancing** — respects daily max hours, inserts breaks every 2 study hours
5. **Multi-week generation** — shuffles topic order each week for spaced repetition

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit + Custom CSS (glassmorphism)
- **Charts:** Plotly
- **Scheduling:** Pure Python constraint engine (OR-Tools optional upgrade)
- **Database:** SQLite via stdlib `sqlite3`
- **Exports:** openpyxl (Excel), pandas (CSV)
- **Auth:** SHA-256 hashed passwords, session state

---

## 📝 License

MIT © 2024 StudyPilot
