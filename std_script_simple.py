# -*- coding: utf-8 -*-
# @Time    : 2018/9/15 14:23
# @Author  : wonderstone
# @FileName: std_script_simple.py
# @Software: PyCharm
# @Ref     :


import datetime
import os
import random
import sys
import time

from apscheduler.events import *
from apscheduler.schedulers.background import BackgroundScheduler


# from apscheduler.schedulers.blocking import BlockingScheduler


class ApsJob:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        # self.scheduler = BlockingScheduler()

    def job(self):
        print(datetime.datetime.now())
        if random.randint(1, 10) > 5:
            raise Exception

    def my_listener(self, event):
        if event.exception:
            msg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Job function Crashed !'

            print(msg)
            self.scheduler.pause_job('my_job_id')
            self.scheduler.remove_job('my_job_id')
            self.scheduler.shutdown(wait=False)
            os._exit(os.EX_OK)
            # os.abort()
            # sys.exit("Some exception happened. Exit!")
        else:
            msg = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Job Done !'
            print(msg)


if __name__ == "__main__":

    aps_job = ApsJob()
    aps_job.scheduler.add_job(aps_job.job, 'interval', seconds=5, id='my_job_id')
    aps_job.scheduler.add_listener(aps_job.my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    aps_job.scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        #
        # aps_job = ApsJob()
        # aps_job.scheduler.add_job(aps_job.job, 'interval', seconds=5,id='my_job_id')
        # aps_job.scheduler.add_listener(aps_job.my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        # aps_job.scheduler.start()
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(5)
    except (Exception, KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        aps_job.scheduler.shutdown()
        sys.exit("Some exception happened. Exit!")
