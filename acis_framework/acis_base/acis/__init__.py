#! /usr/bin/env python
# coding=utf-8

"""
pytest version == 3.7.1
allure version == 2.5.0
"""

from acis.utils.log import Log,peer
from acis.core.port import Port
import os, re

hook_log = None

class ACISMiscer():
    """
    """

    def __init__(self):


        self.limit_name = 'testcases' # Maybe get this var from environment better.

        try:
            self.prefix = os.environ["REPORT_PATH"] + '/' \
                + os.environ["PLATFORM"] + '/' \
                + os.environ["ACIS_DIFF"]
        except KeyError as e:
            peer("Can't get vaild environments from master. \nStack info: \n<{}>.\nSo switch to default branch.".format(e))
            if not os.path.exists('/tmp/acis/testlog/' + self.limit_name):
                os.makedirs('/tmp/acis/testlog/' + self.limit_name, mode = 0o744)
            self.prefix = '/tmp/acis/testlog'

        self.at  = None
        self.adb = None

        self.envs = {}

    def deal_log_path(self, case_file):

        dname,fname = os.path.split(case_file)
        dname = dname.split(self.limit_name + '/')[1]
        mprefix = self.prefix + '/' + self.limit_name + '/' + dname + '/'
        self.which_log = mprefix + fname.replace('.py', '.log')
        self.case_output = mprefix + fname.replace('.py', '')
        if not os.path.exists(self.case_output):
            os.makedirs(self.case_output, mode=0o755)
        peer("Case Log Location: {}".format(self.which_log))
        return self.which_log

    def deal_envs(self):
        """
        Deal Environments after 'deal_log_path'.
        """

        self.envs['Test_Date']  = os.environ['ACIS_DIFF']
        self.envs['Test_Times'] = os.environ['TIMES']

        filesvr_url = 'http://cnshz-ed-svr098/ACIS-IntegrationTest-Reports/' # end of '/'
        replace_from = 'log_and_report'
        log_path_slice = self.which_log.split('/')

        reversed_log_path_slice = list(reversed(log_path_slice))
        reversed_partial_slice  = reversed_log_path_slice[:reversed_log_path_slice.index(replace_from)]
        partial_slice = list(reversed(reversed_partial_slice))
        self.envs['Test_Log'] = filesvr_url + '/'.join(partial_slice)

        diff_location = partial_slice.index(os.environ['ACIS_DIFF']) + 1
        report_suffix = '/' + os.environ['ACIS_DIFF'] + '_report'
        self.envs['Test_IR_Report'] = filesvr_url + '/'.join(partial_slice[:diff_location]) + report_suffix


    def deal_misc(self, log_file, logger_name, port_names, mail_to = "SWI@sierrawireless.com"):

        global hook_log
        hook_log = self.log = Log(self.deal_log_path(log_file), logger_name = logger_name)
        self.mMail = self.register_mail(mail_to)
        self.register_port(port_names)
        import acis.conf.tc_conf as tc
        self.conf = tc
        self.deal_envs()
        return self


    def register_mail(self, mail_to):
        peer("[Mail] From: {}".format(mail_to))

    def order_port_list(self,port_names):
        """
        Note: the order of ports register is important!
        At port should be in front.
        """
        AT_front = []
        other_behind = []

        for p in port_names:
            if re.search('AT..', p):
                AT_front.append(p)
            else:
                other_behind.append(p)
        AT_front.extend(other_behind)
        return AT_front

    def register_port(self, port_names):

        self.mPort = Port()
        port_names = self.order_port_list(port_names)

        for backend_cookie in port_names:
            peer("\n\n Loop is <{}>".format(backend_cookie))
            backend = self.mPort.match(backend_cookie)

            if backend.name == 'AT':
                self.at = backend
            elif backend.name == "ADB":
                self.adb = backend
            else:
                pass

# import os,re
# from pprint import pprint as pp


# def get_log_files(path):

#     if not os.path.isdir(path):
#         raise TypeError

#     log_files = []
#     for root, dirs, files in os.walk(path):
#         [log_files.append(os.path.join(root, f)) for f in files if f.startswith('ACIS') and f.endswith('.log')]
#     return log_files

# def get_element(files):
#     """
#     Element:
#     - TESTCASE - Result - Test_Date - Test_Times - Test_Log - Test_IR_Report

#     - Platform - FW_version - PASS_TIMES - FAIL_TIMES
#     """
#     record = {}

#     re_g = {
#         'testcase'       : 1,
#         'result'         : 2,
#         'test_date'      : 3,
#         'test_times'     : 4,
#         'test_log'       : 5,
#         'test_ir_report' : 6,

#         'product'        : 1,
#         'fw_version'     : 2,
#     }

#     platform_maps = {
#         '9X28' : ('AR7588',),
#         '9X40' : ('AR7598',),
#     }

#     re_SWI_ACIS = re.compile(r'TESTCASE:\[(.*?)\]\sResult:\[(.*?)\]\sTest_Date:\[(.*?)\]\sTest_Times:\[(.*?)\]\sTest_Log:\[(.*?)\]\sTest_IR_Report:\[(.*?)\]')
#     re_AT_ATI = re.compile(r'\[Model: (.*)<CR><LF>Revision: (.*?)\s')

#     for f in files:
#         record[f] = {}
#         last_one_touch = False
#         once_flag      = False

#         pass_times = 0
#         fail_times = 0

#         for line in reversed(list(open(f))):
#             if line.startswith('<SWI:ACIS>'):

#                 gs = re_SWI_ACIS.search(line)

#                 if gs and gs.group(re_g['result']) == 'PASS':
#                     pass_times += 1
#                 elif gs and gs.group(re_g['result']) == 'FAIL':
#                     fail_times += 1

#                 if gs and not last_one_touch:
#                     print("hook?")
#                     record[f]['TESTCASE'] = gs.group(re_g['testcase'])
#                     record[f]['Result']   = gs.group(re_g['result'])
#                     record[f]['Test_Date']  = gs.group(re_g['test_date'])
#                     record[f]['Test_Times'] = gs.group(re_g['test_times'])
#                     record[f]['Test_Log']   = gs.group(re_g['test_log'])
#                     record[f]['IR_Report_Path'] = gs.group(re_g['test_ir_report'])
#                     last_one_touch = True

#             rs = re_AT_ATI.search(line)

#             if rs and not once_flag:
#                 for platform, products in platform_maps.items():
#                     if rs.group(re_g['product']) in products:
#                         record[f]['Platform'] = platform

#                 record[f]['FW_version'] = rs.group(re_g['fw_version'])

#                 once_flag = True

#         record[f]['PASS_TIMES'] = pass_times
#         record[f]['FAIL_TIMES'] = fail_times

#     return record


# if __name__ == "__main__":

#     obj_dir = './2019_01_19_11_47_30'
#     files = get_log_files(obj_dir)
#     record = get_element(files)
#     pp(record)
