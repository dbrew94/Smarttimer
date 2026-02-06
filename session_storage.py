import json
import datetime

SESSION_DATA_FILE = "session_history.json"

def today_date():
    # Returns date string as YYYY-MM-DD
    return datetime.date.today().isoformat()

def save_sessions(session_history_by_day):
    with open(SESSION_DATA_FILE, "w") as f:
        json.dump(session_history_by_day, f)

def load_sessions():
    try:
        with open(SESSION_DATA_FILE, "r") as f:
            contents = f.read().strip()
            if not contents:
                return {}  # Return an empty dict (by-day format) for new/empty files
            return json.loads(contents)
    except FileNotFoundError:
        return {}

def add_session_for_today(session_history_by_day, finished_length):
    date_str = today_date()
    if date_str not in session_history_by_day:
        session_history_by_day[date_str] = []
    session_history_by_day[date_str].append(finished_length)
    save_sessions(session_history_by_day)