#! /usr/bin/env python
# coding=utf-8

"""
"""
import os,shutil,getopt,sys

def cpfile(src, dst):
    if not os.path.exists(src):
        raise FileExistsError("Source file not exists.")

    shutil.copyfile(src, dst)

def deal_cmdline(argv):
    src = ''
    dst = ''

    try:
       opts, args = getopt.getopt(argv,"hs:d:",["sfile=","dfile="])
    except getopt.GetoptError:
       sys.exit(2)

    for opt, arg in opts:
       if opt == '-h':
          print('master_cpfile.py -s <src_dir> -d <dst_dir>')
          sys.exit()
       elif opt in ("-s", "--sfile"):
          src  = arg
       elif opt in ("-d", "--dfile"):
          dst = arg

    cpfile(src, dst)

if __name__ == "__main__":
    deal_cmdline(sys.argv[1:])
