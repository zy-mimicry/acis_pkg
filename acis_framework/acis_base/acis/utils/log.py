#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import logging
import logging.config
import os, time

# You can overwrite this environment argument.
if not os.getenv("ACIS_SYS_LOG", ""):
    diff = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    log_path = "/tmp/acis/logs/" + diff
    if not os.path.exists(log_path):
        os.makedirs(log_path , 0o755)
        os.environ["ACIS_SYS_LOG"] = log_path
    else:
        os.environ["ACIS_SYS_LOG"] = log_path

DEFAULT_LOGGING = {
    'version' : 1,
    'disable_existing_loggers' : False,

    # TBD. Maybe useful
    # 'filters' : {},

    'formatters' : {
        'verbose' : {
            'format' : "[{levelname}] [{asctime}] [{module}] [{process:d}] [{thread:d}] | {message}",
            'style' : "{",

        },
        'simple' : {
            'format' : "[{asctime}] [{module}] | {message}",
            'style' : "{",
        },

    },
    'handlers' : {
        'console' : {
            'level' : "INFO",
            'class' : "logging.StreamHandler",
            'formatter' : "simple",
        },
        'developer_file' : {
            'level' : "INFO",
            'class' : "logging.FileHandler",
            'filename' : os.environ["ACIS_SYS_LOG"] + "/case_debug.log",
            'formatter' : 'simple',
            'mode' : 'w',
        },
        'core_file' : {
            'level' : "DEBUG",
            'class' : "logging.FileHandler",
            'filename' : os.environ["ACIS_SYS_LOG"] + "/admin_peer.log",
            'formatter' : 'verbose',
            'mode' : 'w',
        },
    },
    'loggers' : {
        'admin' : {
            'handlers' : ["core_file"],
            #'handlers' : ["console", "core_file"],
            'level' : "DEBUG",
            'propagate' : True,
        },
        'developer' : {
            'handlers' : ["console", "developer_file"],
            'level' : "INFO",
        }
    }
}


class Peer:
    """"""
    def __init__(self, logger_name):
        logging.config.dictConfig(DEFAULT_LOGGING)
        self.logger = logging.getLogger(logger_name)

    def __call__(self,*kargs, **kwargs):
        self.logger.error(*kargs, **kwargs)
        from acis import hook_log
        if hook_log: hook_log(*kargs, **kwargs)

class Log:
    """"""
    def __init__(self,
                 log_path,
                 logger_name = 'acis.testcase.debug',
                 log_level = logging.DEBUG,
                 log_format = "%(asctime)s |  %(message)s"):
                 #log_format = "%(asctime)s - %(filename)s[line:%(lineno)d] : %(message)s"):

        print("<logger name :{}>".format(logger_name))
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path), mode=0o775)
        self.logger = logging.getLogger(logger_name)
        ch1 = logging.StreamHandler()
        ch2 = logging.FileHandler(log_path)
        formatter = logging.Formatter(log_format)
        ch1.setLevel(log_level)
        ch2.setLevel(log_level)
        ch1.setFormatter(formatter)
        ch2.setFormatter(formatter)
        self.logger.addHandler(ch1)
        self.logger.addHandler(ch2)

    def __call__(self, *kargs, **kwargs):
        return self.logger.error(*kargs, **kwargs)

peer = Peer("admin")
