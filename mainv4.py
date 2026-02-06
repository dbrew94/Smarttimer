import tkinter as tk
from tkinter import ttk, messagebox
from playsound3 import playsound
import matplotlib
import threading
import os
from session_storage import save_sessions, load_sessions, add_session_for_today, today_date
from timerlogic import PomodoroTimer, suggest_adaptive_interval
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime

class StudyTimerApp:
    def __init__(self, root):
        self.root = root
        root.title("Smart Study Timer")
        self.study_duration = 25 * 60
        self.break_duration = 5 * 60
        self.session_history_by_day = load_sessions()  # {"2026-01-30": [1500, 900]}

        # Timer/logic tracking
        self.on_study = True
        self.session_timer = PomodoroTimer(self.study_duration)
        self.timer_paused = False
        self.study_sessions_completed = 0
        self.break_sessions_completed = 0
        self.suggestion = "25:00"

        # Build GUI
        self.create_widgets()
        self.update_display()
        self.update_chart()
        self.update_controls()

    def create_widgets(self):
        self.session_label = ttk.Label(self.root, text="Study Session", font=("Arial", 20))
        self.session_label.pack(pady=5)

        self.time_label = ttk.Label(self.root, text="", font=("Arial", 48))
        self.time_label.pack(pady=10)

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=10)
        self.start_stop_button = ttk.Button(self.button_frame, text="Start", command=self.start_stop_timer)
        self.start_stop_button.pack(side="left", padx=5)
        self.pause_resume_button = ttk.Button(self.button_frame, text="Pause", command=self.pause_resume_timer)
        self.pause_resume_button.pack(side="left", padx=5)
        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.pack(side="left", padx=5)
        self.start_break_button = ttk.Button(self.button_frame, text="Start Break", command=self.start_break)
        self.start_break_button.pack(side="left", padx=5)

        ttk.Label(self.root, text="").pack(pady=5)
        chart_label = ttk.Label(self.root, text="Sessions Per Day (last 7 days)", font=("Arial", 14))
        chart_label.pack(pady=(10, 0))
        chart_frame = ttk.Frame(self.root)
        chart_frame.pack(pady=15)

        self.figure, self.ax = plt.subplots(figsize=(10, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.chart_widget = self.canvas.get_tk_widget()
        self.chart_widget.pack()
        self.suggestion_label = ttk.Label(self.root, text="Suggested Session: 25:00", font=("Arial", 12), foreground="purple")
        self.suggestion_label.pack(pady=10)

    def start_stop_timer(self):
        if not self.session_timer.running:
            self.session_timer.start()
            self.timer_paused = False
            self.countdown()
        else:
            self.session_timer.pause()
            self.timer_paused = False
        self.update_controls()

    def pause_resume_timer(self):
        if self.session_timer.running and not self.timer_paused:
            self.timer_paused = True
        elif self.session_timer.running and self.timer_paused:
            self.timer_paused = False
            self.countdown()
        self.update_controls()

    def reset_timer(self):
        # Only prompt if in study session and timer isn't at full or zero
        if (self.on_study and
            self.session_timer.remaining != self.session_timer.initial and
            self.session_timer.remaining != 0):

            minutes_completed = (self.session_timer.initial - self.session_timer.remaining) // 60
            response = messagebox.askyesno(
                "Partial Session",
                f"Count this as a completed study session?\n({minutes_completed} min completed)"
            )
            if response:
                self.on_session_end(manual=True)  # Record partial

        self.session_timer.reset()
        self.timer_paused = False
        self.update_display()
        self.update_controls()

    def start_break(self):
        self.session_timer = PomodoroTimer(self.break_duration)
        self.on_study = False
        self.update_display()
        self.update_controls()

    def countdown(self):
        if self.session_timer.running and not self.timer_paused and self.session_timer.remaining > 0:
            self.session_timer.tick()
            self.update_display()
            self.root.after(1000, self.countdown)
        elif self.session_timer.is_complete():
            self.session_timer.pause()
            self.timer_paused = False
            self.update_display()
            self.on_session_end()
            self.update_controls()

    def on_session_end(self, manual=False):
        threading.Thread(target=self.play_sound, daemon=True).start()
        if self.on_study:
            self.study_sessions_completed += 1
            finished_length = (
                self.session_timer.initial - self.session_timer.remaining
                if manual else self.session_timer.initial
            )
            add_session_for_today(self.session_history_by_day, finished_length)
            self.update_chart()
            if manual:
                messagebox.showinfo("Session Saved", f"Recorded {finished_length // 60} min as completed.")
            else:
                messagebox.showinfo("Time's up!", "Study session complete! Time for a break.")

            # *** Adaptive logic based only on today's sessions ***
            today_history = self.session_history_by_day.get(today_date(), [])
            new_suggestion = suggest_adaptive_interval(today_history)
            mins = new_suggestion // 60
            secs = new_suggestion % 60
            self.suggestion = f"{mins:02d}:{secs:02d}"
            self.suggestion_label.config(text=f"Suggested Session: {self.suggestion}")

            self.switch_session(False)
        else:
            self.break_sessions_completed += 1
            self.update_chart()
            messagebox.showinfo("Break over!", "Break time is over! Time to study again.")
            self.switch_session(True)

    def switch_session(self, to_study: bool):
        self.on_study = to_study
        duration = self.study_duration if self.on_study else self.break_duration
        self.session_timer = PomodoroTimer(duration)
        self.timer_paused = False
        self.update_display()
        self.update_controls()

    def play_sound(self):
        try:
            if os.path.exists("alert.wav"):
                playsound("alert.wav")
            else:
                print("\a")
        except Exception as e:
            print("Error playing sound:", e)

    def update_chart(self):
        self.ax.clear()
        today = datetime.date.today()
        weekday = today.weekday()  # Monday is 0
        monday = today - datetime.timedelta(days=weekday)
        days = [monday + datetime.timedelta(days=i) for i in range(7)]
        day_labels = [d.strftime('%a') for d in days]  # 'Mon', 'Tue', etc.
        values = [len(self.session_history_by_day.get(d.isoformat(), [])) for d in days]

       # Canvas settings
        self.ax.bar(day_labels, values, color='#4caf50')
        self.ax.set_ylabel("Sessions Completed", fontsize=12)
        self.ax.set_ylim(0, max(values + [1]))
        self.ax.tick_params(axis='x', labelrotation=45, labelsize=10)
        self.ax.tick_params(axis='y', labelsize=11)
        for i, v in enumerate(values):
            if v != 0:
                self.ax.text(i, v + 0.05, str(v), ha='center', fontweight='bold', fontsize=11)
        self.figure.tight_layout()
        self.canvas.draw()

    def update_display(self):
        minutes = self.session_timer.remaining // 60
        seconds = self.session_timer.remaining % 60
        self.time_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.session_label.config(text="Study Session" if self.on_study else "Break Time")

    def update_controls(self):
        if not self.session_timer.running:
            self.start_stop_button.config(text="Start")
            self.pause_resume_button.config(state="disabled")
        else:
            self.start_stop_button.config(text="Stop")
            self.pause_resume_button.config(state="normal")

        if self.session_timer.running:
            if not self.timer_paused:
                self.pause_resume_button.config(text="Pause")
            else:
                self.pause_resume_button.config(text="Resume")
        else:
            self.pause_resume_button.config(text="Pause")

        if self.on_study and not self.session_timer.running:
            self.start_break_button.config(state="normal")
        else:
            self.start_break_button.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTimerApp(root)
    root.mainloop()