#! /usr/bin/env python3
# coding=utf-8

"""
"""

import shutil
import os,sys,getopt


def check_and_construct(dest, subs):
    """
    dest : can NOT end with '/' eg. /home/jenkins
    subs : ['fw_image' ,'log_and_report', 'loop_test']
    """
    _um = os.umask(0o0000)
    if os.path.exists(dest):
        for s in subs:
            if os.path.exists(os.path.join(dest, s)):
                continue
            else:
                os.makedirs(os.path.join(dest, s))
    else:
        os.makedirs(dest, mode = 0o777)
        for s in subs:
            os.makedirs(os.path.join(dest, s))
    os.umask(_um)

def deal_cmdline(argv):
    dest  = ''
    subs  = []

    try:
       opts, args = getopt.getopt(argv,"hd:s:",["dest=","sub="])
    except getopt.GetoptError:
       sys.exit(2)

    for opt, arg in opts:
       if opt == '-h':
          print('master_check_or_construct.py -d <dest> -s <sub>')
          sys.exit()
       elif opt in ("-d", "--dest"):
          dest = arg
       elif opt in ("-s", "--src"):
          subs = arg.strip().split(',')

    check_and_construct(dest, subs)

if __name__ == "__main__":
    deal_cmdline(sys.argv[1:])
