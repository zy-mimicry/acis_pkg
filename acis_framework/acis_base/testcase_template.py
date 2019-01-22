#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from acis.core.report import report
import os

"""
@ Author:
@ Test Name:
@ Brief:

@ History
Date                    Fixer                           Modification
2018-June-08            rzheng                          Create file
------------------------------------------------------------------------
"""


@report.fixture(scope="module")
def m(request, minit):
    """
    port_names  : testcase registers ports [AT or ADB ...] from framework.
                : ? DUT1   << map to '/etc/udev/rules.d/11-acis.rules' - 'DUT1'
                : ? DUT2   << map to '/etc/udev/rules.d/11-acis.rules' - 'DUT2'
                : ? any    << map to '/etc/udev/rules.d/11-acis.rules' - 'DUT1' or 'DUT2'
                : eg. port_names  = [
                                    'AT..DUT1',
                                    'AT..DUT2',
                                    'ADB..DUT1',
                                    'ADB..DUT2',
                                    ]
    """
    mz =  minit(__file__,
                logger_name = __name__,
                port_names  = [
                    'AT..any',              #  << [Modify as needed]
                    'ADB..any',             #  << [Modify as needed]
                ])

    mz.test_ID = __name__
    mz.errors = {}
    mz.flags  = []
    def module_close_AT():
        if mz.at: mz.at.closeall()
    request.addfinalizer(module_close_AT)
    return mz

# Functions defined outside the class can still be used. You can also place your function here.
#####################################################################
@report.step("[Stage] < out of class functions>")
def out_of_class_function(m):
    m.log("Out of class, get 'm' is :{}".format(m))

#####################################################################


@report.epic(os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
@report.feature(os.path.basename(os.path.dirname(os.path.abspath(__file__))))
class !AcisSystemReset!(): # << should be modified to test case name. <Written in hump format>

    # Methods defined inside the class like this. You can place your method here.
    # Please note that you should NOT name the function with 'test' or 'acis'.
    # > Test_ or _test is wrong
    # > Acis_ or _acis is wrong
    # > ACIS_ or _ACIS is wrong
    #####################################################################

    def class_local_method(self,m):
        m.log("01 Inside of class, get 'm' is : {}".format(m))

    def class_local_method_02(self,m):
        m.log("02 Inside of class, get 'm' is : {}".format(m))

    #####################################################################
    @report.step("[Stage] <Pre-Condition>")
    def pre(self, m):
        self.class_local_method(m)
        m.log("Stage [pre]")
        sim_ini = m.conf.SIM_INI
        m.at.any.send_cmd("ATE0\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("AT+CMEE=1\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("ATI3\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("ATI8\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("AT!PACKAGE?\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("AT!SKU?\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("AT!UNLOCK=\"A710\"\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("AT!EROPTION=0,1\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("AT!RESET\r\n")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)
        m.at.any.sleep(40000)

    @report.step("[Stage] <Real-Test-Body>")
    def body(self, m):
        m.log("Stage [body]")
        self.class_local_method_02(m)
        m.at.any.send_cmd("AT\r")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

    @report.step("[Stage] <Restore-Module>")
    def restore(self, m):
        m.log("Stage [restore]")
        m.adb.any.send_cmd("shell \"poweroff\"")
        out_of_class_function(m)

    @report.story(__name__)
    @report.mark.run(order=1)
    def !TEST_CASE_NAME!(self, m): # << should modify. MUST: testcase ID(file name)
        """
        TODO:
        1. The test entrance.
        2. A functional description of testcase should be added here.
        """

        m.log(">> Welcome to use ACIS ! ^_^\n")
        try:
            try:
                self.pre(m)                    # << Stage | pre
            except Exception as e:
                m.flags.append('pre')
                m.errors['pre'] = e
                raise e
            self.body(m)                       # << Stage | body
        except Exception as e:
            if not m.flags :
                m.flags.append('body')
                m.errors['body'] = e
            raise e

        finally:
            try:
                if m.flags:
                    [ m.at.closeall() for me in m.errors[m.flags[0]].args if 'Input/output error' in me ]
                self.restore(m)                # << Stage | restore
            except Exception as e:
                m.log("<Restore> The restore process should not have an exception.\nBut now NOT,reason:\n{}".format(e))
                m.flags.append('restore')
                m.errors['restore'] = e

            if m.flags:
                m.log("\n\n  <ACIS Exception Stack Information>\n")
                for f in m.flags:
                    m.log("--- {} stack info ---\n{}\n\n".format(f, m.errors[f]))

                m.log("\n<SWI:ACIS> TESTCASE:[{}] Result:[{}] Test_Date:[{}] Test_Times:[{}] Test_Log:[{}] Test_IR_Report:[{}]\n"
                      "".format(m.test_ID, "FAIL", m.envs['Test_Date'],m.envs['Test_Times'],m.envs['Test_Log'], m.envs['Test_IR_Report']))
                report.attach_file(source = m.which_log, name = __name__ + '.log',
                                   attachment_type = report.attachment_type.TEXT)
            else:
                m.log("\n<SWI:ACIS> TESTCASE:[{}] Result:[{}] Test_Date:[{}] Test_Times:[{}] Test_Log:[{}] Test_IR_Report:[{}]\n"
                      "".format(m.test_ID, "PASS", m.envs['Test_Date'],m.envs['Test_Times'],m.envs['Test_Log'], m.envs['Test_IR_Report']))
                report.attach_file(source = m.which_log, name = __name__ + '.log',
                                   attachment_type = report.attachment_type.TEXT)
