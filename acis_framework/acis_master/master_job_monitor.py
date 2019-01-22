#! /usr/bin/env python3
# coding=utf-8

"""
TODO:
 - 1. Monitor should be able to cancel the job that stay in 'stuck' status.

 - 2. Monitor shoulb be able to trace every job and trigger timer for tracing it,
      if job timeout, cancel it.
"""

from jenkins import Jenkins
import time

class JenkinsJobMonitor():
    def __init__(self, url, username, password, *args, **argvs):
        self._attach_server(url, username, password, *args, **argvs)

    def _attach_server(self, url, username, password,*args, **argvs):
        self.server = Jenkins(url = url, username = username, password = password, *args, **argvs)

    def _is_stuck(self, item):
        if item['pending'] == False and item['stuck'] == True:
            print("Cancel 'stuck' job [name : {name}] [id : {job_id} [why: {why}]]".format(
                name = item['task']['name'],
                job_id = item['id'],
                why = item['why']))
            return True
        else:
            return False

    def _cancel_jobs(self, build_id):
        self.server.cancel_queue(build_id)

    def cancel_stuck_jobs(self):
        if self.server.get_queue_info():
            for item in self.server.get_queue_info():
                if self._is_stuck(item):
                    self._cancel_jobs(item['id'])
        else:
            self.poll_flag = False

    def _is_timeout(self):
        pass

    def cancel_timeout_jobs(self):
        pass

    def poll_stuck(self):
        self.poll_flag = True
        while self.poll_flag:
            time.sleep(10) # Timer maybe better.
            self.cancel_stuck_jobs()

    def poll_timeout(self):
        pass

if __name__ == "__main__":
    jm = JenkinsJobMonitor(url = "http://10.22.52.211:8080",
                           username = 'mzpython',
                           password = '123')
    jm.poll_stuck()
