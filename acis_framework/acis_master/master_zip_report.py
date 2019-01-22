#! /usr/bin/env python
# coding=utf-8

"""
"""

import sys,re,os
import shutil
import zipfile
import getopt

def make_zip(source_dir, output_filename):
    """
    Zip source_dir to output file.
    """
    if not os.path.exists(source_dir):
        raise Exception

    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile, arcname)
    zipf.close()


def deal_cmdline(argv):
    src = ''
    dst = ''

    try:
       opts, args = getopt.getopt(argv,"hs:z:",["sfile=","zfile="])
    except getopt.GetoptError:
       sys.exit(2)

    for opt, arg in opts:
       if opt == '-h':
          print('master_zip_report.py -s <src_dir> -d <dst_zip>')
          sys.exit()
       elif opt in ("-s", "--sfile"):
          src  = arg
       elif opt in ("-z", "--zfile"):
          dst = arg

    make_zip(src, dst)

if __name__ == "__main__":
    deal_cmdline(sys.argv[1:])
