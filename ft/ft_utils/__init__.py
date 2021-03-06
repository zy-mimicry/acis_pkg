#! /usr/bin/env python
# coding=utf-8

"""
pytest version == 3.7.1
allure version == 2.5.0
"""

import os, re
from ft_utils.log import Log,peer
from ft_utils.port import Port,PortProber

hook_log = None

class ACISMiscer():
    """
    ACISMiscer class

    It's provide the method and attribute to operate the misc. It's a bridge between testcases and devices.
    when we write the testcases, we can init a miscer,and use the method and attribute of the misc to complete the testcase.
    """

    def __init__(self):
        """
        the ACISMiscer class constructor function, init necessary conditions

        Args:
            none

        Returns:
            none
        """
        self.limit_name = 'ft' # Maybe get this var from environment better.

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
        """
        Deal and provide the log path, the testcase log will saved in the path.

        Examples:
            deal_log_path('/home/jenkins/tmp/loop_test/testcases/Driver/LowSpeedBus/ACIS_A_D_LSBUS_SPI_TEST.py')

        Args:
            case_file: the case path, it will be made for the log.

        Returns:
            the log path("/tmp/acis/testlog/testcases/Driver/LowSpeedBus/*").

        """
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
        self.envs['Description'] = os.environ['DESCRIPTION']

        filesvr_url = 'http://cnshz-ed-svr098/ACIS-IntegrationTest-Reports/' # end of '/'

        if os.environ.get("PLATFORM") == "offline":
            replace_from = 'logs'
        else:
            replace_from = 'log_and_report'

        log_path_slice = self.which_log.split('/')
        reversed_log_path_slice = list(reversed(log_path_slice))
        reversed_partial_slice  = reversed_log_path_slice[:reversed_log_path_slice.index(replace_from)]
        partial_slice = list(reversed(reversed_partial_slice))
        self.envs['Test_Log'] = filesvr_url + '/'.join(partial_slice)

        diff_location = partial_slice.index(os.environ['ACIS_DIFF']) + 1
        report_suffix = '/' + os.environ['ACIS_DIFF'] + '_report'
        self.envs['Test_IR_Report'] = filesvr_url + '/'.join(partial_slice[:diff_location]) + report_suffix


    def echo_slave_info(self):
        import subprocess
        output_format = "<slave info> [{:<25s}]: [status:{:<4d}] [{}]"
        self.log("<SLAVE INFORMATION RECORD BEG>")

        status, hostname = subprocess.getstatusoutput('hostname')
        self.log(output_format.format('hostname', status, hostname))

        status, ip = subprocess.getstatusoutput('/sbin/ifconfig -a | grep inet | grep -v 127.0.0.1 | grep -v inet6 | awk \'{print $2}\' | tr -d "addr"')
        self.log(output_format.format('ip', status, ip))

        status, mac = subprocess.getstatusoutput('cat /sys/class/net/eth0/address')
        self.log(output_format.format('mac_eth0', status, mac))

        status, pi_time = subprocess.getstatusoutput('date +%Y_%m_%d_%H_%M_%S')
        self.log(output_format.format('pi_time', status, pi_time))

        status, bootup_time = subprocess.getstatusoutput('uptime -s')
        self.log(output_format.format('bootup_time', status, bootup_time))

        status, mem_total = subprocess.getstatusoutput('grep MemTotal /proc/meminfo | awk \'{print $2" "$3}\'')
        self.log(output_format.format('mem_total', status, mem_total))

        status, mem_available = subprocess.getstatusoutput('grep MemAvailable /proc/meminfo | awk \'{print $2" "$3}\'')
        self.log(output_format.format('mem_available', status, mem_available))

        status, mem_free = subprocess.getstatusoutput('grep MemFree /proc/meminfo | awk \'{print $2" "$3}\'')
        self.log(output_format.format('mem_free', status, mem_free))

        status, swap_total = subprocess.getstatusoutput('grep SwapTotal /proc/meminfo | awk \'{print $2" "$3}\'')
        self.log(output_format.format('swap_total', status, swap_total))

        status, swap_free = subprocess.getstatusoutput('grep SwapFree /proc/meminfo | awk \'{print $2" "$3}\'')
        self.log(output_format.format('swap_free', status, swap_free))

        status, slave_workspace = subprocess.getstatusoutput('du -sh $HOME/workspace | awk \'{print $1}\'')
        self.log(output_format.format('slave_workspace', status, slave_workspace))

        status, slave_root_space_total = subprocess.getstatusoutput('df -kh $HOME | grep "/dev/root" | awk \'{print $2}\'')
        self.log(output_format.format('slave_root_space_total', status, slave_root_space_total))

        status, slave_root_space_used = subprocess.getstatusoutput('df -kh $HOME | grep "/dev/root" | awk \'{print $3}\'')
        self.log(output_format.format('slave_root_space_used', status, slave_root_space_used))

        status, slave_root_space_avail = subprocess.getstatusoutput('df -kh $HOME | grep "/dev/root" | awk \'{print $4}\'')
        self.log(output_format.format('slave_root_space_avail', status, slave_root_space_avail))

        self.log("<SLAVE INFORMATION RECORD END>\n")


    def deal_misc(self, log_file, logger_name, port_names):
        """
        Deal with the misc information from the testcases, init the misc for use by testcase

        Args:
            log_file: the path will be made for the log
            logger_name: the logger object
            port_names: the port names you want to register

        Returns:
            the misc instance.

        """
        global hook_log
        hook_log = self.log = Log(self.deal_log_path(log_file), logger_name = logger_name)
        self.register_port(port_names)
        self.deal_envs()
        self.echo_slave_info()
        return self

    def order_port_list(self,port_names):
        """
        Order the port list, make the AT port in front of the ADB

        Examples:
            order_port_list('AT..DUT1')

        Args:
            port_names: the port name .

        Returns:
            ordered port list.

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
        """
        Register the port.

        Examples:
            register_port('AT..DUT1')

        Args:
            port_names: the port name you want to register.

        Returns:
            none.

        """

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

    def probe_port(self):
        global hook_log
        hook_log = self.log = Log(log_path = '/tmp/drop.log')
        return PortProber().get_samples()

