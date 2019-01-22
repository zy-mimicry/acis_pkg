#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
@author: Shawn Wu
@contact: shwu@sierrawireless.com
@file : acis_slave_at_testplan_generator.py
@time: 2018/10/31 14:50
"""

import os
import re
from acis_slave_testplan_generator import Slave_testplan_prepare
import shutil

def get_test_script_with_full_path(test_case_name, test_script_path):
    test_script = test_case_name + ".py"
    for root, dirs, files in os.walk(test_script_path, topdown=True):
        for name in files:
            full_path = os.path.join(root, name)
            if test_script in full_path:
                return full_path
    raise Exception("@ Error can't find the test case[%s]!" % test_case_name)

def get_test_script_relate_path(test_scipt_store_path, test_script_full_path, test_case_name):
    case_relative_store_path_list = test_script_full_path.split(test_scipt_store_path)
    case_relative_store_path_list = case_relative_store_path_list[1].split(test_case_name)
    case_relative_store_path = case_relative_store_path_list[0][0:-1]
    print('case relative path: ', case_relative_store_path)
    return case_relative_store_path


class Slave_at_testplan_prepare(Slave_testplan_prepare):
    def __init__(self, ):
        Slave_testplan_prepare.__init__(self)
        self.test_script_with_path = ''
        self.case_relative_store_path = ''

    def search_case(self):
        # self.test_script_with_path = get_test_script_with_full_path(self.envs.get_test_case_list(), self.envs.get_test_script_store_path())
        # print(self.test_script_with_path)
        # if self.test_script_with_path == '':
        #     raise Exception("@@@@@@@ Error can't find the test case[%s]!" % self.envs.get_test_case_list())
        # return self.test_script_with_path
        self.test_script_with_path = get_test_script_with_full_path(self.envs.get_test_case_list(), self.envs.get_test_script_store_path())


    def copy_test_script_to_loop_test(self):
        self.case_relative_store_path = get_test_script_relate_path(self.envs.get_test_script_store_path(),
                                                               self.test_script_with_path,
                                                               self.envs.get_test_case_list())

        self.auto_generate_script_directory = (self.envs.loop_test_path() + '/' +
                                               self.envs.get_test_script_directory_name() +
                                               self.case_relative_store_path)

        if not os.path.basename(self.auto_generate_script_directory):
            self.auto_generate_script_directory = self.auto_generate_script_directory[:-1]

        print(self.auto_generate_script_directory)
        shutil.copy(self.test_script_with_path, self.auto_generate_script_directory)

    def run_test(self):
        report_path = (self.envs.get_log_directory() + '/' +
                             self.envs.get_test_script_directory_name() + '/' +
                             self.case_relative_store_path + "/" +
                             self.envs.get_test_case_list().replace('.', '_') + "_report")

        self.run_pytest(report_path,
                        self.auto_generate_script_directory + "/" + self.envs.get_test_case_list() + ".py")


