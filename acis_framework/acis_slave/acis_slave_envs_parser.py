#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
@author: Shawn Wu
@contact: shwu@sierrawireless.com
@file : acis_slave_envs_parser.py
@time: 2018/10/30 17:06
"""

import os

# parse the string like UART1_COM=r'/dev/ttyUSB1'
# for UART1_COM=r'/dev/ttyUSB1', key is UART1_COM, value is r'/dev/ttyUSB1'
# def parse_key_and_value(key_value_string):
#     key_value_dict = {}
    
#     if key_value_string:
#         for i in range(len(key_value_string)):
#             index = key_value_string[i].find("=")
#             string_len = len(key_value_string[i])
#             key_value_dict[key_value_string[i][0:index]] = key_value_string[i][index + 1 : string_len]
    
#     return key_value_dict


# def get_bool_value(name):
#     bool_value = os.getenv(name)
#     if "true" == bool_value:
#         return True
#     else:
#         return False

class Slave_envs_parser:
    # Get test case list
    def get_test_case_list(self):
        return os.environ["CASENAME"]

    # Get test count for each test case
    def get_test_count(self):
        test_count = int(os.environ["TIMES"])
        return test_count

    # Get platform
    def get_platform(self):
        return os.environ['PLATFORM']

    # check if test QMI unit test, otherwise test AT unit test.
    def enable_qmi_test(self):
        if 'qmi' in os.environ["TYPES"]:
            return True
        else:
            return False

    # check if need to update FW
    def enable_update_fw(self):
        bool_value = os.getenv('FW_UPDATE')
        if "true" == bool_value:
            return True
        else:
            return False
        #return get_bool_value('FW_UPDATE')

    # Get FW version
    def get_FW_ver(self):
        return os.environ['FW_VERSION']
        
    # Get FW image path
    def get_FW_image_path(self):
        return os.environ['FW_IMAGE_PATH']
    
    # Get the test sciprt store path
    def get_test_script_store_path(self):
        self.test_script_store_path = os.environ['TESTCASE_PATH']
        return self.test_script_store_path

    def get_test_script_directory_name(self):
        script_directory_name = self.get_test_script_store_path().split('/')[-1]
        return script_directory_name

    def get_acis_diff(self):
        return os.environ["ACIS_DIFF"]
    # Get log directory
    def get_log_directory(self):
        return os.environ['REPORT_PATH'] + '/' + self.get_platform() + "/" + self.get_acis_diff()

    # Get qmi test app path and name
    def get_qmi_testapp_path(self):
        return os.environ['FW_IMAGE_PATH']

    # Get qmi test configuration file
    def get_qmi_configuration_file(self):
        return self.get_qmi_testapp_path() + '/config_file'

    def get_qmi_log_directory(self):
        qmi_log_path = self.get_log_directory() + "/" + self.get_test_script_directory_name() + "/QMI"
        if not os.path.exists(qmi_log_path):
            os.makedirs(qmi_log_path)
        return qmi_log_path

    def get_qmi_auto_generate_script_path(self):
        qmi_loop_test = self.loop_test_path() + "/" + self.get_test_script_directory_name() + "/QMI"
        if not os.path.exists(qmi_loop_test):
            os.makedirs(qmi_loop_test)
        return qmi_loop_test

    def loop_test_path(self):
        return os.environ['LOOP_TEST'] + '/' + self.get_platform() + "/" + self.get_acis_diff()

    def get_qmi_testapp(self):
        return self.get_qmi_testapp_path() + '/testQaQmi'

    def at_loop_test_conftest_path(self):
        return self.loop_test_path() + "/" + self.get_test_script_directory_name()
