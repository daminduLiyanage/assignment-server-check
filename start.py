#!/usr/bin/env python
import time
import threading
import schedule
import task
import task2
import create_empty_bucket_log

RUN_JOB_TWO_AT = "17:20"
# Every 2 hours
RUN_JOB_ONE_EVERY = 60*60*2 
# 40 s
WAIT_BEFORE_JOB_TWO = 40

# ------------------------------------------------------------------------
def run_continuously(interval=1):
    # --------------------------------------------------------------------
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)
    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

# ------------------------------------------------------------------------
def job_one():
    # --------------------------------------------------------------------
    task.main()

# ------------------------------------------------------------------------
def job_two():
    # --------------------------------------------------------------------
    task2.main()
    
try:
    print("[!] Starting the tasks..")
    create_empty_bucket_log.main()
    # job 1 bootstraps server if not running
    job_one()
    time.sleep(WAIT_BEFORE_JOB_TWO)
    # repeat job 2
    schedule.every().day.at(RUN_JOB_TWO_AT).do(job_two)
    stop_run_continuously = run_continuously()
    # repeat job 1
    while True:
        job_one()
        time.sleep(RUN_JOB_ONE_EVERY)
except KeyboardInterrupt:
    print ("[!] Keyboard inturruption occured. Exiting the program..")