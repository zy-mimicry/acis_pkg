#! /usr/bin/env python3
# coding=utf-8

import shutil
import os,sys,getopt

def do_copy_with_init(src_dir, dst_dir):
    """
    TODO: Reserved '__init__.py' in directory.
    """

    _um = os.umask(0o0002)
    shutil.copytree(src_dir, dst_dir)

    for root, dirs, filelist in os.walk(dst_dir):
        for f in filelist:
            if '__init__' not in f:
                #print("delete file: ", os.path.join(root, f))
                os.remove(os.path.join(root, f))
    os.umask(_um)

def do_copy_without_py(src_dir, dst_dir):
    """
    TODO: Copy directory tree, without any file.
    """

    _um = os.umask(0o0002)
    shutil.copytree(src_dir, dst_dir)

    for root, dirs, filelist in os.walk(dst_dir):
        for f in filelist:
            #print("delete file: ", os.path.join(root, f))
            os.remove(os.path.join(root, f))
    os.umask(_um)

def deal_cmdline(argv):
    src  = ''
    dst  = ''
    cmd_with_init_flag = False

    try:
       opts, args = getopt.getopt(argv,"hc:s:d:",["cmd=","src=","dst="])
    except getopt.GetoptError:
       sys.exit(2)

    for opt, arg in opts:
       if opt == '-h':
          print('master_copytree.py -s <src_dir> -d <dest_dir>')
          sys.exit()
       elif opt == '-c':
           if arg == 'with_init':
               cmd_with_init_flag = True
           if arg == 'without_init':
               cmd_with_init_flag = False
       elif opt in ("-s", "--src"):
          src  = arg
       elif opt in ("-d", "--dest"):
          dst = arg

    if cmd_with_init_flag:
        do_copy_with_init(src, dst)
    else:
        do_copy_without_py(src,dst)


if __name__ == "__main__":
    deal_cmdline(sys.argv[1:])
