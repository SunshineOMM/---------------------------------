import threading
import time
from datetime import datetime
import system_for_selecting_and_analyzing_actions.leaner as leaner

class repeated_timer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self.timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self.timer = threading.Timer(self.next_call - time.time(), self.run)
      self.timer.start()
      self.is_running = True

  def stop(self):
    self.timer.cancel()
    self.is_running = False


def alarm():
    leaner.daily_calendar_crawl()
    print(f"chek :{datetime.now()}")


# print("starting...")
# rt = RepeatedTimer(60, alarm)