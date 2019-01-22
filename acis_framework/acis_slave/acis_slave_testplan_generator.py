#!/usr/bin/python3
# -*-coding:utf-8-*-
"""
@author: Shawn Wu
@contact: shwu@sierrawireless.com
@file : acis_slave_testplan_generator.py
@time: 2018/10/31 14:50
"""

import os
import acis_slave_envs_parser
import re
import shutil

import subprocess
from acis.utils.log import peer
from acis import ACISMiscer
miscer = ACISMiscer()

def get_devices_from_real():
    """
    devices = [ 'serial_id_1', 'serial_id_2', ...]
    """
    try:
        output = subprocess.check_output('adb devices',
                                        shell = True).decode('utf-8').strip()
    except subprocess.CalledProcessError as err:
        print("ERROR: ", err)
        sys.exit(-1)
    else:
        devices = []
        for line in output.split('\n'):
            print(line)
            g = re.match('\s*?(.*)\s*device$', line)
            if g:
                devices.append(g.group(1).strip())
        print("List devices: ", devices)
        return devices

def get_devices_from_rules(_file):
    """
    configs: >>
    "DUT1" : { "serial" : serial_id},
    "DUT2"  : { "serial" : serial_id},
    """

    if not os.path.exists(_file):
        raise Exception("No rules for ACIS udev configuration. This board can NOT do test!!! ")

    configs = {}
    with open(_file, mode = 'r') as f:
        for line in f:
            g = re.match(r'\s*ATTRS{serial}=="(.*)",\s*GOTO="(.*)\s*"', line)
            if g:
                if g.group(2) == "acis_DUT1":
                    configs["DUT1"] = {"serial" : g.group(1)}
                elif g.group(2) == "acis_DUT2":
                    configs["DUT2"]  = {"serial" : g.group(1)}
    return configs


def match_devices(_file):
    """
    match : >>
    "DUT1" : serial_id,
    "DUT2"  : serial_id,
    """

    devices_rule = get_devices_from_rules(_file)
    devices_real = get_devices_from_real()

    match = {}

    for d in devices_real:
        for r in devices_rule:
            if d == devices_rule[r]["serial"]:
                match[r] = d

    if len(match) == 0:
        print("Can NOT recognize the ports.\n{}".format(match))
        raise Exception("Serial IDs don't match Rules IDs.")

    return match

def init_ports(_file):
    """
    return : dict >>
    { "DUT1" : {"AT" : miscer.at.DUT1, "ADB" : miscer.adb.DUT1},
      "DUT2"  : {"AT" : miscer.at.DUT2,  "ADB" : miscer.adb.DUT2},}
    """
    global miscer
    matched = match_devices(_file)

    print("Hook matched devices: ", matched)

    if len(matched) == 2:
         miscer.register_port(port_names = ["AT..DUT1",
                                            "AT..DUT2",
                                            "ADB..DUT1",
                                            "ADB..DUT2"])
         return { "DUT1" : {"AT" : miscer.at.DUT1, "ADB" : miscer.adb.DUT1},
                  "DUT2"  : {"AT" : miscer.at.DUT2,  "ADB" : miscer.adb.DUT2}, }

    elif len(matched) == 1:
        for name in matched:
            if name == "DUT1":
                miscer.register_port(port_names = ["AT..DUT1",
                                                   "ADB..DUT1"])
                return {"DUT1" : {"AT" : miscer.at.DUT1, "ADB" : miscer.adb.DUT1}}
            if name == "DUT2":
                miscer.register_port(port_names = ["AT..DUT2",
                                                   "ADB..DUT2"])
                return {"DUT2" : {"AT" : miscer.at.DUT2, "ADB" : miscer.adb.DUT2}}


def get_dut_information(at):

    print("hook <<< here")
    at.send_cmd("ATI\r")
    response1 = at.wait_resp(["*\r\nOK\r\n"], 4000)

    at.send_cmd("ATI8\r")
    response2 = at.wait_resp(["*\r\nOK\r\n"], 4000)

    response = response1 + response2
    at.close()
    return response


def image_update(at, adb, image_file, image_version, platform):

    print("[update] Img update ...")
    dut_information = get_dut_information(at)
    if platform not in dut_information:
        print("Error, Platform Conflict")
        raise Exception("Fw update: Error, Platform Conflict")

    if image_version in dut_information:
        print("fw version is expected, no need to update")
        return True
    else:

        print("ADB > fastboot update FW doing...")
        adb.send_cmd("reboot-bootloader && fastboot flash sierra-dual-system {FW_File} && fastboot reboot".format(FW_File = image_file))

    at.sleep(90000)

    # check if update success
    dut_information = get_dut_information(at)

    if image_version in dut_information:
        print("fw image update successed")
        print("[update] Img update Done.")
        return True
    else:
        print("fw update failed for" + image_version)
        raise Exception("image update Failed")



