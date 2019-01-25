#! /usr/bin/env python
# coding=utf-8


"""
"""

from .conf import PI_SLAVE_CONF
from acis.utils.log import peer
from .port_exceptions import (UnsupportBackendErr,
                              ATdevLinkNotExist,
                              NotFindTypeNameInRule,
                              ATportBusyErr,
                              UnsupportTypeErr,
                              AcisRuleFileNotExist)
import os, re, subprocess
from random import choice


class PortConfParser():
    """
    A PortConfParser class, it's provide method to parse the port config.

    """

    def __init__(self):
        """
        PortConfParser constructor function, init necessary conditions

        Args:
            none

        Returns:
            none

        """

        self.configs = {}

        # any_conf = { "any" : 'DUT1' or 'DUT2' }
        self.any_conf = {}

        # ACIS udev-configuration Location
        self.udev_conf_file = '/etc/udev/rules.d/11-acis.rules'

        self._pick_info(self.udev_conf_file)

    def __narrow_config(self):
        """
        the method purpose to drop self.configs items that without in devices.

        Args:
            none

        Returns:
            none

        """
        try:
            output = subprocess.check_output('adb devices',
                                            shell = True).decode('utf-8').strip()
        except subprocess.CalledProcessError as err:
            raise err
        else:
            # devices = [ 'serial_id_1', 'serial_id_2', ...]
            devices = []
            for line in output.split('\n'):
                g = re.match('\s*?(.*)\s*device$', line)
                if g:
                    devices.append(g.group(1).strip())

            pop = []
            for i in self.configs:
                if self.configs[i]['serial'] not in devices:
                    pop.append(i)
            for item in pop:
                peer("Narrowing - Drop item: {}".format(self.configs.pop(item)))
            peer("Final <configs> : {}".format(self.configs))

    def _pick_info(self,_file):
        """
        The method to Pick some information from udev file

        'self.configs' content:
        eg.\n
        {
        "DUT1" : { "serial" : xxx,
                     "link"   : xxx, << acis/DUT1
                     "AT"     : xxx, << acis/DUT1/AT
                     "DM"     : xxx},<< acis/DUT1/DM

        "DUT2" : { "serial"  : xxx,
                     "link"   : xxx, << acis/DUT2
                     "AT"     : xxx, << acis/DUT2/AT
                     "DM"     : xxx},<< acis/DUT2/DM
        }

        Examples:
        _pick_info('/etc/udev/rules.d/11-acis.rules')

        Args:
            _file: the udev file you want to pick information

        Returns:
            none.
        """
        if not os.path.exists(_file): raise AcisRuleFileNotExist()

        with open(_file, mode = 'r') as f:
            for line in f:
                g = re.match(r'\s*ATTRS{serial}=="(.*)",\s*GOTO="(.*)\s*"', line)
                if g:
                    if g.group(2) == "acis_DUT1":
                        self.configs["DUT1"] = {"serial" : g.group(1) }
                    elif g.group(2) == "acis_DUT2":
                        self.configs["DUT2"]  = {"serial" : g.group(1) }
                g = re.match(r"\s*SUBSYSTEMS==\"usb\",\s*DRIVERS==\"GobiSerial\",\s*SYMLINK\+=\"(acis/(.*))/(.*)\",\s*ATTRS{bInterfaceNumber}==\"(.*)\"\s*", line)
                if g:
                    if g.group(2) == "DUT1":
                        self.configs["DUT1"]["link"] = g.group(1)
                        if g.group(4) == "03":
                            self.configs["DUT1"]["AT"] = g.group(1) + '/' + g.group(3)
                        if g.group(4) == "00":
                            self.configs["DUT1"]["DM"] = g.group(1) + '/' + g.group(3)
                    elif g.group(2) == "DUT2" :
                        self.configs["DUT2"]["link"]  = g.group(1)
                        if g.group(4) == "03":
                            self.configs["DUT2"]["AT"] = g.group(1) + '/' + g.group(3)
                        if g.group(4) == "00":
                            self.configs["DUT2"]["DM"] = g.group(1) + '/' + g.group(3)

        peer("<Rules> configs: {}".format(self.configs))
        self.__narrow_config()

    def get_conf(self, backend_name, type_name):
        """
        The method to get the port object config.

        Examples:
        get_conf("AT", "DUT1")

        Args:
            backend_name: The port name(AT/adb).
            type_name: The DUT name(DUT1/DUT2/any)

        Returns:
            return the port object config.
            Examples:   'type_name' : >> 'DUT1' or 'DUT2' or 'any' \n
                        'mapto'     : >> only 'any' has this prop. \n
                        'backend'   : >> 'AT' or 'ADB' \n
                        'dev_link'  : >> eg: AT > /dev/acis/DUT1/AT \n
                        'serial_id' : >> adb serial id.
        """
        if type_name == "DUT1":

            if "DUT1" not in self.configs:
                raise NotFindTypeNameInRule("Can NOT find type name <{}> in udev-rules file.".format(type_name))

            if backend_name == "AT":
                if not subprocess.call("lsof {where}".format(where = '/dev/' + self.configs[type_name][backend_name]), shell=True):
                    raise ATportBusyErr("AT port is using.")
                if subprocess.call('ls {where}'.format(where = '/dev/' + self.configs[type_name][backend_name]), shell=True):
                    raise ATdevLinkNotExist("Can NOT find dev-link [{}] for test.".format('/dev/'+self.configs[type_name][backend_name]))
                return { 'type_name' : type_name,
                         'mapto'     : type_name,
                         'backend'   : backend_name,
                         'dev_link'  : '/dev/' + self.configs[type_name][backend_name],
                         'serial_id' : self.configs[type_name]["serial"]}
            elif backend_name == "DM":
                raise UnsupportBackendErr("NOT support backend <{backend}>.".format(backend = backend_name))
            elif backend_name == "ADB":
                return { 'type_name' : type_name,
                         'mapto'     : type_name,
                         'backend'   : backend_name,
                         'serial_id' : self.configs[type_name]["serial"]}

        elif type_name == "DUT2":

            if "DUT2" not in self.configs:
                raise NotFindTypeNameInRule("Can NOT find type name <{}> in udev-rules file.".format(type_name))

            if backend_name == "AT":
                if not subprocess.call("lsof {where}".format(where = '/dev/' + self.configs[type_name][backend_name]), shell=True):
                    raise ATportBusyErr("AT port is using.")
                if subprocess.call('ls {where}'.format(where = '/dev/' + self.configs[type_name][backend_name]), shell=True):
                    raise ATdevLinkNotExist("Can NOT find dev-link [{}] for test.".format('/dev/'+self.configs[type_name][backend_name]))
                return { 'type_name' : type_name,
                         'mapto'     : type_name,
                         'backend'   : backend_name,
                         'dev_link'  : '/dev/' + self.configs[type_name][backend_name],
                         'serial_id' : self.configs[type_name]["serial"]}
            elif backend_name == "DM":
                raise UnsupportBackendErr("NOT support backend <{backend}>.".format(backend = backend_name))
            elif backend_name == "ADB":
                return { 'type_name' : type_name,
                         'mapto'     : type_name,
                         'backend'   : backend_name,
                         'serial_id' : self.configs[type_name]["serial"]}

        elif type_name == "any":

            if not self.configs:
                raise NotFindTypeNameInRule("Can NOT find any type names <DUT2 or DUT1> in udev-rules file.")

            if len(self.configs) == 2:

                if backend_name == "AT":
                    sel = choice(["DUT1", "DUT2"])
                    peer("First get type is {name}".format(name = sel))
                    if not subprocess.call("lsof {where}".format(where = '/dev/' + self.configs[sel][backend_name]), shell=True):
                        peer("Port Busy! Try another...")
                        for another in ["DUT1", "DUT2"]:
                            if sel != another:
                                if not subprocess.call("lsof {where}".format(where = '/dev/' + self.configs[another][backend_name]), shell=True):
                                    raise ATportBusyErr("Double AT ports had been using.")
                                else:
                                    if subprocess.call('ls {where}'.format(where = '/dev/' + self.configs[sel][backend_name]), shell=True):
                                        raise ATdevLinkNotExist("Can NOT find dev-link [{}] for test.".format('/dev/'+self.configs[sel][backend_name]))
                                    self.any_conf[type_name] = another
                                    return { 'type_name' : type_name,
                                            'mapto'      : self.any_conf[type_name],
                                            'backend'    : backend_name,
                                            'dev_link'   : '/dev/' + self.configs[self.any_conf[type_name]][backend_name],
                                            'serial_id'  : self.configs[self.any_conf[type_name]]["serial"]}
                    else:
                        if subprocess.call('ls {where}'.format(where = '/dev/' + self.configs[sel][backend_name]), shell=True):
                            raise ATdevLinkNotExist("Can NOT find dev-link [{}] for test.".format('/dev/'+self.configs[sel][backend_name]))
                        self.any_conf[type_name] = sel
                        return {'type_name' : type_name,
                                'mapto'     : self.any_conf[type_name],
                                'backend'   : backend_name,
                                'dev_link'  : '/dev/' + self.configs[self.any_conf[type_name]][backend_name],
                                'serial_id' : self.configs[self.any_conf[type_name]]["serial"]}

                elif backend_name == "DM":
                    raise UnsupportBackendErr("NOT support backend <{backend}>.".format(backend = backend_name))

                elif backend_name == "ADB":
                    return {'type_name' : type_name,
                            'mapto'     : self.any_conf[type_name],
                            'backend'   : backend_name,
                            'serial_id' : self.configs[self.any_conf[type_name]]["serial"]}

            elif len(self.configs) == 1:
                if 'DUT1' in self.configs:
                    if backend_name == "AT":
                        sel = 'DUT1'
                        if not subprocess.call("lsof {where}".format(where = '/dev/' + self.configs[sel][backend_name]), shell=True):
                            raise ATportBusyErr("Only one module register to udev-rules: <{name}>, but this port is using.".format(name = sel))
                        else:
                            if subprocess.call('ls {where}'.format(where = '/dev/' + self.configs[sel][backend_name]), shell=True):
                                raise ATdevLinkNotExist("Can NOT find dev-link [{}] for test.".format('/dev/'+self.configs[sel][backend_name]))
                            self.any_conf[type_name] = sel
                            return { 'type_name'  : type_name,
                                     'mapto'      : self.any_conf[type_name],
                                     'backend'    : backend_name,
                                     'dev_link'   : '/dev/' + self.configs[self.any_conf[type_name]][backend_name],
                                     'serial_id'  : self.configs[self.any_conf[type_name]]["serial"]}

                    elif backend_name == "DM":
                        raise UnsupportBackendErr("NOT support backend <{backend}>.".format(backend = backend_name))

                    elif backend_name == "ADB":
                        return {'type_name' : type_name,
                                'mapto'     : self.any_conf[type_name],
                                'backend'   : backend_name,
                                'serial_id' : self.configs[self.any_conf[type_name]]["serial"]}

                elif 'DUT2' in self.configs:

                    if backend_name == "AT":
                        sel = 'DUT2'
                        if not subprocess.call("lsof {where}".format(where = '/dev/' + self.configs[sel][backend_name]), shell=True):
                            raise ATportBusyErr("Only one module register to udev-rules: <{name}>, but this port is using.".format(name = sel))
                        else:
                            if subprocess.call('ls {where}'.format(where = '/dev/' + self.configs[sel][backend_name]), shell=True):
                                raise ATdevLinkNotExist("Can NOT find dev-link [{}] for test.".format('/dev/'+self.configs[sel][backend_name]))
                            self.any_conf[type_name] = sel
                            return { 'type_name'  : type_name,
                                     'mapto'      : self.any_conf[type_name],
                                     'backend'    : backend_name,
                                     'dev_link'   : '/dev/' + self.configs[self.any_conf[type_name]][backend_name],
                                     'serial_id'  : self.configs[self.any_conf[type_name]]["serial"]}

                    elif backend_name == "DM":
                        raise UnsupportBackendErr("NOT support backend <{backend}>.".format(backend = backend_name))

                    elif backend_name == "ADB":
                        return {'type_name' : type_name,
                                'mapto'     : self.any_conf[type_name],
                                'backend'   : backend_name,
                                'serial_id' : self.configs[self.any_conf[type_name]]["serial"]}

        else:
            raise UnsupportTypeErr("This type that your input [{}] is NOT support now.".format(type_name))
