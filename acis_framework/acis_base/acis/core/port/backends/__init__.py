#! /usr/bin/env python
# coding=utf-8


"""
"""

from .at  import AT
from .adb import ADB

class PortFactory():

    backends = {
        'AT' : AT,
        'ADB': ADB,
    }

    def __init__(self):

        self.records = {}
        self.port_obj = None

    def which_backend(self, backend_name, type_name, conf):

        print("backend_name is : <{}>".format(backend_name))
        if backend_name not in self.records.keys():
            print("first get object")
            self.port_obj = PortFactory.backends.get(backend_name)(type_name, conf)
            print("get object from factory : {}".format(self.port_obj))
            self.records[backend_name] = [type_name]
        else:
            print("re-init get object")
            self.port_obj.reinit(type_name,conf)
            self.records[backend_name].append(type_name)
        print("factory records: {}".format(self.records))
        return self.port_obj
