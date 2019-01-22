#! /usr/bin/env python
# coding=utf-8


"""
"""

from acis.utils.log import peer
import subprocess,os,signal
import threading,traceback
from datetime import datetime
from .at import _AT

class _ADB():

    name = '_ADB'

    def __init__(self, serial_id):

        self.serial_id = serial_id

        peer(self)

    def __killSubProcess(self, proc):
        proc.terminate()

    def __repr__(self):
       return "<Class: {name} , serial id: {conf}>".format(name = _ADB.name,conf=self.serial_id)

    def send_cmd(self, command, timeout=30):

        try:
            start_time = datetime.now()
            dt = datetime.now()
            timeDisplay =  "(%0.2d:%0.2d:%0.2d:%0.3d) Snd"%(dt.hour, dt.minute, dt.second, dt.microsecond/1000)

            cmd = 'adb -s %s %s' % (self.serial_id, command)
            peer(timeDisplay + " ADB " + self.serial_id + " ["+ cmd + "]")

            #p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines = True)
            # > 'exec ' + cmd can FIX the process kill issue
            p = subprocess.Popen("exec " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines = True)
            t = threading.Timer(timeout, self.__killSubProcess, args = (p,))
            t.start()

            output = p.communicate()[0]

            if command.strip() in ("shell init 6",
                                   "shell init 0",
                                   "shell \"poweroff\"",
                                   "reboot-bootloader",
                                   "reboot"):
                peer("framework hook <Module reboot> commands [{}]".format(command.strip()))
                _AT.objs[self.serial_id].close()

            try:
                if t is not None:
                    if t.isAlive():
                        peer("Terminate the monitoring process")
                        t.cancel()
                        peer("%s : Timer is cancelled" % datetime.now().strftime("%y/%m/%d %H:%M:%S"))
                    else:
                        peer("Monitoring process expired, actively kill the thread.")
                else:
                    peer("Timer NOT set.")
            except Exception as e:
                peer(e)
                traceback.print_exc()
                peer("---->Problem when terminating mornitor process !!!")

            timeDisplay =  "(%0.2d:%0.2d:%0.2d:%0.3d) Rcv"%(dt.hour, dt.minute, dt.second, dt.microsecond/1000)
            diff_time = datetime.now() - start_time
            diff_time_ms = diff_time.seconds * 1000 + diff_time.microseconds / 1000
            for each_line in output.split('\n'):
                peer(timeDisplay + " ADB "+ self.serial_id + " ["+ each_line.replace("\r","<CR>").replace("\n","<CR>") +"]"+" @"+str(diff_time_ms)+" ms ")
            return output
        except Exception as e:
            peer(e)
            peer("----->Problem: Exception comes up when send command !!!")
            return "\r\nERROR\r\n"

class ADB():

    name = 'ADB'

    def __init__(self, obj, conf):

        self.conf = {}

        if obj == "DUT1":
            self.conf["DUT1"] = conf
            self.DUT1 = _ADB(conf['serial_id'])
        elif obj == "DUT2":
            self.conf["DUT2"] = conf
            self.DUT2 = _ADB(conf['serial_id'])
        elif obj == "any":
            self.conf["any"] = conf
            self.any = _ADB(conf['serial_id'])

        self.info()

    def reinit(self, obj, conf):

        if obj == "DUT1":
            self.conf["DUT1"] = conf
            self.DUT1 = _ADB(conf['serial_id'])
        else:
            self.conf["DUT2"] = conf
            self.DUT2 = _ADB(conf['serial_id'])
        return self

    def info(self):
        peer("My name is : {name}\n- conf:\n{conf}".format(name = ADB.name, conf = self.conf))
