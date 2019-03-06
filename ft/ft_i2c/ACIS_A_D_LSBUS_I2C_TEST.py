#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from ft_utils.report import report
import os
import re

"""
@ Author:
@ Test Name:ACIS_A_D_LSBUS_I2C_TEST
@ Brief:

@ History
Date                    Fixer                           Modification
2018-June-08            Daemon                          Create file
2018-Dec-11             Rdeng
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


I2C_BUS_DETECT = "i2cdetect -l"
current_dir = os.path.dirname(os.path.abspath(__file__))


@report.epic(os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
@report.feature(os.path.basename(os.path.dirname(os.path.abspath(__file__))))
@report.link("https://issues.sierrawireless.com/browse/QTI9X40-5131", name = "JIRA TICKET")
class ACIS_A_D_LSBUS_I2C_TEST(): # << should be modified to test case name. <Written in hump format>

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
        m.log("\nInitiate DUT:")
        m.at.any.send_cmd("AT\r")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.at.any.send_cmd("AT&F;&W\r")
        m.at.any.waitn_match_resp(["*\r\nOK\r\n"], 4000)

        m.log("\nCancel Echo:")
        m.at.any.send_cmd("ATE0\r\n")
        m.at.any.waitn_match_resp(['*\r\nOK\r\n'], 2000)

        m.at.any.send_cmd('ATI3\r')
        m.at.any.waitn_match_resp(['*\r\n\r\nOK\r\n'], 4000)

        m.at.any.send_cmd('ATI8\r')
        m.at.any.waitn_match_resp(['*\r\n\r\nOK\r\n'], 4000)

        m.at.any.send_cmd('AT!PACKAGE?\r')
        m.at.any.waitn_match_resp(['*\r\n\r\nOK\r\n'], 4000)
        
        #test_file_path = m.conf.TEST_FILE_PATH
        ret = m.adb.any.send_cmd('push %s/eeprog /tmp' % current_dir)

        path = m.case_output

        ret = m.adb.any.send_cmd('pull /tmp/eeprog %s' % path)
        ret = m.adb.any.send_cmd('shell "chmod 777 /tmp/eeprog" ' )

    @report.step("[Stage] <Real-Test-Body>")
    def body(self, m):
        m.log("Stage [body]")
        self.class_local_method_02(m)
        # i2c bus detect
        ret = m.adb.any.send_cmd(
            'shell %s'% I2C_BUS_DETECT, timeout = 60)
        if "i2c" in ret:
            m.log("I2C Bus Detect Passed\n")
        else:
            raise Exception("---->Problem: I2C Bus Detect Failed !!!")

        # i2c bus scan
        bus = re.compile(r'i2c-\d')
        bus_name = bus.findall(ret)

        FOR_REPORT_FLAG = 0
        for name in range(len(bus_name)):
            bus_num = bus_name[name][4]
            I2C_EACHBUS_DETECT = "i2cdetect -y -r " + bus_num
            ret = m.adb.any.send_cmd('shell "%s" ' % I2C_EACHBUS_DETECT, timeout = 60)
            if "57" in ret:
                FOR_REPORT_FLAG += 1
                epm_exist_bus = list()   # epm_exist_bus for for found i2c bus with eeprom
                epm_exist_bus.append(bus_num)
                m.log("I2C-" + bus_num + " Scan Passed\n")
            else:
                m.log("Not found the eeprom on i2c-" + bus_num + "\n")

        if FOR_REPORT_FLAG >= 1:
            m.log("I2C Bus Scan Passed\n")
        else:
            raise Exception("---->Problem: I2C Bus Scan Failed !!!")


        # i2c bus read
        for epm_bus in epm_exist_bus:
            I2C_EACHBUS_DUMP = "i2cdump -f -y " + epm_bus + " 0x57"
            ret = m.adb.any.send_cmd('shell "%s" ' % I2C_EACHBUS_DUMP, timeout = 60)
            if len(ret):
                if "failed" in ret:
                    raise Exception("Dump Error: I2C Bus Read Failed !!!")
                else:
                    m.log("Dump OK: I2C Bus Read Passed\n")
            else:
                raise Exception("Unknown Error: I2C Bus Read Failed !!!")


        # i2c bus write
        for epm_bus in epm_exist_bus:
            NEW_FILE = "echo 0123456789abcdef > /tmp/echo.txt"
            ret = m.adb.any.send_cmd('shell "%s"' % NEW_FILE, timeout = 60)
            # write
            I2C_WRITE_REG = "/tmp/eeprog -fq -16 -w 0x00 -i /tmp/echo.txt -t 5 /dev/i2c-" + epm_bus + " 0x57"
            ret = m.adb.any.send_cmd('shell "%s" ' % I2C_WRITE_REG, timeout = 60)
            # read
            I2C_READ_REG = "/tmp/eeprog -fq -16 -r 0x00:16 /dev/i2c-" + epm_bus + " 0x57"
            ret = m.adb.any.send_cmd('shell "%s" ' % I2C_READ_REG, timeout = 60)

            if ret == "0123456789abcdef":
                m.log("Read Data At 0x57 By i2c-" + epm_bus + ": " + ret + "\n")
                m.log("I2C Bus Write Passed\n")
            else:
                m.log("Read Data At 0x57 By i2c-" + epm_bus + ": " + ret + "\n")
                raise Exception("I2C Bus Write Failed !!!")


    @report.step("[Stage] <Restore-Module>")
    def restore(self, m):
        m.log("Stage [restore]")
        out_of_class_function(m)

    @report.story(__name__)
    @report.mark.run(order=1)
    def ACIS_A_D_LSBUS_I2C_TEST(self, m): # << should modify. MUST: testcase ID(file name)
        """
        To verify the each I2C interface read/write
        """

        m.log(">> Welcome to use ACIS ! ^_^\n")
        m.log(m.case_output)
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

                m.log("\n<SWI:ACIS> TESTCASE:[{}] Result:[{}] Test_Date:[{}] Description:[{}] Test_Times:[{}] Test_Log:[{}] Test_IR_Report:[{}]\n"
                      "".format(m.test_ID, "FAIL", m.envs['Test_Date'],m.envs['Description'],m.envs['Test_Times'],m.envs['Test_Log'], m.envs['Test_IR_Report']))
                report.attach_file(source = m.which_log, name = __name__ + '.log',
                                   attachment_type = report.attachment_type.TEXT)
            else:
                m.log("\n<SWI:ACIS> TESTCASE:[{}] Result:[{}] Test_Date:[{}] Description:[{}] Test_Times:[{}] Test_Log:[{}] Test_IR_Report:[{}]\n"
                      "".format(m.test_ID, "PASS", m.envs['Test_Date'],m.envs['Description'],m.envs['Test_Times'],m.envs['Test_Log'], m.envs['Test_IR_Report']))
                report.attach_file(source = m.which_log, name = __name__ + '.log',
                                   attachment_type = report.attachment_type.TEXT)
