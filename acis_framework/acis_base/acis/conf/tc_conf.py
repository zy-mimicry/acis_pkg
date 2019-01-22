#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TODO:

1. Read file context to this module.
2. Join the 'INI_PATH' to strings from file.
3. execute string and make it to be a module.

Note: If you want to know what contains in this module, please check the 'acis_testcases.cfg' file.

"""

import os,configparser
from acis.utils.log import peer

if os.getenv('TESTCASE_CFG', None) == None:
    if os.getenv('JOB_NAME',None) is None:
        # Now, we hope default.
        os.environ['TESTCASE_CFG'] = '/home/jenkins/nfs_acis/Integration_Test/acis_testcases/acis_testcases.cfg'
    else:
        if os.getenv('USER_NAME') is None:
            os.environ['TESTCASE_CFG'] = '/home/jenkins/nfs_acis/' + os.environ['JOB_NAME'].rsplit('_', maxsplit=1)[0] + '/acis_testcases/acis_testcases.cfg'
        else:
            os.environ['TESTCASE_CFG'] = '/home/jenkins/nfs_acis/' + os.environ['JOB_NAME'] + '/' + os.environ['USER_NAME'] +'/acis_testcases/acis_testcases.cfg'


cfile = open(os.environ['TESTCASE_CFG'], 'r')
strings = cfile.read().replace('\\', '/')
cfile.close()

strings = strings.format(INI_PATH = os.path.dirname(os.environ['TESTCASE_CFG']))

exec(compile(strings, 'tc_conf', 'exec'))

def get_ini_value ( file_path, sections, name ):
    if os.path.isfile(file_path):
        peer("\nRead %s:%s from %s\n" % ( sections, name, file_path ))
        Parser = configparser.RawConfigParser()
        found = Parser.read(file_path)
        if not Parser.has_section(sections):
            peer("\nNo Section %s in %s  !!!" % ( str(sections), file_path ))
        if not Parser.has_option(sections, name):
            peer("\nNo Name %s udner %s in %s  !!!" % ( name, str(sections), file_path ))

        Parser = configparser.ConfigParser()
        found = Parser.read(file_path)
        value = Parser.get(sections, name)
        return value.strip("\"'")
    else:
        peer("\%s NOT exits !!!\n" % file_path)
        return ''

del strings
del cfile

