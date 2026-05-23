# StudyPilot — Smart Study Scheduler

A Streamlit-based study planning application that generates optimized study timetables based on user constraints such as college timings, sleep schedule, study goals, and blocked hours.

🔗 Live Demo: https://smart-schedule-generator.streamlit.app/

---

## Features

- Automated timetable generation
- Multi-week study planning
- Productivity analytics dashboard
- Subject-wise study tracking
- Pomodoro-based focus mode
- Excel and CSV export
- SQLite-based login system
- Responsive Streamlit UI

---

## Screenshots

### Dashboard
![Dashboard](assets/screenshots/dboard.png)

### Timetable Generator
![Generator](assets/screenshots/gen.png)

### Timetable
![Timetable](assets/screenshots/tt.png)

### Focus Mode
![Focus](assets/screenshots/fm.png)

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- SQLite
- OpenPyXL

---

## Project Structure

```text
studypilot/
├── app.py
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml
│
├── pages/
│   ├── auth_page.py
│   ├── generator_page.py
│   ├── timetable_page.py
│   ├── dashboard_page.py
│   ├── focus_page.py
│   └── settings_page.py
│
├── backend/
│   ├── scheduler/
│   │   └── engine.py
│   └── exports/
│       └── export_engine.py
│
├── components/
│   └── timetable_view.py
│
├── database/
│   └── models.py
│
└── assets/
    ├── screenshots/
    └── styles/
```

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/studypilot.git
cd studypilot
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / Mac

```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Application

```bash
streamlit run app.py
```

App runs at:

```text
http://localhost:8501
```

---

## Deployment

### Streamlit Cloud

1. Push project to GitHub
2. Go to https://share.streamlit.io
3. Create a new app
4. Select repository
5. Set main file:

```text
app.py
```

6. Deploy

---

## Scheduling Workflow

1. User inputs study preferences and constraints
2. Blocked slots are identified
3. Available study periods are calculated
4. Subjects are distributed based on priority and workload
5. Timetable is generated and visualized
6. User can export schedules to Excel or CSV

---

## Future Improvements

- Calendar integration
- OCR timetable extraction
- AI-based recommendations
- Mobile optimization
- Notification system
- Cloud database support

---

## Author

Shubham Maskare

---

## License

MIT License
