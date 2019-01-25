#! /usr/bin/env python
# coding=utf-8


"""
"""

from .at  import AT
from .adb import ADB

class PortFactory():
    """
    An PortFactory class, it's provide method to hook port backend
    """

    backends = {
        'AT' : AT,
        'ADB': ADB,
    }

    def __init__(self):
        """
        The PortFactory class constructor function

        Args:
            none

        Returns:
            none
        """

        self.records = {}
        self.port_obj = None

    def which_backend(self, backend_name, type_name, conf):
        """
        The method to hook the port backend and get the port object.

        Examples:
        which_backend("AT", "DUT1", conf)

        Args:
            backend_name: The port name(AT/adb).
            type_name: The DUT name(DUT1/DUT2/any)
            conf: the config of the port

        Returns:
            return the port object.
        """
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
