#! /usr/bin/env python
# coding=utf-8

"""
"""

from acis.utils.log import peer
from .parser import PortConfParser
from .backends import PortFactory

class Port:

    def __init__(self):

        self.parser  = PortConfParser()
        self.factory = PortFactory()

        self.at  = None
        self.adb = None

    def name_split(self, aka_name):
        return tuple([n.strip() for n in aka_name.split('..')])

    def match(self, aka_name):
        backend_name, type_name = self.name_split(aka_name)

        backend_name = backend_name.upper()
        if type_name != 'any':
            type_name    = type_name.upper()

        conf = self.parser.get_conf(backend_name, type_name)

        peer(conf)

        if backend_name == "AT":
            self.at = self.factory.which_backend(backend_name, type_name, conf)
            return self.at

        elif backend_name == "ADB":
            self.adb = self.factory.which_backend(backend_name, type_name, conf)
            return self.adb
        # else:
        #     from .port_exceptions import (UnsupportBackendErr)
        #     raise UnsupportBackendErr("NOT support backend <{backend}>.".format(backend = backend_name))
