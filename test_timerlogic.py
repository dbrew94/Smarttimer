import unittest
import os
import json
from timerlogic import PomodoroTimer, suggest_adaptive_interval

SESSION_DATA_FILE = "session_history_test.json"

def save_sessions_test(session_history):
    with open(SESSION_DATA_FILE, "w") as f:
        json.dump(session_history, f)

def load_sessions_test():
    try:
        with open(SESSION_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

class TestPomodoroTimer(unittest.TestCase):
    def setUp(self):
        print(f"\n=== {self._testMethodName} ===")

    def test_timer_starts_and_ticks_down(self):
        timer = PomodoroTimer(5)
        timer.start()
        for _ in range(3):
            timer.tick()
        self.assertEqual(timer.remaining, 2)
        self.assertTrue(timer.running) #Passed result
        print("Completed: test_timer_starts_and_ticks_down")

    def test_timer_stops_at_zero(self):
        timer = PomodoroTimer(2)
        timer.start()
        timer.tick()
        timer.tick()
        self.assertEqual(timer.remaining, 0)
        #self.assertTrue(timer.running) #Failed method
        self.assertFalse(timer.running) #Passed result
        self.assertTrue(timer.is_complete())
        print("Completed: test_timer_stops_at_zero")

    def test_reset_brings_timer_to_initial_state(self):
        timer = PomodoroTimer(7) #Passed Result
        #timer = PomodoroTimer(0) #failed method
        timer.start()
        timer.tick()
        timer.reset()
        self.assertEqual(timer.remaining, 7)
        self.assertFalse(timer.running)
        print("Completed: test_reset_brings_timer_to_initial_state")

    def test_pausing_and_resuming(self):
        timer = PomodoroTimer(5)
        timer.start()
        timer.tick()
        timer.pause()
        timer.tick()
        self.assertEqual(timer.remaining, 4)
        #self.assertTrue(timer.running) #failing method
        self.assertFalse(timer.running) #Passing method
        timer.start()
        timer.tick()
        self.assertEqual(timer.remaining, 3)
        self.assertTrue(timer.running)
        print("Completed: test_pausing_and_resuming")

class TestSuggestAdaptiveInterval(unittest.TestCase):
    def setUp(self):
        print(f"\n=== {self._testMethodName} ===")

    def test_suggest_default_when_history_empty(self):
        #self.assertEqual(suggest_adaptive_interval([]), 5 * 60) #failed method
        self.assertEqual(suggest_adaptive_interval([]), 25*60) #Passing method
        print("Completed: test_suggest_default_when_history_empty")

    def test_suggest_shorter_for_short_sessions(self):
        history = [10*60, 13*60, 11*60] #failed method
        suggestion = suggest_adaptive_interval(history)
        self.assertTrue(suggestion < 25*60)
        self.assertGreaterEqual(suggestion, 10*60)
        print("Completed: test_suggest_shorter_for_short_sessions")

    def test_suggest_longer_for_long_sessions(self):
        history = [32*60, 35*60, 40*60]
        suggestion = suggest_adaptive_interval(history)
        #self.assertTrue(suggestion > 65 * 60) #failing method
        self.assertTrue(suggestion > 25*60) #Passing method
        self.assertLessEqual(suggestion, 60*60)
        print("Completed: test_suggest_longer_for_long_sessions")

    def test_suggest_capped_at_one_hour(self):
        history = [70*60, 90*60, 100*60]
        suggestion = suggest_adaptive_interval(history)
        #self.assertEqual(suggestion, 70 * 60) #failing method
        self.assertEqual(suggestion, 60*60) #Passing method
        print("Completed: test_suggest_capped_at_one_hour")

    def test_suggest_default_for_regular_sessions(self):
        history = [25*60, 27*60, 24*60]
        suggestion = suggest_adaptive_interval(history)
        #self.assertEqual(suggestion, 30 * 60) #failing method
        self.assertEqual(suggestion, 25*60) #Passing method
        print("Completed: test_suggest_default_for_regular_sessions")

class TestSessionHistoryPersistence(unittest.TestCase):
    def setUp(self):
        print(f"\n=== {self._testMethodName} ===")
    def tearDown(self):
        try:
            os.remove(SESSION_DATA_FILE)
        except (FileNotFoundError, PermissionError):
            pass

    def test_save_and_load_sessions(self):
        #history =  #Failing method
        history = [25*60, 20*60] #Passing method
        save_sessions_test(history)
        loaded = load_sessions_test()
        self.assertEqual(loaded, history)
        print("Completed: test_save_and_load_sessions")

    def test_load_empty_file_returns_empty_list(self):
        loaded = load_sessions_test()
        #self.assertEqual(loaded, [1]) #failed method
        self.assertEqual(loaded, []) #Passing method
        print("Completed: test_load_empty_file_returns_empty_list")

if __name__ == "__main__":
    unittest.main()