# Single loop app that logs time

import time
import datetime
import signal

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, signum, frame):
    self.kill_now = True

def job():
    killer = GracefulKiller()
    while not killer.kill_now:
        now = datetime.datetime.now()
        print(f'Job running {now.strftime("%Y-%m-%d %H:%M:%S")}')    
        time.sleep(1)
    print("Job exited gracefully")


if __name__ == "__main__":
    job()