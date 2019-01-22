#! /usr/bin/env python3
#coding=utf-8

import os,sys,re,shutil
import subprocess

def get_cookies():
    """
    """

    # which_net = 'wlp3s0'
    which_net = 'eth0'

    # GET: IP , hostname , mac address
    try:
        ip = subprocess.check_output("ifconfig {net} | grep \"inet \" | awk '{{ print $2}}' #| awk -F: '{{print $2}}'".
                                     format(net = which_net),
                                     shell=True).decode('utf-8').strip()
        hostname = subprocess.check_output('hostname', shell=True).decode('utf-8').strip()
        mac = subprocess.check_output('cat /sys/class/net/{net}/address'.
                                      format(net = which_net),
                                      shell = True).decode('utf-8').strip()
    except subprocess.SubprocessError as e:
        print(e)
        sys.exit(-1)
    else:
        return { 'ip' : ip,
                 'hostname' : hostname,
                 'mac' : mac}


def find_ipfile(dst, ip):
    for root, dirs, filelist in os.walk(dst):
        for f in filelist:
            if f == ip:
               return (True, root, os.path.basename(root))
        for d in dirs:
            find_ipfile(root + '/' + d, ip)
    return (False, "", "")

def write_d_item_to_file(root, name, m_dict):
    with open(os.path.join(root, name), 'w') as f:
        for item in m_dict:
            f.write(item + ' : ' + m_dict[item] + '\n')

def rm_empty_dir(dst):

    for root, dirs, filelist in os.walk(dst):
        for d in dirs:
            if not os.listdir(root + '/' + d):
                os.rmdir(root + '/' + d)
            else:
                rm_empty_dir(root + '/' + d)

def auto_upload_ipfile(NFS_mounted):

    NFS_dir = NFS_mounted

    # Is exists? (NFS directory)
    if not os.path.exists(NFS_dir):
        raise FileNotFoundError("Sorry, '{}' directory is not exists.".format(NFS_dir))

    cookies = get_cookies()

    obj_file = cookies['ip']
    if obj_file.strip() == "":
        raise Exception("You can't get the vaild IP address from your platform.")

    # exists : True or False
    # root_dir : if exists, root_dir is file dir name eg.'/home/jenkins/nfs_acis/rasp-nodes-list/rasp-bsp-101/'
    # host   : if exists, host is file-root base name eg.'rasp-bsp-101'
    (exists, root_dir, host) = find_ipfile(NFS_dir, obj_file)
    print("record:\n\t-exists:{}\n\t-root_dir:{}\n\t-host:{}".format(exists, root_dir, host))

    if exists:
        if host == cookies['hostname']:
            pass
        else:
            os.remove(os.path.join(root_dir, obj_file))
            want_dir = os.path.dirname(root_dir) + '/' + cookies['hostname']
            if os.path.exists(want_dir):
                write_d_item_to_file(want_dir, obj_file, cookies)
            else:
                os.makedirs(want_dir)
                write_d_item_to_file(want_dir, obj_file, cookies)
    else:
        if os.path.exists(os.path.join(NFS_dir, cookies['hostname'])):
            write_d_item_to_file(os.path.join(NFS_dir, cookies['hostname']), obj_file, cookies)
        else:
            os.makedirs(os.path.join(NFS_dir, cookies['hostname']))
            write_d_item_to_file(os.path.join(NFS_dir, cookies['hostname']), obj_file, cookies)

    rm_empty_dir(NFS_dir)

if __name__ == "__main__":

    # may be you can modify here for NFS mount dir.
    # NFS_dir = './rasp-nodes-ips'
    NFS_dir = '/home/jenkins/nfs_acis/Rasp-Img/rasp-nodes-list'
    auto_upload_ipfile(NFS_dir)
