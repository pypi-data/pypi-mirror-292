import datetime
import time


class Timer:
    start: float

    def __init__(self):
        self.start = time.process_time() * 1000

    def stop(self):
        end = time.process_time() * 1000
        dur = end - self.start
        return dur

    def seq_stop(self):
        self.start = time.process_time() * 1000
        return self.stop()
