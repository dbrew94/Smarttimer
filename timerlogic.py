# timerlogic.py

class PomodoroTimer:
    def __init__(self, duration_sec):
        self.initial = duration_sec
        self.remaining = duration_sec
        self.running = False

    def start(self):
        self.running = True

    def tick(self):
        if self.running and self.remaining > 0:
            self.remaining -= 1
            if self.remaining == 0:
                self.running = False

    def pause(self):
        self.running = False

    def reset(self):
        self.remaining = self.initial
        self.running = False

    def is_complete(self):
        return self.remaining == 0

def suggest_adaptive_interval(session_durations):
    default = 25 * 60
    if not session_durations:
        return default
    avg = sum(session_durations) / len(session_durations)
    if avg < 15 * 60:
        return int(max(avg, 10*60))  # Don't go below 10min
    elif avg > 30 * 60:
        return int(min(avg, 60*60))  # Cap at 1hr
    else:
        return default