class Slave_testplan_prepare:
    def __init__(self):
        self.envs = acis_slave_envs_parser.Slave_envs_parser()
        self.fw_image_file = ''
        self.pytest_format_file_name = self.envs.get_test_case_list().replace('.', '_') + ".py"
        self.rules_location = '/etc/udev/rules.d/11-acis.rules'

    def set_fw_image_file(self):
        fw_image_path = self.envs.get_FW_image_path()
        fw_image_name = ''
        file_list = os.listdir(fw_image_path)
        for file_item in file_list:
            if not file_item.endswith('.cwe'):
                continue
            if ('spkg' in file_item) and (fw_image_name == ''):
                fw_image_name = file_item
        if fw_image_name == '':
            print("Can't find FW image")
        else:
            self.fw_image_file = self.envs.get_FW_image_path() + '/' + fw_image_name

    def fw_image_update(self):
        self.ports = init_ports(self.rules_location)
        print("update fw ports:", self.ports)
        for each in self.ports:
            image_update(self.ports[each]['AT'],
                         self.ports[each]['ADB'],
                         self.fw_image_file,
                         self.envs.get_FW_ver(),
                         self.envs.get_platform())

    def dut_test_history_prepare(self):
        ports = init_ports(self.rules_location)
        save_string = {}

        for each in ports:
            dut_serial_id = ports[each]['ADB'].serial_id

            # Get FSN from DUT
            at = ports[each]['AT']
            at.send_cmd("AT!UNLOCK=\"A710\"\r\n")
            try:
                at.waitn_match_resp(["*\r\nOK\r\n"], 4000)
            except Exception as e:
                print("dut_test_history_save: Failed unlock the DUT")
                print(str(e))
            at.send_cmd("AT!NVFSN?\r\n")
            response = at.wait_resp(["*\r\nOK\r\n"], 4000)
            dut_fsn = response.split("\n")[1].strip()
            at.close()

            save_string[dut_serial_id] = (
                "[{TIME}]:{TPYE:<8s} Serial_ID:{SERIAL_ID:<10s}  Module_FSN:{FSN:<20s} Platform:{PLATFORM:<8s} Test_Case: {CASENAME:<60s} Test_Count:{COUNT}\n".format(
                    TIME=self.envs.get_acis_diff(),
                    TPYE=str(each),
                    SERIAL_ID=dut_serial_id,
                    FSN=dut_fsn,
                    PLATFORM=self.envs.get_platform(),
                    CASENAME=self.envs.get_test_case_list(),
                    COUNT=self.envs.get_test_count()))
        # this string is dict like {"DUT1": [{TIME}]:DUT1 Serial_ID:{SERIAL_ID}  Module_FSN:{FSN} Test_Case: {CASENAME} Test_Count:{COUNT}}
        return save_string

    def save_dut_test_history(self, test_history, report_path):
        node_build_history_path = "/home/jenkins/nfs_acis/node_build_history/" + os.environ["NODE_NAME"]
        dut_test_history_file = node_build_history_path + "/dut_test_history.txt"
        history_list = []

        if not os.path.exists(node_build_history_path):
            os.makedirs(node_build_history_path, mode=0o755)

        if not os.path.exists(dut_test_history_file):
            os.mknod(dut_test_history_file)

        test_log_directory = os.path.abspath(report_path)
        test_log_directory = os.path.dirname(test_log_directory)

        test_history_fd = open(dut_test_history_file, "r+")
        test_log_fd = open(test_log_directory + "/" + self.envs.get_test_case_list().replace('.', '_') + ".log", "r")
        buffer_test_log = test_log_fd.read()


        for dut_serial_id, history in test_history.items():
            if "'serial_id': '{}'".format(dut_serial_id) in buffer_test_log:
                test_history_fd.write(history)

        test_history_fd.close()
        test_log_fd.close()

    def run_pytest(self, report_path, test_script):
        os.chdir(self.envs.loop_test_path())
        test_history = self.dut_test_history_prepare()
        print(test_script)
        os.system('pytest -s {TEST_SCRIPT} --count={COUNT} --alluredir {REPORT_PATH} --junitxml={JUNIT_REPORT}'.format(
                TEST_SCRIPT=test_script,
                COUNT=self.envs.get_test_count(),
                REPORT_PATH=report_path,
                JUNIT_REPORT=self.envs.get_log_directory() + "/junit_report/" + self.envs.get_test_case_list().replace(".", "_") + ".xml"))
        self.save_dut_test_history(test_history, report_path)

