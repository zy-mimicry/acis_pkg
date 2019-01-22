#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
@author: Shawn Wu
@contact: shwu@sierrawireless.com
@file : acis_slave_at_testplan_generator.py
@time: 2018/10/31 14:50
"""

import os
from acis_slave_testplan_generator import Slave_testplan_prepare
import shutil


def qmi_auto_generate_case_str():
    return """\
# _*_ coding:utf-8 _*_

import pytest
import allure
from acis.core.report import report
import os
import re
import time
import subprocess

@report.fixture(scope="module")
def m(request, minit):
    mz =  minit(__file__,
               logger_name = 'ACIS.QMI.APP.TEST',
               mail_to     = 'rzheng@sierrawireless.com',
               port_names  = [
                   'AT..any',
                   'ADB..any',
               ])

    mz.test_ID = os.path.basename(__file__.split('.')[0])
    mz.errors = {{}}
    mz.flags  = []
    def module_upload_log():
        allure.attach.file("{LOG_PATH}/{CASENAME}.log",
                           attachment_type = allure.attachment_type.TEXT)
        if mz.at: mz.at.closeall()
    request.addfinalizer(module_upload_log)
    return mz


@report.epic("QMI")
class ACISQMITest():
    \"\"\"
    Something you want to descript for this test. (can't display)
    \"\"\"

    @report.step("[Stage] <Pre-Condition>")
    def pre(self, m):
        serial_id = m.adb.conf['any']['serial_id']
        m.log("PUSH : testapp to DUT." + serial_id)
        returninfo = os.popen("adb -s {{SERIAL_ID}} push  {TEST_APP} /tmp/testQaQmi".format(SERIAL_ID = serial_id))
        while 1:
            try:
                line = returninfo.readline()
            except :
                continue
            if len(line) <= 0:
                break

        m.log("PUSH : testapp config to DUT.")
        returninfo = os.popen("adb -s {{SERIAL_ID}} push  {CONFIG_FILE} /tmp".format(SERIAL_ID = serial_id))
        while 1:
            try:
                line = returninfo.readline()
            except :
                continue
            if len(line) <= 0:
                break

    @report.step("[Stage] <Real-Test-Body>")
    def body(self, m):
        m.log("***********test {CASENAME} start*************")

        serial_id = m.adb.conf['any']['serial_id']

        m.log('adb -s {{SERIAL_ID}} shell "cd /tmp && ./testQaQmi -t {CASENAME}"'.format(SERIAL_ID = serial_id))
        returninfo = os.popen('adb -s {{SERIAL_ID}} shell "cd /tmp&&./testQaQmi -t {CASENAME}"'.format(SERIAL_ID = serial_id))
        while 1:
            try:
                line = returninfo.readline()
                m.log(line)
            except :
                continue
            if len(line) <= 0:
                break

        returninfo = os.popen('adb -s {{SERIAL_ID}} pull /tmp/te_log/{CASENAME}.log {LOG_PATH}/{CASENAME}.log'.format(SERIAL_ID = serial_id))
        while 1:
            try:
                line = returninfo.readline()
            except :
                continue
            if len(line) <= 0:
                break

        # check the test result.
        fd = open('{LOG_PATH}/{CASENAME}.log', 'r')
        log_read = fd.read()
        if re.findall(r'>>>>>>>RESULT:Passed:\d+/\d+=100%', log_read):
            test_result = True
        else:
            test_result = False

        returninfo = os.popen('adb -s {{SERIAL_ID}} shell "rm /tmp/te_log/* -rf"'.format(SERIAL_ID = serial_id))
        while 1:
            try:
                line = returninfo.readline()
            except :
                continue
            if len(line) <= 0:
                break
        m.log("***********test {CASENAME} end*************\\n")

        fd.close()
        assert test_result == True

    @report.step("[Stage] <Restore-Module>")
    def restore(self, m):
        m.log("Nothing....")


    @report.story("QMI")
    @pytest.mark.run(order=1)
    def {CASENAME_FUNC}(self, m):
        \"\"\"
        TODO: QMI APP TEST.
        \"\"\"

        m.log("\\n>> Welcome use ACIS ! ^_^")

        try:
            try:
                self.pre(m)                    # << Stage | pre
            except Exception as e:
                m.log("<Pre-Stage-Exception> reason: {{}}".format(e))
                m.flags.append('pre')
                m.errors['pre'] = e
                raise e
            self.body(m)                       # << Stage | body
        except Exception as e:
            if not m.flags :
                m.log("<Body-Stage-Exception> reason: {{}}".format(e))
                m.flags.append('body')
                m.errors['body'] = e

        try:
            self.restore(m)                    # << Stage | restore
        except Exception as e:
            m.log("<Restore-Stage-Exception> reason: {{}}".format(e))
            m.flags.append('restore')
            m.errors['restore'] = e

        if m.flags:
            m.log("\\n\\n  <ACIS Exception Stack Information>\\n")
            for f in m.flags:
                m.log("--- {{}} stack info ---\\n{{}}\\n".format(f, m.errors[f]))
            m.log("\\nTESTCASE:[{{}}] Result:[{{}}]\\n".format(m.test_ID, "FAIL"))
            raise Exception("\\n\\n <ACIS Test Exception, Please check stack information.>\\n")
        else:
            m.log("\\nTESTCASE:[{{}}] Result:[{{}}]\\n".format(m.test_ID, "PASS"))
"""

class Slave_QMI_testplan_prepare(Slave_testplan_prepare):
    def __init__(self):
        Slave_testplan_prepare.__init__(self)

    def create_pytest_format_script(self):
        test_function_string = qmi_auto_generate_case_str()
        format_script = self.envs.get_qmi_auto_generate_script_path() + '/' + self.pytest_format_file_name
        print(format_script)
        log_path = self.envs.get_qmi_log_directory()
        with open(format_script, 'w+') as fd:
            case_function_string = test_function_string.format(CASENAME=self.envs.get_test_case_list(),
                                                               LOG_PATH=log_path,
                                                               TEST_APP=self.envs.get_qmi_testapp(),
                                                               CONFIG_FILE=self.envs.get_qmi_configuration_file(),
                                                               CASENAME_FUNC=self.envs.get_test_case_list().replace(".", "_"))
            fd.write(case_function_string)

    def run_test(self):
        self.run_pytest(self.envs.get_qmi_log_directory() + '/' + self.envs.get_test_case_list().replace('.', '_') + "_report",
                        self.envs.get_qmi_auto_generate_script_path() + "/" + self.pytest_format_file_name)


