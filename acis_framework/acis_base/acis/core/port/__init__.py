#! /usr/bin/env python
# coding=utf-8

"""
"""

from acis.utils.log import peer
from .parser import PortConfParser
from .backends import PortFactory

class Port:
    """
    An port class, it's provide method to parse and get port obj.

    """
    def __init__(self):
        """
        The Port class constructor function, init necessary conditions

        Args:
            none

        Returns:
            none
        """

        self.parser  = PortConfParser()
        self.factory = PortFactory()

        self.at  = None
        self.adb = None

    def name_split(self, aka_name):
        """
        The method to split the port object string.

        Examples:
        name_split("AT..DUT1")

        Args:
            aka_name: The port object string you want to split

        Returns:
            return the splited tuple.
        """
        return tuple([n.strip() for n in aka_name.split('..')])

    def match(self, aka_name):
        """
        The method to match the port object.

        Examples:
        match("AT..DUT1")

        Args:
            aka_name: The port object you want to match

        Returns:
            return the matched port object(adb/AT).
        """
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
